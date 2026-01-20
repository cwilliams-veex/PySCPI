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

    def doResLinecodeLevel(self, parameters):
        """**RES:LINECODE** - Process linecode error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resLinecodeLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.lineCode structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for linecode errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement linecode level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResCollisionLevel(self, parameters):
        """**RES:COLLISION** - Process collision error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resCollisionLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.collisions structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for collision errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement collision level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResPfcsLevel(self, parameters):
        """**RES:PFCS** - Process payload FCS error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resPfcsLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.pfcs structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for payload FCS errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement PFCS level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResIpChecksumLevel(self, parameters):
        """**RES:IPCHECKSUM** - Process IP checksum error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resIpChecksumLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.ipChecksum structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for IP checksum errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement IP checksum level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getCurrentErrors(self, parameters):
        """**RES:SCANERRORS?** - Query all current errors in system.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() and callGetPacketStreamStatistics()
        - Calls getErrorToken() for each error type in csPacketErrorNames array
        - Returns concatenated error tokens for all active errors
        - Checks allowed settings via callGetAllowedSettings()
        - Returns "+0" if no errors present
        
        Python TODO:
        - Call packet statistics methods
        - Build error token list for all active errors
        - Return formatted error token string
        """
        response = None
        # TODO: Implement error scanning logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResFcAlignLevel(self, parameters):
        """**RES:FCALIGN** - Process Fibre Channel alignment error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resFcAlignLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.fcAlignment structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for FC alignment errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement FC alignment level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResOversizedLevel(self, parameters):
        """**RES:OVERSIZED** - Process oversized packet error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resOversizedLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.oversized structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for oversized packet errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement oversized level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResUndersizedLevel(self, parameters):
        """**RES:UNDERSIZED** - Process undersized packet error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resUndersizedLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.undersized structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for undersized packet errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement undersized level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResCppLevel(self, parameters):
        """**RES:LOSS** - Process carrier power loss level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resCppLevel table
        - Sub-commands: SECS?
        - Accesses idlStatPacket.cpPowerLoss.alarmSecs structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for carrier power loss
        - Support query commands for alarm seconds
        """
        response = None
        # TODO: Implement CPP level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResLosLevel(self, parameters):
        """**RES:LOS** - Process loss of signal level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resLosLevel table
        - Sub-commands: SECS?
        - Accesses idlStatPacket.los.alarmSecs structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for loss of signal
        - Support query commands for alarm seconds
        """
        response = None
        # TODO: Implement LOS level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResLinkLevel(self, parameters):
        """**RES:LINK** - Process link status level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resLinkLevel table
        - Sub-commands: SECS?
        - Accesses idlStatPacket.link.alarmSecs structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for link status
        - Support query commands for alarm seconds
        """
        response = None
        # TODO: Implement link level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxPackets(self, parameters):
        """**RES:TXPACK?** - Query the count of transmitted packets.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.txPackets.count field
        - Format: signed 64-bit integer ("%I64i")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return txPackets.count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxPackets(self, parameters):
        """**RES:RXPACK?** - Query the count of received packets.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rxPackets.count field
        - Format: signed 64-bit integer ("%I64i")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rxPackets.count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxBytes(self, parameters):
        """**RES:TXBYT?** - Query the count of transmitted bytes.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.txBytes.count field
        - Format: signed 64-bit integer ("%I64i")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return txBytes.count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxBytes(self, parameters):
        """**RES:RXBYT?** - Query the count of received bytes.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rxBytes.count field
        - Format: signed 64-bit integer ("%I64i")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rxBytes.count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxJumboPackets(self, parameters):
        """**RES:JUMBO?** - Query the count of received jumbo packets.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rxJumboPackets.count field
        - Format: signed 64-bit integer ("%I64i")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rxJumboPackets.count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResPauseLevel(self, parameters):
        """**RES:PAUSE** - Process pause packet level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resPauseLevel table
        - Sub-commands: TX?, RX?, SECS?
        - Accesses idlStatPacket.pauseTx, pauseRx, ppPaused structures
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for pause packets
        - Support query commands for TX/RX counts and alarm seconds
        """
        response = None
        # TODO: Implement pause level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResTxPacketLevel(self, parameters):
        """**RES:TXPACK** - Process TX packet level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resTxPacketLevel table
        - Sub-commands: IDLE?
        - Accesses idlStatPacket.txGfpIdlePackets structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for TX packets
        - Support query commands for idle packets
        """
        response = None
        # TODO: Implement TX packet level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResVlanLevel(self, parameters):
        """**RES:VLAN** - Process VLAN level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resVlanLevel table
        - Sub-commands include various VLAN-related queries
        - Accesses VLAN-specific fields in IdlPacket2Stats
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for VLAN statistics
        - Support query commands for VLAN-tagged traffic
        """
        response = None
        # TODO: Implement VLAN level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthNone(self, parameters):
        """**RES:TXPCTBW?** - Query TX link percent bandwidth utilization.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.txLinkPctBandwidth field
        - Format: float divided by 100, displayed as "%.2f"
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return txLinkPctBandwidth / 100 as formatted bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthNone(self, parameters):
        """**RES:RXPCTBW?** - Query RX link percent bandwidth utilization.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rxLinkPctBandwidth field
        - Format: float divided by 100, displayed as "%.2f"
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rxLinkPctBandwidth / 100 as formatted bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecNone(self, parameters):
        """**RES:TXPPS?** - Query TX link packets per second.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.txLinkPacketPerSec field
        - Format: unsigned 32-bit integer ("%u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return txLinkPacketPerSec as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecNone(self, parameters):
        """**RES:RXPPS?** - Query RX link packets per second.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rxLinkPacketPerSec field
        - Format: unsigned 32-bit integer ("%u")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rxLinkPacketPerSec as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecNone(self, parameters):
        """**RES:TXMBPS?** - Query TX link megabits per second.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.txLinkKBPerSec field
        - Format: float displayed as "%.3f"
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return txLinkKBPerSec as formatted bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecNone(self, parameters):
        """**RES:RXMBPS?** - Query RX link megabits per second.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rxLinkKBPerSec field
        - Format: float displayed as "%.3f"
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rxLinkKBPerSec as formatted bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResSPM(self, parameters):
        """**RES:SPM?** - Query Stream Performance Monitoring data.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() and callGetPacketStreamStatistics()
        - Returns comprehensive SPM data for all streams
        - Complex format with multiple error and alarm counts
        - Includes stream sequence, bit errors, and pattern sync data
        
        Python TODO:
        - Call packet and stream statistics methods
        - Build comprehensive SPM data string
        - Return formatted SPM data as bytes
        """
        response = None
        # TODO: Implement SPM query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResSTSD(self, parameters):
        """**RES:STSD?** - Query Stream Test Summary Data.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() and callGetPacketStreamStatistics()
        - Returns comprehensive STSD data including error counts and seconds
        - Includes linecode, UDP checksum, FCS, IP checksum errors
        - Includes stream sequence, bit errors, and alarm seconds
        - Complex CSV format with quoted values
        
        Python TODO:
        - Call packet and stream statistics methods
        - Build comprehensive STSD data string
        - Return formatted STSD data as bytes
        """
        response = None
        # TODO: Implement STSD query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getEventLog(self, parameters):
        """**RES:EVENTLOG** - Query event log entries.
        
        C++ Implementation Details:
        - Accesses event log system
        - Returns formatted event log entries
        - May require parameters for filtering
        
        Python TODO:
        - Implement event log access
        - Return formatted event log data as bytes
        """
        response = None
        # TODO: Implement event log query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResRfLevel(self, parameters):
        """**RES:RF** - Process remote fault level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resRfLevel table
        - Sub-commands: SECS? (already implemented separately)
        - Accesses idlStatPacket.remoteLinkFault structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for remote fault
        - Support query commands for alarm seconds
        """
        response = None
        # TODO: Implement RF level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResLfdLevel(self, parameters):
        """**RES:LFD** - Process local fault detect level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resLfdLevel table
        - Sub-commands for local fault detection queries
        - Accesses local fault detection structures
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for local fault detect
        - Support query commands for fault detection
        """
        response = None
        # TODO: Implement LFD level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResUnCorrCHecLevel(self, parameters):
        """**RES:UCHEC** - Process uncorrectable CHEC error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resUnCorrCHecLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.uncorrectableCHec structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for uncorrectable CHEC errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement uncorrectable CHEC level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResCorrCHecLevel(self, parameters):
        """**RES:CHEC** - Process correctable CHEC error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resCorrCHecLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.correctableCHec structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for correctable CHEC errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement correctable CHEC level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResUnCorrTHecLevel(self, parameters):
        """**RES:UTHEC** - Process uncorrectable THEC error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resUnCorrTHecLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.uncorrectableTHec structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for uncorrectable THEC errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement uncorrectable THEC level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResCorrTHecLevel(self, parameters):
        """**RES:THEC** - Process correctable THEC error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resCorrTHecLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.correctableTHec structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for correctable THEC errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement correctable THEC level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResUnCorrEHecLevel(self, parameters):
        """**RES:UEHEC** - Process uncorrectable EHEC error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resUnCorrEHecLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.uncorrectableEHec structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for uncorrectable EHEC errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement uncorrectable EHEC level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResCorrEHecLevel(self, parameters):
        """**RES:EHEC** - Process correctable EHEC error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resCorrEHecLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.correctableEHec structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for correctable EHEC errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement correctable EHEC level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResSfcsLevel(self, parameters):
        """**RES:SFCS** - Process superblock FCS error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resSfcsLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.superFcs structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for superblock FCS errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement SFCS level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResLfLevel(self, parameters):
        """**RES:LF** - Process local fault level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resLfLevel table
        - Sub-commands: SECS? (already implemented separately)
        - Accesses idlStatPacket.localLinkFault structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for local fault
        - Support query commands for alarm seconds
        """
        response = None
        # TODO: Implement LF level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResLoccsLevel(self, parameters):
        """**RES:LOCCS** - Process loss of character sync level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resLoccsLevel table
        - Sub-commands for character sync loss queries
        - Accesses character sync structures
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for loss of character sync
        - Support query commands for sync loss
        """
        response = None
        # TODO: Implement LOCCS level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResLocLevel(self, parameters):
        """**RES:LOCS** - Process loss of clock level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resLocLevel table
        - Sub-commands for clock loss queries
        - Accesses clock loss structures
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for loss of clock
        - Support query commands for clock loss
        """
        response = None
        # TODO: Implement LOCS level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResFcsLevel(self, parameters):
        """**RES:FCS** or **RES:CRC** - Process FCS/CRC error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resFcsLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.fcs structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for FCS errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement FCS level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getFabricLoginStatus(self, parameters):
        """**RES:FABRICLOGIN?** - Query Fibre Channel fabric login status.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns fabric login status
        - Format depends on login state
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return fabric login status as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getPortLoginStatus(self, parameters):
        """**RES:PORTLOGIN?** - Query Fibre Channel port login status.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns port login status
        - Format depends on login state
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return port login status as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResFcDispLevel(self, parameters):
        """**RES:FCDISP** - Process FC disparity error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resFcDispLevel table
        - Sub-commands for FC disparity error queries
        - Accesses FC disparity structures
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for FC disparity errors
        - Support query commands for disparity errors
        """
        response = None
        # TODO: Implement FC disparity level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResFcEofALevel(self, parameters):
        """**RES:FCEOFA** - Process FC EOF abort level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resFcEofALevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.fcEofAbort structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for FC EOF abort
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement FC EOF abort level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResRuntLevel(self, parameters):
        """**RES:RUNT** - Process runt packet error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resRuntLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.runt structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for runt packet errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement runt level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResInvSuperLevel(self, parameters):
        """**RES:INVSUPER** - Process invalid superblock error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resInvSuperLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.invalidSuper structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for invalid superblock errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement invalid superblock level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResJabberLevel(self, parameters):
        """**RES:JABBER** - Process jabber packet level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resJabberLevel table
        - Sub-commands: COUNT?, ES?, SECS?
        - Accesses idlStatPacket.jabber structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for jabber packets
        - Support query commands for error counts and alarm seconds
        """
        response = None
        # TODO: Implement jabber level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResTcpChecksumLevel(self, parameters):
        """**RES:TCPERR** - Process TCP checksum error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resTcpChecksumLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.tcpChecksum structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for TCP checksum errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement TCP checksum level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResUdpChecksumLevel(self, parameters):
        """**RES:UDPERR** - Process UDP checksum error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resUdpChecksumLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.udpChecksum structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for UDP checksum errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement UDP checksum level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getCurrentAlarms(self, parameters):
        """**RES:SCANALARMS?** - Query all current alarms in system.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() and callGetPacketStreamStatistics()
        - Calls getAlarmToken() for each alarm type
        - Returns concatenated alarm tokens for all active alarms
        - Returns "+0" if no alarms present
        
        Python TODO:
        - Call packet statistics methods
        - Build alarm token list for all active alarms
        - Return formatted alarm token string
        """
        response = None
        # TODO: Implement alarm scanning logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResFcEofErrLevel(self, parameters):
        """**RES:FCEOFERR** - Process FC EOF error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resFcEofErrLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.fcEofErr structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for FC EOF errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement FC EOF error level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResAlarmLevel(self, parameters):
        """**RES:AL** - Process alarm level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resAlarmLevel table
        - Sub-commands for various alarm queries
        - Accesses alarm structures
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for alarms
        - Support query commands for alarm status
        """
        response = None
        # TODO: Implement alarm level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResDisparityLevel(self, parameters):
        """**RES:DISPARITY** - Process disparity error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resDisparityLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.disparity structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for disparity errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement disparity level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResCaptureLevel(self, parameters):
        """**RES:CAPTURE** - Process packet capture level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resCaptureLevel table
        - Sub-commands for packet capture control and queries
        - Accesses packet capture structures
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for packet capture
        - Support query and control commands
        """
        response = None
        # TODO: Implement capture level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResHdrMMLevel(self, parameters):
        """**RES:HDRMM** - Process header mismatch level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resHdrMMLevel table
        - Sub-commands for header mismatch queries
        - Accesses header mismatch structures
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for header mismatches
        - Support query commands for mismatch detection
        """
        response = None
        # TODO: Implement header mismatch level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResRxPacketLevel(self, parameters):
        """**RES:RXPACK** - Process RX packet level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resRxPacketLevel table
        - Sub-commands: IDLE?
        - Accesses idlStatPacket.rxGfpIdlePackets structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for RX packets
        - Support query commands for idle packets
        """
        response = None
        # TODO: Implement RX packet level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResUtilLevel(self, parameters):
        """**RES:UTIL** - Process utilization level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resUtilLevel table
        - Sub-commands: CUR, AVG, MAX, MIN, MPLS, VLAN, IPV4, IPV6, L1, L2
        - Accesses utilization structures
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for utilization
        - Support query commands for various utilization metrics
        """
        response = None
        # TODO: Implement utilization level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResMplsLevel(self, parameters):
        """**RES:MPLS** - Process MPLS level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resMplsLevel table
        - Sub-commands for MPLS-related queries
        - Accesses MPLS-specific fields
        - Requires MPLS license
        
        Python TODO:
        - Implement sub-command parsing for MPLS statistics
        - Support query commands for MPLS-tagged traffic
        """
        response = None
        # TODO: Implement MPLS level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResPacketLevel(self, parameters):
        """**RES:PACK** - Process packet level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resPacketLevel table
        - Sub-commands for general packet queries
        - Accesses packet structures
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for packet statistics
        - Support query commands for packet data
        """
        response = None
        # TODO: Implement packet level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResOversizedCount(self, parameters):
        """**RES:SUPJUMBO?** - Query the count of super jumbo packets.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Returns idlStatPacket.rxSuperJumboPackets.count field
        - Format: signed 64-bit integer ("%I64i")
        - No parameters required
        
        Python TODO:
        - Call veexlib packet statistics method
        - Return rxSuperJumboPackets.count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResSyncHdrLevel(self, parameters):
        """**RES:SYNCHDR** - Process sync header error level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resSyncHdrLevel table
        - Sub-commands: COUNT?, ES?, AVGRATE?, CURRATE?
        - Accesses idlStatPacket.syncHdr structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for sync header errors
        - Support query commands for error counts and rates
        """
        response = None
        # TODO: Implement sync header level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResBlockLockLossLevel(self, parameters):
        """**RES:BLKLOC** - Process block lock loss level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resBlockLockLossLevel table
        - Sub-commands: SECS? (already implemented separately)
        - Accesses idlStatPacket.blockLockLoss structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for block lock loss
        - Support query commands for alarm seconds
        """
        response = None
        # TODO: Implement block lock loss level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doResHiBerLevel(self, parameters):
        """**RES:HIBER** - Process high BER level commands.
        
        C++ Implementation Details:
        - Calls TStartParse() with resHiBerLevel table
        - Sub-commands: SECS? (already implemented separately)
        - Accesses idlStatPacket.hiBER structure
        - No parameters at this level
        
        Python TODO:
        - Implement sub-command parsing for high BER
        - Support query commands for alarm seconds
        """
        response = None
        # TODO: Implement high BER level parsing
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getCaptureStatus(self, parameters):
        """**RES:CAPSTATUS?** - Query packet capture status.
        
        C++ Implementation Details:
        - Queries packet capture system status
        - Returns capture state (running, stopped, etc.)
        - No parameters required
        
        Python TODO:
        - Call packet capture status method
        - Return capture status as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getCaptureCount(self, parameters):
        """**RES:CAPCOUNT?** - Query packet capture count.
        
        C++ Implementation Details:
        - Queries number of packets captured
        - Returns capture count
        - No parameters required
        
        Python TODO:
        - Call packet capture count method
        - Return capture count as bytes
        """
        response = None
        # TODO: Implement query logic
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

# This table contains all the system SCPI commands. Note that queries must
# come before the matching setting commands. Also if two commands start with
# the same text then the longer one must come first.
commandTable = [
    Cmnd(b"ARP:GATEWAY", ScpiPacket.setGatewayAddr),
    Cmnd(b"ARP:GATEWAY?", ScpiPacket.getGatewayAddr),
    Cmnd(b"ARP:IPSRC", ScpiPacket.setIPSrc),
    Cmnd(b"ARP:IPSRC?", ScpiPacket.getIPSrc),
    Cmnd(b"ARP:MACSRC", ScpiPacket.setMACSrc),
    Cmnd(b"ARP:MACSRC?", ScpiPacket.getMACSrc),
    Cmnd(b"ARP:SUBNET", ScpiPacket.setSubnetAddr),
    Cmnd(b"ARP:SUBNET?", ScpiPacket.getSubnetAddr),
    Cmnd(b"FETC:AL:CPP?", ScpiPacket.getResCpPowerLossState),
    Cmnd(b"FETC:AL:HDRMM?", ScpiPacket.getResHdrMMState),
    Cmnd(b"FETC:AL:LFD?", ScpiPacket.getResLfdState),
    Cmnd(b"FETC:AL:LINK?", ScpiPacket.getResLinkState),
    Cmnd(b"FETC:AL:LOC?", ScpiPacket.getResLocState),
    Cmnd(b"FETC:AL:LOCCS?", ScpiPacket.getResLoccsState),
    Cmnd(b"FETC:AL:LOS?", ScpiPacket.getResLosState),
    Cmnd(b"FETC:AL:MODULESTATUS?", ScpiPacket.getResSummaryModuleState),
    Cmnd(b"FETC:AL:PAUSED?", ScpiPacket.getResAlarmPausedState),
    Cmnd(b"FETC:BLKLOC:SECS?", ScpiPacket.getBlockLockLossSecs),
    Cmnd(b"FETC:CAPCOUNT?", ScpiPacket.getCaptureCount),
    Cmnd(b"FETC:CAPSTATUS?", ScpiPacket.getCaptureStatus),
    Cmnd(b"FETC:CAPTURE:CID?", ScpiPacket.getCaptureCid),  # GFP capture CID handler complete
    Cmnd(b"FETC:CAPTURE:EXI?", ScpiPacket.getCaptureExi),
    Cmnd(b"FETC:CAPTURE:PFI?", ScpiPacket.getCapturePfi),
    Cmnd(b"FETC:CAPTURE:PLI?", ScpiPacket.getCapturePli),
    Cmnd(b"FETC:CAPTURE:PTI?", ScpiPacket.getCapturePti),
    Cmnd(b"FETC:CAPTURE:SELECT", ScpiPacket.setRxCidFilter),  # Shared GFP CID filter setter
    Cmnd(b"FETC:CAPTURE:SELECT?", ScpiPacket.getRxCidFilter),  # Shared GFP CID filter query
    Cmnd(b"FETC:CAPTURE:SPARE?", ScpiPacket.getCaptureSpare),
    Cmnd(b"FETC:CAPTURE:UPI?", ScpiPacket.getCaptureUpi),
    Cmnd(b"FETC:CHEC:AVGRATE?", ScpiPacket.getResCorrCHecAvgRate),
    Cmnd(b"FETC:CHEC:COUNT?", ScpiPacket.getResCorrCHecCount),
    Cmnd(b"FETC:CHEC:CURRATE?", ScpiPacket.getResCorrCHecCurRate),
    Cmnd(b"FETC:CHEC:ES?", ScpiPacket.getResCorrCHecES),
    Cmnd(b"FETC:COLLISION:AVGRATE?", ScpiPacket.getResCollisionAvgRate),
    Cmnd(b"FETC:COLLISION:COUNT?", ScpiPacket.getResCollisionCount),
    Cmnd(b"FETC:COLLISION:CURRATE?", ScpiPacket.getResCollisionCurRate),
    Cmnd(b"FETC:COLLISION:ES?", ScpiPacket.getResCollisionES),
    Cmnd(b"FETC:CRC:AVGRATE?", ScpiPacket.getResFcsAvgRate),
    Cmnd(b"FETC:CRC:COUNT?", ScpiPacket.getResFcsCount),
    Cmnd(b"FETC:CRC:CURRATE?", ScpiPacket.getResFcsCurRate),
    Cmnd(b"FETC:CRC:ES?", ScpiPacket.getResFcsES),
    Cmnd(b"FETC:DISPARITY:AVGRATE?", ScpiPacket.getResDisparityAvgRate),
    Cmnd(b"FETC:DISPARITY:COUNT?", ScpiPacket.getResDisparityCount),
    Cmnd(b"FETC:DISPARITY:CURRATE?", ScpiPacket.getResDisparityCurRate),
    Cmnd(b"FETC:DISPARITY:ES?", ScpiPacket.getResDisparityES),
    Cmnd(b"FETC:EHEC:AVGRATE?", ScpiPacket.getResCorrEHecAvgRate),
    Cmnd(b"FETC:EHEC:COUNT?", ScpiPacket.getResCorrEHecCount),
    Cmnd(b"FETC:EHEC:CURRATE?", ScpiPacket.getResCorrEHecCurRate),
    Cmnd(b"FETC:EHEC:ES?", ScpiPacket.getResCorrEHecES),
    Cmnd(b"FETC:EVENTLOG", ScpiPacket.getEventLog),
    Cmnd(b"FETC:FABRICLOGIN?", ScpiPacket.getFabricLoginStatus),
    Cmnd(b"FETC:FCALIGN:AVGRATE?", ScpiPacket.getResFcAlignAvgRate),
    Cmnd(b"FETC:FCALIGN:COUNT?", ScpiPacket.getResFcAlignCount),
    Cmnd(b"FETC:FCALIGN:CURRATE?", ScpiPacket.getResFcAlignCurRate),
    Cmnd(b"FETC:FCALIGN:ES?", ScpiPacket.getResFcAlignES),
    Cmnd(b"FETC:FCBBCREDIT?", ScpiPacket.getFcBbCredit),
    Cmnd(b"FETC:FCDISP:AVGRATE?", ScpiPacket.getResFcDispAvgRate),
    Cmnd(b"FETC:FCDISP:COUNT?", ScpiPacket.getResFcDispCount),
    Cmnd(b"FETC:FCDISP:CURRATE?", ScpiPacket.getResFcDispCurRate),
    Cmnd(b"FETC:FCDISP:ES?", ScpiPacket.getResFcDispES),
    Cmnd(b"FETC:FCEOFA:AVGRATE?", ScpiPacket.getResFcEofAAvgRate),
    Cmnd(b"FETC:FCEOFA:COUNT?", ScpiPacket.getResFcEofACount),
    Cmnd(b"FETC:FCEOFA:CURRATE?", ScpiPacket.getResFcEofACurRate),
    Cmnd(b"FETC:FCEOFA:ES?", ScpiPacket.getResFcEofAES),
    Cmnd(b"FETC:FCEOFERR:AVGRATE?", ScpiPacket.getResFcEofErrAvgRate),
    Cmnd(b"FETC:FCEOFERR:COUNT?", ScpiPacket.getResFcEofErrCount),
    Cmnd(b"FETC:FCEOFERR:CURRATE?", ScpiPacket.getResFcEofErrCurRate),
    Cmnd(b"FETC:FCEOFERR:ES?", ScpiPacket.getResFcEofErrES),
    Cmnd(b"FETC:FCRRDYPEND?", ScpiPacket.getFcRrdyPend),
    Cmnd(b"FETC:FCRXRRDY?", ScpiPacket.getFcRxRrdy),
    Cmnd(b"FETC:FCS:AVGRATE?", ScpiPacket.getResFcsAvgRate),
    Cmnd(b"FETC:FCS:COUNT?", ScpiPacket.getResFcsCount),
    Cmnd(b"FETC:FCS:CURRATE?", ScpiPacket.getResFcsCurRate),
    Cmnd(b"FETC:FCS:ES?", ScpiPacket.getResFcsES),
    Cmnd(b"FETC:FCTXRRDY?", ScpiPacket.getFcTxRrdy),
    Cmnd(b"FETC:HDRMM:SECS?", ScpiPacket.getResHdrMMSecs),
    Cmnd(b"FETC:HDRMM:STATE?", ScpiPacket.getResHdrMMState),
    Cmnd(b"FETC:HIBER:SECS?", ScpiPacket.getHiBerSecs),
    Cmnd(b"FETC:INVSUPER:AVGRATE?", ScpiPacket.getResInvSuperAvgRate),
    Cmnd(b"FETC:INVSUPER:COUNT?", ScpiPacket.getResInvSuperCount),
    Cmnd(b"FETC:INVSUPER:CURRATE?", ScpiPacket.getResInvSuperCurRate),
    Cmnd(b"FETC:INVSUPER:ES?", ScpiPacket.getResInvSuperES),
    Cmnd(b"FETC:IPCHECKSUM:AVGRATE?", ScpiPacket.getResIpChecksumAvgRate),
    Cmnd(b"FETC:IPCHECKSUM:COUNT?", ScpiPacket.getResIpChecksumCount),
    Cmnd(b"FETC:IPCHECKSUM:CURRATE?", ScpiPacket.getResIpChecksumCurRate),
    Cmnd(b"FETC:IPCHECKSUM:ES?", ScpiPacket.getResIpChecksumES),
    Cmnd(b"FETC:JABBER:SECS?", ScpiPacket.getJabberSecs),
    Cmnd(b"FETC:JUMBO?", ScpiPacket.getResRxJumboPackets),
    Cmnd(b"FETC:LF:SECS?", ScpiPacket.getLfSecs),
    Cmnd(b"FETC:LFD:SECS?", ScpiPacket.getResLfdSecs),
    Cmnd(b"FETC:LFD:STATE?", ScpiPacket.getResLfdState),
    Cmnd(b"FETC:LINECODE:AVGRATE?", ScpiPacket.getResLinecodeAvgRate),
    Cmnd(b"FETC:LINECODE:COUNT?", ScpiPacket.getResLinecodeCount),
    Cmnd(b"FETC:LINECODE:CURRATE?", ScpiPacket.getResLinecodeCurRate),
    Cmnd(b"FETC:LINECODE:ES?", ScpiPacket.getResLinecodeES),
    Cmnd(b"FETC:LINK:SECS?", ScpiPacket.getResLinkSecs),
    Cmnd(b"FETC:LINK:STATE?", ScpiPacket.getResLinkState),
    Cmnd(b"FETC:LINK:STATUS?", ScpiPacket.getResLinkStatus),
    Cmnd(b"FETC:LOCCS:SECS?", ScpiPacket.getResLoccsSecs),
    Cmnd(b"FETC:LOCCS:STATE?", ScpiPacket.getResLoccsState),
    Cmnd(b"FETC:LOCS:SECS?", ScpiPacket.getResLocSecs),
    Cmnd(b"FETC:LOCS:STATE?", ScpiPacket.getResLocState),
    Cmnd(b"FETC:LOS:SECS?", ScpiPacket.getResLosSecs),
    Cmnd(b"FETC:LOS:STATE?", ScpiPacket.getResLosState),
    Cmnd(b"FETC:LOSS:SECS?", ScpiPacket.getResCpPowerLossSecs),
    Cmnd(b"FETC:LOSS:STATE?", ScpiPacket.getResCpPowerLossState),
    Cmnd(b"FETC:MOSSALRMS?", ScpiPacket.getTxIdle),
    Cmnd(b"FETC:MOSSERRS?", ScpiPacket.getTxIdle),
    Cmnd(b"FETC:MPLS:PACKETS?", ScpiPacket.getResMplsPacketsByLevel),
    Cmnd(b"FETC:MPLS:TC?", ScpiPacket.getResMplsTC),
    Cmnd(b"FETC:OVERSIZED:AVGRATE?", ScpiPacket.getResOversizedAvgRate),
    Cmnd(b"FETC:OVERSIZED:COUNT?", ScpiPacket.getResOversizedCount),
    Cmnd(b"FETC:OVERSIZED:CURRATE?", ScpiPacket.getResOversizedCurRate),
    Cmnd(b"FETC:OVERSIZED:ES?", ScpiPacket.getResOversizedES),
    Cmnd(b"FETC:PACK:BGP?", ScpiPacket.getResBgpPackets),
    Cmnd(b"FETC:PACK:ICMP?", ScpiPacket.getResIcmpPackets),
    Cmnd(b"FETC:PACK:IGMP?", ScpiPacket.getResIgmpPackets),
    Cmnd(b"FETC:PACK:IP?", ScpiPacket.getResIpPackets),
    Cmnd(b"FETC:PACK:IPV6?", ScpiPacket.getResIpv6Packets),
    Cmnd(b"FETC:PACK:MPLS?", ScpiPacket.getResMplsPackets),
    Cmnd(b"FETC:PACK:OSPF?", ScpiPacket.getResOspfPackets),
    Cmnd(b"FETC:PACK:TCP?", ScpiPacket.getResTcpPackets),
    Cmnd(b"FETC:PACK:UDP?", ScpiPacket.getResUdpPackets),
    Cmnd(b"FETC:PAUSE:ENDPACKETS?", ScpiPacket.getResPauseEndPackets),
    Cmnd(b"FETC:PAUSE:PACKETS?", ScpiPacket.getResPausePackets),
    Cmnd(b"FETC:PAUSE:QUANTAS?", ScpiPacket.getResPauseQuantas),
    Cmnd(b"FETC:PAUSE:SECS?", ScpiPacket.getResPauseSecs),
    Cmnd(b"FETC:PAUSE:STATE?", ScpiPacket.getResPauseState),
    Cmnd(b"FETC:PAUSE:TXENDPACKETS?", ScpiPacket.getResTxPauseEndPackets),
    Cmnd(b"FETC:PAUSE:TXPACKETS?", ScpiPacket.getResTxPausePackets),
    Cmnd(b"FETC:PAUSE:TXQUANTAS?", ScpiPacket.getResTxPauseQuantas),
    Cmnd(b"FETC:PAUSED:ENDPACKETS?", ScpiPacket.getResPauseEndPackets),
    Cmnd(b"FETC:PAUSED:PACKETS?", ScpiPacket.getResPausePackets),
    Cmnd(b"FETC:PAUSED:QUANTAS?", ScpiPacket.getResPauseQuantas),
    Cmnd(b"FETC:PAUSED:SECS?", ScpiPacket.getResPauseSecs),
    Cmnd(b"FETC:PAUSED:STATE?", ScpiPacket.getResPauseState),
    Cmnd(b"FETC:PAUSED:TXENDPACKETS?", ScpiPacket.getResTxPauseEndPackets),
    Cmnd(b"FETC:PAUSED:TXPACKETS?", ScpiPacket.getResTxPausePackets),
    Cmnd(b"FETC:PAUSED:TXQUANTAS?", ScpiPacket.getResTxPauseQuantas),
    Cmnd(b"FETC:PFCS:AVGRATE?", ScpiPacket.getResPfcsAvgRate),
    Cmnd(b"FETC:PFCS:COUNT?", ScpiPacket.getResPfcsCount),
    Cmnd(b"FETC:PFCS:CURRATE?", ScpiPacket.getResPfcsCurRate),
    Cmnd(b"FETC:PFCS:ES?", ScpiPacket.getResPfcsES),
    Cmnd(b"FETC:PORTLOGIN?", ScpiPacket.getPortLoginStatus),
    Cmnd(b"FETC:RF:SECS?", ScpiPacket.getRfSecs),
    Cmnd(b"FETC:RUNT:AVGRATE?", ScpiPacket.getResRuntAvgRate),
    Cmnd(b"FETC:RUNT:COUNT?", ScpiPacket.getResRuntCount),
    Cmnd(b"FETC:RUNT:CURRATE?", ScpiPacket.getResRuntCurRate),
    Cmnd(b"FETC:RUNT:ES?", ScpiPacket.getResRuntES),
    Cmnd(b"FETC:RX1024?", ScpiPacket.getRx1024bp),
    Cmnd(b"FETC:RX128?", ScpiPacket.getRx128bp),
    Cmnd(b"FETC:RX1519?", ScpiPacket.getRx1519bp),
    Cmnd(b"FETC:RX256?", ScpiPacket.getRx256bp),
    Cmnd(b"FETC:RX512?", ScpiPacket.getRx512bp),
    Cmnd(b"FETC:RX64?", ScpiPacket.getRx64bp),
    Cmnd(b"FETC:RX65?", ScpiPacket.getRx65bp),
    Cmnd(b"FETC:RXBCAST?", ScpiPacket.getRxbCast),
    Cmnd(b"FETC:RXBYT?", ScpiPacket.getResRxBytes),
    Cmnd(b"FETC:RXIDLE?", ScpiPacket.getRxIdle),
    Cmnd(b"FETC:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecNone),
    Cmnd(b"FETC:RXMCAST?", ScpiPacket.getRxmCast),
    Cmnd(b"FETC:RXPACK:BGP?", ScpiPacket.getResBgpPackets),
    Cmnd(b"FETC:RXPACK:BROAD?", ScpiPacket.getRxbCast),
    Cmnd(b"FETC:RXPACK:BYT?", ScpiPacket.getResRxBytes),
    Cmnd(b"FETC:RXPACK:ICMP?", ScpiPacket.getResIcmpPackets),
    Cmnd(b"FETC:RXPACK:IDLE?", ScpiPacket.getRxIdle),
    Cmnd(b"FETC:RXPACK:IGMP?", ScpiPacket.getResIgmpPackets),
    Cmnd(b"FETC:RXPACK:IPV4?", ScpiPacket.getResIpPackets),
    Cmnd(b"FETC:RXPACK:IPV6?", ScpiPacket.getResIpv6Packets),
    Cmnd(b"FETC:RXPACK:JUMBO?", ScpiPacket.getResRxJumboPackets),
    Cmnd(b"FETC:RXPACK:L2BYT?", ScpiPacket.getResRxBytes),
    Cmnd(b"FETC:RXPACK:MPLS:TAG?", ScpiPacket.getResMplsPacketsByLevel),
    Cmnd(b"FETC:RXPACK:MPLS:TC?", ScpiPacket.getResMplsTC),
    Cmnd(b"FETC:RXPACK:MPLS?", ScpiPacket.getResMplsPackets),
    Cmnd(b"FETC:RXPACK:MULTI?", ScpiPacket.getRxmCast),
    Cmnd(b"FETC:RXPACK:OSPF?", ScpiPacket.getResOspfPackets),
    Cmnd(b"FETC:RXPACK:PAUSE:ENDPACKETS?", ScpiPacket.getResPauseEndPackets),
    Cmnd(b"FETC:RXPACK:PAUSE:PACKETS?", ScpiPacket.getResPausePackets),
    Cmnd(b"FETC:RXPACK:PAUSE:QUANT?", ScpiPacket.getResPauseQuantas),
    Cmnd(b"FETC:RXPACK:SIZE:1024?", ScpiPacket.getRx1024bp),
    Cmnd(b"FETC:RXPACK:SIZE:128?", ScpiPacket.getRx128bp),
    Cmnd(b"FETC:RXPACK:SIZE:1519?", ScpiPacket.getRx1519bp),
    Cmnd(b"FETC:RXPACK:SIZE:256?", ScpiPacket.getRx256bp),
    Cmnd(b"FETC:RXPACK:SIZE:512?", ScpiPacket.getRx512bp),
    Cmnd(b"FETC:RXPACK:SIZE:64?", ScpiPacket.getRx64bp),
    Cmnd(b"FETC:RXPACK:SIZE:65?", ScpiPacket.getRx65bp),
    Cmnd(b"FETC:RXPACK:SUPERBLOCK?", ScpiPacket.getRxSuperBlock),
    Cmnd(b"FETC:RXPACK:SUPERJUMBO?", ScpiPacket.getResOversizedCount),
    Cmnd(b"FETC:RXPACK:TCP?", ScpiPacket.getResTcpPackets),
    Cmnd(b"FETC:RXPACK:UDP?", ScpiPacket.getResUdpPackets),
    Cmnd(b"FETC:RXPACK:UNI?", ScpiPacket.getRxuCast),
    Cmnd(b"FETC:RXPACK:VLAN:QOS?", ScpiPacket.getResVlanPacketsQos),
    Cmnd(b"FETC:RXPACK:VLAN:TAG?", ScpiPacket.getResVlanPackets),
    Cmnd(b"FETC:RXPACK:VLAN?", ScpiPacket.getResVlanPackets1),
    Cmnd(b"FETC:RXPACK?", ScpiPacket.getResRxPackets),
    Cmnd(b"FETC:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthNone),
    Cmnd(b"FETC:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecNone),
    Cmnd(b"FETC:RXSUPERBLOCK?", ScpiPacket.getRxSuperBlock),
    Cmnd(b"FETC:RXUCAST?", ScpiPacket.getRxuCast),
    Cmnd(b"FETC:SCANALARMS?", ScpiPacket.getCurrentAlarms),
    Cmnd(b"FETC:SCANERRORS?", ScpiPacket.getCurrentErrors),
    Cmnd(b"FETC:SFCS:AVGRATE?", ScpiPacket.getResSfcsAvgRate),
    Cmnd(b"FETC:SFCS:COUNT?", ScpiPacket.getResSfcsCount),
    Cmnd(b"FETC:SFCS:CURRATE?", ScpiPacket.getResSfcsCurRate),
    Cmnd(b"FETC:SFCS:ES?", ScpiPacket.getResSfcsES),
    Cmnd(b"FETC:SPM?", ScpiPacket.getResSPM),
    Cmnd(b"FETC:STSD?", ScpiPacket.getResSTSD),
    Cmnd(b"FETC:SUPJUMBO?", ScpiPacket.getResOversizedCount),
    Cmnd(b"FETC:SYNCHDR:AVGRATE?", ScpiPacket.getResSyncHdrAvgRate),
    Cmnd(b"FETC:SYNCHDR:COUNT?", ScpiPacket.getResSyncHdrCount),
    Cmnd(b"FETC:SYNCHDR:CURRATE?", ScpiPacket.getResSyncHdrCurRate),
    Cmnd(b"FETC:SYNCHDR:ES?", ScpiPacket.getResSyncHdrES),
    Cmnd(b"FETC:TCPERR:AVGRATE?", ScpiPacket.getResTcpChecksumAvgRate),
    Cmnd(b"FETC:TCPERR:COUNT?", ScpiPacket.getResTcpChecksumCount),
    Cmnd(b"FETC:TCPERR:CURRATE?", ScpiPacket.getResTcpChecksumCurRate),
    Cmnd(b"FETC:TCPERR:ES?", ScpiPacket.getResTcpChecksumES),
    Cmnd(b"FETC:THEC:AVGRATE?", ScpiPacket.getResCorrTHecAvgRate),
    Cmnd(b"FETC:THEC:COUNT?", ScpiPacket.getResCorrTHecCount),
    Cmnd(b"FETC:THEC:CURRATE?", ScpiPacket.getResCorrTHecCurRate),
    Cmnd(b"FETC:THEC:ES?", ScpiPacket.getResCorrTHecES),
    Cmnd(b"FETC:TXBYT?", ScpiPacket.getResTxBytes),
    Cmnd(b"FETC:TXIDLE?", ScpiPacket.getTxIdle),
    Cmnd(b"FETC:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecNone),
    Cmnd(b"FETC:TXPACK:BYT?", ScpiPacket.getResTxBytes),
    Cmnd(b"FETC:TXPACK:IDLE?", ScpiPacket.getTxIdle),
    Cmnd(b"FETC:TXPACK:IP?", ScpiPacket.getResTxIpPackets),
    Cmnd(b"FETC:TXPACK:IPV4?", ScpiPacket.getResTxIpPackets),
    Cmnd(b"FETC:TXPACK:IPV6?", ScpiPacket.getResTxIpv6Packets),
    Cmnd(b"FETC:TXPACK:L2BYT?", ScpiPacket.getResTxBytes),
    Cmnd(b"FETC:TXPACK:MPLS?", ScpiPacket.getResTxMplsPackets),
    Cmnd(b"FETC:TXPACK:PAUSE:ENDPACKETS?", ScpiPacket.getResTxPauseEndPackets),
    Cmnd(b"FETC:TXPACK:PAUSE:PACKETS?", ScpiPacket.getResTxPausePackets),
    Cmnd(b"FETC:TXPACK:PAUSE:QUANT?", ScpiPacket.getResTxPauseQuantas),
    Cmnd(b"FETC:TXPACK:SUPERBLOCK?", ScpiPacket.getTxSuperBlock),
    Cmnd(b"FETC:TXPACK:VLAN?", ScpiPacket.getResTxVlanPackets),
    Cmnd(b"FETC:TXPACK?", ScpiPacket.getResTxPackets),
    Cmnd(b"FETC:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthNone),
    Cmnd(b"FETC:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecNone),
    Cmnd(b"FETC:TXSUPERBLOCK?", ScpiPacket.getTxSuperBlock),
    Cmnd(b"FETC:UCHEC:AVGRATE?", ScpiPacket.getResUnCorrCHecAvgRate),
    Cmnd(b"FETC:UCHEC:COUNT?", ScpiPacket.getResUnCorrCHecCount),
    Cmnd(b"FETC:UCHEC:CURRATE?", ScpiPacket.getResUnCorrCHecCurRate),
    Cmnd(b"FETC:UCHEC:ES?", ScpiPacket.getResUnCorrCHecES),
    Cmnd(b"FETC:UDPERR:AVGRATE?", ScpiPacket.getResUdpChecksumAvgRate),
    Cmnd(b"FETC:UDPERR:COUNT?", ScpiPacket.getResUdpChecksumCount),
    Cmnd(b"FETC:UDPERR:CURRATE?", ScpiPacket.getResUdpChecksumCurRate),
    Cmnd(b"FETC:UDPERR:ES?", ScpiPacket.getResUdpChecksumES),
    Cmnd(b"FETC:UEHEC:AVGRATE?", ScpiPacket.getResUnCorrEHecAvgRate),
    Cmnd(b"FETC:UEHEC:COUNT?", ScpiPacket.getResUnCorrEHecCount),
    Cmnd(b"FETC:UEHEC:CURRATE?", ScpiPacket.getResUnCorrEHecCurRate),
    Cmnd(b"FETC:UEHEC:ES?", ScpiPacket.getResUnCorrEHecES),
    Cmnd(b"FETC:UNDERSIZED:AVGRATE?", ScpiPacket.getResUndersizedAvgRate),
    Cmnd(b"FETC:UNDERSIZED:COUNT?", ScpiPacket.getResUndersizedCount),
    Cmnd(b"FETC:UNDERSIZED:CURRATE?", ScpiPacket.getResUndersizedCurRate),
    Cmnd(b"FETC:UNDERSIZED:ES?", ScpiPacket.getResUndersizedES),
    Cmnd(b"FETC:UTHEC:AVGRATE?", ScpiPacket.getResUnCorrTHecAvgRate),
    Cmnd(b"FETC:UTHEC:COUNT?", ScpiPacket.getResUnCorrTHecCount),
    Cmnd(b"FETC:UTHEC:CURRATE?", ScpiPacket.getResUnCorrTHecCurRate),
    Cmnd(b"FETC:UTHEC:ES?", ScpiPacket.getResUnCorrTHecES),
    Cmnd(b"FETC:UTIL:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgNone),
    Cmnd(b"FETC:UTIL:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgNone),
    Cmnd(b"FETC:UTIL:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgNone),
    Cmnd(b"FETC:UTIL:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgNone),
    Cmnd(b"FETC:UTIL:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgNone),
    Cmnd(b"FETC:UTIL:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgNone),
    Cmnd(b"FETC:UTIL:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecNone),
    Cmnd(b"FETC:UTIL:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthNone),
    Cmnd(b"FETC:UTIL:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecNone),
    Cmnd(b"FETC:UTIL:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecNone),
    Cmnd(b"FETC:UTIL:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthNone),
    Cmnd(b"FETC:UTIL:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecNone),
    Cmnd(b"FETC:UTIL:IPV4:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgIpv4),
    Cmnd(b"FETC:UTIL:IPV4:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgIpv4),
    Cmnd(b"FETC:UTIL:IPV4:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgIpv4),
    Cmnd(b"FETC:UTIL:IPV4:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgIpv4),
    Cmnd(b"FETC:UTIL:IPV4:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgIpv4),
    Cmnd(b"FETC:UTIL:IPV4:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgIpv4),
    Cmnd(b"FETC:UTIL:IPV4:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecIpv4),
    Cmnd(b"FETC:UTIL:IPV4:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthIpv4),
    Cmnd(b"FETC:UTIL:IPV4:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecIpv4),
    Cmnd(b"FETC:UTIL:IPV4:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecIpv4),
    Cmnd(b"FETC:UTIL:IPV4:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthIpv4),
    Cmnd(b"FETC:UTIL:IPV4:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecIpv4),
    Cmnd(b"FETC:UTIL:IPV4:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxIpv4),
    Cmnd(b"FETC:UTIL:IPV4:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxIpv4),
    Cmnd(b"FETC:UTIL:IPV4:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxIpv4),
    Cmnd(b"FETC:UTIL:IPV4:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxIpv4),
    Cmnd(b"FETC:UTIL:IPV4:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxIpv4),
    Cmnd(b"FETC:UTIL:IPV4:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxIpv4),
    Cmnd(b"FETC:UTIL:IPV4:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinIpv4),
    Cmnd(b"FETC:UTIL:IPV4:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinIpv4),
    Cmnd(b"FETC:UTIL:IPV4:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinIpv4),
    Cmnd(b"FETC:UTIL:IPV4:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinIpv4),
    Cmnd(b"FETC:UTIL:IPV4:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinIpv4),
    Cmnd(b"FETC:UTIL:IPV4:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinIpv4),
    Cmnd(b"FETC:UTIL:IPV6:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgIpv6),
    Cmnd(b"FETC:UTIL:IPV6:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgIpv6),
    Cmnd(b"FETC:UTIL:IPV6:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgIpv6),
    Cmnd(b"FETC:UTIL:IPV6:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgIpv6),
    Cmnd(b"FETC:UTIL:IPV6:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgIpv6),
    Cmnd(b"FETC:UTIL:IPV6:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgIpv6),
    Cmnd(b"FETC:UTIL:IPV6:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecIpv6),
    Cmnd(b"FETC:UTIL:IPV6:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthIpv6),
    Cmnd(b"FETC:UTIL:IPV6:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecIpv6),
    Cmnd(b"FETC:UTIL:IPV6:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecIpv6),
    Cmnd(b"FETC:UTIL:IPV6:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthIpv6),
    Cmnd(b"FETC:UTIL:IPV6:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecIpv6),
    Cmnd(b"FETC:UTIL:IPV6:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxIpv6),
    Cmnd(b"FETC:UTIL:IPV6:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxIpv6),
    Cmnd(b"FETC:UTIL:IPV6:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxIpv6),
    Cmnd(b"FETC:UTIL:IPV6:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxIpv6),
    Cmnd(b"FETC:UTIL:IPV6:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxIpv6),
    Cmnd(b"FETC:UTIL:IPV6:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxIpv6),
    Cmnd(b"FETC:UTIL:IPV6:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinIpv6),
    Cmnd(b"FETC:UTIL:IPV6:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinIpv6),
    Cmnd(b"FETC:UTIL:IPV6:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinIpv6),
    Cmnd(b"FETC:UTIL:IPV6:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinIpv6),
    Cmnd(b"FETC:UTIL:IPV6:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinIpv6),
    Cmnd(b"FETC:UTIL:IPV6:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinIpv6),
    Cmnd(b"FETC:UTIL:L1:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgNone),
    Cmnd(b"FETC:UTIL:L1:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgNone),
    Cmnd(b"FETC:UTIL:L1:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgNone),
    Cmnd(b"FETC:UTIL:L1:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgNone),
    Cmnd(b"FETC:UTIL:L1:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgNone),
    Cmnd(b"FETC:UTIL:L1:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgNone),
    Cmnd(b"FETC:UTIL:L1:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecNone),
    Cmnd(b"FETC:UTIL:L1:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthNone),
    Cmnd(b"FETC:UTIL:L1:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecNone),
    Cmnd(b"FETC:UTIL:L1:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecNone),
    Cmnd(b"FETC:UTIL:L1:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthNone),
    Cmnd(b"FETC:UTIL:L1:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecNone),
    Cmnd(b"FETC:UTIL:L1:IPV4:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV4:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinIpv4),
    Cmnd(b"FETC:UTIL:L1:IPV6:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinIpv6),
    Cmnd(b"FETC:UTIL:L1:IPV6:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinIpv6),
    Cmnd(b"FETC:UTIL:L1:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxNone),
    Cmnd(b"FETC:UTIL:L1:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxNone),
    Cmnd(b"FETC:UTIL:L1:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxNone),
    Cmnd(b"FETC:UTIL:L1:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxNone),
    Cmnd(b"FETC:UTIL:L1:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxNone),
    Cmnd(b"FETC:UTIL:L1:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxNone),
    Cmnd(b"FETC:UTIL:L1:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinNone),
    Cmnd(b"FETC:UTIL:L1:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinNone),
    Cmnd(b"FETC:UTIL:L1:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinNone),
    Cmnd(b"FETC:UTIL:L1:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinNone),
    Cmnd(b"FETC:UTIL:L1:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinNone),
    Cmnd(b"FETC:UTIL:L1:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinNone),
    Cmnd(b"FETC:UTIL:L1:MPLS:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinMpls),
    Cmnd(b"FETC:UTIL:L1:MPLS:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinMpls),
    Cmnd(b"FETC:UTIL:L1:VLAN:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinVlan),
    Cmnd(b"FETC:UTIL:L1:VLAN:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinVlan),
    Cmnd(b"FETC:UTIL:L2:AVG:RXMBPS?", ScpiPacket.getResL2RxLinkKBPerSecAvgNone),
    Cmnd(b"FETC:UTIL:L2:AVG:RXPCTBW?", ScpiPacket.getResL2RxLinkPctBandwidthAvgNone),
    Cmnd(b"FETC:UTIL:L2:AVG:TXMBPS?", ScpiPacket.getResL2TxLinkKBPerSecAvgNone),
    Cmnd(b"FETC:UTIL:L2:AVG:TXPCTBW?", ScpiPacket.getResL2TxLinkPctBandwidthAvgNone),
    Cmnd(b"FETC:UTIL:L2:CUR:RXMBPS?", ScpiPacket.getResL2RxLinkKBPerSecNone),
    Cmnd(b"FETC:UTIL:L2:CUR:RXPCTBW?", ScpiPacket.getResL2RxLinkPctBandwidthNone),
    Cmnd(b"FETC:UTIL:L2:CUR:TXMBPS?", ScpiPacket.getResL2TxLinkKBPerSecNone),
    Cmnd(b"FETC:UTIL:L2:CUR:TXPCTBW?", ScpiPacket.getResL2TxLinkPctBandwidthNone),
    Cmnd(b"FETC:UTIL:L2:MAX:RXMBPS?", ScpiPacket.getResL2RxLinkKBPerSecMaxNone),
    Cmnd(b"FETC:UTIL:L2:MAX:RXPCTBW?", ScpiPacket.getResL2RxLinkPctBandwidthMaxNone),
    Cmnd(b"FETC:UTIL:L2:MAX:TXMBPS?", ScpiPacket.getResL2TxLinkKBPerSecMaxNone),
    Cmnd(b"FETC:UTIL:L2:MAX:TXPCTBW?", ScpiPacket.getResL2TxLinkPctBandwidthMaxNone),
    Cmnd(b"FETC:UTIL:L2:MIN:RXMBPS?", ScpiPacket.getResL2RxLinkKBPerSecMinNone),
    Cmnd(b"FETC:UTIL:L2:MIN:RXPCTBW?", ScpiPacket.getResL2RxLinkPctBandwidthMinNone),
    Cmnd(b"FETC:UTIL:L2:MIN:TXMBPS?", ScpiPacket.getResL2TxLinkKBPerSecMinNone),
    Cmnd(b"FETC:UTIL:L2:MIN:TXPCTBW?", ScpiPacket.getResL2TxLinkPctBandwidthMinNone),
    Cmnd(b"FETC:UTIL:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxNone),
    Cmnd(b"FETC:UTIL:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxNone),
    Cmnd(b"FETC:UTIL:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxNone),
    Cmnd(b"FETC:UTIL:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxNone),
    Cmnd(b"FETC:UTIL:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxNone),
    Cmnd(b"FETC:UTIL:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxNone),
    Cmnd(b"FETC:UTIL:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinNone),
    Cmnd(b"FETC:UTIL:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinNone),
    Cmnd(b"FETC:UTIL:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinNone),
    Cmnd(b"FETC:UTIL:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinNone),
    Cmnd(b"FETC:UTIL:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinNone),
    Cmnd(b"FETC:UTIL:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinNone),
    Cmnd(b"FETC:UTIL:MPLS:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgMpls),
    Cmnd(b"FETC:UTIL:MPLS:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgMpls),
    Cmnd(b"FETC:UTIL:MPLS:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgMpls),
    Cmnd(b"FETC:UTIL:MPLS:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgMpls),
    Cmnd(b"FETC:UTIL:MPLS:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgMpls),
    Cmnd(b"FETC:UTIL:MPLS:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgMpls),
    Cmnd(b"FETC:UTIL:MPLS:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMpls),
    Cmnd(b"FETC:UTIL:MPLS:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMpls),
    Cmnd(b"FETC:UTIL:MPLS:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMpls),
    Cmnd(b"FETC:UTIL:MPLS:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMpls),
    Cmnd(b"FETC:UTIL:MPLS:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMpls),
    Cmnd(b"FETC:UTIL:MPLS:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMpls),
    Cmnd(b"FETC:UTIL:MPLS:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxMpls),
    Cmnd(b"FETC:UTIL:MPLS:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxMpls),
    Cmnd(b"FETC:UTIL:MPLS:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxMpls),
    Cmnd(b"FETC:UTIL:MPLS:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxMpls),
    Cmnd(b"FETC:UTIL:MPLS:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxMpls),
    Cmnd(b"FETC:UTIL:MPLS:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxMpls),
    Cmnd(b"FETC:UTIL:MPLS:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinMpls),
    Cmnd(b"FETC:UTIL:MPLS:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinMpls),
    Cmnd(b"FETC:UTIL:MPLS:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinMpls),
    Cmnd(b"FETC:UTIL:MPLS:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinMpls),
    Cmnd(b"FETC:UTIL:MPLS:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinMpls),
    Cmnd(b"FETC:UTIL:MPLS:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinMpls),
    Cmnd(b"FETC:UTIL:VLAN:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgVlan),
    Cmnd(b"FETC:UTIL:VLAN:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgVlan),
    Cmnd(b"FETC:UTIL:VLAN:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgVlan),
    Cmnd(b"FETC:UTIL:VLAN:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgVlan),
    Cmnd(b"FETC:UTIL:VLAN:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgVlan),
    Cmnd(b"FETC:UTIL:VLAN:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgVlan),
    Cmnd(b"FETC:UTIL:VLAN:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecVlan),
    Cmnd(b"FETC:UTIL:VLAN:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthVlan),
    Cmnd(b"FETC:UTIL:VLAN:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecVlan),
    Cmnd(b"FETC:UTIL:VLAN:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecVlan),
    Cmnd(b"FETC:UTIL:VLAN:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthVlan),
    Cmnd(b"FETC:UTIL:VLAN:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecVlan),
    Cmnd(b"FETC:UTIL:VLAN:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxVlan),
    Cmnd(b"FETC:UTIL:VLAN:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxVlan),
    Cmnd(b"FETC:UTIL:VLAN:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxVlan),
    Cmnd(b"FETC:UTIL:VLAN:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxVlan),
    Cmnd(b"FETC:UTIL:VLAN:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxVlan),
    Cmnd(b"FETC:UTIL:VLAN:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxVlan),
    Cmnd(b"FETC:UTIL:VLAN:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinVlan),
    Cmnd(b"FETC:UTIL:VLAN:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinVlan),
    Cmnd(b"FETC:UTIL:VLAN:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinVlan),
    Cmnd(b"FETC:UTIL:VLAN:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinVlan),
    Cmnd(b"FETC:UTIL:VLAN:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinVlan),
    Cmnd(b"FETC:UTIL:VLAN:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinVlan),
    Cmnd(b"FETC:VLAN:PACKETS1?", ScpiPacket.getResVlanPackets1),
    Cmnd(b"FETC:VLAN:PACKETS2?", ScpiPacket.getResVlanPackets2),
    Cmnd(b"FETC:VLAN:PACKETS3?", ScpiPacket.getResVlanPackets3),
    Cmnd(b"FETC:VLAN:PACKETS4?", ScpiPacket.getResVlanPackets4),
    Cmnd(b"FETC:VLAN:PACKETS?", ScpiPacket.getResVlanPackets),
    Cmnd(b"FETC:VLAN:QOS1?", ScpiPacket.getResVlanPacketsQos1),
    Cmnd(b"FETC:VLAN:QOS2?", ScpiPacket.getResVlanPacketsQos2),
    Cmnd(b"FETC:VLAN:QOS3?", ScpiPacket.getResVlanPacketsQos3),
    Cmnd(b"FETC:VLAN:QOS4?", ScpiPacket.getResVlanPacketsQos4),
    Cmnd(b"FETC:VLAN:QOS?", ScpiPacket.getResVlanPacketsQos),
    Cmnd(b"PING:BYTESRX?", ScpiPacket.getBytesRx),
    Cmnd(b"PING:DESTMAC?", ScpiPacket.getDestMAC),
    Cmnd(b"PING:GATEWAY", ScpiPacket.setGatewayAddr),
    Cmnd(b"PING:GATEWAY?", ScpiPacket.getGatewayAddr),
    Cmnd(b"PING:IPDEST", ScpiPacket.setIPDest),
    Cmnd(b"PING:IPDEST?", ScpiPacket.getIPDest),
    Cmnd(b"PING:IPSRC", ScpiPacket.setIPSrc),
    Cmnd(b"PING:IPSRC?", ScpiPacket.getIPSrc),
    Cmnd(b"PING:LOSS?", ScpiPacket.getLoss),
    Cmnd(b"PING:MACSRC", ScpiPacket.setMACSrc),
    Cmnd(b"PING:MACSRC?", ScpiPacket.getMACSrc),
    Cmnd(b"PING:NUMPINGS", ScpiPacket.setNumPings),
    Cmnd(b"PING:NUMPINGS?", ScpiPacket.getNumPings),
    Cmnd(b"PING:PKTLEN", ScpiPacket.setPktLen),
    Cmnd(b"PING:PKTLEN?", ScpiPacket.getPktLen),
    Cmnd(b"PING:PKTTIME?", ScpiPacket.getPktTime),
    Cmnd(b"PING:PKTTTL?", ScpiPacket.getPktTTL),
    Cmnd(b"PING:REPLY?", ScpiPacket.getReply),
    Cmnd(b"PING:RTDAVG?", ScpiPacket.getRTDAvg),
    Cmnd(b"PING:RTDMAX?", ScpiPacket.getRTDMax),
    Cmnd(b"PING:RTDMIN?", ScpiPacket.getRTDMin),
    Cmnd(b"PING:RX?", ScpiPacket.getRx),
    Cmnd(b"PING:SEQNO?", ScpiPacket.getSeqNo),
    Cmnd(b"PING:START", ScpiPacket.setStart),
    Cmnd(b"PING:STOP", ScpiPacket.setStop),
    Cmnd(b"PING:SUBNET", ScpiPacket.setSubnetAddr),
    Cmnd(b"PING:SUBNET?", ScpiPacket.getSubnetAddr),
    Cmnd(b"PING:TIMEOUT", ScpiPacket.setTimeOut),
    Cmnd(b"PING:TIMEOUT?", ScpiPacket.getTimeOut),
    Cmnd(b"PING:TTL", ScpiPacket.setTTL),
    Cmnd(b"PING:TTL?", ScpiPacket.getTTL),
    Cmnd(b"PING:TX?", ScpiPacket.getTx),
    Cmnd(b"RES:AL:CPP?", ScpiPacket.getResCpPowerLossState),
    Cmnd(b"RES:AL:HDRMM?", ScpiPacket.getResHdrMMState),
    Cmnd(b"RES:AL:LFD?", ScpiPacket.getResLfdState),
    Cmnd(b"RES:AL:LINK?", ScpiPacket.getResLinkState),
    Cmnd(b"RES:AL:LOC?", ScpiPacket.getResLocState),
    Cmnd(b"RES:AL:LOCCS?", ScpiPacket.getResLoccsState),
    Cmnd(b"RES:AL:LOS?", ScpiPacket.getResLosState),
    Cmnd(b"RES:AL:MODULESTATUS?", ScpiPacket.getResSummaryModuleState),
    Cmnd(b"RES:AL:PAUSED?", ScpiPacket.getResAlarmPausedState),
    Cmnd(b"RES:BLKLOC:SECS?", ScpiPacket.getBlockLockLossSecs),
    Cmnd(b"RES:CAPCOUNT?", ScpiPacket.getCaptureCount),
    Cmnd(b"RES:CAPSTATUS?", ScpiPacket.getCaptureStatus),
    Cmnd(b"RES:CAPTURE:CID?", ScpiPacket.getCaptureCid),  # Shared GFP capture CID handler
    Cmnd(b"RES:CAPTURE:EXI?", ScpiPacket.getCaptureExi),
    Cmnd(b"RES:CAPTURE:PFI?", ScpiPacket.getCapturePfi),
    Cmnd(b"RES:CAPTURE:PLI?", ScpiPacket.getCapturePli),
    Cmnd(b"RES:CAPTURE:PTI?", ScpiPacket.getCapturePti),
    Cmnd(b"RES:CAPTURE:SELECT", ScpiPacket.setRxCidFilter),  # Shared GFP CID filter setter
    Cmnd(b"RES:CAPTURE:SELECT?", ScpiPacket.getRxCidFilter),  # Shared GFP CID filter query
    Cmnd(b"RES:CAPTURE:SPARE?", ScpiPacket.getCaptureSpare),
    Cmnd(b"RES:CAPTURE:UPI?", ScpiPacket.getCaptureUpi),
    Cmnd(b"RES:CHEC:AVGRATE?", ScpiPacket.getResCorrCHecAvgRate),
    Cmnd(b"RES:CHEC:COUNT?", ScpiPacket.getResCorrCHecCount),
    Cmnd(b"RES:CHEC:CURRATE?", ScpiPacket.getResCorrCHecCurRate),
    Cmnd(b"RES:CHEC:ES?", ScpiPacket.getResCorrCHecES),
    Cmnd(b"RES:COLLISION:AVGRATE?", ScpiPacket.getResCollisionAvgRate),
    Cmnd(b"RES:COLLISION:COUNT?", ScpiPacket.getResCollisionCount),
    Cmnd(b"RES:COLLISION:CURRATE?", ScpiPacket.getResCollisionCurRate),
    Cmnd(b"RES:COLLISION:ES?", ScpiPacket.getResCollisionES),
    Cmnd(b"RES:CRC:AVGRATE?", ScpiPacket.getResFcsAvgRate),
    Cmnd(b"RES:CRC:COUNT?", ScpiPacket.getResFcsCount),
    Cmnd(b"RES:CRC:CURRATE?", ScpiPacket.getResFcsCurRate),
    Cmnd(b"RES:CRC:ES?", ScpiPacket.getResFcsES),
    Cmnd(b"RES:DISPARITY:AVGRATE?", ScpiPacket.getResDisparityAvgRate),
    Cmnd(b"RES:DISPARITY:COUNT?", ScpiPacket.getResDisparityCount),
    Cmnd(b"RES:DISPARITY:CURRATE?", ScpiPacket.getResDisparityCurRate),
    Cmnd(b"RES:DISPARITY:ES?", ScpiPacket.getResDisparityES),
    Cmnd(b"RES:EHEC:AVGRATE?", ScpiPacket.getResCorrEHecAvgRate),
    Cmnd(b"RES:EHEC:COUNT?", ScpiPacket.getResCorrEHecCount),
    Cmnd(b"RES:EHEC:CURRATE?", ScpiPacket.getResCorrEHecCurRate),
    Cmnd(b"RES:EHEC:ES?", ScpiPacket.getResCorrEHecES),
    Cmnd(b"RES:EVENTLOG", ScpiPacket.getEventLog),
    Cmnd(b"RES:FABRICLOGIN?", ScpiPacket.getFabricLoginStatus),
    Cmnd(b"RES:FCALIGN:AVGRATE?", ScpiPacket.getResFcAlignAvgRate),
    Cmnd(b"RES:FCALIGN:COUNT?", ScpiPacket.getResFcAlignCount),
    Cmnd(b"RES:FCALIGN:CURRATE?", ScpiPacket.getResFcAlignCurRate),
    Cmnd(b"RES:FCALIGN:ES?", ScpiPacket.getResFcAlignES),
    Cmnd(b"RES:FCBBCREDIT?", ScpiPacket.getFcBbCredit),
    Cmnd(b"RES:FCDISP:AVGRATE?", ScpiPacket.getResFcDispAvgRate),
    Cmnd(b"RES:FCDISP:COUNT?", ScpiPacket.getResFcDispCount),
    Cmnd(b"RES:FCDISP:CURRATE?", ScpiPacket.getResFcDispCurRate),
    Cmnd(b"RES:FCDISP:ES?", ScpiPacket.getResFcDispES),
    Cmnd(b"RES:FCEOFA:AVGRATE?", ScpiPacket.getResFcEofAAvgRate),
    Cmnd(b"RES:FCEOFA:COUNT?", ScpiPacket.getResFcEofACount),
    Cmnd(b"RES:FCEOFA:CURRATE?", ScpiPacket.getResFcEofACurRate),
    Cmnd(b"RES:FCEOFA:ES?", ScpiPacket.getResFcEofAES),
    Cmnd(b"RES:FCEOFERR:AVGRATE?", ScpiPacket.getResFcEofErrAvgRate),
    Cmnd(b"RES:FCEOFERR:COUNT?", ScpiPacket.getResFcEofErrCount),
    Cmnd(b"RES:FCEOFERR:CURRATE?", ScpiPacket.getResFcEofErrCurRate),
    Cmnd(b"RES:FCEOFERR:ES?", ScpiPacket.getResFcEofErrES),
    Cmnd(b"RES:FCRRDYPEND?", ScpiPacket.getFcRrdyPend),
    Cmnd(b"RES:FCRXRRDY?", ScpiPacket.getFcRxRrdy),
    Cmnd(b"RES:FCS:AVGRATE?", ScpiPacket.getResFcsAvgRate),
    Cmnd(b"RES:FCS:COUNT?", ScpiPacket.getResFcsCount),
    Cmnd(b"RES:FCS:CURRATE?", ScpiPacket.getResFcsCurRate),
    Cmnd(b"RES:FCS:ES?", ScpiPacket.getResFcsES),
    Cmnd(b"RES:FCTXRRDY?", ScpiPacket.getFcTxRrdy),
    Cmnd(b"RES:HDRMM:SECS?", ScpiPacket.getResHdrMMSecs),
    Cmnd(b"RES:HDRMM:STATE?", ScpiPacket.getResHdrMMState),
    Cmnd(b"RES:HIBER:SECS?", ScpiPacket.getHiBerSecs),
    Cmnd(b"RES:INVSUPER:AVGRATE?", ScpiPacket.getResInvSuperAvgRate),
    Cmnd(b"RES:INVSUPER:COUNT?", ScpiPacket.getResInvSuperCount),
    Cmnd(b"RES:INVSUPER:CURRATE?", ScpiPacket.getResInvSuperCurRate),
    Cmnd(b"RES:INVSUPER:ES?", ScpiPacket.getResInvSuperES),
    Cmnd(b"RES:IPCHECKSUM:AVGRATE?", ScpiPacket.getResIpChecksumAvgRate),
    Cmnd(b"RES:IPCHECKSUM:COUNT?", ScpiPacket.getResIpChecksumCount),
    Cmnd(b"RES:IPCHECKSUM:CURRATE?", ScpiPacket.getResIpChecksumCurRate),
    Cmnd(b"RES:IPCHECKSUM:ES?", ScpiPacket.getResIpChecksumES),
    Cmnd(b"RES:JABBER:SECS?", ScpiPacket.getJabberSecs),
    Cmnd(b"RES:JUMBO?", ScpiPacket.getResRxJumboPackets),
    Cmnd(b"RES:LF:SECS?", ScpiPacket.getLfSecs),
    Cmnd(b"RES:LFD:SECS?", ScpiPacket.getResLfdSecs),
    Cmnd(b"RES:LFD:STATE?", ScpiPacket.getResLfdState),
    Cmnd(b"RES:LINECODE:AVGRATE?", ScpiPacket.getResLinecodeAvgRate),
    Cmnd(b"RES:LINECODE:COUNT?", ScpiPacket.getResLinecodeCount),
    Cmnd(b"RES:LINECODE:CURRATE?", ScpiPacket.getResLinecodeCurRate),
    Cmnd(b"RES:LINECODE:ES?", ScpiPacket.getResLinecodeES),
    Cmnd(b"RES:LINK:SECS?", ScpiPacket.getResLinkSecs),
    Cmnd(b"RES:LINK:STATE?", ScpiPacket.getResLinkState),
    Cmnd(b"RES:LINK:STATUS?", ScpiPacket.getResLinkStatus),
    Cmnd(b"RES:LOCCS:SECS?", ScpiPacket.getResLoccsSecs),
    Cmnd(b"RES:LOCCS:STATE?", ScpiPacket.getResLoccsState),
    Cmnd(b"RES:LOCS:SECS?", ScpiPacket.getResLocSecs),
    Cmnd(b"RES:LOCS:STATE?", ScpiPacket.getResLocState),
    Cmnd(b"RES:LOS:SECS?", ScpiPacket.getResLosSecs),
    Cmnd(b"RES:LOS:STATE?", ScpiPacket.getResLosState),
    Cmnd(b"RES:LOSS:SECS?", ScpiPacket.getResCpPowerLossSecs),
    Cmnd(b"RES:LOSS:STATE?", ScpiPacket.getResCpPowerLossState),
    Cmnd(b"RES:MOSSALRMS?", ScpiPacket.getTxIdle),
    Cmnd(b"RES:MOSSERRS?", ScpiPacket.getTxIdle),
    Cmnd(b"RES:MPLS:PACKETS?", ScpiPacket.getResMplsPacketsByLevel),
    Cmnd(b"RES:MPLS:TC?", ScpiPacket.getResMplsTC),
    Cmnd(b"RES:OVERSIZED:AVGRATE?", ScpiPacket.getResOversizedAvgRate),
    Cmnd(b"RES:OVERSIZED:COUNT?", ScpiPacket.getResOversizedCount),
    Cmnd(b"RES:OVERSIZED:CURRATE?", ScpiPacket.getResOversizedCurRate),
    Cmnd(b"RES:OVERSIZED:ES?", ScpiPacket.getResOversizedES),
    Cmnd(b"RES:PACK:BGP?", ScpiPacket.getResBgpPackets),
    Cmnd(b"RES:PACK:ICMP?", ScpiPacket.getResIcmpPackets),
    Cmnd(b"RES:PACK:IGMP?", ScpiPacket.getResIgmpPackets),
    Cmnd(b"RES:PACK:IP?", ScpiPacket.getResIpPackets),
    Cmnd(b"RES:PACK:IPV6?", ScpiPacket.getResIpv6Packets),
    Cmnd(b"RES:PACK:MPLS?", ScpiPacket.getResMplsPackets),
    Cmnd(b"RES:PACK:OSPF?", ScpiPacket.getResOspfPackets),
    Cmnd(b"RES:PACK:TCP?", ScpiPacket.getResTcpPackets),
    Cmnd(b"RES:PACK:UDP?", ScpiPacket.getResUdpPackets),
    Cmnd(b"RES:PAUSE:ENDPACKETS?", ScpiPacket.getResPauseEndPackets),
    Cmnd(b"RES:PAUSE:PACKETS?", ScpiPacket.getResPausePackets),
    Cmnd(b"RES:PAUSE:QUANTAS?", ScpiPacket.getResPauseQuantas),
    Cmnd(b"RES:PAUSE:SECS?", ScpiPacket.getResPauseSecs),
    Cmnd(b"RES:PAUSE:STATE?", ScpiPacket.getResPauseState),
    Cmnd(b"RES:PAUSE:TXENDPACKETS?", ScpiPacket.getResTxPauseEndPackets),
    Cmnd(b"RES:PAUSE:TXPACKETS?", ScpiPacket.getResTxPausePackets),
    Cmnd(b"RES:PAUSE:TXQUANTAS?", ScpiPacket.getResTxPauseQuantas),
    Cmnd(b"RES:PAUSED:ENDPACKETS?", ScpiPacket.getResPauseEndPackets),
    Cmnd(b"RES:PAUSED:PACKETS?", ScpiPacket.getResPausePackets),
    Cmnd(b"RES:PAUSED:QUANTAS?", ScpiPacket.getResPauseQuantas),
    Cmnd(b"RES:PAUSED:SECS?", ScpiPacket.getResPauseSecs),
    Cmnd(b"RES:PAUSED:STATE?", ScpiPacket.getResPauseState),
    Cmnd(b"RES:PAUSED:TXENDPACKETS?", ScpiPacket.getResTxPauseEndPackets),
    Cmnd(b"RES:PAUSED:TXPACKETS?", ScpiPacket.getResTxPausePackets),
    Cmnd(b"RES:PAUSED:TXQUANTAS?", ScpiPacket.getResTxPauseQuantas),
    Cmnd(b"RES:PFCS:AVGRATE?", ScpiPacket.getResPfcsAvgRate),
    Cmnd(b"RES:PFCS:COUNT?", ScpiPacket.getResPfcsCount),
    Cmnd(b"RES:PFCS:CURRATE?", ScpiPacket.getResPfcsCurRate),
    Cmnd(b"RES:PFCS:ES?", ScpiPacket.getResPfcsES),
    Cmnd(b"RES:PORTLOGIN?", ScpiPacket.getPortLoginStatus),
    Cmnd(b"RES:RF:SECS?", ScpiPacket.getRfSecs),
    Cmnd(b"RES:RUNT:AVGRATE?", ScpiPacket.getResRuntAvgRate),
    Cmnd(b"RES:RUNT:COUNT?", ScpiPacket.getResRuntCount),
    Cmnd(b"RES:RUNT:CURRATE?", ScpiPacket.getResRuntCurRate),
    Cmnd(b"RES:RUNT:ES?", ScpiPacket.getResRuntES),
    Cmnd(b"RES:RX1024?", ScpiPacket.getRx1024bp),
    Cmnd(b"RES:RX128?", ScpiPacket.getRx128bp),
    Cmnd(b"RES:RX1519?", ScpiPacket.getRx1519bp),
    Cmnd(b"RES:RX256?", ScpiPacket.getRx256bp),
    Cmnd(b"RES:RX512?", ScpiPacket.getRx512bp),
    Cmnd(b"RES:RX64?", ScpiPacket.getRx64bp),
    Cmnd(b"RES:RX65?", ScpiPacket.getRx65bp),
    Cmnd(b"RES:RXBCAST?", ScpiPacket.getRxbCast),
    Cmnd(b"RES:RXBYT?", ScpiPacket.getResRxBytes),
    Cmnd(b"RES:RXIDLE?", ScpiPacket.getRxIdle),
    Cmnd(b"RES:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecNone),
    Cmnd(b"RES:RXMCAST?", ScpiPacket.getRxmCast),
    Cmnd(b"RES:RXPACK:BGP?", ScpiPacket.getResBgpPackets),
    Cmnd(b"RES:RXPACK:BROAD?", ScpiPacket.getRxbCast),
    Cmnd(b"RES:RXPACK:BYT?", ScpiPacket.getResRxBytes),
    Cmnd(b"RES:RXPACK:ICMP?", ScpiPacket.getResIcmpPackets),
    Cmnd(b"RES:RXPACK:IDLE?", ScpiPacket.getRxIdle),
    Cmnd(b"RES:RXPACK:IGMP?", ScpiPacket.getResIgmpPackets),
    Cmnd(b"RES:RXPACK:IPV4?", ScpiPacket.getResIpPackets),
    Cmnd(b"RES:RXPACK:IPV6?", ScpiPacket.getResIpv6Packets),
    Cmnd(b"RES:RXPACK:JUMBO?", ScpiPacket.getResRxJumboPackets),
    Cmnd(b"RES:RXPACK:L2BYT?", ScpiPacket.getResRxBytes),
    Cmnd(b"RES:RXPACK:MPLS:TAG?", ScpiPacket.getResMplsPacketsByLevel),
    Cmnd(b"RES:RXPACK:MPLS:TC?", ScpiPacket.getResMplsTC),
    Cmnd(b"RES:RXPACK:MPLS?", ScpiPacket.getResMplsPackets),
    Cmnd(b"RES:RXPACK:MULTI?", ScpiPacket.getRxmCast),
    Cmnd(b"RES:RXPACK:OSPF?", ScpiPacket.getResOspfPackets),
    Cmnd(b"RES:RXPACK:PAUSE:ENDPACKETS?", ScpiPacket.getResPauseEndPackets),
    Cmnd(b"RES:RXPACK:PAUSE:PACKETS?", ScpiPacket.getResPausePackets),
    Cmnd(b"RES:RXPACK:PAUSE:QUANT?", ScpiPacket.getResPauseQuantas),
    Cmnd(b"RES:RXPACK:SIZE:1024?", ScpiPacket.getRx1024bp),
    Cmnd(b"RES:RXPACK:SIZE:128?", ScpiPacket.getRx128bp),
    Cmnd(b"RES:RXPACK:SIZE:1519?", ScpiPacket.getRx1519bp),
    Cmnd(b"RES:RXPACK:SIZE:256?", ScpiPacket.getRx256bp),
    Cmnd(b"RES:RXPACK:SIZE:512?", ScpiPacket.getRx512bp),
    Cmnd(b"RES:RXPACK:SIZE:64?", ScpiPacket.getRx64bp),
    Cmnd(b"RES:RXPACK:SIZE:65?", ScpiPacket.getRx65bp),
    Cmnd(b"RES:RXPACK:SUPERBLOCK?", ScpiPacket.getRxSuperBlock),
    Cmnd(b"RES:RXPACK:SUPERJUMBO?", ScpiPacket.getResOversizedCount),
    Cmnd(b"RES:RXPACK:TCP?", ScpiPacket.getResTcpPackets),
    Cmnd(b"RES:RXPACK:UDP?", ScpiPacket.getResUdpPackets),
    Cmnd(b"RES:RXPACK:UNI?", ScpiPacket.getRxuCast),
    Cmnd(b"RES:RXPACK:VLAN:QOS?", ScpiPacket.getResVlanPacketsQos),
    Cmnd(b"RES:RXPACK:VLAN:TAG?", ScpiPacket.getResVlanPackets),
    Cmnd(b"RES:RXPACK:VLAN?", ScpiPacket.getResVlanPackets1),
    Cmnd(b"RES:RXPACK?", ScpiPacket.getResRxPackets),
    Cmnd(b"RES:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthNone),
    Cmnd(b"RES:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecNone),
    Cmnd(b"RES:RXSUPERBLOCK?", ScpiPacket.getRxSuperBlock),
    Cmnd(b"RES:RXUCAST?", ScpiPacket.getRxuCast),
    Cmnd(b"RES:SCANALARMS?", ScpiPacket.getCurrentAlarms),
    Cmnd(b"RES:SCANERRORS?", ScpiPacket.getCurrentErrors),
    Cmnd(b"RES:SFCS:AVGRATE?", ScpiPacket.getResSfcsAvgRate),
    Cmnd(b"RES:SFCS:COUNT?", ScpiPacket.getResSfcsCount),
    Cmnd(b"RES:SFCS:CURRATE?", ScpiPacket.getResSfcsCurRate),
    Cmnd(b"RES:SFCS:ES?", ScpiPacket.getResSfcsES),
    Cmnd(b"RES:SPM?", ScpiPacket.getResSPM),
    Cmnd(b"RES:STSD?", ScpiPacket.getResSTSD),
    Cmnd(b"RES:SUPJUMBO?", ScpiPacket.getResOversizedCount),
    Cmnd(b"RES:SYNCHDR:AVGRATE?", ScpiPacket.getResSyncHdrAvgRate),
    Cmnd(b"RES:SYNCHDR:COUNT?", ScpiPacket.getResSyncHdrCount),
    Cmnd(b"RES:SYNCHDR:CURRATE?", ScpiPacket.getResSyncHdrCurRate),
    Cmnd(b"RES:SYNCHDR:ES?", ScpiPacket.getResSyncHdrES),
    Cmnd(b"RES:TCPERR:AVGRATE?", ScpiPacket.getResTcpChecksumAvgRate),
    Cmnd(b"RES:TCPERR:COUNT?", ScpiPacket.getResTcpChecksumCount),
    Cmnd(b"RES:TCPERR:CURRATE?", ScpiPacket.getResTcpChecksumCurRate),
    Cmnd(b"RES:TCPERR:ES?", ScpiPacket.getResTcpChecksumES),
    Cmnd(b"RES:THEC:AVGRATE?", ScpiPacket.getResCorrTHecAvgRate),
    Cmnd(b"RES:THEC:COUNT?", ScpiPacket.getResCorrTHecCount),
    Cmnd(b"RES:THEC:CURRATE?", ScpiPacket.getResCorrTHecCurRate),
    Cmnd(b"RES:THEC:ES?", ScpiPacket.getResCorrTHecES),
    Cmnd(b"RES:TXBYT?", ScpiPacket.getResTxBytes),
    Cmnd(b"RES:TXIDLE?", ScpiPacket.getTxIdle),
    Cmnd(b"RES:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecNone),
    Cmnd(b"RES:TXPACK:BYT?", ScpiPacket.getResTxBytes),
    Cmnd(b"RES:TXPACK:IDLE?", ScpiPacket.getTxIdle),
    Cmnd(b"RES:TXPACK:IP?", ScpiPacket.getResTxIpPackets),
    Cmnd(b"RES:TXPACK:IPV4?", ScpiPacket.getResTxIpPackets),
    Cmnd(b"RES:TXPACK:IPV6?", ScpiPacket.getResTxIpv6Packets),
    Cmnd(b"RES:TXPACK:L2BYT?", ScpiPacket.getResTxBytes),
    Cmnd(b"RES:TXPACK:MPLS?", ScpiPacket.getResTxMplsPackets),
    Cmnd(b"RES:TXPACK:PAUSE:ENDPACKETS?", ScpiPacket.getResTxPauseEndPackets),
    Cmnd(b"RES:TXPACK:PAUSE:PACKETS?", ScpiPacket.getResTxPausePackets),
    Cmnd(b"RES:TXPACK:PAUSE:QUANT?", ScpiPacket.getResTxPauseQuantas),
    Cmnd(b"RES:TXPACK:SUPERBLOCK?", ScpiPacket.getTxSuperBlock),
    Cmnd(b"RES:TXPACK:VLAN?", ScpiPacket.getResTxVlanPackets),
    Cmnd(b"RES:TXPACK?", ScpiPacket.getResTxPackets),
    Cmnd(b"RES:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthNone),
    Cmnd(b"RES:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecNone),
    Cmnd(b"RES:TXSUPERBLOCK?", ScpiPacket.getTxSuperBlock),
    Cmnd(b"RES:UCHEC:AVGRATE?", ScpiPacket.getResUnCorrCHecAvgRate),
    Cmnd(b"RES:UCHEC:COUNT?", ScpiPacket.getResUnCorrCHecCount),
    Cmnd(b"RES:UCHEC:CURRATE?", ScpiPacket.getResUnCorrCHecCurRate),
    Cmnd(b"RES:UCHEC:ES?", ScpiPacket.getResUnCorrCHecES),
    Cmnd(b"RES:UDPERR:AVGRATE?", ScpiPacket.getResUdpChecksumAvgRate),
    Cmnd(b"RES:UDPERR:COUNT?", ScpiPacket.getResUdpChecksumCount),
    Cmnd(b"RES:UDPERR:CURRATE?", ScpiPacket.getResUdpChecksumCurRate),
    Cmnd(b"RES:UDPERR:ES?", ScpiPacket.getResUdpChecksumES),
    Cmnd(b"RES:UEHEC:AVGRATE?", ScpiPacket.getResUnCorrEHecAvgRate),
    Cmnd(b"RES:UEHEC:COUNT?", ScpiPacket.getResUnCorrEHecCount),
    Cmnd(b"RES:UEHEC:CURRATE?", ScpiPacket.getResUnCorrEHecCurRate),
    Cmnd(b"RES:UEHEC:ES?", ScpiPacket.getResUnCorrEHecES),
    Cmnd(b"RES:UNDERSIZED:AVGRATE?", ScpiPacket.getResUndersizedAvgRate),
    Cmnd(b"RES:UNDERSIZED:COUNT?", ScpiPacket.getResUndersizedCount),
    Cmnd(b"RES:UNDERSIZED:CURRATE?", ScpiPacket.getResUndersizedCurRate),
    Cmnd(b"RES:UNDERSIZED:ES?", ScpiPacket.getResUndersizedES),
    Cmnd(b"RES:UTHEC:AVGRATE?", ScpiPacket.getResUnCorrTHecAvgRate),
    Cmnd(b"RES:UTHEC:COUNT?", ScpiPacket.getResUnCorrTHecCount),
    Cmnd(b"RES:UTHEC:CURRATE?", ScpiPacket.getResUnCorrTHecCurRate),
    Cmnd(b"RES:UTHEC:ES?", ScpiPacket.getResUnCorrTHecES),
    Cmnd(b"RES:UTIL:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgNone),
    Cmnd(b"RES:UTIL:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgNone),
    Cmnd(b"RES:UTIL:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgNone),
    Cmnd(b"RES:UTIL:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgNone),
    Cmnd(b"RES:UTIL:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgNone),
    Cmnd(b"RES:UTIL:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgNone),
    Cmnd(b"RES:UTIL:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecNone),
    Cmnd(b"RES:UTIL:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthNone),
    Cmnd(b"RES:UTIL:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecNone),
    Cmnd(b"RES:UTIL:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecNone),
    Cmnd(b"RES:UTIL:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthNone),
    Cmnd(b"RES:UTIL:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecNone),
    Cmnd(b"RES:UTIL:IPV4:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgIpv4),
    Cmnd(b"RES:UTIL:IPV4:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgIpv4),
    Cmnd(b"RES:UTIL:IPV4:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgIpv4),
    Cmnd(b"RES:UTIL:IPV4:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgIpv4),
    Cmnd(b"RES:UTIL:IPV4:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgIpv4),
    Cmnd(b"RES:UTIL:IPV4:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgIpv4),
    Cmnd(b"RES:UTIL:IPV4:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecIpv4),
    Cmnd(b"RES:UTIL:IPV4:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthIpv4),
    Cmnd(b"RES:UTIL:IPV4:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecIpv4),
    Cmnd(b"RES:UTIL:IPV4:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecIpv4),
    Cmnd(b"RES:UTIL:IPV4:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthIpv4),
    Cmnd(b"RES:UTIL:IPV4:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecIpv4),
    Cmnd(b"RES:UTIL:IPV4:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxIpv4),
    Cmnd(b"RES:UTIL:IPV4:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxIpv4),
    Cmnd(b"RES:UTIL:IPV4:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxIpv4),
    Cmnd(b"RES:UTIL:IPV4:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxIpv4),
    Cmnd(b"RES:UTIL:IPV4:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxIpv4),
    Cmnd(b"RES:UTIL:IPV4:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxIpv4),
    Cmnd(b"RES:UTIL:IPV4:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinIpv4),
    Cmnd(b"RES:UTIL:IPV4:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinIpv4),
    Cmnd(b"RES:UTIL:IPV4:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinIpv4),
    Cmnd(b"RES:UTIL:IPV4:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinIpv4),
    Cmnd(b"RES:UTIL:IPV4:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinIpv4),
    Cmnd(b"RES:UTIL:IPV4:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinIpv4),
    Cmnd(b"RES:UTIL:IPV6:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgIpv6),
    Cmnd(b"RES:UTIL:IPV6:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgIpv6),
    Cmnd(b"RES:UTIL:IPV6:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgIpv6),
    Cmnd(b"RES:UTIL:IPV6:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgIpv6),
    Cmnd(b"RES:UTIL:IPV6:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgIpv6),
    Cmnd(b"RES:UTIL:IPV6:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgIpv6),
    Cmnd(b"RES:UTIL:IPV6:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecIpv6),
    Cmnd(b"RES:UTIL:IPV6:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthIpv6),
    Cmnd(b"RES:UTIL:IPV6:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecIpv6),
    Cmnd(b"RES:UTIL:IPV6:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecIpv6),
    Cmnd(b"RES:UTIL:IPV6:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthIpv6),
    Cmnd(b"RES:UTIL:IPV6:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecIpv6),
    Cmnd(b"RES:UTIL:IPV6:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxIpv6),
    Cmnd(b"RES:UTIL:IPV6:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxIpv6),
    Cmnd(b"RES:UTIL:IPV6:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxIpv6),
    Cmnd(b"RES:UTIL:IPV6:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxIpv6),
    Cmnd(b"RES:UTIL:IPV6:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxIpv6),
    Cmnd(b"RES:UTIL:IPV6:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxIpv6),
    Cmnd(b"RES:UTIL:IPV6:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinIpv6),
    Cmnd(b"RES:UTIL:IPV6:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinIpv6),
    Cmnd(b"RES:UTIL:IPV6:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinIpv6),
    Cmnd(b"RES:UTIL:IPV6:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinIpv6),
    Cmnd(b"RES:UTIL:IPV6:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinIpv6),
    Cmnd(b"RES:UTIL:IPV6:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinIpv6),
    Cmnd(b"RES:UTIL:L1:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgNone),
    Cmnd(b"RES:UTIL:L1:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgNone),
    Cmnd(b"RES:UTIL:L1:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgNone),
    Cmnd(b"RES:UTIL:L1:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgNone),
    Cmnd(b"RES:UTIL:L1:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgNone),
    Cmnd(b"RES:UTIL:L1:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgNone),
    Cmnd(b"RES:UTIL:L1:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecNone),
    Cmnd(b"RES:UTIL:L1:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthNone),
    Cmnd(b"RES:UTIL:L1:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecNone),
    Cmnd(b"RES:UTIL:L1:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecNone),
    Cmnd(b"RES:UTIL:L1:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthNone),
    Cmnd(b"RES:UTIL:L1:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecNone),
    Cmnd(b"RES:UTIL:L1:IPV4:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinIpv4),
    Cmnd(b"RES:UTIL:L1:IPV4:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinIpv4),
    Cmnd(b"RES:UTIL:L1:IPV6:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinIpv6),
    Cmnd(b"RES:UTIL:L1:IPV6:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinIpv6),
    Cmnd(b"RES:UTIL:L1:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxNone),
    Cmnd(b"RES:UTIL:L1:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxNone),
    Cmnd(b"RES:UTIL:L1:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxNone),
    Cmnd(b"RES:UTIL:L1:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxNone),
    Cmnd(b"RES:UTIL:L1:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxNone),
    Cmnd(b"RES:UTIL:L1:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxNone),
    Cmnd(b"RES:UTIL:L1:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinNone),
    Cmnd(b"RES:UTIL:L1:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinNone),
    Cmnd(b"RES:UTIL:L1:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinNone),
    Cmnd(b"RES:UTIL:L1:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinNone),
    Cmnd(b"RES:UTIL:L1:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinNone),
    Cmnd(b"RES:UTIL:L1:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinNone),
    Cmnd(b"RES:UTIL:L1:MPLS:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinMpls),
    Cmnd(b"RES:UTIL:L1:MPLS:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinMpls),
    Cmnd(b"RES:UTIL:L1:VLAN:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinVlan),
    Cmnd(b"RES:UTIL:L1:VLAN:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinVlan),
    Cmnd(b"RES:UTIL:L2:AVG:RXMBPS?", ScpiPacket.getResL2RxLinkKBPerSecAvgNone),
    Cmnd(b"RES:UTIL:L2:AVG:RXPCTBW?", ScpiPacket.getResL2RxLinkPctBandwidthAvgNone),
    Cmnd(b"RES:UTIL:L2:AVG:TXMBPS?", ScpiPacket.getResL2TxLinkKBPerSecAvgNone),
    Cmnd(b"RES:UTIL:L2:AVG:TXPCTBW?", ScpiPacket.getResL2TxLinkPctBandwidthAvgNone),
    Cmnd(b"RES:UTIL:L2:CUR:RXMBPS?", ScpiPacket.getResL2RxLinkKBPerSecNone),
    Cmnd(b"RES:UTIL:L2:CUR:RXPCTBW?", ScpiPacket.getResL2RxLinkPctBandwidthNone),
    Cmnd(b"RES:UTIL:L2:CUR:TXMBPS?", ScpiPacket.getResL2TxLinkKBPerSecNone),
    Cmnd(b"RES:UTIL:L2:CUR:TXPCTBW?", ScpiPacket.getResL2TxLinkPctBandwidthNone),
    Cmnd(b"RES:UTIL:L2:MAX:RXMBPS?", ScpiPacket.getResL2RxLinkKBPerSecMaxNone),
    Cmnd(b"RES:UTIL:L2:MAX:RXPCTBW?", ScpiPacket.getResL2RxLinkPctBandwidthMaxNone),
    Cmnd(b"RES:UTIL:L2:MAX:TXMBPS?", ScpiPacket.getResL2TxLinkKBPerSecMaxNone),
    Cmnd(b"RES:UTIL:L2:MAX:TXPCTBW?", ScpiPacket.getResL2TxLinkPctBandwidthMaxNone),
    Cmnd(b"RES:UTIL:L2:MIN:RXMBPS?", ScpiPacket.getResL2RxLinkKBPerSecMinNone),
    Cmnd(b"RES:UTIL:L2:MIN:RXPCTBW?", ScpiPacket.getResL2RxLinkPctBandwidthMinNone),
    Cmnd(b"RES:UTIL:L2:MIN:TXMBPS?", ScpiPacket.getResL2TxLinkKBPerSecMinNone),
    Cmnd(b"RES:UTIL:L2:MIN:TXPCTBW?", ScpiPacket.getResL2TxLinkPctBandwidthMinNone),
    Cmnd(b"RES:UTIL:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxNone),
    Cmnd(b"RES:UTIL:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxNone),
    Cmnd(b"RES:UTIL:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxNone),
    Cmnd(b"RES:UTIL:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxNone),
    Cmnd(b"RES:UTIL:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxNone),
    Cmnd(b"RES:UTIL:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxNone),
    Cmnd(b"RES:UTIL:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinNone),
    Cmnd(b"RES:UTIL:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinNone),
    Cmnd(b"RES:UTIL:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinNone),
    Cmnd(b"RES:UTIL:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinNone),
    Cmnd(b"RES:UTIL:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinNone),
    Cmnd(b"RES:UTIL:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinNone),
    Cmnd(b"RES:UTIL:MPLS:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgMpls),
    Cmnd(b"RES:UTIL:MPLS:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgMpls),
    Cmnd(b"RES:UTIL:MPLS:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgMpls),
    Cmnd(b"RES:UTIL:MPLS:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgMpls),
    Cmnd(b"RES:UTIL:MPLS:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgMpls),
    Cmnd(b"RES:UTIL:MPLS:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgMpls),
    Cmnd(b"RES:UTIL:MPLS:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMpls),
    Cmnd(b"RES:UTIL:MPLS:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMpls),
    Cmnd(b"RES:UTIL:MPLS:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMpls),
    Cmnd(b"RES:UTIL:MPLS:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMpls),
    Cmnd(b"RES:UTIL:MPLS:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMpls),
    Cmnd(b"RES:UTIL:MPLS:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMpls),
    Cmnd(b"RES:UTIL:MPLS:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxMpls),
    Cmnd(b"RES:UTIL:MPLS:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxMpls),
    Cmnd(b"RES:UTIL:MPLS:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxMpls),
    Cmnd(b"RES:UTIL:MPLS:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxMpls),
    Cmnd(b"RES:UTIL:MPLS:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxMpls),
    Cmnd(b"RES:UTIL:MPLS:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxMpls),
    Cmnd(b"RES:UTIL:MPLS:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinMpls),
    Cmnd(b"RES:UTIL:MPLS:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinMpls),
    Cmnd(b"RES:UTIL:MPLS:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinMpls),
    Cmnd(b"RES:UTIL:MPLS:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinMpls),
    Cmnd(b"RES:UTIL:MPLS:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinMpls),
    Cmnd(b"RES:UTIL:MPLS:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinMpls),
    Cmnd(b"RES:UTIL:VLAN:AVG:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecAvgVlan),
    Cmnd(b"RES:UTIL:VLAN:AVG:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthAvgVlan),
    Cmnd(b"RES:UTIL:VLAN:AVG:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecAvgVlan),
    Cmnd(b"RES:UTIL:VLAN:AVG:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecAvgVlan),
    Cmnd(b"RES:UTIL:VLAN:AVG:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthAvgVlan),
    Cmnd(b"RES:UTIL:VLAN:AVG:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecAvgVlan),
    Cmnd(b"RES:UTIL:VLAN:CUR:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecVlan),
    Cmnd(b"RES:UTIL:VLAN:CUR:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthVlan),
    Cmnd(b"RES:UTIL:VLAN:CUR:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecVlan),
    Cmnd(b"RES:UTIL:VLAN:CUR:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecVlan),
    Cmnd(b"RES:UTIL:VLAN:CUR:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthVlan),
    Cmnd(b"RES:UTIL:VLAN:CUR:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecVlan),
    Cmnd(b"RES:UTIL:VLAN:MAX:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMaxVlan),
    Cmnd(b"RES:UTIL:VLAN:MAX:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMaxVlan),
    Cmnd(b"RES:UTIL:VLAN:MAX:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMaxVlan),
    Cmnd(b"RES:UTIL:VLAN:MAX:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMaxVlan),
    Cmnd(b"RES:UTIL:VLAN:MAX:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMaxVlan),
    Cmnd(b"RES:UTIL:VLAN:MAX:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMaxVlan),
    Cmnd(b"RES:UTIL:VLAN:MIN:RXMBPS?", ScpiPacket.getResRxLinkKBPerSecMinVlan),
    Cmnd(b"RES:UTIL:VLAN:MIN:RXPCTBW?", ScpiPacket.getResRxLinkPctBandwidthMinVlan),
    Cmnd(b"RES:UTIL:VLAN:MIN:RXPPS?", ScpiPacket.getResRxLinkPacketPerSecMinVlan),
    Cmnd(b"RES:UTIL:VLAN:MIN:TXMBPS?", ScpiPacket.getResTxLinkKBPerSecMinVlan),
    Cmnd(b"RES:UTIL:VLAN:MIN:TXPCTBW?", ScpiPacket.getResTxLinkPctBandwidthMinVlan),
    Cmnd(b"RES:UTIL:VLAN:MIN:TXPPS?", ScpiPacket.getResTxLinkPacketPerSecMinVlan),
    Cmnd(b"RES:VLAN:PACKETS1?", ScpiPacket.getResVlanPackets1),
    Cmnd(b"RES:VLAN:PACKETS2?", ScpiPacket.getResVlanPackets2),
    Cmnd(b"RES:VLAN:PACKETS3?", ScpiPacket.getResVlanPackets3),
    Cmnd(b"RES:VLAN:PACKETS4?", ScpiPacket.getResVlanPackets4),
    Cmnd(b"RES:VLAN:PACKETS?", ScpiPacket.getResVlanPackets),
    Cmnd(b"RES:VLAN:QOS1?", ScpiPacket.getResVlanPacketsQos1),
    Cmnd(b"RES:VLAN:QOS2?", ScpiPacket.getResVlanPacketsQos2),
    Cmnd(b"RES:VLAN:QOS3?", ScpiPacket.getResVlanPacketsQos3),
    Cmnd(b"RES:VLAN:QOS4?", ScpiPacket.getResVlanPacketsQos4),
    Cmnd(b"RES:VLAN:QOS?", ScpiPacket.getResVlanPacketsQos),
    Cmnd(b"RFC:B2B:ACT", ScpiPacket.rfcSetActivate),
    Cmnd(b"RFC:B2B:ACT?", ScpiPacket.rfcGetActivate),
    Cmnd(b"RFC:B2B:AVGOBS?", ScpiPacket.rfcGetAvgObServed),
    Cmnd(b"RFC:B2B:MAXPOS?", ScpiPacket.rfcGetMaxPossible),
    Cmnd(b"RFC:B2B:REP", ScpiPacket.rfcSetRepititions),
    Cmnd(b"RFC:B2B:REP?", ScpiPacket.rfcGetRepititions),
    Cmnd(b"RFC:B2B:RES", ScpiPacket.rfcSetResolution),
    Cmnd(b"RFC:B2B:RES?", ScpiPacket.rfcGetResolution),
    Cmnd(b"RFC:BW:CEILING", ScpiPacket.rfcSetBwCeiling),
    Cmnd(b"RFC:BW:CEILING?", ScpiPacket.rfcGetBwCeiling),
    Cmnd(b"RFC:BW:FLOOR", ScpiPacket.rfcSetBwFloor),
    Cmnd(b"RFC:BW:FLOOR?", ScpiPacket.rfcGetBwFloor),
    Cmnd(b"RFC:FRAME:ACT", ScpiPacket.rfcSetFrameActivate),
    Cmnd(b"RFC:FRAME:ACT?", ScpiPacket.rfcGetFrameActivate),
    Cmnd(b"RFC:FRAME:LOSS?", ScpiPacket.rfcGetFrameLoss),
    Cmnd(b"RFC:FRAME:RATE?", ScpiPacket.rfcGetFrameRate),
    Cmnd(b"RFC:FRAME:RX?", ScpiPacket.rfcGetFrameRx),
    Cmnd(b"RFC:FRAME:TX?", ScpiPacket.rfcGetFrameTx),
    Cmnd(b"RFC:STATE?", ScpiPacket.rfcGetState),
    Cmnd(b"RFC:TEST:DEFAULT", ScpiPacket.rfcSetFactoryDeflt),
    Cmnd(b"RFC:TEST:DEST", ScpiPacket.rfcSetDestination),
    Cmnd(b"RFC:TEST:DEST?", ScpiPacket.rfcGetDestination),
    Cmnd(b"RFC:TEST:DUR", ScpiPacket.rfcSetTestDuration),
    Cmnd(b"RFC:TEST:DUR?", ScpiPacket.rfcGetTestDuration),
    Cmnd(b"RFC:TEST:MODE", ScpiPacket.rfcSetTestMode),
    Cmnd(b"RFC:TEST:MODE?", ScpiPacket.rfcGetTestMode),
    Cmnd(b"RFC:TEST:SIZE", ScpiPacket.rfcSetTestSize),
    Cmnd(b"RFC:TEST:SIZE?", ScpiPacket.rfcGetTestSize),
    Cmnd(b"RFC:TEST:STREAM", ScpiPacket.rfcSetStream),
    Cmnd(b"RFC:TEST:STREAM?", ScpiPacket.rfcGetStream),
    Cmnd(b"RFC:THRU:ACT", ScpiPacket.rfcSetThruActivate),
    Cmnd(b"RFC:THRU:ACT?", ScpiPacket.rfcGetThruActivate),
    Cmnd(b"RFC:THRU:AVG?", ScpiPacket.rfcGetThruAvg),
    Cmnd(b"RFC:THRU:LAT", ScpiPacket.rfcSetLatencyIterations),
    Cmnd(b"RFC:THRU:LAT?", ScpiPacket.rfcGetLatencyIterations),
    Cmnd(b"RFC:THRU:LOSS", ScpiPacket.rfcSetThruLoss),
    Cmnd(b"RFC:THRU:LOSS?", ScpiPacket.rfcGetThruLoss),
    Cmnd(b"RFC:THRU:MAX?", ScpiPacket.rfcGetThruMax),
    Cmnd(b"RFC:THRU:MIN?", ScpiPacket.rfcGetThruMin),
    Cmnd(b"RFC:THRU:PASS?", ScpiPacket.rfcGetThruPass),
    Cmnd(b"RFC:THRU:RES", ScpiPacket.rfcSetThruRes),
    Cmnd(b"RFC:THRU:RES?", ScpiPacket.rfcGetThruRes),
    Cmnd(b"RFC:THRU:RX?", ScpiPacket.rfcGetThruRx),
    Cmnd(b"RFC:THRU:TX?", ScpiPacket.rfcGetThruTx),
    Cmnd(b"RX:CAPSAVE:MICROPCAP", ScpiPacket.saveCapturePcap),
    Cmnd(b"RX:CAPSAVE:NANOPCAP", ScpiPacket.saveCaptureNanoPcap),
    Cmnd(b"RX:CAPSAVE:PCAP", ScpiPacket.saveCapturePcap),
    Cmnd(b"RX:CAPSAVE:PCAPNG", ScpiPacket.saveCapturePcapNg),
    Cmnd(b"RX:CAPSIZE", ScpiPacket.setCaptureSize),
    Cmnd(b"RX:CAPSIZE?", ScpiPacket.getCaptureSize),
    Cmnd(b"RX:CAPSTART", ScpiPacket.startCapture),
    Cmnd(b"RX:CAPSTOP", ScpiPacket.stopCapture),
    Cmnd(b"RX:CID", ScpiPacket.setRxCid),
    Cmnd(b"RX:CID?", ScpiPacket.getRxCid),
    Cmnd(b"RX:FCTOV", ScpiPacket.setRxFcTov),
    Cmnd(b"RX:FCTOV?", ScpiPacket.getRxFcTov),
    Cmnd(b"RX:OH:CID?", ScpiPacket.getCaptureCid),  # Shared GFP capture CID handler
    Cmnd(b"RX:OH:EXI?", ScpiPacket.getCaptureExi),
    Cmnd(b"RX:OH:PFI?", ScpiPacket.getCapturePfi),
    Cmnd(b"RX:OH:PLI?", ScpiPacket.getCapturePli),
    Cmnd(b"RX:OH:PTI?", ScpiPacket.getCapturePti),
    Cmnd(b"RX:OH:SELECT", ScpiPacket.setRxCidFilter),  # Shared GFP CID filter setter
    Cmnd(b"RX:OH:SELECT?", ScpiPacket.getRxCidFilter),  # Shared GFP CID filter query
    Cmnd(b"RX:OH:SPARE?", ScpiPacket.getCaptureSpare),
    Cmnd(b"RX:OH:UPI?", ScpiPacket.getCaptureUpi),
    Cmnd(b"RX:OPP?", ScpiPacket.rxGetOpticalPower),
    Cmnd(b"RX:PAT", ScpiPacket.setRxGfpPat),
    Cmnd(b"RX:PAT?", ScpiPacket.getRxGfpPat),
    Cmnd(b"RX:PAUSE", ScpiPacket.setPpPauseState),
    Cmnd(b"RX:PAUSE?", ScpiPacket.getPpPauseState),
    Cmnd(b"RX:TPID:STATE", ScpiPacket.setRxTpidState),
    Cmnd(b"RX:TPID:STATE?", ScpiPacket.getRxTpidState),
    Cmnd(b"RX:TPID:VALUE", ScpiPacket.setRxTpidValue),
    Cmnd(b"RX:TPID:VALUE?", ScpiPacket.getRxTpidValue),
    Cmnd(b"SD:ACTION", ScpiPacket.setSDAction),
    Cmnd(b"SD:ACTION?", ScpiPacket.getSDState),
    Cmnd(b"SD:AVGFRAME?", ScpiPacket.getSDAvgFrame),
    Cmnd(b"SD:AVGTIME?", ScpiPacket.getSDAvgTime),
    Cmnd(b"SD:BADFRAME", ScpiPacket.setSDBadFrame),
    Cmnd(b"SD:BADFRAME?", ScpiPacket.getSDBadFrame),
    Cmnd(b"SD:BADTIME", ScpiPacket.setSDBadTime),
    Cmnd(b"SD:BADTIME?", ScpiPacket.getSDBadTime),
    Cmnd(b"SD:CURFRAME?", ScpiPacket.getSDCurFrame),
    Cmnd(b"SD:CURTIME?", ScpiPacket.getSDCurTime),
    Cmnd(b"SD:GOODFRAME", ScpiPacket.setSDGoodFrame),
    Cmnd(b"SD:GOODFRAME?", ScpiPacket.getSDGoodFrame),
    Cmnd(b"SD:GOODTIME", ScpiPacket.setSDGoodTime),
    Cmnd(b"SD:GOODTIME?", ScpiPacket.getSDGoodTime),
    Cmnd(b"SD:MAXFRAME?", ScpiPacket.getSDMaxFrame),
    Cmnd(b"SD:MAXTIME?", ScpiPacket.getSDMaxTime),
    Cmnd(b"SD:MINFRAME?", ScpiPacket.getSDMinFrame),
    Cmnd(b"SD:MINTIME?", ScpiPacket.getSDMinTime),
    Cmnd(b"SD:RECFRAME?", ScpiPacket.getSDRecentFrame),
    Cmnd(b"SD:RECTIME?", ScpiPacket.getSDRecentTime),
    Cmnd(b"SEEDAB:ABPAT", ScpiPacket.setSeedABPat),
    Cmnd(b"SEEDAB:ABPAT?", ScpiPacket.getSeedABPat),
    Cmnd(b"SEEDAB:APAT", ScpiPacket.setSeedAPat),
    Cmnd(b"SEEDAB:APAT?", ScpiPacket.getSeedAPat),
    Cmnd(b"SEEDAB:AVGRATE?", ScpiPacket.getSeedABAvgRate),
    Cmnd(b"SEEDAB:BPAT", ScpiPacket.setSeedBPat),
    Cmnd(b"SEEDAB:BPAT?", ScpiPacket.getSeedBPat),
    Cmnd(b"SEEDAB:COUNT?", ScpiPacket.getSeedABCount),
    Cmnd(b"SEEDAB:CURRATE?", ScpiPacket.getSeedABCurRate),
    Cmnd(b"SEEDAB:ES?", ScpiPacket.getSeedABES),
    Cmnd(b"SOUR:AL:TYPE", ScpiPacket.txSetAlarmType),
    Cmnd(b"SOUR:AL:TYPE?", ScpiPacket.txGetAlarmType),
    Cmnd(b"SOUR:AUTO", ScpiPacket.txSetAutoNeg),
    Cmnd(b"SOUR:AUTO?", ScpiPacket.txGetAutoNeg),
    Cmnd(b"SOUR:BBCREDIT", ScpiPacket.setBBCredit),
    Cmnd(b"SOUR:BBCREDIT?", ScpiPacket.getBBCredit),
    Cmnd(b"SOUR:BBCREDITBYPASS", ScpiPacket.setBBCreditBypass),
    Cmnd(b"SOUR:BBCREDITBYPASS?", ScpiPacket.getBBCreditBypass),
    Cmnd(b"SOUR:CID", ScpiPacket.setGfpCid),
    Cmnd(b"SOUR:CID?", ScpiPacket.getGfpCid),
    Cmnd(b"SOUR:DEFICIT", ScpiPacket.setDeficitIdle),
    Cmnd(b"SOUR:DEFICIT?", ScpiPacket.getDeficitIdle),
    Cmnd(b"SOUR:EMIXMODE", ScpiPacket.txSetEmixMode),
    Cmnd(b"SOUR:EMIXMODE?", ScpiPacket.txGetEmixMode),
    Cmnd(b"SOUR:ERR:RATE", ScpiPacket.txSetErrRate),
    Cmnd(b"SOUR:ERR:RATE?", ScpiPacket.txGetErrRate),
    Cmnd(b"SOUR:ERR:RUNTSIZE", ScpiPacket.txSetRuntSize),
    Cmnd(b"SOUR:ERR:RUNTSIZE?", ScpiPacket.txGetRuntSize),
    Cmnd(b"SOUR:ERR:TYPE", ScpiPacket.txSetErrType),
    Cmnd(b"SOUR:ERR:TYPE?", ScpiPacket.txGetErrType),
    Cmnd(b"SOUR:EXI", ScpiPacket.setGfpExi),
    Cmnd(b"SOUR:EXI?", ScpiPacket.getGfpExi),
    Cmnd(b"SOUR:FABRICLOGIN", ScpiPacket.fabricLogin),
    Cmnd(b"SOUR:FABRICLOGIN?", ScpiPacket.getFabricLoginStatus),
    Cmnd(b"SOUR:FCPRIM", ScpiPacket.setTxFcPrim),
    Cmnd(b"SOUR:FILLWORD", ScpiPacket.setFillword),
    Cmnd(b"SOUR:FILLWORD?", ScpiPacket.getFillword),
    Cmnd(b"SOUR:FLOWCONTROL", ScpiPacket.txSetFlowControl),
    Cmnd(b"SOUR:FLOWCONTROL?", ScpiPacket.txGetFlowControl),
    Cmnd(b"SOUR:IPR", ScpiPacket.txSetIPReflection),
    Cmnd(b"SOUR:IPR?", ScpiPacket.txGetIPReflection),
    Cmnd(b"SOUR:LASER", ScpiPacket.txSetLaserMode),
    Cmnd(b"SOUR:LASER?", ScpiPacket.txGetLaserMode),
    Cmnd(b"SOUR:LASERPUP", ScpiPacket.txSetLaserPwrUp),
    Cmnd(b"SOUR:LASERPUP?", ScpiPacket.txGetLaserPwrUp),
    Cmnd(b"SOUR:LASERTYPE", ScpiPacket.txSetLaserType),
    Cmnd(b"SOUR:LASERTYPE?", ScpiPacket.txGetLaserType),
    Cmnd(b"SOUR:LATENCYMODE", ScpiPacket.setLatencyMode),
    Cmnd(b"SOUR:LATENCYMODE?", ScpiPacket.getLatencyMode),
    Cmnd(b"SOUR:LEN", ScpiPacket.setGfpLen),
    Cmnd(b"SOUR:LEN?", ScpiPacket.getGfpLen),
    Cmnd(b"SOUR:LINECONTROL", ScpiPacket.txSetLineControl),
    Cmnd(b"SOUR:LINECONTROL?", ScpiPacket.txGetLineControl),
    Cmnd(b"SOUR:LINKINIT", ScpiPacket.setLinkinit),
    Cmnd(b"SOUR:LINKINIT?", ScpiPacket.getLinkinit),
    Cmnd(b"SOUR:MAP", ScpiPacket.setPortMap),
    Cmnd(b"SOUR:MAP?", ScpiPacket.getPortMap),
    Cmnd(b"SOUR:MODE", ScpiPacket.txSetMode),
    Cmnd(b"SOUR:MODE?", ScpiPacket.getPortInterface),
    Cmnd(b"SOUR:PAT", ScpiPacket.setGfpPat),
    Cmnd(b"SOUR:PAT?", ScpiPacket.getGfpPat),
    Cmnd(b"SOUR:PAUSE", ScpiPacket.txSetPause),
    Cmnd(b"SOUR:PAUSE?", ScpiPacket.txGetPause),
    Cmnd(b"SOUR:PFCS", ScpiPacket.setGfpPfcs),
    Cmnd(b"SOUR:PFCS?", ScpiPacket.getGfpPfcs),
    Cmnd(b"SOUR:PORTLOGIN", ScpiPacket.portLogin),
    Cmnd(b"SOUR:PORTLOGIN?", ScpiPacket.getPortLoginStatus),
    Cmnd(b"SOUR:PREAMBLE", ScpiPacket.setPreamble),
    Cmnd(b"SOUR:PREAMBLE?", ScpiPacket.getPreamble),
    Cmnd(b"SOUR:PTI", ScpiPacket.setTxPti),
    Cmnd(b"SOUR:PTI?", ScpiPacket.getTxPti),
    Cmnd(b"SOUR:RATE", ScpiPacket.setGfpRate),
    Cmnd(b"SOUR:RATE?", ScpiPacket.getGfpRate),
    Cmnd(b"SOUR:REPLY", ScpiPacket.txSetReply),
    Cmnd(b"SOUR:REPLY?", ScpiPacket.txGetReply),
    Cmnd(b"SOUR:SCRAMBLE", ScpiPacket.setScramble),
    Cmnd(b"SOUR:SCRAMBLE?", ScpiPacket.getScramble),
    Cmnd(b"SOUR:SET?", ScpiPacket.txGetSet),
    Cmnd(b"SOUR:SPARE", ScpiPacket.setTxSpare),
    Cmnd(b"SOUR:SPARE?", ScpiPacket.getTxSpare),
    Cmnd(b"SOUR:STATUS?", ScpiPacket.txGetMode),
    Cmnd(b"SOUR:SUPERBLK", ScpiPacket.setSuperBlock),
    Cmnd(b"SOUR:SUPERBLK?", ScpiPacket.getSuperBlock),
    Cmnd(b"SOUR:UPI", ScpiPacket.setGfpUpi),
    Cmnd(b"SOUR:UPI?", ScpiPacket.getGfpUpi),
    Cmnd(b"SOUR:VLANFLOOD", ScpiPacket.setVlanFlooding),
    Cmnd(b"SOUR:VLANFLOOD?", ScpiPacket.getVlanFlooding),
    Cmnd(b"STRM:ARP", ScpiPacket.setArpEnable),
    Cmnd(b"STRM:ARP?", ScpiPacket.getArpEnable),
    Cmnd(b"STRM:AVG:RXMBPS?", ScpiPacket.getStreamL1RxLinkKBPerSecAvgNone),
    Cmnd(b"STRM:AVG:RXPCTBW?", ScpiPacket.getStreamL1RxLinkPctBandwidthAvgNone),
    Cmnd(b"STRM:AVG:RXPPS?", ScpiPacket.getStreamRxLinkPacketPerSecAvgNone),
    Cmnd(b"STRM:AVG:TXMBPS?", ScpiPacket.getStreamL1TxLinkKBPerSecAvgNone),
    Cmnd(b"STRM:AVG:TXPCTBW?", ScpiPacket.getStreamL1TxLinkPctBandwidthAvgNone),
    Cmnd(b"STRM:AVG:TXPPS?", ScpiPacket.getStreamTxLinkPacketPerSecAvgNone),
    Cmnd(b"STRM:BIT:AVGRATE?", ScpiPacket.getStreamBitAvgRate),
    Cmnd(b"STRM:BIT:COUNT?", ScpiPacket.getStreamBitCount),
    Cmnd(b"STRM:BIT:CURRATE?", ScpiPacket.getStreamBitCurRate),
    Cmnd(b"STRM:BIT:ES?", ScpiPacket.getStreamBitES),
    Cmnd(b"STRM:BURST", ScpiPacket.sendBurst),
    Cmnd(b"STRM:BURSTSIZE", ScpiPacket.setBurst),
    Cmnd(b"STRM:BURSTSIZE?", ScpiPacket.getBurst),
    Cmnd(b"STRM:BW", ScpiPacket.setBandwidth),
    Cmnd(b"STRM:BW?", ScpiPacket.getBandwidth),
    Cmnd(b"STRM:CUR:RXMBPS?", ScpiPacket.getStreamL1RxLinkKBPerSecNone),
    Cmnd(b"STRM:CUR:RXPCTBW?", ScpiPacket.getStreamL1RxLinkPctBandwidthNone),
    Cmnd(b"STRM:CUR:RXPPS?", ScpiPacket.getStreamRxLinkPacketPerSecNone),
    Cmnd(b"STRM:CUR:TXMBPS?", ScpiPacket.getStreamL1TxLinkKBPerSecNone),
    Cmnd(b"STRM:CUR:TXPCTBW?", ScpiPacket.getStreamL1TxLinkPctBandwidthNone),
    Cmnd(b"STRM:CUR:TXPPS?", ScpiPacket.getStreamTxLinkPacketPerSecNone),
    Cmnd(b"STRM:DURATION", ScpiPacket.setTrafficDuration),
    Cmnd(b"STRM:DURATION?", ScpiPacket.getTrafficDuration),
    Cmnd(b"STRM:ETYPE", ScpiPacket.setEtherType),
    Cmnd(b"STRM:ETYPE?", ScpiPacket.getEtherType),
    Cmnd(b"STRM:FC:B2BCREDIT", ScpiPacket.setB2BCredit),
    Cmnd(b"STRM:FC:B2BCREDIT?", ScpiPacket.getB2BCredit),
    Cmnd(b"STRM:FC:CLASS", ScpiPacket.setClass),
    Cmnd(b"STRM:FC:CLASS?", ScpiPacket.getClass),
    Cmnd(b"STRM:FC:CSCTL", ScpiPacket.setCsctl),
    Cmnd(b"STRM:FC:CSCTL?", ScpiPacket.getCsctl),
    Cmnd(b"STRM:FC:DFCTL", ScpiPacket.setDfctl),
    Cmnd(b"STRM:FC:DFCTL?", ScpiPacket.getDfctl),
    Cmnd(b"STRM:FC:DID", ScpiPacket.setDid),
    Cmnd(b"STRM:FC:DID?", ScpiPacket.getDid),
    Cmnd(b"STRM:FC:EOF", ScpiPacket.setEof),
    Cmnd(b"STRM:FC:EOF?", ScpiPacket.getEof),
    Cmnd(b"STRM:FC:FCTL", ScpiPacket.setFctl),
    Cmnd(b"STRM:FC:FCTL?", ScpiPacket.getFctl),
    Cmnd(b"STRM:FC:OXID", ScpiPacket.setOxid),
    Cmnd(b"STRM:FC:OXID?", ScpiPacket.getOxid),
    Cmnd(b"STRM:FC:PARM", ScpiPacket.setParm),
    Cmnd(b"STRM:FC:PARM?", ScpiPacket.getParm),
    Cmnd(b"STRM:FC:RCTL", ScpiPacket.setRctl),
    Cmnd(b"STRM:FC:RCTL?", ScpiPacket.getRctl),
    Cmnd(b"STRM:FC:RXID", ScpiPacket.setRxid),
    Cmnd(b"STRM:FC:RXID?", ScpiPacket.getRxid),
    Cmnd(b"STRM:FC:SEQID", ScpiPacket.setSeqid),
    Cmnd(b"STRM:FC:SEQID?", ScpiPacket.getSeqid),
    Cmnd(b"STRM:FC:SID", ScpiPacket.setSid),
    Cmnd(b"STRM:FC:SID?", ScpiPacket.getSid),
    Cmnd(b"STRM:FC:SOF", ScpiPacket.setSof),
    Cmnd(b"STRM:FC:SOF?", ScpiPacket.getSof),
    Cmnd(b"STRM:FC:TYPE", ScpiPacket.setType),
    Cmnd(b"STRM:FC:TYPE?", ScpiPacket.getType),
    Cmnd(b"STRM:FC:WWNDEST", ScpiPacket.setFcMacdest),
    Cmnd(b"STRM:FC:WWNDEST?", ScpiPacket.getFcMacdest),
    Cmnd(b"STRM:FC:WWNSOURCE", ScpiPacket.setFcMacsource),
    Cmnd(b"STRM:FC:WWNSOURCE?", ScpiPacket.getFcMacsource),
    Cmnd(b"STRM:FRAMESIZE", ScpiPacket.setFramesize),
    Cmnd(b"STRM:FRAMESIZE?", ScpiPacket.getFramesize),
    Cmnd(b"STRM:IPDEST", ScpiPacket.setIpdest),
    Cmnd(b"STRM:IPDEST?", ScpiPacket.getIpdest),
    Cmnd(b"STRM:IPFRAG", ScpiPacket.setIpFrag),
    Cmnd(b"STRM:IPFRAG?", ScpiPacket.getIpFrag),
    Cmnd(b"STRM:IPGB", ScpiPacket.setIpcgC),
    Cmnd(b"STRM:IPGB?", ScpiPacket.getIpcgC),
    Cmnd(b"STRM:IPGM", ScpiPacket.setIpcgM),
    Cmnd(b"STRM:IPGM?", ScpiPacket.getIpcgM),
    Cmnd(b"STRM:IPMODE", ScpiPacket.setIpMode),
    Cmnd(b"STRM:IPMODE?", ScpiPacket.getIpMode),
    Cmnd(b"STRM:IPSOURCE", ScpiPacket.setIpsource),
    Cmnd(b"STRM:IPSOURCE?", ScpiPacket.getIpsource),
    Cmnd(b"STRM:IPTOS", ScpiPacket.setIpTos),
    Cmnd(b"STRM:IPTOS?", ScpiPacket.getIpTos),
    Cmnd(b"STRM:IPTTL", ScpiPacket.setIpTtl),
    Cmnd(b"STRM:IPTTL?", ScpiPacket.getIpTtl),
    Cmnd(b"STRM:IPV6:FLOWLABEL", ScpiPacket.setIpv6FlowControl),
    Cmnd(b"STRM:IPV6:FLOWLABEL?", ScpiPacket.getIpv6FlowControl),
    Cmnd(b"STRM:IPV6:HOPLIMIT", ScpiPacket.setIpv6NextHop),
    Cmnd(b"STRM:IPV6:HOPLIMIT?", ScpiPacket.getIpv6NextHop),
    Cmnd(b"STRM:IPV6:IPDEST", ScpiPacket.setIpv6IpDestAddress),
    Cmnd(b"STRM:IPV6:IPDEST?", ScpiPacket.getIpv6IpDestAddress),
    Cmnd(b"STRM:IPV6:IPSOURCE", ScpiPacket.setIpv6IpSourceAddress),
    Cmnd(b"STRM:IPV6:IPSOURCE?", ScpiPacket.getIpv6IpSourceAddress),
    Cmnd(b"STRM:IPV6:TRAFCLASS", ScpiPacket.setIpv6TrafClass),
    Cmnd(b"STRM:IPV6:TRAFCLASS?", ScpiPacket.getIpv6TrafClass),
    Cmnd(b"STRM:JIT:AVG?", ScpiPacket.getStreamJitAvg),
    Cmnd(b"STRM:JIT:MAX?", ScpiPacket.getStreamJitMax),
    Cmnd(b"STRM:JIT:MIN?", ScpiPacket.getStreamJitMin),
    Cmnd(b"STRM:L1:AVG:RXMBPS?", ScpiPacket.getStreamL1RxLinkKBPerSecAvgNone),
    Cmnd(b"STRM:L1:AVG:RXPCTBW?", ScpiPacket.getStreamL1RxLinkPctBandwidthAvgNone),
    Cmnd(b"STRM:L1:AVG:TXMBPS?", ScpiPacket.getStreamL1TxLinkKBPerSecAvgNone),
    Cmnd(b"STRM:L1:AVG:TXPCTBW?", ScpiPacket.getStreamL1TxLinkPctBandwidthAvgNone),
    Cmnd(b"STRM:L1:CUR:RXMBPS?", ScpiPacket.getStreamL1RxLinkKBPerSecNone),
    Cmnd(b"STRM:L1:CUR:RXPCTBW?", ScpiPacket.getStreamL1RxLinkPctBandwidthNone),
    Cmnd(b"STRM:L1:CUR:TXMBPS?", ScpiPacket.getStreamL1TxLinkKBPerSecNone),
    Cmnd(b"STRM:L1:CUR:TXPCTBW?", ScpiPacket.getStreamL1TxLinkPctBandwidthNone),
    Cmnd(b"STRM:L1:MAX:RXMBPS?", ScpiPacket.getStreamL1RxLinkKBPerSecMaxNone),
    Cmnd(b"STRM:L1:MAX:RXPCTBW?", ScpiPacket.getStreamL1RxLinkPctBandwidthMaxNone),
    Cmnd(b"STRM:L1:MAX:TXMBPS?", ScpiPacket.getStreamL1TxLinkKBPerSecMaxNone),
    Cmnd(b"STRM:L1:MAX:TXPCTBW?", ScpiPacket.getStreamL1TxLinkPctBandwidthMaxNone),
    Cmnd(b"STRM:L1:MIN:RXMBPS?", ScpiPacket.getStreamL1RxLinkKBPerSecMinNone),
    Cmnd(b"STRM:L1:MIN:RXPCTBW?", ScpiPacket.getStreamL1RxLinkPctBandwidthMinNone),
    Cmnd(b"STRM:L1:MIN:TXMBPS?", ScpiPacket.getStreamL1TxLinkKBPerSecMinNone),
    Cmnd(b"STRM:L1:MIN:TXPCTBW?", ScpiPacket.getStreamL1TxLinkPctBandwidthMinNone),
    Cmnd(b"STRM:L2:AVG:RXMBPS?", ScpiPacket.getStreamL2RxLinkKBPerSecAvgNone),
    Cmnd(b"STRM:L2:AVG:RXPCTBW?", ScpiPacket.getStreamL2RxLinkPctBandwidthAvgNone),
    Cmnd(b"STRM:L2:AVG:TXMBPS?", ScpiPacket.getStreamL2TxLinkKBPerSecAvgNone),
    Cmnd(b"STRM:L2:AVG:TXPCTBW?", ScpiPacket.getStreamL2TxLinkPctBandwidthAvgNone),
    Cmnd(b"STRM:L2:CUR:RXMBPS?", ScpiPacket.getStreamL2RxLinkKBPerSecNone),
    Cmnd(b"STRM:L2:CUR:RXPCTBW?", ScpiPacket.getStreamL2RxLinkPctBandwidthNone),
    Cmnd(b"STRM:L2:CUR:TXMBPS?", ScpiPacket.getStreamL2TxLinkKBPerSecNone),
    Cmnd(b"STRM:L2:CUR:TXPCTBW?", ScpiPacket.getStreamL2TxLinkPctBandwidthNone),
    Cmnd(b"STRM:L2:MAX:RXMBPS?", ScpiPacket.getStreamL2RxLinkKBPerSecMaxNone),
    Cmnd(b"STRM:L2:MAX:RXPCTBW?", ScpiPacket.getStreamL2RxLinkPctBandwidthMaxNone),
    Cmnd(b"STRM:L2:MAX:TXMBPS?", ScpiPacket.getStreamL2TxLinkKBPerSecMaxNone),
    Cmnd(b"STRM:L2:MAX:TXPCTBW?", ScpiPacket.getStreamL2TxLinkPctBandwidthMaxNone),
    Cmnd(b"STRM:L2:MIN:RXMBPS?", ScpiPacket.getStreamL2RxLinkKBPerSecMinNone),
    Cmnd(b"STRM:L2:MIN:RXPCTBW?", ScpiPacket.getStreamL2RxLinkPctBandwidthMinNone),
    Cmnd(b"STRM:L2:MIN:TXMBPS?", ScpiPacket.getStreamL2TxLinkKBPerSecMinNone),
    Cmnd(b"STRM:L2:MIN:TXPCTBW?", ScpiPacket.getStreamL2TxLinkPctBandwidthMinNone),
    Cmnd(b"STRM:L2:RXBYTEPS?", ScpiPacket.getStreamL2RxBytesPerSec),
    Cmnd(b"STRM:L2:RXBYTES?", ScpiPacket.getRxStreamBytes),
    Cmnd(b"STRM:L2:TXBYTEPS?", ScpiPacket.getStreamL2TxBytesPerSec),
    Cmnd(b"STRM:L2:TXBYTES?", ScpiPacket.getTxStreamBytes),
    Cmnd(b"STRM:LAT:AVG?", ScpiPacket.getStreamLatAvg),
    Cmnd(b"STRM:LAT:CUR?", ScpiPacket.getStreamLatCur),
    Cmnd(b"STRM:LAT:MAX?", ScpiPacket.getStreamLatMax),
    Cmnd(b"STRM:LAT:MIN?", ScpiPacket.getStreamLatMin),
    Cmnd(b"STRM:LOSS:AVGRATE?", ScpiPacket.getStreamLossAvgRate),
    Cmnd(b"STRM:LOSS:COUNT?", ScpiPacket.getStreamLossCount),
    Cmnd(b"STRM:LOSS:COUNTPS?", ScpiPacket.getStreamLossPerSec),
    Cmnd(b"STRM:LOSS:CURRATE?", ScpiPacket.getStreamLossCurRate),
    Cmnd(b"STRM:LOSS:ES?", ScpiPacket.getStreamLossES),
    Cmnd(b"STRM:MACDEST", ScpiPacket.setMacdest),
    Cmnd(b"STRM:MACDEST?", ScpiPacket.getMacdest),
    Cmnd(b"STRM:MACSOURCE", ScpiPacket.setMacsource),
    Cmnd(b"STRM:MACSOURCE?", ScpiPacket.getMacsource),
    Cmnd(b"STRM:MAX:RXMBPS?", ScpiPacket.getStreamL1RxLinkKBPerSecMaxNone),
    Cmnd(b"STRM:MAX:RXPCTBW?", ScpiPacket.getStreamL1RxLinkPctBandwidthMaxNone),
    Cmnd(b"STRM:MAX:RXPPS?", ScpiPacket.getStreamRxLinkPacketPerSecMaxNone),
    Cmnd(b"STRM:MAX:TXMBPS?", ScpiPacket.getStreamL1TxLinkKBPerSecMaxNone),
    Cmnd(b"STRM:MAX:TXPCTBW?", ScpiPacket.getStreamL1TxLinkPctBandwidthMaxNone),
    Cmnd(b"STRM:MAX:TXPPS?", ScpiPacket.getStreamTxLinkPacketPerSecMaxNone),
    Cmnd(b"STRM:MBPS", ScpiPacket.setMbps),
    Cmnd(b"STRM:MBPS?", ScpiPacket.getMbps),
    Cmnd(b"STRM:MIN:RXMBPS?", ScpiPacket.getStreamL1RxLinkKBPerSecMinNone),
    Cmnd(b"STRM:MIN:RXPCTBW?", ScpiPacket.getStreamL1RxLinkPctBandwidthMinNone),
    Cmnd(b"STRM:MIN:RXPPS?", ScpiPacket.getStreamRxLinkPacketPerSecMinNone),
    Cmnd(b"STRM:MIN:TXMBPS?", ScpiPacket.getStreamL1TxLinkKBPerSecMinNone),
    Cmnd(b"STRM:MIN:TXPCTBW?", ScpiPacket.getStreamL1TxLinkPctBandwidthMinNone),
    Cmnd(b"STRM:MIN:TXPPS?", ScpiPacket.getStreamTxLinkPacketPerSecMinNone),
    Cmnd(b"STRM:PATTERN", ScpiPacket.setPattern),
    Cmnd(b"STRM:PATTERN?", ScpiPacket.getPattern),
    Cmnd(b"STRM:PORTDEST", ScpiPacket.setPortdest),
    Cmnd(b"STRM:PORTDEST?", ScpiPacket.getPortdest),
    Cmnd(b"STRM:PORTSOURCE", ScpiPacket.setPortsource),
    Cmnd(b"STRM:PORTSOURCE?", ScpiPacket.getPortsource),
    Cmnd(b"STRM:PROTOCOL", ScpiPacket.setProtocol),
    Cmnd(b"STRM:PROTOCOL?", ScpiPacket.getProtocol),
    Cmnd(b"STRM:RAMP:CEILBW", ScpiPacket.setRampBw),
    Cmnd(b"STRM:RAMP:CEILBW?", ScpiPacket.getRampBw),
    Cmnd(b"STRM:RAMP:CEILMBPS", ScpiPacket.setRampMbps),
    Cmnd(b"STRM:RAMP:CEILMBPS?", ScpiPacket.getRampMbps),
    Cmnd(b"STRM:RAMP:DUR", ScpiPacket.setRampDur),
    Cmnd(b"STRM:RAMP:DUR?", ScpiPacket.getRampDur),
    Cmnd(b"STRM:RAMP:FLOOR", ScpiPacket.setRampStop),
    Cmnd(b"STRM:RAMP:FLOOR?", ScpiPacket.getRampStop),
    Cmnd(b"STRM:RAMP:FLOORBW", ScpiPacket.setRampStop),
    Cmnd(b"STRM:RAMP:FLOORBW?", ScpiPacket.getRampStop),
    Cmnd(b"STRM:RAMP:FLOORMBPS", ScpiPacket.setRampStop),
    Cmnd(b"STRM:RAMP:FLOORMBPS?", ScpiPacket.getRampStop),
    Cmnd(b"STRM:RAMP:STEP", ScpiPacket.setRampStep),
    Cmnd(b"STRM:RAMP:STEP?", ScpiPacket.getRampStep),
    Cmnd(b"STRM:RAMP:STEPBW", ScpiPacket.setRampStep),
    Cmnd(b"STRM:RAMP:STEPBW?", ScpiPacket.getRampStep),
    Cmnd(b"STRM:RAMP:STEPMBPS", ScpiPacket.setRampStep),
    Cmnd(b"STRM:RAMP:STEPMBPS?", ScpiPacket.getRampStep),
    Cmnd(b"STRM:RAMP:UOM", ScpiPacket.setRampUom),
    Cmnd(b"STRM:RAMP:UOM?", ScpiPacket.getRampUom),
    Cmnd(b"STRM:RXBW?", ScpiPacket.getRxStreamBw),
    Cmnd(b"STRM:RXBYTES?", ScpiPacket.getRxStreamBytes),
    Cmnd(b"STRM:RXLOSS?", ScpiPacket.getRxStreamLoss),
    Cmnd(b"STRM:RXPACKETS?", ScpiPacket.getRxStreamPackets),
    Cmnd(b"STRM:SEQ:AVGRATE?", ScpiPacket.getStreamSeqAvgRate),
    Cmnd(b"STRM:SEQ:COUNT?", ScpiPacket.getStreamSeqCount),
    Cmnd(b"STRM:SEQ:CURRATE?", ScpiPacket.getStreamSeqCurRate),
    Cmnd(b"STRM:SEQ:ES?", ScpiPacket.getStreamSeqES),
    Cmnd(b"STRM:SET?", ScpiPacket.getStrmSet),
    Cmnd(b"STRM:SYNC:SECS?", ScpiPacket.getStreamSyncSecs),
    Cmnd(b"STRM:SYNC:STATE?", ScpiPacket.getStreamSyncState),
    Cmnd(b"STRM:TAG:CUSTOM", ScpiPacket.doTagCustom),
    Cmnd(b"STRM:TAG:LEVEL", ScpiPacket.setTagLevel),
    Cmnd(b"STRM:TAG:LEVEL?", ScpiPacket.getTagLevel),
    Cmnd(b"STRM:TAG:MODE", ScpiPacket.setTagMode),
    Cmnd(b"STRM:TAG:MODE?", ScpiPacket.getTagMode),
    Cmnd(b"STRM:TAG:MPLS", ScpiPacket.doTagMpls),
    Cmnd(b"STRM:TAG:VLAN", ScpiPacket.doTagVlan),
    Cmnd(b"STRM:TRAFFICLAYER", ScpiPacket.setTrafficLayer),
    Cmnd(b"STRM:TRAFFICLAYER?", ScpiPacket.getTrafficLayer),
    Cmnd(b"STRM:TXBW?", ScpiPacket.getTxStreamBw),
    Cmnd(b"STRM:TXBYTES?", ScpiPacket.getTxStreamBytes),
    Cmnd(b"STRM:TXENABLE", ScpiPacket.setTxEnable),
    Cmnd(b"STRM:TXENABLE?", ScpiPacket.getTxEnable),
    Cmnd(b"STRM:TXPACKETS?", ScpiPacket.getTxStreamPackets),
    Cmnd(b"STRM:VLANCFI1", ScpiPacket.setVlanCfi1),
    Cmnd(b"STRM:VLANCFI1?", ScpiPacket.getVlanCfi1),
    Cmnd(b"STRM:VLANCFI2", ScpiPacket.setVlanCfi2),
    Cmnd(b"STRM:VLANCFI2?", ScpiPacket.getVlanCfi2),
    Cmnd(b"STRM:VLANCFI3", ScpiPacket.setVlanCfi3),
    Cmnd(b"STRM:VLANCFI3?", ScpiPacket.getVlanCfi3),
    Cmnd(b"STRM:VLANCFI4", ScpiPacket.setVlanCfi4),
    Cmnd(b"STRM:VLANCFI4?", ScpiPacket.getVlanCfi4),
    Cmnd(b"STRM:VLANDEI1", ScpiPacket.setVlanCfi1),
    Cmnd(b"STRM:VLANDEI1?", ScpiPacket.getVlanCfi1),
    Cmnd(b"STRM:VLANDEI2", ScpiPacket.setVlanCfi2),
    Cmnd(b"STRM:VLANDEI2?", ScpiPacket.getVlanCfi2),
    Cmnd(b"STRM:VLANDEI3", ScpiPacket.setVlanCfi3),
    Cmnd(b"STRM:VLANDEI3?", ScpiPacket.getVlanCfi3),
    Cmnd(b"STRM:VLANDEI4", ScpiPacket.setVlanCfi4),
    Cmnd(b"STRM:VLANDEI4?", ScpiPacket.getVlanCfi4),
    Cmnd(b"STRM:VLANID1", ScpiPacket.setVlanId1),
    Cmnd(b"STRM:VLANID1?", ScpiPacket.getVlanId1),
    Cmnd(b"STRM:VLANID2", ScpiPacket.setVlanId2),
    Cmnd(b"STRM:VLANID2?", ScpiPacket.getVlanId2),
    Cmnd(b"STRM:VLANID3", ScpiPacket.setVlanId3),
    Cmnd(b"STRM:VLANID3?", ScpiPacket.getVlanId3),
    Cmnd(b"STRM:VLANID4", ScpiPacket.setVlanId4),
    Cmnd(b"STRM:VLANID4?", ScpiPacket.getVlanId4),
    Cmnd(b"STRM:VLANQOS1", ScpiPacket.setVlanQos1),
    Cmnd(b"STRM:VLANQOS1?", ScpiPacket.getVlanQos1),
    Cmnd(b"STRM:VLANQOS2", ScpiPacket.setVlanQos2),
    Cmnd(b"STRM:VLANQOS2?", ScpiPacket.getVlanQos2),
    Cmnd(b"STRM:VLANQOS3", ScpiPacket.setVlanQos3),
    Cmnd(b"STRM:VLANQOS3?", ScpiPacket.getVlanQos3),
    Cmnd(b"STRM:VLANQOS4", ScpiPacket.setVlanQos4),
    Cmnd(b"STRM:VLANQOS4?", ScpiPacket.getVlanQos4),
    Cmnd(b"STRM:VLANTAG", ScpiPacket.setVlanTag),
    Cmnd(b"STRM:VLANTAG?", ScpiPacket.getVlanTag),
    Cmnd(b"STRM:VLANTPID1", ScpiPacket.setVlanTpid1),
    Cmnd(b"STRM:VLANTPID1?", ScpiPacket.getVlanTpid1),
    Cmnd(b"STRM:VLANTPID2", ScpiPacket.setVlanTpid2),
    Cmnd(b"STRM:VLANTPID2?", ScpiPacket.getVlanTpid2),
    Cmnd(b"STRM:VLANTPID3", ScpiPacket.setVlanTpid3),
    Cmnd(b"STRM:VLANTPID3?", ScpiPacket.getVlanTpid3),
    Cmnd(b"STRM:VLANTPID4", ScpiPacket.setVlanTpid4),
    Cmnd(b"STRM:VLANTPID4?", ScpiPacket.getVlanTpid4),
    Cmnd(b"TX:AL:TYPE", ScpiPacket.txSetAlarmType),
    Cmnd(b"TX:AL:TYPE?", ScpiPacket.txGetAlarmType),
    Cmnd(b"TX:AUTO", ScpiPacket.txSetAutoNeg),
    Cmnd(b"TX:AUTO?", ScpiPacket.txGetAutoNeg),
    Cmnd(b"TX:BBCREDIT", ScpiPacket.setBBCredit),
    Cmnd(b"TX:BBCREDIT?", ScpiPacket.getBBCredit),
    Cmnd(b"TX:BBCREDITBYPASS", ScpiPacket.setBBCreditBypass),
    Cmnd(b"TX:BBCREDITBYPASS?", ScpiPacket.getBBCreditBypass),
    Cmnd(b"TX:CID", ScpiPacket.setGfpCid),
    Cmnd(b"TX:CID?", ScpiPacket.getGfpCid),
    Cmnd(b"TX:DEFICIT", ScpiPacket.setDeficitIdle),
    Cmnd(b"TX:DEFICIT?", ScpiPacket.getDeficitIdle),
    Cmnd(b"TX:EMIXMODE", ScpiPacket.txSetEmixMode),
    Cmnd(b"TX:EMIXMODE?", ScpiPacket.txGetEmixMode),
    Cmnd(b"TX:ERR:RATE", ScpiPacket.txSetErrRate),
    Cmnd(b"TX:ERR:RATE?", ScpiPacket.txGetErrRate),
    Cmnd(b"TX:ERR:RUNTSIZE", ScpiPacket.txSetRuntSize),
    Cmnd(b"TX:ERR:RUNTSIZE?", ScpiPacket.txGetRuntSize),
    Cmnd(b"TX:ERR:TYPE", ScpiPacket.txSetErrType),
    Cmnd(b"TX:ERR:TYPE?", ScpiPacket.txGetErrType),
    Cmnd(b"TX:EXI", ScpiPacket.setGfpExi),
    Cmnd(b"TX:EXI?", ScpiPacket.getGfpExi),
    Cmnd(b"TX:FABRICLOGIN", ScpiPacket.fabricLogin),
    Cmnd(b"TX:FABRICLOGIN?", ScpiPacket.getFabricLoginStatus),
    Cmnd(b"TX:FCPRIM", ScpiPacket.setTxFcPrim),
    Cmnd(b"TX:FILLWORD", ScpiPacket.setFillword),
    Cmnd(b"TX:FILLWORD?", ScpiPacket.getFillword),
    Cmnd(b"TX:FLOWCONTROL", ScpiPacket.txSetFlowControl),
    Cmnd(b"TX:FLOWCONTROL?", ScpiPacket.txGetFlowControl),
    Cmnd(b"TX:IPR", ScpiPacket.txSetIPReflection),
    Cmnd(b"TX:IPR?", ScpiPacket.txGetIPReflection),
    Cmnd(b"TX:LASER", ScpiPacket.txSetLaserMode),
    Cmnd(b"TX:LASER?", ScpiPacket.txGetLaserMode),
    Cmnd(b"TX:LASERPUP", ScpiPacket.txSetLaserPwrUp),
    Cmnd(b"TX:LASERPUP?", ScpiPacket.txGetLaserPwrUp),
    Cmnd(b"TX:LASERTYPE", ScpiPacket.txSetLaserType),
    Cmnd(b"TX:LASERTYPE?", ScpiPacket.txGetLaserType),
    Cmnd(b"TX:LATENCYMODE", ScpiPacket.setLatencyMode),
    Cmnd(b"TX:LATENCYMODE?", ScpiPacket.getLatencyMode),
    Cmnd(b"TX:LEN", ScpiPacket.setGfpLen),
    Cmnd(b"TX:LEN?", ScpiPacket.getGfpLen),
    Cmnd(b"TX:LINECONTROL", ScpiPacket.txSetLineControl),
    Cmnd(b"TX:LINECONTROL?", ScpiPacket.txGetLineControl),
    Cmnd(b"TX:LINKINIT", ScpiPacket.setLinkinit),
    Cmnd(b"TX:LINKINIT?", ScpiPacket.getLinkinit),
    Cmnd(b"TX:MAP", ScpiPacket.setPortMap),
    Cmnd(b"TX:MAP?", ScpiPacket.getPortMap),
    Cmnd(b"TX:MODE", ScpiPacket.txSetMode),
    Cmnd(b"TX:MODE?", ScpiPacket.getPortInterface),
    Cmnd(b"TX:PAT", ScpiPacket.setGfpPat),
    Cmnd(b"TX:PAT?", ScpiPacket.getGfpPat),
    Cmnd(b"TX:PAUSE", ScpiPacket.txSetPause),
    Cmnd(b"TX:PAUSE?", ScpiPacket.txGetPause),
    Cmnd(b"TX:PFCS", ScpiPacket.setGfpPfcs),
    Cmnd(b"TX:PFCS?", ScpiPacket.getGfpPfcs),
    Cmnd(b"TX:PORTLOGIN", ScpiPacket.portLogin),
    Cmnd(b"TX:PORTLOGIN?", ScpiPacket.getPortLoginStatus),
    Cmnd(b"TX:PREAMBLE", ScpiPacket.setPreamble),
    Cmnd(b"TX:PREAMBLE?", ScpiPacket.getPreamble),
    Cmnd(b"TX:PTI", ScpiPacket.setTxPti),
    Cmnd(b"TX:PTI?", ScpiPacket.getTxPti),
    Cmnd(b"TX:RATE", ScpiPacket.setGfpRate),
    Cmnd(b"TX:RATE?", ScpiPacket.getGfpRate),
    Cmnd(b"TX:REPLY", ScpiPacket.txSetReply),
    Cmnd(b"TX:REPLY?", ScpiPacket.txGetReply),
    Cmnd(b"TX:SCRAMBLE", ScpiPacket.setScramble),
    Cmnd(b"TX:SCRAMBLE?", ScpiPacket.getScramble),
    Cmnd(b"TX:SET?", ScpiPacket.txGetSet),
    Cmnd(b"TX:SPARE", ScpiPacket.setTxSpare),
    Cmnd(b"TX:SPARE?", ScpiPacket.getTxSpare),
    Cmnd(b"TX:STATUS?", ScpiPacket.txGetMode),
    Cmnd(b"TX:SUPERBLK", ScpiPacket.setSuperBlock),
    Cmnd(b"TX:SUPERBLK?", ScpiPacket.getSuperBlock),
    Cmnd(b"TX:UPI", ScpiPacket.setGfpUpi),
    Cmnd(b"TX:UPI?", ScpiPacket.getGfpUpi),
    Cmnd(b"TX:VLANFLOOD", ScpiPacket.setVlanFlooding),
    Cmnd(b"TX:VLANFLOOD?", ScpiPacket.getVlanFlooding),
    Cmnd(b"Y1564:ACT", ScpiPacket.y1564SetActivate),
    Cmnd(b"Y1564:ACT?", ScpiPacket.y1564GetActivate),
    Cmnd(b"Y1564:CIR", ScpiPacket.y1564SetCir),
    Cmnd(b"Y1564:CIR?", ScpiPacket.y1564GetCir),
    Cmnd(b"Y1564:CIREIR", ScpiPacket.y1564SetCirEir),
    Cmnd(b"Y1564:CIREIR?", ScpiPacket.y1564GetCirEir),
    Cmnd(b"Y1564:DEFAULT", ScpiPacket.y1564SetFactoryDeflt),
    Cmnd(b"Y1564:DESTPORT", ScpiPacket.rfcSetDestination),
    Cmnd(b"Y1564:DESTPORT?", ScpiPacket.rfcGetDestination),
    Cmnd(b"Y1564:ENABLE", ScpiPacket.y1564SetEnable),
    Cmnd(b"Y1564:ENABLE?", ScpiPacket.y1564GetEnable),
    Cmnd(b"Y1564:JITPERF?", ScpiPacket.y1564GetJitPerf),
    Cmnd(b"Y1564:LATPERF?", ScpiPacket.y1564GetLatPerf),
    Cmnd(b"Y1564:LOSSPERF?", ScpiPacket.y1564GetLossPerf),
    Cmnd(b"Y1564:MASKSTEP", ScpiPacket.y1564SetMaskStep),
    Cmnd(b"Y1564:MASKSTEP?", ScpiPacket.y1564GetMaskStep),
    Cmnd(b"Y1564:MAXJIT", ScpiPacket.y1564SetMaxJit),
    Cmnd(b"Y1564:MAXJIT?", ScpiPacket.y1564GetMaxJit),
    Cmnd(b"Y1564:MAXLAT", ScpiPacket.y1564SetMaxLat),
    Cmnd(b"Y1564:MAXLAT?", ScpiPacket.y1564GetMaxLat),
    Cmnd(b"Y1564:MAXLOSS", ScpiPacket.y1564SetMaxLoss),
    Cmnd(b"Y1564:MAXLOSS?", ScpiPacket.y1564GetMaxLoss),
    Cmnd(b"Y1564:PERF?", ScpiPacket.y1564GetPerf),
    Cmnd(b"Y1564:PERFDUR", ScpiPacket.y1564SetPerfDur),
    Cmnd(b"Y1564:PERFDUR?", ScpiPacket.y1564GetPerfDur),
    Cmnd(b"Y1564:PERFSTATUS?", ScpiPacket.y1564GetPerfStatus),
    Cmnd(b"Y1564:RAMP?", ScpiPacket.y1564GetRamp),
    Cmnd(b"Y1564:RAMPSTATUS?", ScpiPacket.y1564GetRampStatus),
    Cmnd(b"Y1564:RATESTEP", ScpiPacket.y1564SetRateStep),
    Cmnd(b"Y1564:RATESTEP?", ScpiPacket.y1564GetRateStep),
    Cmnd(b"Y1564:RXPERF?", ScpiPacket.y1564GetRxPerf),
    Cmnd(b"Y1564:SEQPERF?", ScpiPacket.y1564GetSeqPerf),
    Cmnd(b"Y1564:SERVICENAME", ScpiPacket.y1564SetServiceName),
    Cmnd(b"Y1564:SERVICENAME?", ScpiPacket.y1564GetServiceName),
    Cmnd(b"Y1564:STEP?", ScpiPacket.y1564GetStep),
    Cmnd(b"Y1564:TRIALDUR", ScpiPacket.y1564SetTrialDur),
    Cmnd(b"Y1564:TRIALDUR?", ScpiPacket.y1564GetTrialDur)
]


# This converts the above table into a tree of lists that can be searched
# for commands. Doing this here and not in the class init means it is done
# once at boot and not at the start of each user session.
commandTreeRoot = []
ParseUtils.processCommandTableIntoTree(commandTable, commandTreeRoot)


if __name__ == "__main__":
    pass

