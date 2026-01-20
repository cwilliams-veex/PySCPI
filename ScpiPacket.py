###############################################################################
#
# Copyright 2018-2019, VeEX, Inc.
# All Rights Reserved.
#
# $Workfile:   ScpiPacket.py  $
# $Revision: 20644 $
# $Author: patrickellis $
# $Date: 2019-10-18 17:59:15 -0400 (Fri, 18 Oct 2019) $
#
# DESCRIPTION:
#    Module to process Packet SCPI commands.
#
###############################################################################

from ErrorCodes import ScpiErrorCode
from ErrorCodes import errorResponse
from ParseUtils import CommandTableEntry as Cmnd
from SessionGlobals import SessionGlobals
import ParseUtils
#import SessionGlobals
import veexlib


class ScpiPacket(object):
    #'''This class processes text Packet SCPI commands and returns a text response.
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


    def getTxLaserPwrUp(self, parameters):
        '''**TX:LASERPUP?** -
        Query the laser state on power up.
        '''
        self.globals.veexPhy.sets.update()
        if self.globals.veexPhy.sets.powerUpLaserState == veexlib.LASER_POWERS_UP_OFF:
            response = b"OFF"
        elif self.globals.veexPhy.sets.powerUpLaserState == veexlib.LASER_POWERS_UP_ON:
            response = b"ON"
        elif self.globals.veexPhy.sets.powerUpLaserState == veexlib.LASER_POWERS_UP_LAST_SAVED_STATE:
            response = b"RESTORE"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setTxLaserPwrUp(self, parameters):
        '''**TX:LASERPUP <ON|OFF|RESTORE>** -
        Set the laser state on power up.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"OFF"):
                self.globals.veexPhy.sets.powerUpLaserState = veexlib.LASER_POWERS_UP_OFF
            elif paramList[0].head.upper().startswith(b"ON"):
                self.globals.veexPhy.sets.powerUpLaserState = veexlib.LASER_POWERS_UP_ON
            elif paramList[0].head.upper().startswith(b"RESTORE"):
                self.globals.veexPhy.sets.powerUpLaserState = veexlib.LASER_POWERS_UP_LAST_SAVED_STATE
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response


    def getTxLaser(self, parameters):
        '''**TX:LASER?** -
        Query the laser on/off state.
        '''
        self.globals.veexPhy.sets.update()
        if self.globals.veexPhy.sets.laserOn:
            response = b"ON"
        else:
            response = b"OFF"
        return response

    def setTxLaser(self, parameters):
        '''**TX:LASER <ON|OFF>** -
        Set the laser on/off state.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ON"):
                self.globals.veexPhy.sets.laserOn = True
            elif paramList[0].head.upper().startswith(b"OFF"):
                self.globals.veexPhy.sets.laserOn = False
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response


    def rxGetOpticalPower(self, parameters):
        '''**RX:OPP?** -
        Query the measured RX optical power.
        '''
        self.globals.veexPhy.update()
        if (self.globals.veexPhy.stats.signalStrength < -99.7999) and \
           (self.globals.veexPhy.stats.signalStrength > -99.8001):
            response = b"No Module"
        elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_10000T_ETHERNET) or \
             (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_5000T_ETHERNET)  or \
             (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_2500T_ETHERNET)  or \
             (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_1000T_ETHERNET)  or \
             (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_100T_ETHERNET)   or \
             (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_10T_ETHERNET):
            response = b"Electical"
        elif (self.globals.veexPhy.stats.signalStrength < -99.6999) and \
             (self.globals.veexPhy.stats.signalStrength > -99.7001):
            response = b"No Measurement"
        elif self.globals.veexPhy.stats.signalStrength < -50:
            response = b"Loss of Power";
        else:
            response = b"%.2f dBm" % self.globals.veexPhy.stats.signalStrength
        return response

    def getRxbCast(self, parameters):
        """**RES:RXBCAST?** - Query the count of received broadcast packets.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rxBroadcastPackets field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rxBroadcastPackets count as bytes
        """
        # No parameters
        response = None
        # TODO: Implement query logic
        # Example:
        # idlStatPacket = self.globals.veexPacket.getStatistics()
        # response = b"%d" % idlStatPacket.rxBroadcastPackets
        
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxmCast(self, parameters):
        """**RES:RXMCAST?** - Query the count of received multicast packets.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rxMulticastPackets field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rxMulticastPackets count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxuCast(self, parameters):
        """**RES:RXUCAST?** - Query the count of received unicast packets.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rxUnicastPackets field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rxUnicastPackets count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRx64bp(self, parameters):
        """**RES:RX64?** - Query the count of received 64-byte packets.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rx64BytePackets field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rx64BytePackets count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRx65bp(self, parameters):
        """**RES:RX65?** - Query the count of received packets sized 65-127 bytes.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rx65To127BytePackets field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rx65To127BytePackets count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRx128bp(self, parameters):
        """**RES:RX128?** - Query the count of received packets sized 128-255 bytes.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rx128To255BytePackets field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rx128To255BytePackets count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRx256bp(self, parameters):
        """**RES:RX256?** - Query the count of received packets sized 256-511 bytes.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rx256To511BytePackets field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rx256To511BytePackets count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRx512bp(self, parameters):
        """**RES:RX512?** - Query the count of received packets sized 512-1023 bytes.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rx512To1023BytePackets field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rx512To1023BytePackets count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRx1024bp(self, parameters):
        """**RES:RX1024?** - Query the count of received packets sized 1024-1518 bytes.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rx1024To1518BytePackets field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rx1024To1518BytePackets count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRx1519bp(self, parameters):
        """**RES:RX1519?** - Query the count of received packets sized 1519 bytes to maximum.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rx1519ToMaxBytePackets field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rx1519ToMaxBytePackets count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTxIdle(self, parameters):
        """**RES:TXIDLE?** - Query the count of transmitted GFP idle packets.
        
        Also used for:
        - RES:TXPACKETS:IDLE?
        - RES:MOSSERRS? (same implementation)
        - RES:MOSSALRMS? (same implementation)
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.txGfpIdlePackets field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return txGfpIdlePackets count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxIdle(self, parameters):
        """**RES:RXIDLE?** - Query the count of received GFP idle packets.
        
        Also used for:
        - RES:RXPACKETS:IDLE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rxGfpIdlePackets field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rxGfpIdlePackets count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTxSuperBlock(self, parameters):
        """**RES:TXSUPERBLOCK?** - Query the count of transmitted GFP superblocks.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.txGfpSuperBlocks field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return txGfpSuperBlocks count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxSuperBlock(self, parameters):
        """**RES:RXSUPERBLOCK?** - Query the count of received GFP superblocks.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rxGfpSuperBlocks field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rxGfpSuperBlocks count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getFcRrdyPend(self, parameters):
        """**RES:FCRRDYPEND?** - Query the Fibre Channel R_RDY credit value.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.fcRrdyCredit field
        - Format: signed 32-bit integer ("%d")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return fcRrdyCredit value as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getFcBbCredit(self, parameters):
        """**RES:FCBBCREDIT?** - Query the Fibre Channel buffer-to-buffer credit value.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.fcB2BCredit field
        - Format: signed 32-bit integer ("%d")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return fcB2BCredit value as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getFcTxRrdy(self, parameters):
        """**RES:FCTXRRDY?** - Query the count of transmitted Fibre Channel R_RDY primitives.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.fcTrdy field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return fcTrdy count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getFcRxRrdy(self, parameters):
        """**RES:FCRXRRDY?** - Query the count of received Fibre Channel R_RDY primitives.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.fcRrdy field
        - Format: unsigned 64-bit integer ("%I64u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return fcRrdy count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRfSecs(self, parameters):
        """**RES:RF:SECS?** - Query the seconds count for remote link fault alarm.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.remoteLinkFault.alarmSecs field
        - Format: signed 32-bit integer ("%d")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return remoteLinkFault.alarmSecs value as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getLfSecs(self, parameters):
        """**RES:LF:SECS?** - Query the seconds count for local link fault alarm.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.localLinkFault.alarmSecs field
        - Format: signed 32-bit integer ("%d")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return localLinkFault.alarmSecs value as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getJabberSecs(self, parameters):
        """**RES:JABBER:SECS?** - Query the seconds count for jabber alarm.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.jabber.alarmSecs field
        - Format: signed 32-bit integer ("%d")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return jabber.alarmSecs value as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getBlockLockLossSecs(self, parameters):
        """**RES:BLKLOC:SECS?** - Query the seconds count for block lock loss alarm.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.blockLockLoss.alarmSecs field
        - Format: signed 32-bit integer ("%d")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return blockLockLoss.alarmSecs value as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getHiBerSecs(self, parameters):
        """**RES:HIBER:SECS?** - Query the seconds count for high BER alarm.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.hiBER.alarmSecs field
        - Format: signed 32-bit integer ("%d")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return hiBER.alarmSecs value as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

