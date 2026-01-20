###############################################################################
#
# Copyright 2018-2019, VeEX, Inc.
# All Rights Reserved.
#
# $Workfile:   ScpiSystem.py  $
# $Revision: 25603 $
# $Author: patrickellis $
# $Date: 2021-12-30 01:37:33 -0500 (Thu, 30 Dec 2021) $
#
# DESCRIPTION:
#    Module to process system wide SCPI commands. This is the python version
#    of ScpiProxyServer.cpp
#
###############################################################################

from ErrorCodes import ScpiErrorCode
from ErrorCodes import errorResponse
from ParseUtils import CommandTableEntry as Cmnd
from SessionGlobals import SessionGlobals
import pickle
import time
import ParseUtils
#import SessionGlobals
import veexlib

class ScpiSystem(object):
    #'''This class processes system SCPI commands (INST, GET:PROTO?, \*RST, etc)
    #and returns a text response.
    #
    #Args:
    #    globals (SessionGlobals object): Data class of session variables.
    #'''

    def __init__(self, globals):
        self.globals = globals


    def _errorResponse(self, errorCode):
        '''Handle legacy response when converting integer error codes to text.
        The utiltity that converts doesn't have access to the globals.

        Args:
            errorCode (int): ScpiErrorCode enum of the error
        '''
        return errorResponse(errorCode, self.globals)


    def processCommand(self, parsedCommand):
        #'''Processes a preparsed command that isn't login or logout. Calls the
        #INSTrument specific handler.
        #
        #Args:
        #    parsedCommand (List of SubCommand named tuples): The command that needs to be processed.
        #
        #Returns:
        #    (Bytes, bool): Tuple of response string to send back to user and
        #                   boolean flag of whether the command was found.
        #'''
        response = b""
        foundCommand = False

        # Search for the command.
        callback, parameters = ParseUtils.searchCommandTree(parsedCommand, \
                                                            commandTreeRoot)

        # If the command was found then call the handler function.
        if callback:
            response = callback(self, parameters)
            foundCommand = True

        # return the results.
        return (response, foundCommand)

    def clearStatusByte(self, parameters):
        '''**\*CLS"** -
        Allegedly is supposed to clear all SCPI registers but this actually
        has no effect.
        '''
        return b"0"

    def repSesByte(self, parameters):
        '''**\*ESR?"** -
        Query the Standard Event Status Register.
        '''
        if self.globals.errorQueue.errorCount() == 0:
            sesrReg = 0x00
        else:
            sesrReg = 0x20
        return ParseUtils.intToBinSdh(sesrReg)

    def identifySelf(self, parameters):
        '''**\*IDN?"** -
        Query the Identification Sequence.
        '''
        return bytes(self.globals.veexChassis.companyName, encoding='utf-8') + b", " + \
               bytes(self.globals.veexChassis.productName, encoding='utf-8') + b", " + \
               bytes(self.globals.veexChassis.productSerialNumber, encoding='utf-8') + b", " + \
               bytes(self.globals.veexChassis.featureSetVersion, encoding='utf-8')


    def setFactoryDefault(self, parameters):
        '''**\*RST <optional protocol mode>** -
        Set the test unit of the INST PP to factory default.
        '''
        # Save protocol for possible use at the end.
        previousProtocol = self.getProtocolMode(b"")

        if self.globals.veexProtocol and self.globals.veexProtocol.isLocked():
            # An INSTrument is selected and locked. Factory default the
            # selected PP and thus the test unit.
            self.globals.veexProtocol.updateTestUnit()
            self.globals.veexProtocol.setFactoryDefault()
        elif self.globals.veexProtocol:
            # Read-only INST selected, return an error.
            return self._errorResponse(ScpiErrorCode.DLI_INVALID_PP_MODE)
        else:
            # No INST selected. Factory default all the test units that are
            # not locked by someone else.
            for tu in self.globals.veexChassis.testUnits:
                # Call updateTestUnit() to be certain of getting current
                # lock data.
                tu.updateTestUnit()
                if tu.isLocked() or tu.isNotLocked():
                    tu.setFactoryDefault()

        # Give time for factory default to finish before changing protocol.
        time.sleep(2)

        paramList = ParseUtils.preParseParameters(parameters)
        if len(paramList) >= 1:
            # Set protocol mode to user specified setting.
            self.setProtocolMode(parameters)
        else:
            # No user setting, restore protocol mode to previous setting.
            self.setProtocolMode(previousProtocol)
        return self.getProtocolMode(b"")


    def setStop(self, parameters):
        '''**ABORt** -
        Same as GUI stop button.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        if (len(paramList) > 0) and paramList[0].head.upper().startswith(b"ALL"):
            # Loop through all the PPs
            for pp in self.globals.veexChassis.protocols:
                try:
                    # Call updateTestUnit() to be certain of getting current
                    # lock data.
                    pp.updateTestUnit()
                    pp.stop(requireLock = False, includeDelay = False)
                except veexlib.ProtocolNotLocked as error:
                    # PP wasn't locked so it can't be stopped, skip to next PP.
                    pass
            # Give some time for restart to settle. Needed because of setting
            # includeDelay parameter to false.
            time.sleep(3)
        elif len(paramList) > 0:
            # The PP is specified in the parameters, use common function to
            # find the PP.
            localGlobals = SessionGlobals(0, b"")
            errorCode = self.setInstCommon(parameters, localGlobals)
            if not errorCode or errorCode == ScpiErrorCode.DLI_NO_ERROR:
                # Found the specified PP, do the stop.
                try:
                    # Call updateTestUnit() to be certain of getting current
                    # lock data.
                    localGlobals.veexProtocol.updateTestUnit()
                    localGlobals.veexProtocol.stop(requireLock = False)
                except veexlib.ProtocolNotLocked as error:
                    # PP wasn't locked so it can't be stopped, return error.
                    response = self._errorResponse(DLI_PROTOMGR_TESTUNIT_LOCKED)
            else:
                response = self._errorResponse(errorCode)
        else:
            # Stop the INST selected PP. An INSTrument command must have
            # been issued.
            if self.globals.veexProtocol and self.globals.veexProtocol.isLocked():
                self.globals.veexProtocol.stop()
            else:
                response = self._errorResponse(ScpiErrorCode.DLI_INVALID_PP_MODE)

        return response

    def scpiDelay(self, parameters):
        '''**DELAY <milliSecs>** -
        Delay a number of milliSeconds.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        if len(paramList) > 0:
            if paramList[0].head.isdigit():
                milliSec = int(paramList[0].head)
                time.sleep(float(milliSec) * 0.001)
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)

    def getDuration(self, parameters):
        '''**DURation?** -
        Query the how long a test on the inst PP will run for.
        '''
        if self.globals.veexProtocol:
            self.globals.veexProtocol.stats.update()
            elapsedTime = self.globals.veexProtocol.stats.elapsedTime
            remainTime = self.globals.veexProtocol.stats.runTimeLeft
            if remainTime < 0:
                return b"CONTINUOUS"
            else:
                # Both elapsed and remaining time are returned by PP in secs.
                # Hence it needs to be converted to minutes before sending
                # the results to client
                duration = (elapsedTime + remainTime + 1) / 60
                return b"%d" % duration
        else:
            return self._errorResponse(ScpiErrorCode.DLI_INVALID_PP_MODE)

    def setDuration(self, parameters):
        '''**DURation** -
        Set the how long a test on the inst PP will run for and do an INIT
        restart.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        if len(paramList) > 0:
            if paramList[0].head.upper().startswith(b"CONTINUOUS"):
                testDuration = -1
            elif paramList[0].head.isdigit():
                testDuration = int(paramList[0].head) * 60
            else:
                return self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)

            # Do a restart with the new duration.
            if self.globals.veexProtocol:
                self.globals.veexProtocol.updateTestUnit()
                self.globals.veexProtocol.restart(testDuration)
            else:
                return self._errorResponse(ScpiErrorCode.DLI_INVALID_PP_MODE)
        else:
            return self._errorResponse(ScpiErrorCode.MISSING_PARAM)

    def getElapsedTime(self, parameters):
        '''**ELAPSEdtime?** -
        Query the how long the running test on the inst PP has been running.
        '''
        if self.globals.veexProtocol:
            self.globals.veexProtocol.stats.update()
            return b"%d" % self.globals.veexProtocol.stats.elapsedTime
        else:
            return self._errorResponse(ScpiErrorCode.DLI_INVALID_PP_MODE)

    def getPartNumbers(self, parameters):
        '''**GET:PARTnumbers?** -
        Return a list of part numbers for every board in the chassis.
        '''
        result = b""
        for cp in self.globals.veexChassis.cards:
            if cp.cardType == veexlib.CARD_OSA_PMD:
                cpName = b"OSA="
            elif cp.cardType == veexlib.CARD_IM_100:
                cpName = b"IM-100="
            elif cp.cardType == veexlib.CARD_OTDR:
                cpName = b"OTDR="
            elif cp.cardType == veexlib.CARD_OP_SWITCH:
                cpName = b"OPSW="
            elif cp.cardType == veexlib.CARD_SCM210:
                cpName = b"SCM-210="
            elif cp.cardType == veexlib.CARD_MPM10G:
                cpName = b"MPM-10G="
            elif cp.cardType == veexlib.CARD_MPM100G:
                cpName = b"MPM-100G="
            elif cp.cardType == veexlib.CARD_MPM100AR:
                cpName = b"MPM-100AR="
            elif cp.cardType == veexlib.CARD_MPM400G:
                cpName = b"MPM-400G="
            elif cp.cardType == veexlib.CARD_MPM400AR:
                cpName = b"MPM-400AR="
            elif cp.cardType == veexlib.CARD_MPM400DCO:
                cpName = b"MPM-400DCO="
            elif cp.cardType == veexlib.CARD_MPM600G:
                cpName = b"MPM-600G="
            elif cp.cardType == veexlib.CARD_SCM220:
                cpName = b"SCM-220="
            else:
                cpName = b"<unknown>="

            # Add card name and part number to result with comma when needed.
            if len(result) > 0:
                result += b","
            result += cpName + bytes(cp.partNumber, encoding='utf-8')

        # Add SC part number to result with comma when needed. NOTE: Not done
        # because original SCPI only does it for NICs.
        #if len(result) > 0:
        #    result += b","
        #result += b"SC=" + bytes(self.globals.veexChassis.scPartNumber, encoding='utf-8')

        return result

    def getProtocol(self, parameters):
        '''**GET:PROTOcol?** -
        Return a list of all the PPs in the chassis.
        '''
        result = b""
        for pp in self.globals.veexChassis.protocols:
            ppName = b""
            if pp.protocolType == veexlib.PROTO_PHY:
                # MPM10G card doesn't have an MLD in SCPI
                if (pp.cardType == veexlib.CARD_MPM100G) or \
                   (pp.cardType == veexlib.CARD_MPM100AR):
                    ppName = b"MPM100MLD"
                elif pp.cardType == veexlib.CARD_MPM400G:
                    ppName = b"MPM400GMLD"
                elif pp.cardType == veexlib.CARD_MPM400AR:
                    ppName = b"MPM400MLD"
                elif pp.cardType == veexlib.CARD_MPM400DCO:
                    ppName = b"MPM400MLD"
                elif pp.cardType == veexlib.CARD_MPM600G:
                    ppName = b"MPM600MLD"
            elif pp.protocolType == veexlib.PROTO_OTN:
                if pp.cardType == veexlib.CARD_MPM10G:
                    ppName = b"OTN"
                elif (pp.cardType == veexlib.CARD_MPM100G) or \
                     (pp.cardType == veexlib.CARD_MPM100AR):
                    ppName = b"MPM100OTN"
                elif pp.cardType == veexlib.CARD_MPM400G:
                    ppName = b"MPM400GOTN"
                elif pp.cardType == veexlib.CARD_MPM400AR:
                    ppName = b"MPM400OTN"
                elif pp.cardType == veexlib.CARD_MPM400DCO:
                    ppName = b"MPM400OTN"
                elif pp.cardType == veexlib.CARD_MPM600G:
                    ppName = b"MPM600OTN"
            elif pp.protocolType == veexlib.PROTO_SONET_SDH:
                if pp.cardType == veexlib.CARD_MPM10G:
                    ppName = b"SONETSDH"
                elif (pp.cardType == veexlib.CARD_MPM100G) or \
                     (pp.cardType == veexlib.CARD_MPM100AR):
                    ppName = b"MPM100SONETSDH"
                elif pp.cardType == veexlib.CARD_MPM400G:
                    ppName = b"MPM400GSONETSDH"
                elif pp.cardType == veexlib.CARD_MPM400AR:
                    ppName = b"MPM400SONETSDH"
                elif pp.cardType == veexlib.CARD_MPM400DCO:
                    ppName = b"MPM400SONETSDH"
                elif pp.cardType == veexlib.CARD_MPM600G:
                    ppName = b"MPM600SONETSDH"
            elif pp.protocolType == veexlib.PROTO_ETHERNET:
                if pp.cardType == veexlib.CARD_MPM10G:
                    ppName = b"PACKET"
                elif (pp.cardType == veexlib.CARD_MPM100G) or \
                     (pp.cardType == veexlib.CARD_MPM100AR):
                    ppName = b"MPM100PACKET"
                elif pp.cardType == veexlib.CARD_MPM400G:
                    ppName = b"MPM400GPACKET"
                elif pp.cardType == veexlib.CARD_MPM400AR:
                    ppName = b"MPM400PACKET"
                elif pp.cardType == veexlib.CARD_MPM400DCO:
                    ppName = b"MPM400PACKET"
                elif pp.cardType == veexlib.CARD_MPM600G:
                    ppName = b"MPM600PACKET"

            # Not every protocol has a SCPI counterpart (ie. PHY, OCS, and OTL
            # become just MLD in SCPI).
            if len(ppName) > 0:
                result += b"0 %d %d %s; " % (pp.slotId, pp.portId, ppName)

        return result

    def getSerialNumbers(self, parameters):
        '''**GET:SERialnumbers?** -
        Return a list of serial numbers for every board in the chassis.
        '''
        result = b""
        for cp in self.globals.veexChassis.cards:
            if cp.cardType == veexlib.CARD_OSA_PMD:
                cpName = b"OSA="
            elif cp.cardType == veexlib.CARD_IM_100:
                cpName = b"IM-100="
            elif cp.cardType == veexlib.CARD_OTDR:
                cpName = b"OTDR="
            elif cp.cardType == veexlib.CARD_OP_SWITCH:
                cpName = b"OPSW="
            elif cp.cardType == veexlib.CARD_SCM210:
                cpName = b"SCM-210="
            elif cp.cardType == veexlib.CARD_MPM10G:
                cpName = b"MPM-10G="
            elif cp.cardType == veexlib.CARD_MPM100G:
                cpName = b"MPM-100G="
            elif cp.cardType == veexlib.CARD_MPM100AR:
                cpName = b"MPM-100AR="
            elif cp.cardType == veexlib.CARD_MPM400G:
                cpName = b"MPM-400G="
            elif cp.cardType == veexlib.CARD_MPM400AR:
                cpName = b"MPM-400AR="
            elif cp.cardType == veexlib.CARD_MPM400DCO:
                cpName = b"MPM-400DCO="
            elif cp.cardType == veexlib.CARD_MPM600G:
                cpName = b"MPM-600G="
            elif cp.cardType == veexlib.CARD_SCM220:
                cpName = b"SCM-220="
            else:
                cpName = b"<unknown>="

            # Add card name and part number to result with comma when needed.
            if len(result) > 0:
                result += b","
            result += cpName + bytes(cp.serialNumber, encoding='utf-8')

        # Add SC part number to result with comma when needed. NOTE: Not done
        # because original SCPI only does it for NICs.
        #if len(result) > 0:
        #    result += b","
        #result += b"SC=" + bytes(self.globals.veexChassis.scSerialNumber, encoding='utf-8')

        return result

    def getVersions(self, parameters):
        '''**GET:VERsion?** -
        Return a list of version numbers for every board in the chassis as
        well as SC and SCPI software (SC means Corba for now).
        '''
        result = b""
        for cp in self.globals.veexChassis.cards:
            if cp.cardType == veexlib.CARD_OSA_PMD:
                cpName = b"OSA="
            elif cp.cardType == veexlib.CARD_IM_100:
                cpName = b"IM-100="
            elif cp.cardType == veexlib.CARD_OTDR:
                cpName = b"OTDR="
            elif cp.cardType == veexlib.CARD_OP_SWITCH:
                cpName = b"OPSW="
            elif cp.cardType == veexlib.CARD_SCM210:
                cpName = b"SCM-210="
            elif cp.cardType == veexlib.CARD_MPM10G:
                cpName = b"MPM-10G="
            elif cp.cardType == veexlib.CARD_MPM100G:
                cpName = b"MPM-100G="
            elif cp.cardType == veexlib.CARD_MPM100AR:
                cpName = b"MPM-100AR="
            elif cp.cardType == veexlib.CARD_MPM400G:
                cpName = b"MPM-400G="
            elif cp.cardType == veexlib.CARD_MPM400AR:
                cpName = b"MPM-400AR="
            elif cp.cardType == veexlib.CARD_MPM400DCO:
                cpName = b"MPM-400DCO="
            elif cp.cardType == veexlib.CARD_MPM600G:
                cpName = b"MPM-600G="
            elif cp.cardType == veexlib.CARD_SCM220:
                cpName = b"SCM-220="
            else:
                cpName = b"<unknown>="

            # Add card name and part number to result with comma when needed.
            if len(result) > 0:
                result += b","
            result += cpName + bytes(cp.softwareVersion, encoding='utf-8')

        # Add SC part number to result with comma when needed.
        if len(result) > 0:
            result += b","
        result += b"SC=" + bytes(self.globals.veexChassis.scSoftwareVersion, encoding='utf-8')

        # Add SCPI part number to result with comma when needed.
        if len(result) > 0:
            result += b","
        result += b"SCPI=" + bytes(self.globals.veexChassis.scpiSoftwareVersion, encoding='utf-8')

        return result

    def setRestart(self, parameters):
        '''**INITiate** -
        Same as GUI restart button.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        if (len(paramList) > 0) and paramList[0].head.upper().startswith(b"ALL"):
            # Loop through all the PPs
            for pp in self.globals.veexChassis.protocols:
                try:
                    # Call updateTestUnit() to be certain of getting current
                    # lock data.
                    pp.updateTestUnit()
                    pp.restart(duration = -1, requireLock = False, \
                               includeDelay = False)
                except veexlib.ProtocolNotLocked as error:
                    # PP wasn't locked so it can't be restarted, skip to next PP.
                    pass
            # Give some time for restart to settle. Needed because of setting
            # includeDelay parameter to false.
            time.sleep(3)
        elif len(paramList) > 0:
            # The PP is specified in the parameters, use common function to
            # find the PP.
            localGlobals = SessionGlobals(0, b"")
            errorCode = self.setInstCommon(parameters, localGlobals)
            if not errorCode or errorCode == ScpiErrorCode.DLI_NO_ERROR:
                # Found the specified PP, do the restart.
                try:
                    # Call updateTestUnit() to be certain of getting current
                    # lock data.
                    localGlobals.veexProtocol.updateTestUnit()
                    localGlobals.veexProtocol.restart(duration = -1, \
                                                      requireLock = False)
                except veexlib.ProtocolNotLocked as error:
                    # PP wasn't locked so it can't be stopped, return error.
                    response = self._errorResponse(ScpiErrorCode.DLI_PROTOMGR_TESTUNIT_LOCKED)
            else:
                response = self._errorResponse(errorCode)
        else:
            # Restart the INST selected PP. An INSTrument command must have
            # been issued.
            if self.globals.veexProtocol and self.globals.veexProtocol.isLocked():
                self.globals.veexProtocol.restart(duration = -1)
            else:
                response = self._errorResponse(ScpiErrorCode.DLI_INVALID_PP_MODE)

        return response

    def getInst(self, parameters):
        '''**INSTrument?** or **INS\_?** -
        Query which PP is selected from the chassis.
        '''
        result = b""
        ppName = b""
        if self.globals.protocolType == veexlib.PROTO_PHY:
            pp = self.globals.veexPhy
            # MPM10G card doesn't have an MLD in SCPI
            if (pp.cardType == veexlib.CARD_MPM100G) or \
               (pp.cardType == veexlib.CARD_MPM100AR):
                ppName = b"MPM100MLD"
            elif pp.cardType == veexlib.CARD_MPM400G:
                ppName = b"MPM400GMLD"
            elif pp.cardType == veexlib.CARD_MPM400AR:
                ppName = b"MPM400MLD"
            elif pp.cardType == veexlib.CARD_MPM400DCO:
                ppName = b"MPM400MLD"
            elif pp.cardType == veexlib.CARD_MPM600G:
                ppName = b"MPM600MLD"
        elif self.globals.protocolType == veexlib.PROTO_OTN:
            pp = self.globals.veexOtn
            if pp.cardType == veexlib.CARD_MPM10G:
                ppName = b"OTN"
            elif (pp.cardType == veexlib.CARD_MPM100G) or \
                 (pp.cardType == veexlib.CARD_MPM100AR):
                ppName = b"MPM100OTN"
            elif pp.cardType == veexlib.CARD_MPM400G:
                ppName = b"MPM400GOTN"
            elif pp.cardType == veexlib.CARD_MPM400AR:
                ppName = b"MPM400OTN"
            elif pp.cardType == veexlib.CARD_MPM400DCO:
                ppName = b"MPM400OTN"
            elif pp.cardType == veexlib.CARD_MPM600G:
                ppName = b"MPM600OTN"
        elif self.globals.protocolType == veexlib.PROTO_SONET_SDH:
            pp = self.globals.veexSonetSdh
            if pp.cardType == veexlib.CARD_MPM10G:
                ppName = b"SONETSDH"
            elif (pp.cardType == veexlib.CARD_MPM100G) or \
                 (pp.cardType == veexlib.CARD_MPM100AR):
                ppName = b"MPM100SONETSDH"
            elif pp.cardType == veexlib.CARD_MPM400G:
                ppName = b"MPM400GSONETSDH"
            elif pp.cardType == veexlib.CARD_MPM400AR:
                ppName = b"MPM400SONETSDH"
            elif pp.cardType == veexlib.CARD_MPM400DCO:
                ppName = b"MPM400SONETSDH"
            elif pp.cardType == veexlib.CARD_MPM600G:
                ppName = b"MPM600SONETSDH"
        elif self.globals.protocolType == veexlib.PROTO_ETHERNET:
            pp = self.globals.veexEthernet
            if pp.cardType == veexlib.CARD_MPM10G:
                ppName = b"PACKET"
            elif (pp.cardType == veexlib.CARD_MPM100G) or \
                 (pp.cardType == veexlib.CARD_MPM100AR):
                ppName = b"MPM100PACKET"
            elif pp.cardType == veexlib.CARD_MPM400G:
                ppName = b"MPM400GPACKET"
            elif pp.cardType == veexlib.CARD_MPM400AR:
                ppName = b"MPM400PACKET"
            elif pp.cardType == veexlib.CARD_MPM400DCO:
                ppName = b"MPM400PACKET"
            elif pp.cardType == veexlib.CARD_MPM600G:
                ppName = b"MPM600PACKET"

        # Not every protocol has a SCPI counterpart (ie. PHY, OCS, and OTL
        # become just MLD in SCPI).
        if len(ppName) > 0:
            result += b"0 %d %d %s" % (pp.slotId, pp.portId, ppName)
        else:
            result = b"NONE"
        return result

    def setInstLock(self, parameters):
        '''**INSTrument** -
        Select a PP from the chassis and lock it.
        '''
        previousPp = self.globals.veexProtocol
        errorCode = self.setInstCommon(parameters, self.globals)
        if not errorCode or errorCode == ScpiErrorCode.DLI_NO_ERROR:
            # the INST is selected, need to try and get the lock.

            # New PP is selected (or NONE), unlock the previous PP.
            if previousPp:
                # Unlock only if test unit changed or set to none.
                if (not self.globals.veexProtocol) or \
                   (self.globals.veexProtocol.testUnitId != previousPp.testUnitId):
                    previousPp.unlock()

            if self.globals.veexProtocol:
                # Lock the selected PP, use forceLock flag.
                if self.globals.forceLock:
                    locked = self.globals.veexProtocol.lock(forced=True)
                else:
                    locked = self.globals.veexProtocol.lock(forced=False)

                # If lock succeeded then return nothing, otherwise a message 
                if locked:
                    response = b""
                else:
                    response = b'"Test unit is locked.  Only read commands may be performed."'
            else:
                # If no pp is selected the the INST must have been to NONE.
                response = b""
        else:
            response = self._errorResponse(errorCode)
        return response

    def setInstNoLock(self, parameters):
        '''**INS\_** -
        Select a PP from the chassis but don't lock it.
        '''
        previousPp = self.globals.veexProtocol
        errorCode = self.setInstCommon(parameters, self.globals)
        if not errorCode or errorCode == ScpiErrorCode.DLI_NO_ERROR:
            # Setting inst succeeded, unlock previous PP and return special
            # response.
            if previousPp:
                # Unlock only if test unit changed or set to none.
                if (not self.globals.veexProtocol) or \
                   (self.globals.veexProtocol.testUnitId != previousPp.testUnitId):
                    previousPp.unlock()
            response = b'"Only read commands may be performed."'
        else:
            response = self._errorResponse(errorCode)
        return response

    def setInstCommon(self, parameters, globalObject):
        #'''Utility function used by several commands where parsing parameters to
        #select a PP from the chassis is needed. Examples are INST, INST\_, INIT
        #and ABOR.
        #'''
        paramList = ParseUtils.preParseParameters(parameters)
        if len(paramList) > 4:
            return ScpiErrorCode.MISSING_PARAM
        elif len(paramList) < 1:
            return ScpiErrorCode.MISSING_PARAM
        else:
            # Correct number of parameters is 1..4
            ppName = paramList[len(paramList) - 1].head.upper()
            ppType = veexlib.PROTO_ZERO
            try:
                if len(paramList) == 1:
                    ppChassis = 0
                    ppSlot    = -1
                    ppPort    = -1
                elif len(paramList) == 2:
                    ppChassis = 0
                    ppSlot    = int(paramList[0].head)
                    ppPort    = -1
                elif len(paramList) == 3:
                    ppChassis = 0
                    ppSlot    = int(paramList[0].head)
                    ppPort    = int(paramList[1].head)
                else:
                    ppChassis = int(paramList[0].head)
                    ppSlot    = int(paramList[1].head)
                    ppPort    = int(paramList[2].head)
                    # The chassis must be zero for all MPA chassis.
                    if ppChassis != 0:
                        return ScpiErrorCode.ILLEGAL_PARAM_VALUE
            except ValueError as error:
                return ScpiErrorCode.DATA_TYPE_ERR


            # Convert ppName to ppType
            # MPM10G card doesn't have an MLD in SCPI
            if ppName.startswith(b"MPM100MLD"):
                cardType = veexlib.CARD_MPM100G
                ppType = veexlib.PROTO_PHY
            elif ppName.startswith(b"MPM400GMLD"):
                cardType = veexlib.CARD_MPM400G
                ppType = veexlib.PROTO_PHY
            elif ppName.startswith(b"MPM400MLD"):
                cardType = veexlib.CARD_MPMP400AR
                ppType = veexlib.PROTO_PHY
            elif ppName.startswith(b"MPM600MLD"):
                cardType = veexlib.CARD_MPM600G
                ppType = veexlib.PROTO_PHY

            elif ppName.startswith(b"OTN"):
                cardType = veexlib.CARD_MPM10G
                ppType = veexlib.PROTO_OTN
            elif ppName.startswith(b"MPM100OTN"):
                cardType = veexlib.CARD_MPM100G
                ppType = veexlib.PROTO_OTN
            elif ppName.startswith(b"MPM400GOTN"):
                cardType = veexlib.CARD_MPM400G
                ppType = veexlib.PROTO_OTN
            elif ppName.startswith(b"MPM400OTN"):
                cardType = veexlib.CARD_MPMP400AR
                ppType = veexlib.PROTO_OTN
            elif ppName.startswith(b"MPM600OTN"):
                cardType = veexlib.CARD_MPM600G
                ppType = veexlib.PROTO_OTN

            elif ppName.startswith(b"SONETSDH"):
                cardType = veexlib.CARD_MPM10G
                ppType = veexlib.PROTO_SONET_SDH
            elif ppName.startswith(b"MPM100SONETSDH"):
                cardType = veexlib.CARD_MPM100G
                ppType = veexlib.PROTO_SONET_SDH
            elif ppName.startswith(b"MPM400GSONETSDH"):
                cardType = veexlib.CARD_MPMP400AR
                ppType = veexlib.PROTO_SONET_SDH
            elif ppName.startswith(b"MPM400SONETSDH"):
                cardType = veexlib.CARD_MPM400G
                ppType = veexlib.PROTO_SONET_SDH
            elif ppName.startswith(b"MPM600SONETSDH"):
                cardType = veexlib.CARD_MPM600G
                ppType = veexlib.PROTO_SONET_SDH

            elif ppName.startswith(b"PACKET"):
                cardType = veexlib.CARD_MPM10G
                ppType = veexlib.PROTO_ETHERNET
            elif ppName.startswith(b"MPM100PACKET"):
                cardType = veexlib.CARD_MPM100G
                ppType = veexlib.PROTO_ETHERNET
            elif ppName.startswith(b"MPM400GPACKET"):
                cardType = veexlib.CARD_MPM400G
                ppType = veexlib.PROTO_ETHERNET
            elif ppName.startswith(b"MPM400PACKET"):
                cardType = veexlib.CARD_MPMP400AR
                ppType = veexlib.PROTO_ETHERNET
            elif ppName.startswith(b"MPM600PACKET"):
                cardType = veexlib.CARD_MPM600G
                ppType = veexlib.PROTO_ETHERNET
            elif ppName.startswith(b"NONE"):
