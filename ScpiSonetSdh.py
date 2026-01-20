###############################################################################
#
# Copyright 2018-2019, VeEX, Inc.
# All Rights Reserved.
#
# $Workfile:   ScpiSonetSdh.py  $
# $Revision: 21408 $
# $Author: patrickellis $
# $Date: 2020-03-23 20:15:04 -0400 (Mon, 23 Mar 2020) $
#
# DESCRIPTION:
#    Module to process SONET/SDH SCPI commands.
#
###############################################################################

from ErrorCodes import ScpiErrorCode
from ErrorCodes import errorResponse
from ParseUtils import CommandTableEntry as Cmnd
from SessionGlobals import SessionGlobals
import ParseUtils
#import SessionGlobals
import veexlib


class ScpiSonetSdh(object):
    #'''This class processes text SONET/SDH SCPI commands and returns a text
    #response.
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


    def getTxPassthru(self, parameters):
        '''**TX:PASSthru?** -
        Query the passthru mode is enabled state.
        '''
        self.globals.veexSonetSdh.sets.update()
        if self.globals.veexSonetSdh.sets.passthruMode:
            response = b"ON"
        else:
            response = b"OFF"
        return response

    def setTxPassthru(self, parameters):
        '''**TX:PASSthru <ON|OFF>** -
        Sets the passthru mode enable/disable state.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ON"):
                self.globals.veexSonetSdh.sets.passthruMode = True
            elif paramList[0].head.upper().startswith(b"OFF"):
                self.globals.veexSonetSdh.sets.passthruMode = False
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response


    def getTxCoupled(self, parameters):
        '''**TX:COUPled?** -
        Query if coupled or independent.
        '''
        self.globals.veexSonetSdh.sets.update()
        if (self.globals.veexSonetSdh.sets.settingsControl == veexlib.COUPLED_TX_INTO_RX) or \
           (self.globals.veexSonetSdh.sets.settingsControl == veexlib.COUPLED_RX_INTO_TX):
            response = b"YES"
        elif self.globals.veexSonetSdh.sets.settingsControl == veexlib.INDEPENDENT_TX_RX:
            response = b"NO"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setTxCoupled(self, parameters):
        '''**TX:COUPled <YES|NO>** -
        Sets to coupled or independent.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"YES"):
                self.globals.veexSonetSdh.sets.settingsControl = veexlib.COUPLED_TX_INTO_RX
            elif paramList[0].head.upper().startswith(b"NO"):
                self.globals.veexSonetSdh.sets.settingsControl = veexlib.INDEPENDENT_TX_RX
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response


    def getTxClock(self, parameters):
        '''**TX:CLOCK?** -
        Query the TX clock reference source.
        '''
        self.globals.veexSonetSdh.sets.update()
        if self.globals.veexSonetSdh.sets.clockType == veexlib.CLOCK_INTERNAL:
            response = b"INT"
        elif self.globals.veexSonetSdh.sets.clockType == veexlib.CLOCK_RECOVERED:
            response = b"LOOP"
        elif self.globals.veexSonetSdh.sets.clockType == veexlib.CLOCK_BITS_SETS:
            response = b"BITS/SETS"
        elif self.globals.veexSonetSdh.sets.clockType == veexlib.CLOCK_BITS:
            response = b"BITS"
        elif self.globals.veexSonetSdh.sets.clockType == veexlib.CLOCK_SETS:
            response = b"SETS"
        elif self.globals.veexSonetSdh.sets.clockType == veexlib.CLOCK_EXT_8KHZ:
            response = b"EXT8KHZ"
        elif self.globals.veexSonetSdh.sets.clockType == veexlib.CLOCK_EXT_BITS:
            response = b"EXT1_5MHZ"
        elif self.globals.veexSonetSdh.sets.clockType == veexlib.CLOCK_EXT_SETS:
            response = b"EXT2MHZ"
        elif self.globals.veexSonetSdh.sets.clockType == veexlib.CLOCK_EXT_10MHZ:
            response = b"EXT10MHZ"
        elif self.globals.veexSonetSdh.sets.clockType == veexlib.CLOCK_SYNC:
            response = b"SYNC"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setTxClock(self, parameters):
        '''**TX:CLOCK <source>** -
        Set the TX clock reference source.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"INT"):
                self.globals.veexSonetSdh.sets.clockType = veexlib.CLOCK_INTERNAL
            elif paramList[0].head.upper().startswith(b"LOOP"):
                self.globals.veexSonetSdh.sets.clockType = veexlib.CLOCK_RECOVERED
            elif paramList[0].head.upper().startswith(b"BITS/SETS"):
                self.globals.veexSonetSdh.sets.clockType = veexlib.CLOCK_BITS_SETS
            elif paramList[0].head.upper().startswith(b"BITS"):
                self.globals.veexSonetSdh.sets.clockType = veexlib.CLOCK_BITS
            elif paramList[0].head.upper().startswith(b"SETS"):
                self.globals.veexSonetSdh.sets.clockType = veexlib.CLOCK_SETS
            elif paramList[0].head.upper().startswith(b"EXT8KHZ"):
                self.globals.veexSonetSdh.sets.clockType = veexlib.CLOCK_EXT_8KHZ
            elif paramList[0].head.upper().startswith(b"EXT1_5MHZ"):
                self.globals.veexSonetSdh.sets.clockType = veexlib.CLOCK_EXT_BITS
            elif paramList[0].head.upper().startswith(b"EXT2MHZ"):
                self.globals.veexSonetSdh.sets.clockType = veexlib.CLOCK_EXT_SETS
            elif paramList[0].head.upper().startswith(b"EXT10MHZ"):
                self.globals.veexSonetSdh.sets.clockType = veexlib.CLOCK_EXT_10MHZ
            elif paramList[0].head.upper().startswith(b"SYNC"):
                self.globals.veexSonetSdh.sets.clockType = veexlib.CLOCK_SYNC
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response


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


    def getTxFreq(self, parameters):
        '''**TX:FREQuency?** -
        Query the measured TX line frequency.
        '''
        self.globals.veexPhy.stats.update()
        return b"%d Hz" % self.globals.veexPhy.stats.freqTx

    def getTxFreqOffsetPpm(self, parameters):
        '''**TX:FREQOFFset:PPM?** -
        Query the offset from nominal measured TX line frequency in PPM.
        '''
        self.globals.veexPhy.stats.update()
        return b"%0.2f ppm" % self.globals.veexPhy.stats.freqOffsetTxPpm

    def getTxFreqOffsetHz(self, parameters):
        '''**TX:FREQOFFset:HZ?** -
        Query the offset from nominal measured TX line frequency in Hz.
        '''
        self.globals.veexPhy.stats.update()
        return b"%d Hz" % self.globals.veexPhy.stats.freqOffsetTxHz


    def getTxFreqOffLine(self, parameters):
        '''**TX:FREQOFFset:LINE?** -
        Query the TX line frequency setting.
        '''
        self.globals.veexPhy.sets.update()
        if (self.globals.veexPhy.sets.lineFreqOffset == 0.0) and \
           (self.globals.veexPhy.sets.lineFreqRampStart == 0.0):
            response = b"OFF"
        elif ((self.globals.veexPhy.sets.lineFreqRampStart        !=        \
               self.globals.veexPhy.sets.lineFreqOffset)                and \
              (self.globals.veexPhy.sets.lineFreqRampStepDuration != 0) and \
              (self.globals.veexPhy.sets.lineFreqRampStepSize     != 0.0)):
            response = b"%.1f %.1f %d %.1f" % (                                \
                           self.globals.veexPhy.sets.lineFreqOffset,           \
                           self.globals.veexPhy.sets.lineFreqRampStart,        \
                           self.globals.veexPhy.sets.lineFreqRampStepDuration, \
                           self.globals.veexPhy.sets.lineFreqRampStepSize)
        else:
            response = b"%.1f ppm" % self.globals.veexPhy.sets.lineFreqOffset
        return response

    def setTxFreqOffLine(self, parameters):
        '''**TX:FREQOFFset:LINE <float freq | set of 4 ramp freq settings>** -
        Set the TX line frequency setting.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) == 1:
            if ParseUtils.isFloatE(paramList[0].head):
                self.globals.veexPhy.sets.lineFreqOffset = float(paramList[0].head)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        elif len(paramList) < 4:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        else:
            if not (ParseUtils.isFloatE(paramList[0].head) and \
                    ParseUtils.isFloatE(paramList[1].head) and \
                    paramList[2].head.isdigit() and \
                    ParseUtils.isFloatE(paramList[3].head)):
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            else:
                lineFreqOffset           = float(paramList[0].head)
                lineFreqRampStart        = float(paramList[1].head)
                lineFreqRampStepDuration =   int(paramList[2].head)
                lineFreqRampStepSize     = float(paramList[3].head)
                if (lineFreqOffset           == lineFreqRampStart) or \
                   (lineFreqRampStepDuration == 0)                 or \
                   (lineFreqRampStepSize     == 0.0):
                    response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
                else:
                    self.globals.veexPhy.sets.setLineFreqRamp(lineFreqOffset, \
                                                              lineFreqRampStart, \
                                                              lineFreqRampStepSize, \
                                                              lineFreqRampStepDuration)
        return response


    def getRxFreq(self, parameters):
        '''**RX:FREQuency?** -
        Query the measured RX line frequency. Would use PHY stats, but that is
        per lane.
        '''
        self.globals.veexSonetSdh.stats.update()
        return b"%d Hz" % self.globals.veexSonetSdh.stats.freqRx

    def getRxFreqOffsetPpm(self, parameters):
        '''**RX:FREQOFFset:PPM?** -
        Query the offset from nominal measured RX line frequency in PPM.
        Would use PHY stats, but that is per lane.
        '''
        self.globals.veexSonetSdh.stats.update()
        return b"%0.2f ppm" % self.globals.veexSonetSdh.stats.freqOffsetRxPpm

    def getRxFreqOffsetHz(self, parameters):
        '''**RX:FREQOFFset:HZ?** -
        Query the offset from nominal measured RX line frequency in Hz.
        Would use PHY stats, but that is per lane.
        '''
        self.globals.veexSonetSdh.stats.update()
        return b"%d Hz" % self.globals.veexSonetSdh.stats.freqOffsetRxHz


    def getRxOptPwr(self, parameters):
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
            response = b"Electical LAN"
        elif (self.globals.veexPhy.stats.signalStrength < -99.6999) and \
             (self.globals.veexPhy.stats.signalStrength > -99.7001):
            response = b"No Measurement"
        elif self.globals.veexPhy.stats.signalStrength < -50:
            response = b"Loss of Power";
        else:
            response = b"%.2f dBm" % self.globals.veexPhy.stats.signalStrength
        return response