# This table contains all the system SCPI commands. Note that queries must
# come before the matching setting commands. Also if two commands start with
# the same text then the longer one must come first.
commandTable = [
    Cmnd(b"TX:LASERPUP?",          ScpiPacket.getTxLaserPwrUp),
    Cmnd(b"TX:LASERPUP",           ScpiPacket.setTxLaserPwrUp),
    Cmnd(b"TX:LASER?",             ScpiPacket.getTxLaser),
    Cmnd(b"TX:LASER",              ScpiPacket.setTxLaser),

    Cmnd(b"RX:OPP?",               ScpiPacket.rxGetOpticalPower),

    # RES (Results/Fetch) Level Commands - Ported from ScpiPacket.cpp resLevel table
    Cmnd(b"RES:RXBCAST?",          ScpiPacket.getRxbCast),
    Cmnd(b"FETC:RXBCAST?",         ScpiPacket.getRxbCast),  # FETC is alias for RES
    Cmnd(b"RES:RXMCAST?",          ScpiPacket.getRxmCast),
    Cmnd(b"FETC:RXMCAST?",         ScpiPacket.getRxmCast),
    Cmnd(b"RES:RXUCAST?",          ScpiPacket.getRxuCast),
    Cmnd(b"FETC:RXUCAST?",         ScpiPacket.getRxuCast),
    Cmnd(b"RES:RX64?",             ScpiPacket.getRx64bp),
    Cmnd(b"FETC:RX64?",            ScpiPacket.getRx64bp),
    Cmnd(b"RES:RX65?",             ScpiPacket.getRx65bp),
    Cmnd(b"FETC:RX65?",            ScpiPacket.getRx65bp),
    Cmnd(b"RES:RX128?",            ScpiPacket.getRx128bp),
    Cmnd(b"FETC:RX128?",           ScpiPacket.getRx128bp),
    Cmnd(b"RES:RX256?",            ScpiPacket.getRx256bp),
    Cmnd(b"FETC:RX256?",           ScpiPacket.getRx256bp),
    Cmnd(b"RES:RX512?",            ScpiPacket.getRx512bp),
    Cmnd(b"FETC:RX512?",           ScpiPacket.getRx512bp),
    Cmnd(b"RES:RX1024?",           ScpiPacket.getRx1024bp),
    Cmnd(b"FETC:RX1024?",          ScpiPacket.getRx1024bp),
    Cmnd(b"RES:RX1519?",           ScpiPacket.getRx1519bp),
    Cmnd(b"FETC:RX1519?",          ScpiPacket.getRx1519bp),
    Cmnd(b"RES:TXIDLE?",           ScpiPacket.getTxIdle),
    Cmnd(b"FETC:TXIDLE?",          ScpiPacket.getTxIdle),
    Cmnd(b"RES:RXIDLE?",           ScpiPacket.getRxIdle),
    Cmnd(b"FETC:RXIDLE?",          ScpiPacket.getRxIdle),
    Cmnd(b"RES:TXSUPERBLOCK?",     ScpiPacket.getTxSuperBlock),
    Cmnd(b"FETC:TXSUPERBLOCK?",    ScpiPacket.getTxSuperBlock),
    Cmnd(b"RES:RXSUPERBLOCK?",     ScpiPacket.getRxSuperBlock),
    Cmnd(b"FETC:RXSUPERBLOCK?",    ScpiPacket.getRxSuperBlock),
    Cmnd(b"RES:FCRRDYPEND?",       ScpiPacket.getFcRrdyPend),
    Cmnd(b"FETC:FCRRDYPEND?",      ScpiPacket.getFcRrdyPend),
    Cmnd(b"RES:FCBBCREDIT?",       ScpiPacket.getFcBbCredit),
    Cmnd(b"FETC:FCBBCREDIT?",      ScpiPacket.getFcBbCredit),
    Cmnd(b"RES:FCTXRRDY?",         ScpiPacket.getFcTxRrdy),
    Cmnd(b"FETC:FCTXRRDY?",        ScpiPacket.getFcTxRrdy),
    Cmnd(b"RES:FCRXRRDY?",         ScpiPacket.getFcRxRrdy),
    Cmnd(b"FETC:FCRXRRDY?",        ScpiPacket.getFcRxRrdy),
    Cmnd(b"RES:RF:SECS?",          ScpiPacket.getRfSecs),
    Cmnd(b"FETC:RF:SECS?",         ScpiPacket.getRfSecs),
    Cmnd(b"RES:LF:SECS?",          ScpiPacket.getLfSecs),
    Cmnd(b"FETC:LF:SECS?",         ScpiPacket.getLfSecs),
    Cmnd(b"RES:JABBER:SECS?",      ScpiPacket.getJabberSecs),
    Cmnd(b"FETC:JABBER:SECS?",     ScpiPacket.getJabberSecs),
    Cmnd(b"RES:BLKLOC:SECS?",      ScpiPacket.getBlockLockLossSecs),
    Cmnd(b"FETC:BLKLOC:SECS?",     ScpiPacket.getBlockLockLossSecs),
    Cmnd(b"RES:HIBER:SECS?",       ScpiPacket.getHiBerSecs),
    Cmnd(b"FETC:HIBER:SECS?",      ScpiPacket.getHiBerSecs),
    Cmnd(b"RES:MOSSERRS?",         ScpiPacket.getTxIdle),  # Alias for TXIDLE
    Cmnd(b"FETC:MOSSERRS?",        ScpiPacket.getTxIdle),
    Cmnd(b"RES:MOSSALRMS?",        ScpiPacket.getTxIdle),  # Alias for TXIDLE
    Cmnd(b"FETC:MOSSALRMS?",       ScpiPacket.getTxIdle),
    ]


# This converts the above table into a tree of lists that can be searched
# for commands. Doing this here and not in the class init means it is done
# once at boot and not at the start of each user session.
commandTreeRoot = []
ParseUtils.processCommandTableIntoTree(commandTable, commandTreeRoot)


if __name__ == "__main__":
    pass