#                ppType = veexlib.PROTO_ZERO
                globalObject.veexProtocol  = None
                globalObject.veexPhy       = None
                globalObject.veexPcs       = None
                globalObject.veexOtl       = None
                globalObject.veexOtn       = None
                globalObject.veexSonetSdh  = None
                globalObject.veexGfp       = None
                globalObject.veexEthernet  = None
                globalObject.veexFibreChan = None
                globalObject.protocolType  = veexlib.PROTO_ZERO
                return ScpiErrorCode.DLI_NO_ERROR
            else:
                return ScpiErrorCode.DATA_TYPE_ERR

            # Now know ppChassis, ppSlot, ppPort, cardType, and ppType. Need to
            # get # veexPhy, veexPcs, veexOtl, veexOtn, veexSonetSdh, veexGfp,
            # veexEthernet, and veexFibreChan for putting into globalObject.

            portObj = None
            veexProtocol = None
            if ppSlot < 0:
                # No slot or port given. Search for the first PP that has
                # matching ppType and cardType.
                for pp in self.globals.veexChassis.protocols:
                    if (pp.protocolType == ppType) and \
                       ((pp.cardType    == cardType) or \
                        ((pp.cardType == veexlib.CARD_MPM100AR) and \
                         (cardType    == veexlib.CARD_MPM100G))):
                        ppSlot = pp.slotId
                        ppPort = pp.portId
                        portObj = pp.getPort()
                        veexProtocol = pp
                        break
            elif ppPort < 0:
                # Only specified slot, not port. Search for the first PP
                # in the slot that has matching ppSlot, ppType, and cardType.
                for pp in self.globals.veexChassis.protocols:
                    if (pp.slotId       == ppSlot) and \
                       (pp.protocolType == ppType) and \
                       ((pp.cardType    == cardType) or \
                        ((pp.cardType == veexlib.CARD_MPM100AR) and \
                         (cardType    == veexlib.CARD_MPM100G))):
                        ppPort = pp.portId
                        portObj = pp.getPort()
                        veexProtocol = pp
                        break
            else:
                # Specified slot and port. Search for the first PP with
                # matching ppSlot, ppPort, ppType, and cardType.
                for pp in self.globals.veexChassis.protocols:
                    if (pp.slotId       == ppSlot) and \
                       (pp.portId       == ppPort) and \
                       (pp.protocolType == ppType) and \
                       ((pp.cardType    == cardType) or \
                        ((pp.cardType == veexlib.CARD_MPM100AR) and \
                         (cardType    == veexlib.CARD_MPM100G))):
                        portObj = pp.getPort()
                        veexProtocol = pp
                        break

            if portObj:
                # Get the PP references out of the port object.
                veexPhy       = None
                veexPcs       = None
                veexOtl       = None
                veexOtn       = None
                veexSonetSdh  = None
                veexGfp       = None
                veexEthernet  = None
                veexFibreChan = None
                for pp in portObj.protocols:
                    if pp.protocolType == veexlib.PROTO_PHY and not veexPhy:
                        veexPhy       = pp
                    elif pp.protocolType == veexlib.PROTO_OTL and not veexPcs:
                        veexPcs       = pp
                    elif pp.protocolType == veexlib.PROTO_PCS and not veexOtl:
                        veexOtl       = pp
                    elif pp.protocolType == veexlib.PROTO_OTN and not veexOtn:
                        veexOtn       = pp
                    elif pp.protocolType == veexlib.PROTO_SONET_SDH and not veexSonetSdh:
                        veexSonetSdh  = pp
                    elif pp.protocolType == veexlib.PROTO_GFP and not veexGfp:
                        veexGfp       = pp
                    elif pp.protocolType == veexlib.PROTO_ETHERNET and not veexEthernet:
                        veexEthernet  = pp
                    elif pp.protocolType == veexlib.PROTO_FIBRECHAN and not veexFibreChan:
                        veexFibreChan = pp

                # Have all the data, copy into globals.
                globalObject.veexProtocol  = veexProtocol
                globalObject.veexPhy       = veexPhy
                globalObject.veexPcs       = veexPcs
                globalObject.veexOtl       = veexOtl
                globalObject.veexOtn       = veexOtn
                globalObject.veexSonetSdh  = veexSonetSdh
                globalObject.veexGfp       = veexGfp
                globalObject.veexEthernet  = veexEthernet
                globalObject.veexFibreChan = veexFibreChan
                globalObject.protocolType  = ppType

                # Alias for Packet SCPI handlers: use veexPacket as Ethernet PP
                if veexEthernet is not None:
                    try:
                        globalObject.veexPacket = veexEthernet
                    except Exception:
                        # SessionGlobals may not predefine veexPacket; assign dynamically
                        setattr(globalObject, 'veexPacket', veexEthernet)

                return ScpiErrorCode.DLI_NO_ERROR
            else:
                # No matching pp was found, return an error.
                return ScpiErrorCode.INVALID_SETTINGS

    def saveReport(self, parameters):
        '''**SAVEREPORT** -
        Select a port from the chassis and save a printed report for that port
        to given filename. All options are reported.
        '''
        print(parameters)
        paramList = ParseUtils.preParseParameters(parameters)
        if len(paramList) > 4:
            return self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        elif len(paramList) < 3:
            return self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        else:
            # Correct number of parameters is 3 or 4
            try:
                if len(paramList) == 3:
                    paramChassis  = 0
                    paramSlot     = int(paramList[0].head)
                    paramPort     = int(paramList[1].head)
                    paramFilename = paramList[2].head
                else:
                    paramChassis  = int(paramList[0].head)
                    paramSlot     = int(paramList[1].head)
                    paramPort     = int(paramList[2].head)
                    paramFilename = paramList[3].head
                    # The chassis must be zero for all MPA chassis.
                    if paramChassis != 0:
                        return self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            except ValueError as error:
                return self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)

            # Now know slot, port, and filename. That is all that is needed.
            try:
                portRequest = self.globals.veexChassis.ReportPortRequest( \
                              self.globals.veexChassis.getPort(paramSlot, paramPort))
            except veexlib.Exceptions.PortNotFound:
                return self._errorResponse(ScpiErrorCode.DLI_PP_NOT_PRESENT)
            status = self.globals.veexChassis.saveReport(paramFilename, [portRequest,])

            if status == veexlib.REPORT_COMPLETE:
                return b"";
            elif status == veexlib.REPORT_IN_PROGRESS:
                return b"";
            elif status == veexlib.REPORT_FAILED:
                return self._errorResponse(ScpiErrorCode.CMD_WRITE_ERR)
            elif status == veexlib.REPORT_BAD_FILENAME:
                return self._errorResponse(ScpiErrorCode.DLI_FILE_IO_FAIL)
            else:
                return self._errorResponse(ScpiErrorCode.CMD_WRITE_ERR)


    def getCpLicense(self, parameters):
        '''**LICense?** -
        Query the license on the inst CP.
        '''
        if self.globals.veexProtocol:
            return bytes(self.globals.veexProtocol.getPort().card.getLicense(), encoding='utf-8')
        else:
            return self._errorResponse(ScpiErrorCode.DLI_INVALID_PP_MODE)

    def setCpLicense(self, parameters):
        '''**LICense** -
        Set the license on the inst CP.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        if len(paramList) >= 1:
            if self.globals.veexProtocol:
                status = self.globals.veexProtocol.getPort().card.setLicense(paramList[0].head.upper())
                if status == veexlib.LICENSE_SUCCESS:
                    return b"OK"
                elif status == veexlib.LICENSE_UNSUPPORTED:
                    return b"Licensing not supportted by CP"
                elif status == veexlib.LICENSE_DECODE_FAIL:
                    return b"License string decode failed"
                elif status == veexlib.LICENSE_CHECKSUM_FAIL:
                    return b"License checksum failed"
                elif status == veexlib.LICENSE_CP_SW_TYPE_FAIL:
                    return b"License CP type didn't match real CP"
                elif status == veexlib.LICENSE_SERIAL_NUM_FAIL:
                    return b"License serial number didn't match real CP"
                elif status == veexlib.LICENSE_DATE_FAIL:
                    return b"License date misformatted"
                elif status == veexlib.LICENSE_EXPIRED_FAIL:
                    return b"License already expired"
                elif status == veexlib.LICENSE_SEEPROM_FAIL:
                    return b"License store to SEEPROM failed"
                elif status == veexlib.LICENSE_UNKNOWN_FAIL:
                    return b"Unknown failure"
                else:
                    return b"Unknown failure"
            else:
                return self._errorResponse(ScpiErrorCode.DLI_INVALID_PP_MODE)
        else:
            return self._errorResponse(ScpiErrorCode.MISSING_PARAM)

    def getProtocolMode(self, parameters):
        '''**PROTOCOL?** -
        Query the protocol mode. ie SONET or SDH.
        '''
        if self.globals.veexProtocol:
            # Get mode of the INST selected PP.
            tu = self.globals.veexProtocol.testUnit
        else:
            # Get mode of first test unit.
            tu = self.globals.veexChassis.testUnits[0]

        # Find out which protocol modes this test unit supports and only
        # report those.
        hasSonetSdh = False
        hasPdh = False
        tu.updateTestUnit()
        for pp in tu.protocols:
            if pp.protocolType == veexlib.PROTO_SONET_SDH:
                hasSonetSdh = True
            elif pp.protocolType == veexlib.PROTO_T1E1:
                hasPdh = True
            elif pp.protocolType == veexlib.PROTO_T3E3E4:
                hasPdh = True

        # Convert mode of test unit to a string.
        if hasPdh:
            if hasSonetSdh:
                if tu.protocolIsSonet():
                    if tu.protocolIsE1():
                        if tu.protocolIsE3():
                            response = b"SONET_E1_E3"
                        else:
                            response = b"SONET_E1_DS3"
                    else:
                        if tu.protocolIsE3():
                            response = b"SONET_DS1_E3"
                        else:
                            response = b"SONET_DS1_DS3"
                else:
                    if tu.protocolIsE1():
                        if tu.protocolIsE3():
                            response = b"SDH_E1_E3"
                        else:
                            response = b"SDH_E1_DS3"
                    else:
                        if tu.protocolIsE3():
                            response = b"SDH_DS1_E3"
                        else:
                            response = b"SDH_DS1_DS3"
            else:
                if tu.protocolIsE1():
                    if tu.protocolIsE3():
                        response = b"E1_E3"
                    else:
                        response = b"E1_DS3"
                else:
                    if tu.protocolIsE3():
                        response = b"DS1_E3"
                    else:
                        response = b"DS1_DS3"
        elif hasSonetSdh:
            if tu.protocolIsSonet():
                response = b"SONET"
            else:
                response = b"SDH"
        else:
            response = b"+0"
        return response

    def setProtocolMode(self, parameters):
        '''**PROTOCOL <protocol mode>** -
        Set the protocol mode. ie SONET or SDH.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        setSonet = False
        setDs3   = False
        setDs1   = False
        setSdh   = False
        setE3    = False
        setE1    = False
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"SONET_DS1_DS3"):
                setSonet = True
                setDs3   = True
                setDs1   = True
            elif paramList[0].head.upper().startswith(b"SONET_E1_DS3"):
                setSonet = True
                setDs3   = True
                setE1    = True
            elif paramList[0].head.upper().startswith(b"SONET_E1_E3"):
                setSonet = True
                setE3    = True
                setE1    = True
            elif paramList[0].head.upper().startswith(b"SDH_DS1_DS3"):
                setSdh   = True
                setDs3   = True
                setDs1   = True
            elif paramList[0].head.upper().startswith(b"SDH_E1_DS3"):
                setSdh   = True
                setDs3   = True
                setE1    = True
            elif paramList[0].head.upper().startswith(b"SDH_E1_E3"):
                setSdh   = True
                setE3    = True
                setE1    = True
            elif paramList[0].head.upper().startswith(b"DS1_DS3"):
                setDs3   = True
                setDs1   = True
            elif paramList[0].head.upper().startswith(b"E1_DS3"):
                setDs3   = True
                setE1    = True
            elif paramList[0].head.upper().startswith(b"E1_E3"):
                setE3    = True
                setE1    = True
            elif paramList[0].head.upper().startswith(b"SONET"):
                setSonet = True
            elif paramList[0].head.upper().startswith(b"SDH"):
                setSdh   = True
            else:
                return self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            return self._errorResponse(ScpiErrorCode.MISSING_PARAM)

        if self.globals.veexProtocol:
            # Set mode of the INST selected PP.
            tuList = [self.globals.veexProtocol.testUnit]
        else:
            # Set mode of all the test units that are
            # not locked by someone else.
            tuList = self.globals.veexChassis.testUnits

        # Loop through the selected test unit(s) and set the mode for each.
        for tu in tuList:
            tu.updateTestUnit()
            if tu.isLocked() or tu.isNotLocked():
                if setSonet and tu.protocolIsSdh():   tu.setProtocolToSonet()
                if setSdh   and tu.protocolIsSonet(): tu.setProtocolToSdh()
                if setDs3   and tu.protocolIsE3():    tu.setProtocolToDs3()
                if setE3    and tu.protocolIsDs3():   tu.setProtocolToE3()
                if setDs1   and tu.protocolIsE1():    tu.setProtocolToDs1()
                if setE1    and tu.protocolIsDs1():   tu.setProtocolToE1()
                tu.updateTestUnit()

        # Give time for protocol change to finish before returning.
        time.sleep(5)


    def getRemainingTime(self, parameters):
        '''**REMAINingtime?** -
        Query the how long before the running test on the inst PP stops.
        '''
        if self.globals.veexProtocol:
            self.globals.veexProtocol.stats.update()
            if self.globals.veexProtocol.stats.runTimeLeft < 0:
                return b"CONTINUOUS"
            else:
                return b"%d" % self.globals.veexProtocol.stats.runTimeLeft
        else:
            return self._errorResponse(ScpiErrorCode.DLI_INVALID_PP_MODE)

    def getScpi(self, parameters):
        '''**SCPI?** -
        Always returns "YES" to tell if user is still connected to SCPI.
        '''
        return b"YES"

    def getCpTimedLicense(self, parameters):
        '''**TIMLIC?** -
        Query the timed license on the inst CP.
        '''
        if self.globals.veexProtocol:
            timedLicense = self.globals.veexProtocol.getPort().card.getTimedLicense()
            if timedLicense.status == veexlib.TIMED_LICENSE_INVALID:
                status = b"Unused"
            elif timedLicense.status == veexlib.TIMED_LICENSE_IN_USE:
                status = b"InUse"
            elif timedLicense.status == veexlib.TIMED_LICENSE_IN_FUTURE:
                status = b"InFuture"
            elif timedLicense.status == veexlib.TIMED_LICENSE_ON_REBOOT:
                status = b"OnReboot"
            else:
                status = b"Unused"


            if (timedLicense.stopMonth < timedLicense.startMonth) or \
               ((timedLicense.stopMonth == timedLicense.startMonth) and \
                (timedLicense.stopDay < timedLicense.startDay)):
                # The stop year is startYear + 1
                stopYear = timedLicense.startYear + 1
            else:
                stopYear = timedLicense.startYear

            return b'"%s", %02d/%02d/%d, %02d/%02d/%d, %s' % \
                       (#b"****************************************", \
                        bytes(timedLicense.codedString, encoding='utf-8'), \
                        timedLicense.startMonth, \
                        timedLicense.startDay, \
                        timedLicense.startYear, \
                        timedLicense.stopMonth, \
                        timedLicense.stopDay, \
                        stopYear, status)
        else:
            return self._errorResponse(ScpiErrorCode.DLI_INVALID_PP_MODE)

    def restoreSettings(self, parameters):
        '''**SET:RESTore** -
        Restore settings from a file.
        **UNIMPLEMENTED**.
        '''
        return self._errorResponse(ScpiErrorCode.CMD_ERR)

    def saveSettings(self, parameters):
        '''**SET:SAVE** -
        Save settings to a file.
        **UNIMPLEMENTED**.
        '''
        return self._errorResponse(ScpiErrorCode.CMD_ERR)

    def setAutoLoginDetails(self, parameters):
        '''**SYSTem:AUTOLOGIN:DETails <username password>** -
        Sets the username and password to use when auto login is enabled.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 2:
            self.globals.autoLogin.username = paramList[0].head
            self.globals.autoLogin.password = paramList[1].head
            try:
                with open('autologin.pickle', 'wb') as f:
                    pickle.dump(self.globals.autoLogin, f)
            except OSError as error:
                # If file can't be opened then not much we can do.
                pass
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getAutoLoginUser(self, parameters):
        '''**SYSTem:AUTOLOGIN:USER?** -
        Query the username used when auto login is enabled. There is no way
        to query the password.
        '''
        return self.globals.autoLogin.username

    def getAutoLoginEnable(self, parameters):
        '''**SYSTem:AUTOLOGIN:VALue?** -
        Query auto login is enabled state.
        '''
        if self.globals.autoLogin.enabled:
            return b"TRUE"
        else:
            return b"FALSE"

    def setAutoLoginEnable(self, parameters):
        '''**SYSTem:AUTOLOGIN:VALue <TRUE|FALSE>** -
        Sets the auto login enable/disable state.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"TRUE"):
                self.globals.autoLogin.enabled = True
                try:
                    with open('autologin.pickle', 'wb') as f:
                        pickle.dump(self.globals.autoLogin, f)
                except OSError as error:
                    # If file can't be opened then not much we can do.
                    pass
            elif paramList[0].head.upper().startswith(b"FALSE"):
                self.globals.autoLogin.enabled = False
                try:
                    with open('autologin.pickle', 'wb') as f:
                        pickle.dump(self.globals.autoLogin, f)
                except OSError as error:
                    # If file can't be opened then not much we can do.
                    pass
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getSystClock(self, parameters):
        '''**SYSTem:CLOCK?** -
        Query the setting of the chassis clock.
        '''
        systemClock = self.globals.veexChassis.chassisClock
        if systemClock == veexlib.SYS_CLOCK_SETS:
            return b"SETS (2.048 Mbps)"
        elif systemClock == veexlib.SYS_CLOCK_BITS:
            return b"BITS (1.544 Mbps)"
        elif systemClock == veexlib.SYS_CLOCK_2048_SINE:
            return b"SETS (2.048 Mbps Sine)"
        elif systemClock == veexlib.SYS_CLOCK_1544_SINE:
            return b"BITS (1.544 Mbps Sine)"
        elif systemClock == veexlib.SYS_CLOCK_INTERNAL_NO_OUTPUT:
            return b"INTERNAL"
        elif systemClock == veexlib.SYS_CLOCK_INTERNAL_SETS:
            return b"INT_SETS"
        elif systemClock == veexlib.SYS_CLOCK_INTERNAL_BITS:
            return b"INT_BITS"
        elif systemClock == veexlib.SYS_CLOCK_INTERNAL_2048_SINE:
            return b"INT_SETSSINE"
        elif systemClock == veexlib.SYS_CLOCK_INTERNAL_1544_SINE:
            return b"INT_BITSSINE"
        elif systemClock == veexlib.SYS_CLOCK_GPS_NO_OUTPUT:
            return b"GPS"
        elif systemClock == veexlib.SYS_CLOCK_SMA_1544_NO_OUTPUT:
            return b"SMA_1544_NO_OUT"
        elif systemClock == veexlib.SYS_CLOCK_SMA_2048_NO_OUTPUT:
            return b"SMA_2048_NO_OUT"
        elif systemClock == veexlib.SYS_CLOCK_SMA_1544_IN_OUT:
            return b"SMA_1544"
        elif systemClock == veexlib.SYS_CLOCK_SMA_2048_IN_OUT:
            return b"SMA_2048"
        elif systemClock == veexlib.SYS_CLOCK_SMA_10M_IN_OUT:
            return b"SMA_10M"
        elif systemClock == veexlib.SYS_CLOCK_SMA_1PPS_IN_OUT:
            return b"SMA_1PPS"
        elif systemClock == veexlib.SYS_CLOCK_INTERNAL_10M_OUT:
            return b"INT_10M"
        elif systemClock == veexlib.SYS_CLOCK_INTERNAL_1PPS_OUT:
            return b"INT_1PPS"
        elif systemClock == veexlib.SYS_CLOCK_SMA_10M_IN_1PPS_OUT:
            return b"SMA_10M_1PPS"
        elif systemClock == veexlib.SYS_CLOCK_SMA_1PPS_IN_10M_OUT:
            return b"SMA_1PPS_10M"
        elif systemClock == veexlib.SYS_CLOCK_GPS_IN_1PPS_OUT:
            return b"GPS_1PPS"
        elif systemClock == veexlib.SYS_CLOCK_GPS_IN_2048_OUT:
            return b"GPS_2048"
        elif systemClock == veexlib.SYS_CLOCK_GPS_IN_1544_OUT:
            return b"GPS_1544"
        elif systemClock == veexlib.SYS_CLOCK_GPS_IN_10M_OUT:
            return b"GPS_10M"
        else:
            return b"NO EXTERNAL"

    def setSystClock(self, parameters):
        '''**SYSTem:CLOCK** -
        Set the setting of the chassis clock.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        if len(paramList) >= 1:
            mchType = self.globals.veexChassis.mchType
            scpiCmd = paramList[0].head.upper()
            if mchType == veexlib.MCH_SCM:
                if scpiCmd == b"INTERNAL":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_INTERNAL_NO_OUTPUT
                elif scpiCmd == b"INT_SETS":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_INTERNAL_SETS
                elif scpiCmd == b"INT_BITS":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_INTERNAL_BITS
                elif scpiCmd == b"INT_SETSSINE":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_INTERNAL_2048_SINE
                elif scpiCmd == b"INT_BITSSINE":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_INTERNAL_1544_SINE
                elif scpiCmd == b"BITS":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_BITS
                elif scpiCmd == b"SETS":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_SETS
                #elif scpiCmd == b"BITSSINE":
                #    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_1544_SINE
                elif scpiCmd == b"SETSSINE":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_2048_SINE
                elif scpiCmd == b"GPS":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_GPS_NO_OUTPUT
                elif scpiCmd == b"SMA_1544_NO_OUT":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_SMA_1544_NO_OUTPUT
                elif scpiCmd == b"SMA_2048_NO_OUT":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_SMA_2048_NO_OUTPUT
                elif scpiCmd == b"SMA_1544":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_SMA_1544_IN_OUT
                elif scpiCmd == b"SMA_2048":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_SMA_2048_IN_OUT
                elif scpiCmd == b"SMA_10M":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_SMA_10M_IN_OUT
                elif scpiCmd == b"SMA_1PPS":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_SMA_1PPS_IN_OUT
                elif scpiCmd == b"INT_10M":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_INTERNAL_10M_OUT
                elif scpiCmd == b"INT_1PPS":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_INTERNAL_1PPS_OUT
                elif scpiCmd == b"SMA_10M_1PPS":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_SMA_10M_IN_1PPS_OUT
                elif scpiCmd == b"SMA_1PPS_10M":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_SMA_1PPS_IN_10M_OUT
                elif scpiCmd == b"GPS_1PPS":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_GPS_IN_1PPS_OUT
                elif scpiCmd == b"GPS_2048":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_GPS_IN_2048_OUT
                elif scpiCmd == b"GPS_1544":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_GPS_IN_1544_OUT
                elif scpiCmd == b"GPS_10M":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_GPS_IN_10M_OUT
                else:
                    return self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
            elif mchType == veexlib.MCH_NO_BITS_SETS:
                if scpiCmd == b"INTERNAL":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_INTERNAL_NO_OUTPUT
                else:
                    return self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
            elif mchType == veexlib.MCH_WITH_BITS_SETS:
                if scpiCmd == b"INTERNAL":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_INTERNAL_NO_OUTPUT
                elif scpiCmd == b"INT_SETS":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_INTERNAL_SETS
                elif scpiCmd == b"INT_BITS":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_INTERNAL_BITS
                elif scpiCmd == b"INT_SETSSINE":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_INTERNAL_2048_SINE
                elif scpiCmd == b"INT_BITSSINE":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_INTERNAL_1544_SINE
                elif scpiCmd == b"BITS":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_BITS
                elif scpiCmd == b"SETS":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_SETS
                #elif scpiCmd == b"BITSSINE":
                #    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_1544_SINE
                elif scpiCmd == b"SETSSINE":
                    self.globals.veexChassis.chassisClock = veexlib.SYS_CLOCK_2048_SINE
                else:
                    return self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
            else:
                return self._errorResponse(ScpiErrorCode.INVALID_SETTINGS)
        else:
            return self._errorResponse(ScpiErrorCode.MISSING_PARAM)

    def getExternalClockStatus(self, parameters):
        '''**SYSTem:CLKSTATUS?** -
        Query the status of the chassis clock.
        '''
        clockStatus = self.globals.veexChassis.clockStatus
        if clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_NA:
            return b"Unknown"
        elif clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_NOT_CONNECTED:
            return b"Internal Reference"
        elif clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_NO_BITS_SETS:
            return b"Internal Reference"
        elif clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_NO_RESPONSE:
            return b"No Status"
        elif clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_INTERNAL:
            return b"Internal Reference"
        elif clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_RLOS:
            return b"No Signal"
        elif clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_FREE_RUN:
            return b"Not Locked"
        elif clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_PRE_LOCKED:
            return b"Pre-Locked"
        elif clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_PRE_LOCKED_2:
            return b"Pre-Locked 2"
        elif clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_LOCKED:
            return b"Locked"
        elif clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_LOSS_OF_LOCK:
            return b"Loss of Lock"
        elif clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_HOLDOVER:
            return b"Holdover"
        else:
            return b"Unknown"

    def getEtherAddr(self, parameters):
        '''**SYST:COMM:ETHER:ADDR?** -
        Query the IP address for the external chassis Ethernet port.
        '''
        return bytes(self.globals.veexChassis.getTcpIpAddress(), encoding='utf-8')

    def setEtherAddr(self, parameters):
        '''**SYST:COMM:ETHER:ADDR** -
        Set the IP address for the external chassis Ethernet port. Setting
        is changed by the REBOOT command (:meth:`~ScpiSystem.ScpiSystem.doReboot`).
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        if len(paramList) >= 1:
            self.globals.chassisIpAddress = paramList[0].head
        else:
            return self._errorResponse(ScpiErrorCode.MISSING_PARAM)

    def getEtherDns1(self, parameters):
        '''**SYST:COMM:ETHER:DNS1?** -
        Query the primary Domain Name Server for the external chassis Ethernet
        port.
        '''
        return bytes(self.globals.veexChassis.getTcpIpDnsAddress1(), encoding='utf-8')

    def setEtherDns1(self, parameters):
        '''**SYST:COMM:ETHER:DNS1** -
        Set the primary Domain Name Server for the external chassis Ethernet
        port. Setting is changed by the REBOOT command
        (:meth:`~ScpiSystem.ScpiSystem.doReboot`).
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        if len(paramList) >= 1:
            self.globals.chassisDnsAddress1 = paramList[0].head
        else:
            return self._errorResponse(ScpiErrorCode.MISSING_PARAM)

    def getEtherDns2(self, parameters):
        '''**SYST:COMM:ETHER:DNS2?** -
        Query the secondary Domain Name Server for the external chassis Ethernet
        port.
        '''
        return bytes(self.globals.veexChassis.getTcpIpDnsAddress2(), encoding='utf-8')

    def setEtherDns2(self, parameters):
        '''**SYST:COMM:ETHER:DNS2** -
        Set the secondary Domain Name Server for the external chassis Ethernet
        port. Setting is changed by the REBOOT command
        (:meth:`~ScpiSystem.ScpiSystem.doReboot`).
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        if len(paramList) >= 1:
            self.globals.chassisDnsAddress2 = paramList[0].head
        else:
            return self._errorResponse(ScpiErrorCode.MISSING_PARAM)

    def getEtherRout(self, parameters):
        '''**SYST:COMM:ETHER:ROUTer?** -
        Query the default router for the external chassis Ethernet port.
        '''
        return bytes(self.globals.veexChassis.getTcpIpDefRouter(), encoding='utf-8')

    def setEtherRout(self, parameters):
        '''**SYST:COMM:ETHER:ROUTer** -
        Set the default router for the external chassis Ethernet port. Setting
        is changed by the REBOOT command (:meth:`~ScpiSystem.ScpiSystem.doReboot`).
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        if len(paramList) >= 1:
            self.globals.chassisDefRouter = paramList[0].head
        else:
            return self._errorResponse(ScpiErrorCode.MISSING_PARAM)

    def getEtherSub(self, parameters):
        '''**SYST:COMM:ETHER:SUBnet?** -
        Query the subnet mask for the external chassis Ethernet port.
        '''
        return bytes(self.globals.veexChassis.getTcpIpSubnetMask(), encoding='utf-8')

    def setEtherSub(self, parameters):
        '''**SYST:COMM:ETHER:SUBnet** -
        Set the subnet mask for the external chassis Ethernet port. Setting
        is changed by the REBOOT command (:meth:`~ScpiSystem.ScpiSystem.doReboot`).
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        if len(paramList) >= 1:
            self.globals.chassisSubnetMask = paramList[0].head
        else:
            return self._errorResponse(ScpiErrorCode.MISSING_PARAM)

    def getDate(self, parameters):
        '''**SYSTem:DATE?** -
        Query the chassis date as month/day/year.
        '''
        sysDate = self.globals.veexChassis.getDate()
        return b"%d/%d/%d" % (sysDate[1], sysDate[2], sysDate[0])

    def setDate(self, parameters):
        '''**SYSTem:DATE** -
        Set the chassis date as month/day/year.
        '''
        # Special parse so that / and : are handled.
        paramList = ParseUtils.preParse(parameters, B' \t,/:')
        if (len(paramList) == 1) and (len(paramList[0].head) == 0):
            paramList =  []
        if len(paramList) >= 3:
            if paramList[0].head.isdigit() and \
               paramList[1].head.isdigit() and \
               paramList[2].head.isdigit():
                month = int(paramList[0].head)
                day   = int(paramList[1].head)
                year  = int(paramList[2].head)
                if  (day > 31)    or (day < 1) or \
                    (month > 12)  or (month < 1) or \
                    (year > 2099) or (year < 2000):
                    return self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
                else:
                    self.globals.veexChassis.setDate(year, month, day)
            else:
                return self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
        else:
            return self._errorResponse(ScpiErrorCode.MISSING_PARAM)

    def getDefaultTUList(self, parameters):
        '''**SYSTem:DTESTUList?** -
        Return a list of Test Units in the chassis with a sub list of PPs
        in each test unit.
        '''
        result = b""
        testUnitNumber = 0
        for tu in self.globals.veexChassis.testUnits:
            testUnitNumber += 1
            if len(result) == 0:
                result += b"Default%d " % testUnitNumber
            else:
                result += b": Default%d " % testUnitNumber

            ppResult = b""
            for pp in tu.protocols:
                ppName = b""
                if pp.protocolType == veexlib.PROTO_PHY:
                    # MPM10G card doesn't have an MLD in SCPI
                    if (pp.cardType == veexlib.CARD_MPM100G) or \
                       (pp.cardType == veexlib.CARD_MPM100AR):
                        ppName = b"MPM100MLD"
                    elif pp.cardType == veexlib.CARD_MPM400G:
                        ppName = b"MPM400GMLD"
                    elif pp.cardType == veexlib.CARD_MPM400AR:
                        ppName = b"MPM400MLD"
                    elif pp.cardType == veexlib.CARD_MPM400DCO:
                        ppName = b"MPM400MLD"
                    elif pp.cardType == veexlib.CARD_MPM600G:
                        ppName = b"MPM600MLD"
                elif pp.protocolType == veexlib.PROTO_OTN:
                    if pp.cardType == veexlib.CARD_MPM10G:
                        ppName = b"OTN"
                    elif (pp.cardType == veexlib.CARD_MPM100G) or \
                         (pp.cardType == veexlib.CARD_MPM100AR):
                        ppName = b"MPM100OTN"
                    elif pp.cardType == veexlib.CARD_MPM400G:
                        ppName = b"MPM400GOTN"
                    elif pp.cardType == veexlib.CARD_MPM400AR:
                        ppName = b"MPM400OTN"
                    elif pp.cardType == veexlib.CARD_MPM400DCO:
                        ppName = b"MPM400OTN"
                    elif pp.cardType == veexlib.CARD_MPM600G:
                        ppName = b"MPM600OTN"
                elif pp.protocolType == veexlib.PROTO_SONET_SDH:
                    if pp.cardType == veexlib.CARD_MPM10G:
                        ppName = b"SONETSDH"
                    elif (pp.cardType == veexlib.CARD_MPM100G) or \
                         (pp.cardType == veexlib.CARD_MPM100AR):
                        ppName = b"MPM100SONETSDH"
                    elif pp.cardType == veexlib.CARD_MPM400G:
                        ppName = b"MPM400GSONETSDH"
                    elif pp.cardType == veexlib.CARD_MPM400AR:
                        ppName = b"MPM400SONETSDH"
                    elif pp.cardType == veexlib.CARD_MPM400DCO:
                        ppName = b"MPM400SONETSDH"
                    elif pp.cardType == veexlib.CARD_MPM600G:
                        ppName = b"MPM600SONETSDH"
                elif pp.protocolType == veexlib.PROTO_ETHERNET:
                    if pp.cardType == veexlib.CARD_MPM10G:
                        ppName = b"PACKET"
                    elif (pp.cardType == veexlib.CARD_MPM100G) or \
                         (pp.cardType == veexlib.CARD_MPM100AR):
                        ppName = b"MPM100PACKET"
                    elif pp.cardType == veexlib.CARD_MPM400G:
                        ppName = b"MPM400GPACKET"
                    elif pp.cardType == veexlib.CARD_MPM400AR:
                        ppName = b"MPM400PACKET"
                    elif pp.cardType == veexlib.CARD_MPM400DCO:
                        ppName = b"MPM400PACKET"
                    elif pp.cardType == veexlib.CARD_MPM600G:
                        ppName = b"MPM600PACKET"

                # Not every protocol has a SCPI counterpart (ie. PHY, OCS, and OTL
                # become just MLD in SCPI).
                if len(ppName) > 0:
                    if len(ppResult) == 0:
                        ppResult += b"0 %d %d %s" % (pp.slotId, pp.portId, ppName)
                    else:
                        ppResult += b", 0 %d %d %s" % (pp.slotId, pp.portId, ppName)
            result += ppResult

        return result

    def getNextError(self, parameters):
        '''**SYSTem:ERRor?** or **SYSTem:ERRor:CODE?** or 
        **SYSTem:ERRor:CODE:NEXT?** or **SYSTem:ERRor:NEXT?** -
        Return oldest error in the error queue and remove it from the queue.
        '''
        errorCode = self.globals.errorQueue.nextError()
        if errorCode is None:
            return b"0"
        else:
            return errorResponse(errorCode, self.globals, False)

    def getLastError(self, parameters):
        '''**SYSTem:ERRor:CODE:LAST?** or **SYSTem:ERRor:LAST?** -
        Return newest error in the error queue and clear the queue.
        '''
        errorCode = self.globals.errorQueue.lastError()
        if errorCode is None:
            return b"0"
        else:
            return errorResponse(errorCode, self.globals, False)

    def getErrorCount(self, parameters):
        '''**SYSTem:ERRor:COUNt?** -
        Return the integer number of entries in the error queue.
        '''
        return b"%d" % self.globals.errorQueue.errorCount()


    def getLegacyResponse(self, parameters):
        '''**SYSTem:LEGACYResponse?** -
        Query the legacy response setting.
        '''
        if self.globals.legacyResponse:
            return b"TRUE"
        else:
            return b"FALSE"

    def setLegacyResponse(self, parameters):
        '''**SYSTem:LEGACYResponse <TRUE|FALSE>** -
        The legacy response to command errors is a simple integer. The default
        is to return the integer followed by a text decription of the error.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"TRUE"):
                self.globals.legacyResponse = True
            elif paramList[0].head.upper().startswith(b"FALSE"):
                self.globals.legacyResponse = False
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getLockForced(self, parameters):
        '''**SYSTem:LOCK:FORCED?** -
        Query the lock forced setting.
        '''
        if self.globals.forceLock:
            return b"ON"
        else:
            return b"OFF"

    def setLockForced(self, parameters):
        '''**SYSTem:LOCK:FORCED <ON|OFF|DEFAULT_ON|DEFAULT_OFF>** -
        If INST command tries to get the lock, and someone else has it, then
        it goes into read only mode without the lock. Setting this allows
        the lock to be forcibly taken.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ON"):
                self.globals.forceLock = True
            elif paramList[0].head.upper().startswith(b"OFF"):
                self.globals.forceLock = False
            elif paramList[0].head.upper().startswith(b"DEFAULT_ON"):
                self.globals.forceLock = True
                self.globals.veexChassis.setScpiLockForcedOn(True)
            elif paramList[0].head.upper().startswith(b"DEFAULT_OFF"):
                self.globals.forceLock = False
                self.globals.veexChassis.setScpiLockForcedOn(False)
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getLockOwner(self, parameters):
        '''**SYSTem:LOCK:OWNER?** -
        Query a list of the protocols that are locked and who has the lock.
        '''
        result = b""
