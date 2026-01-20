###############################################################################
#
# Copyright 2018-2019, VeEX, Inc.
# All Rights Reserved.
#
# $Workfile:   ScpiEngine.py  $
# $Revision: 21493 $
# $Author: patrickellis $
# $Date: 2020-04-08 15:00:55 -0400 (Wed, 08 Apr 2020) $
#
# DESCRIPTION:
#    Module to process SCPI commands, provided as Bytes strings.
#
###############################################################################

from ErrorCodes import ScpiErrorCode
from ErrorCodes import errorResponse
from ErrorCodes import TcpipServerExit
from ScpiMld import ScpiMld
from ScpiOtn import ScpiOtn
from ScpiSonetSdh import ScpiSonetSdh
from ScpiPacket import ScpiPacket
from ScpiSystem import ScpiSystem
from SessionGlobals import SessionGlobals
import pickle
import ParseUtils
import traceback
import veexlib

class ScpiEngine(object):
    '''This class processes text SCPI commands and returns a text response.

    Args:
        sessionType (string): The type of socket (ie "TCP", "SSL", etc).
        sessionId (int): The ID number assiged to the socket. Used for
                         response messages.
        ipAddress (string): The IP address of the protobuf server to connect to.
    '''

    def __init__(self, sessionType, sessionId, ipAddress):
        self.globals      = SessionGlobals(sessionType, sessionId, ipAddress)
        self.scpiMld      = ScpiMld(self.globals)
        self.scpiOtn      = ScpiOtn(self.globals)
        self.scpiSonetSdh = ScpiSonetSdh(self.globals)
        self.scpiPacket   = ScpiPacket(self.globals)
        self.scpiSystem   = ScpiSystem(self.globals)


    def _errorResponse(self, errorCode):
        '''Handle legacy response when converting integer error codes to text.
        The utiltity that converts doesn't have access to the globals.

        Args:
            errorCode (int): ScpiErrorCode enum of the error
        '''
        return errorResponse(errorCode, self.globals)


    def _processCommands(self, parsedCommand):
        '''Processes a preparsed command that isn't login or logout. Calls the
        INSTrument specific handler.

        Args:
            parsedCommand (List of SubCommand named tuples): The command that needs to be processed.

        Returns:
            Bytes: Response string to send back to user.
        '''
        response = b""
        foundCommand = False

        try:
            # Handle commands directed aty a PP by INSTrument selection.
            if (self.globals.protocolType == veexlib.PROTO_PHY) or \
               (self.globals.protocolType == veexlib.PROTO_OTL) or \
               (self.globals.protocolType == veexlib.PROTO_PCS):
                # These are all MLD
                response, foundCommand = self.scpiMld.processCommand(parsedCommand)
            elif (self.globals.protocolType == veexlib.PROTO_OTN):
                response, foundCommand = self.scpiOtn.processCommand(parsedCommand)
            elif (self.globals.protocolType == veexlib.PROTO_SONET_SDH):
                response, foundCommand = self.scpiSonetSdh.processCommand(parsedCommand)
            elif (self.globals.protocolType == veexlib.PROTO_GFP) or \
                 (self.globals.protocolType == veexlib.PROTO_ETHERNET) or \
                 (self.globals.protocolType == veexlib.PROTO_FIBRECHAN):
                # These are all Packet
                response, foundCommand = self.scpiPacket.processCommand(parsedCommand)

            # If no INST is selected or the protocol specific handler can't
            # find the command then fall back on the system handler for global
            # commands.
            if not foundCommand:
                response, foundCommand = self.scpiSystem.processCommand(parsedCommand)
                if not foundCommand:
                    # The command could not be found in any handler, return -100
                    # command error.
                    response = self._errorResponse(ScpiErrorCode.CMD_ERR)
        except veexlib.ProtocolNak as nak:
            if (nak.reason == veexlib.REASON_INVALID_MSG_RES_ID):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" RES ID"
            elif (nak.reason == veexlib.REASON_INVALID_MSG_TYPE):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" MSG TYPE"
            elif (nak.reason == veexlib.REASON_INVALID_MSG_PAYLOAD):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" PAYLOAD"
            elif (nak.reason == veexlib.REASON_INVALID_SETTING):
                response = self._errorResponse(ScpiErrorCode.INVALID_SETTINGS)
            elif (nak.reason == veexlib.REASON_INVALID_MSG_ACTION):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" ACTION"
            elif (nak.reason == veexlib.REASON_TIMEOUT):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" TIMEOUT"
            elif (nak.reason == veexlib.REASON_REGISTER_READ_FAIL):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" READ"
            elif (nak.reason == veexlib.REASON_SEEPROM_ACCESS_FAIL):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" ACCESS"
            elif (nak.reason == veexlib.REASON_RESOURCE_NOTAVAIL):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" NOTAVAIL"
            elif (nak.reason == veexlib.REASON_SIGNALLING_ERROR):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" SIGNALLING"
            elif (nak.reason == veexlib.REASON_CONNPARAM_NOT_AVAIL):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" NOT AVAIL"
            elif (nak.reason == veexlib.REASON_CONNECTION_FAILURE):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" CONN FAIL"
            elif (nak.reason == veexlib.REASON_INVALID_TEST_ID):
                response = self._errorResponse(ScpiErrorCode.DLI_INVALID_TESTID)
            elif (nak.reason == veexlib.REASON_OUT_OF_SERVICE):
                response = self._errorResponse(ScpiErrorCode.DLI_OUT_OF_SERVICE)
            elif (nak.reason == veexlib.REASON_INVALID_CP_LICENSE):
                response = self._errorResponse(ScpiErrorCode.DLI_INVALID_LICENSE)
            elif (nak.reason == veexlib.REASON_EXPIRED_CP_LICENSE):
                response = self._errorResponse(ScpiErrorCode.DLI_LICENSE_EXPIRED)
            elif (nak.reason == veexlib.REASON_INVALID_MSG_PP_TYPE):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" MSG PP"
            elif (nak.reason == veexlib.REASON_CORBA_SYS_EXCEPTION):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" SYS EXCEPT"
            elif (nak.reason == veexlib.REASON_UNKNOWN_EXCEPTION):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" UNKNOWN EXCEPT"
            elif (nak.reason == veexlib.REASON_UNKNOWN_NAK):
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" UNKNOWN NAK"
            else:
                response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        except veexlib.ServerException as serverExcept:
            if serverExcept.reason == veexlib.EXCEPT_USER_UNAUTHORIZED:
                response = self._errorResponse(ScpiErrorCode.DLI_USER_UNAUTHORIZED)
            elif serverExcept.reason == veexlib.EXCEPT_ADMIN_USER_NOT_FOUND:
                response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_USER_NOT_FOUND)
            elif serverExcept.reason == veexlib.EXCEPT_ADMIN_USER_NOT_LOGGED_IN:
                response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_USER_NOT_LOGGED_IN)
            elif serverExcept.reason == veexlib.EXCEPT_ADMIN_INVALID_PASSWORD:
                response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_INVALID_PASSWORD)
            elif serverExcept.reason == veexlib.EXCEPT_ADMIN_INVALID_LOGIN_NAME:
                response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_INVALID_LOGIN_NAME)
            elif serverExcept.reason == veexlib.EXCEPT_ADMIN_REACHED_MAX_LOGGEDIN_USERS:
                response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_REACHED_MAX_LOGGEDIN_USERS)
            elif serverExcept.reason == veexlib.EXCEPT_ADMIN_USER_ALREADY_LOGGED_IN:
                response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_USER_ALREADY_LOGGED_IN)
            else:
                response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR)
        except TcpipServerExit as e:
            # Don't catch signals in the following catch-all handler.
            raise
        except Exception as e:
            print(traceback.format_exc())
            response = self._errorResponse(ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR) + b" See log for trace."

        return response

    def logCommand(self, command):
        '''Adds the command to the SCPI monitor FIFO for display in the GUI.

        Args:
            command (bytes): The command that needs to be logged.
        '''
        if self.globals.veexChassis:
            self.globals.veexChassis.addScpiMonitorData("RCV(%s%d): %s" % \
                            (self.globals.sessionType.decode(), \
                             self.globals.sessionId, \
                             command.decode()))

    def logResponse(self, response):
        '''Adds the response to the SCPI monitor FIFO for display in the GUI.

        Args:
            response (bytes): The response that needs to be logged.
        '''
        if self.globals.veexChassis:
            self.globals.veexChassis.addScpiMonitorData("RCV(%s%d): %s" % \
                            (self.globals.sessionType.decode(), \
                            self.globals.sessionId, \
                            response.decode()))

    def processCommand(self, command):
        '''The main function of this module. It is called from the I/O front
        ends to process SCPI commands.

        Args:
            command (bytes): The command that needs to be processed.

        Returns:
            Bytes: Response string to send back to user.
        '''
        # Log the command to SCPI monitor FIFO for display in GUI.
        self.logCommand(command)
        parsedCommand = ParseUtils.preParseCommand(command)
        #print (parsedCommand)
        response = command

        # Login and logout are handled as special cases.
        if parsedCommand[0].head.upper().startswith(b"LOGIN"):
            if self.globals.veexChassis:
                response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_USER_ALREADY_LOGGED_IN)
            else:
                # Must have two parameters for username and password
                if len(parsedCommand) > 2:
                    userName = parsedCommand[1].head.decode()
                    userPassword = parsedCommand[2].head.decode()

                    # Login with the username and password
                    try:
                        # Connect and login to the server on the chassis.
                        self.globals.veexChassis = veexlib.connect(self.globals.ipAddress, userName, userPassword)
                        self.globals.userName = parsedCommand[1].head

                        # Read the default response always setting from the server.
                        self.globals.respondAlways = self.globals.veexChassis.getScpiRespAlways()

                        # Read the default lock forced setting from the server.
                        self.globals.forceLock = self.globals.veexChassis.getScpiLockForcedOn()

                        # Read the autoLogin settings from a file.
                        try:
                            with open('autologin.pickle', 'rb') as f:
                                self.globals.autoLogin = pickle.load(f)
                        except FileNotFoundError as error:
                            # If file doesn't exist then use defaults already set.
                            pass
                        except pickle.UnpicklingError as error:
                            # If unpickle fails then use defaults already set.
                            pass

                        # Log the login command to SCPI monitor FIFO for
                        # display in GUI. Previous attempt failed due to
                        # self.globals.veexChassis not being there.
                        self.logCommand(command)

                        # Respond that the login worked.
                        response = b"Login successful, SID %d" % self.globals.sessionId
                    except veexlib.ConnectFailed as user:
                        print("connect failed", self.globals.ipAddress)
                        response = self._errorResponse(ScpiErrorCode.DLI_INVALID_IP_ADDRESS)
                    except veexlib.LoginFailed as address:
                        response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_USER_NOT_LOGGED_IN)
                    except veexlib.ServerException as serverExcept:
                        if serverExcept.reason == veexlib.EXCEPT_USER_UNAUTHORIZED:
                            response = self._errorResponse(ScpiErrorCode.DLI_USER_UNAUTHORIZED)
                        elif serverExcept.reason == veexlib.EXCEPT_ADMIN_USER_NOT_FOUND:
                            response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_USER_NOT_FOUND)
                        elif serverExcept.reason == veexlib.EXCEPT_ADMIN_USER_NOT_LOGGED_IN:
                            response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_USER_NOT_LOGGED_IN)
                        elif serverExcept.reason == veexlib.EXCEPT_ADMIN_INVALID_PASSWORD:
                            response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_INVALID_PASSWORD)
                        elif serverExcept.reason == veexlib.EXCEPT_ADMIN_INVALID_LOGIN_NAME:
                            response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_INVALID_LOGIN_NAME)
                        elif serverExcept.reason == veexlib.EXCEPT_ADMIN_REACHED_MAX_LOGGEDIN_USERS:
                            response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_REACHED_MAX_LOGGEDIN_USERS)
                        elif serverExcept.reason == veexlib.EXCEPT_ADMIN_USER_ALREADY_LOGGED_IN:
                            response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_USER_ALREADY_LOGGED_IN)
                else:
                    response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)

        elif parsedCommand[0].head.upper().startswith(b"LOGOUT") or \
             parsedCommand[0].head.upper().startswith(b"CLOSE"):
            if self.globals.veexChassis:
                # Cleanup before dropping connection. These will need to be
                # set this way for any following login.
                parsedCommand = ParseUtils.preParseCommand(b"INST NONE")
                response = self._processCommands(parsedCommand)
                parsedCommand = ParseUtils.preParseCommand(b"SYST:LOCK:FORCED OFF")
                response = self._processCommands(parsedCommand)

                # Log the logout response to SCPI monitor FIFO for display in
                # GUI. Later attempt will fail due to # self.globals.veexChassis
                # not being there.
                response = b"Logout successful, SID %d" % self.globals.sessionId;
                self.logResponse(response)

                self.globals.veexChassis = self.globals.veexChassis.disconnect()
                self.globals.userName = b""
            else:
                response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_USER_NOT_LOGGED_IN)
        else:
            # This is a normal command and needs to go through the
            # normal processing.
            if self.globals.veexChassis:
                response = self._processCommands(parsedCommand)
            else:
                response = self._errorResponse(ScpiErrorCode.DLI_ADMIN_USER_NOT_LOGGED_IN)

        # Handle returning a +0 for SYST:RESP ALWAYS.
        if ((not response) or (len(response) == 0)) and self.globals.respondAlways:
            response = b"+0"

        # Log the response to SCPI monitor FIFO for display in GUI.
        self.logResponse(response)

        return response


if __name__ == "__main__":
    pass

