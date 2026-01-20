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

    # ============================================================================
    # AUTO-GENERATED STUB FUNCTIONS
    # These functions are referenced in commandTable but not yet implemented.
    # Each stub follows the getRxbCast template pattern.
    # ============================================================================

    def doTagCustom(self, parameters):
        """**STRM:TAG:CUSTOM** - doTagCustom command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement doTagCustom
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doTagMpls(self, parameters):
        """**STRM:TAG:MPLS** - doTagMpls command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement doTagMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def doTagVlan(self, parameters):
        """**STRM:TAG:VLAN** - doTagVlan command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement doTagVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def fabricLogin(self, parameters):
        """**SOUR:FABRICLOGIN** - fabricLogin command.
        Also used for:
        - TX:FABRICLOGIN
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement fabricLogin
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getArpEnable(self, parameters):
        """**STRM:ARP?** - getArpEnable command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getArpEnable
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getB2BCredit(self, parameters):
        """**STRM:FC:B2BCREDIT?** - getB2BCredit command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getB2BCredit
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getBBCredit(self, parameters):
        """**SOUR:BBCREDIT?** - getBBCredit command.
        Also used for:
        - TX:BBCREDIT?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getBBCredit
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getBBCreditBypass(self, parameters):
        """**SOUR:BBCREDITBYPASS?** - getBBCreditBypass command.
        Also used for:
        - TX:BBCREDITBYPASS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getBBCreditBypass
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getBandwidth(self, parameters):
        """**STRM:BW?** - getBandwidth command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getBandwidth
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getBurst(self, parameters):
        """**STRM:BURSTSIZE?** - getBurst command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getBurst
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getBytesRx(self, parameters):
        """**PING:BYTESRX?** - getBytesRx command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getBytesRx
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getCaptureCid(self, parameters):
        """**FETC:CAPTURE:CID?** - getCaptureCid command.
        Also used for:
        - RES:CAPTURE:CID?
        - RX:OH:CID?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getCaptureCid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getCaptureExi(self, parameters):
        """**FETC:CAPTURE:EXI?** - getCaptureExi command.
        Also used for:
        - RES:CAPTURE:EXI?
        - RX:OH:EXI?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %s
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getCaptureExi
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getCapturePfi(self, parameters):
        """**FETC:CAPTURE:PFI?** - getCapturePfi command.
        Also used for:
        - RES:CAPTURE:PFI?
        - RX:OH:PFI?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %s
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getCapturePfi
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getCapturePli(self, parameters):
        """**FETC:CAPTURE:PLI?** - getCapturePli command.
        Also used for:
        - RES:CAPTURE:PLI?
        - RX:OH:PLI?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: 0x%X
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getCapturePli
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getCapturePti(self, parameters):
        """**FETC:CAPTURE:PTI?** - getCapturePti command.
        Also used for:
        - RES:CAPTURE:PTI?
        - RX:OH:PTI?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %s
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getCapturePti
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getCaptureSize(self, parameters):
        """**RX:CAPSIZE?** - getCaptureSize command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getCaptureSize
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getCaptureSpare(self, parameters):
        """**FETC:CAPTURE:SPARE?** - getCaptureSpare command.
        Also used for:
        - RES:CAPTURE:SPARE?
        - RX:OH:SPARE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getCaptureSpare
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getCaptureUpi(self, parameters):
        """**FETC:CAPTURE:UPI?** - getCaptureUpi command.
        Also used for:
        - RES:CAPTURE:UPI?
        - RX:OH:UPI?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %s
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getCaptureUpi
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getClass(self, parameters):
        """**STRM:FC:CLASS?** - getClass command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %X
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getClass
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getCsctl(self, parameters):
        """**STRM:FC:CSCTL?** - getCsctl command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %02X
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getCsctl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getDeficitIdle(self, parameters):
        """**SOUR:DEFICIT?** - getDeficitIdle command.
        Also used for:
        - TX:DEFICIT?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getDeficitIdle
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getDestMAC(self, parameters):
        """**PING:DESTMAC?** - getDestMAC command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %x
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getDestMAC
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getDfctl(self, parameters):
        """**STRM:FC:DFCTL?** - getDfctl command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %02X
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getDfctl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getDid(self, parameters):
        """**STRM:FC:DID?** - getDid command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %06X
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getDid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getEof(self, parameters):
        """**STRM:FC:EOF?** - getEof command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: EOFt
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getEof
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getEtherType(self, parameters):
        """**STRM:ETYPE?** - getEtherType command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getEtherType
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getFcMacdest(self, parameters):
        """**STRM:FC:WWNDEST?** - getFcMacdest command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getFcMacdest
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getFcMacsource(self, parameters):
        """**STRM:FC:WWNSOURCE?** - getFcMacsource command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getFcMacsource
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getFctl(self, parameters):
        """**STRM:FC:FCTL?** - getFctl command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %06X
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getFctl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getFillword(self, parameters):
        """**SOUR:FILLWORD?** - getFillword command.
        Also used for:
        - TX:FILLWORD?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getFillword
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getFramesize(self, parameters):
        """**STRM:FRAMESIZE?** - getFramesize command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getFramesize
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getGatewayAddr(self, parameters):
        """**ARP:GATEWAY?** - getGatewayAddr command.
        Also used for:
        - PING:GATEWAY?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getGatewayAddr
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getGfpCid(self, parameters):
        """**SOUR:CID?** - getGfpCid command.
        Also used for:
        - TX:CID?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getGfpCid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getGfpExi(self, parameters):
        """**SOUR:EXI?** - getGfpExi command.
        Also used for:
        - TX:EXI?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getGfpExi
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getGfpLen(self, parameters):
        """**SOUR:LEN?** - getGfpLen command.
        Also used for:
        - TX:LEN?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getGfpLen
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getGfpPat(self, parameters):
        """**SOUR:PAT?** - getGfpPat command.
        Also used for:
        - TX:PAT?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getGfpPat
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getGfpPfcs(self, parameters):
        """**SOUR:PFCS?** - getGfpPfcs command.
        Also used for:
        - TX:PFCS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getGfpPfcs
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getGfpRate(self, parameters):
        """**SOUR:RATE?** - getGfpRate command.
        Also used for:
        - TX:RATE?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getGfpRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getGfpUpi(self, parameters):
        """**SOUR:UPI?** - getGfpUpi command.
        Also used for:
        - TX:UPI?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getGfpUpi
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIPDest(self, parameters):
        """**PING:IPDEST?** - getIPDest command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIPDest
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIPSrc(self, parameters):
        """**ARP:IPSRC?** - getIPSrc command.
        Also used for:
        - PING:IPSRC?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIPSrc
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIpFrag(self, parameters):
        """**STRM:IPFRAG?** - getIpFrag command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIpFrag
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIpMode(self, parameters):
        """**STRM:IPMODE?** - getIpMode command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIpMode
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIpTos(self, parameters):
        """**STRM:IPTOS?** - getIpTos command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIpTos
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIpTtl(self, parameters):
        """**STRM:IPTTL?** - getIpTtl command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIpTtl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIpcgC(self, parameters):
        """**STRM:IPGB?** - getIpcgC command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIpcgC
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIpcgM(self, parameters):
        """**STRM:IPGM?** - getIpcgM command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIpcgM
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIpdest(self, parameters):
        """**STRM:IPDEST?** - getIpdest command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIpdest
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIpsource(self, parameters):
        """**STRM:IPSOURCE?** - getIpsource command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIpsource
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIpv6FlowControl(self, parameters):
        """**STRM:IPV6:FLOWLABEL?** - getIpv6FlowControl command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIpv6FlowControl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIpv6IpDestAddress(self, parameters):
        """**STRM:IPV6:IPDEST?** - getIpv6IpDestAddress command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIpv6IpDestAddress
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIpv6IpSourceAddress(self, parameters):
        """**STRM:IPV6:IPSOURCE?** - getIpv6IpSourceAddress command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIpv6IpSourceAddress
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIpv6NextHop(self, parameters):
        """**STRM:IPV6:HOPLIMIT?** - getIpv6NextHop command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIpv6NextHop
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getIpv6TrafClass(self, parameters):
        """**STRM:IPV6:TRAFCLASS?** - getIpv6TrafClass command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getIpv6TrafClass
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getLatencyMode(self, parameters):
        """**SOUR:LATENCYMODE?** - getLatencyMode command.
        Also used for:
        - TX:LATENCYMODE?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %s
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getLatencyMode
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getLinkinit(self, parameters):
        """**SOUR:LINKINIT?** - getLinkinit command.
        Also used for:
        - TX:LINKINIT?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getLinkinit
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getLoss(self, parameters):
        """**PING:LOSS?** - getLoss command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %.2f
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getLoss
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getMACSrc(self, parameters):
        """**ARP:MACSRC?** - getMACSrc command.
        Also used for:
        - PING:MACSRC?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %x
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getMACSrc
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getMacdest(self, parameters):
        """**STRM:MACDEST?** - getMacdest command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getMacdest
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getMacsource(self, parameters):
        """**STRM:MACSOURCE?** - getMacsource command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getMacsource
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getMbps(self, parameters):
        """**STRM:MBPS?** - getMbps command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getMbps
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getNumPings(self, parameters):
        """**PING:NUMPINGS?** - getNumPings command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getNumPings
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getOxid(self, parameters):
        """**STRM:FC:OXID?** - getOxid command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %04X
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getOxid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getParm(self, parameters):
        """**STRM:FC:PARM?** - getParm command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %08X
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getParm
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getPattern(self, parameters):
        """**STRM:PATTERN?** - getPattern command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getPattern
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getPktLen(self, parameters):
        """**PING:PKTLEN?** - getPktLen command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getPktLen
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getPktTTL(self, parameters):
        """**PING:PKTTTL?** - getPktTTL command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getPktTTL
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getPktTime(self, parameters):
        """**PING:PKTTIME?** - getPktTime command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getPktTime
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getPortInterface(self, parameters):
        """**SOUR:MODE?** - getPortInterface command.
        Also used for:
        - TX:MODE?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getPortInterface
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getPortMap(self, parameters):
        """**SOUR:MAP?** - getPortMap command.
        Also used for:
        - TX:MAP?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getPortMap
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getPortdest(self, parameters):
        """**STRM:PORTDEST?** - getPortdest command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getPortdest
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getPortsource(self, parameters):
        """**STRM:PORTSOURCE?** - getPortsource command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getPortsource
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getPpPauseState(self, parameters):
        """**RX:PAUSE?** - getPpPauseState command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getPpPauseState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getPreamble(self, parameters):
        """**SOUR:PREAMBLE?** - getPreamble command.
        Also used for:
        - TX:PREAMBLE?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getPreamble
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getProtocol(self, parameters):
        """**STRM:PROTOCOL?** - getProtocol command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getProtocol
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRTDAvg(self, parameters):
        """**PING:RTDAVG?** - getRTDAvg command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %ld ms
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRTDAvg
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRTDMax(self, parameters):
        """**PING:RTDMAX?** - getRTDMax command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %ld ms
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRTDMax
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRTDMin(self, parameters):
        """**PING:RTDMIN?** - getRTDMin command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %ld ms
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRTDMin
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRampBw(self, parameters):
        """**STRM:RAMP:CEILBW?** - getRampBw command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRampBw
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRampDur(self, parameters):
        """**STRM:RAMP:DUR?** - getRampDur command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRampDur
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRampMbps(self, parameters):
        """**STRM:RAMP:CEILMBPS?** - getRampMbps command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRampMbps
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRampStep(self, parameters):
        """**STRM:RAMP:STEP?** - getRampStep command.
        Also used for:
        - STRM:RAMP:STEPBW?
        - STRM:RAMP:STEPMBPS?
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRampStep
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRampStop(self, parameters):
        """**STRM:RAMP:FLOOR?** - getRampStop command.
        Also used for:
        - STRM:RAMP:FLOORBW?
        - STRM:RAMP:FLOORMBPS?
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRampStop
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRampUom(self, parameters):
        """**STRM:RAMP:UOM?** - getRampUom command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRampUom
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRctl(self, parameters):
        """**STRM:FC:RCTL?** - getRctl command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %02X
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRctl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getReply(self, parameters):
        """**PING:REPLY?** - getReply command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getReply
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResAlarmPausedState(self, parameters):
        """**FETC:AL:PAUSED?** - getResAlarmPausedState command.
        Also used for:
        - RES:AL:PAUSED?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: Fabric: State Unknown
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResAlarmPausedState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResBgpPackets(self, parameters):
        """**FETC:PACK:BGP?** - getResBgpPackets command.
        Also used for:
        - FETC:RXPACK:BGP?
        - RES:PACK:BGP?
        - RES:RXPACK:BGP?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResBgpPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCollisionAvgRate(self, parameters):
        """**FETC:COLLISION:AVGRATE?** - getResCollisionAvgRate command.
        Also used for:
        - RES:COLLISION:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCollisionAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCollisionCount(self, parameters):
        """**FETC:COLLISION:COUNT?** - getResCollisionCount command.
        Also used for:
        - RES:COLLISION:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCollisionCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCollisionCurRate(self, parameters):
        """**FETC:COLLISION:CURRATE?** - getResCollisionCurRate command.
        Also used for:
        - RES:COLLISION:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCollisionCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCollisionES(self, parameters):
        """**FETC:COLLISION:ES?** - getResCollisionES command.
        Also used for:
        - RES:COLLISION:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCollisionES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCorrCHecAvgRate(self, parameters):
        """**FETC:CHEC:AVGRATE?** - getResCorrCHecAvgRate command.
        Also used for:
        - RES:CHEC:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCorrCHecAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCorrCHecCount(self, parameters):
        """**FETC:CHEC:COUNT?** - getResCorrCHecCount command.
        Also used for:
        - RES:CHEC:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCorrCHecCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCorrCHecCurRate(self, parameters):
        """**FETC:CHEC:CURRATE?** - getResCorrCHecCurRate command.
        Also used for:
        - RES:CHEC:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCorrCHecCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCorrCHecES(self, parameters):
        """**FETC:CHEC:ES?** - getResCorrCHecES command.
        Also used for:
        - RES:CHEC:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCorrCHecES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCorrEHecAvgRate(self, parameters):
        """**FETC:EHEC:AVGRATE?** - getResCorrEHecAvgRate command.
        Also used for:
        - RES:EHEC:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCorrEHecAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCorrEHecCount(self, parameters):
        """**FETC:EHEC:COUNT?** - getResCorrEHecCount command.
        Also used for:
        - RES:EHEC:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCorrEHecCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCorrEHecCurRate(self, parameters):
        """**FETC:EHEC:CURRATE?** - getResCorrEHecCurRate command.
        Also used for:
        - RES:EHEC:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCorrEHecCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCorrEHecES(self, parameters):
        """**FETC:EHEC:ES?** - getResCorrEHecES command.
        Also used for:
        - RES:EHEC:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCorrEHecES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCorrTHecAvgRate(self, parameters):
        """**FETC:THEC:AVGRATE?** - getResCorrTHecAvgRate command.
        Also used for:
        - RES:THEC:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCorrTHecAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCorrTHecCount(self, parameters):
        """**FETC:THEC:COUNT?** - getResCorrTHecCount command.
        Also used for:
        - RES:THEC:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCorrTHecCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCorrTHecCurRate(self, parameters):
        """**FETC:THEC:CURRATE?** - getResCorrTHecCurRate command.
        Also used for:
        - RES:THEC:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCorrTHecCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCorrTHecES(self, parameters):
        """**FETC:THEC:ES?** - getResCorrTHecES command.
        Also used for:
        - RES:THEC:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCorrTHecES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCpPowerLossSecs(self, parameters):
        """**FETC:LOSS:SECS?** - getResCpPowerLossSecs command.
        Also used for:
        - RES:LOSS:SECS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %u
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCpPowerLossSecs
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResCpPowerLossState(self, parameters):
        """**FETC:AL:CPP?** - getResCpPowerLossState command.
        Also used for:
        - FETC:LOSS:STATE?
        - RES:AL:CPP?
        - RES:LOSS:STATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %u
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResCpPowerLossState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResDisparityAvgRate(self, parameters):
        """**FETC:DISPARITY:AVGRATE?** - getResDisparityAvgRate command.
        Also used for:
        - RES:DISPARITY:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResDisparityAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResDisparityCount(self, parameters):
        """**FETC:DISPARITY:COUNT?** - getResDisparityCount command.
        Also used for:
        - RES:DISPARITY:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResDisparityCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResDisparityCurRate(self, parameters):
        """**FETC:DISPARITY:CURRATE?** - getResDisparityCurRate command.
        Also used for:
        - RES:DISPARITY:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResDisparityCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResDisparityES(self, parameters):
        """**FETC:DISPARITY:ES?** - getResDisparityES command.
        Also used for:
        - RES:DISPARITY:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResDisparityES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcAlignAvgRate(self, parameters):
        """**FETC:FCALIGN:AVGRATE?** - getResFcAlignAvgRate command.
        Also used for:
        - RES:FCALIGN:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcAlignAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcAlignCount(self, parameters):
        """**FETC:FCALIGN:COUNT?** - getResFcAlignCount command.
        Also used for:
        - RES:FCALIGN:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcAlignCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcAlignCurRate(self, parameters):
        """**FETC:FCALIGN:CURRATE?** - getResFcAlignCurRate command.
        Also used for:
        - RES:FCALIGN:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcAlignCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcAlignES(self, parameters):
        """**FETC:FCALIGN:ES?** - getResFcAlignES command.
        Also used for:
        - RES:FCALIGN:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcAlignES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcDispAvgRate(self, parameters):
        """**FETC:FCDISP:AVGRATE?** - getResFcDispAvgRate command.
        Also used for:
        - RES:FCDISP:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcDispAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcDispCount(self, parameters):
        """**FETC:FCDISP:COUNT?** - getResFcDispCount command.
        Also used for:
        - RES:FCDISP:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcDispCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcDispCurRate(self, parameters):
        """**FETC:FCDISP:CURRATE?** - getResFcDispCurRate command.
        Also used for:
        - RES:FCDISP:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcDispCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcDispES(self, parameters):
        """**FETC:FCDISP:ES?** - getResFcDispES command.
        Also used for:
        - RES:FCDISP:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcDispES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcEofAAvgRate(self, parameters):
        """**FETC:FCEOFA:AVGRATE?** - getResFcEofAAvgRate command.
        Also used for:
        - RES:FCEOFA:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcEofAAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcEofACount(self, parameters):
        """**FETC:FCEOFA:COUNT?** - getResFcEofACount command.
        Also used for:
        - RES:FCEOFA:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcEofACount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcEofACurRate(self, parameters):
        """**FETC:FCEOFA:CURRATE?** - getResFcEofACurRate command.
        Also used for:
        - RES:FCEOFA:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcEofACurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcEofAES(self, parameters):
        """**FETC:FCEOFA:ES?** - getResFcEofAES command.
        Also used for:
        - RES:FCEOFA:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcEofAES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcEofErrAvgRate(self, parameters):
        """**FETC:FCEOFERR:AVGRATE?** - getResFcEofErrAvgRate command.
        Also used for:
        - RES:FCEOFERR:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcEofErrAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcEofErrCount(self, parameters):
        """**FETC:FCEOFERR:COUNT?** - getResFcEofErrCount command.
        Also used for:
        - RES:FCEOFERR:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcEofErrCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcEofErrCurRate(self, parameters):
        """**FETC:FCEOFERR:CURRATE?** - getResFcEofErrCurRate command.
        Also used for:
        - RES:FCEOFERR:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcEofErrCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcEofErrES(self, parameters):
        """**FETC:FCEOFERR:ES?** - getResFcEofErrES command.
        Also used for:
        - RES:FCEOFERR:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcEofErrES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcsAvgRate(self, parameters):
        """**FETC:CRC:AVGRATE?** - getResFcsAvgRate command.
        Also used for:
        - FETC:FCS:AVGRATE?
        - RES:CRC:AVGRATE?
        - RES:FCS:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcsAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcsCount(self, parameters):
        """**FETC:CRC:COUNT?** - getResFcsCount command.
        Also used for:
        - FETC:FCS:COUNT?
        - RES:CRC:COUNT?
        - RES:FCS:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcsCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcsCurRate(self, parameters):
        """**FETC:CRC:CURRATE?** - getResFcsCurRate command.
        Also used for:
        - FETC:FCS:CURRATE?
        - RES:CRC:CURRATE?
        - RES:FCS:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcsCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResFcsES(self, parameters):
        """**FETC:CRC:ES?** - getResFcsES command.
        Also used for:
        - FETC:FCS:ES?
        - RES:CRC:ES?
        - RES:FCS:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResFcsES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResHdrMMSecs(self, parameters):
        """**FETC:HDRMM:SECS?** - getResHdrMMSecs command.
        Also used for:
        - RES:HDRMM:SECS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %u
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResHdrMMSecs
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResHdrMMState(self, parameters):
        """**FETC:AL:HDRMM?** - getResHdrMMState command.
        Also used for:
        - FETC:HDRMM:STATE?
        - RES:AL:HDRMM?
        - RES:HDRMM:STATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %u
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResHdrMMState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResIcmpPackets(self, parameters):
        """**FETC:PACK:ICMP?** - getResIcmpPackets command.
        Also used for:
        - FETC:RXPACK:ICMP?
        - RES:PACK:ICMP?
        - RES:RXPACK:ICMP?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResIcmpPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResIgmpPackets(self, parameters):
        """**FETC:PACK:IGMP?** - getResIgmpPackets command.
        Also used for:
        - FETC:RXPACK:IGMP?
        - RES:PACK:IGMP?
        - RES:RXPACK:IGMP?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResIgmpPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResInvSuperAvgRate(self, parameters):
        """**FETC:INVSUPER:AVGRATE?** - getResInvSuperAvgRate command.
        Also used for:
        - RES:INVSUPER:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResInvSuperAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResInvSuperCount(self, parameters):
        """**FETC:INVSUPER:COUNT?** - getResInvSuperCount command.
        Also used for:
        - RES:INVSUPER:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResInvSuperCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResInvSuperCurRate(self, parameters):
        """**FETC:INVSUPER:CURRATE?** - getResInvSuperCurRate command.
        Also used for:
        - RES:INVSUPER:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResInvSuperCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResInvSuperES(self, parameters):
        """**FETC:INVSUPER:ES?** - getResInvSuperES command.
        Also used for:
        - RES:INVSUPER:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResInvSuperES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResIpChecksumAvgRate(self, parameters):
        """**FETC:IPCHECKSUM:AVGRATE?** - getResIpChecksumAvgRate command.
        Also used for:
        - RES:IPCHECKSUM:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResIpChecksumAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResIpChecksumCount(self, parameters):
        """**FETC:IPCHECKSUM:COUNT?** - getResIpChecksumCount command.
        Also used for:
        - RES:IPCHECKSUM:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResIpChecksumCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResIpChecksumCurRate(self, parameters):
        """**FETC:IPCHECKSUM:CURRATE?** - getResIpChecksumCurRate command.
        Also used for:
        - RES:IPCHECKSUM:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResIpChecksumCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResIpChecksumES(self, parameters):
        """**FETC:IPCHECKSUM:ES?** - getResIpChecksumES command.
        Also used for:
        - RES:IPCHECKSUM:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResIpChecksumES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResIpPackets(self, parameters):
        """**FETC:PACK:IP?** - getResIpPackets command.
        Also used for:
        - FETC:RXPACK:IPV4?
        - RES:PACK:IP?
        - RES:RXPACK:IPV4?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResIpPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResIpv6Packets(self, parameters):
        """**FETC:PACK:IPV6?** - getResIpv6Packets command.
        Also used for:
        - FETC:RXPACK:IPV6?
        - RES:PACK:IPV6?
        - RES:RXPACK:IPV6?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResIpv6Packets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2RxLinkKBPerSecAvgNone(self, parameters):
        """**FETC:UTIL:L2:AVG:RXMBPS?** - getResL2RxLinkKBPerSecAvgNone command.
        Also used for:
        - RES:UTIL:L2:AVG:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2RxLinkKBPerSecAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2RxLinkKBPerSecMaxNone(self, parameters):
        """**FETC:UTIL:L2:MAX:RXMBPS?** - getResL2RxLinkKBPerSecMaxNone command.
        Also used for:
        - RES:UTIL:L2:MAX:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2RxLinkKBPerSecMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2RxLinkKBPerSecMinNone(self, parameters):
        """**FETC:UTIL:L2:MIN:RXMBPS?** - getResL2RxLinkKBPerSecMinNone command.
        Also used for:
        - RES:UTIL:L2:MIN:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2RxLinkKBPerSecMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2RxLinkKBPerSecNone(self, parameters):
        """**FETC:UTIL:L2:CUR:RXMBPS?** - getResL2RxLinkKBPerSecNone command.
        Also used for:
        - RES:UTIL:L2:CUR:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2RxLinkKBPerSecNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2RxLinkPctBandwidthAvgNone(self, parameters):
        """**FETC:UTIL:L2:AVG:RXPCTBW?** - getResL2RxLinkPctBandwidthAvgNone command.
        Also used for:
        - RES:UTIL:L2:AVG:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2RxLinkPctBandwidthAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2RxLinkPctBandwidthMaxNone(self, parameters):
        """**FETC:UTIL:L2:MAX:RXPCTBW?** - getResL2RxLinkPctBandwidthMaxNone command.
        Also used for:
        - RES:UTIL:L2:MAX:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2RxLinkPctBandwidthMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2RxLinkPctBandwidthMinNone(self, parameters):
        """**FETC:UTIL:L2:MIN:RXPCTBW?** - getResL2RxLinkPctBandwidthMinNone command.
        Also used for:
        - RES:UTIL:L2:MIN:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2RxLinkPctBandwidthMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2RxLinkPctBandwidthNone(self, parameters):
        """**FETC:UTIL:L2:CUR:RXPCTBW?** - getResL2RxLinkPctBandwidthNone command.
        Also used for:
        - RES:UTIL:L2:CUR:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2RxLinkPctBandwidthNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2TxLinkKBPerSecAvgNone(self, parameters):
        """**FETC:UTIL:L2:AVG:TXMBPS?** - getResL2TxLinkKBPerSecAvgNone command.
        Also used for:
        - RES:UTIL:L2:AVG:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2TxLinkKBPerSecAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2TxLinkKBPerSecMaxNone(self, parameters):
        """**FETC:UTIL:L2:MAX:TXMBPS?** - getResL2TxLinkKBPerSecMaxNone command.
        Also used for:
        - RES:UTIL:L2:MAX:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2TxLinkKBPerSecMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2TxLinkKBPerSecMinNone(self, parameters):
        """**FETC:UTIL:L2:MIN:TXMBPS?** - getResL2TxLinkKBPerSecMinNone command.
        Also used for:
        - RES:UTIL:L2:MIN:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2TxLinkKBPerSecMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2TxLinkKBPerSecNone(self, parameters):
        """**FETC:UTIL:L2:CUR:TXMBPS?** - getResL2TxLinkKBPerSecNone command.
        Also used for:
        - RES:UTIL:L2:CUR:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2TxLinkKBPerSecNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2TxLinkPctBandwidthAvgNone(self, parameters):
        """**FETC:UTIL:L2:AVG:TXPCTBW?** - getResL2TxLinkPctBandwidthAvgNone command.
        Also used for:
        - RES:UTIL:L2:AVG:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2TxLinkPctBandwidthAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2TxLinkPctBandwidthMaxNone(self, parameters):
        """**FETC:UTIL:L2:MAX:TXPCTBW?** - getResL2TxLinkPctBandwidthMaxNone command.
        Also used for:
        - RES:UTIL:L2:MAX:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2TxLinkPctBandwidthMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2TxLinkPctBandwidthMinNone(self, parameters):
        """**FETC:UTIL:L2:MIN:TXPCTBW?** - getResL2TxLinkPctBandwidthMinNone command.
        Also used for:
        - RES:UTIL:L2:MIN:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2TxLinkPctBandwidthMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResL2TxLinkPctBandwidthNone(self, parameters):
        """**FETC:UTIL:L2:CUR:TXPCTBW?** - getResL2TxLinkPctBandwidthNone command.
        Also used for:
        - RES:UTIL:L2:CUR:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResL2TxLinkPctBandwidthNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLfdSecs(self, parameters):
        """**FETC:LFD:SECS?** - getResLfdSecs command.
        Also used for:
        - RES:LFD:SECS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %u
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResLfdSecs
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLfdState(self, parameters):
        """**FETC:AL:LFD?** - getResLfdState command.
        Also used for:
        - FETC:LFD:STATE?
        - RES:AL:LFD?
        - RES:LFD:STATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResLfdState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLinecodeAvgRate(self, parameters):
        """**FETC:LINECODE:AVGRATE?** - getResLinecodeAvgRate command.
        Also used for:
        - RES:LINECODE:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResLinecodeAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLinecodeCount(self, parameters):
        """**FETC:LINECODE:COUNT?** - getResLinecodeCount command.
        Also used for:
        - RES:LINECODE:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResLinecodeCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLinecodeCurRate(self, parameters):
        """**FETC:LINECODE:CURRATE?** - getResLinecodeCurRate command.
        Also used for:
        - RES:LINECODE:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResLinecodeCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLinecodeES(self, parameters):
        """**FETC:LINECODE:ES?** - getResLinecodeES command.
        Also used for:
        - RES:LINECODE:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResLinecodeES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLinkSecs(self, parameters):
        """**FETC:LINK:SECS?** - getResLinkSecs command.
        Also used for:
        - RES:LINK:SECS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %u
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResLinkSecs
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLinkState(self, parameters):
        """**FETC:AL:LINK?** - getResLinkState command.
        Also used for:
        - FETC:LINK:STATE?
        - RES:AL:LINK?
        - RES:LINK:STATE?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResLinkState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLinkStatus(self, parameters):
        """**FETC:LINK:STATUS?** - getResLinkStatus command.
        Also used for:
        - RES:LINK:STATUS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %u
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResLinkStatus
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLocSecs(self, parameters):
        """**FETC:LOCS:SECS?** - getResLocSecs command.
        Also used for:
        - RES:LOCS:SECS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %u
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResLocSecs
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLocState(self, parameters):
        """**FETC:AL:LOC?** - getResLocState command.
        Also used for:
        - FETC:LOCS:STATE?
        - RES:AL:LOC?
        - RES:LOCS:STATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResLocState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLoccsSecs(self, parameters):
        """**FETC:LOCCS:SECS?** - getResLoccsSecs command.
        Also used for:
        - RES:LOCCS:SECS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %u
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResLoccsSecs
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLoccsState(self, parameters):
        """**FETC:AL:LOCCS?** - getResLoccsState command.
        Also used for:
        - FETC:LOCCS:STATE?
        - RES:AL:LOCCS?
        - RES:LOCCS:STATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %u
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResLoccsState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLosSecs(self, parameters):
        """**FETC:LOS:SECS?** - getResLosSecs command.
        Also used for:
        - RES:LOS:SECS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %u
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResLosSecs
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResLosState(self, parameters):
        """**FETC:AL:LOS?** - getResLosState command.
        Also used for:
        - FETC:LOS:STATE?
        - RES:AL:LOS?
        - RES:LOS:STATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %u
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResLosState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResMplsPackets(self, parameters):
        """**FETC:PACK:MPLS?** - getResMplsPackets command.
        Also used for:
        - FETC:RXPACK:MPLS?
        - RES:PACK:MPLS?
        - RES:RXPACK:MPLS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResMplsPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResMplsPacketsByLevel(self, parameters):
        """**FETC:MPLS:PACKETS?** - getResMplsPacketsByLevel command.
        Also used for:
        - FETC:RXPACK:MPLS:TAG?
        - RES:MPLS:PACKETS?
        - RES:RXPACK:MPLS:TAG?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResMplsPacketsByLevel
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResMplsTC(self, parameters):
        """**FETC:MPLS:TC?** - getResMplsTC command.
        Also used for:
        - FETC:RXPACK:MPLS:TC?
        - RES:MPLS:TC?
        - RES:RXPACK:MPLS:TC?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResMplsTC
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResOspfPackets(self, parameters):
        """**FETC:PACK:OSPF?** - getResOspfPackets command.
        Also used for:
        - FETC:RXPACK:OSPF?
        - RES:PACK:OSPF?
        - RES:RXPACK:OSPF?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResOspfPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResOversizedAvgRate(self, parameters):
        """**FETC:OVERSIZED:AVGRATE?** - getResOversizedAvgRate command.
        Also used for:
        - RES:OVERSIZED:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResOversizedAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResOversizedCurRate(self, parameters):
        """**FETC:OVERSIZED:CURRATE?** - getResOversizedCurRate command.
        Also used for:
        - RES:OVERSIZED:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResOversizedCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResOversizedES(self, parameters):
        """**FETC:OVERSIZED:ES?** - getResOversizedES command.
        Also used for:
        - RES:OVERSIZED:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResOversizedES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResPauseEndPackets(self, parameters):
        """**FETC:PAUSE:ENDPACKETS?** - getResPauseEndPackets command.
        Also used for:
        - FETC:PAUSED:ENDPACKETS?
        - FETC:RXPACK:PAUSE:ENDPACKETS?
        - RES:PAUSE:ENDPACKETS?
        - RES:PAUSED:ENDPACKETS?
        - RES:RXPACK:PAUSE:ENDPACKETS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResPauseEndPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResPausePackets(self, parameters):
        """**FETC:PAUSE:PACKETS?** - getResPausePackets command.
        Also used for:
        - FETC:PAUSED:PACKETS?
        - FETC:RXPACK:PAUSE:PACKETS?
        - RES:PAUSE:PACKETS?
        - RES:PAUSED:PACKETS?
        - RES:RXPACK:PAUSE:PACKETS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResPausePackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResPauseQuantas(self, parameters):
        """**FETC:PAUSE:QUANTAS?** - getResPauseQuantas command.
        Also used for:
        - FETC:PAUSED:QUANTAS?
        - FETC:RXPACK:PAUSE:QUANT?
        - RES:PAUSE:QUANTAS?
        - RES:PAUSED:QUANTAS?
        - RES:RXPACK:PAUSE:QUANT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResPauseQuantas
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResPauseSecs(self, parameters):
        """**FETC:PAUSE:SECS?** - getResPauseSecs command.
        Also used for:
        - FETC:PAUSED:SECS?
        - RES:PAUSE:SECS?
        - RES:PAUSED:SECS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResPauseSecs
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResPauseState(self, parameters):
        """**FETC:PAUSE:STATE?** - getResPauseState command.
        Also used for:
        - FETC:PAUSED:STATE?
        - RES:PAUSE:STATE?
        - RES:PAUSED:STATE?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResPauseState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResPfcsAvgRate(self, parameters):
        """**FETC:PFCS:AVGRATE?** - getResPfcsAvgRate command.
        Also used for:
        - RES:PFCS:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResPfcsAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResPfcsCount(self, parameters):
        """**FETC:PFCS:COUNT?** - getResPfcsCount command.
        Also used for:
        - RES:PFCS:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResPfcsCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResPfcsCurRate(self, parameters):
        """**FETC:PFCS:CURRATE?** - getResPfcsCurRate command.
        Also used for:
        - RES:PFCS:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResPfcsCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResPfcsES(self, parameters):
        """**FETC:PFCS:ES?** - getResPfcsES command.
        Also used for:
        - RES:PFCS:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResPfcsES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRuntAvgRate(self, parameters):
        """**FETC:RUNT:AVGRATE?** - getResRuntAvgRate command.
        Also used for:
        - RES:RUNT:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResRuntAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRuntCount(self, parameters):
        """**FETC:RUNT:COUNT?** - getResRuntCount command.
        Also used for:
        - RES:RUNT:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResRuntCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRuntCurRate(self, parameters):
        """**FETC:RUNT:CURRATE?** - getResRuntCurRate command.
        Also used for:
        - RES:RUNT:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResRuntCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRuntES(self, parameters):
        """**FETC:RUNT:ES?** - getResRuntES command.
        Also used for:
        - RES:RUNT:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResRuntES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecAvgIpv4(self, parameters):
        """**FETC:UTIL:IPV4:AVG:RXMBPS?** - getResRxLinkKBPerSecAvgIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:AVG:RXMBPS?
        - RES:UTIL:IPV4:AVG:RXMBPS?
        - RES:UTIL:L1:IPV4:AVG:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecAvgIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecAvgIpv6(self, parameters):
        """**FETC:UTIL:IPV6:AVG:RXMBPS?** - getResRxLinkKBPerSecAvgIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:AVG:RXMBPS?
        - RES:UTIL:IPV6:AVG:RXMBPS?
        - RES:UTIL:L1:IPV6:AVG:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecAvgIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecAvgMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:AVG:RXMBPS?** - getResRxLinkKBPerSecAvgMpls command.
        Also used for:
        - FETC:UTIL:MPLS:AVG:RXMBPS?
        - RES:UTIL:L1:MPLS:AVG:RXMBPS?
        - RES:UTIL:MPLS:AVG:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecAvgMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecAvgNone(self, parameters):
        """**FETC:UTIL:AVG:RXMBPS?** - getResRxLinkKBPerSecAvgNone command.
        Also used for:
        - FETC:UTIL:L1:AVG:RXMBPS?
        - RES:UTIL:AVG:RXMBPS?
        - RES:UTIL:L1:AVG:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecAvgVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:AVG:RXMBPS?** - getResRxLinkKBPerSecAvgVlan command.
        Also used for:
        - FETC:UTIL:VLAN:AVG:RXMBPS?
        - RES:UTIL:L1:VLAN:AVG:RXMBPS?
        - RES:UTIL:VLAN:AVG:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecAvgVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecIpv4(self, parameters):
        """**FETC:UTIL:IPV4:CUR:RXMBPS?** - getResRxLinkKBPerSecIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:CUR:RXMBPS?
        - RES:UTIL:IPV4:CUR:RXMBPS?
        - RES:UTIL:L1:IPV4:CUR:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecIpv6(self, parameters):
        """**FETC:UTIL:IPV6:CUR:RXMBPS?** - getResRxLinkKBPerSecIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:CUR:RXMBPS?
        - RES:UTIL:IPV6:CUR:RXMBPS?
        - RES:UTIL:L1:IPV6:CUR:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecMaxIpv4(self, parameters):
        """**FETC:UTIL:IPV4:MAX:RXMBPS?** - getResRxLinkKBPerSecMaxIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:MAX:RXMBPS?
        - RES:UTIL:IPV4:MAX:RXMBPS?
        - RES:UTIL:L1:IPV4:MAX:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecMaxIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecMaxIpv6(self, parameters):
        """**FETC:UTIL:IPV6:MAX:RXMBPS?** - getResRxLinkKBPerSecMaxIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:MAX:RXMBPS?
        - RES:UTIL:IPV6:MAX:RXMBPS?
        - RES:UTIL:L1:IPV6:MAX:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecMaxIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecMaxMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:MAX:RXMBPS?** - getResRxLinkKBPerSecMaxMpls command.
        Also used for:
        - FETC:UTIL:MPLS:MAX:RXMBPS?
        - RES:UTIL:L1:MPLS:MAX:RXMBPS?
        - RES:UTIL:MPLS:MAX:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecMaxMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecMaxNone(self, parameters):
        """**FETC:UTIL:L1:MAX:RXMBPS?** - getResRxLinkKBPerSecMaxNone command.
        Also used for:
        - FETC:UTIL:MAX:RXMBPS?
        - RES:UTIL:L1:MAX:RXMBPS?
        - RES:UTIL:MAX:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecMaxVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:MAX:RXMBPS?** - getResRxLinkKBPerSecMaxVlan command.
        Also used for:
        - FETC:UTIL:VLAN:MAX:RXMBPS?
        - RES:UTIL:L1:VLAN:MAX:RXMBPS?
        - RES:UTIL:VLAN:MAX:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecMaxVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecMinIpv4(self, parameters):
        """**FETC:UTIL:IPV4:MIN:RXMBPS?** - getResRxLinkKBPerSecMinIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:MIN:RXMBPS?
        - RES:UTIL:IPV4:MIN:RXMBPS?
        - RES:UTIL:L1:IPV4:MIN:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecMinIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecMinIpv6(self, parameters):
        """**FETC:UTIL:IPV6:MIN:RXMBPS?** - getResRxLinkKBPerSecMinIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:MIN:RXMBPS?
        - RES:UTIL:IPV6:MIN:RXMBPS?
        - RES:UTIL:L1:IPV6:MIN:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecMinIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecMinMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:MIN:RXMBPS?** - getResRxLinkKBPerSecMinMpls command.
        Also used for:
        - FETC:UTIL:MPLS:MIN:RXMBPS?
        - RES:UTIL:L1:MPLS:MIN:RXMBPS?
        - RES:UTIL:MPLS:MIN:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecMinMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecMinNone(self, parameters):
        """**FETC:UTIL:L1:MIN:RXMBPS?** - getResRxLinkKBPerSecMinNone command.
        Also used for:
        - FETC:UTIL:MIN:RXMBPS?
        - RES:UTIL:L1:MIN:RXMBPS?
        - RES:UTIL:MIN:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecMinVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:MIN:RXMBPS?** - getResRxLinkKBPerSecMinVlan command.
        Also used for:
        - FETC:UTIL:VLAN:MIN:RXMBPS?
        - RES:UTIL:L1:VLAN:MIN:RXMBPS?
        - RES:UTIL:VLAN:MIN:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecMinVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:CUR:RXMBPS?** - getResRxLinkKBPerSecMpls command.
        Also used for:
        - FETC:UTIL:MPLS:CUR:RXMBPS?
        - RES:UTIL:L1:MPLS:CUR:RXMBPS?
        - RES:UTIL:MPLS:CUR:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkKBPerSecVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:CUR:RXMBPS?** - getResRxLinkKBPerSecVlan command.
        Also used for:
        - FETC:UTIL:VLAN:CUR:RXMBPS?
        - RES:UTIL:L1:VLAN:CUR:RXMBPS?
        - RES:UTIL:VLAN:CUR:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkKBPerSecVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecAvgIpv4(self, parameters):
        """**FETC:UTIL:IPV4:AVG:RXPPS?** - getResRxLinkPacketPerSecAvgIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:AVG:RXPPS?
        - RES:UTIL:IPV4:AVG:RXPPS?
        - RES:UTIL:L1:IPV4:AVG:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecAvgIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecAvgIpv6(self, parameters):
        """**FETC:UTIL:IPV6:AVG:RXPPS?** - getResRxLinkPacketPerSecAvgIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:AVG:RXPPS?
        - RES:UTIL:IPV6:AVG:RXPPS?
        - RES:UTIL:L1:IPV6:AVG:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecAvgIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecAvgMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:AVG:RXPPS?** - getResRxLinkPacketPerSecAvgMpls command.
        Also used for:
        - FETC:UTIL:MPLS:AVG:RXPPS?
        - RES:UTIL:L1:MPLS:AVG:RXPPS?
        - RES:UTIL:MPLS:AVG:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecAvgMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecAvgNone(self, parameters):
        """**FETC:UTIL:AVG:RXPPS?** - getResRxLinkPacketPerSecAvgNone command.
        Also used for:
        - FETC:UTIL:L1:AVG:RXPPS?
        - RES:UTIL:AVG:RXPPS?
        - RES:UTIL:L1:AVG:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecAvgVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:AVG:RXPPS?** - getResRxLinkPacketPerSecAvgVlan command.
        Also used for:
        - FETC:UTIL:VLAN:AVG:RXPPS?
        - RES:UTIL:L1:VLAN:AVG:RXPPS?
        - RES:UTIL:VLAN:AVG:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecAvgVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecIpv4(self, parameters):
        """**FETC:UTIL:IPV4:CUR:RXPPS?** - getResRxLinkPacketPerSecIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:CUR:RXPPS?
        - RES:UTIL:IPV4:CUR:RXPPS?
        - RES:UTIL:L1:IPV4:CUR:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecIpv6(self, parameters):
        """**FETC:UTIL:IPV6:CUR:RXPPS?** - getResRxLinkPacketPerSecIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:CUR:RXPPS?
        - RES:UTIL:IPV6:CUR:RXPPS?
        - RES:UTIL:L1:IPV6:CUR:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecMaxIpv4(self, parameters):
        """**FETC:UTIL:IPV4:MAX:RXPPS?** - getResRxLinkPacketPerSecMaxIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:MAX:RXPPS?
        - RES:UTIL:IPV4:MAX:RXPPS?
        - RES:UTIL:L1:IPV4:MAX:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecMaxIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecMaxIpv6(self, parameters):
        """**FETC:UTIL:IPV6:MAX:RXPPS?** - getResRxLinkPacketPerSecMaxIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:MAX:RXPPS?
        - RES:UTIL:IPV6:MAX:RXPPS?
        - RES:UTIL:L1:IPV6:MAX:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecMaxIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecMaxMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:MAX:RXPPS?** - getResRxLinkPacketPerSecMaxMpls command.
        Also used for:
        - FETC:UTIL:MPLS:MAX:RXPPS?
        - RES:UTIL:L1:MPLS:MAX:RXPPS?
        - RES:UTIL:MPLS:MAX:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecMaxMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecMaxNone(self, parameters):
        """**FETC:UTIL:L1:MAX:RXPPS?** - getResRxLinkPacketPerSecMaxNone command.
        Also used for:
        - FETC:UTIL:MAX:RXPPS?
        - RES:UTIL:L1:MAX:RXPPS?
        - RES:UTIL:MAX:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecMaxVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:MAX:RXPPS?** - getResRxLinkPacketPerSecMaxVlan command.
        Also used for:
        - FETC:UTIL:VLAN:MAX:RXPPS?
        - RES:UTIL:L1:VLAN:MAX:RXPPS?
        - RES:UTIL:VLAN:MAX:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecMaxVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecMinIpv4(self, parameters):
        """**FETC:UTIL:IPV4:MIN:RXPPS?** - getResRxLinkPacketPerSecMinIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:MIN:RXPPS?
        - RES:UTIL:IPV4:MIN:RXPPS?
        - RES:UTIL:L1:IPV4:MIN:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecMinIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecMinIpv6(self, parameters):
        """**FETC:UTIL:IPV6:MIN:RXPPS?** - getResRxLinkPacketPerSecMinIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:MIN:RXPPS?
        - RES:UTIL:IPV6:MIN:RXPPS?
        - RES:UTIL:L1:IPV6:MIN:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecMinIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecMinMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:MIN:RXPPS?** - getResRxLinkPacketPerSecMinMpls command.
        Also used for:
        - FETC:UTIL:MPLS:MIN:RXPPS?
        - RES:UTIL:L1:MPLS:MIN:RXPPS?
        - RES:UTIL:MPLS:MIN:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecMinMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecMinNone(self, parameters):
        """**FETC:UTIL:L1:MIN:RXPPS?** - getResRxLinkPacketPerSecMinNone command.
        Also used for:
        - FETC:UTIL:MIN:RXPPS?
        - RES:UTIL:L1:MIN:RXPPS?
        - RES:UTIL:MIN:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecMinVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:MIN:RXPPS?** - getResRxLinkPacketPerSecMinVlan command.
        Also used for:
        - FETC:UTIL:VLAN:MIN:RXPPS?
        - RES:UTIL:L1:VLAN:MIN:RXPPS?
        - RES:UTIL:VLAN:MIN:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecMinVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:CUR:RXPPS?** - getResRxLinkPacketPerSecMpls command.
        Also used for:
        - FETC:UTIL:MPLS:CUR:RXPPS?
        - RES:UTIL:L1:MPLS:CUR:RXPPS?
        - RES:UTIL:MPLS:CUR:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPacketPerSecVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:CUR:RXPPS?** - getResRxLinkPacketPerSecVlan command.
        Also used for:
        - FETC:UTIL:VLAN:CUR:RXPPS?
        - RES:UTIL:L1:VLAN:CUR:RXPPS?
        - RES:UTIL:VLAN:CUR:RXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPacketPerSecVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthAvgIpv4(self, parameters):
        """**FETC:UTIL:IPV4:AVG:RXPCTBW?** - getResRxLinkPctBandwidthAvgIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:AVG:RXPCTBW?
        - RES:UTIL:IPV4:AVG:RXPCTBW?
        - RES:UTIL:L1:IPV4:AVG:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthAvgIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthAvgIpv6(self, parameters):
        """**FETC:UTIL:IPV6:AVG:RXPCTBW?** - getResRxLinkPctBandwidthAvgIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:AVG:RXPCTBW?
        - RES:UTIL:IPV6:AVG:RXPCTBW?
        - RES:UTIL:L1:IPV6:AVG:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthAvgIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthAvgMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:AVG:RXPCTBW?** - getResRxLinkPctBandwidthAvgMpls command.
        Also used for:
        - FETC:UTIL:MPLS:AVG:RXPCTBW?
        - RES:UTIL:L1:MPLS:AVG:RXPCTBW?
        - RES:UTIL:MPLS:AVG:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthAvgMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthAvgNone(self, parameters):
        """**FETC:UTIL:AVG:RXPCTBW?** - getResRxLinkPctBandwidthAvgNone command.
        Also used for:
        - FETC:UTIL:L1:AVG:RXPCTBW?
        - RES:UTIL:AVG:RXPCTBW?
        - RES:UTIL:L1:AVG:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthAvgVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:AVG:RXPCTBW?** - getResRxLinkPctBandwidthAvgVlan command.
        Also used for:
        - FETC:UTIL:VLAN:AVG:RXPCTBW?
        - RES:UTIL:L1:VLAN:AVG:RXPCTBW?
        - RES:UTIL:VLAN:AVG:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthAvgVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthIpv4(self, parameters):
        """**FETC:UTIL:IPV4:CUR:RXPCTBW?** - getResRxLinkPctBandwidthIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:CUR:RXPCTBW?
        - RES:UTIL:IPV4:CUR:RXPCTBW?
        - RES:UTIL:L1:IPV4:CUR:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthIpv6(self, parameters):
        """**FETC:UTIL:IPV6:CUR:RXPCTBW?** - getResRxLinkPctBandwidthIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:CUR:RXPCTBW?
        - RES:UTIL:IPV6:CUR:RXPCTBW?
        - RES:UTIL:L1:IPV6:CUR:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthMaxIpv4(self, parameters):
        """**FETC:UTIL:IPV4:MAX:RXPCTBW?** - getResRxLinkPctBandwidthMaxIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:MAX:RXPCTBW?
        - RES:UTIL:IPV4:MAX:RXPCTBW?
        - RES:UTIL:L1:IPV4:MAX:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthMaxIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthMaxIpv6(self, parameters):
        """**FETC:UTIL:IPV6:MAX:RXPCTBW?** - getResRxLinkPctBandwidthMaxIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:MAX:RXPCTBW?
        - RES:UTIL:IPV6:MAX:RXPCTBW?
        - RES:UTIL:L1:IPV6:MAX:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthMaxIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthMaxMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:MAX:RXPCTBW?** - getResRxLinkPctBandwidthMaxMpls command.
        Also used for:
        - FETC:UTIL:MPLS:MAX:RXPCTBW?
        - RES:UTIL:L1:MPLS:MAX:RXPCTBW?
        - RES:UTIL:MPLS:MAX:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthMaxMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthMaxNone(self, parameters):
        """**FETC:UTIL:L1:MAX:RXPCTBW?** - getResRxLinkPctBandwidthMaxNone command.
        Also used for:
        - FETC:UTIL:MAX:RXPCTBW?
        - RES:UTIL:L1:MAX:RXPCTBW?
        - RES:UTIL:MAX:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthMaxVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:MAX:RXPCTBW?** - getResRxLinkPctBandwidthMaxVlan command.
        Also used for:
        - FETC:UTIL:VLAN:MAX:RXPCTBW?
        - RES:UTIL:L1:VLAN:MAX:RXPCTBW?
        - RES:UTIL:VLAN:MAX:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthMaxVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthMinIpv4(self, parameters):
        """**FETC:UTIL:IPV4:MIN:RXPCTBW?** - getResRxLinkPctBandwidthMinIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:MIN:RXPCTBW?
        - RES:UTIL:IPV4:MIN:RXPCTBW?
        - RES:UTIL:L1:IPV4:MIN:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthMinIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthMinIpv6(self, parameters):
        """**FETC:UTIL:IPV6:MIN:RXPCTBW?** - getResRxLinkPctBandwidthMinIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:MIN:RXPCTBW?
        - RES:UTIL:IPV6:MIN:RXPCTBW?
        - RES:UTIL:L1:IPV6:MIN:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthMinIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthMinMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:MIN:RXPCTBW?** - getResRxLinkPctBandwidthMinMpls command.
        Also used for:
        - FETC:UTIL:MPLS:MIN:RXPCTBW?
        - RES:UTIL:L1:MPLS:MIN:RXPCTBW?
        - RES:UTIL:MPLS:MIN:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthMinMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthMinNone(self, parameters):
        """**FETC:UTIL:L1:MIN:RXPCTBW?** - getResRxLinkPctBandwidthMinNone command.
        Also used for:
        - FETC:UTIL:MIN:RXPCTBW?
        - RES:UTIL:L1:MIN:RXPCTBW?
        - RES:UTIL:MIN:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthMinVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:MIN:RXPCTBW?** - getResRxLinkPctBandwidthMinVlan command.
        Also used for:
        - FETC:UTIL:VLAN:MIN:RXPCTBW?
        - RES:UTIL:L1:VLAN:MIN:RXPCTBW?
        - RES:UTIL:VLAN:MIN:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthMinVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:CUR:RXPCTBW?** - getResRxLinkPctBandwidthMpls command.
        Also used for:
        - FETC:UTIL:MPLS:CUR:RXPCTBW?
        - RES:UTIL:L1:MPLS:CUR:RXPCTBW?
        - RES:UTIL:MPLS:CUR:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResRxLinkPctBandwidthVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:CUR:RXPCTBW?** - getResRxLinkPctBandwidthVlan command.
        Also used for:
        - FETC:UTIL:VLAN:CUR:RXPCTBW?
        - RES:UTIL:L1:VLAN:CUR:RXPCTBW?
        - RES:UTIL:VLAN:CUR:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResRxLinkPctBandwidthVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResSfcsAvgRate(self, parameters):
        """**FETC:SFCS:AVGRATE?** - getResSfcsAvgRate command.
        Also used for:
        - RES:SFCS:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResSfcsAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResSfcsCount(self, parameters):
        """**FETC:SFCS:COUNT?** - getResSfcsCount command.
        Also used for:
        - RES:SFCS:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResSfcsCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResSfcsCurRate(self, parameters):
        """**FETC:SFCS:CURRATE?** - getResSfcsCurRate command.
        Also used for:
        - RES:SFCS:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResSfcsCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResSfcsES(self, parameters):
        """**FETC:SFCS:ES?** - getResSfcsES command.
        Also used for:
        - RES:SFCS:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResSfcsES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResSummaryModuleState(self, parameters):
        """**FETC:AL:MODULESTATUS?** - getResSummaryModuleState command.
        Also used for:
        - RES:AL:MODULESTATUS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResSummaryModuleState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResSyncHdrAvgRate(self, parameters):
        """**FETC:SYNCHDR:AVGRATE?** - getResSyncHdrAvgRate command.
        Also used for:
        - RES:SYNCHDR:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResSyncHdrAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResSyncHdrCount(self, parameters):
        """**FETC:SYNCHDR:COUNT?** - getResSyncHdrCount command.
        Also used for:
        - RES:SYNCHDR:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResSyncHdrCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResSyncHdrCurRate(self, parameters):
        """**FETC:SYNCHDR:CURRATE?** - getResSyncHdrCurRate command.
        Also used for:
        - RES:SYNCHDR:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResSyncHdrCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResSyncHdrES(self, parameters):
        """**FETC:SYNCHDR:ES?** - getResSyncHdrES command.
        Also used for:
        - RES:SYNCHDR:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResSyncHdrES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTcpChecksumAvgRate(self, parameters):
        """**FETC:TCPERR:AVGRATE?** - getResTcpChecksumAvgRate command.
        Also used for:
        - RES:TCPERR:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResTcpChecksumAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTcpChecksumCount(self, parameters):
        """**FETC:TCPERR:COUNT?** - getResTcpChecksumCount command.
        Also used for:
        - RES:TCPERR:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResTcpChecksumCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTcpChecksumCurRate(self, parameters):
        """**FETC:TCPERR:CURRATE?** - getResTcpChecksumCurRate command.
        Also used for:
        - RES:TCPERR:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResTcpChecksumCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTcpChecksumES(self, parameters):
        """**FETC:TCPERR:ES?** - getResTcpChecksumES command.
        Also used for:
        - RES:TCPERR:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResTcpChecksumES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTcpPackets(self, parameters):
        """**FETC:PACK:TCP?** - getResTcpPackets command.
        Also used for:
        - FETC:RXPACK:TCP?
        - RES:PACK:TCP?
        - RES:RXPACK:TCP?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResTcpPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxIpPackets(self, parameters):
        """**FETC:TXPACK:IP?** - getResTxIpPackets command.
        Also used for:
        - FETC:TXPACK:IPV4?
        - RES:TXPACK:IP?
        - RES:TXPACK:IPV4?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResTxIpPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxIpv6Packets(self, parameters):
        """**FETC:TXPACK:IPV6?** - getResTxIpv6Packets command.
        Also used for:
        - RES:TXPACK:IPV6?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResTxIpv6Packets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecAvgIpv4(self, parameters):
        """**FETC:UTIL:IPV4:AVG:TXMBPS?** - getResTxLinkKBPerSecAvgIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:AVG:TXMBPS?
        - RES:UTIL:IPV4:AVG:TXMBPS?
        - RES:UTIL:L1:IPV4:AVG:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecAvgIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecAvgIpv6(self, parameters):
        """**FETC:UTIL:IPV6:AVG:TXMBPS?** - getResTxLinkKBPerSecAvgIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:AVG:TXMBPS?
        - RES:UTIL:IPV6:AVG:TXMBPS?
        - RES:UTIL:L1:IPV6:AVG:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecAvgIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecAvgMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:AVG:TXMBPS?** - getResTxLinkKBPerSecAvgMpls command.
        Also used for:
        - FETC:UTIL:MPLS:AVG:TXMBPS?
        - RES:UTIL:L1:MPLS:AVG:TXMBPS?
        - RES:UTIL:MPLS:AVG:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecAvgMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecAvgNone(self, parameters):
        """**FETC:UTIL:AVG:TXMBPS?** - getResTxLinkKBPerSecAvgNone command.
        Also used for:
        - FETC:UTIL:L1:AVG:TXMBPS?
        - RES:UTIL:AVG:TXMBPS?
        - RES:UTIL:L1:AVG:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecAvgVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:AVG:TXMBPS?** - getResTxLinkKBPerSecAvgVlan command.
        Also used for:
        - FETC:UTIL:VLAN:AVG:TXMBPS?
        - RES:UTIL:L1:VLAN:AVG:TXMBPS?
        - RES:UTIL:VLAN:AVG:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecAvgVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecIpv4(self, parameters):
        """**FETC:UTIL:IPV4:CUR:TXMBPS?** - getResTxLinkKBPerSecIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:CUR:TXMBPS?
        - RES:UTIL:IPV4:CUR:TXMBPS?
        - RES:UTIL:L1:IPV4:CUR:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecIpv6(self, parameters):
        """**FETC:UTIL:IPV6:CUR:TXMBPS?** - getResTxLinkKBPerSecIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:CUR:TXMBPS?
        - RES:UTIL:IPV6:CUR:TXMBPS?
        - RES:UTIL:L1:IPV6:CUR:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecMaxIpv4(self, parameters):
        """**FETC:UTIL:IPV4:MAX:TXMBPS?** - getResTxLinkKBPerSecMaxIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:MAX:TXMBPS?
        - RES:UTIL:IPV4:MAX:TXMBPS?
        - RES:UTIL:L1:IPV4:MAX:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecMaxIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecMaxIpv6(self, parameters):
        """**FETC:UTIL:IPV6:MAX:TXMBPS?** - getResTxLinkKBPerSecMaxIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:MAX:TXMBPS?
        - RES:UTIL:IPV6:MAX:TXMBPS?
        - RES:UTIL:L1:IPV6:MAX:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecMaxIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecMaxMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:MAX:TXMBPS?** - getResTxLinkKBPerSecMaxMpls command.
        Also used for:
        - FETC:UTIL:MPLS:MAX:TXMBPS?
        - RES:UTIL:L1:MPLS:MAX:TXMBPS?
        - RES:UTIL:MPLS:MAX:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecMaxMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecMaxNone(self, parameters):
        """**FETC:UTIL:L1:MAX:TXMBPS?** - getResTxLinkKBPerSecMaxNone command.
        Also used for:
        - FETC:UTIL:MAX:TXMBPS?
        - RES:UTIL:L1:MAX:TXMBPS?
        - RES:UTIL:MAX:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecMaxVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:MAX:TXMBPS?** - getResTxLinkKBPerSecMaxVlan command.
        Also used for:
        - FETC:UTIL:VLAN:MAX:TXMBPS?
        - RES:UTIL:L1:VLAN:MAX:TXMBPS?
        - RES:UTIL:VLAN:MAX:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecMaxVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecMinIpv4(self, parameters):
        """**FETC:UTIL:IPV4:MIN:TXMBPS?** - getResTxLinkKBPerSecMinIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:MIN:TXMBPS?
        - RES:UTIL:IPV4:MIN:TXMBPS?
        - RES:UTIL:L1:IPV4:MIN:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecMinIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecMinIpv6(self, parameters):
        """**FETC:UTIL:IPV6:MIN:TXMBPS?** - getResTxLinkKBPerSecMinIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:MIN:TXMBPS?
        - RES:UTIL:IPV6:MIN:TXMBPS?
        - RES:UTIL:L1:IPV6:MIN:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecMinIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecMinMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:MIN:TXMBPS?** - getResTxLinkKBPerSecMinMpls command.
        Also used for:
        - FETC:UTIL:MPLS:MIN:TXMBPS?
        - RES:UTIL:L1:MPLS:MIN:TXMBPS?
        - RES:UTIL:MPLS:MIN:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecMinMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecMinNone(self, parameters):
        """**FETC:UTIL:L1:MIN:TXMBPS?** - getResTxLinkKBPerSecMinNone command.
        Also used for:
        - FETC:UTIL:MIN:TXMBPS?
        - RES:UTIL:L1:MIN:TXMBPS?
        - RES:UTIL:MIN:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecMinVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:MIN:TXMBPS?** - getResTxLinkKBPerSecMinVlan command.
        Also used for:
        - FETC:UTIL:VLAN:MIN:TXMBPS?
        - RES:UTIL:L1:VLAN:MIN:TXMBPS?
        - RES:UTIL:VLAN:MIN:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecMinVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:CUR:TXMBPS?** - getResTxLinkKBPerSecMpls command.
        Also used for:
        - FETC:UTIL:MPLS:CUR:TXMBPS?
        - RES:UTIL:L1:MPLS:CUR:TXMBPS?
        - RES:UTIL:MPLS:CUR:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkKBPerSecVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:CUR:TXMBPS?** - getResTxLinkKBPerSecVlan command.
        Also used for:
        - FETC:UTIL:VLAN:CUR:TXMBPS?
        - RES:UTIL:L1:VLAN:CUR:TXMBPS?
        - RES:UTIL:VLAN:CUR:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkKBPerSecVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecAvgIpv4(self, parameters):
        """**FETC:UTIL:IPV4:AVG:TXPPS?** - getResTxLinkPacketPerSecAvgIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:AVG:TXPPS?
        - RES:UTIL:IPV4:AVG:TXPPS?
        - RES:UTIL:L1:IPV4:AVG:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecAvgIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecAvgIpv6(self, parameters):
        """**FETC:UTIL:IPV6:AVG:TXPPS?** - getResTxLinkPacketPerSecAvgIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:AVG:TXPPS?
        - RES:UTIL:IPV6:AVG:TXPPS?
        - RES:UTIL:L1:IPV6:AVG:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecAvgIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecAvgMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:AVG:TXPPS?** - getResTxLinkPacketPerSecAvgMpls command.
        Also used for:
        - FETC:UTIL:MPLS:AVG:TXPPS?
        - RES:UTIL:L1:MPLS:AVG:TXPPS?
        - RES:UTIL:MPLS:AVG:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecAvgMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecAvgNone(self, parameters):
        """**FETC:UTIL:AVG:TXPPS?** - getResTxLinkPacketPerSecAvgNone command.
        Also used for:
        - FETC:UTIL:L1:AVG:TXPPS?
        - RES:UTIL:AVG:TXPPS?
        - RES:UTIL:L1:AVG:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecAvgVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:AVG:TXPPS?** - getResTxLinkPacketPerSecAvgVlan command.
        Also used for:
        - FETC:UTIL:VLAN:AVG:TXPPS?
        - RES:UTIL:L1:VLAN:AVG:TXPPS?
        - RES:UTIL:VLAN:AVG:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecAvgVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecIpv4(self, parameters):
        """**FETC:UTIL:IPV4:CUR:TXPPS?** - getResTxLinkPacketPerSecIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:CUR:TXPPS?
        - RES:UTIL:IPV4:CUR:TXPPS?
        - RES:UTIL:L1:IPV4:CUR:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecIpv6(self, parameters):
        """**FETC:UTIL:IPV6:CUR:TXPPS?** - getResTxLinkPacketPerSecIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:CUR:TXPPS?
        - RES:UTIL:IPV6:CUR:TXPPS?
        - RES:UTIL:L1:IPV6:CUR:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecMaxIpv4(self, parameters):
        """**FETC:UTIL:IPV4:MAX:TXPPS?** - getResTxLinkPacketPerSecMaxIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:MAX:TXPPS?
        - RES:UTIL:IPV4:MAX:TXPPS?
        - RES:UTIL:L1:IPV4:MAX:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecMaxIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecMaxIpv6(self, parameters):
        """**FETC:UTIL:IPV6:MAX:TXPPS?** - getResTxLinkPacketPerSecMaxIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:MAX:TXPPS?
        - RES:UTIL:IPV6:MAX:TXPPS?
        - RES:UTIL:L1:IPV6:MAX:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecMaxIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecMaxMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:MAX:TXPPS?** - getResTxLinkPacketPerSecMaxMpls command.
        Also used for:
        - FETC:UTIL:MPLS:MAX:TXPPS?
        - RES:UTIL:L1:MPLS:MAX:TXPPS?
        - RES:UTIL:MPLS:MAX:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecMaxMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecMaxNone(self, parameters):
        """**FETC:UTIL:L1:MAX:TXPPS?** - getResTxLinkPacketPerSecMaxNone command.
        Also used for:
        - FETC:UTIL:MAX:TXPPS?
        - RES:UTIL:L1:MAX:TXPPS?
        - RES:UTIL:MAX:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecMaxVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:MAX:TXPPS?** - getResTxLinkPacketPerSecMaxVlan command.
        Also used for:
        - FETC:UTIL:VLAN:MAX:TXPPS?
        - RES:UTIL:L1:VLAN:MAX:TXPPS?
        - RES:UTIL:VLAN:MAX:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecMaxVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecMinIpv4(self, parameters):
        """**FETC:UTIL:IPV4:MIN:TXPPS?** - getResTxLinkPacketPerSecMinIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:MIN:TXPPS?
        - RES:UTIL:IPV4:MIN:TXPPS?
        - RES:UTIL:L1:IPV4:MIN:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecMinIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecMinIpv6(self, parameters):
        """**FETC:UTIL:IPV6:MIN:TXPPS?** - getResTxLinkPacketPerSecMinIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:MIN:TXPPS?
        - RES:UTIL:IPV6:MIN:TXPPS?
        - RES:UTIL:L1:IPV6:MIN:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecMinIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecMinMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:MIN:TXPPS?** - getResTxLinkPacketPerSecMinMpls command.
        Also used for:
        - FETC:UTIL:MPLS:MIN:TXPPS?
        - RES:UTIL:L1:MPLS:MIN:TXPPS?
        - RES:UTIL:MPLS:MIN:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecMinMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecMinNone(self, parameters):
        """**FETC:UTIL:L1:MIN:TXPPS?** - getResTxLinkPacketPerSecMinNone command.
        Also used for:
        - FETC:UTIL:MIN:TXPPS?
        - RES:UTIL:L1:MIN:TXPPS?
        - RES:UTIL:MIN:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecMinVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:MIN:TXPPS?** - getResTxLinkPacketPerSecMinVlan command.
        Also used for:
        - FETC:UTIL:VLAN:MIN:TXPPS?
        - RES:UTIL:L1:VLAN:MIN:TXPPS?
        - RES:UTIL:VLAN:MIN:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecMinVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:CUR:TXPPS?** - getResTxLinkPacketPerSecMpls command.
        Also used for:
        - FETC:UTIL:MPLS:CUR:TXPPS?
        - RES:UTIL:L1:MPLS:CUR:TXPPS?
        - RES:UTIL:MPLS:CUR:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPacketPerSecVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:CUR:TXPPS?** - getResTxLinkPacketPerSecVlan command.
        Also used for:
        - FETC:UTIL:VLAN:CUR:TXPPS?
        - RES:UTIL:L1:VLAN:CUR:TXPPS?
        - RES:UTIL:VLAN:CUR:TXPPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPacketPerSecVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthAvgIpv4(self, parameters):
        """**FETC:UTIL:IPV4:AVG:TXPCTBW?** - getResTxLinkPctBandwidthAvgIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:AVG:TXPCTBW?
        - RES:UTIL:IPV4:AVG:TXPCTBW?
        - RES:UTIL:L1:IPV4:AVG:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthAvgIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthAvgIpv6(self, parameters):
        """**FETC:UTIL:IPV6:AVG:TXPCTBW?** - getResTxLinkPctBandwidthAvgIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:AVG:TXPCTBW?
        - RES:UTIL:IPV6:AVG:TXPCTBW?
        - RES:UTIL:L1:IPV6:AVG:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthAvgIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthAvgMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:AVG:TXPCTBW?** - getResTxLinkPctBandwidthAvgMpls command.
        Also used for:
        - FETC:UTIL:MPLS:AVG:TXPCTBW?
        - RES:UTIL:L1:MPLS:AVG:TXPCTBW?
        - RES:UTIL:MPLS:AVG:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthAvgMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthAvgNone(self, parameters):
        """**FETC:UTIL:AVG:TXPCTBW?** - getResTxLinkPctBandwidthAvgNone command.
        Also used for:
        - FETC:UTIL:L1:AVG:TXPCTBW?
        - RES:UTIL:AVG:TXPCTBW?
        - RES:UTIL:L1:AVG:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthAvgVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:AVG:TXPCTBW?** - getResTxLinkPctBandwidthAvgVlan command.
        Also used for:
        - FETC:UTIL:VLAN:AVG:TXPCTBW?
        - RES:UTIL:L1:VLAN:AVG:TXPCTBW?
        - RES:UTIL:VLAN:AVG:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthAvgVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthIpv4(self, parameters):
        """**FETC:UTIL:IPV4:CUR:TXPCTBW?** - getResTxLinkPctBandwidthIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:CUR:TXPCTBW?
        - RES:UTIL:IPV4:CUR:TXPCTBW?
        - RES:UTIL:L1:IPV4:CUR:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthIpv6(self, parameters):
        """**FETC:UTIL:IPV6:CUR:TXPCTBW?** - getResTxLinkPctBandwidthIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:CUR:TXPCTBW?
        - RES:UTIL:IPV6:CUR:TXPCTBW?
        - RES:UTIL:L1:IPV6:CUR:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthMaxIpv4(self, parameters):
        """**FETC:UTIL:IPV4:MAX:TXPCTBW?** - getResTxLinkPctBandwidthMaxIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:MAX:TXPCTBW?
        - RES:UTIL:IPV4:MAX:TXPCTBW?
        - RES:UTIL:L1:IPV4:MAX:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthMaxIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthMaxIpv6(self, parameters):
        """**FETC:UTIL:IPV6:MAX:TXPCTBW?** - getResTxLinkPctBandwidthMaxIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:MAX:TXPCTBW?
        - RES:UTIL:IPV6:MAX:TXPCTBW?
        - RES:UTIL:L1:IPV6:MAX:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthMaxIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthMaxMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:MAX:TXPCTBW?** - getResTxLinkPctBandwidthMaxMpls command.
        Also used for:
        - FETC:UTIL:MPLS:MAX:TXPCTBW?
        - RES:UTIL:L1:MPLS:MAX:TXPCTBW?
        - RES:UTIL:MPLS:MAX:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthMaxMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthMaxNone(self, parameters):
        """**FETC:UTIL:L1:MAX:TXPCTBW?** - getResTxLinkPctBandwidthMaxNone command.
        Also used for:
        - FETC:UTIL:MAX:TXPCTBW?
        - RES:UTIL:L1:MAX:TXPCTBW?
        - RES:UTIL:MAX:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthMaxVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:MAX:TXPCTBW?** - getResTxLinkPctBandwidthMaxVlan command.
        Also used for:
        - FETC:UTIL:VLAN:MAX:TXPCTBW?
        - RES:UTIL:L1:VLAN:MAX:TXPCTBW?
        - RES:UTIL:VLAN:MAX:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthMaxVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthMinIpv4(self, parameters):
        """**FETC:UTIL:IPV4:MIN:TXPCTBW?** - getResTxLinkPctBandwidthMinIpv4 command.
        Also used for:
        - FETC:UTIL:L1:IPV4:MIN:TXPCTBW?
        - RES:UTIL:IPV4:MIN:TXPCTBW?
        - RES:UTIL:L1:IPV4:MIN:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthMinIpv4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthMinIpv6(self, parameters):
        """**FETC:UTIL:IPV6:MIN:TXPCTBW?** - getResTxLinkPctBandwidthMinIpv6 command.
        Also used for:
        - FETC:UTIL:L1:IPV6:MIN:TXPCTBW?
        - RES:UTIL:IPV6:MIN:TXPCTBW?
        - RES:UTIL:L1:IPV6:MIN:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthMinIpv6
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthMinMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:MIN:TXPCTBW?** - getResTxLinkPctBandwidthMinMpls command.
        Also used for:
        - FETC:UTIL:MPLS:MIN:TXPCTBW?
        - RES:UTIL:L1:MPLS:MIN:TXPCTBW?
        - RES:UTIL:MPLS:MIN:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthMinMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthMinNone(self, parameters):
        """**FETC:UTIL:L1:MIN:TXPCTBW?** - getResTxLinkPctBandwidthMinNone command.
        Also used for:
        - FETC:UTIL:MIN:TXPCTBW?
        - RES:UTIL:L1:MIN:TXPCTBW?
        - RES:UTIL:MIN:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthMinVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:MIN:TXPCTBW?** - getResTxLinkPctBandwidthMinVlan command.
        Also used for:
        - FETC:UTIL:VLAN:MIN:TXPCTBW?
        - RES:UTIL:L1:VLAN:MIN:TXPCTBW?
        - RES:UTIL:VLAN:MIN:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthMinVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthMpls(self, parameters):
        """**FETC:UTIL:L1:MPLS:CUR:TXPCTBW?** - getResTxLinkPctBandwidthMpls command.
        Also used for:
        - FETC:UTIL:MPLS:CUR:TXPCTBW?
        - RES:UTIL:L1:MPLS:CUR:TXPCTBW?
        - RES:UTIL:MPLS:CUR:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthMpls
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxLinkPctBandwidthVlan(self, parameters):
        """**FETC:UTIL:L1:VLAN:CUR:TXPCTBW?** - getResTxLinkPctBandwidthVlan command.
        Also used for:
        - FETC:UTIL:VLAN:CUR:TXPCTBW?
        - RES:UTIL:L1:VLAN:CUR:TXPCTBW?
        - RES:UTIL:VLAN:CUR:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResTxLinkPctBandwidthVlan
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxMplsPackets(self, parameters):
        """**FETC:TXPACK:MPLS?** - getResTxMplsPackets command.
        Also used for:
        - RES:TXPACK:MPLS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResTxMplsPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxPauseEndPackets(self, parameters):
        """**FETC:PAUSE:TXENDPACKETS?** - getResTxPauseEndPackets command.
        Also used for:
        - FETC:PAUSED:TXENDPACKETS?
        - FETC:TXPACK:PAUSE:ENDPACKETS?
        - RES:PAUSE:TXENDPACKETS?
        - RES:PAUSED:TXENDPACKETS?
        - RES:TXPACK:PAUSE:ENDPACKETS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResTxPauseEndPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxPausePackets(self, parameters):
        """**FETC:PAUSE:TXPACKETS?** - getResTxPausePackets command.
        Also used for:
        - FETC:PAUSED:TXPACKETS?
        - FETC:TXPACK:PAUSE:PACKETS?
        - RES:PAUSE:TXPACKETS?
        - RES:PAUSED:TXPACKETS?
        - RES:TXPACK:PAUSE:PACKETS?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResTxPausePackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxPauseQuantas(self, parameters):
        """**FETC:PAUSE:TXQUANTAS?** - getResTxPauseQuantas command.
        Also used for:
        - FETC:PAUSED:TXQUANTAS?
        - FETC:TXPACK:PAUSE:QUANT?
        - RES:PAUSE:TXQUANTAS?
        - RES:PAUSED:TXQUANTAS?
        - RES:TXPACK:PAUSE:QUANT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResTxPauseQuantas
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResTxVlanPackets(self, parameters):
        """**FETC:TXPACK:VLAN?** - getResTxVlanPackets command.
        Also used for:
        - RES:TXPACK:VLAN?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResTxVlanPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUdpChecksumAvgRate(self, parameters):
        """**FETC:UDPERR:AVGRATE?** - getResUdpChecksumAvgRate command.
        Also used for:
        - RES:UDPERR:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUdpChecksumAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUdpChecksumCount(self, parameters):
        """**FETC:UDPERR:COUNT?** - getResUdpChecksumCount command.
        Also used for:
        - RES:UDPERR:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUdpChecksumCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUdpChecksumCurRate(self, parameters):
        """**FETC:UDPERR:CURRATE?** - getResUdpChecksumCurRate command.
        Also used for:
        - RES:UDPERR:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUdpChecksumCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUdpChecksumES(self, parameters):
        """**FETC:UDPERR:ES?** - getResUdpChecksumES command.
        Also used for:
        - RES:UDPERR:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUdpChecksumES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUdpPackets(self, parameters):
        """**FETC:PACK:UDP?** - getResUdpPackets command.
        Also used for:
        - FETC:RXPACK:UDP?
        - RES:PACK:UDP?
        - RES:RXPACK:UDP?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUdpPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUnCorrCHecAvgRate(self, parameters):
        """**FETC:UCHEC:AVGRATE?** - getResUnCorrCHecAvgRate command.
        Also used for:
        - RES:UCHEC:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUnCorrCHecAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUnCorrCHecCount(self, parameters):
        """**FETC:UCHEC:COUNT?** - getResUnCorrCHecCount command.
        Also used for:
        - RES:UCHEC:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUnCorrCHecCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUnCorrCHecCurRate(self, parameters):
        """**FETC:UCHEC:CURRATE?** - getResUnCorrCHecCurRate command.
        Also used for:
        - RES:UCHEC:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUnCorrCHecCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUnCorrCHecES(self, parameters):
        """**FETC:UCHEC:ES?** - getResUnCorrCHecES command.
        Also used for:
        - RES:UCHEC:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUnCorrCHecES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUnCorrEHecAvgRate(self, parameters):
        """**FETC:UEHEC:AVGRATE?** - getResUnCorrEHecAvgRate command.
        Also used for:
        - RES:UEHEC:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUnCorrEHecAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUnCorrEHecCount(self, parameters):
        """**FETC:UEHEC:COUNT?** - getResUnCorrEHecCount command.
        Also used for:
        - RES:UEHEC:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUnCorrEHecCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUnCorrEHecCurRate(self, parameters):
        """**FETC:UEHEC:CURRATE?** - getResUnCorrEHecCurRate command.
        Also used for:
        - RES:UEHEC:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUnCorrEHecCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUnCorrEHecES(self, parameters):
        """**FETC:UEHEC:ES?** - getResUnCorrEHecES command.
        Also used for:
        - RES:UEHEC:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUnCorrEHecES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUnCorrTHecAvgRate(self, parameters):
        """**FETC:UTHEC:AVGRATE?** - getResUnCorrTHecAvgRate command.
        Also used for:
        - RES:UTHEC:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUnCorrTHecAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUnCorrTHecCount(self, parameters):
        """**FETC:UTHEC:COUNT?** - getResUnCorrTHecCount command.
        Also used for:
        - RES:UTHEC:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUnCorrTHecCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUnCorrTHecCurRate(self, parameters):
        """**FETC:UTHEC:CURRATE?** - getResUnCorrTHecCurRate command.
        Also used for:
        - RES:UTHEC:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUnCorrTHecCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUnCorrTHecES(self, parameters):
        """**FETC:UTHEC:ES?** - getResUnCorrTHecES command.
        Also used for:
        - RES:UTHEC:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUnCorrTHecES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUndersizedAvgRate(self, parameters):
        """**FETC:UNDERSIZED:AVGRATE?** - getResUndersizedAvgRate command.
        Also used for:
        - RES:UNDERSIZED:AVGRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUndersizedAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUndersizedCount(self, parameters):
        """**FETC:UNDERSIZED:COUNT?** - getResUndersizedCount command.
        Also used for:
        - RES:UNDERSIZED:COUNT?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUndersizedCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUndersizedCurRate(self, parameters):
        """**FETC:UNDERSIZED:CURRATE?** - getResUndersizedCurRate command.
        Also used for:
        - RES:UNDERSIZED:CURRATE?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUndersizedCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResUndersizedES(self, parameters):
        """**FETC:UNDERSIZED:ES?** - getResUndersizedES command.
        Also used for:
        - RES:UNDERSIZED:ES?
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getResUndersizedES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResVlanPackets(self, parameters):
        """**FETC:RXPACK:VLAN:TAG?** - getResVlanPackets command.
        Also used for:
        - FETC:VLAN:PACKETS?
        - RES:RXPACK:VLAN:TAG?
        - RES:VLAN:PACKETS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResVlanPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResVlanPackets1(self, parameters):
        """**FETC:RXPACK:VLAN?** - getResVlanPackets1 command.
        Also used for:
        - FETC:VLAN:PACKETS1?
        - RES:RXPACK:VLAN?
        - RES:VLAN:PACKETS1?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResVlanPackets1
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResVlanPackets2(self, parameters):
        """**FETC:VLAN:PACKETS2?** - getResVlanPackets2 command.
        Also used for:
        - RES:VLAN:PACKETS2?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResVlanPackets2
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResVlanPackets3(self, parameters):
        """**FETC:VLAN:PACKETS3?** - getResVlanPackets3 command.
        Also used for:
        - RES:VLAN:PACKETS3?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResVlanPackets3
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResVlanPackets4(self, parameters):
        """**FETC:VLAN:PACKETS4?** - getResVlanPackets4 command.
        Also used for:
        - RES:VLAN:PACKETS4?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResVlanPackets4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResVlanPacketsQos(self, parameters):
        """**FETC:RXPACK:VLAN:QOS?** - getResVlanPacketsQos command.
        Also used for:
        - FETC:VLAN:QOS?
        - RES:RXPACK:VLAN:QOS?
        - RES:VLAN:QOS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResVlanPacketsQos
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResVlanPacketsQos1(self, parameters):
        """**FETC:VLAN:QOS1?** - getResVlanPacketsQos1 command.
        Also used for:
        - RES:VLAN:QOS1?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResVlanPacketsQos1
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResVlanPacketsQos2(self, parameters):
        """**FETC:VLAN:QOS2?** - getResVlanPacketsQos2 command.
        Also used for:
        - RES:VLAN:QOS2?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResVlanPacketsQos2
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResVlanPacketsQos3(self, parameters):
        """**FETC:VLAN:QOS3?** - getResVlanPacketsQos3 command.
        Also used for:
        - RES:VLAN:QOS3?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResVlanPacketsQos3
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getResVlanPacketsQos4(self, parameters):
        """**FETC:VLAN:QOS4?** - getResVlanPacketsQos4 command.
        Also used for:
        - RES:VLAN:QOS4?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getResVlanPacketsQos4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRx(self, parameters):
        """**PING:RX?** - getRx command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRx
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxCid(self, parameters):
        """**RX:CID?** - getRxCid command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRxCid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxCidFilter(self, parameters):
        """**FETC:CAPTURE:SELECT?** - getRxCidFilter command.
        Also used for:
        - RES:CAPTURE:SELECT?
        - RX:OH:SELECT?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: ALL
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRxCidFilter
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxFcTov(self, parameters):
        """**RX:FCTOV?** - getRxFcTov command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %.2f
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRxFcTov
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxGfpPat(self, parameters):
        """**RX:PAT?** - getRxGfpPat command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getRxGfpPat
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxStreamBw(self, parameters):
        """**STRM:RXBW?** - getRxStreamBw command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRxStreamBw
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxStreamBytes(self, parameters):
        """**STRM:L2:RXBYTES?** - getRxStreamBytes command.
        Also used for:
        - STRM:RXBYTES?
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRxStreamBytes
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxStreamLoss(self, parameters):
        """**STRM:RXLOSS?** - getRxStreamLoss command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRxStreamLoss
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxStreamPackets(self, parameters):
        """**STRM:RXPACKETS?** - getRxStreamPackets command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRxStreamPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxTpidState(self, parameters):
        """**RX:TPID:STATE?** - getRxTpidState command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRxTpidState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxTpidValue(self, parameters):
        """**RX:TPID:VALUE?** - getRxTpidValue command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRxTpidValue
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getRxid(self, parameters):
        """**STRM:FC:RXID?** - getRxid command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %04X
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getRxid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDAvgFrame(self, parameters):
        """**SD:AVGFRAME?** - getSDAvgFrame command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDAvgFrame
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDAvgTime(self, parameters):
        """**SD:AVGTIME?** - getSDAvgTime command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDAvgTime
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDBadFrame(self, parameters):
        """**SD:BADFRAME?** - getSDBadFrame command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDBadFrame
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDBadTime(self, parameters):
        """**SD:BADTIME?** - getSDBadTime command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %.1f ms
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDBadTime
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDCurFrame(self, parameters):
        """**SD:CURFRAME?** - getSDCurFrame command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDCurFrame
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDCurTime(self, parameters):
        """**SD:CURTIME?** - getSDCurTime command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDCurTime
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDGoodFrame(self, parameters):
        """**SD:GOODFRAME?** - getSDGoodFrame command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDGoodFrame
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDGoodTime(self, parameters):
        """**SD:GOODTIME?** - getSDGoodTime command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %.1f ms
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDGoodTime
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDMaxFrame(self, parameters):
        """**SD:MAXFRAME?** - getSDMaxFrame command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDMaxFrame
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDMaxTime(self, parameters):
        """**SD:MAXTIME?** - getSDMaxTime command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDMaxTime
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDMinFrame(self, parameters):
        """**SD:MINFRAME?** - getSDMinFrame command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDMinFrame
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDMinTime(self, parameters):
        """**SD:MINTIME?** - getSDMinTime command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDMinTime
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDRecentFrame(self, parameters):
        """**SD:RECFRAME?** - getSDRecentFrame command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDRecentFrame
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDRecentTime(self, parameters):
        """**SD:RECTIME?** - getSDRecentTime command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDRecentTime
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSDState(self, parameters):
        """**SD:ACTION?** - getSDState command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSDState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getScramble(self, parameters):
        """**SOUR:SCRAMBLE?** - getScramble command.
        Also used for:
        - TX:SCRAMBLE?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getScramble
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSeedABAvgRate(self, parameters):
        """**SEEDAB:AVGRATE?** - getSeedABAvgRate command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSeedABAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSeedABCount(self, parameters):
        """**SEEDAB:COUNT?** - getSeedABCount command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSeedABCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSeedABCurRate(self, parameters):
        """**SEEDAB:CURRATE?** - getSeedABCurRate command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSeedABCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSeedABES(self, parameters):
        """**SEEDAB:ES?** - getSeedABES command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSeedABES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSeedABPat(self, parameters):
        """**SEEDAB:ABPAT?** - getSeedABPat command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getSeedABPat
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSeedAPat(self, parameters):
        """**SEEDAB:APAT?** - getSeedAPat command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getSeedAPat
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSeedBPat(self, parameters):
        """**SEEDAB:BPAT?** - getSeedBPat command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getSeedBPat
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSeqNo(self, parameters):
        """**PING:SEQNO?** - getSeqNo command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSeqNo
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSeqid(self, parameters):
        """**STRM:FC:SEQID?** - getSeqid command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %02X
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSeqid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSid(self, parameters):
        """**STRM:FC:SID?** - getSid command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %06X
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSof(self, parameters):
        """**STRM:FC:SOF?** - getSof command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: SOFc1
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSof
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamBitAvgRate(self, parameters):
        """**STRM:BIT:AVGRATE?** - getStreamBitAvgRate command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamBitAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamBitCount(self, parameters):
        """**STRM:BIT:COUNT?** - getStreamBitCount command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamBitCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamBitCurRate(self, parameters):
        """**STRM:BIT:CURRATE?** - getStreamBitCurRate command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamBitCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamBitES(self, parameters):
        """**STRM:BIT:ES?** - getStreamBitES command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamBitES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamJitAvg(self, parameters):
        """**STRM:JIT:AVG?** - getStreamJitAvg command.
        
        C++ Implementation Details:
        - Uses callGetPacketStreamStatistics() to get stream statistics
        - Format: %.3f
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamJitAvg
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamJitMax(self, parameters):
        """**STRM:JIT:MAX?** - getStreamJitMax command.
        
        C++ Implementation Details:
        - Uses callGetPacketStreamStatistics() to get stream statistics
        - Format: %.3f
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamJitMax
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamJitMin(self, parameters):
        """**STRM:JIT:MIN?** - getStreamJitMin command.
        
        C++ Implementation Details:
        - Uses callGetPacketStreamStatistics() to get stream statistics
        - Format: %.3f
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamJitMin
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1RxLinkKBPerSecAvgNone(self, parameters):
        """**STRM:AVG:RXMBPS?** - getStreamL1RxLinkKBPerSecAvgNone command.
        Also used for:
        - STRM:L1:AVG:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1RxLinkKBPerSecAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1RxLinkKBPerSecMaxNone(self, parameters):
        """**STRM:L1:MAX:RXMBPS?** - getStreamL1RxLinkKBPerSecMaxNone command.
        Also used for:
        - STRM:MAX:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1RxLinkKBPerSecMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1RxLinkKBPerSecMinNone(self, parameters):
        """**STRM:L1:MIN:RXMBPS?** - getStreamL1RxLinkKBPerSecMinNone command.
        Also used for:
        - STRM:MIN:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1RxLinkKBPerSecMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1RxLinkKBPerSecNone(self, parameters):
        """**STRM:CUR:RXMBPS?** - getStreamL1RxLinkKBPerSecNone command.
        Also used for:
        - STRM:L1:CUR:RXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1RxLinkKBPerSecNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1RxLinkPctBandwidthAvgNone(self, parameters):
        """**STRM:AVG:RXPCTBW?** - getStreamL1RxLinkPctBandwidthAvgNone command.
        Also used for:
        - STRM:L1:AVG:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1RxLinkPctBandwidthAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1RxLinkPctBandwidthMaxNone(self, parameters):
        """**STRM:L1:MAX:RXPCTBW?** - getStreamL1RxLinkPctBandwidthMaxNone command.
        Also used for:
        - STRM:MAX:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1RxLinkPctBandwidthMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1RxLinkPctBandwidthMinNone(self, parameters):
        """**STRM:L1:MIN:RXPCTBW?** - getStreamL1RxLinkPctBandwidthMinNone command.
        Also used for:
        - STRM:MIN:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1RxLinkPctBandwidthMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1RxLinkPctBandwidthNone(self, parameters):
        """**STRM:CUR:RXPCTBW?** - getStreamL1RxLinkPctBandwidthNone command.
        Also used for:
        - STRM:L1:CUR:RXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1RxLinkPctBandwidthNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1TxLinkKBPerSecAvgNone(self, parameters):
        """**STRM:AVG:TXMBPS?** - getStreamL1TxLinkKBPerSecAvgNone command.
        Also used for:
        - STRM:L1:AVG:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1TxLinkKBPerSecAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1TxLinkKBPerSecMaxNone(self, parameters):
        """**STRM:L1:MAX:TXMBPS?** - getStreamL1TxLinkKBPerSecMaxNone command.
        Also used for:
        - STRM:MAX:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1TxLinkKBPerSecMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1TxLinkKBPerSecMinNone(self, parameters):
        """**STRM:L1:MIN:TXMBPS?** - getStreamL1TxLinkKBPerSecMinNone command.
        Also used for:
        - STRM:MIN:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1TxLinkKBPerSecMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1TxLinkKBPerSecNone(self, parameters):
        """**STRM:CUR:TXMBPS?** - getStreamL1TxLinkKBPerSecNone command.
        Also used for:
        - STRM:L1:CUR:TXMBPS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1TxLinkKBPerSecNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1TxLinkPctBandwidthAvgNone(self, parameters):
        """**STRM:AVG:TXPCTBW?** - getStreamL1TxLinkPctBandwidthAvgNone command.
        Also used for:
        - STRM:L1:AVG:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1TxLinkPctBandwidthAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1TxLinkPctBandwidthMaxNone(self, parameters):
        """**STRM:L1:MAX:TXPCTBW?** - getStreamL1TxLinkPctBandwidthMaxNone command.
        Also used for:
        - STRM:MAX:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1TxLinkPctBandwidthMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1TxLinkPctBandwidthMinNone(self, parameters):
        """**STRM:L1:MIN:TXPCTBW?** - getStreamL1TxLinkPctBandwidthMinNone command.
        Also used for:
        - STRM:MIN:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1TxLinkPctBandwidthMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL1TxLinkPctBandwidthNone(self, parameters):
        """**STRM:CUR:TXPCTBW?** - getStreamL1TxLinkPctBandwidthNone command.
        Also used for:
        - STRM:L1:CUR:TXPCTBW?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL1TxLinkPctBandwidthNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2RxBytesPerSec(self, parameters):
        """**STRM:L2:RXBYTEPS?** - getStreamL2RxBytesPerSec command.
        
        C++ Implementation Details:
        - Uses callGetPacketStreamStatistics() to get stream statistics
        - Format: %I64u
        - No parameters required
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamL2RxBytesPerSec
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2RxLinkKBPerSecAvgNone(self, parameters):
        """**STRM:L2:AVG:RXMBPS?** - getStreamL2RxLinkKBPerSecAvgNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2RxLinkKBPerSecAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2RxLinkKBPerSecMaxNone(self, parameters):
        """**STRM:L2:MAX:RXMBPS?** - getStreamL2RxLinkKBPerSecMaxNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2RxLinkKBPerSecMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2RxLinkKBPerSecMinNone(self, parameters):
        """**STRM:L2:MIN:RXMBPS?** - getStreamL2RxLinkKBPerSecMinNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2RxLinkKBPerSecMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2RxLinkKBPerSecNone(self, parameters):
        """**STRM:L2:CUR:RXMBPS?** - getStreamL2RxLinkKBPerSecNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2RxLinkKBPerSecNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2RxLinkPctBandwidthAvgNone(self, parameters):
        """**STRM:L2:AVG:RXPCTBW?** - getStreamL2RxLinkPctBandwidthAvgNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2RxLinkPctBandwidthAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2RxLinkPctBandwidthMaxNone(self, parameters):
        """**STRM:L2:MAX:RXPCTBW?** - getStreamL2RxLinkPctBandwidthMaxNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2RxLinkPctBandwidthMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2RxLinkPctBandwidthMinNone(self, parameters):
        """**STRM:L2:MIN:RXPCTBW?** - getStreamL2RxLinkPctBandwidthMinNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2RxLinkPctBandwidthMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2RxLinkPctBandwidthNone(self, parameters):
        """**STRM:L2:CUR:RXPCTBW?** - getStreamL2RxLinkPctBandwidthNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2RxLinkPctBandwidthNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2TxBytesPerSec(self, parameters):
        """**STRM:L2:TXBYTEPS?** - getStreamL2TxBytesPerSec command.
        
        C++ Implementation Details:
        - Uses callGetPacketStreamStatistics() to get stream statistics
        - Format: %I64u
        - No parameters required
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamL2TxBytesPerSec
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2TxLinkKBPerSecAvgNone(self, parameters):
        """**STRM:L2:AVG:TXMBPS?** - getStreamL2TxLinkKBPerSecAvgNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2TxLinkKBPerSecAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2TxLinkKBPerSecMaxNone(self, parameters):
        """**STRM:L2:MAX:TXMBPS?** - getStreamL2TxLinkKBPerSecMaxNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2TxLinkKBPerSecMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2TxLinkKBPerSecMinNone(self, parameters):
        """**STRM:L2:MIN:TXMBPS?** - getStreamL2TxLinkKBPerSecMinNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2TxLinkKBPerSecMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2TxLinkKBPerSecNone(self, parameters):
        """**STRM:L2:CUR:TXMBPS?** - getStreamL2TxLinkKBPerSecNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2TxLinkKBPerSecNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2TxLinkPctBandwidthAvgNone(self, parameters):
        """**STRM:L2:AVG:TXPCTBW?** - getStreamL2TxLinkPctBandwidthAvgNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2TxLinkPctBandwidthAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2TxLinkPctBandwidthMaxNone(self, parameters):
        """**STRM:L2:MAX:TXPCTBW?** - getStreamL2TxLinkPctBandwidthMaxNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2TxLinkPctBandwidthMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2TxLinkPctBandwidthMinNone(self, parameters):
        """**STRM:L2:MIN:TXPCTBW?** - getStreamL2TxLinkPctBandwidthMinNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2TxLinkPctBandwidthMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamL2TxLinkPctBandwidthNone(self, parameters):
        """**STRM:L2:CUR:TXPCTBW?** - getStreamL2TxLinkPctBandwidthNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamL2TxLinkPctBandwidthNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamLatAvg(self, parameters):
        """**STRM:LAT:AVG?** - getStreamLatAvg command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamLatAvg
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamLatCur(self, parameters):
        """**STRM:LAT:CUR?** - getStreamLatCur command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamLatCur
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamLatMax(self, parameters):
        """**STRM:LAT:MAX?** - getStreamLatMax command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamLatMax
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamLatMin(self, parameters):
        """**STRM:LAT:MIN?** - getStreamLatMin command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamLatMin
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamLossAvgRate(self, parameters):
        """**STRM:LOSS:AVGRATE?** - getStreamLossAvgRate command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamLossAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamLossCount(self, parameters):
        """**STRM:LOSS:COUNT?** - getStreamLossCount command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamLossCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamLossCurRate(self, parameters):
        """**STRM:LOSS:CURRATE?** - getStreamLossCurRate command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamLossCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamLossES(self, parameters):
        """**STRM:LOSS:ES?** - getStreamLossES command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamLossES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamLossPerSec(self, parameters):
        """**STRM:LOSS:COUNTPS?** - getStreamLossPerSec command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamLossPerSec
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamRxLinkPacketPerSecAvgNone(self, parameters):
        """**STRM:AVG:RXPPS?** - getStreamRxLinkPacketPerSecAvgNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamRxLinkPacketPerSecAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamRxLinkPacketPerSecMaxNone(self, parameters):
        """**STRM:MAX:RXPPS?** - getStreamRxLinkPacketPerSecMaxNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamRxLinkPacketPerSecMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamRxLinkPacketPerSecMinNone(self, parameters):
        """**STRM:MIN:RXPPS?** - getStreamRxLinkPacketPerSecMinNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamRxLinkPacketPerSecMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamRxLinkPacketPerSecNone(self, parameters):
        """**STRM:CUR:RXPPS?** - getStreamRxLinkPacketPerSecNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamRxLinkPacketPerSecNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamSeqAvgRate(self, parameters):
        """**STRM:SEQ:AVGRATE?** - getStreamSeqAvgRate command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamSeqAvgRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamSeqCount(self, parameters):
        """**STRM:SEQ:COUNT?** - getStreamSeqCount command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamSeqCount
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamSeqCurRate(self, parameters):
        """**STRM:SEQ:CURRATE?** - getStreamSeqCurRate command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamSeqCurRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamSeqES(self, parameters):
        """**STRM:SEQ:ES?** - getStreamSeqES command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamSeqES
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamSyncSecs(self, parameters):
        """**STRM:SYNC:SECS?** - getStreamSyncSecs command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamSyncSecs
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamSyncState(self, parameters):
        """**STRM:SYNC:STATE?** - getStreamSyncState command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStreamSyncState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamTxLinkPacketPerSecAvgNone(self, parameters):
        """**STRM:AVG:TXPPS?** - getStreamTxLinkPacketPerSecAvgNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamTxLinkPacketPerSecAvgNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamTxLinkPacketPerSecMaxNone(self, parameters):
        """**STRM:MAX:TXPPS?** - getStreamTxLinkPacketPerSecMaxNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamTxLinkPacketPerSecMaxNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamTxLinkPacketPerSecMinNone(self, parameters):
        """**STRM:MIN:TXPPS?** - getStreamTxLinkPacketPerSecMinNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamTxLinkPacketPerSecMinNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStreamTxLinkPacketPerSecNone(self, parameters):
        """**STRM:CUR:TXPPS?** - getStreamTxLinkPacketPerSecNone command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getStreamTxLinkPacketPerSecNone
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getStrmSet(self, parameters):
        """**STRM:SET?** - getStrmSet command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getStrmSet
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSubnetAddr(self, parameters):
        """**ARP:SUBNET?** - getSubnetAddr command.
        Also used for:
        - PING:SUBNET?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getSubnetAddr
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getSuperBlock(self, parameters):
        """**SOUR:SUPERBLK?** - getSuperBlock command.
        Also used for:
        - TX:SUPERBLK?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getSuperBlock
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTTL(self, parameters):
        """**PING:TTL?** - getTTL command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getTTL
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTagLevel(self, parameters):
        """**STRM:TAG:LEVEL?** - getTagLevel command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getTagLevel
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTagMode(self, parameters):
        """**STRM:TAG:MODE?** - getTagMode command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getTagMode
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTimeOut(self, parameters):
        """**PING:TIMEOUT?** - getTimeOut command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getTimeOut
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTrafficDuration(self, parameters):
        """**STRM:DURATION?** - getTrafficDuration command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getTrafficDuration
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTrafficLayer(self, parameters):
        """**STRM:TRAFFICLAYER?** - getTrafficLayer command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getTrafficLayer
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTx(self, parameters):
        """**PING:TX?** - getTx command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getTx
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTxEnable(self, parameters):
        """**STRM:TXENABLE?** - getTxEnable command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getTxEnable
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTxPti(self, parameters):
        """**SOUR:PTI?** - getTxPti command.
        Also used for:
        - TX:PTI?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getTxPti
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTxSpare(self, parameters):
        """**SOUR:SPARE?** - getTxSpare command.
        Also used for:
        - TX:SPARE?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getTxSpare
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTxStreamBw(self, parameters):
        """**STRM:TXBW?** - getTxStreamBw command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getTxStreamBw
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTxStreamBytes(self, parameters):
        """**STRM:L2:TXBYTES?** - getTxStreamBytes command.
        Also used for:
        - STRM:TXBYTES?
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getTxStreamBytes
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getTxStreamPackets(self, parameters):
        """**STRM:TXPACKETS?** - getTxStreamPackets command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getTxStreamPackets
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getType(self, parameters):
        """**STRM:FC:TYPE?** - getType command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %02X
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getType
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanCfi1(self, parameters):
        """**STRM:VLANCFI1?** - getVlanCfi1 command.
        Also used for:
        - STRM:VLANDEI1?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanCfi1
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanCfi2(self, parameters):
        """**STRM:VLANCFI2?** - getVlanCfi2 command.
        Also used for:
        - STRM:VLANDEI2?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanCfi2
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanCfi3(self, parameters):
        """**STRM:VLANCFI3?** - getVlanCfi3 command.
        Also used for:
        - STRM:VLANDEI3?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanCfi3
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanCfi4(self, parameters):
        """**STRM:VLANCFI4?** - getVlanCfi4 command.
        Also used for:
        - STRM:VLANDEI4?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanCfi4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanFlooding(self, parameters):
        """**SOUR:VLANFLOOD?** - getVlanFlooding command.
        Also used for:
        - TX:VLANFLOOD?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getVlanFlooding
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanId1(self, parameters):
        """**STRM:VLANID1?** - getVlanId1 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanId1
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanId2(self, parameters):
        """**STRM:VLANID2?** - getVlanId2 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanId2
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanId3(self, parameters):
        """**STRM:VLANID3?** - getVlanId3 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanId3
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanId4(self, parameters):
        """**STRM:VLANID4?** - getVlanId4 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanId4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanQos1(self, parameters):
        """**STRM:VLANQOS1?** - getVlanQos1 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanQos1
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanQos2(self, parameters):
        """**STRM:VLANQOS2?** - getVlanQos2 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanQos2
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanQos3(self, parameters):
        """**STRM:VLANQOS3?** - getVlanQos3 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanQos3
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanQos4(self, parameters):
        """**STRM:VLANQOS4?** - getVlanQos4 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanQos4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanTag(self, parameters):
        """**STRM:VLANTAG?** - getVlanTag command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement getVlanTag
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanTpid1(self, parameters):
        """**STRM:VLANTPID1?** - getVlanTpid1 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanTpid1
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanTpid2(self, parameters):
        """**STRM:VLANTPID2?** - getVlanTpid2 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanTpid2
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanTpid3(self, parameters):
        """**STRM:VLANTPID3?** - getVlanTpid3 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanTpid3
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def getVlanTpid4(self, parameters):
        """**STRM:VLANTPID4?** - getVlanTpid4 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement getVlanTpid4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def portLogin(self, parameters):
        """**SOUR:PORTLOGIN** - portLogin command.
        Also used for:
        - TX:PORTLOGIN
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement portLogin
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetActivate(self, parameters):
        """**RFC:B2B:ACT?** - rfcGetActivate command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetActivate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetAvgObServed(self, parameters):
        """**RFC:B2B:AVGOBS?** - rfcGetAvgObServed command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %I64u
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetAvgObServed
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetBwCeiling(self, parameters):
        """**RFC:BW:CEILING?** - rfcGetBwCeiling command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetBwCeiling
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetBwFloor(self, parameters):
        """**RFC:BW:FLOOR?** - rfcGetBwFloor command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetBwFloor
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetDestination(self, parameters):
        """**RFC:TEST:DEST?** - rfcGetDestination command.
        Also used for:
        - Y1564:DESTPORT?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: Destination is Port %u
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetDestination
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetFrameActivate(self, parameters):
        """**RFC:FRAME:ACT?** - rfcGetFrameActivate command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetFrameActivate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetFrameLoss(self, parameters):
        """**RFC:FRAME:LOSS?** - rfcGetFrameLoss command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetFrameLoss
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetFrameRate(self, parameters):
        """**RFC:FRAME:RATE?** - rfcGetFrameRate command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetFrameRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetFrameRx(self, parameters):
        """**RFC:FRAME:RX?** - rfcGetFrameRx command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetFrameRx
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetFrameTx(self, parameters):
        """**RFC:FRAME:TX?** - rfcGetFrameTx command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetFrameTx
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetLatencyIterations(self, parameters):
        """**RFC:THRU:LAT?** - rfcGetLatencyIterations command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetLatencyIterations
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetMaxPossible(self, parameters):
        """**RFC:B2B:MAXPOS?** - rfcGetMaxPossible command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Format: %I64u
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetMaxPossible
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetRepititions(self, parameters):
        """**RFC:B2B:REP?** - rfcGetRepititions command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetRepititions
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetResolution(self, parameters):
        """**RFC:B2B:RES?** - rfcGetResolution command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetResolution
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetState(self, parameters):
        """**RFC:STATE?** - rfcGetState command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetStream(self, parameters):
        """**RFC:TEST:STREAM?** - rfcGetStream command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetStream
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetTestDuration(self, parameters):
        """**RFC:TEST:DUR?** - rfcGetTestDuration command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %d secs
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetTestDuration
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetTestMode(self, parameters):
        """**RFC:TEST:MODE?** - rfcGetTestMode command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetTestMode
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetTestSize(self, parameters):
        """**RFC:TEST:SIZE?** - rfcGetTestSize command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetTestSize
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetThruActivate(self, parameters):
        """**RFC:THRU:ACT?** - rfcGetThruActivate command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetThruActivate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetThruAvg(self, parameters):
        """**RFC:THRU:AVG?** - rfcGetThruAvg command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetThruAvg
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetThruLoss(self, parameters):
        """**RFC:THRU:LOSS?** - rfcGetThruLoss command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %0.0f%%
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetThruLoss
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetThruMax(self, parameters):
        """**RFC:THRU:MAX?** - rfcGetThruMax command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetThruMax
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetThruMin(self, parameters):
        """**RFC:THRU:MIN?** - rfcGetThruMin command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetThruMin
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetThruPass(self, parameters):
        """**RFC:THRU:PASS?** - rfcGetThruPass command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetThruPass
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetThruRes(self, parameters):
        """**RFC:THRU:RES?** - rfcGetThruRes command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %0.2f%%
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetThruRes
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetThruRx(self, parameters):
        """**RFC:THRU:RX?** - rfcGetThruRx command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetThruRx
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcGetThruTx(self, parameters):
        """**RFC:THRU:TX?** - rfcGetThruTx command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcGetThruTx
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetActivate(self, parameters):
        """**RFC:B2B:ACT** - rfcSetActivate command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetActivate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetBwCeiling(self, parameters):
        """**RFC:BW:CEILING** - rfcSetBwCeiling command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetBwCeiling
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetBwFloor(self, parameters):
        """**RFC:BW:FLOOR** - rfcSetBwFloor command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetBwFloor
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetDestination(self, parameters):
        """**RFC:TEST:DEST** - rfcSetDestination command.
        Also used for:
        - Y1564:DESTPORT
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetDestination
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetFactoryDeflt(self, parameters):
        """**RFC:TEST:DEFAULT** - rfcSetFactoryDeflt command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetFactoryDeflt
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetFrameActivate(self, parameters):
        """**RFC:FRAME:ACT** - rfcSetFrameActivate command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetFrameActivate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetLatencyIterations(self, parameters):
        """**RFC:THRU:LAT** - rfcSetLatencyIterations command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetLatencyIterations
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetRepititions(self, parameters):
        """**RFC:B2B:REP** - rfcSetRepititions command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetRepititions
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetResolution(self, parameters):
        """**RFC:B2B:RES** - rfcSetResolution command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetResolution
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetStream(self, parameters):
        """**RFC:TEST:STREAM** - rfcSetStream command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetStream
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetTestDuration(self, parameters):
        """**RFC:TEST:DUR** - rfcSetTestDuration command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetTestDuration
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetTestMode(self, parameters):
        """**RFC:TEST:MODE** - rfcSetTestMode command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetTestMode
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetTestSize(self, parameters):
        """**RFC:TEST:SIZE** - rfcSetTestSize command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetTestSize
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetThruActivate(self, parameters):
        """**RFC:THRU:ACT** - rfcSetThruActivate command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetThruActivate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetThruLoss(self, parameters):
        """**RFC:THRU:LOSS** - rfcSetThruLoss command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetThruLoss
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def rfcSetThruRes(self, parameters):
        """**RFC:THRU:RES** - rfcSetThruRes command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement rfcSetThruRes
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def saveCaptureNanoPcap(self, parameters):
        """**RX:CAPSAVE:NANOPCAP** - saveCaptureNanoPcap command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement saveCaptureNanoPcap
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def saveCapturePcap(self, parameters):
        """**RX:CAPSAVE:MICROPCAP** - saveCapturePcap command.
        Also used for:
        - RX:CAPSAVE:PCAP
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement saveCapturePcap
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def saveCapturePcapNg(self, parameters):
        """**RX:CAPSAVE:PCAPNG** - saveCapturePcapNg command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement saveCapturePcapNg
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def sendBurst(self, parameters):
        """**STRM:BURST** - sendBurst command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement sendBurst
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setArpEnable(self, parameters):
        """**STRM:ARP** - setArpEnable command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setArpEnable
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setB2BCredit(self, parameters):
        """**STRM:FC:B2BCREDIT** - setB2BCredit command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setB2BCredit
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setBBCredit(self, parameters):
        """**SOUR:BBCREDIT** - setBBCredit command.
        Also used for:
        - TX:BBCREDIT
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setBBCredit
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setBBCreditBypass(self, parameters):
        """**SOUR:BBCREDITBYPASS** - setBBCreditBypass command.
        Also used for:
        - TX:BBCREDITBYPASS
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setBBCreditBypass
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setBandwidth(self, parameters):
        """**STRM:BW** - setBandwidth command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setBandwidth
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setBurst(self, parameters):
        """**STRM:BURSTSIZE** - setBurst command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setBurst
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setCaptureSize(self, parameters):
        """**RX:CAPSIZE** - setCaptureSize command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setCaptureSize
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setClass(self, parameters):
        """**STRM:FC:CLASS** - setClass command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setClass
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setCsctl(self, parameters):
        """**STRM:FC:CSCTL** - setCsctl command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setCsctl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setDeficitIdle(self, parameters):
        """**SOUR:DEFICIT** - setDeficitIdle command.
        Also used for:
        - TX:DEFICIT
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setDeficitIdle
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setDfctl(self, parameters):
        """**STRM:FC:DFCTL** - setDfctl command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setDfctl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setDid(self, parameters):
        """**STRM:FC:DID** - setDid command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setDid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setEof(self, parameters):
        """**STRM:FC:EOF** - setEof command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setEof
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setEtherType(self, parameters):
        """**STRM:ETYPE** - setEtherType command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setEtherType
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setFcMacdest(self, parameters):
        """**STRM:FC:WWNDEST** - setFcMacdest command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setFcMacdest
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setFcMacsource(self, parameters):
        """**STRM:FC:WWNSOURCE** - setFcMacsource command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setFcMacsource
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setFctl(self, parameters):
        """**STRM:FC:FCTL** - setFctl command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setFctl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setFillword(self, parameters):
        """**SOUR:FILLWORD** - setFillword command.
        Also used for:
        - TX:FILLWORD
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setFillword
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setFramesize(self, parameters):
        """**STRM:FRAMESIZE** - setFramesize command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setFramesize
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setGatewayAddr(self, parameters):
        """**ARP:GATEWAY** - setGatewayAddr command.
        Also used for:
        - PING:GATEWAY
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setGatewayAddr
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setGfpCid(self, parameters):
        """**SOUR:CID** - setGfpCid command.
        Also used for:
        - TX:CID
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setGfpCid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setGfpExi(self, parameters):
        """**SOUR:EXI** - setGfpExi command.
        Also used for:
        - TX:EXI
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setGfpExi
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setGfpLen(self, parameters):
        """**SOUR:LEN** - setGfpLen command.
        Also used for:
        - TX:LEN
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setGfpLen
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setGfpPat(self, parameters):
        """**SOUR:PAT** - setGfpPat command.
        Also used for:
        - TX:PAT
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setGfpPat
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setGfpPfcs(self, parameters):
        """**SOUR:PFCS** - setGfpPfcs command.
        Also used for:
        - TX:PFCS
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setGfpPfcs
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setGfpRate(self, parameters):
        """**SOUR:RATE** - setGfpRate command.
        Also used for:
        - TX:RATE
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setGfpRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setGfpUpi(self, parameters):
        """**SOUR:UPI** - setGfpUpi command.
        Also used for:
        - TX:UPI
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setGfpUpi
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIPDest(self, parameters):
        """**PING:IPDEST** - setIPDest command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIPDest
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIPSrc(self, parameters):
        """**ARP:IPSRC** - setIPSrc command.
        Also used for:
        - PING:IPSRC
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIPSrc
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIpFrag(self, parameters):
        """**STRM:IPFRAG** - setIpFrag command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIpFrag
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIpMode(self, parameters):
        """**STRM:IPMODE** - setIpMode command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIpMode
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIpTos(self, parameters):
        """**STRM:IPTOS** - setIpTos command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIpTos
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIpTtl(self, parameters):
        """**STRM:IPTTL** - setIpTtl command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIpTtl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIpcgC(self, parameters):
        """**STRM:IPGB** - setIpcgC command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIpcgC
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIpcgM(self, parameters):
        """**STRM:IPGM** - setIpcgM command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIpcgM
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIpdest(self, parameters):
        """**STRM:IPDEST** - setIpdest command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIpdest
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIpsource(self, parameters):
        """**STRM:IPSOURCE** - setIpsource command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIpsource
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIpv6FlowControl(self, parameters):
        """**STRM:IPV6:FLOWLABEL** - setIpv6FlowControl command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIpv6FlowControl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIpv6IpDestAddress(self, parameters):
        """**STRM:IPV6:IPDEST** - setIpv6IpDestAddress command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIpv6IpDestAddress
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIpv6IpSourceAddress(self, parameters):
        """**STRM:IPV6:IPSOURCE** - setIpv6IpSourceAddress command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIpv6IpSourceAddress
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIpv6NextHop(self, parameters):
        """**STRM:IPV6:HOPLIMIT** - setIpv6NextHop command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIpv6NextHop
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setIpv6TrafClass(self, parameters):
        """**STRM:IPV6:TRAFCLASS** - setIpv6TrafClass command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setIpv6TrafClass
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setLatencyMode(self, parameters):
        """**SOUR:LATENCYMODE** - setLatencyMode command.
        Also used for:
        - TX:LATENCYMODE
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setLatencyMode
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setLinkinit(self, parameters):
        """**SOUR:LINKINIT** - setLinkinit command.
        Also used for:
        - TX:LINKINIT
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setLinkinit
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setMACSrc(self, parameters):
        """**ARP:MACSRC** - setMACSrc command.
        Also used for:
        - PING:MACSRC
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setMACSrc
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setMacdest(self, parameters):
        """**STRM:MACDEST** - setMacdest command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setMacdest
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setMacsource(self, parameters):
        """**STRM:MACSOURCE** - setMacsource command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setMacsource
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setMbps(self, parameters):
        """**STRM:MBPS** - setMbps command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setMbps
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setNumPings(self, parameters):
        """**PING:NUMPINGS** - setNumPings command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setNumPings
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setOxid(self, parameters):
        """**STRM:FC:OXID** - setOxid command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setOxid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setParm(self, parameters):
        """**STRM:FC:PARM** - setParm command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setParm
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setPattern(self, parameters):
        """**STRM:PATTERN** - setPattern command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setPattern
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setPktLen(self, parameters):
        """**PING:PKTLEN** - setPktLen command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setPktLen
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setPortMap(self, parameters):
        """**SOUR:MAP** - setPortMap command.
        Also used for:
        - TX:MAP
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setPortMap
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setPortdest(self, parameters):
        """**STRM:PORTDEST** - setPortdest command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setPortdest
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setPortsource(self, parameters):
        """**STRM:PORTSOURCE** - setPortsource command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setPortsource
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setPpPauseState(self, parameters):
        """**RX:PAUSE** - setPpPauseState command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setPpPauseState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setPreamble(self, parameters):
        """**SOUR:PREAMBLE** - setPreamble command.
        Also used for:
        - TX:PREAMBLE
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setPreamble
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setProtocol(self, parameters):
        """**STRM:PROTOCOL** - setProtocol command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setProtocol
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRampBw(self, parameters):
        """**STRM:RAMP:CEILBW** - setRampBw command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setRampBw
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRampDur(self, parameters):
        """**STRM:RAMP:DUR** - setRampDur command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setRampDur
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRampMbps(self, parameters):
        """**STRM:RAMP:CEILMBPS** - setRampMbps command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setRampMbps
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRampStep(self, parameters):
        """**STRM:RAMP:STEP** - setRampStep command.
        Also used for:
        - STRM:RAMP:STEPBW
        - STRM:RAMP:STEPMBPS
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setRampStep
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRampStop(self, parameters):
        """**STRM:RAMP:FLOOR** - setRampStop command.
        Also used for:
        - STRM:RAMP:FLOORBW
        - STRM:RAMP:FLOORMBPS
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setRampStop
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRampUom(self, parameters):
        """**STRM:RAMP:UOM** - setRampUom command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setRampUom
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRctl(self, parameters):
        """**STRM:FC:RCTL** - setRctl command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setRctl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRxCid(self, parameters):
        """**RX:CID** - setRxCid command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setRxCid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRxCidFilter(self, parameters):
        """**FETC:CAPTURE:SELECT** - setRxCidFilter command.
        Also used for:
        - RES:CAPTURE:SELECT
        - RX:OH:SELECT
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setRxCidFilter
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRxFcTov(self, parameters):
        """**RX:FCTOV** - setRxFcTov command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setRxFcTov
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRxGfpPat(self, parameters):
        """**RX:PAT** - setRxGfpPat command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setRxGfpPat
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRxTpidState(self, parameters):
        """**RX:TPID:STATE** - setRxTpidState command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setRxTpidState
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRxTpidValue(self, parameters):
        """**RX:TPID:VALUE** - setRxTpidValue command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setRxTpidValue
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRxid(self, parameters):
        """**STRM:FC:RXID** - setRxid command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setRxid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setSDAction(self, parameters):
        """**SD:ACTION** - setSDAction command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setSDAction
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setSDBadFrame(self, parameters):
        """**SD:BADFRAME** - setSDBadFrame command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %.1f ms
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setSDBadFrame
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setSDBadTime(self, parameters):
        """**SD:BADTIME** - setSDBadTime command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setSDBadTime
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setSDGoodFrame(self, parameters):
        """**SD:GOODFRAME** - setSDGoodFrame command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %.1f ms
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setSDGoodFrame
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setSDGoodTime(self, parameters):
        """**SD:GOODTIME** - setSDGoodTime command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setSDGoodTime
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setScramble(self, parameters):
        """**SOUR:SCRAMBLE** - setScramble command.
        Also used for:
        - TX:SCRAMBLE
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setScramble
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setSeedABPat(self, parameters):
        """**SEEDAB:ABPAT** - setSeedABPat command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setSeedABPat
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setSeedAPat(self, parameters):
        """**SEEDAB:APAT** - setSeedAPat command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %I64X
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setSeedAPat
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setSeedBPat(self, parameters):
        """**SEEDAB:BPAT** - setSeedBPat command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %I64X
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setSeedBPat
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setSeqid(self, parameters):
        """**STRM:FC:SEQID** - setSeqid command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setSeqid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setSid(self, parameters):
        """**STRM:FC:SID** - setSid command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setSid
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setSof(self, parameters):
        """**STRM:FC:SOF** - setSof command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setSof
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setStart(self, parameters):
        """**PING:START** - setStart command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setStart
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setStop(self, parameters):
        """**PING:STOP** - setStop command.
        
        C++ Implementation Details:
        - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setStop
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setSubnetAddr(self, parameters):
        """**ARP:SUBNET** - setSubnetAddr command.
        Also used for:
        - PING:SUBNET
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setSubnetAddr
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setSuperBlock(self, parameters):
        """**SOUR:SUPERBLK** - setSuperBlock command.
        Also used for:
        - TX:SUPERBLK
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setSuperBlock
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setTTL(self, parameters):
        """**PING:TTL** - setTTL command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setTTL
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setTagLevel(self, parameters):
        """**STRM:TAG:LEVEL** - setTagLevel command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setTagLevel
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setTagMode(self, parameters):
        """**STRM:TAG:MODE** - setTagMode command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setTagMode
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setTimeOut(self, parameters):
        """**PING:TIMEOUT** - setTimeOut command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setTimeOut
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setTrafficDuration(self, parameters):
        """**STRM:DURATION** - setTrafficDuration command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setTrafficDuration
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setTrafficLayer(self, parameters):
        """**STRM:TRAFFICLAYER** - setTrafficLayer command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setTrafficLayer
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setTxEnable(self, parameters):
        """**STRM:TXENABLE** - setTxEnable command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setTxEnable
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setTxFcPrim(self, parameters):
        """**SOUR:FCPRIM** - setTxFcPrim command.
        Also used for:
        - TX:FCPRIM
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setTxFcPrim
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setTxPti(self, parameters):
        """**SOUR:PTI** - setTxPti command.
        Also used for:
        - TX:PTI
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setTxPti
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setTxSpare(self, parameters):
        """**SOUR:SPARE** - setTxSpare command.
        Also used for:
        - TX:SPARE
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setTxSpare
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setType(self, parameters):
        """**STRM:FC:TYPE** - setType command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setType
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanCfi1(self, parameters):
        """**STRM:VLANCFI1** - setVlanCfi1 command.
        Also used for:
        - STRM:VLANDEI1
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanCfi1
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanCfi2(self, parameters):
        """**STRM:VLANCFI2** - setVlanCfi2 command.
        Also used for:
        - STRM:VLANDEI2
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanCfi2
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanCfi3(self, parameters):
        """**STRM:VLANCFI3** - setVlanCfi3 command.
        Also used for:
        - STRM:VLANDEI3
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanCfi3
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanCfi4(self, parameters):
        """**STRM:VLANCFI4** - setVlanCfi4 command.
        Also used for:
        - STRM:VLANDEI4
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanCfi4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanFlooding(self, parameters):
        """**SOUR:VLANFLOOD** - setVlanFlooding command.
        Also used for:
        - TX:VLANFLOOD
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setVlanFlooding
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanId1(self, parameters):
        """**STRM:VLANID1** - setVlanId1 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanId1
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanId2(self, parameters):
        """**STRM:VLANID2** - setVlanId2 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanId2
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanId3(self, parameters):
        """**STRM:VLANID3** - setVlanId3 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanId3
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanId4(self, parameters):
        """**STRM:VLANID4** - setVlanId4 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanId4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanQos1(self, parameters):
        """**STRM:VLANQOS1** - setVlanQos1 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanQos1
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanQos2(self, parameters):
        """**STRM:VLANQOS2** - setVlanQos2 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanQos2
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanQos3(self, parameters):
        """**STRM:VLANQOS3** - setVlanQos3 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanQos3
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanQos4(self, parameters):
        """**STRM:VLANQOS4** - setVlanQos4 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanQos4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanTag(self, parameters):
        """**STRM:VLANTAG** - setVlanTag command.
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement setVlanTag
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanTpid1(self, parameters):
        """**STRM:VLANTPID1** - setVlanTpid1 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanTpid1
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanTpid2(self, parameters):
        """**STRM:VLANTPID2** - setVlanTpid2 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanTpid2
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanTpid3(self, parameters):
        """**STRM:VLANTPID3** - setVlanTpid3 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanTpid3
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setVlanTpid4(self, parameters):
        """**STRM:VLANTPID4** - setVlanTpid4 command.
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement setVlanTpid4
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def startCapture(self, parameters):
        """**RX:CAPSTART** - startCapture command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement startCapture
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def stopCapture(self, parameters):
        """**RX:CAPSTOP** - stopCapture command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement stopCapture
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetAlarmType(self, parameters):
        """**SOUR:AL:TYPE?** - txGetAlarmType command.
        Also used for:
        - TX:AL:TYPE?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetAlarmType
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetAutoNeg(self, parameters):
        """**SOUR:AUTO?** - txGetAutoNeg command.
        Also used for:
        - TX:AUTO?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetAutoNeg
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetEmixMode(self, parameters):
        """**SOUR:EMIXMODE?** - txGetEmixMode command.
        Also used for:
        - TX:EMIXMODE?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetEmixMode
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetErrRate(self, parameters):
        """**SOUR:ERR:RATE?** - txGetErrRate command.
        Also used for:
        - TX:ERR:RATE?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetErrRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetErrType(self, parameters):
        """**SOUR:ERR:TYPE?** - txGetErrType command.
        Also used for:
        - TX:ERR:TYPE?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: BIT%d
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetErrType
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetFlowControl(self, parameters):
        """**SOUR:FLOWCONTROL?** - txGetFlowControl command.
        Also used for:
        - TX:FLOWCONTROL?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetFlowControl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetIPReflection(self, parameters):
        """**SOUR:IPR?** - txGetIPReflection command.
        Also used for:
        - TX:IPR?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetIPReflection
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetLaserMode(self, parameters):
        """**SOUR:LASER?** - txGetLaserMode command.
        Also used for:
        - TX:LASER?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetLaserMode
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetLaserPwrUp(self, parameters):
        """**SOUR:LASERPUP?** - txGetLaserPwrUp command.
        Also used for:
        - TX:LASERPUP?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetLaserPwrUp
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetLaserType(self, parameters):
        """**SOUR:LASERTYPE?** - txGetLaserType command.
        Also used for:
        - TX:LASERTYPE?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetLaserType
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetLineControl(self, parameters):
        """**SOUR:LINECONTROL?** - txGetLineControl command.
        Also used for:
        - TX:LINECONTROL?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetLineControl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetMode(self, parameters):
        """**SOUR:STATUS?** - txGetMode command.
        Also used for:
        - TX:STATUS?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetMode
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetPause(self, parameters):
        """**SOUR:PAUSE?** - txGetPause command.
        Also used for:
        - TX:PAUSE?
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetPause
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetReply(self, parameters):
        """**SOUR:REPLY?** - txGetReply command.
        Also used for:
        - TX:REPLY?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetReply
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetRuntSize(self, parameters):
        """**SOUR:ERR:RUNTSIZE?** - txGetRuntSize command.
        Also used for:
        - TX:ERR:RUNTSIZE?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Format: %u
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txGetRuntSize
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txGetSet(self, parameters):
        """**SOUR:SET?** - txGetSet command.
        Also used for:
        - TX:SET?
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Implement query logic
        - Call appropriate veexlib method
        - Return result as bytes
        """
        response = None
        # TODO: Implement txGetSet
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetAlarmType(self, parameters):
        """**SOUR:AL:TYPE** - txSetAlarmType command.
        Also used for:
        - TX:AL:TYPE
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txSetAlarmType
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetAutoNeg(self, parameters):
        """**SOUR:AUTO** - txSetAutoNeg command.
        Also used for:
        - TX:AUTO
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txSetAutoNeg
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetEmixMode(self, parameters):
        """**SOUR:EMIXMODE** - txSetEmixMode command.
        Also used for:
        - TX:EMIXMODE
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txSetEmixMode
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetErrRate(self, parameters):
        """**SOUR:ERR:RATE** - txSetErrRate command.
        Also used for:
        - TX:ERR:RATE
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement txSetErrRate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetErrType(self, parameters):
        """**SOUR:ERR:TYPE** - txSetErrType command.
        Also used for:
        - TX:ERR:TYPE
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement txSetErrType
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetFlowControl(self, parameters):
        """**SOUR:FLOWCONTROL** - txSetFlowControl command.
        Also used for:
        - TX:FLOWCONTROL
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement txSetFlowControl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetIPReflection(self, parameters):
        """**SOUR:IPR** - txSetIPReflection command.
        Also used for:
        - TX:IPR
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txSetIPReflection
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetLaserMode(self, parameters):
        """**SOUR:LASER** - txSetLaserMode command.
        Also used for:
        - TX:LASER
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txSetLaserMode
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetLaserPwrUp(self, parameters):
        """**SOUR:LASERPUP** - txSetLaserPwrUp command.
        Also used for:
        - TX:LASERPUP
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txSetLaserPwrUp
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetLaserType(self, parameters):
        """**SOUR:LASERTYPE** - txSetLaserType command.
        Also used for:
        - TX:LASERTYPE
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txSetLaserType
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetLineControl(self, parameters):
        """**SOUR:LINECONTROL** - txSetLineControl command.
        Also used for:
        - TX:LINECONTROL
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement txSetLineControl
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetMode(self, parameters):
        """**SOUR:MODE** - txSetMode command.
        Also used for:
        - TX:MODE
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txSetMode
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetPause(self, parameters):
        """**SOUR:PAUSE** - txSetPause command.
        Also used for:
        - TX:PAUSE
        
        C++ Implementation Details:
        - C++ implementation not found in ScpiPacket.cpp
        - Check C++ source for implementation details
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement txSetPause
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetReply(self, parameters):
        """**SOUR:REPLY** - txSetReply command.
        Also used for:
        - TX:REPLY
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement txSetReply
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def txSetRuntSize(self, parameters):
        """**SOUR:ERR:RUNTSIZE** - txSetRuntSize command.
        Also used for:
        - TX:ERR:RUNTSIZE
        
        C++ Implementation Details:
        - Uses callGetAllSettings() and/or callGetAllowedSettings()
        - Takes parameters from command string
        
        Python TODO:
        - Parse parameters using ParseUtils.preParseParameters()
        - Validate parameter values
        - Call appropriate veexlib method to set value
        - Return None on success or error response
        """
        response = None
        # TODO: Implement txSetRuntSize
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetActivate(self, parameters):
        """**Y1564:ACT?** - y1564GetActivate command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetActivate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetCir(self, parameters):
        """**Y1564:CIR?** - y1564GetCir command.
        
        C++ Implementation Details:
        - Format: %.2f %%
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetCir
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetCirEir(self, parameters):
        """**Y1564:CIREIR?** - y1564GetCirEir command.
        
        C++ Implementation Details:
        - Format: %.2f %%
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetCirEir
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetEnable(self, parameters):
        """**Y1564:ENABLE?** - y1564GetEnable command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetEnable
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetJitPerf(self, parameters):
        """**Y1564:JITPERF?** - y1564GetJitPerf command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetJitPerf
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetLatPerf(self, parameters):
        """**Y1564:LATPERF?** - y1564GetLatPerf command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetLatPerf
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetLossPerf(self, parameters):
        """**Y1564:LOSSPERF?** - y1564GetLossPerf command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetLossPerf
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetMaskStep(self, parameters):
        """**Y1564:MASKSTEP?** - y1564GetMaskStep command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetMaskStep
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetMaxJit(self, parameters):
        """**Y1564:MAXJIT?** - y1564GetMaxJit command.
        
        C++ Implementation Details:
        - Format: %.3f
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetMaxJit
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetMaxLat(self, parameters):
        """**Y1564:MAXLAT?** - y1564GetMaxLat command.
        
        C++ Implementation Details:
        - Format: %.3f
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetMaxLat
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetMaxLoss(self, parameters):
        """**Y1564:MAXLOSS?** - y1564GetMaxLoss command.
        
        C++ Implementation Details:
        - Format: %.2f %%
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetMaxLoss
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetPerf(self, parameters):
        """**Y1564:PERF?** - y1564GetPerf command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetPerf
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetPerfDur(self, parameters):
        """**Y1564:PERFDUR?** - y1564GetPerfDur command.
        
        C++ Implementation Details:
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetPerfDur
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetPerfStatus(self, parameters):
        """**Y1564:PERFSTATUS?** - y1564GetPerfStatus command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetPerfStatus
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetRamp(self, parameters):
        """**Y1564:RAMP?** - y1564GetRamp command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetRamp
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetRampStatus(self, parameters):
        """**Y1564:RAMPSTATUS?** - y1564GetRampStatus command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetRampStatus
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetRateStep(self, parameters):
        """**Y1564:RATESTEP?** - y1564GetRateStep command.
        
        C++ Implementation Details:
        - Format: %.2f %%
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetRateStep
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetRxPerf(self, parameters):
        """**Y1564:RXPERF?** - y1564GetRxPerf command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetRxPerf
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetSeqPerf(self, parameters):
        """**Y1564:SEQPERF?** - y1564GetSeqPerf command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetSeqPerf
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetServiceName(self, parameters):
        """**Y1564:SERVICENAME?** - y1564GetServiceName command.
        
        C++ Implementation Details:
        - Format: %s
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetServiceName
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetStep(self, parameters):
        """**Y1564:STEP?** - y1564GetStep command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetStep
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564GetTrialDur(self, parameters):
        """**Y1564:TRIALDUR?** - y1564GetTrialDur command.
        
        C++ Implementation Details:
        - Format: %d
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564GetTrialDur
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564SetActivate(self, parameters):
        """**Y1564:ACT** - y1564SetActivate command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564SetActivate
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564SetCir(self, parameters):
        """**Y1564:CIR** - y1564SetCir command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564SetCir
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564SetCirEir(self, parameters):
        """**Y1564:CIREIR** - y1564SetCirEir command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564SetCirEir
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564SetEnable(self, parameters):
        """**Y1564:ENABLE** - y1564SetEnable command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564SetEnable
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564SetFactoryDeflt(self, parameters):
        """**Y1564:DEFAULT** - y1564SetFactoryDeflt command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564SetFactoryDeflt
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564SetMaskStep(self, parameters):
        """**Y1564:MASKSTEP** - y1564SetMaskStep command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564SetMaskStep
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564SetMaxJit(self, parameters):
        """**Y1564:MAXJIT** - y1564SetMaxJit command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564SetMaxJit
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564SetMaxLat(self, parameters):
        """**Y1564:MAXLAT** - y1564SetMaxLat command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564SetMaxLat
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564SetMaxLoss(self, parameters):
        """**Y1564:MAXLOSS** - y1564SetMaxLoss command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564SetMaxLoss
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564SetPerfDur(self, parameters):
        """**Y1564:PERFDUR** - y1564SetPerfDur command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564SetPerfDur
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564SetRateStep(self, parameters):
        """**Y1564:RATESTEP** - y1564SetRateStep command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564SetRateStep
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564SetServiceName(self, parameters):
        """**Y1564:SERVICENAME** - y1564SetServiceName command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564SetServiceName
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def y1564SetTrialDur(self, parameters):
        """**Y1564:TRIALDUR** - y1564SetTrialDur command.
        
        C++ Implementation Details:
        - Takes parameters from command string
        
        Python TODO:
        - Implement command logic
        - Follow C++ implementation pattern
        """
        response = None
        # TODO: Implement y1564SetTrialDur
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)


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

