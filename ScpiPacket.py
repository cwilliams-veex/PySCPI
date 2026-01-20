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

    # Additional RES Level Commands - Remaining entries from resLevel table
    Cmnd(b"RES:LINECODE",          ScpiPacket.doResLinecodeLevel),
    Cmnd(b"FETC:LINECODE",         ScpiPacket.doResLinecodeLevel),
    Cmnd(b"RES:COLLISION",         ScpiPacket.doResCollisionLevel),
    Cmnd(b"FETC:COLLISION",        ScpiPacket.doResCollisionLevel),
    Cmnd(b"RES:PFCS",              ScpiPacket.doResPfcsLevel),
    Cmnd(b"FETC:PFCS",             ScpiPacket.doResPfcsLevel),
    Cmnd(b"RES:IPCHECKSUM",        ScpiPacket.doResIpChecksumLevel),
    Cmnd(b"FETC:IPCHECKSUM",       ScpiPacket.doResIpChecksumLevel),
    Cmnd(b"RES:SCANERRORS?",       ScpiPacket.getCurrentErrors),
    Cmnd(b"FETC:SCANERRORS?",      ScpiPacket.getCurrentErrors),
    Cmnd(b"RES:FCALIGN",           ScpiPacket.doResFcAlignLevel),
    Cmnd(b"FETC:FCALIGN",          ScpiPacket.doResFcAlignLevel),
    Cmnd(b"RES:OVERSIZED",         ScpiPacket.doResOversizedLevel),
    Cmnd(b"FETC:OVERSIZED",        ScpiPacket.doResOversizedLevel),
    Cmnd(b"RES:UNDERSIZED",        ScpiPacket.doResUndersizedLevel),
    Cmnd(b"FETC:UNDERSIZED",       ScpiPacket.doResUndersizedLevel),
    Cmnd(b"RES:LOSS",              ScpiPacket.doResCppLevel),
    Cmnd(b"FETC:LOSS",             ScpiPacket.doResCppLevel),
    Cmnd(b"RES:LOS",               ScpiPacket.doResLosLevel),
    Cmnd(b"FETC:LOS",              ScpiPacket.doResLosLevel),
    Cmnd(b"RES:LINK",              ScpiPacket.doResLinkLevel),
    Cmnd(b"FETC:LINK",             ScpiPacket.doResLinkLevel),
    Cmnd(b"RES:TXPACK?",           ScpiPacket.getResTxPackets),
    Cmnd(b"FETC:TXPACK?",          ScpiPacket.getResTxPackets),
    Cmnd(b"RES:RXPACK?",           ScpiPacket.getResRxPackets),
    Cmnd(b"FETC:RXPACK?",          ScpiPacket.getResRxPackets),
    Cmnd(b"RES:TXBYT?",            ScpiPacket.getResTxBytes),
    Cmnd(b"FETC:TXBYT?",           ScpiPacket.getResTxBytes),
    Cmnd(b"RES:RXBYT?",            ScpiPacket.getResRxBytes),
    Cmnd(b"FETC:RXBYT?",           ScpiPacket.getResRxBytes),
    Cmnd(b"RES:JUMBO?",            ScpiPacket.getResRxJumboPackets),
    Cmnd(b"FETC:JUMBO?",           ScpiPacket.getResRxJumboPackets),
    Cmnd(b"RES:PAUSE",             ScpiPacket.doResPauseLevel),
    Cmnd(b"FETC:PAUSE",            ScpiPacket.doResPauseLevel),
    Cmnd(b"RES:TXPACK",            ScpiPacket.doResTxPacketLevel),
    Cmnd(b"FETC:TXPACK",           ScpiPacket.doResTxPacketLevel),
    Cmnd(b"RES:VLAN",              ScpiPacket.doResVlanLevel),
    Cmnd(b"FETC:VLAN",             ScpiPacket.doResVlanLevel),
    Cmnd(b"RES:TXPCTBW?",          ScpiPacket.getResTxLinkPctBandwidthNone),
    Cmnd(b"FETC:TXPCTBW?",         ScpiPacket.getResTxLinkPctBandwidthNone),
    Cmnd(b"RES:RXPCTBW?",          ScpiPacket.getResRxLinkPctBandwidthNone),
    Cmnd(b"FETC:RXPCTBW?",         ScpiPacket.getResRxLinkPctBandwidthNone),
    Cmnd(b"RES:TXPPS?",            ScpiPacket.getResTxLinkPacketPerSecNone),
    Cmnd(b"FETC:TXPPS?",           ScpiPacket.getResTxLinkPacketPerSecNone),
    Cmnd(b"RES:RXPPS?",            ScpiPacket.getResRxLinkPacketPerSecNone),
    Cmnd(b"FETC:RXPPS?",           ScpiPacket.getResRxLinkPacketPerSecNone),
    Cmnd(b"RES:TXMBPS?",           ScpiPacket.getResTxLinkKBPerSecNone),
    Cmnd(b"FETC:TXMBPS?",          ScpiPacket.getResTxLinkKBPerSecNone),
    Cmnd(b"RES:RXMBPS?",           ScpiPacket.getResRxLinkKBPerSecNone),
    Cmnd(b"FETC:RXMBPS?",          ScpiPacket.getResRxLinkKBPerSecNone),
    Cmnd(b"RES:SPM?",              ScpiPacket.getResSPM),
    Cmnd(b"FETC:SPM?",             ScpiPacket.getResSPM),
    Cmnd(b"RES:STSD?",             ScpiPacket.getResSTSD),
    Cmnd(b"FETC:STSD?",            ScpiPacket.getResSTSD),
    Cmnd(b"RES:EVENTLOG",          ScpiPacket.getEventLog),
    Cmnd(b"FETC:EVENTLOG",         ScpiPacket.getEventLog),
    Cmnd(b"RES:RF",                ScpiPacket.doResRfLevel),
    Cmnd(b"FETC:RF",               ScpiPacket.doResRfLevel),
    Cmnd(b"RES:LFD",               ScpiPacket.doResLfdLevel),
    Cmnd(b"FETC:LFD",              ScpiPacket.doResLfdLevel),
    Cmnd(b"RES:UCHEC",             ScpiPacket.doResUnCorrCHecLevel),
    Cmnd(b"FETC:UCHEC",            ScpiPacket.doResUnCorrCHecLevel),
    Cmnd(b"RES:CHEC",              ScpiPacket.doResCorrCHecLevel),
    Cmnd(b"FETC:CHEC",             ScpiPacket.doResCorrCHecLevel),
    Cmnd(b"RES:UTHEC",             ScpiPacket.doResUnCorrTHecLevel),
    Cmnd(b"FETC:UTHEC",            ScpiPacket.doResUnCorrTHecLevel),
    Cmnd(b"RES:THEC",              ScpiPacket.doResCorrTHecLevel),
    Cmnd(b"FETC:THEC",             ScpiPacket.doResCorrTHecLevel),
    Cmnd(b"RES:UEHEC",             ScpiPacket.doResUnCorrEHecLevel),
    Cmnd(b"FETC:UEHEC",            ScpiPacket.doResUnCorrEHecLevel),
    Cmnd(b"RES:EHEC",              ScpiPacket.doResCorrEHecLevel),
    Cmnd(b"FETC:EHEC",             ScpiPacket.doResCorrEHecLevel),
    Cmnd(b"RES:SFCS",              ScpiPacket.doResSfcsLevel),
    Cmnd(b"FETC:SFCS",             ScpiPacket.doResSfcsLevel),
    Cmnd(b"RES:LF",                ScpiPacket.doResLfLevel),
    Cmnd(b"FETC:LF",               ScpiPacket.doResLfLevel),
    Cmnd(b"RES:LOCCS",             ScpiPacket.doResLoccsLevel),
    Cmnd(b"FETC:LOCCS",            ScpiPacket.doResLoccsLevel),
    Cmnd(b"RES:LOCS",              ScpiPacket.doResLocLevel),
    Cmnd(b"FETC:LOCS",             ScpiPacket.doResLocLevel),
    Cmnd(b"RES:CRC",               ScpiPacket.doResFcsLevel),
    Cmnd(b"FETC:CRC",              ScpiPacket.doResFcsLevel),
    Cmnd(b"RES:FABRICLOGIN?",      ScpiPacket.getFabricLoginStatus),
    Cmnd(b"FETC:FABRICLOGIN?",     ScpiPacket.getFabricLoginStatus),
    Cmnd(b"RES:PORTLOGIN?",        ScpiPacket.getPortLoginStatus),
    Cmnd(b"FETC:PORTLOGIN?",       ScpiPacket.getPortLoginStatus),
    Cmnd(b"RES:FCDISP",            ScpiPacket.doResFcDispLevel),
    Cmnd(b"FETC:FCDISP",           ScpiPacket.doResFcDispLevel),
    Cmnd(b"RES:FCEOFA",            ScpiPacket.doResFcEofALevel),
    Cmnd(b"FETC:FCEOFA",           ScpiPacket.doResFcEofALevel),
    Cmnd(b"RES:RUNT",              ScpiPacket.doResRuntLevel),
    Cmnd(b"FETC:RUNT",             ScpiPacket.doResRuntLevel),
    Cmnd(b"RES:FCS",               ScpiPacket.doResFcsLevel),
    Cmnd(b"FETC:FCS",              ScpiPacket.doResFcsLevel),
    Cmnd(b"RES:INVSUPER",          ScpiPacket.doResInvSuperLevel),
    Cmnd(b"FETC:INVSUPER",         ScpiPacket.doResInvSuperLevel),
    Cmnd(b"RES:JABBER",            ScpiPacket.doResJabberLevel),
    Cmnd(b"FETC:JABBER",           ScpiPacket.doResJabberLevel),
    Cmnd(b"RES:TCPERR",            ScpiPacket.doResTcpChecksumLevel),
    Cmnd(b"FETC:TCPERR",           ScpiPacket.doResTcpChecksumLevel),
    Cmnd(b"RES:UDPERR",            ScpiPacket.doResUdpChecksumLevel),
    Cmnd(b"FETC:UDPERR",           ScpiPacket.doResUdpChecksumLevel),
    Cmnd(b"RES:SCANALARMS?",       ScpiPacket.getCurrentAlarms),
    Cmnd(b"FETC:SCANALARMS?",      ScpiPacket.getCurrentAlarms),
    Cmnd(b"RES:FCEOFERR",          ScpiPacket.doResFcEofErrLevel),
    Cmnd(b"FETC:FCEOFERR",         ScpiPacket.doResFcEofErrLevel),
    Cmnd(b"RES:AL",                ScpiPacket.doResAlarmLevel),
    Cmnd(b"FETC:AL",               ScpiPacket.doResAlarmLevel),
    Cmnd(b"RES:DISPARITY",         ScpiPacket.doResDisparityLevel),
    Cmnd(b"FETC:DISPARITY",        ScpiPacket.doResDisparityLevel),
    Cmnd(b"RES:CAPTURE",           ScpiPacket.doResCaptureLevel),
    Cmnd(b"FETC:CAPTURE",          ScpiPacket.doResCaptureLevel),
    Cmnd(b"RES:HDRMM",             ScpiPacket.doResHdrMMLevel),
    Cmnd(b"FETC:HDRMM",            ScpiPacket.doResHdrMMLevel),
    Cmnd(b"RES:RXPACK",            ScpiPacket.doResRxPacketLevel),
    Cmnd(b"FETC:RXPACK",           ScpiPacket.doResRxPacketLevel),
    Cmnd(b"RES:UTIL",              ScpiPacket.doResUtilLevel),
    Cmnd(b"FETC:UTIL",             ScpiPacket.doResUtilLevel),
    Cmnd(b"RES:MPLS",              ScpiPacket.doResMplsLevel),
    Cmnd(b"FETC:MPLS",             ScpiPacket.doResMplsLevel),
    Cmnd(b"RES:PACK",              ScpiPacket.doResPacketLevel),
    Cmnd(b"FETC:PACK",             ScpiPacket.doResPacketLevel),
    Cmnd(b"RES:SUPJUMBO?",         ScpiPacket.getResOversizedCount),
    Cmnd(b"FETC:SUPJUMBO?",        ScpiPacket.getResOversizedCount),
    Cmnd(b"RES:SYNCHDR",           ScpiPacket.doResSyncHdrLevel),
    Cmnd(b"FETC:SYNCHDR",          ScpiPacket.doResSyncHdrLevel),
    Cmnd(b"RES:BLKLOC",            ScpiPacket.doResBlockLockLossLevel),
    Cmnd(b"FETC:BLKLOC",           ScpiPacket.doResBlockLockLossLevel),
    Cmnd(b"RES:HIBER",             ScpiPacket.doResHiBerLevel),
    Cmnd(b"FETC:HIBER",            ScpiPacket.doResHiBerLevel),
    Cmnd(b"RES:PAUSED",            ScpiPacket.doResPauseLevel),  # Alias for PAUSE
    Cmnd(b"FETC:PAUSED",           ScpiPacket.doResPauseLevel),
    Cmnd(b"RES:CAPSTATUS?",        ScpiPacket.getCaptureStatus),
    Cmnd(b"FETC:CAPSTATUS?",       ScpiPacket.getCaptureStatus),
    Cmnd(b"RES:CAPCOUNT?",         ScpiPacket.getCaptureCount),
    Cmnd(b"FETC:CAPCOUNT?",        ScpiPacket.getCaptureCount),
    ]


# This converts the above table into a tree of lists that can be searched
# for commands. Doing this here and not in the class init means it is done
# once at boot and not at the start of each user session.
commandTreeRoot = []
ParseUtils.processCommandTableIntoTree(commandTable, commandTreeRoot)


if __name__ == "__main__":
    pass