#        if self.globals.veexProtocol and (not self.globals.veexProtocol.isNotLocked()):
#        if self.globals.veexProtocol:
            # Set mode of the INST selected PP.
        for tu in self.globals.veexChassis.testUnits:
            tu.updateTestUnit()
            userId = tu.lockOwnerId
            userName = bytes(self.globals.veexChassis.getUserName(userId), encoding='utf-8')
            if (not tu.isNotLocked()) and (len(userName) > 0):
                for pp in tu.protocols:
                    ppName = b""
                    if pp.protocolType == veexlib.PROTO_PHY:
                        # MPM10G card doesn't have an MLD in SCPI
                        if (pp.cardType == veexlib.CARD_MPM100G) or \
                           (pp.cardType == veexlib.CARD_MPM100AR):
                            ppName = b"MPM100MLD"
                        elif pp.cardType == veexlib.CARD_MPM400G:
                            ppName = b"MPM400GMLD"
                        elif pp.cardType == veexlib.CARD_MPM400AR:
                            ppName = b"MPM400MLD"
                        elif pp.cardType == veexlib.CARD_MPM400DCO:
                            ppName = b"MPM400MLD"
                        elif pp.cardType == veexlib.CARD_MPM600G:
                            ppName = b"MPM600MLD"
                    elif pp.protocolType == veexlib.PROTO_OTN:
                        if pp.cardType == veexlib.CARD_MPM10G:
                            ppName = b"OTN"
                        elif (pp.cardType == veexlib.CARD_MPM100G) or \
                             (pp.cardType == veexlib.CARD_MPM100AR):
                            ppName = b"MPM100OTN"
                        elif pp.cardType == veexlib.CARD_MPM400G:
                            ppName = b"MPM400GOTN"
                        elif pp.cardType == veexlib.CARD_MPM400AR:
                            ppName = b"MPM400OTN"
                        elif pp.cardType == veexlib.CARD_MPM400DCO:
                            ppName = b"MPM400OTN"
                        elif pp.cardType == veexlib.CARD_MPM600G:
                            ppName = b"MPM600OTN"
                    elif pp.protocolType == veexlib.PROTO_SONET_SDH:
                        if pp.cardType == veexlib.CARD_MPM10G:
                            ppName = b"SONETSDH"
                        elif (pp.cardType == veexlib.CARD_MPM100G) or \
                             (pp.cardType == veexlib.CARD_MPM100AR):
                            ppName = b"MPM100SONETSDH"
                        elif pp.cardType == veexlib.CARD_MPM400G:
                            ppName = b"MPM400GSONETSDH"
                        elif pp.cardType == veexlib.CARD_MPM400AR:
                            ppName = b"MPM400SONETSDH"
                        elif pp.cardType == veexlib.CARD_MPM400DCO:
                            ppName = b"MPM400SONETSDH"
                        elif pp.cardType == veexlib.CARD_MPM600G:
                            ppName = b"MPM600SONETSDH"
                    elif pp.protocolType == veexlib.PROTO_ETHERNET:
                        if pp.cardType == veexlib.CARD_MPM10G:
                            ppName = b"PACKET"
                        elif (pp.cardType == veexlib.CARD_MPM100G) or \
                             (pp.cardType == veexlib.CARD_MPM100AR):
                            ppName = b"MPM100PACKET"
                        elif pp.cardType == veexlib.CARD_MPM400G:
                            ppName = b"MPM400GPACKET"
                        elif pp.cardType == veexlib.CARD_MPM400AR:
                            ppName = b"MPM400PACKET"
                        elif pp.cardType == veexlib.CARD_MPM400DCO:
                            ppName = b"MPM400PACKET"
                        elif pp.cardType == veexlib.CARD_MPM600G:
                            ppName = b"MPM600PACKET"

                    # Not every protocol has a SCPI counterpart (ie. PHY, OCS, and OTL
                    # become just MLD in SCPI).
                    if len(ppName) > 0:
                        if len(result) != 0:
                            result += b":"
                        result += b"0 %d %d %s %s" % (pp.slotId, pp.portId, ppName, userName)

        # If nobody has a lock then return NONE
        if len(result) == 0:
            result = b"NONE"
        return result

    def getMchIpAddress(self, parameters):
        '''**SYST:MCHADDR?** -
        Query the IP address of the MCH in the chassis, for non-SCM chassis'.
        '''
        return bytes(self.globals.veexChassis.mchIpAddress, encoding='utf-8')

    def setMchIpAddress(self, parameters):
        '''**SYST:MCHADDR** -
        Set the IP address to use when connectin to the MCH in the chassis,
        for non-SCM chassis'. Does not set the MCH address, just what address
        to use when connecting.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexChassis.mchIpAddress = paramList[0].head.decode()
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)

    def getMchClockStatus(self, parameters):
        '''**SYST:MCHSTATUS?** -
        Query the connection status of the MCH. Used to tell if the chassis
        clock can be set.
        '''
        mchType = self.globals.veexChassis.mchType
        if mchType == veexlib.MCH_SCM:
            csMchStatus = "SCM";
        elif (mchType == veexlib.MCH_NO_BITS_SETS) or \
             (mchType == veexlib.MCH_WITH_BITS_SETS):
            clockStatus = self.globals.veexChassis.clockStatus
            if clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_NA:
                return b"Unknown"
            elif clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_NOT_CONNECTED:
                return b"MCH not connected"
            elif clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_NO_BITS_SETS:
                return b"MCH without BITS/SETS"
            elif clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_NO_RESPONSE:
                return b"MCH no response"
            elif (clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_INTERNAL)     or \
                 (clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_RLOS)         or \
                 (clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_FREE_RUN)     or \
                 (clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_PRE_LOCKED)   or \
                 (clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_PRE_LOCKED_2) or \
                 (clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_LOCKED)       or \
                 (clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_LOSS_OF_LOCK) or \
                 (clockStatus == veexlib.SYS_CLOCK_STATUS_MCH_HOLDOVER):
                return b"MCH with BITS/SETS"
            else:
                return b"Unknown"

    def getOsVersion(self, parameters):
        '''**SYST:OSVERSion?** -
        Query the operating system version. This is a VeEX assigned number and
        not the operating system's number.
        '''
        return bytes(self.globals.veexChassis.osVersion, encoding='utf-8')

    def doReboot(self, parameters):
        '''**SYSTem:REBOOT** -
        Do an operating system reboot of the chassis. If any of the
        SYST:COMM:ETHER:\* settings have changed then those are applied first.
        '''
        if (self.globals.chassisIpAddress   != b"") or \
           (self.globals.chassisSubnetMask  != b"") or \
           (self.globals.chassisDefRouter   != b"") or \
           (self.globals.chassisDnsAddress1 != b"") or \
           (self.globals.chassisDnsAddress2 != b""):
            self.globals.veexChassis.setTcpIpParams(self.globals.chassisIpAddress.decode(),   \
                                                    self.globals.chassisSubnetMask.decode(),  \
                                                    self.globals.chassisDefRouter.decode(),   \
                                                    self.globals.chassisDnsAddress1.decode(), \
                                                    self.globals.chassisDnsAddress2.decode())

        self.globals.veexChassis = self.globals.veexChassis.reboot()
        exit()

    def getResponse(self, parameters):
        '''**SYSTem:RESPonse?** -
        Query the response setting of <ALWAYS|STANDARD>.
        '''
        if self.globals.respondAlways:
            return b"ALWAYS"
        else:
            return b"STANDARD"

    def setResponse(self, parameters):
        '''**SYSTem:RESPonse <ALWAYS|STANDARD|DEFAULT_ALWAYS|DEFAULT_STANDARD>** -
        The default for a command that doesn't have a error is to return
        nothing. Setting to always causes a +0 to be returned instead so the
        user can always tell when the command has finished.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ALWAYS"):
                self.globals.respondAlways = True
                response = b"SCPI response mode set to: ALWAYS"
            elif paramList[0].head.upper().startswith(b"STANDARD"):
                self.globals.respondAlways = False
                response = b"SCPI response mode set to: STANDARD"
            elif paramList[0].head.upper().startswith(b"DEFAULT_ALWAYS"):
                self.globals.respondAlways = True
                self.globals.veexChassis.setScpiRespAlways(True)
                response = b"SCPI response mode set to: ALWAYS"
            elif paramList[0].head.upper().startswith(b"DEFAULT_STANDARD"):
                self.globals.respondAlways = False
                self.globals.veexChassis.setScpiRespAlways(False)
                response = b"SCPI response mode set to: STANDARD"
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getSystRuntime(self, parameters):
        '''**SYSTem:RUNTIME?** -
        Query how long the chassis has been running since manufature as
        hour:min:sec.
        '''
        runTime = self.globals.veexChassis.getUsageTime()
        return b"%d:%d:%d" % runTime

    def doShutDown(self, parameters):
        '''**SYSTem:SHUTDOWN** -
        Do an operating system shutdown of the chassis.
        '''
        self.globals.veexChassis = self.globals.veexChassis.shutdown()
        exit()

    def getTime(self, parameters):
        '''**SYSTem:TIME?** -
        Query the chassis time as hour:min:sec.
        '''
        sysTime = self.globals.veexChassis.getTime()
        return b"%d:%d:%d" % sysTime

    def setTime(self, parameters):
        '''**SYSTem:TIME** -
        Set the chassis time as hour:min:sec.
        '''
        # Special parse so that : are handled.
        paramList = ParseUtils.preParse(parameters, B' \t,:')
        if (len(paramList) == 1) and (len(paramList[0].head) == 0):
            paramList =  []
        if len(paramList) >= 3:
            if paramList[0].head.isdigit() and \
               paramList[1].head.isdigit() and \
               paramList[2].head.isdigit():
                hours   = int(paramList[0].head)
                minutes = int(paramList[1].head)
                seconds = int(paramList[2].head)
                if  (seconds > 59) or (seconds < 0) or \
                    (minutes > 59) or (minutes < 0) or \
                    (hours > 23) or (hours < 0):
                    return self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
                else:
                    self.globals.veexChassis.setTime(hours, minutes, seconds)
            else:
                return self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
        else:
            return self._errorResponse(ScpiErrorCode.MISSING_PARAM)


    def getScpiVers(self, parameters):
        '''**SYSTem:VERSion?** -
        Query the software version of the SCPI server.
        '''
        return bytes(self.globals.veexChassis.scpiSoftwareVersion, encoding='utf-8')

    def getWhoAmI(self, parameters):
        '''**SYSTem:WHOAMI?** -
        Query the user and connection as <user name>/<connection type><connection number>.
        '''
        return b"%s/%s%d" % (self.globals.userName, self.globals.sessionType, self.globals.sessionId)