# This table contains all the system SCPI commands. Note that queries must
# come before the matching setting commands. Also if two commands start with
# the same text then the longer one must come first.
commandTable = [
    Cmnd(b"TX:PASSthru?",          ScpiSonetSdh.getTxPassthru),
    Cmnd(b"TX:PASSthru",           ScpiSonetSdh.setTxPassthru),
    Cmnd(b"TX:COUPled?",           ScpiSonetSdh.getTxCoupled),
    Cmnd(b"TX:COUPled",            ScpiSonetSdh.setTxCoupled),
    Cmnd(b"TX:CLOCK?",             ScpiSonetSdh.getTxClock),
    Cmnd(b"TX:CLOCK",              ScpiSonetSdh.setTxClock),
    Cmnd(b"TX:LASERPUP?",          ScpiSonetSdh.getTxLaserPwrUp),
    Cmnd(b"TX:LASERPUP",           ScpiSonetSdh.setTxLaserPwrUp),
    Cmnd(b"TX:LASER?",             ScpiSonetSdh.getTxLaser),
    Cmnd(b"TX:LASER",              ScpiSonetSdh.setTxLaser),
    Cmnd(b"TX:FREQuency?",         ScpiSonetSdh.getTxFreq),
    Cmnd(b"TX:FREQOFFset:PPM?",    ScpiSonetSdh.getTxFreqOffsetPpm),
    Cmnd(b"TX:FREQOFFset:HZ?",     ScpiSonetSdh.getTxFreqOffsetHz),
    Cmnd(b"TX:FREQOFFset:LINE?",   ScpiSonetSdh.getTxFreqOffLine),
    Cmnd(b"TX:FREQOFFset:LINE",    ScpiSonetSdh.setTxFreqOffLine),

    Cmnd(b"RX:COUPled?",           ScpiSonetSdh.getTxCoupled),
    Cmnd(b"RX:COUPled",            ScpiSonetSdh.setTxCoupled),
    Cmnd(b"RX:FREQuency?",         ScpiSonetSdh.getRxFreq),
    Cmnd(b"RX:FREQOFFset:PPM?",    ScpiSonetSdh.getRxFreqOffsetPpm),
    Cmnd(b"RX:FREQOFFset:HZ?",     ScpiSonetSdh.getRxFreqOffsetHz),
    Cmnd(b"RX:OPP?",               ScpiSonetSdh.getRxOptPwr),
    ]



# This converts the above table into a tree of lists that can be searched
# for commands. Doing this here and not in the class init means it is done
# once at boot and not at the start of each user session.
commandTreeRoot = []
ParseUtils.processCommandTableIntoTree(commandTable, commandTreeRoot)


if __name__ == "__main__":
    pass