# This table contains all the system SCPI commands. Note that queries must
# come before the matching setting commands. Also if two commands start with
# the same text then the longer one must come first.
commandTable = [
    Cmnd(b"*CLS",                       ScpiSystem.clearStatusByte),
    Cmnd(b"*ESR?",                      ScpiSystem.repSesByte),
    Cmnd(b"*IDN?",                      ScpiSystem.identifySelf),
    Cmnd(b"*RST",                       ScpiSystem.setFactoryDefault),
    Cmnd(b"ABORt",                      ScpiSystem.setStop),
    Cmnd(b"DELAY",                      ScpiSystem.scpiDelay),
    Cmnd(b"DURation?",                  ScpiSystem.getDuration),
    Cmnd(b"DURation",                   ScpiSystem.setDuration),
    Cmnd(b"ELAPSEdtime?",               ScpiSystem.getElapsedTime),
    Cmnd(b"GET:PARTnumbers?",           ScpiSystem.getPartNumbers),
    Cmnd(b"GET:PROTOcol?",              ScpiSystem.getProtocol),
    Cmnd(b"GET:SERialnumbers?",         ScpiSystem.getSerialNumbers),
    Cmnd(b"GET:VERsion?",               ScpiSystem.getVersions),
    Cmnd(b"INITiate",                   ScpiSystem.setRestart),
    Cmnd(b"INSTrument?",                ScpiSystem.getInst),
    Cmnd(b"INSTrument",                 ScpiSystem.setInstLock),
    Cmnd(b"INS_?",                      ScpiSystem.getInst),
    Cmnd(b"INS_",                       ScpiSystem.setInstNoLock),
    Cmnd(b"LICense?",                   ScpiSystem.getCpLicense),
    Cmnd(b"LICense",                    ScpiSystem.setCpLicense),
    Cmnd(b"PROTOCOL?",                  ScpiSystem.getProtocolMode),
    Cmnd(b"PROTOCOL",                   ScpiSystem.setProtocolMode),
    Cmnd(b"REMAINingtime?",             ScpiSystem.getRemainingTime),
    Cmnd(b"SAVEREPORT",                 ScpiSystem.saveReport),
    Cmnd(b"SCPI?",                      ScpiSystem.getScpi),
    Cmnd(b"TIMLIC?",                    ScpiSystem.getCpTimedLicense),
    Cmnd(b"SET:RESTore",                ScpiSystem.restoreSettings),
    Cmnd(b"SET:SAVE",                   ScpiSystem.saveSettings),
    Cmnd(b"SYSTem:AUTOLOGIN:DETails",   ScpiSystem.setAutoLoginDetails),
    Cmnd(b"SYSTem:AUTOLOGIN:USER?",     ScpiSystem.getAutoLoginUser),
    Cmnd(b"SYSTem:AUTOLOGIN:VALue?",    ScpiSystem.getAutoLoginEnable),
    Cmnd(b"SYSTem:AUTOLOGIN:VALue",     ScpiSystem.setAutoLoginEnable),
    Cmnd(b"SYSTem:CLOCK?",              ScpiSystem.getSystClock),
    Cmnd(b"SYSTem:CLOCK",               ScpiSystem.setSystClock),
    Cmnd(b"SYSTem:CLKSTATUS?",          ScpiSystem.getExternalClockStatus),
    Cmnd(b"SYSTem:COMM:ETHER:ADDR?",    ScpiSystem.getEtherAddr),
    Cmnd(b"SYSTem:COMM:ETHER:ADDR",     ScpiSystem.setEtherAddr),
    Cmnd(b"SYSTem:COMM:ETHER:DNS1?",    ScpiSystem.getEtherDns1),
    Cmnd(b"SYSTem:COMM:ETHER:DNS1",     ScpiSystem.setEtherDns1),
    Cmnd(b"SYSTem:COMM:ETHER:DNS2?",    ScpiSystem.getEtherDns2),
    Cmnd(b"SYSTem:COMM:ETHER:DNS2",     ScpiSystem.setEtherDns2),
    Cmnd(b"SYSTem:COMM:ETHER:ROUTer?",  ScpiSystem.getEtherRout),
    Cmnd(b"SYSTem:COMM:ETHER:ROUTer",   ScpiSystem.setEtherRout),
    Cmnd(b"SYSTem:COMM:ETHER:SUBnet?",  ScpiSystem.getEtherSub),
    Cmnd(b"SYSTem:COMM:ETHER:SUBnet",   ScpiSystem.setEtherSub),
    Cmnd(b"SYSTem:DATE?",               ScpiSystem.getDate),
    Cmnd(b"SYSTem:DATE",                ScpiSystem.setDate),
    Cmnd(b"SYSTem:DTESTUList?",         ScpiSystem.getDefaultTUList),
    Cmnd(b"SYSTem:ERRor?",              ScpiSystem.getNextError),
    Cmnd(b"SYSTem:ERRor:CODE?",         ScpiSystem.getNextError),
    Cmnd(b"SYSTem:ERRor:CODE:NEXT?",    ScpiSystem.getNextError),
    Cmnd(b"SYSTem:ERRor:NEXT?",         ScpiSystem.getNextError),
    Cmnd(b"SYSTem:ERRor:CODE:LAST?",    ScpiSystem.getLastError),
    Cmnd(b"SYSTem:ERRor:LAST?",         ScpiSystem.getLastError),
    Cmnd(b"SYSTem:ERRor:COUNt?",        ScpiSystem.getErrorCount),
    Cmnd(b"SYSTem:LEGACYResponse?",     ScpiSystem.getLegacyResponse),
    Cmnd(b"SYSTem:LEGACYResponse",      ScpiSystem.setLegacyResponse),
    Cmnd(b"SYSTem:LOCK:FORCED?",        ScpiSystem.getLockForced),
    Cmnd(b"SYSTem:LOCK:FORCED",         ScpiSystem.setLockForced),
    Cmnd(b"SYSTem:LOCK:OWNER?",         ScpiSystem.getLockOwner),
    Cmnd(b"SYSTem:MCHADDR?",            ScpiSystem.getMchIpAddress),
    Cmnd(b"SYSTem:MCHADDR",             ScpiSystem.setMchIpAddress),
    Cmnd(b"SYSTem:MCHSTATUS?",          ScpiSystem.getMchClockStatus),
    Cmnd(b"SYSTem:OSVERSion?",          ScpiSystem.getOsVersion),
    Cmnd(b"SYSTem:REBOOT",              ScpiSystem.doReboot),
    Cmnd(b"SYSTem:RESPonse?",           ScpiSystem.getResponse),
    Cmnd(b"SYSTem:RESPonse",            ScpiSystem.setResponse),
    Cmnd(b"SYSTem:RUNTIME?",            ScpiSystem.getSystRuntime),
    Cmnd(b"SYSTem:SHUTDOWN",            ScpiSystem.doShutDown),
    Cmnd(b"SYSTem:TIME?",               ScpiSystem.getTime),
    Cmnd(b"SYSTem:TIME",                ScpiSystem.setTime),
    Cmnd(b"SYSTem:VERSion?",            ScpiSystem.getScpiVers),
    Cmnd(b"SYSTem:WHOAMI?",             ScpiSystem.getWhoAmI),
    ]


# This converts the above table into a tree of lists that can be searched
# for commands. Doing this here and not in the class init means it is done
# once at boot and not at the start of each user session.
commandTreeRoot = []
ParseUtils.processCommandTableIntoTree(commandTable, commandTreeRoot)


if __name__ == "__main__":
    pass

