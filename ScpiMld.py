###############################################################################
#
# Copyright 2018-2019, VeEX, Inc.
# All Rights Reserved.
#
# $Workfile:   ScpiMld.py  $
# $Revision: 21555 $
# $Author: hzhang $
# $Date: 2020-04-17 02:04:43 -0400 (Fri, 17 Apr 2020) $
#
# DESCRIPTION:
#    Module to process MLD SCPI commands.
#
###############################################################################

from ErrorCodes import ScpiErrorCode
from ErrorCodes import errorResponse
from ParseUtils import CommandTableEntry as Cmnd
from SessionGlobals import SessionGlobals
import ParseUtils
#import SessionGlobals
import veexlib
import math
#from builtins import False, True
#from locale import atof


class ScpiMld(object):
    #'''This class processes text MLD SCPI commands and returns a text response.
    #
    #Args:
    #    globals (SessionGlobals object): Data class of session variables.
    #'''

    # Dictionary to convert between ProtoBuf enum and SPCI text for TX/RX PCS Alarm type.
    MldVirtAlarmsTypeTable = {
        veexlib.PCS_OTL_ALARM_OFF                         : b"OFF",
        veexlib.PCS_OTL_ALARM_BLOCK_LOCK_LOSS             : b"BLKLOC",
        veexlib.PCS_OTL_ALARM_LOA                         : b"LOA",
        veexlib.PCS_OTL_ALARM_ALIGNMENT_MARKER_LOSS       : b"LOALM",
        veexlib.PCS_OTL_ALARM_RS_FEC_ALIGN_MARK_LOSS      : b"LOAMPS",
        veexlib.PCS_OTL_ALARM_RS_FEC_ALIGN_MARK_LOSS_LANE : b"LOA",
        veexlib.PCS_OTL_ALARM_HI_BER                      : b"HIBER",
        veexlib.PCS_OTL_ALARM_HI_SER                      : b"HISER",
        veexlib.PCS_OTL_ALARM_RS_FEC_LOA                  : b"FECLOA",
        veexlib.PCS_OTL_ALARM_RS_FEC_STRESS               : b"FECSTRESS",
        veexlib.PCS_OTL_ALARM_RS_FEC_STRESS_CHANNEL_A     : b"FECSTRESSA",
        veexlib.PCS_OTL_ALARM_RS_FEC_STRESS_CHANNEL_B     : b"FECSTRESSB",
        veexlib.PCS_OTL_ALARM_RS_FEC_LOCAL_SER_DEGRADED   : b"LOCALDEGSER",
        veexlib.PCS_OTL_ALARM_RS_FEC_REM_SER_DEGRADED     : b"REMDEGSER",
        }
    
    # Dictionary to convert between ProtoBuf enum and SPCI text for TX/RX PCS Error type.
    MldVirtErrorsTypeTable = {
        veexlib.PCS_OTL_ERR_NONE                             : b"NONE",
        veexlib.PCS_OTL_ERR_INVALID_SYNC_HEADER              : b"SYNCHDR",
        veexlib.PCS_OTL_ERR_INVALID_ALIGNMENT_MARKER         : b"ALMARK",
        veexlib.PCS_OTL_ERR_BIP_8                            : b"BIP8",
        veexlib.PCS_OTL_ERR_RS_FEC_CORRECTABLE_A_LANE        : b"FECCORSYMA",
        veexlib.PCS_OTL_ERR_RS_FEC_CORRECTABLE_B_LANE        : b"FECCORSYMB",
        veexlib.PCS_OTL_ERR_BLOCK                            : b"BLOCK",
        veexlib.PCS_OTL_ERR_RS_FEC_CORRECTABLE               : b"FECCOR",
        veexlib.PCS_OTL_ERR_RS_FEC_UNCORRECTABLE             : b"FECUNCOR",
        veexlib.PCS_OTL_ERR_RS_FEC_TRANSCODE                 : b"FECCODE",
        veexlib.PCS_OTL_ERR_RS_FEC_CHAN_A_CORRECTABLE_SYMBOL : b"FECCORSYMA",
        veexlib.PCS_OTL_ERR_RS_FEC_CHAN_B_CORRECTABLE_SYMBOL : b"FECCORSYMB",
        veexlib.PCS_OTL_ERR_RS_FEC_CHAN_A_UNCORRECTABLE      : b"FECUNCORA",
        veexlib.PCS_OTL_ERR_RS_FEC_CHAN_B_UNCORRECTABLE      : b"FECUNCORB",
        veexlib.PCS_OTL_ERR_RS_FEC_ALIGN_MARKER_PAD          : b"FECALMARKPAD",
        }

    # Dictionary to convert between ProtoBuf enum and SPCI text for TX/RX interface type. 
    # TBD - a lot of members will be added later   
    MldInterfaceTable = {
        (veexlib.PHY_INTERFACE_OFF, veexlib.PHY_INTERFACE_TYPE_CFP4)                           : b"NOT_ASSIGNED",
        (veexlib.PHY_INTERFACE_OFF, veexlib.PHY_INTERFACE_TYPE_CFP8)                           : b"NOT_ASSIGNED",
        (veexlib.PHY_INTERFACE_OFF, veexlib.PHY_INTERFACE_TYPE_QSFP)                           : b"NOT_ASSIGNED",
        (veexlib.PHY_INTERFACE_OFF, veexlib.PHY_INTERFACE_TYPE_SFP)                            : b"NOT_ASSIGNED",
        (veexlib.PHY_INTERFACE_OFF, veexlib.PHY_INTERFACE_TYPE_QSFP_DD56)                      : b"NOT_ASSIGNED",
        (veexlib.PHY_INTERFACE_OFF, veexlib.PHY_INTERFACE_TYPE_QSFP_DD28)                      : b"NOT_ASSIGNED",
        (veexlib.PHY_INTERFACE_OFF, veexlib.PHY_INTERFACE_TYPE_QSFP_DD10)                      : b"NOT_ASSIGNED",
        (veexlib.PHY_INTERFACE_OFF, veexlib.PHY_INTERFACE_TYPE_QSFP56)                         : b"NOT_ASSIGNED",
        (veexlib.PHY_INTERFACE_OFF, veexlib.PHY_INTERFACE_TYPE_QSFP28)                         : b"NOT_ASSIGNED",
        (veexlib.PHY_INTERFACE_OFF, veexlib.PHY_INTERFACE_TYPE_QSFP10)                         : b"NOT_ASSIGNED",
        (veexlib.PHY_INTERFACE_OFF, veexlib.PHY_INTERFACE_TYPE_SFP56)                          : b"NOT_ASSIGNED",
        (veexlib.PHY_INTERFACE_OFF, veexlib.PHY_INTERFACE_TYPE_SFP28)                          : b"NOT_ASSIGNED",
        (veexlib.PHY_INTERFACE_OFF, veexlib.PHY_INTERFACE_TYPE_SFP10)                          : b"NOT_ASSIGNED",
        (veexlib.PHY_INTERFACE_OFF, veexlib.PHY_INTERFACE_TYPE_CFP)                            : b"NOT_ASSIGNED",
        (veexlib.PHY_INTERFACE_40G_OC_768_STM_256_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_CFP4)   : b"STM256_OC768_UNFRAMED_BERT_CFP",
        (veexlib.PHY_INTERFACE_40G_OC_768_STM_256_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_QSFP)   : b"STM256_OC768_UNFRAMED_BERT_QSFP",
        (veexlib.PHY_INTERFACE_40G_OC_768_STM_256_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_QSFP10) : b"STM256_OC768_UNFRAMED_BERT_QSFP",
        (veexlib.PHY_INTERFACE_40G_OC_768_STM_256_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_CFP4)   : b"STM256_OC768_UNFRAMED_BERT",
        (veexlib.PHY_INTERFACE_41G_ETHERNET_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_CFP4)         : b"41_25G_LAN_UNFRAMED_BERT_CFP",
        (veexlib.PHY_INTERFACE_41G_ETHERNET_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_QSFP)         : b"41_25G_LAN_UNFRAMED_BERT_QSFP",
        (veexlib.PHY_INTERFACE_41G_ETHERNET_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_QSFP10)       : b"41_25G_LAN_UNFRAMED_BERT_QSFP",
        (veexlib.PHY_INTERFACE_41G_ETHERNET_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_CFP4)         : b"41_25G_LAN_UNFRAMED_BERT",
        (veexlib.PHY_INTERFACE_43G_OTU_3_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_CFP4)            : b"G709_43G_UNFRAMED_BERT_CFP",
        (veexlib.PHY_INTERFACE_43G_OTU_3_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_QSFP)            : b"G709_43G_UNFRAMED_BERT_QSFP",
        (veexlib.PHY_INTERFACE_43G_OTU_3_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_QSFP10)          : b"G709_43G_UNFRAMED_BERT_QSFP",
        (veexlib.PHY_INTERFACE_43G_OTU_3_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_CFP4)            : b"G709_43G_UNFRAMED_BERT",
        (veexlib.PHY_INTERFACE_103G_ETHERNET_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_CFP4)        : b"103_125G_LAN_UNFRAMED_BERT_CFP",
        (veexlib.PHY_INTERFACE_103G_ETHERNET_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_QSFP)        : b"103_125G_LAN_UNFRAMED_BERT_QSFP",
        (veexlib.PHY_INTERFACE_103G_ETHERNET_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_QSFP28)      : b"103_125G_LAN_UNFRAMED_BERT_QSFP",
        (veexlib.PHY_INTERFACE_103G_ETHERNET_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_QSFP56)      : b"103_125G_LAN_UNFRAMED_BERT_QSFP56",
        (veexlib.PHY_INTERFACE_103G_ETHERNET_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_CFP4)        : b"103_125G_LAN_UNFRAMED_BERT",
        (veexlib.PHY_INTERFACE_112G_OTU_4_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_CFP4)           : b"G709_112G_UNFRAMED_BERT_CFP",
        (veexlib.PHY_INTERFACE_112G_OTU_4_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_QSFP)           : b"G709_112G_UNFRAMED_BERT_QSFP",
        (veexlib.PHY_INTERFACE_112G_OTU_4_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_QSFP28)         : b"G709_112G_UNFRAMED_BERT_QSFP",
        (veexlib.PHY_INTERFACE_112G_OTU_4_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_QSFP56)         : b"G709_112G_UNFRAMED_BERT_QSFP56",
        (veexlib.PHY_INTERFACE_112G_OTU_4_UNFRAMED, veexlib.PHY_INTERFACE_TYPE_CFP4)           : b"G709_112G_UNFRAMED_BERT",
        (veexlib.PHY_INTERFACE_41G_FRAMED_PCS_BERT, veexlib.PHY_INTERFACE_TYPE_CFP4)           : b"41_25G_LAN_PCS_BERT_CFP",
        (veexlib.PHY_INTERFACE_41G_FRAMED_PCS_BERT, veexlib.PHY_INTERFACE_TYPE_QSFP)           : b"41_25G_LAN_PCS_BERT_QSFP",
        (veexlib.PHY_INTERFACE_41G_FRAMED_PCS_BERT, veexlib.PHY_INTERFACE_TYPE_QSFP10)         : b"41_25G_LAN_PCS_BERT_QSFP",
        (veexlib.PHY_INTERFACE_41G_FRAMED_PCS_BERT, veexlib.PHY_INTERFACE_TYPE_CFP4)           : b"41_25G_LAN_PCS_BERT",
        }


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

    def getTxAlarmOptType(self, parameters):
        '''**TX:ALarm:OPTicaltype? <lane|ALL>** -
        Query the current protocol processor for the Optical Alarm Type it is generating, 
        for the specified Optical Lane number.
        '''
        self.globals.veexPhy.sets.update()
        self.globals.veexPhy.allowedSets.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        if len(paramList) >= 1:
            laneCount = self.globals.veexPhy.allowedSets.txOpticalLaneCount
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value >= 0:
                if value >= laneCount:
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                else:
                    if self.globals.veexPhy.sets.opticalAlarmGenType[value] == veexlib.PHY_ALARM_OFF:
                        response = b"OFF"
                    elif self.globals.veexPhy.sets.opticalAlarmGenType[value] == veexlib.PHY_ALARM_LOS:
                        response = b"LOS"
                    else:
                        response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
            elif paramList[0].head.upper().startswith(b"ALL"):
                for i in range(laneCount):
                    if self.globals.veexPhy.sets.opticalAlarmGenType[i] == veexlib.PHY_ALARM_OFF:
                        if len(response) != 0:
                            response += b", "
                        response += b"OFF"
                    elif self.globals.veexPhy.sets.opticalAlarmGenType[i] == veexlib.PHY_ALARM_LOS:
                        if len(response) != 0:
                            response += b", "
                        response += b"LOS"
                if len(response) == 0:
                    response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
            else:
                response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response
    
    def setTxAlarmOptType(self, parameters):
        '''**TX:ALarm:OPTicaltype:<lane|ALL> <OFF|LOS>** -
        Sets the Optical Alarm Type to be generated, for the specified Optical Lane number.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 2:
            isAlarmType = False
            if paramList[1].head.upper().startswith(b"OFF"):
                alarmType = veexlib.PHY_ALARM_OFF
                isAlarmType = True
            elif paramList[1].head.upper().startswith(b"LOS"):
                alarmType = veexlib.PHY_ALARM_LOS
                isAlarmType = True
            if isAlarmType:
                self.globals.veexPhy.allowedSets.update()
                value = ParseUtils.checkNumeric(paramList[0].head)
                if value >= 0:
                    if value < self.globals.veexPhy.allowedSets.txOpticalLaneCount:
                        opticalAlarmGenType = self.globals.veexPhy.sets.opticalAlarmGenType
                        opticalAlarmGenType[value] = alarmType
                        self.globals.veexPhy.sets.opticalAlarmGenType = opticalAlarmGenType
                    else:
                        response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                elif paramList[0].head.upper().startswith(b"ALL"):
                    opticalAlarmGenType = self.globals.veexPhy.sets.opticalAlarmGenType
                    for i in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
                        opticalAlarmGenType[i] = alarmType
                    self.globals.veexPhy.sets.opticalAlarmGenType = opticalAlarmGenType 
                else:
                    response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response    

    def getTxAlarmVirType(self, parameters):
        '''**TX:ALarm:TYPE? <position>** -
        Queries whether any alarm types are actively being generated, 
        either at the global level or on individual Logical/PCS lanes.
        '''
        self.globals.veexPcs.sets.update()
        self.globals.veexPcs.allowedSets.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        if len(paramList) == 0:
            if self.globals.veexPcs.sets.alarmGenType in ScpiMld.MldVirtAlarmsTypeTable.keys():
                response = ScpiMld.MldVirtAlarmsTypeTable[self.globals.veexPcs.sets.alarmGenType]
            else:
                response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        elif len(paramList) >= 1:
            laneCount = self.globals.veexPcs.allowedSets.txVirtualLaneCount
            value = ParseUtils.checkNumeric(paramList[0].head)
            if laneCount == 0 or laneCount == 1:
                if value == 0:
                    if self.globals.veexPcs.sets.alarmGenType in ScpiMld.MldVirtAlarmsTypeTable.keys():
                        response = ScpiMld.MldVirtAlarmsTypeTable[self.globals.veexPcs.sets.alarmGenType]
                    else:
                        response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
                else:
                    response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            elif value >= 0:
                if value >= laneCount:
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                else:
                    if self.globals.veexPcs.sets.laneAlarmGenType[value] in ScpiMld.MldVirtAlarmsTypeTable.keys():
                        response = ScpiMld.MldVirtAlarmsTypeTable[self.globals.veexPcs.sets.laneAlarmGenType[value]]
                    else:
                        response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
            elif paramList[0].head.upper().startswith(b"ALL"):
                for i in range(laneCount):
                    if self.globals.veexPcs.sets.laneAlarmGenType[i] in ScpiMld.MldVirtAlarmsTypeTable.keys():
                        if len(response) != 0:
                            response += b", "
                        response += ScpiMld.MldVirtAlarmsTypeTable[self.globals.veexPcs.sets.laneAlarmGenType[i]]
                if len(response) == 0:
                    response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
            else:
                response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
        else:
            if self.globals.veexPcs.sets.alarmGenType in ScpiMld.MldVirtAlarmsTypeTable.keys():
                response = ScpiMld.MldVirtAlarmsTypeTable[self.globals.veexPcs.sets.alarmGenType]
            else:
                response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response 

    def setTxAlarmVirType(self, parameters):
        '''**TX:ALarm:TYPE:<lane|ALL> <value>** -
        Sets the Alarm Type to be generated on one or all Logical/PCS lanes.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) == 1:
            isAlarmType = False
            for key, value in ScpiMld.MldVirtAlarmsTypeTable.items():
                if paramList[0].head.upper().startswith(value):
                    isAlarmType = True
                    alarmType = key
                    break
            if isAlarmType:
                self.globals.veexPcs.sets.alarmGenType = alarmType
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        elif len(paramList) >= 2:
            isAlarmType = False
            for key, value in ScpiMld.MldVirtAlarmsTypeTable.items():
                if paramList[1].head.upper().startswith(value):
                    isAlarmType = True
                    alarmType = key
                    break
            if isAlarmType:
                self.globals.veexPcs.allowedSets.update()
                laneCount = self.globals.veexPcs.allowedSets.txVirtualLaneCount
                value = ParseUtils.checkNumeric(paramList[0].head)
                if laneCount == 0 or laneCount == 1:
                    if value == 0:
                        self.globals.veexPcs.sets.alarmGenType = alarmType
                    else:  
                        response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE) 
                elif value >= 0:
                    if value < laneCount:
                        laneAlarmGenType = self.globals.veexPcs.sets.laneAlarmGenType
                        laneAlarmGenType[value] = alarmType
                        self.globals.veexPcs.sets.laneAlarmGenType = laneAlarmGenType
                    else:
                        response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                elif paramList[0].head.upper().startswith(b"ALL"):
                    laneAlarmGenType = self.globals.veexPcs.sets.laneAlarmGenType
                    for i in range(laneCount):
                        laneAlarmGenType[i] = alarmType
                    self.globals.veexPcs.sets.laneAlarmGenType = laneAlarmGenType
                else:
                    response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response   
    
    def getTxCoupled(self, parameters):
        '''**TX:COUPled?** -
        Query if coupled or independent.
        '''
        self.globals.veexPhy.sets.update()
        if (self.globals.veexPhy.sets.settingsControl == veexlib.COUPLED_TX_INTO_RX) or \
           (self.globals.veexPhy.sets.settingsControl == veexlib.COUPLED_RX_INTO_TX):
            response = b"YES"
        elif self.globals.veexPhy.sets.settingsControl == veexlib.INDEPENDENT_TX_RX:
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
                self.globals.veexPhy.sets.settingsControl = veexlib.COUPLED_TX_INTO_RX
            elif paramList[0].head.upper().startswith(b"NO"):
                self.globals.veexPhy.sets.settingsControl = veexlib.INDEPENDENT_TX_RX
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxClock(self, parameters):
        '''**TX:CLOCK?** -
        Query the TX clock reference source.
        '''
        self.globals.veexPhy.sets.update()
        if self.globals.veexPhy.sets.clockType == veexlib.CLOCK_INTERNAL:
            response = b"INT"
        elif self.globals.veexPhy.sets.clockType == veexlib.CLOCK_RECOVERED:
            response = b"LOOP"
        elif self.globals.veexPhy.sets.clockType == veexlib.CLOCK_BITS_SETS:
            response = b"BITS/SETS"
        elif self.globals.veexPhy.sets.clockType == veexlib.CLOCK_BITS:
            response = b"BITS"
        elif self.globals.veexPhy.sets.clockType == veexlib.CLOCK_SETS:
            response = b"SETS"
        elif self.globals.veexPhy.sets.clockType == veexlib.CLOCK_EXT_8KHZ:
            response = b"EXT8KHZ"
        elif self.globals.veexPhy.sets.clockType == veexlib.CLOCK_EXT_BITS:
            response = b"EXT1_5MHZ"
        elif self.globals.veexPhy.sets.clockType == veexlib.CLOCK_EXT_SETS:
            response = b"EXT2MHZ"
        elif self.globals.veexPhy.sets.clockType == veexlib.CLOCK_EXT_10MHZ:
            response = b"EXT10MHZ"
        elif self.globals.veexPhy.sets.clockType == veexlib.CLOCK_SYNC:
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
                self.globals.veexPhy.sets.clockType = veexlib.CLOCK_INTERNAL
            elif paramList[0].head.upper().startswith(b"LOOP"):
                self.globals.veexPhy.sets.clockType = veexlib.CLOCK_RECOVERED
            elif paramList[0].head.upper().startswith(b"BITS/SETS"):
                self.globals.veexPhy.sets.clockType = veexlib.CLOCK_BITS_SETS
            elif paramList[0].head.upper().startswith(b"BITS"):
                self.globals.veexPhy.sets.clockType = veexlib.CLOCK_BITS
            elif paramList[0].head.upper().startswith(b"SETS"):
                self.globals.veexPhy.sets.clockType = veexlib.CLOCK_SETS
            elif paramList[0].head.upper().startswith(b"EXT8KHZ"):
                self.globals.veexPhy.sets.clockType = veexlib.CLOCK_EXT_8KHZ
            elif paramList[0].head.upper().startswith(b"EXT1_5MHZ"):
                self.globals.veexPhy.sets.clockType = veexlib.CLOCK_EXT_BITS
            elif paramList[0].head.upper().startswith(b"EXT2MHZ"):
                self.globals.veexPhy.sets.clockType = veexlib.CLOCK_EXT_SETS
            elif paramList[0].head.upper().startswith(b"EXT10MHZ"):
                self.globals.veexPhy.sets.clockType = veexlib.CLOCK_EXT_10MHZ
            elif paramList[0].head.upper().startswith(b"SYNC"):
                self.globals.veexPhy.sets.clockType = veexlib.CLOCK_SYNC
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxErrBurst(self, parameters):
        '''**TX:ERRor:BURSTPERIOD?** -
        Query the duration between the start of each Error Burst.
        '''
        self.globals.veexPcs.sets.update()
        return b"%d" % self.globals.veexPcs.sets.errorGenBurstPeriod
    
    def setTxErrBurst(self, parameters):
        '''**TX:ERRor:BURSTPERIOD:<value>** -
        Set the duration from the start of each Error Burst to the start of the next.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 505290270):
                self.globals.veexPcs.sets.update()
                errorType = self.globals.veexPcs.sets.errorGenType
                burstSize = self.globals.veexPcs.sets.errorGenBurstSize
                self.globals.veexPcs.sets.setErrorGenBurst(errorType,burstSize,value)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response
    
    def getTxErrBurstSize(self, parameters):
        '''**TX:ERRor:BURSTSIZE?** -
        Query the number of codeword errors to transmit, per burst.
        '''
        self.globals.veexPcs.sets.update()
        return b"%d" % self.globals.veexPcs.sets.errorGenBurstSize

    def setTxErrBurstSize(self, parameters):
        '''**TX:ERRor:BURSTSIZE:<value>** -
        Set the number of errors to transmit, per burst.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 15):
                self.globals.veexPcs.sets.update()
                errorType = self.globals.veexPcs.sets.errorGenType
                burstPeriod = self.globals.veexPcs.sets.errorGenBurstPeriod
                self.globals.veexPcs.sets.setErrorGenBurst(errorType,value,burstPeriod)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxErrRate(self, parameters):
        '''**TX:ERRor:RATE? <position>** -
        Query the transmit error rate, on one or all Logical/PCS lanes.
        '''
        self.globals.veexPcs.sets.update()
        self.globals.veexPcs.allowedSets.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        laneCount = self.globals.veexPcs.allowedSets.txVirtualLaneCount
        if len(paramList) < 1:
            if laneCount != 1:
                response = b"%1.2e" % self.globals.veexPcs.sets.errorGenRate
            else:
                response = b"%1.2e" % self.globals.veexPcs.sets.laneErrorGenRate[0]
        else:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value >= 0:
                if laneCount == 0:
                    response = b"%1.2e" % self.globals.veexPcs.sets.errorGenRate 
                elif value < laneCount:
                    response = b"%1.2e" % self.globals.veexPcs.sets.laneErrorGenRate[value]
                else:
                    response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            elif paramList[0].head.upper().startswith(b"ALL"):
                for i in range(laneCount):
                    if len(response) != 0:
                        response += b", "
                    response += b"%1.2e" % self.globals.veexPcs.sets.laneErrorGenRate[i]
                if len(response) == 0:
                    response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        return response

    def setTxErrRate(self, parameters):
        '''**TX:ERRor:RATE:<position> <rate>** -
        Set the transmit Error generation rate, on one or all Logical/PCS lanes.
        '''
        self.globals.veexPcs.sets.update()
        self.globals.veexPcs.allowedSets.update()
        laneCount = self.globals.veexPcs.allowedSets.txVirtualLaneCount
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) == 1:
            if paramList[0].head.upper().startswith(b"SINGLE"):
                self.globals.veexPcs.sets.insertSingleError()
            elif self.globals.veexPcs.sets.errorGenType == veexlib.PCS_OTL_ERR_NONE:
                response = self._errorResponse(ScpiErrorCode.INVALID_FOR_CUR_SETTING)
            elif laneCount != 1:
                errRate = ParseUtils.checkNumeric(paramList[0].head)
                if errRate == 0:
                    # Only one parameter for multiple lanes means the lane
                    # wasn't specified and the 0 is just the error rate of off.
                    self.globals.veexPcs.sets.errorGenRate = 0.0
                elif ParseUtils.isFloatE(paramList[0].head):
                    self.globals.veexPcs.sets.errorGenRate = float(paramList[0].head)
                else:
                    response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
            else:
                errRate = ParseUtils.checkNumeric(paramList[0].head)
                laneErrorGenRate = self.globals.veexPcs.sets.laneErrorGenRate
                if errRate == 0:
                    # SFP has not lanes, so 0 is just the error rate of off.
                    laneErrorGenRate[0] = 0.0
                    self.globals.veexPcs.sets.laneErrorGenRate = laneErrorGenRate
                elif ParseUtils.isFloatE(paramList[0].head):
                    laneErrorGenRate[0] = float(paramList[0].head)
                    self.globals.veexPcs.sets.laneErrorGenRate = laneErrorGenRate
                else:
                    response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        elif len(paramList) >= 2:
            position = ParseUtils.checkNumeric(paramList[0].head)
            errRate = ParseUtils.checkNumeric(paramList[1].head)
            if paramList[1].head.upper().startswith(b"SINGLE"):
                self.globals.veexPcs.sets.insertSingleError()
            elif laneCount == 0:
                if paramList[0].head.upper().startswith(b"0"):
                    if self.globals.veexPcs.sets.errorGenType == veexlib.PCS_OTL_ERR_NONE:
                        response = self._errorResponse(ScpiErrorCode.INVALID_FOR_CUR_SETTING)
                    elif errRate == 0:
                        # SFP doesn't have lanes, so 0 is just the error rate of off.
                        self.globals.veexPcs.sets.errorGenRate = 0.0
                    elif ParseUtils.isFloatE(paramList[1].head):
                        self.globals.veexPcs.sets.errorGenRate = float(paramList[1].head)
                    else:
                        response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
                else:
                    response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            elif paramList[0].head.upper().startswith(b"ALL"):
                if errRate == 0:
                    laneErrorGenRate = self.globals.veexPcs.sets.laneErrorGenRate
                    for lane in range(laneCount):
                        if self.globals.veexPcs.sets.laneErrorGenType[lane] == veexlib.PCS_OTL_ERR_NONE:
                            response = self._errorResponse(ScpiErrorCode.INVALID_FOR_CUR_SETTING)
                            break
                        # Error rate of 0 means an error rate of off.
                        laneErrorGenRate[lane] = 0.0
                    self.globals.veexPcs.sets.laneErrorGenRate = laneErrorGenRate
                elif ParseUtils.isFloatE(paramList[1].head):
                    errRate = float(paramList[1].head)
                    laneErrorGenRate = self.globals.veexPcs.sets.laneErrorGenRate
                    for lane in range(laneCount):
                        if self.globals.veexPcs.sets.laneErrorGenType[lane] == veexlib.PCS_OTL_ERR_NONE:
                            response = self._errorResponse(ScpiErrorCode.INVALID_FOR_CUR_SETTING)
                            break
                        laneErrorGenRate[lane] = errRate
                    self.globals.veexPcs.sets.laneErrorGenRate = laneErrorGenRate
                else:
                    response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
            elif position >= 0:
                if position < laneCount:
                    laneErrorGenRate = self.globals.veexPcs.sets.laneErrorGenRate
                    if self.globals.veexPcs.sets.laneErrorGenType[position] == veexlib.PCS_OTL_ERR_NONE:
                        response = self._errorResponse(ScpiErrorCode.INVALID_FOR_CUR_SETTING)
                    elif errRate == 0:
                        # Error rate of 0 means an error rate of off.
                        laneErrorGenRate[position] = 0.0
                        self.globals.veexPcs.sets.laneErrorGenRate = laneErrorGenRate
                    elif ParseUtils.isFloatE(paramList[1].head):
                        laneErrorGenRate[position] = float(paramList[1].head)
                        self.globals.veexPcs.sets.laneErrorGenRate = laneErrorGenRate
                    else:
                        response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
                else:
                    response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxErrType(self, parameters):
        '''**TX:ERRor:TYPE? <position>** -
        Query the Logical/PCS lane position for the error type it is inserting.
        '''
        self.globals.veexPcs.sets.update()
        self.globals.veexPcs.allowedSets.update()
        laneCount = self.globals.veexPcs.allowedSets.txVirtualLaneCount
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        if len(paramList) < 1:
            if laneCount != 1:
                if self.globals.veexPcs.sets.errorGenType in ScpiMld.MldVirtErrorsTypeTable.keys():
                    response = ScpiMld.MldVirtErrorsTypeTable[self.globals.veexPcs.sets.errorGenType]
                else:
                    response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
            else:
                if self.globals.veexPcs.sets.laneErrorGenType[0] in ScpiMld.MldVirtErrorsTypeTable.keys():
                    response = ScpiMld.MldVirtErrorsTypeTable[self.globals.veexPcs.sets.laneErrorGenType[0]]
                else:
                    response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)     
        elif laneCount == 0:
            if paramList[0].head.upper().startswith(b"0"):
                if self.globals.veexPcs.sets.errorGenType in ScpiMld.MldVirtErrorsTypeTable.keys():
                    response = ScpiMld.MldVirtErrorsTypeTable[self.globals.veexPcs.sets.errorGenType]
                else:
                    response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value >= 0:
                if value >= laneCount:
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                else:
                    if self.globals.veexPcs.sets.laneErrorGenType[value] in ScpiMld.MldVirtErrorsTypeTable.keys():
                        response = ScpiMld.MldVirtErrorsTypeTable[self.globals.veexPcs.sets.laneErrorGenType[value]]
                    else:
                        response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
            elif paramList[0].head.upper().startswith(b"ALL"):
                for i in range(laneCount):
                    if self.globals.veexPcs.sets.laneErrorGenType[i] in ScpiMld.MldVirtErrorsTypeTable.keys():
                        if len(response) != 0:
                            response += b", "
                        response += ScpiMld.MldVirtErrorsTypeTable[self.globals.veexPcs.sets.laneErrorGenType[i]]
                if len(response) == 0:
                    response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        return response 

    def setTxErrType(self, parameters):
        '''**TX:ERRor:TYPE:<position> <error>** -
        Sets the Error Type to be generated, on one or all Logical/PCS lanes.
        '''
        self.globals.veexPcs.allowedSets.update()
        laneCount = self.globals.veexPcs.allowedSets.txVirtualLaneCount
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) <= 1:
            isErrorType = False
            for key, value in ScpiMld.MldVirtErrorsTypeTable.items():
                if paramList[0].head.upper().startswith(value):
                    isErrorType = True
                    errorType = key
                    break
            if isErrorType:
                if laneCount == 0 or laneCount != 1:
                    self.globals.veexPcs.sets.errorGenType = errorType
                else:
                    laneErrorGenType = self.globals.veexPcs.sets.laneErrorGenType
                    laneErrorGenType[0] = errorType
                    self.globals.veexPcs.sets.laneErrorGenType = laneErrorGenType
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        elif len(paramList) >= 2:
            isErrorType = False
            for key, value in ScpiMld.MldVirtErrorsTypeTable.items():
                if paramList[1].head.upper().startswith(value):
                    isErrorType = True
                    errorType = key
                    break
            if isErrorType:
                value = ParseUtils.checkNumeric(paramList[0].head)
                laneErrorGenType = self.globals.veexPcs.sets.laneErrorGenType
                if laneCount == 0:
                    self.globals.veexPcs.sets.errorGenType = errorType
                elif laneCount == 1:
                    laneErrorGenType[0] = errorType
                    self.globals.veexPcs.sets.laneErrorGenType = laneErrorGenType
                elif value >= 0 and value < laneCount:
                    laneErrorGenType[value] = errorType
                    self.globals.veexPcs.sets.laneErrorGenType = laneErrorGenType
                elif value >= laneCount:
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                elif paramList[0].head.upper().startswith(b"ALL"):
                    for i in range(laneCount):
                        laneErrorGenType[i] = errorType
                    self.globals.veexPcs.sets.laneErrorGenType = laneErrorGenType
                else:
                    response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response  

    def getEyeClockSource(self, parameters):
        '''**TX:EYECLOCK?** -
        Query the Port value for the transmit Eye Clock Source setting.
        '''
        self.globals.veexPhy.sets.update()
        if self.globals.veexPhy.sets.eyeClockSource == veexlib.PHY_EYE_CLOCK_SOURCE_DISABLED:
            response = b"DISABLED"
        elif self.globals.veexPhy.sets.eyeClockSource == veexlib.PHY_EYE_CLOCK_SOURCE_PORT_1:
            response = b"PORT1"
        elif self.globals.veexPhy.sets.eyeClockSource == veexlib.PHY_EYE_CLOCK_SOURCE_PORT_2:
            response = b"PORT2"
        elif self.globals.veexPhy.sets.eyeClockSource == veexlib.PHY_EYE_CLOCK_SOURCE_PORT_3:
            response = b"PORT3"
        elif self.globals.veexPhy.sets.eyeClockSource == veexlib.PHY_EYE_CLOCK_SOURCE_PORT_4:
            response = b"PORT4"
        elif self.globals.veexPhy.sets.eyeClockSource == veexlib.PHY_EYE_CLOCK_SOURCE_PORT_5:
            response = b"PORT5"
        elif self.globals.veexPhy.sets.eyeClockSource == veexlib.PHY_EYE_CLOCK_SOURCE_PORT_6:
            response = b"PORT6"
        elif self.globals.veexPhy.sets.eyeClockSource == veexlib.PHY_EYE_CLOCK_SOURCE_PORT_7:
            response = b"PORT7"
        elif self.globals.veexPhy.sets.eyeClockSource == veexlib.PHY_EYE_CLOCK_SOURCE_PORT_8:
            response = b"PORT8"
        elif self.globals.veexPhy.sets.eyeClockSource == veexlib.PHY_EYE_CLOCK_SOURCE_PORT_9:
            response = b"PORT9"
        elif self.globals.veexPhy.sets.eyeClockSource == veexlib.PHY_EYE_CLOCK_SOURCE_PORT_10:
            response = b"PORT10"
        elif self.globals.veexPhy.sets.eyeClockSource == veexlib.PHY_EYE_CLOCK_SOURCE_PORT_11:
            response = b"PORT11"
        elif self.globals.veexPhy.sets.eyeClockSource == veexlib.PHY_EYE_CLOCK_SOURCE_PORT_12:
            response = b"PORT12"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setEyeClockSource(self, parameters):
        '''**TX:EYECLOCK <port>** -
        Set the Port value for the transmit Eye Clock Source setting.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexPhy.sets.eyeClockSource = veexlib.PHY_EYE_CLOCK_SOURCE_DISABLED
            elif paramList[0].head.upper().startswith(b"PORT1"):
                self.globals.veexPhy.sets.eyeClockSource = veexlib.PHY_EYE_CLOCK_SOURCE_PORT_1
            elif paramList[0].head.upper().startswith(b"PORT2"):
                self.globals.veexPhy.sets.eyeClockSource = veexlib.PHY_EYE_CLOCK_SOURCE_PORT_2
            elif paramList[0].head.upper().startswith(b"PORT3"):
                self.globals.veexPhy.sets.eyeClockSource = veexlib.PHY_EYE_CLOCK_SOURCE_PORT_3
            elif paramList[0].head.upper().startswith(b"PORT4"):
                self.globals.veexPhy.sets.eyeClockSource = veexlib.PHY_EYE_CLOCK_SOURCE_PORT_4
            elif paramList[0].head.upper().startswith(b"PORT5"):
                self.globals.veexPhy.sets.eyeClockSource = veexlib.PHY_EYE_CLOCK_SOURCE_PORT_5
            elif paramList[0].head.upper().startswith(b"PORT6"):
                self.globals.veexPhy.sets.eyeClockSource = veexlib.PHY_EYE_CLOCK_SOURCE_PORT_6
            elif paramList[0].head.upper().startswith(b"PORT7"):
                self.globals.veexPhy.sets.eyeClockSource = veexlib.PHY_EYE_CLOCK_SOURCE_PORT_7
            elif paramList[0].head.upper().startswith(b"PORT8"):
                self.globals.veexPhy.sets.eyeClockSource = veexlib.PHY_EYE_CLOCK_SOURCE_PORT_8
            elif paramList[0].head.upper().startswith(b"PORT9"):
                self.globals.veexPhy.sets.eyeClockSource = veexlib.PHY_EYE_CLOCK_SOURCE_PORT_9
            elif paramList[0].head.upper().startswith(b"PORT10"):
                self.globals.veexPhy.sets.eyeClockSource = veexlib.PHY_EYE_CLOCK_SOURCE_PORT_10
            elif paramList[0].head.upper().startswith(b"PORT11"):
                self.globals.veexPhy.sets.eyeClockSource = veexlib.PHY_EYE_CLOCK_SOURCE_PORT_11
            elif paramList[0].head.upper().startswith(b"PORT12"):
                self.globals.veexPhy.sets.eyeClockSource = veexlib.PHY_EYE_CLOCK_SOURCE_PORT_12
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response 

    def getTxRxInterface(self, parameters):
        '''**TX:INTerface?** -
        Query the selected transmit Interface setting.
        '''
        self.globals.veexPhy.sets.update()
        interface = self.globals.veexPhy.sets.txRxInterface
        interfaceType = self.globals.veexPhy.sets.txRxInterfaceType
        if interfaceType == veexlib.PHY_INTERFACE_TYPE_SINGLE:
            interfaceType = veexlib.PHY_INTERFACE_TYPE_CFP4
        if (interface,interfaceType) in ScpiMld.MldInterfaceTable.keys():
            response = ScpiMld.MldInterfaceTable[(interface,interfaceType)]
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setTxRxInterface(self, parameters):
        '''**TX:INTerface:<interface>** -
        Sets the transmit SONET/SDH, OTN or ETHERNET Interface rate/speed/type.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            isInterface = False
            for (interface, interfaceType), value in ScpiMld.MldInterfaceTable.items():
                if paramList[1].head.upper().startswith(value):
                    self.globals.veexPhy.sets.setTxRxInterface(interface, interfaceType)
                    isInterface = True
                    break
            if isInterface == False:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxLaneMap(self, parameters):
        '''**TX:LANE:MAP?** -
        Query the list of all Logical/PCS lanes.
        '''
        self.globals.veexPcs.sets.update()
        self.globals.veexPcs.allowedSets.update()
        response = b""
        for i in range(self.globals.veexPcs.allowedSets.txVirtLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPcs.sets.txLaneMap[i]
        if len(response) == 0:
            response = b"No Lanes"
        return response

    def setTxLaneMap(self, parameters):
        '''**TX:LANE:MAP:<setting>** -
        Set the list of all transmit Logical/PCS lanes.
        '''
        self.globals.veexPcs.sets.update()
        self.globals.veexPcs.allowedSets.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            laneCount = self.globals.veexPcs.allowedSets.txVirtLaneCount
            if paramList[0].head.upper().startswith(b"DEFAULT"):
                txLaneMap = self.globals.veexPcs.sets.txLaneMap
                if laneCount == 20:
                    for lane in range(laneCount):
                        txLaneMap[lane] = (lane >> 1) + ((lane & 1) * 10)
                    self.globals.veexPcs.sets.txLaneMap = txLaneMap
                else:
                    for lane in range(laneCount):
                        txLaneMap[lane] = lane
                    self.globals.veexPcs.sets.txLaneMap = txLaneMap
            elif paramList[0].head.upper().startswith(b"SWAP"):
                if len(paramList) >= 3:
                    laneA = ParseUtils.checkNumeric(paramList[1].head)
                    laneB = ParseUtils.checkNumeric(paramList[2].head)
                    if laneA < 0 or laneB < 0:
                        response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
                    elif laneA > laneCount or laneB > laneCount:
                        response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                    else:
                        txLaneMap = self.globals.veexPcs.sets.txLaneMap
                        for indexA in range(laneCount):
                            if self.globals.veexPcs.sets.txLaneMap[indexA] == laneA:
                                for indexB in range(laneCount):
                                    if self.globals.veexPcs.sets.txLaneMap[indexB] == laneB:
                                        txLaneMap[indexA] = laneB
                                        txLaneMap[indexB] = laneA
                                        break
                                break
                        self.globals.veexPcs.sets.txLaneMap = txLaneMap
                else:
                    response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            elif len(paramList) == laneCount:
                laneList = []
                for i in range(laneCount):
                    value = ParseUtils.checkNumeric(paramList[i].head)
                    if value < 0:
                        response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
                        break
                    elif value > laneCount:
                        response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                        break
                    elif value in laneList:
                        response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                        break
                    else:
                        laneList.append(value)
                if len(laneList) == laneCount:
                    txLaneMap = self.globals.veexPcs.sets.txLaneMap
                    for i in range(laneCount):
                        txLaneMap[i] = laneList[i]
                    self.globals.veexPcs.sets.txLaneMap = txLaneMap
                else:
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxLaneSkew(self, parameters):
        '''**TX:LANE:SKEW? <lane|ALL>** -
        Query the transmit Skew Bit Delay value, for the specified Lane position.
        '''
        self.globals.veexPcs.sets.update()
        self.globals.veexPcs.allowedSets.update()
        laneCount = self.globals.veexPcs.allowedSets.rxVirtualLaneCount
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if paramList[0].head.upper().startswith(b"ALL"):
                for lane in range(laneCount):
                    if len(response) != 0:
                        response += b", "
                    response += b"%d" % self.globals.veexPcs.sets.txLaneSkew[lane]
                if len(response) == 0:
                    response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
            elif value < 0:
                response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
            elif laneCount == 0 and value != 0:
                response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
            elif laneCount > 0 and value >= laneCount:
                response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
            else:
                response  = b"%d" % self.globals.veexPcs.sets.txLaneSkew[value]
        return response

    def setTxLaneSkew(self, parameters):
        '''**TX:LANE:SKEW:<position> <value> | CLEAR** -
        Set the transmit Skew Bit Delay value, for the specified Lane position.
        '''
        self.globals.veexPcs.allowedSets.update()
        laneCount = self.globals.veexPcs.allowedSets.txVirtLaneCount
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            position = ParseUtils.checkNumeric(paramList[0].head)
            txLaneSkew = self.globals.veexPcs.sets.txLaneSkew
            if paramList[0].head.upper().startswith(b"CLEAR"):
                for lane in range(laneCount):
                    txLaneSkew[lane] = 0
                self.globals.veexPcs.sets.txLaneSkew = txLaneSkew
            elif paramList[0].head.upper().startswith(b"ALL"):
                if len(paramList) >= 2:
                    value = ParseUtils.checkNumeric(paramList[1].head)
                    if value >= 0 and value < 65000:
                        for lane in range(laneCount):
                            txLaneSkew[lane] = value 
                        self.globals.veexPcs.sets.txLaneSkew = txLaneSkew
                    else:
                        response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
                else:
                    response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
            elif position < 0:
                response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
            elif position >= laneCount:
                response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
            elif len(paramList) >= 2:
                value = ParseUtils.checkNumeric(paramList[1].head)
                if value >= 0 and value < 65000:
                    txLaneSkew[position] = value
                    self.globals.veexPcs.sets.txLaneSkew = txLaneSkew
                else:
                    response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            else:
                response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
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

    def getTxLaneCountOptical(self, parameters):
        '''**TX:LANE:COUNT:OPT?** -
        Query the number of TX optical lanes.
        '''
        self.globals.veexPhy.update()
        return b"%d" % self.globals.veexPhy.sets.txNetLaneCount

    def getTxLaneCountHost(self, parameters):
        '''**TX:LANE:COUNT:PHY?** -
        Query the number of TX physical lanes.
        '''
        self.globals.veexPhy.update()
        return b"%d" % self.globals.veexPhy.sets.txHostLaneCount

    def getTxLaneCountLog(self, parameters):
        '''**TX:LANE:COUNT:LOG?** -
        Query the number of TX OTL logical lanes.
        '''
        self.globals.veexOtl.update()
        return b"%d" % self.globals.veexOtl.sets.txVirtLaneCount

    def getTxLaneCountPcs(self, parameters):
        '''**TX:LANE:COUNT:PCS?** -
        Query the number of TX PCS or logical lanes.
        '''
        self.globals.veexPcs.update()
        return b"%d" % self.globals.veexPcs.sets.txVirtLaneCount

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

    def getTxOutThresh(self, parameters):
        '''**TX:OUTTHRESHold?** -
        Query the Transmit Clock Loss Threshold alarm +/- value (in ppm).
        '''
        self.globals.veexPhy.sets.update()
        response = b""
        fInValue = self.globals.veexPhy.sets.txFreqTolerance
        if math.isclose(fInValue, 0.00, rel_tol = 0.000001):
            response = b"OFF"
        else:
            response = b"%.1f ppm" % fInValue
        return response

    def setTxOutThresh(self, parameters):
        '''**TX:OUTTHRESHold:<offset>** -
        Set the +/- value (in ppm) for the Transmit Clock Loss Threshold alarm.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) == 1:
            if ParseUtils.isFloatSdh(paramList[0].head):
                fInValue = float(paramList[0].head)
                if math.isclose(fInValue, 0.00, rel_tol = 0.000001):
                    self.globals.veexPhy.sets.txFreqTolerance = 0.0
                elif fInValue >= 0.0 and fInValue <= 120.0:
                    self.globals.veexPhy.sets.txFreqTolerance = fInValue
                else:
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxPattern(self, parameters):
        '''**TX:PATTern? <position>** -
        Query the transmit payload pattern, for the specified Lane number.
        '''
        self.globals.veexPhy.sets.update()
        self.globals.veexPcs.allowedSets.update()
        laneCount = self.globals.veexPcs.allowedSets.txVirtualLaneCount
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        laneStart = -1
        laneEnd = -1
        if len(paramList) == 0 and laneCount == 1:
            laneStart = 0;
            laneEnd = 1;
        elif len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if paramList[0].head.upper().startswith(b"ALL"):
                laneStart = 0;
                laneEnd = laneCount;
            elif value >= 0 and value < laneCount:
                laneStart = value;
                laneEnd = value + 1;
            else:
                response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        if laneStart != -1:
            for lane in range(laneStart, laneEnd):
                if len(response) != 0:
                    response += b", "
                if self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_USER:
                    response += b"#h%X" % self.globals.veexPhy.sets.txUserPattern[lane]
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_LIVE:
                    response += b"LIVE"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_PRBS_9:
                    response += b"PRBS9"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_PRBS_9_INV:
                    response += b"PRBS9INV"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_PRBS_11:
                    response += b"PRBS11"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_PRBS_11_INV:
                    response += b"PRBS11INV"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_PRBS_13:
                    response += b"PRBS13"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_PRBS_13_INV:
                    response += b"PRBS13INV"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_PRBS_15:
                    response += b"PRBS15"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_PRBS_15_INV:
                    response += b"PRBS15INV"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_PRBS_20:
                    response += b"PRBS20"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_PRBS_20_INV:
                    response += b"PRBS20INV"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_PRBS_23:
                    response += b"PRBS23"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_PRBS_23_INV:
                    response += b"PRBS23INV"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_PRBS_31:
                    response += b"PRBS31"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_PRBS_31_INV:
                    response += b"PRBS31INV"
                elif self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_SQUARE_WAVE:
                    response += b"SQUARE"
            if len(response) == 0:
                response = self._errorResponse(ScpiErrorCode.INVALID_PATTERN)        
        return response

    def setTxPattern(self, parameters):
        '''**TX:PATTern:<position> <pattern>** -
        Set the transmit payload pattern, for the specified Lane position.
        '''
        self.globals.veexPcs.allowedSets.update()
        laneCount = self.globals.veexPcs.allowedSets.txVirtualLaneCount
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) == 1:
            txPatternParam = paramList[0].head
        elif len(paramList) >= 2:
            txPatternParam = paramList[1].head
        else:
            return self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
        txPattern = veexlib.PHY_PATTERN_USER
        userPattern = 0
        if txPatternParam.upper().startswith(b"LIVE"):
            txPattern = veexlib.PHY_PATTERN_LIVE
        elif txPatternParam.upper().startswith(b"USER"):
            txPattern = veexlib.PHY_PATTERN_USER
        elif txPatternParam.upper().startswith(b"PRBS9"):
            txPattern = veexlib.PHY_PATTERN_PRBS_9
        elif txPatternParam.upper().startswith(b"PRBS9INV"):
            txPattern = veexlib.PHY_PATTERN_PRBS_9_INV
        elif txPatternParam.upper().startswith(b"PRBS11"):
            txPattern = veexlib.PHY_PATTERN_PRBS_11
        elif txPatternParam.upper().startswith(b"PRBS11INV"):
            txPattern = veexlib.PHY_PATTERN_PRBS_11_INV
        elif txPatternParam.upper().startswith(b"PRBS13"):
            txPattern = veexlib.PHY_PATTERN_PRBS_13
        elif txPatternParam.upper().startswith(b"PRBS13INV"):
            txPattern = veexlib.PHY_PATTERN_PRBS_13_INV
        elif txPatternParam.upper().startswith(b"PRBS15"):
            txPattern = veexlib.PHY_PATTERN_PRBS_15
        elif txPatternParam.upper().startswith(b"PRBS15INV"):
            txPattern = veexlib.PHY_PATTERN_PRBS_15_INV
        elif txPatternParam.upper().startswith(b"PRBS20"):
            txPattern = veexlib.PHY_PATTERN_PRBS_20
        elif txPatternParam.upper().startswith(b"PRBS20INV"):
            txPattern = veexlib.PHY_PATTERN_PRBS_20_INV
        elif txPatternParam.upper().startswith(b"PRBS23"):
            txPattern = veexlib.PHY_PATTERN_PRBS_23
        elif txPatternParam.upper().startswith(b"PRBS23INV"):
            txPattern = veexlib.PHY_PATTERN_PRBS_23_INV
        elif txPatternParam.upper().startswith(b"PRBS31"):
            txPattern = veexlib.PHY_PATTERN_PRBS_31
        elif txPatternParam.upper().startswith(b"PRBS31INV"):
            txPattern = veexlib.PHY_PATTERN_PRBS_31_INV
        elif txPatternParam.upper().startswith(b"SQUARE"):
            txPattern = veexlib.PHY_PATTERN_SQUARE_WAVE
        if txPattern == veexlib.PHY_PATTERN_USER:
            userPattern = ParseUtils.checkNumeric(txPatternParam)
            if userPattern < 0:
                return self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        if len(paramList) == 1 and laneCount == 1:
            if txPattern == veexlib.PHY_PATTERN_USER:
                txUserPattern = self.globals.veexPhy.sets.txUserPattern
                txUserPattern[0] = userPattern
                self.globals.veexPhy.sets.txUserPattern =txUserPattern
            else:
                pattern = self.globals.veexPhy.sets.txPattern
                pattern[0] = txPattern
                self.globals.veexPhy.sets.txPattern = pattern
        elif len(paramList) >= 2:
            lane = ParseUtils.checkNumeric(paramList[0].head)
            if paramList[0].head.upper().startswith(b"ALL"):
                self.globals.veexPhy.sets.setTxPattern(txPattern, -1)
            elif lane >= 0 and lane < laneCount:
                pattern = self.globals.veexPhy.sets.txPattern
                pattern[lane] = txPattern
                self.globals.veexPhy.sets.txPattern = pattern
            else:
                response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        return response

    def getTxPostEmph(self, parameters):
        '''**TX:POSTEMPH?** -
        Query the selected laser's transmit signal condition Post-Emphasis value in dB for all Physical lanes.
        '''
        self.globals.veexPhy.sets.update()
        self.globals.veexPhy.allowedSets.update()
        response = b""
        if self.globals.veexPhy.allowedSets.txPhysicalLaneCount <= 0:
            response += b"No Lanes"
        else:
            for lane in range(self.globals.veexPhy.allowedSets.txPhysicalLaneCount):
                if len(response) != 0:
                    response += b", "
                if self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_DEFAULT:
                    response += b"DEFAULT"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_0_00:
                    response += b"0.0"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_0_22:
                    response += b"0.22"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_0_45:
                    response += b"0.45"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_0_68:
                    response += b"0.68"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_0_92:
                    response += b"0.92"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_1_16:
                    response += b"1.16"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_1_41:
                    response += b"1.41"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_1_67:
                    response += b"1.67"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_1_94:
                    response += b"1.94"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_2_21:
                    response += b"2.21"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_2_50:
                    response += b"2.5"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_2_79:
                    response += b"2.79"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_3_10:
                    response += b"3.1"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_3_41:
                    response += b"3.41"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_3_74:
                    response += b"3.74"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_4_08:
                    response += b"4.08"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_4_44:
                    response += b"4.44"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_4_81:
                    response += b"4.81"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_5_19:
                    response += b"5.19"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_5_60:
                    response += b"5.6"
                elif self.globals.veexPhy.sets.txLanePostEmph[lane] == veexlib.PHY_TX_POST_EMPH_6_02:
                    response += b"6.02"
                else:
                    response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
                    break;
        return response

    def setTxPostEmph(self, parameters):
        '''**TX:POSTEMPH:<lane> <value>** -
        Set the selected laser's transmit signal condition Post-Emphasis value in dB for the Physical lanes.
        '''
        self.globals.veexPhy.sets.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if self.globals.veexPhy.sets.txInterface == veexlib.PHY_INTERFACE_OFF:
            response = self._errorResponse(ScpiErrorCode.INVALID_SETTINGS)
        elif len(paramList) >= 2:
            if paramList[1].head.upper().startswith(b"DEFAULT"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_DEFAULT
            elif paramList[1].head.upper().startswith(b"0.0"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_0_00
            elif paramList[1].head.upper().startswith(b"0.22"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_0_22
            elif paramList[1].head.upper().startswith(b"0.45"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_0_45
            elif paramList[1].head.upper().startswith(b"0.68"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_0_68
            elif paramList[1].head.upper().startswith(b"0.92"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_0_92
            elif paramList[1].head.upper().startswith(b"1.16"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_1_16
            elif paramList[1].head.upper().startswith(b"1.41"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_1_41
            elif paramList[1].head.upper().startswith(b"1.67"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_1_67
            elif paramList[1].head.upper().startswith(b"1.94"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_1_94
            elif paramList[1].head.upper().startswith(b"2.21"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_2_21
            elif paramList[1].head.upper().startswith(b"2.5"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_2_50
            elif paramList[1].head.upper().startswith(b"2.79"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_2_79
            elif paramList[1].head.upper().startswith(b"3.1"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_3_10
            elif paramList[1].head.upper().startswith(b"3.41"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_3_41
            elif paramList[1].head.upper().startswith(b"3.74"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_3_74
            elif paramList[1].head.upper().startswith(b"4.08"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_4_08
            elif paramList[1].head.upper().startswith(b"4.44"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_4_44
            elif paramList[1].head.upper().startswith(b"4.81"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_4_81
            elif paramList[1].head.upper().startswith(b"5.19"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_5_19
            elif paramList[1].head.upper().startswith(b"5.6"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_5_60
            elif paramList[1].head.upper().startswith(b"6.02"):
                idlPostEmph = veexlib.PHY_TX_POST_EMPH_6_02
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            if response == None:
                value = ParseUtils.checkNumeric(paramList[0].head)
                if paramList[0].head.upper().startswith(b"ALL"):
                    self.globals.veexPhy.allowedSets.update()
                    txLanePostEmph = self.globals.veexPhy.sets.txLanePostEmph
                    for lane in range(self.globals.veexPhy.allowedSets.txPhysicalLaneCount):
                        txLanePostEmph[lane] = idlPostEmph
                    self.globals.veexPhy.sets.txLanePostEmph = txLanePostEmph
                elif value < 0:
                    response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
                elif value != 0 and self.globals.veexPhy.allowedSets.txPhysicalLaneCount == 0:
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                elif value < self.globals.veexPhy.allowedSets.txPhysicalLaneCount:
                    txLanePostEmph = self.globals.veexPhy.sets.txLanePostEmph
                    txLanePostEmph[value] = idlPostEmph
                    self.globals.veexPhy.sets.txLanePostEmph = txLanePostEmph
                else:
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)    
        return response

    def getTxPreEmph(self, parameters):
        '''**TX:PREEMPH?** -
        Query the selected laser's transmit signal condition Pre-Emphasis value in dB for all Physical lanes.
        '''
        self.globals.veexPhy.sets.update()
        self.globals.veexPhy.allowedSets.update()
        response = b""
        if self.globals.veexPhy.allowedSets.txPhysicalLaneCount <= 0:
            response += b"No Lanes"
        else:
            for lane in range(self.globals.veexPhy.allowedSets.txPhysicalLaneCount):
                if len(response) != 0:
                    response += b", "
                if self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_DEFAULT:
                    response += b"DEFAULT"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_0_00:
                    response += b"0.0"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_0_22:
                    response += b"0.22"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_0_45:
                    response += b"0.45"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_0_68:
                    response += b"0.68"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_0_92:
                    response += b"0.92"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_1_16:
                    response += b"1.16"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_1_41:
                    response += b"1.41"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_1_67:
                    response += b"1.67"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_1_94:
                    response += b"1.94"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_2_21:
                    response += b"2.21"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_2_50:
                    response += b"2.5"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_2_79:
                    response += b"2.79"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_3_10:
                    response += b"3.1"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_3_41:
                    response += b"3.41"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_3_74:
                    response += b"3.74"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_4_08:
                    response += b"4.08"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_4_44:
                    response += b"4.44"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_4_81:
                    response += b"4.81"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_5_19:
                    response += b"5.19"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_5_60:
                    response += b"5.6"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_6_02:
                    response += b"6.02"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_6_47:
                    response += b"6.47"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_6_94:
                    response += b"6.94"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_7_43:
                    response += b"7.43"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_7_96:
                    response += b"7.96"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_8_52:
                    response += b"8.52"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_9_12:
                    response += b"9.12"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_9_76:
                    response += b"9.76"
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_10_46:
                    response += b"10.46"                
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_11_21:
                    response += b"11.21"                
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_12_04:
                    response += b"12.04"                
                elif self.globals.veexPhy.sets.txLanePreEmph[lane] == veexlib.PHY_TX_PRE_EMPH_12_96:
                    response += b"12.96"                
                else:
                    response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
                    break;
        return response

    def setTxPreEmph(self, parameters):
        '''**TX:PREEMPH:<lane> <value>** -
        Set the selected laser's transmit signal condition Pre-Emphasis value in dB for all Physical lanes.
        '''
        self.globals.veexPhy.sets.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if self.globals.veexPhy.sets.txInterface == veexlib.PHY_INTERFACE_OFF:
            response = self._errorResponse(ScpiErrorCode.INVALID_SETTINGS)
        elif len(paramList) >= 2:
            if paramList[1].head.upper().startswith(b"DEFAULT"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_DEFAULT
            elif paramList[1].head.upper().startswith(b"0.0"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_0_00
            elif paramList[1].head.upper().startswith(b"0.22"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_0_22
            elif paramList[1].head.upper().startswith(b"0.45"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_0_45
            elif paramList[1].head.upper().startswith(b"0.68"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_0_68
            elif paramList[1].head.upper().startswith(b"0.92"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_0_92
            elif paramList[1].head.upper().startswith(b"1.16"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_1_16
            elif paramList[1].head.upper().startswith(b"1.41"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_1_41
            elif paramList[1].head.upper().startswith(b"1.67"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_1_67
            elif paramList[1].head.upper().startswith(b"1.94"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_1_94
            elif paramList[1].head.upper().startswith(b"2.21"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_2_21
            elif paramList[1].head.upper().startswith(b"2.5"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_2_50
            elif paramList[1].head.upper().startswith(b"2.79"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_2_79
            elif paramList[1].head.upper().startswith(b"3.1"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_3_10
            elif paramList[1].head.upper().startswith(b"3.41"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_3_41
            elif paramList[1].head.upper().startswith(b"3.74"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_3_74
            elif paramList[1].head.upper().startswith(b"4.08"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_4_08
            elif paramList[1].head.upper().startswith(b"4.44"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_4_44
            elif paramList[1].head.upper().startswith(b"4.81"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_4_81
            elif paramList[1].head.upper().startswith(b"5.19"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_5_19
            elif paramList[1].head.upper().startswith(b"5.6"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_5_60
            elif paramList[1].head.upper().startswith(b"6.02"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_6_02
            elif paramList[1].head.upper().startswith(b"6.47"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_6_47
            elif paramList[1].head.upper().startswith(b"6.94"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_6_94
            elif paramList[1].head.upper().startswith(b"7.43"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_7_43
            elif paramList[1].head.upper().startswith(b"7.96"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_7_96
            elif paramList[1].head.upper().startswith(b"8.52"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_8_52
            elif paramList[1].head.upper().startswith(b"9.12"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_9_12
            elif paramList[1].head.upper().startswith(b"9.76"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_9_76
            elif paramList[1].head.upper().startswith(b"10.46"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_10_46
            elif paramList[1].head.upper().startswith(b"11.21"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_11_21
            elif paramList[1].head.upper().startswith(b"12.04"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_12_04
            elif paramList[1].head.upper().startswith(b"12.96"):
                idlPreEmph = veexlib.PHY_TX_PRE_EMPH_12_96
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            if response == None:
                value = ParseUtils.checkNumeric(paramList[0].head)
                if paramList[0].head.upper().startswith(b"ALL"):
                    self.globals.veexPhy.allowedSets.update()
                    txLanePreEmph = self.globals.veexPhy.sets.txLanePreEmph
                    for lane in range(self.globals.veexPhy.allowedSets.txPhysicalLaneCount):
                        txLanePreEmph[lane] = idlPreEmph
                    self.globals.veexPhy.sets.txLanePreEmph = txLanePreEmph
                elif value < 0:
                    response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
                elif value != 0 and self.globals.veexPhy.allowedSets.txPhysicalLaneCount == 0:
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                elif value < self.globals.veexPhy.allowedSets.txPhysicalLaneCount:
                    txLanePreEmph = self.globals.veexPhy.sets.txLanePreEmph
                    txLanePreEmph[value] = idlPreEmph
                    self.globals.veexPhy.sets.txLanePreEmph = txLanePreEmph
                else:
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)    
        return response

    def getTxSwing(self, parameters):
        '''**TX:SWING?** -
        Query the selected laser's transmit signal condition Swing value in mV for all Physical lanes.
        '''
        self.globals.veexPhy.sets.update()
        response = b""
        self.globals.veexPhy.allowedSets.update()
        response = b""
        if self.globals.veexPhy.allowedSets.txPhysicalLaneCount <= 0:
            response += b"No Lanes"
        else:
            for lane in range(self.globals.veexPhy.allowedSets.txPhysicalLaneCount):
                if len(response) != 0:
                    response += b", "
                if self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_DEFAULT:
                    response += b"DEFAULT"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_285:
                    response += b"285"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_315:
                    response += b"315"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_344:
                    response += b"344"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_374:
                    response += b"374"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_404:
                    response += b"404"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_433:
                    response += b"433"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_463:
                    response += b"463"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_493:
                    response += b"493"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_523:
                    response += b"523"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_552:
                    response += b"552"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_582:
                    response += b"582"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_612:
                    response += b"612"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_641:
                    response += b"641"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_671:
                    response += b"671"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_701:
                    response += b"701"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_730:
                    response += b"730"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_760:
                    response += b"760"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_790:
                    response += b"790"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_819:
                    response += b"819"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_849:
                    response += b"849"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_879:
                    response += b"879"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_908:
                    response += b"908"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_938:
                    response += b"938"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_968:
                    response += b"968"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_998:
                    response += b"998"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_1027:
                    response += b"1027"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_1057:
                    response += b"1057"
                elif self.globals.veexPhy.sets.txLaneSwing[lane] == veexlib.PHY_TX_SWING_1087:
                    response += b"1087"
                else:
                    response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
                    break;
        return response

    def setTxSwing(self, parameters):
        '''**TX:SWING:<lane> <value>** -
        Set the selected laser's transmit signal condition Swing value in mV for the Physical lanes.
        '''
        self.globals.veexPhy.sets.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if self.globals.veexPhy.sets.txInterface == veexlib.PHY_INTERFACE_OFF:
            response = self._errorResponse(ScpiErrorCode.INVALID_SETTINGS)
        elif len(paramList) >= 2:
            if paramList[1].head.upper().startswith(b"DEFAULT"):
                idlSwing = veexlib.PHY_TX_SWING_DEFAULT
            elif paramList[1].head.upper().startswith(b"285"):
                idlSwing = veexlib.PHY_TX_SWING_285
            elif paramList[1].head.upper().startswith(b"315"):
                idlSwing = veexlib.PHY_TX_SWING_315
            elif paramList[1].head.upper().startswith(b"344"):
                idlSwing = veexlib.PHY_TX_SWING_344
            elif paramList[1].head.upper().startswith(b"374"):
                idlSwing = veexlib.PHY_TX_SWING_374
            elif paramList[1].head.upper().startswith(b"404"):
                idlSwing = veexlib.PHY_TX_SWING_404
            elif paramList[1].head.upper().startswith(b"433"):
                idlSwing = veexlib.PHY_TX_SWING_443
            elif paramList[1].head.upper().startswith(b"463"):
                idlSwing = veexlib.PHY_TX_SWING_463
            elif paramList[1].head.upper().startswith(b"493"):
                idlSwing = veexlib.PHY_TX_SWING_493
            elif paramList[1].head.upper().startswith(b"523"):
                idlSwing = veexlib.PHY_TX_SWING_523
            elif paramList[1].head.upper().startswith(b"552"):
                idlSwing = veexlib.PHY_TX_SWING_552
            elif paramList[1].head.upper().startswith(b"582"):
                idlSwing = veexlib.PHY_TX_SWING_582
            elif paramList[1].head.upper().startswith(b"612"):
                idlSwing = veexlib.PHY_TX_SWING_612
            elif paramList[1].head.upper().startswith(b"641"):
                idlSwing = veexlib.PHY_TX_SWING_641
            elif paramList[1].head.upper().startswith(b"671"):
                idlSwing = veexlib.PHY_TX_SWING_671
            elif paramList[1].head.upper().startswith(b"701"):
                idlSwing = veexlib.PHY_TX_SWING_701
            elif paramList[1].head.upper().startswith(b"730"):
                idlSwing = veexlib.PHY_TX_SWING_730
            elif paramList[1].head.upper().startswith(b"760"):
                idlSwing = veexlib.PHY_TX_SWING_760
            elif paramList[1].head.upper().startswith(b"790"):
                idlSwing = veexlib.PHY_TX_SWING_790
            elif paramList[1].head.upper().startswith(b"819"):
                idlSwing = veexlib.PHY_TX_SWING_819
            elif paramList[1].head.upper().startswith(b"849"):
                idlSwing = veexlib.PHY_TX_SWING_849
            elif paramList[1].head.upper().startswith(b"879"):
                idlSwing = veexlib.PHY_TX_SWING_879
            elif paramList[1].head.upper().startswith(b"908"):
                idlSwing = veexlib.PHY_TX_SWING_908
            elif paramList[1].head.upper().startswith(b"938"):
                idlSwing = veexlib.PHY_TX_SWING_938
            elif paramList[1].head.upper().startswith(b"968"):
                idlSwing = veexlib.PHY_TX_SWING_968
            elif paramList[1].head.upper().startswith(b"998"):
                idlSwing = veexlib.PHY_TX_SWING_998
            elif paramList[1].head.upper().startswith(b"1027"):
                idlSwing = veexlib.PHY_TX_SWING_1027
            elif paramList[1].head.upper().startswith(b"1057"):
                idlSwing = veexlib.PHY_TX_SWING_1057
            elif paramList[1].head.upper().startswith(b"1087"):
                idlSwing = veexlib.PHY_TX_SWING_1087
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            if response == None:
                value = ParseUtils.checkNumeric(paramList[0].head)
                if paramList[0].head.upper().startswith(b"ALL"):
                    self.globals.veexPhy.allowedSets.update()
                    txLaneSwing = self.globals.veexPhy.sets.txLaneSwing
                    for lane in range(self.globals.veexPhy.allowedSets.txPhysicalLaneCount):
                        txLaneSwing[lane] = idlSwing
                    self.globals.veexPhy.sets.txLaneSwing = txLaneSwing
                elif value < 0:
                    response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
                elif value != 0 and self.globals.veexPhy.allowedSets.txPhysicalLaneCount == 0:
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                elif value < self.globals.veexPhy.allowedSets.txPhysicalLaneCount:
                    txLaneSwing = self.globals.veexPhy.sets.txLaneSwing
                    txLaneSwing[value] = idlSwing
                    self.globals.veexPhy.sets.txLaneSwing = txLaneSwing
                else:
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)    
        return response

    def getRxFreq(self, parameters):
        '''**RX:FREQuency?** -
        Query the measured RX line frequency. Would use PHY stats, but that is
        per lane.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        for lane in range(self.globals.veexPhy.stats.rxHostLaneCount):
            if lane != 0:
                response += b", "
            response += b"%d Hz" % self.globals.veexPhy.stats.freqRx[lane]
        return response

    def getRxFreqOffsetPpm(self, parameters):
        '''**RX:FREQOFFset:PPM?** -
        Query the offset from nominal measured RX line frequency in PPM.
        Would use PHY stats, but that is per lane.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        for lane in range(self.globals.veexPhy.stats.rxHostLaneCount):
            if lane != 0:
                response += b", "
            response += b"%0.1f ppm" % self.globals.veexPhy.stats.freqOffsetRxPpm[lane]
        return response

    def getRxFreqOffsetHz(self, parameters):
        '''**RX:FREQOFFset:HZ?** -
        Query the offset from nominal measured RX line frequency in Hz.
        Would use PHY stats, but that is per lane.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        for lane in range(self.globals.veexPhy.stats.rxHostLaneCount):
            if lane != 0:
                response += b", "
            response += b"%d Hz" % self.globals.veexPhy.stats.freqOffsetRxHz[lane]
        return response

    def getDisableHiSer(self, parameters):
        '''**RX:HISERALARM?** -
        Query the receive HISERALARM mode setting.
        '''
        self.globals.veexPcs.sets.update()
        response = b""
        if self.globals.veexPcs.sets.hiSerDisable:
            response = b"DISABLE"
        else:
            response = b"ENABLE"
        return response

    def setDisableHiSer(self, parameters):
        '''**RX:HISERALARM:<mode>** -
        Enables or Disables the HiSER (High Symbol Error Ratio) Alarm reporting.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ENABLE"):
                self.globals.veexPcs.sets.hiSerDisable = False
            elif paramList[0].head.upper().startswith(b"DISABLE"):
                self.globals.veexPcs.sets.hiSerDisable = True
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getHiSerPeriod(self, parameters):
        '''**RX:HISERPERIOD?** -
        Query the HISERPERIOD value.
        '''
        self.globals.veexPcs.sets.update()
        return b"%d" % self.globals.veexPcs.sets.hiSerPeriod

    def setHiSerPeriod(self, parameters):
        '''**RX:HISERPERIOD:<value>** -
        Sets a consecutive number of milliseconds that must elapse without receiving 
        FEC Correctable Symbol Errors at a rate above 1.00e-04 before HiSer alarms will stop accumulating.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value >= 60 and value <= 75:
                self.globals.veexPcs.sets.hiSerPeriod = value
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxLaneCountOptical(self, parameters):
        '''**RX:LANE:COUNT:OPT?** -
        Query the number of RX optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        return b"%d" % self.globals.veexPhy.stats.rxNetLaneCount

    def getRxLaneCountHost(self, parameters):
        '''**RX:LANE:COUNT:PHY?** -
        Query the number of RX physical lanes.
        '''
        self.globals.veexPhy.stats.update()
        return b"%d" % self.globals.veexPhy.stats.rxHostLaneCount

    def getRxLaneCountOtl(self, parameters):
        '''**RX:LANE:COUNT:LOG?** -
        Query the number of RX OTL logical lanes.
        '''
        self.globals.veexOtl.stats.update()
        return b"%d" % self.globals.veexOtl.stats.rxVirtLaneCount

    def getRxLaneCountPcs(self, parameters):
        '''**RX:LANE:COUNT:PCS?** -
        Query the number of RX PCS lanes.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.rxVirtLaneCount

    def getRxLaneMap(self, parameters):
        '''**RX:LANE:MAP?** -
        Query the list of all receive Logical/PCS lanes (comma-separated).
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        else:
            for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
                if len(response) != 0:
                    response += b", "
                if self.globals.veexPcs.stats.rxLaneMap[lane] > 20:
                    response += b"99"
                else:
                    response += b"%d" % self.globals.veexPcs.stats.rxLaneMap[lane]
        return response

    def getRxLaneSkewBits(self, parameters):
        '''**RX:LANE:SKEW:BITS?** -
        Query the list of SKEW delay values (in bit delay time from 0-65000) for all Logical/PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        else:
            for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
                if len(response) != 0:
                    response += b", "
                if self.globals.veexPcs.stats.rxLaneSkew[lane] > 20:
                    response += b"0"
                else:
                    response += b"%d" % self.globals.veexPcs.stats.rxLaneSkew[lane]        
        return response

    def getRxLaneSkewPs(self, parameters):
        '''**RX:LANE:SKEW:PS?** -
        Query the list of SKEW delay values (in picoseconds) for all Logical/PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        else:
            psConvertFactor = 0.0
            self.globals.veexPhy.sets.update()
            if (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_40G_OC_768_STM_256_UNFRAMED) or \
               (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_40G_OC_768_STM_256) or \
               (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_40G_FRAMED_OC_STM_BERT):
                virtualLaneDataRate = 9953280000.0
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_41G_ETHERNET_UNFRAMED) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_41G_FRAMED_PCS_BERT) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_41G_ETHERNET):
                virtualLaneDataRate = 10312500000.0
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_43G_OTU_3_UNFRAMED) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_43G_OTU_3) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_43G_FRAMED_OTU_BERT):
                virtualLaneDataRate = (9953280000.0 * 255) / 236
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_44G_OTU_3E1_UNFRAMED) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_44G_OTU_3E1):
                virtualLaneDataRate = (10312500000.0 * 255) / 236
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_44G_OTU_3E2_UNFRAMED) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_44G_OTU_3E2):
                virtualLaneDataRate = (9953280000.0 * 243) / 217
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_103G_ETHERNET_UNFRAMED):
                virtualLaneDataRate = 10312500000.0
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_103G_FRAMED_PCS_BERT) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_103G_ETHERNET) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PB_PHY_INTERFACE_103G_RS_FEC_ETHERNET) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_103G_ETHERNET_FLEXE):
                virtualLaneDataRate = 10312500000.0 /2
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_212G_ETHERNET_UNFRAMED):
                virtualLaneDataRate = 26562500000.0
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_212G_FRAMED_PCS_BERT) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_212G_RS_FEC_ETHERNET):
                virtualLaneDataRate = 10312500000.0 / 2
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_412G_ETHERNET_UNFRAMED):
                virtualLaneDataRate = 25781250000.0 
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_425G_ETHERNET_UNFRAMED):
                virtualLaneDataRate = 26562500000.0
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_425G_FRAMED_PCS_BERT) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_425G_RS_FEC_ETHERNET):
                virtualLaneDataRate = 10312500000.0 / 2
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_112G_OTU_4_UNFRAMED):
                virtualLaneDataRate = (9953280000.0 * 255) / 227 
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_112G_OTU_4) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_112G_FRAMED_OTU_BERT):
                virtualLaneDataRate = (9953280000.0 * 255) / (227 * 2) 
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_112G_OTU_CN_UNFRAMED):
                virtualLaneDataRate = (9953280000.0 * 255) / 226
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_112G_OTU_CN):
                virtualLaneDataRate = (9953280000.0 * 255) / (226 * 2)
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_112G_FIBRE_UNFRAMED):
                virtualLaneDataRate = 11220000000.0
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_112G_FIBRE_CHANNEL):
                virtualLaneDataRate = 11220000000.0 / 2
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_10G_OTU_2_UNFRAMED) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_10G_OTU_2):
                virtualLaneDataRate = (9953280000.0 * 255) / 237 
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_11G_OTU_1E_UNFRAMED) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_11G_OTU_1E):
                virtualLaneDataRate = (10312500000.0 * 255) / 238 
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_11G_OTU_2E_UNFRAMED) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_11G_OTU_2E):
                virtualLaneDataRate = (10312500000.0 * 255) / 237
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_10G_ETHERNET_UNFRAMED) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_10G_ETHERNET):
                virtualLaneDataRate = 10312500000
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_25G_RS_FEC_ETHERNET) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_25G_ETHERNET_UNFRAMED) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_25G_ETHERNET):
                virtualLaneDataRate = 25781250000
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_8G_FIBRE_UNFRAMED) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_8G_FIBRE_CHANNEL):
                virtualLaneDataRate = 8500000000
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_10G_FIBRE_UNFRAMED) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_10G_FIBRE_CHANNEL):
                virtualLaneDataRate = 10518750000
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_16G_FIBRE_UNFRAMED) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_16G_FIBRE_CHANNEL) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_16G_RS_FEC_FIBRE):
                virtualLaneDataRate = 14025000000
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_32G_FIBRE_UNFRAMED) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_32G_FIBRE_CHANNEL):
                virtualLaneDataRate = 28050000000
            elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_24G_CPRI_10) or \
                 (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_24G_CPRI_10_UNFRAMED):
                virtualLaneDataRate = 24330240000 
            if virtualLaneDataRate != 0:                                                
                psConvertFactor = 1.0e12 / virtualLaneDataRate
            for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
                if len(response) != 0:
                    response += b", "
                if self.globals.veexPcs.stats.rxLaneSkew[lane] > 20:
                    response += b"0"
                else:
                    response += b"%d" % (self.globals.veexPcs.stats.rxLaneSkew[lane] * psConvertFactor,)
        return response

    def getRxFreqOffsetHzMax(self, parameters):
        '''**RX:MAXFREQOFFset:Hz?** -
        Query the maximum received Line Frequency Offset value in Hz for all Physical lanes.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        if self.globals.veexPhy.stats.rxHostLaneCount <= 0:
            response = b"No Lanes";
        else:
            for lane in range(self.globals.veexPhy.stats.rxHostLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%d Hz" % self.globals.veexPhy.stats.freqOffsetRxHzMax[lane]
        return response

    def getRxFreqOffsetPpmMax(self, parameters):
        '''**RX:MAXFREQOFFset:PPM?** -
        Query the maximum received Line Frequency Offset value in PPM for all Physical lanes.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        if self.globals.veexPhy.stats.rxHostLaneCount <= 0:
            response = b"No Lanes";
        else:
            for lane in range(self.globals.veexPhy.stats.rxHostLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%0.1f ppm" % self.globals.veexPhy.stats.freqOffsetRxPpmMax[lane]
        return response

    def getRxFreqMax(self, parameters):
        '''**RX:MAXFREQuency?** -
        Query the maximum received Line Frequency value in Hz for all Physical lanes.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        if self.globals.veexPhy.stats.rxHostLaneCount <= 0:
            response = b"No Lanes";
        else:
            for lane in range(self.globals.veexPhy.stats.rxHostLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%d Hz" % self.globals.veexPhy.stats.freqRxMax[lane]
        return response

    def getRxOppBBMax(self, parameters):
        '''**RX:MAXOPPBB?** -
        Query the value of the maximum received broad band (or aggregate) optical power level in dBm for all Optical lanes combined.
        '''
        self.globals.veexPhy.update()
        if self.globals.veexPhy.stats.rxNetLaneCount <= 0:
            response = b"No Lanes";
        else:
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
                response = b"%1.2f dBm" % self.globals.veexPhy.stats.signalStrengthMax
        return response

    def getRxFreqOffsetHzMin(self, parameters):
        '''**RX:MINFREQOFFset:Hz?** -
        Query the minimum received Line Frequency Offset value in Hz for all Physical lanes.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        if self.globals.veexPhy.stats.rxHostLaneCount <= 0:
            response = b"No Lanes";
        else:
            for lane in range(self.globals.veexPhy.stats.rxHostLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%d Hz" % self.globals.veexPhy.stats.freqOffsetRxHzMin[lane]
        return response

    def getRxFreqOffsetPpmMin(self, parameters):
        '''**RX:MINFREQOFFset:PPM?** -
        Query the minimum received Line Frequency Offset value in PPM for all Physical lanes.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        if self.globals.veexPhy.stats.rxHostLaneCount <= 0:
            response = b"No Lanes";
        else:
            for lane in range(self.globals.veexPhy.stats.rxHostLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%0.1f ppm" % self.globals.veexPhy.stats.freqOffsetRxPpmMin[lane]
        return response

    def getRxFreqMin(self, parameters):
        '''**RX:MINFREQuency?** -
        Query the minimum received Line Frequency value in Hz for all Physical lanes.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        if self.globals.veexPhy.stats.rxHostLaneCount <= 0:
            response = b"No Lanes";
        else:
            for lane in range(self.globals.veexPhy.stats.rxHostLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%d Hz" % self.globals.veexPhy.stats.freqRxMin[lane]
        return response

    def getRxOppBBMin(self, parameters):
        '''**RX:MINOPPBB?** -
        Query the value of the minimum received broad band (or aggregate) optical power level in dBm for all Optical lanes combined.
        '''
        self.globals.veexPhy.update()
        if self.globals.veexPhy.stats.rxNetLaneCount <= 0:
            response = b"No Lanes";
        else:
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
                response = b"%1.2f dBm" % self.globals.veexPhy.stats.signalStrengthMin
        return response

    def getRxOppBB(self, parameters):
        '''**RX:OPPBB?** -
        Query the measured RX optical power.
        '''
        self.globals.veexPhy.update()
        if self.globals.veexPhy.stats.rxNetLaneCount <= 0:
            response = b"No Lanes";
        else:
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
                response = b"%1.2f dBm" % self.globals.veexPhy.stats.signalStrength
        return response

    def getModuleDataRxPower(self, parameters):
        '''**RX:OPPLANE?** -
        Query the measured RX optical power.
        '''
        self.globals.veexPhy.update()
        if self.globals.veexPhy.stats.rxNetLaneCount <= 0:
            response = b"No Lanes";
        else:
            response = b""
            for lane in range(self.globals.veexPhy.stats.rxHostLaneCount):
                if lane != 0:
                    response += b", "
                if self.globals.veexPhy.stats.rxLanePower[lane] < -99.999:
                    response += b"Interface not Physical"
                elif (self.globals.veexPhy.stats.rxLanePower[lane] < -99.7999) and \
                   (self.globals.veexPhy.stats.rxLanePower[lane] > -99.8001):
                    response += b"No Module"
                elif (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_10000T_ETHERNET) or \
                     (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_5000T_ETHERNET)  or \
                     (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_2500T_ETHERNET)  or \
                     (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_1000T_ETHERNET)  or \
                     (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_100T_ETHERNET)   or \
                     (self.globals.veexPhy.sets.txRxInterface == veexlib.PHY_INTERFACE_10T_ETHERNET):
                    response += b"Electical LAN"
                elif (self.globals.veexPhy.stats.rxLanePower[lane] < -99.6999) and \
                     (self.globals.veexPhy.stats.rxLanePower[lane] > -99.7001):
                    response += b"No Measurement"
                elif self.globals.veexPhy.stats.rxLanePower[lane] < -50:
                    response += b"Loss of Power";
                else:
                    response += b"%1.2f dBm" % self.globals.veexPhy.stats.rxLanePower[lane]
        return response

    def getRxOutThreshhold(self,parameters):
        '''**RX:OUTTHRESHold?** -
        Queries the Out of Frequency Threshold Alarm value.
        '''
        self.globals.veexPhy.stets.update()
        if math.isclose(self.globals.veexPhy.stets.rxFreqTolerance, 0.00, rel_tol = 0.000001):
            response = b"OFF";
        else:
            response += b"%.1f ppm" % self.globals.veexPhy.stets.rxFreqTolerance
        return response   

    def setRxOutThreshhold(self, parameters):
        '''**RX:OUTTHRESHold:<value>** -
        Enables and sets the PPM value for the Out of Frequency Threshold Alarm.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if ParseUtils.isFloatSdh(paramList[0].head):
                freqThresh = float(paramList[0].head)
                if math.isclose(freqThresh, 0.00, rel_tol = 0.000001):
                    self.globals.veexPhy.stets.rxFreqTolerance = 0.0
                elif freqThresh >= 0.0 and freqThresh <= 120.0:
                    self.globals.veexPhy.stets.rxFreqTolerance = freqThresh
                else:
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxPattern(self, parameters):
        '''**RX:PATTern? <position>** -
        Query the receive payload pattern for the specified Lane number.
        '''
        self.globals.veexPhy.sets.update()
        self.globals.veexPcs.allowedSets.update()
        laneCount = self.globals.veexPcs.allowedSets.rxVirtualLaneCount
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        laneStart = -1
        laneEnd = -1
        if len(paramList) == 0 and laneCount == 1:
            laneStart = 0;
            laneEnd = 1;
        elif len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if paramList[0].head.upper().startswith(b"ALL"):
                laneStart = 0;
                laneEnd = laneCount;
            elif value >= 0 and value < laneCount:
                laneStart = value;
                laneEnd = value + 1;
            else:
                response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        if laneStart != -1:
            for lane in range(laneStart, laneEnd):
                if len(response) != 0:
                    response += b", "
                if self.globals.veexPhy.sets.txPattern[lane] == veexlib.PHY_PATTERN_USER:
                    response += b"#h%X" % self.globals.veexPhy.sets.rxUserPattern[lane]
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_LIVE:
                    response += b"LIVE"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_PRBS_9:
                    response += b"PRBS9"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_PRBS_9_INV:
                    response += b"PRBS9INV"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_PRBS_11:
                    response += b"PRBS11"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_PRBS_11_INV:
                    response += b"PRBS11INV"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_PRBS_13:
                    response += b"PRBS13"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_PRBS_13_INV:
                    response += b"PRBS13INV"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_PRBS_15:
                    response += b"PRBS15"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_PRBS_15_INV:
                    response += b"PRBS15INV"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_PRBS_20:
                    response += b"PRBS20"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_PRBS_20_INV:
                    response += b"PRBS20INV"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_PRBS_23:
                    response += b"PRBS23"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_PRBS_23_INV:
                    response += b"PRBS23INV"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_PRBS_31:
                    response += b"PRBS31"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_PRBS_31_INV:
                    response += b"PRBS31INV"
                elif self.globals.veexPhy.sets.rxPattern[lane] == veexlib.PHY_PATTERN_SQUARE_WAVE:
                    response += b"SQUARE"
            if len(response) == 0:
                response = self._errorResponse(ScpiErrorCode.INVALID_PATTERN)        
        return response

    def setRxPattern(self, parameters):
        '''**RX:PATTern:<position> <pattern>** -
        Set the receive payload pattern for the specified Lane position.
        '''
        self.globals.veexPcs.allowedSets.update()
        laneCount = self.globals.veexPcs.allowedSets.rxVirtualLaneCount
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) == 1:
            rxPatternParam = paramList[0].head
        elif len(paramList) >= 2:
            rxPatternParam = paramList[1].head
        else:
            return self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
        rxPattern = veexlib.PHY_PATTERN_USER
        userPattern = 0
        if rxPatternParam.upper().startswith(b"LIVE"):
            rxPattern = veexlib.PHY_PATTERN_LIVE
        elif rxPatternParam.upper().startswith(b"USER"):
            rxPattern = veexlib.PHY_PATTERN_USER
        elif rxPatternParam.upper().startswith(b"PRBS9"):
            rxPattern = veexlib.PHY_PATTERN_PRBS_9
        elif rxPatternParam.upper().startswith(b"PRBS9INV"):
            rxPattern = veexlib.PHY_PATTERN_PRBS_9_INV
        elif rxPatternParam.upper().startswith(b"PRBS11"):
            rxPattern = veexlib.PHY_PATTERN_PRBS_11
        elif rxPatternParam.upper().startswith(b"PRBS11INV"):
            rxPattern = veexlib.PHY_PATTERN_PRBS_11_INV
        elif rxPatternParam.upper().startswith(b"PRBS13"):
            rxPattern = veexlib.PHY_PATTERN_PRBS_13
        elif rxPatternParam.upper().startswith(b"PRBS13INV"):
            rxPattern = veexlib.PHY_PATTERN_PRBS_13_INV
        elif rxPatternParam.upper().startswith(b"PRBS15"):
            rxPattern = veexlib.PHY_PATTERN_PRBS_15
        elif rxPatternParam.upper().startswith(b"PRBS15INV"):
            rxPattern = veexlib.PHY_PATTERN_PRBS_15_INV
        elif rxPatternParam.upper().startswith(b"PRBS20"):
            rxPattern = veexlib.PHY_PATTERN_PRBS_20
        elif rxPatternParam.upper().startswith(b"PRBS20INV"):
            rxPattern = veexlib.PHY_PATTERN_PRBS_20_INV
        elif rxPatternParam.upper().startswith(b"PRBS23"):
            rxPattern = veexlib.PHY_PATTERN_PRBS_23
        elif rxPatternParam.upper().startswith(b"PRBS23INV"):
            rxPattern = veexlib.PHY_PATTERN_PRBS_23_INV
        elif rxPatternParam.upper().startswith(b"PRBS31"):
            rxPattern = veexlib.PHY_PATTERN_PRBS_31
        elif rxPatternParam.upper().startswith(b"PRBS31INV"):
            rxPattern = veexlib.PHY_PATTERN_PRBS_31_INV
        elif rxPatternParam.upper().startswith(b"SQUARE"):
            rxPattern = veexlib.PHY_PATTERN_SQUARE_WAVE
        if rxPattern == veexlib.PHY_PATTERN_USER:
            userPattern = ParseUtils.checkNumeric(rxPatternParam)
            if userPattern < 0:
                return self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        if len(paramList) == 1 and laneCount == 1:
            if rxPattern == veexlib.PHY_PATTERN_USER:
                rxUserPattern = self.globals.veexPhy.sets.rxUserPattern
                rxUserPattern[0] = userPattern
                self.globals.veexPhy.sets.rxUserPattern = rxUserPattern
            else:
                pattern = self.globals.veexPhy.sets.rxPattern
                pattern[0] = rxPattern
                self.globals.veexPhy.sets.rxPattern = pattern
        elif len(paramList) >= 2:
            lane = ParseUtils.checkNumeric(paramList[0].head)
            if paramList[0].head.upper().startswith(b"ALL"):
                self.globals.veexPhy.sets.setRxPattern(rxPattern, -1)
            elif lane >= 0 and lane < laneCount:
                pattern = self.globals.veexPhy.sets.rxPattern
                pattern[0] = rxPattern
                self.globals.veexPhy.sets.rxPattern = pattern
            else:
                response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        return response

    def getRxPowLowThreshhold(self,parameters):
        '''**RX:PWRLOWT?** -
        Queries the value in dBm for the Power Low Threshold Alarm or OFF.
        '''
        self.globals.veexPhy.sets.update()
        if math.isclose(self.globals.veexPhy.sets.rxPowerMinimum, -100.0, rel_tol = 0.000001):
            response = b"OFF";
        else:
            response += b"%.1f dBm" % (self.globals.veexPhy.sets.rxPowerMinimum * 100.0,)
        return response  

    def setRxPowLowThreshhold(self, parameters):
        '''**RX:PWRLOWT:<value>** -
        Enables and sets the dBm value for the Power Low Threshold Alarm for all Optical lanes.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if ParseUtils.isFloatSdh(paramList[0].head):
                powerLowThresh = float(paramList[0].head)
                if math.isclose(powerLowThresh, 0.00, rel_tol = 0.000001):
                    self.globals.veexPhy.stets.rxPowerMinimum = -100.0
                elif powerLowThresh >= 0.0 and powerLowThresh <= 100.0:
                    self.globals.veexPhy.stets.rxPowerMinimum = powerLowThresh * 0.01
                else:
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getSerDegradedActivate(self,parameters):
        '''**RX:SERACTTHRESHold?** -
        Queries the number of FEC Degraded SER Activate Threshold Symbols or DISABLE.
        '''
        self.globals.veexPcs.sets.update()
        if self.globals.veexPcs.sets.serDegradedActivateThreshold == 0:
            response = b"DISABLE";
        else:
            response += b"%d" % self.globals.veexPcs.sets.serDegradedActivateThreshold
        return response  

    def setSerDegradedActivate(self, parameters):
        '''**RX:SERACTTHRESHold:<value>** -
        Enables and sets the number of Symbols for the FEC Degraded SER Activate Threshold.
        '''
        self.globals.veexPcs.sets.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value < 0:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            else: 
                enable = self.globals.veexPcs.sets.serDegradedEnable
                intervalThreshold = self.globals.veexPcs.sets.serDegradedIntervalThreshold
                deactivateThreshold = self.globals.veexPcs.sets.serDegradedDeactivateThreshold
                self.globals.veexPcs.sets.setSerDegraded(enable,intervalThreshold,value,deactivateThreshold)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getSerDegradedDeactivate(self,parameters):
        '''**RX:SERDEACTTHRESHold?** -
        Queries the number of FEC Degraded SER Deactivate Threshold Symbols, or DISABLE.
        '''
        self.globals.veexPcs.sets.update()
        if self.globals.veexPcs.sets.serDegradedDeactivateThreshold == 0:
            response = b"DISABLE";
        else:
            response += b"%d" % self.globals.veexPcs.sets.serDegradedDeactivateThreshold
        return response  

    def setSerDegradedDeactivate(self, parameters):
        '''**RX:SERDEACTTHRESHold:<value>** -
        Enables and sets the number of Symbols for the FEC Degraded SER Deactivate Threshold.
        '''
        self.globals.veexPcs.sets.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value < 0:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            else: 
                enable = self.globals.veexPcs.sets.serDegradedEnable
                intervalThreshold = self.globals.veexPcs.sets.serDegradedIntervalThreshold
                activateThreshold = self.globals.veexPcs.sets.serDegradedActivateThreshold
                self.globals.veexPcs.sets.setSerDegraded(enable,intervalThreshold,activateThreshold,value)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getSerDegradedInterval(self,parameters):
        '''**RX:SERDEGINTER?** -
        Queries the number of FEC Degraded SER Degrade Interval Codewords or DISABLE.
        '''
        self.globals.veexPcs.sets.update()
        if self.globals.veexPcs.sets.serDegradedIntervalThreshold == 0:
            response = b"DISABLE";
        else:
            response += b"%d" % self.globals.veexPcs.sets.serDegradedIntervalThreshold
        return response  

    def setSerDegradedInterval(self, parameters):
        '''**RX:SERDEGINTER:<value>** -
        Enables and sets the measurement period for the FEC Degraded SER Degrade Interval.
        '''
        self.globals.veexPcs.sets.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value < 0:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            else: 
                enable = self.globals.veexPcs.sets.serDegradedEnable
                activateThreshold = self.globals.veexPcs.sets.serDegradedActivateThreshold
                deactivateThreshold = self.globals.veexPcs.sets.serDegradedDeactivateThreshold
                self.globals.veexPcs.sets.setSerDegraded(enable,value,activateThreshold,deactivateThreshold)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxSkewThreshhold(self,parameters):
        '''**RX:SKEWTHRESHold?** -
        Queries the received Skew Threshold setting.
        '''
        self.globals.veexPcs.sets.update()
        return b"%d" % self.globals.veexPcs.sets.rxLaneSkewThreshold  

    def setRxSkewThreshhold(self, parameters):
        '''**RX:SKEWTHRESHold:<threshold>** -
        Enables and sets the Skew Threshold value (in bits) for the received SKEW alarm.
        '''
        self.globals.veexPcs.sets.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value < 0:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            elif value <= 65000: 
                self.globals.veexPcs.sets.rxLaneSkewThreshold = value
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def resAisSecs(self,parameters):
        '''**RES:AIS:Secs?** -
        Queries the number of Alarm Indication Signal alarm seconds.
        '''
        # Double check -- this is an example, but I can not find the variable ais in veexPcs. 
        self.globals.veexPcs.stats.update()
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes";
        else:
            response = b""
            for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
                if lane != 0:
                    response += b", "
                response += b"%d" % self.globals.veexPcs.stats.ais[lane].alarmSecs 
        return response   

    def resAlarmAlignMarkState(self,parameters):
        '''**RES:AL:ALMARK?** -
        Queries the ALMARK LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.summaryAlignMarkLed.led.isRed else b"OFF"

    def resAlarmBip8State(self,parameters):
        '''**RES:AL:BIP8?** -
        Queries the BIP8 LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.summaryBip8Led.led.isRed else b"OFF"

    def resAlarmBitState(self,parameters):
        '''**RES:AL:BIT?** -
        Queries the BIT ERR LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        return b"ON" if self.globals.veexPhy.stats.summaryBitLed.led.isRed else b"OFF"

    def resAlarmBlockLockState(self,parameters):
        '''**RES:AL:BLKLOC?** -
        Queries the BLKLOC LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.summaryBlockLockLossLed.led.isRed else b"OFF"

    def resAlarmBlockState(self,parameters):
        '''**RES:AL:BLOCK?** -
        Queries the BLOCK LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.block.led.isRed else b"OFF"

    def resAlarmClockState(self,parameters):
        '''**RES:AL:CLOCK?** -
        Queries the CLOCK LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.clock.led.isRed else b"OFF"

    def resAlarmFecAlignMarkPadState(self,parameters):
        '''**RES:AL:FECALMARKPAD?** -
        Queries the FECALMARKPAD LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecAlignMarkPad.led.isRed else b"OFF"

    def resAlarmFecTranscodeState(self,parameters):
        '''**RES:AL:FECCODE?** -
        Queries the FECCODE LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecTranscode.led.isRed else b"OFF"

    def resAlarmFecCorrState(self,parameters):
        '''**RES:AL:FECCORBIT?** -
        Queries the FECCORBIT LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecCorrectable.led.isRed else b"OFF"

    def resAlarmFecCorrBitAState(self,parameters):
        '''**RES:AL:FECCORBIT:A?** -
        Queries the FECCORBIT:A LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanACorrectableBit.led.isRed else b"OFF"

    def resAlarmFecCorrBitABState(self,parameters):
        '''**RES:AL:FECCORBIT:AB?** -
        Queries the FECCORBIT:AB LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanABCorrectableBit.led.isRed else b"OFF"

    def resAlarmFecCorrBitBState(self,parameters):
        '''**RES:AL:FECCORBIT:AB?** -
        Queries the FECCORBIT:AB LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanBCorrectableBit.led.isRed else b"OFF"

    def resAlarmFecCorrBitLaneState(self,parameters):
        '''**RES:AL:FECCORBITLANE? <lane>** -
        Queries the FECCORBITLANE LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        if len(paramList) >= 1:
            lane = ParseUtils.checkNumeric(paramList[0].head)
            if lane < 0 or lane >= 16:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            else:
                response = b"ON" if self.globals.veexPcs.stats.fecCorrectableBitLane[lane].led.isRed else b"OFF"
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def resAlarmFecCorrCwState(self,parameters):
        '''**RES:AL:FECCORCW?** -
        Queries the FECCORCW LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecCorrectableCw.led.isRed else b"OFF"

    def resAlarmFecCorrCwAState(self,parameters):
        '''**RES:AL:FECCORCW:A?** -
        Queries the FECCORCW:A LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanACorrectableCw.led.isRed else b"OFF"

    def resAlarmFecCorrCwABState(self,parameters):
        '''**RES:AL:FECCORCW:AB?** -
        Queries the FECCORCW:AB LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanABCorrectableCw.led.isRed else b"OFF"

    def resAlarmFecCorrCwBState(self,parameters):
        '''**RES:AL:FECCORCW:B?** -
        Queries the FECCORCW:B LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanBCorrectableCw.led.isRed else b"OFF"

    def resAlarmFecCorrOnesAState(self,parameters):
        '''**RES:AL:FECCORONES:A?** -
        Queries the FECCORONES:A LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanACorrectableOnes.led.isRed else b"OFF"

    def resAlarmFecCorrOnesABState(self,parameters):
        '''**RES:AL:FECCORONES:AB?** -
        Queries the FECCORONES:AB LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanABCorrectableOnes.led.isRed else b"OFF"

    def resAlarmFecCorrOnesBState(self,parameters):
        '''**RES:AL:FECCORONES:B?** -
        Queries the FECCORONES:B LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanBCorrectableOnes.led.isRed else b"OFF"

    def resAlarmFecCorrSymbolState(self,parameters):
        '''**RES:AL:FECCORSYM?** -
        Queries the FECCORSYM LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecCorrectableSymbol.led.isRed else b"OFF"

    def resAlarmFecCorrSymAState(self,parameters):
        '''**RES:AL:FECCORSYM:A?** -
        Queries the FECCORSYM:A LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanACorrectableSymbol.led.isRed else b"OFF"

    def resAlarmFecCorrSymABState(self,parameters):
        '''**RES:AL:FECCORSYM:AB?** -
        Queries the FECCORSYM:AB LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanABCorrectableSymbol.led.isRed else b"OFF"

    def resAlarmFecCorrSymBState(self,parameters):
        '''**RES:AL:FECCORSYM:B?** -
        Queries the FECCORSYM:B LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanBCorrectableSymbol.led.isRed else b"OFF"

    def resAlarmFecCorrSymbolLaneState(self,parameters):
        '''**RES:AL:FECCORSYMLANE? <lane>** -
        Queries the FECCORSYMLANE LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        if len(paramList) >= 1:
            lane = ParseUtils.checkNumeric(paramList[0].head)
            if lane < 0 or lane >= 16:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            else:
                response = b"ON" if self.globals.veexPcs.stats.fecCorrectableSymbolLane[lane].led.isRed else b"OFF"
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def resAlarmFecCorrZerosAState(self,parameters):
        '''**RES:AL:FECCORZEROS:A?** -
        Queries the FECCORZEROS:A LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanACorrectableZeros.led.isRed else b"OFF"

    def resAlarmFecCorrZerosABState(self,parameters):
        '''**RES:AL:FECCORZEROS:AB?** -
        Queries the FECCORZEROS:AB LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanABCorrectableZeros.led.isRed else b"OFF"

    def resAlarmFecCorrZerosBState(self,parameters):
        '''**RES:AL:FECCORZEROS:B?** -
        Queries the FECCORZEROS:B LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanBCorrectableZeros.led.isRed else b"OFF"
    
    def resAlarmFecLoaState(self,parameters):
        '''**RES:AL:FECLOA?** -
        Queries the FECLOA LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecLoa.led.isRed else b"OFF"

    def resAlarmFecUncorrState(self,parameters):
        '''**RES:AL:FECUNCOR?** -
        Queries the FECUNCOR LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecUncorrectable.led.isRed else b"OFF"

    def resAlarmFecUnCorrAState(self,parameters):
        '''**RES:AL:FECUNCOR:A?** -
        Queries the FECUNCOR:A LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanAUncorrectable.led.isRed else b"OFF"

    def resAlarmFecUnCorrABState(self,parameters):
        '''**RES:AL:FECUNCOR:AB?** -
        Queries the FECUNCOR:AB LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanABUncorrectable.led.isRed else b"OFF"

    def resAlarmFecUnCorrBState(self,parameters):
        '''**RES:AL:FECUNCOR:B?** -
        Queries the FECUNCOR:B LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.fecChanBUncorrectable.led.isRed else b"OFF"

    def resAlarmFreqWideState(self,parameters):
        '''**RES:AL:FREQWIDE?** -
        Queries the FREQWIDE LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        for lane in range(self.globals.veexPhy.stats.rxHostLaneCount):
            if self.globals.veexPhy.stats.rxFreqWide[lane].led.isRed:
                response = b"ON"
                break
        if len(response) == 0:
            response = b"OFF"
        return response

    def resAlarmHiBerState(self,parameters):
        '''**RES:AL:HIBER?** -
        Queries the HIBER LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.hiBer.led.isRed else b"OFF"

    def resAlarmHiSerState(self,parameters):
        '''**RES:AL:HISER?** -
        Queries the HISER LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.hiSer.led.isRed else b"OFF"

    def resAlarmLaneSummaryState(self,parameters):
        '''**RES:AL:LANESUM?** -
        Queries the LANESUM LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        else:
            for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
                if len(response) != 0:
                    response += b", "
                if self.globals.veexPcs.stats.rxLaneMap[lane] > 20:
                    response += b"ON"
                elif self.globals.veexPcs.stats.summaryLaneLed[lane].led.isRed:
                    response += b"ON"
                else:
                    response += b"OFF"
        return response

    def resAlarmLoaState(self,parameters):
        '''**RES:AL:LOA?** -
        Queries the LOA LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.loa.led.isRed else b"OFF"

    def resAlarmLoAlmState(self,parameters):
        '''**RES:AL:LOALM?** -
        Queries the LOALM LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.summaryAlignMarkLossLed.led.isRed else b"OFF"

    def resAlarmFecLoampsState(self,parameters):
        '''**RES:AL:LOAMPS?** -
        Queries the LOAMPS LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if self.globals.veexPcs.stats.fecAlignMarkLoss[lane].led.isRed:
                response = b"ON"
                break
        if len(response) == 0:
            response = b"OFF"
        return response

#    def resAlarmLofState(self,parameters):
#        '''**RES:AL:LOF?** -
#        Queries the LOF LED state (ON or OFF)
#        '''
#        self.globals.veexPcs.stats.update()
#        return b"ON" if self.globals.veexPcs.stats.lof.led.isRed else b"OFF"

#    def resAlarmLorState(self,parameters):
#        '''**RES:AL:LOR?** -
#        Queries the LOR LED state (ON or OFF)
#        '''
#        self.globals.veexPcs.stats.update()
#        return b"ON" if self.globals.veexPcs.stats.lor.led.isRed else b"OFF"

    def resAlarmLosState(self,parameters):
        '''**RES:AL:LOS?** -
        Queries the LOS LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        return b"ON" if self.globals.veexPhy.stats.los.led.isRed else b"OFF"

    def resAlarmSummaryModuleState(self,parameters):
        '''**RES:AL:MODULESTATUS?** -
        Queries the MODULESTATUS LED state (ON or OFF)
        '''
        # Double check - PCS or PHY?
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.summaryModuleLed.led.isRed:
            response = b"ON"
        elif self.globals.veexPcs.stats.summaryModuleLed.led.isYellow:
            response = b"WARN"
        else:
            response = b"OFF"
        return response

#    def resAlarmOofState(self,parameters):
#        '''**RES:AL:OOF?** -
#        Queries the OOF LED state (ON or OFF)
#        '''
#        self.globals.veexPcs.stats.update()
#        return b"ON" if self.globals.veexPcs.stats.oof.led.isRed else b"OFF"

#    def resAlarmOorState(self,parameters):
#        '''**RES:AL:OOR?** -
#        Queries the OOR LED state (ON or OFF)
#        '''
#        self.globals.veexPcs.stats.update()
#        return b"ON" if self.globals.veexPcs.stats.oor.led.isRed else b"OFF"

    def resAlarmPatSyncState(self,parameters):
        '''**RES:AL:PAT?** -
        Queries the PAT SYNC LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        return b"ON" if self.globals.veexPhy.stats.summaryPatternSyncLed.led.isRed else b"OFF"

    def resAlarmPausedState(self,parameters):
        '''**RES:AL:PAUSED?** -
        Queries the PAUSED LED state (ON or OFF)
        '''
        # Double check -- Phy or Pcs
        self.globals.veexPhy.stats.update()
        return b"ON" if self.globals.veexPhy.stats.testPaused.led.isRed else b"OFF"

    def resAlarmRxPowerHighAlarmThresholdState(self,parameters):
        '''**RES:AL:RXPWRHIALARM?** -
        Queries the RXPWRHIALARM LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        for lane in range(self.globals.veexPhy.allowedSets().txOpticalLaneCount):
            if self.globals.veexPhy.stats.rxPowerHighAlarmThreshold[lane].led.isRed:
                response = b"ON"
        if len(response) == 0:
            response = b"OFF"
        return response

    def resAlarmRxPowerHighWarningThresholdState(self,parameters):
        '''**RES:AL:RXPWRHIWARN?** -
        Queries the RXPWRHIWARN LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        for lane in range(self.globals.veexPhy.allowedSets().txOpticalLaneCount):
            if self.globals.veexPhy.stats.txPowerHighWarningThreshold[lane].led.isRed:
                response = b"ON"
        if len(response) == 0:
            response = b"OFF"
        return response

    def resAlarmRxPowerLowAlarmThresholdState(self,parameters):
        '''**RES:AL:RXPWRLOALARM?** -
        Queries the RXPWRLOALARM LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        for lane in range(self.globals.veexPhy.allowedSets().txOpticalLaneCount):
            if self.globals.veexPhy.stats.rxPowerLowAlarmThreshold[lane].led.isRed:
                response = b"ON"
        if len(response) == 0:
            response = b"OFF"
        return response

    def resAlarmRxPowerLowWarningThresholdState(self,parameters):
        '''**RES:AL:RXPWRLOWARN?** -
        Queries the RXPWRLOWARN LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        for lane in range(self.globals.veexPhy.allowedSets().txOpticalLaneCount):
            if self.globals.veexPhy.stats.txPowerLowWarningThreshold[lane].led.isRed:
                response = b"ON"
        if len(response) == 0:
            response = b"OFF"
        return response

    def resAlarmSkewState(self,parameters):
        '''**RES:AL:SKEW?** -
        Queries the SKEW LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.summaryLaneSkewLed.led.isRed else b"OFF"

    def resAlarmSummaryState(self,parameters):
        '''**RES:AL:SUMMary?** -
        Queries the Lane Details Summary LED state (ON or OFF)
        '''
        # Double check - PCS or PHY?
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.summaryLed.led.isRed else b"OFF"

    def resAlarmSyncHdrState(self,parameters):
        '''**RES:AL:SYNCHDR?** -
        Queries the SYNCHDR LED state (ON or OFF)
        '''
        self.globals.veexPcs.stats.update()
        return b"ON" if self.globals.veexPcs.stats.summarySyncHdrLed.led.isRed else b"OFF"

    def resAlarmTempHighAlarmThresholdState(self,parameters):
        '''**RES:AL:TEMPHIALARM?** -
        Queries the TEMPHIALARM LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        return b"ON" if self.globals.veexPhy.stats.tempHighAlarmThreshold.led.isRed else b"OFF"

    def resAlarmTempHighWarningThresholdState(self,parameters):
        '''**RES:AL:TEMPHIWARN?** -
        Queries the TEMPHIWARN LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        return b"ON" if self.globals.veexPhy.stats.tempHighWarningThreshold.led.isRed else b"OFF"

    def resAlarmTempLowAlarmThresholdState(self,parameters):
        '''**RES:AL:TEMPLOALARM?** -
        Queries the TEMPLOALARM LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        return b"ON" if self.globals.veexPhy.stats.tempLowAlarmThreshold.led.isRed else b"OFF"

    def resAlarmTempLowWarningThresholdState(self,parameters):
        '''**RES:AL:TEMPLOWARN?** -
        Queries the TEMPLOWARN LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        return b"ON" if self.globals.veexPhy.stats.tempLowWarningThreshold.led.isRed else b"OFF"

    def resAlarmTxBiasHighAlarmThresholdState(self,parameters):
        '''**RES:AL:TXBIASHIALARM?** -
        Queries the TXBIASHIALARM LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets.update()
        response = b""
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if self.globals.veexPhy.stats.txBiasHighAlarmThreshold[lane].led.isRed:
                response = b"ON"
                break
        if len(response) == 0:
            response = b"OFF"
        return response

    def resAlarmTxBiasHighWarningThresholdState(self,parameters):
        '''**RES:AL:TXBIASHIWARN?** -
        Queries the TXBIASHIWARN LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets.update()
        response = b""
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if self.globals.veexPhy.stats.txBiasHighWarningThreshold[lane].led.isRed:
                response = b"ON"
                break
        if len(response) == 0:
            response = b"OFF"
        return response

    def resAlarmTxBiasLowAlarmThresholdState(self,parameters):
        '''**RES:AL:TXBIASLOALARM?** -
        Queries the TXBIASLOALARM LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets.update()
        response = b""
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if self.globals.veexPhy.stats.txBiasLowAlarmThreshold[lane].led.isRed:
                response = b"ON"
                break
        if len(response) == 0:
            response = b"OFF"
        return response

    def resAlarmTxBiasLowWarningThresholdState(self,parameters):
        '''**RES:AL:TXBIASLOWARN?** -
        Queries the TXBIASLOWARN LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets.update()
        response = b""
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if self.globals.veexPhy.stats.txBiasLowWarningThreshold[lane].led.isRed:
                response = b"ON"
                break
        if len(response) == 0:
            response = b"OFF"
        return response

    def resAlarmTxPowerHighAlarmThresholdState(self,parameters):
        '''**RES:AL:TXPWRHIALARM?** -
        Queries the TXPWRHIALARM LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets.update()
        response = b""
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if self.globals.veexPhy.stats.txPowerHighAlarmThreshold[lane].led.isRed:
                response = b"ON"
                break
        if len(response) == 0:
            response = b"OFF"
        return response

    def resAlarmTxPowerHighWarningThresholdState(self,parameters):
        '''**RES:AL:TXPWRHIWARN?** -
        Queries the TXPWRHIWARN LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets.update()
        response = b""
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if self.globals.veexPhy.stats.txPowerHighWarningThreshold[lane].led.isRed:
                response = b"ON"
                break
        if len(response) == 0:
            response = b"OFF"
        return response

    def resAlarmTxPowerLowAlarmThresholdState(self,parameters):
        '''**RES:AL:TXPWRLOALARM?** -
        Queries the TXPWRLOALARM LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets.update()
        response = b""
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if self.globals.veexPhy.stats.txPowerLowAlarmThreshold[lane].led.isRed:
                response = b"ON"
                break
        if len(response) == 0:
            response = b"OFF"
        return response

    def resAlarmTxPowerLowWarningThresholdState(self,parameters):
        '''**RES:AL:TXPWRLOWARN?** -
        Queries the TXPWRLOWARN LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets.update()
        response = b""
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if self.globals.veexPhy.stats.txPowerLowWarningThreshold[lane].led.isRed:
                response = b"ON"
                break
        if len(response) == 0:
            response = b"OFF"
        return response

    def resAlarmVccHighAlarmThresholdState(self,parameters):
        '''**RES:AL:VCCHIALARM?** -
        Queries the VCCHIALARM LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        return b"ON" if self.globals.veexPhy.stats.vccHighAlarmThreshold.led.isRed else b"OFF"

    def resAlarmVccHighWarningThresholdState(self,parameters):
        '''**RES:AL:VCCHIWARN?** -
        Queries the VCCHIWARN LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        return b"ON" if self.globals.veexPhy.stats.vccHighWarningThreshold.led.isRed else b"OFF"

    def resAlarmVccLowAlarmThresholdState(self,parameters):
        '''**RES:AL:VCCLOALARM?** -
        Queries the VCCLOALARM LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        return b"ON" if self.globals.veexPhy.stats.vccLowAlarmThreshold.led.isRed else b"OFF"

    def resAlarmVccLowWarningThresholdState(self,parameters):
        '''**RES:AL:VCCLOWARN?** -
        Queries the VCCLOWARN LED state (ON or OFF)
        '''
        self.globals.veexPhy.stats.update()
        return b"ON" if self.globals.veexPhy.stats.vccLowWarningThreshold.led.isRed else b"OFF"

    def resAlignMarkAvg(self,parameters):
        '''**RES:ALMARK:AVErage?** -
        Queries the average Alignment Marker error rate for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%1.2e" % self.globals.veexPcs.stats.alignMark[lane].avgRate
        return response

    def resAlignMarkCount(self,parameters):
        '''**RES:ALMARK:COUNt?** -
        Queries the Alignment Marker error count for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPcs.stats.alignMark[lane].count
        return response

    def resAlignMarkRate(self,parameters):
        '''**RES:ALMARK:RATe?** -
        Queries the current Alignment Marker error rate for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%1.2e" % self.globals.veexPcs.stats.alignMark[lane].currRate
        return response

    def resBip8Avg(self,parameters):
        '''**RES:BIP8:AVErage?** -
        Queries the average BIP-8 error rate for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%1.2e" % self.globals.veexPcs.stats.bip8[lane].avgRate
        return response

    def resBip8Count(self,parameters):
        '''**RES:BIP8:COUNt?** -
        Queries the BIP-8 error count for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPcs.stats.bip8[lane].count
        return response

    def resBip8Rate(self,parameters):
        '''**RES:BIP8:RATe?** -
        Queries the current BIP-8 error rate for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%1.2e" % self.globals.veexPcs.stats.bip8[lane].currRate
        return response

    def resBitAvg(self,parameters):
        '''**RES:BIT:AVErage?** -
        Queries the average BIT error rate for all PCS lane positions.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        if self.globals.veexPhy.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.stats.rxVirtLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%1.2e" % self.globals.veexPhy.stats.bit[lane].avgRate
        return response

    def resBitCount(self,parameters):
        '''**RES:BIT:COUNt?** -
        Queries the BIT error count for all PCS lane positions.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        if self.globals.veexPhy.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.stats.rxVirtLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.bit[lane].count
        return response

    def resBitRate(self,parameters):
        '''**RES:BIT:RATe?** -
        Queries the current BIT error rate for all PCS lane positions.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        if self.globals.veexPhy.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.stats.rxVirtLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%1.2e" % self.globals.veexPhy.stats.bit[lane].currRate
        return response

    def resBlockLockSecs(self,parameters):
        '''**RES:BLKLOC:Secs?** -
        Queries the number of Loss of Block Lock alarm seconds for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPcs.stats.blockLockLoss[lane].secs
        return response

    def resClockSecs(self,parameters):
        '''**RES:CLOCK:Secs?** -
        Queries the number of TX Clock Loss alarm seconds.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.clock.secs

    def resPowerSecs(self,parameters):
        '''**RES:CPPOWERLOSS:Secs?** -
        Queries the number of A/C power loss alarm seconds.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.cpPowerLoss.secs

    def resDegSerSecs(self,parameters):
        '''**RES:DEGSER:Secs?** -
        Queries the number of FEC Degraded Symbol Error Ratio alarm seconds.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.serDegraded.secs

    def getEventLog(self,parameters):
        '''**RES:EVENTLOG <StartRecord>?** -
        Queries the events listed in the Event Log, up to a maximum of 64 events
        '''
        # TBD -- Event log is not implemented now.
        self.globals.veexPhy.stats.update()

    def resFecAlignMarkPadAvg(self,parameters):
        '''**RES:FECALMARKPAD:AVE?** -
        Queries the FEC Alignment Marker Pad Errors average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecAlignMarkPad.avgRate

    def resFecAlignMarkPadCount(self,parameters):
        '''**RES:FECALMARKPAD:COUNt?** -
        Queries the FEC Alignment Marker Pad Errors error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecAlignMarkPad.count
    
    def resFecAlignMarkPadRate(self,parameters):
        '''**RES:FECALMARKPAD:RATe?** -
        Queries the FEC Alignment Marker Pad Errors current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecAlignMarkPad.currRate

    def resFecCorSymCountCount(self,parameters):
        '''**RES:FECANALYSIS:COUNt? <Symbol #>** -
        Queries the FEC Analysis's FEC Correctable Symbol Error Count for the specified <Symbol #> from 1 to 15.
        '''
        self.globals.veexPcs.stats.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        if len(paramList) >= 1:
            symbolN = ParseUtils.checkNumeric(paramList[0].head)
            if symbolN >= 1 and symbolN <= 15:
                response = b"%d" % self.globals.veexPcs.stats.fecCorrectableSymbolN[symbolN -1]   
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def resFecCorSymCountPct(self,parameters):
        '''**RES:FECANALYSIS:PERCENT? <Symbol #>** -
        Queries the FEC Analysis's FEC Correctable Symbol Error Percentage for the specified <Symbol #> from 1 to 15.
        '''
        self.globals.veexPcs.stats.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        if len(paramList) >= 1:
            symbolN = ParseUtils.checkNumeric(paramList[0].head)
            if symbolN >= 1 and symbolN <= 15:
                totalSymCount = 0
                for lane in range(15):
                    totalSymCount += self.globals.veexPcs.stats.fecCorrectableSymbolN[lane]
                if totalSymCount == 0:
                    response = b"%02.06f" % totalSymCount
                else:
                    response = b"%02.06f" % ((float(self.globals.veexPcs.stats.fecCorrectableSymbolN[symbolN -1]) / float(totalSymCount)) * 100.0,)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def resFecTranscodeAvg(self,parameters):
        '''**RES:FECCODE:AVE?** -
        Queries the FEC Correctable Transcoded Errors average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecTranscode.avgRate

    def resFecTranscodeCount(self,parameters):
        '''**RES:FECCODE:COUNt?** -
        Queries the FEC Correctable Transcoded Errors error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecTranscode.count
    
    def resFecTranscodeRate(self,parameters):
        '''**RES:FECCODE:RATe?** -
        Queries the FEC Correctable Transcoded Errors current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecTranscode.currRate

    def resFecCorrBitLaneAvg(self,parameters):
        '''**RES:FECCORBITLANE:AVE?** -
        Queries the FEC Correctable Bit Errors error counts for all FEC lanes.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        else:
            for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%.2e" % self.globals.veexPcs.stats.fecCorrectableBitLane[lane].avgRate
        return response

    def resFecCorrBitLaneCount(self,parameters):
        '''**RES:FECCORBITLANE:COUNt?** -
        Queries the FEC Correctable Bit Errors average error rates for all FEC lanes.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        else:
            for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%d" % self.globals.veexPcs.stats.fecCorrectableBitLane[lane].count
        return response

    def resFecCorrBitLaneRate(self,parameters):
        '''**RES:FECCORBITLANE:RATe?** -
        Queries the FEC Correctable Bit Errors current error rates for all FEC lanes.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        else:
            for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%.2e" % self.globals.veexPcs.stats.fecCorrectableBitLane[lane].currRate
        return response

    def resFecCorrBitAAvg(self,parameters):
        '''**RES:FECCORBIT:A:AVE?** -
        Queries the FEC Correctable Bit Errors (in Channel A) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanACorrectableBit.avgRate

    def resFecCorrBitACount(self,parameters):
        '''**RES:FECCORBIT:A:COUNt?** -
        Queries the FEC Correctable Bit Errors (in Channel A) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanACorrectableBit.count
    
    def resFecCorrBitARate(self,parameters):
        '''**RES:FECCORBIT:A:RATe?** -
        Queries the FEC Correctable Bit Errors (in Channel A) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanACorrectableBit.currRate

    def resFecCorrBitABAvg(self,parameters):
        '''**RES:FECCORBIT:AB:AVE?** -
        Queries the FEC Correctable Bit Errors (in Channel A & B)) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanABCorrectableBit.avgRate

    def resFecCorrBitABCount(self,parameters):
        '''**RES:FECCORBIT:AB:COUNt?** -
        Queries the FEC Correctable Bit Errors (in Channel A & B)) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanABCorrectableBit.count
    
    def resFecCorrBitABRate(self,parameters):
        '''**RES:FECCORBIT:AB:RATe?** -
        Queries the FEC Correctable Bit Errors (in Channel A & B)) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanABCorrectableBit.currRate

    def resFecCorrBitBAvg(self,parameters):
        '''**RES:FECCORBIT:B:AVE?** -
        Queries the FEC Correctable Bit Errors (in Channel B) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanBCorrectableBit.avgRate

    def resFecCorrBitBCount(self,parameters):
        '''**RES:FECCORBIT:B:COUNt?** -
        Queries the FEC Correctable Bit Errors (in Channel B) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanBCorrectableBit.count
    
    def resFecCorrBitBRate(self,parameters):
        '''**RES:FECCORBIT:B:RATe?** -
        Queries the FEC Correctable Bit Errors (in Channel B) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanBCorrectableBit.currRate

    def resFecCorrCwAAvg(self,parameters):
        '''**RES:FECCORCW:A:AVE?** -
        Queries the FEC Correctable Code Word Errors (in Channel A) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanACorrectableCw.avgRate

    def resFecCorrCwACount(self,parameters):
        '''**RES:FECCORCW:A:COUNt?** -
        Queries the FEC Correctable Code Word Errors (in Channel A) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanACorrectableCw.count
    
    def resFecCorrCwARate(self,parameters):
        '''**RES:FECCORCW:A:RATe?** -
        Queries the FEC Correctable Code Word Errors (in Channel A) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanACorrectableCw.currRate

    def resFecCorrCwABAvg(self,parameters):
        '''**RES:FECCORCW:AB:AVE?** -
        Queries the FEC Correctable Code Word Errors (in Channel A & B) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanABCorrectableCw.avgRate

    def resFecCorrCwABCount(self,parameters):
        '''**RES:FECCORCW:AB:COUNt?** -
        Queries the FEC Correctable Code Word Errors (in Channel A & B) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanABCorrectableCw.count
    
    def resFecCorrCwABRate(self,parameters):
        '''**RES:FECCORCW:AB:RATe?** -
        Queries the FEC Correctable Code Word Errors (in Channel A & B) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanABCorrectableCw.currRate

    def resFecCorrCwBAvg(self,parameters):
        '''**RES:FECCORCW:B:AVE?** -
        Queries the FEC Correctable Code Word Errors (in Channel B) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanBCorrectableCw.avgRate

    def resFecCorrCwBCount(self,parameters):
        '''**RES:FECCORCW:B:COUNt?** -
        Queries the FEC Correctable Code Word Errors (in Channel B) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanBCorrectableCw.count
    
    def resFecCorrCwBRate(self,parameters):
        '''**RES:FECCORCW:B:RATe?** -
        Queries the FEC Correctable Code Word Errors (in Channel B) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanBCorrectableCw.currRate

    def resFecCorrOnesAAvg(self,parameters):
        '''**RES:FECCORONES:A:AVE?** -
        Queries the FEC Correctable Ones Errors (in Channel A) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanACorrectableOnes.avgRate

    def resFecCorrOnesACount(self,parameters):
        '''**RES:FECCORONES:A:COUNt?** -
        Queries the FEC Correctable Ones Errors (in Channel A) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanACorrectableOnes.count
    
    def resFecCorrOnesARate(self,parameters):
        '''**RES:FECCORONES:A:RATe?** -
        Queries the FEC Correctable Ones Errors (in Channel A) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanACorrectableOnes.currRate

    def resFecCorrOnesABAvg(self,parameters):
        '''**RES:FECCORONES:AB:AVE?** -
        Queries the FEC Correctable Ones Errors (in Channel A & B) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanABCorrectableOnes.avgRate

    def resFecCorrOnesABCount(self,parameters):
        '''**RES:FECCORONES:AB:COUNt?** -
        Queries the FEC Correctable Ones Errors (in Channel A & B) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanABCorrectableOnes.count
    
    def resFecCorrOnesABRate(self,parameters):
        '''**RES:FECCORONES:AB:RATe?** -
        Queries the FEC Correctable Ones Errors (in Channel A & B) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanABCorrectableOnes.currRate

    def resFecCorrOnesBAvg(self,parameters):
        '''**RES:FECCORONES:B:AVE?** -
        Queries the FEC Correctable Ones Errors (in Channel B) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanBCorrectableZeros.avgRate

    def resFecCorrOnesBCount(self,parameters):
        '''**RES:FECCORONES:B:COUNt?** -
        Queries the FEC Correctable Ones Errors (in Channel B) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanBCorrectableZeros.count
    
    def resFecCorrOnesBRate(self,parameters):
        '''**RES:FECCORONES:B:RATe?** -
        Queries the FEC Correctable Ones Errors (in Channel B) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanBCorrectableZeros.currRate

    def resFecCorrAvg(self,parameters):
        '''**RES:FECCORR:AVE?** -
        Queries the FEC Correctable Bit Errors average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecCorrectable.avgRate

    def resFecCorrCount(self,parameters):
        '''**RES:FECCORR:COUNt?** -
        Queries the FEC Correctable Bit Errors error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecCorrectable.count
    
    def resFecCorrRate(self,parameters):
        '''**RES:FECCORR:RATe?** -
        Queries the FEC Correctable Bit Errors current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecCorrectable.currRate

    def resFecCorrSymbolAvg(self,parameters):
        '''**RES:FECCORSYM:AVE?** -
        Queries the FEC Correctable Symbol Errors average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecCorrectableSymbol.avgRate

    def resFecCorrSymbolCount(self,parameters):
        '''**RES:FECCORSYM:COUNt?** -
        Queries the FEC Correctable Symbol Errors error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecCorrectableSymbol.count
    
    def resFecCorrSymbolRate(self,parameters):
        '''**RES:FECCORSYM:RATe?** -
        Queries the FEC Correctable Symbol Errors current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecCorrectableSymbol.currRate

    def resFecCorrSymbolAAvg(self,parameters):
        '''**RES:FECCORSYM:A:AVE?** -
        Queries the FEC Correctable Symbol Errors(in Channel A) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanACorrectableSymbol.avgRate

    def resFecCorrSymbolACount(self,parameters):
        '''**RES:FECCORSYM:A:COUNt?** -
        Queries the FEC Correctable Symbol Errors(in Channel A) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanACorrectableSymbol.count
    
    def resFecCorrSymbolARate(self,parameters):
        '''**RES:FECCORSYM:A:RATe?** -
        Queries the FEC Correctable Symbol Errors(in Channel A) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanACorrectableSymbol.currRate

    def resFecCorrSymbolABAvg(self,parameters):
        '''**RES:FECCORSYM:AB:AVE?** -
        Queries the FEC Correctable Symbol Errors(in Channel A & B) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanABCorrectableSymbol.avgRate

    def resFecCorrSymbolABCount(self,parameters):
        '''**RES:FECCORSYM:AB:COUNt?** -
        Queries the FEC Correctable Symbol Errors(in Channel A & B) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanABCorrectableSymbol.count
    
    def resFecCorrSymbolABRate(self,parameters):
        '''**RES:FECCORSYM:AB:RATe?** -
        Queries the FEC Correctable Symbol Errors(in Channel A & B) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanABCorrectableSymbol.currRate

    def resFecCorrSymbolBAvg(self,parameters):
        '''**RES:FECCORSYM:B:AVE?** -
        Queries the FEC Correctable Symbol Errors(in Channel B) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanBCorrectableSymbol.avgRate

    def resFecCorrSymbolBCount(self,parameters):
        '''**RES:FECCORSYM:B:COUNt?** -
        Queries the FEC Correctable Symbol Errors(in Channel B) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanBCorrectableSymbol.count
    
    def resFecCorrSymbolBRate(self,parameters):
        '''**RES:FECCORSYM:B:RATe?** -
        Queries the FEC Correctable Symbol Errors(in Channel B) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanBCorrectableSymbol.currRate

    def resFecCorrSymbolLaneAvg(self,parameters):
        '''**RES:FECCORSYMLANE:AVE?** -
        Queries the FEC Correctable Symbol Errors error counts for all FEC lanes.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        else:
            for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%.2e" % self.globals.veexPcs.stats.fecCorrectableSymbolLane[lane].avgRate
        return response

    def resFecCorrSymbolLaneCount(self,parameters):
        '''**RES:FECCORSYMLANE:COUNt?** -
        Queries the FEC Correctable Symbol Errors average error rates for all FEC lanes.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        else:
            for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%d" % self.globals.veexPcs.stats.fecCorrectableSymbolLane[lane].count
        return response

    def resFecCorrSymbolLaneRate(self,parameters):
        '''**RES:FECCORSYMLANE:RATe?** -
        Queries the FEC Correctable Symbol Errors current error rates for all FEC lanes.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        else:
            for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%.2e" % self.globals.veexPcs.stats.fecCorrectableSymbolLane[lane].currRate
        return response

    def resFecCorrZerosAAvg(self,parameters):
        '''**RES:FECCORSYM:A:AVE?** -
        Queries the FEC Correctable Zeros Errors(in Channel A) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanACorrectableZeros.avgRate

    def resFecCorrZerosACount(self,parameters):
        '''**RES:FECCORSYM:A:COUNt?** -
        Queries the FEC Correctable Zeros Errors(in Channel A) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanACorrectableZeros.count
    
    def resFecCorrZerosARate(self,parameters):
        '''**RES:FECCORSYM:A:RATe?** -
        Queries the FEC Correctable Zeros Errors(in Channel A) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanACorrectableZeros.currRate

    def resFecCorrZerosABAvg(self,parameters):
        '''**RES:FECCORZEROS:AB:AVE?** -
        Queries the FEC Correctable Zeros Errors(in Channel A & B) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanABCorrectableZeros.avgRate

    def resFecCorrZerosABCount(self,parameters):
        '''**RES:FECCORZEROS:AB:COUNt?** -
        Queries the FEC Correctable Zeros Errors(in Channel A & B) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanABCorrectableZeros.count
    
    def resFecCorrZerosABRate(self,parameters):
        '''**RES:FECCORZEROS:AB:RATe?** -
        Queries the FEC Correctable Zeros Errors(in Channel A & B) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanABCorrectableZeros.currRate

    def resFecCorrZerosBAvg(self,parameters):
        '''**RES:FECCORZEROS:B:AVE?** -
        Queries the FEC Correctable Zeros Errors(in Channel B) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanBCorrectableZeros.avgRate

    def resFecCorrZerosBCount(self,parameters):
        '''**RES:FECCORZEROS:B:COUNt?** -
        Queries the FEC Correctable Zeros Errors(in Channel B) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanBCorrectableZeros.count
    
    def resFecCorrZerosBRate(self,parameters):
        '''**RES:FECCORZEROS:B:RATe?** -
        Queries the FEC Correctable Zeros Errors(in Channel B) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanBCorrectableZeros.currRate

    def resFecLoaSecs(self,parameters):
        '''**RES:FECLOA:Secs?** -
        Queries the number of Forward Error Correction Loss Of Alignment alarm seconds.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecLoa.secs

    def resFecUncorrAvg(self,parameters):
        '''**RES:FECUNCOR:AVE?** -
        Queries the FEC Uncorrectable Errors average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecUncorrectable.avgRate

    def resFecUncorrCount(self,parameters):
        '''**RES:FECUNCOR:COUNt?** -
        Queries the FEC Uncorrectable Errors error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecUncorrectable.count
    
    def resFecUncorrRate(self,parameters):
        '''**RES:FECUNCOR:RATe?** -
        Queries the FEC Uncorrectable Errors current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecUncorrectable.currRate

    def resFecUncorrAAvg(self,parameters):
        '''**RES:FECUNCOR:A:AVE?** -
        Queries the FEC Uncorrectable Errors (in Channel A) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanAUncorrectable.avgRate

    def resFecUncorrACount(self,parameters):
        '''**RES:FECUNCOR:A:COUNt?** -
        Queries the FEC Uncorrectable Errors (in Channel A) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanAUncorrectable.count
    
    def resFecUncorrARate(self,parameters):
        '''**RES:FECUNCOR:A:RATe?** -
        Queries the FEC Uncorrectable Errors (in Channel A) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanAUncorrectable.currRate

    def resFecUncorrABAvg(self,parameters):
        '''**RES:FECUNCOR:AB:AVE?** -
        Queries the FEC Uncorrectable Errors (in Channel A & B) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanABUncorrectable.avgRate

    def resFecUncorrABCount(self,parameters):
        '''**RES:FECUNCOR:AB:COUNt?** -
        Queries the FEC Uncorrectable Errors (in Channel A & B) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanABUncorrectable.count
    
    def resFecUncorrABRate(self,parameters):
        '''**RES:FECUNCOR:AB:RATe?** -
        Queries the FEC Uncorrectable Errors (in Channel A & B) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanABUncorrectable.currRate

    def resFecUncorrBAvg(self,parameters):
        '''**RES:FECUNCOR:B:AVE?** -
        Queries the FEC Uncorrectable Errors (in Channel B) average error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanBUncorrectable.avgRate

    def resFecUncorrBCount(self,parameters):
        '''**RES:FECUNCOR:B:COUNt?** -
        Queries the FEC Uncorrectable Errors (in Channel B) error count.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.fecChanBUncorrectable.count
    
    def resFecUncorrBRate(self,parameters):
        '''**RES:FECUNCOR:B:RATe?** -
        Queries the FEC Uncorrectable Errors (in Channel B) current error rate.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.fecChanBUncorrectable.currRate

    def resFreqwideSecs(self,parameters):
        '''**RES:FREQWIDE:Secs?** -
        Queries the number of Frequency Wide alarm seconds, for all Physical lanes.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        if self.globals.veexPhy.stats.rxHostLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.stats.rxHostLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.rxFreqWide[lane].secs
        return response

    def resHiBerSecs(self,parameters):
        '''**RES:HIBER:Secs?** -
        Queries the number of High Block Error Rate alarm seconds.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.hiBer.secs

    def resHiSerSecs(self,parameters):
        '''**RES:HISER:Secs?** -
        Queries the number of High Symbol Error Ratio alarm seconds.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.hiSer.secs

    def resLoaSecs(self,parameters):
        '''**RES:LOA:Secs?** -
        Queries the number of Loss Of Alignment alarm seconds.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.loa.secs

    def resLoAlmSecs(self,parameters):
        '''**RES:LOALM:Secs?** -
        Queries the number of Loss Of Alignment Marker alarm seconds for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPcs.stats.alignMarkLoss[lane].secs
        return response

    def resFecLoampsSecs(self,parameters):
        '''**RES:LOAMPS:Secs?** -
        Queries the number of Forward Error Correction Loss of Alignment Marker Payload Sequence alarm seconds 
        for all FEC lane positions.
        '''
        # Double check -- How to know which vaiable should used here (fecAlignMarkLossLane or fecAlignMarkLoss)
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxFecLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPcs.stats.rxFecLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPcs.stats.fecAlignMarkLossLane[lane].secs
        return response

    def resLosSecs(self,parameters):
        '''**RES:LOS:Secs?** -
        Queries the number of Loss of Signal alarm seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        if self.globals.veexPhy.stats.rxNetLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.los[lane].secs
        return response

    def resModuleRxPowerHighAlarmSecs(self,parameters):
        '''**RES:MODULE:RXPWR:HIALARM:Secs?** -
        Queries the number of RX Power High Alarm seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        if self.globals.veexPhy.allowedSets.rxOpticalLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.allowedSets.rxOpticalLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.rxPowerHighAlarmThreshold[lane].secs
        return response
    
    def resModuleRxPowerHighWarningSecs(self,parameters):
        '''**RES:MODULE:RXPWR:HIWARN:Secs?** -
        Queries the number of RX Power High Warning seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        if self.globals.veexPhy.allowedSets.rxOpticalLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.allowedSets.rxOpticalLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.rxPowerHighWarningThreshold[lane].secs
        return response
    
    def resModuleRxPowerLowAlarmSecs(self,parameters):
        '''**RES:MODULE:RXPWR:LOALARM:Secs?** -
        Queries the number of RX Power Low Alarm seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        if self.globals.veexPhy.allowedSets.rxOpticalLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.allowedSets.rxOpticalLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.rxPowerLowAlarmThreshold[lane].secs
        return response
    
    def resModuleRxPowerLowWarningSecs(self,parameters):
        '''**RES:MODULE:RXPWR:LOWARN:Secs?** -
        Queries the number of RX Power Low Warning seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        if self.globals.veexPhy.allowedSets.rxOpticalLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.allowedSets.rxOpticalLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.rxPowerLowWarningThreshold[lane].secs
        return response

    def resModuleTempHighAlarmSecs(self,parameters):
        '''**RES:MODULE:TEMP:HIALARM:Secs?** -
        Queries the number of Temperature High Alarm seconds.
        '''
        self.globals.veexPhy.stats.update()
        return b"%d" % self.globals.veexPhy.stats.tempHighAlarmThreshold.secs
    
    def resModuleTempHighWarningSecs(self,parameters):
        '''**RES:MODULE:TEMP:HIWARN:Secs?** -
        Queries the number of Temperature High Warning seconds.
        '''
        self.globals.veexPhy.stats.update()
        return b"%d" % self.globals.veexPhy.stats.tempHighWarningThreshold.secs
    
    def resModuleTempLowAlarmSecs(self,parameters):
        '''**RES:MODULE:TEMP:LOALARM:Secs?** -
        Queries the number of Temperature low Alarm seconds.
        '''
        self.globals.veexPhy.stats.update()
        return b"%d" % self.globals.veexPhy.stats.tempLowAlarmThreshold.secs
    
    def resModuleTempLowWarningSecs(self,parameters):
        '''**RES:MODULE:TEMP:LOWARN:Secs?** -
        Queries the number of Temperature Low Warning seconds.
        '''
        self.globals.veexPhy.stats.update()
        return b"%d" % self.globals.veexPhy.stats.tempLowWarningThreshold.secs

    def resModuleTxBiasHighAlarmSecs(self,parameters):
        '''**RES:MODULE:TXBIAS:HIALARM:Secs?** -
        Queries the number of TX Bias High Alarm seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        if self.globals.veexPhy.allowedSets.txOpticalLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.txBiasHighAlarmThreshold[lane].secs
        return response
    
    def resModuleTxBiasHighWarningSecs(self,parameters):
        '''**RES:MODULE:TXBIAS:HIWARN:Secs?** -
        Queries the number of TX Bias High Warning seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        if self.globals.veexPhy.allowedSets.txOpticalLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.txBiasHighWarningThreshold[lane].secs
        return response
    
    def resModuleTxBiasLowAlarmSecs(self,parameters):
        '''**RES:MODULE:TXBIAS:LOALARM:Secs?** -
        Queries the number of TX Bias Low Alarm seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        if self.globals.veexPhy.allowedSets.txOpticalLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.txBiasLowAlarmThreshold[lane].secs
        return response
    
    def resModuleTxBiasLowWarningSecs(self,parameters):
        '''**RES:MODULE:TXBIAS:LOWARN:Secs?** -
        Queries the number of TX Bias Low Warning seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        if self.globals.veexPhy.allowedSets.txOpticalLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.txBiasLowWarningThreshold[lane].secs
        return response

    def resModuleTxPowerHighAlarmSecs(self,parameters):
        '''**RES:MODULE:TXPWR:HIALARM:Secs?** -
        Queries the number of TX Power High Alarm seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        if self.globals.veexPhy.allowedSets.txOpticalLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.txPowerHighAlarmThreshold[lane].secs
        return response
    
    def resModuleTxPowerHighWarningSecs(self,parameters):
        '''**RES:MODULE:TXPWR:HIWARN:Secs?** -
        Queries the number of TX Power High Warning seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        if self.globals.veexPhy.allowedSets.txOpticalLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.txPowerHighWarningThreshold[lane].secs
        return response
    
    def resModuleTxPowerLowAlarmSecs(self,parameters):
        '''**RES:MODULE:TXPWR:LOALARM:Secs?** -
        Queries the number of TX Power Low Alarm seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        if self.globals.veexPhy.allowedSets.txOpticalLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.txPowerLowAlarmThreshold[lane].secs
        return response
    
    def resModuleTxPowerLowWarningSecs(self,parameters):
        '''**RES:MODULE:TXPWR:LOWARN:Secs?** -
        Queries the number of TX Power Low Warning seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        if self.globals.veexPhy.allowedSets.txOpticalLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.allowedSets.txOpticalLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.txPowerLowWarningThreshold[lane].secs
        return response

    def resModuleVccHighAlarmSecs(self,parameters):
        '''**RES:MODULE:VCC:HIALARM:Secs?** -
        Queries the number of Voltage High Alarm seconds.
        '''
        self.globals.veexPhy.stats.update()
        return b"%d" % self.globals.veexPhy.stats.vccHighAlarmThreshold.secs
    
    def resModuleVccHighWarningSecs(self,parameters):
        '''**RES:MODULE:VCC:HIWARN:Secs?** -
        Queries the number of Voltage High Warning seconds.
        '''
        self.globals.veexPhy.stats.update()
        return b"%d" % self.globals.veexPhy.stats.vccHighWarningThreshold.secs
    
    def resModuleVccLowAlarmSecs(self,parameters):
        '''**RES:MODULE:VCC:LOALARM:Secs?** -
        Queries the number of Voltage low Alarm seconds.
        '''
        self.globals.veexPhy.stats.update()
        return b"%d" % self.globals.veexPhy.stats.vccLowAlarmThreshold.secs
    
    def resModuleVccLowWarningSecs(self,parameters):
        '''**RES:MODULE:VCC:LOWARN:Secs?** -
        Queries the number of Voltage Low Warning seconds.
        '''
        self.globals.veexPhy.stats.update()
        return b"%d" % self.globals.veexPhy.stats.vccLowWarningThreshold.secs

    def resPatSyncSecs(self,parameters):
        '''**RES:PATsync:Secs?** -
        Queries the number of Pattern Sync alarm seconds for all PCS lane positions.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPhy.allowedSets().update()
        response = b""
        if self.globals.veexPhy.allowedSets.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.allowedSets.rxVirtLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.patternSync[lane].secs
        return response

    def resPausedSecs(self,parameters):
        '''**RES:PAUSED:Secs?** -
        Queries the number of seconds the test was Paused.
        '''
        # Double check -- Phy or Pcs
        self.globals.veexPhy.stats.update()
        return b"%d" % self.globals.veexPhy.stats.testPaused.secs

    def resPwrHotSecs(self,parameters):
        '''**RES:PWRHOT:Secs?** -
        Queries the number of Power Hot alarm seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        if self.globals.veexPhy.stats.rxNetLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.rxPowerHot[lane].secs
        return response

    def resPwrLowSecs(self,parameters):
        '''**RES:PWRLOW:Secs?** -
        Queries the number of Power Low alarm seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        if self.globals.veexPhy.stats.rxNetLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.rxPowerLow[lane].secs
        return response

    def resPwrWarmSecs(self,parameters):
        '''**RES:PWRWARM:Secs?** -
        Queries the number of Power Warm alarm seconds for all Optical lanes.
        '''
        self.globals.veexPhy.stats.update()
        response = b""
        if self.globals.veexPhy.stats.rxNetLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPhy.stats.rxPowerWarm[lane].secs
        return response

    def resScanAlarms(self,parameters):
        '''**RES:SCANALARMS?** -
        Queries all ALARM results statistics and returns a list of any currently active or previously active alarms.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.testPaused.led.isRed:
            response += b"PAUSED 0 1 %d," % self.globals.veexPcs.stats.testPaused.secs
        elif self.globals.veexPcs.stats.testPaused.led.wasRed:
            response += b"PAUSED 0 0 %d," % self.globals.veexPcs.stats.testPaused.secs
        if self.globals.veexPcs.stats.clock.led.isRed:
            response += b"CLOCK 1 1 %d," % self.globals.veexPcs.stats.clock.secs
        elif self.globals.veexPcs.stats.clock.led.wasRed:
            response += b"CLOCK 1 0 %d," % self.globals.veexPcs.stats.clock.secs
        if self.globals.veexPcs.stats.loa.led.isRed:
            response += b"LOA 2 1 %d," % self.globals.veexPcs.stats.loa.secs
        elif self.globals.veexPcs.stats.loa.led.wasRed:
            response += b"LOA 2 0 %d," % self.globals.veexPcs.stats.loa.secs
        if self.globals.veexPcs.stats.fecLoa.led.isRed:
            response += b"FECLOA 3 1 %d," % self.globals.veexPcs.stats.fecLoa.secs
        elif self.globals.veexPcs.stats.fecLoa.led.wasRed:
            response += b"FECLOA 3 0 %d," % self.globals.veexPcs.stats.fecLoa.secs
        if self.globals.veexPcs.stats.hiBer.led.isRed:
            response += b"HIBER 4 1 %d," % self.globals.veexPcs.stats.hiBer.secs
        elif self.globals.veexPcs.stats.hiBer.led.wasRed:
            response += b"HIBER 4 0 %d," % self.globals.veexPcs.stats.hiBer.secs
        if self.globals.veexPcs.stats.hiSer.led.isRed:
            response += b"HISER 5 1 %d," % self.globals.veexPcs.stats.hiSer.secs
        elif self.globals.veexPcs.stats.hiSer.led.wasRed:
            response += b"HISER 5 0 %d," % self.globals.veexPcs.stats.hiSer.secs
        if self.globals.veexPhy.stats.tempHighAlarmThreshold.led.isRed:
            response += b"TEMPHIALARM 6 1 %d," % self.globals.veexPhy.stats.tempHighAlarmThreshold.secs
        elif self.globals.veexPhy.stats.tempHighAlarmThreshold.led.wasRed:
            response += b"TEMPHIALARM 6 0 %d," % self.globals.veexPhy.stats.tempHighAlarmThreshold.secs
        if self.globals.veexPhy.stats.tempLowAlarmThreshold.led.isRed:
            response += b"TEMPLOALARM 7 1 %d," % self.globals.veexPhy.stats.tempLowAlarmThreshold.secs
        elif self.globals.veexPhy.stats.tempLowAlarmThreshold.led.wasRed:
            response += b"TEMPLOALARM 7 0 %d," % self.globals.veexPhy.stats.tempLowAlarmThreshold.secs
        if self.globals.veexPhy.stats.tempHighWarningThreshold.led.isRed:
            response += b"TEMPHIWARN 8 1 %d," % self.globals.veexPhy.stats.tempHighWarningThreshold.secs
        elif self.globals.veexPhy.stats.tempHighWarningThreshold.led.wasRed:
            response += b"TEMPHIWARN 8 0 %d," % self.globals.veexPhy.stats.tempHighWarningThreshold.secs
        if self.globals.veexPhy.stats.tempLowWarningThreshold.led.isRed:
            response += b"TEMPLOWARN 9 1 %d," % self.globals.veexPhy.stats.tempLowWarningThreshold.secs
        elif self.globals.veexPhy.stats.tempLowWarningThreshold.led.wasRed:
            response += b"TEMPLOWARN 9 0 %d," % self.globals.veexPhy.stats.tempLowWarningThreshold.secs
        if self.globals.veexPhy.stats.vccHighAlarmThreshold.led.isRed:
            response += b"VCCHIALARM 10 1 %d," % self.globals.veexPhy.stats.vccHighAlarmThreshold.secs
        elif self.globals.veexPhy.stats.vccHighAlarmThreshold.led.wasRed:
            response += b"VCCHIALARM 10 0 %d," % self.globals.veexPhy.stats.vccHighAlarmThreshold.secs
        if self.globals.veexPhy.stats.vccLowAlarmThreshold.led.isRed:
            response += b"VCCLOALARM 11 1 %d," % self.globals.veexPhy.stats.vccLowAlarmThreshold.secs
        elif self.globals.veexPhy.stats.vccLowAlarmThreshold.led.wasRed:
            response += b"VCCLOALARM 11 0 %d," % self.globals.veexPhy.stats.vccLowAlarmThreshold.secs
        if self.globals.veexPhy.stats.vccHighWarningThreshold.led.isRed:
            response += b"VCCHIWARN 12 1 %d," % self.globals.veexPhy.stats.vccHighWarningThreshold.secs
        elif self.globals.veexPhy.stats.vccHighWarningThreshold.led.wasRed:
            response += b"VCCHIWARN 12 0 %d," % self.globals.veexPhy.stats.vccHighWarningThreshold.secs
        if self.globals.veexPhy.stats.vccLowWarningThreshold.led.isRed:
            response += b"VCCLOWARN 13 1 %d," % self.globals.veexPhy.stats.vccLowWarningThreshold.secs
        elif self.globals.veexPhy.stats.vccLowWarningThreshold.led.wasRed:
            response += b"VCCLOWARN 13 0 %d," % self.globals.veexPhy.stats.vccLowWarningThreshold.secs
        if self.globals.veexPcs.stats.remoteSerDegraded.led.isRed:
            response += b"REMDEGSER 14 1 %d," % self.globals.veexPcs.stats.remoteSerDegraded.secs
        elif self.globals.veexPcs.stats.remoteSerDegraded.led.wasRed:
            response += b"REMDEGSER 14 0 %d," % self.globals.veexPcs.stats.remoteSerDegraded.secs
        if self.globals.veexPcs.stats.localSerDegraded.led.isRed:
            response += b"LOCALDEGSER 15 1 %d," % self.globals.veexPcs.stats.localSerDegraded.secs
        elif self.globals.veexPcs.stats.localSerDegraded.led.wasRed:
            response += b"LOCALDEGSER 15 0 %d," % self.globals.veexPcs.stats.localSerDegraded.secs
        index = 16
        # los Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.los[lane].led.isRed:
                response += b"LOS-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.los[lane].secs)
            elif self.globals.veexPhy.stats.los[lane].led.wasRed:
                response += b"LOS-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.los[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # Power hot Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.rxPowerHot[lane].led.isRed:
                response += b"PWRHOT-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxPowerHot[lane].secs)
            elif self.globals.veexPhy.stats.rxPowerHot[lane].led.wasRed:
                response += b"PWRHOT-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxPowerHot[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # Power warm Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.rxPowerWarm[lane].led.isRed:
                response += b"PWRWARM-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxPowerWarm[lane].secs)
            elif self.globals.veexPhy.stats.rxPowerWarm[lane].led.wasRed:
                response += b"PWRWARM-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxPowerWarm[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # Power low Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.rxPowerLow[lane].led.isRed:
                response += b"PWRLOW-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxPowerLow[lane].secs)
            elif self.globals.veexPhy.stats.rxPowerLow[lane].led.wasRed:
                response += b"PWRLOW-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxPowerLow[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # Freq wide Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxHostLaneCount):
            if self.globals.veexPhy.stats.rxFreqWide[lane].led.isRed:
                response += b"FREQWIDE-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxFreqWide[lane].secs)
            elif self.globals.veexPhy.stats.rxFreqWide[lane].led.wasRed:
                response += b"FREQWIDE-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxFreqWide[lane].secs)
        index += self.globals.veexPhy.stats.rxHostLaneCount
        # alignMarkLoss Valid for current Interface
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if self.globals.veexPcs.stats.alignMarkLoss[lane].led.isRed:
                response += b"LOALM-%d %d 1 %d," % (lane, lane+index, self.globals.veexPcs.stats.alignMarkLoss[lane].secs)
            elif self.globals.veexPcs.stats.alignMarkLoss[lane].led.wasRed:
                response += b"LOALM-%d %d 0 %d," % (lane, lane+index, self.globals.veexPcs.stats.alignMarkLoss[lane].secs)
        index += self.globals.veexPcs.stats.rxVirtLaneCount
        # blockLockLoss Valid for current Interface
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if self.globals.veexPcs.stats.blockLockLoss[lane].led.isRed:
                response += b"BLKLOC-%d %d 1 %d," % (lane, lane+index, self.globals.veexPcs.stats.blockLockLoss[lane].secs)
            elif self.globals.veexPcs.stats.blockLockLoss[lane].led.wasRed:
                response += b"BLKLOC-%d %d 0 %d," % (lane, lane+index, self.globals.veexPcs.stats.blockLockLoss[lane].secs)
        index += self.globals.veexPcs.stats.rxVirtLaneCount
        # Double check here
        for lane in range(self.globals.veexPcs.stats.rxFecLaneCount):
            if self.globals.veexPcs.stats.fecAlignMarkLossLane[lane].led.isRed:
                response += b"LOAMPS-%d %d 1 %d," % (lane, lane+index, self.globals.veexPcs.stats.fecAlignMarkLossLane[lane].secs)
            elif self.globals.veexPcs.stats.fecAlignMarkLossLane[lane].led.wasRed:
                response += b"LOAMPS-%d %d 0 %d," % (lane, lane+index, self.globals.veexPcs.stats.fecAlignMarkLossLane[lane].secs)
        index += self.globals.veexPcs.stats.rxFecLaneCount
        # Double check - Not scan LOF, OOF, AIS, LOR, OOR alarm type
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if self.globals.veexPcs.stats.laneSkew[lane].led.isRed:
                response += b"SKEW-%d %d 1 %d," % (lane, lane+index, self.globals.veexPcs.stats.laneSkew[lane].secs)
            elif self.globals.veexPcs.stats.laneSkew[lane].led.wasRed:
                response += b"SKEW-%d %d 0 %d," % (lane, lane+index, self.globals.veexPcs.stats.laneSkew[lane].secs)
        index += self.globals.veexPcs.stats.rxVirtLaneCount
        # patternSync Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxVirtLaneCount):
            if self.globals.veexPhy.stats.patternSync[lane].led.isRed:
                response += b"PATsync-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.patternSync[lane].secs)
            elif self.globals.veexPhy.stats.patternSync[lane].led.wasRed:
                response += b"PATsync-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.patternSync[lane].secs)
        index += self.globals.veexPhy.stats.rxVirtLaneCount
        # txPowerHighAlarmThreshold Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.txPowerHighAlarmThreshold[lane].led.isRed:
                response += b"TXPWRHIALARM-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.txPowerHighAlarmThreshold[lane].secs)
            elif self.globals.veexPhy.stats.txPowerHighAlarmThreshold[lane].led.wasRed:
                response += b"TXPWRHIALARM-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.txPowerHighAlarmThreshold[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # txPowerLowAlarmThreshold Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.txPowerLowAlarmThreshold[lane].led.isRed:
                response += b"TXPWRLOALARM-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.txPowerLowAlarmThreshold[lane].secs)
            elif self.globals.veexPhy.stats.txPowerLowAlarmThreshold[lane].led.wasRed:
                response += b"TXPWRLOALARM-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.txPowerLowAlarmThreshold[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # txPowerHighWarningThreshold Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.txPowerHighWarningThreshold[lane].led.isRed:
                response += b"TXPWRHIWARN-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.txPowerHighWarningThreshold[lane].secs)
            elif self.globals.veexPhy.stats.txPowerHighWarningThreshold[lane].led.wasRed:
                response += b"TXPWRHIWARN-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.txPowerHighWarningThreshold[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # txPowerLowWarningThreshold Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.txPowerLowWarningThreshold[lane].led.isRed:
                response += b"TXPWRLOWARN-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.txPowerLowWarningThreshold[lane].secs)
            elif self.globals.veexPhy.stats.txPowerLowWarningThreshold[lane].led.wasRed:
                response += b"TXPWRLOWARN-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.txPowerLowWarningThreshold[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # rxPowerHighAlarmThreshold Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.rxPowerHighAlarmThreshold[lane].led.isRed:
                response += b"RXPWRHIALARM-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxPowerHighAlarmThreshold[lane].secs)
            elif self.globals.veexPhy.stats.rxPowerHighAlarmThreshold[lane].led.wasRed:
                response += b"RXPWRHIALARM-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxPowerHighAlarmThreshold[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # rxPowerLowAlarmThreshold Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.rxPowerLowAlarmThreshold[lane].led.isRed:
                response += b"RXPWRLOALARM-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxPowerLowAlarmThreshold[lane].secs)
            elif self.globals.veexPhy.stats.rxPowerLowAlarmThreshold[lane].led.wasRed:
                response += b"RXPWRLOALARM-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxPowerLowAlarmThreshold[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # rxPowerHighWarningThreshold Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.rxPowerHighWarningThreshold[lane].led.isRed:
                response += b"RXPWRHIWARN-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxPowerHighWarningThreshold[lane].secs)
            elif self.globals.veexPhy.stats.rxPowerHighWarningThreshold[lane].led.wasRed:
                response += b"RXPWRHIWARN-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxPowerHighWarningThreshold[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # rxPowerLowWarningThreshold Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.rxPowerLowWarningThreshold[lane].led.isRed:
                response += b"RXPWRLOWARN-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxPowerLowWarningThreshold[lane].secs)
            elif self.globals.veexPhy.stats.rxPowerLowWarningThreshold[lane].led.wasRed:
                response += b"RXPWRLOWARN-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.rxPowerLowWarningThreshold[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # txBiasHighAlarmThreshold Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.txBiasHighAlarmThreshold[lane].led.isRed:
                response += b"TXBIASHIALARM-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.txBiasHighAlarmThreshold[lane].secs)
            elif self.globals.veexPhy.stats.txBiasHighAlarmThreshold[lane].led.wasRed:
                response += b"TXBIASHIALARM-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.txBiasHighAlarmThreshold[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # txBiasLowAlarmThreshold Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.txBiasLowAlarmThreshold[lane].led.isRed:
                response += b"TXBIASLOALARM-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.txBiasLowAlarmThreshold[lane].secs)
            elif self.globals.veexPhy.stats.txBiasLowAlarmThreshold[lane].led.wasRed:
                response += b"TXBIASLOALARM-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.txBiasLowAlarmThreshold[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # txBiasHighWarningThreshold Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.txBiasHighWarningThreshold[lane].led.isRed:
                response += b"TXBIASHIWARN-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.txBiasHighWarningThreshold[lane].secs)
            elif self.globals.veexPhy.stats.txBiasHighWarningThreshold[lane].led.wasRed:
                response += b"TXBIASHIWARN-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.txBiasHighWarningThreshold[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount
        # txBiasLowWarningThreshold Valid for current Interface
        for lane in range(self.globals.veexPhy.stats.rxNetLaneCount):
            if self.globals.veexPhy.stats.txBiasLowWarningThreshold[lane].led.isRed:
                response += b"TXBIASLOWARN-%d %d 1 %d," % (lane, lane+index, self.globals.veexPhy.stats.txBiasLowWarningThreshold[lane].secs)
            elif self.globals.veexPhy.stats.txBiasLowWarningThreshold[lane].led.wasRed:
                response += b"TXBIASLOWARN-%d %d 0 %d," % (lane, lane+index, self.globals.veexPhy.stats.txBiasLowWarningThreshold[lane].secs)
        index += self.globals.veexPhy.stats.rxNetLaneCount 
        if len(response) == 0:
            response = b"+0"
        else:
            response.rstrip(',')
        return response

    def resScanErrors(self,parameters):
        '''**RES:SCANERRORS?** -
        Queries all ERROR results statistics and returns a list of any currently active or previously active errors.
        '''
        self.globals.veexPhy.stats.update()
        self.globals.veexPcs.stats.update()
        response = b""
        index = 0
        if self.globals.veexPcs.stats.block.led.isRed:
            response += b"BLOCK %d 1 %.2e," % (index,self.globals.veexPcs.stats.block.avgRate)
        elif self.globals.veexPcs.stats.block.led.wasRed:
            response += b"BLOCK %d 0 %.2e," % (index,self.globals.veexPcs.stats.block.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecCorrectable.led.isRed:
            response += b"FECCOR %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecCorrectable.avgRate)
        elif self.globals.veexPcs.stats.fecCorrectable.led.wasRed:
            response += b"FECCOR %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecCorrectable.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecCorrectableSymbol.led.isRed:
            response += b"FECCORSYM %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecCorrectableSymbol.avgRate)
        elif self.globals.veexPcs.stats.fecCorrectableSymbol.led.wasRed:
            response += b"FECCORSYM %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecCorrectableSymbol.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecCorrectableCw.led.isRed:
            response += b"FECCORCW %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecCorrectableCw.avgRate)
        elif self.globals.veexPcs.stats.fecCorrectableCw.led.wasRed:
            response += b"FECCORCW %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecCorrectableCw.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecUncorrectable.led.isRed:
            response += b"FECUNCOR %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecUncorrectable.avgRate)
        elif self.globals.veexPcs.stats.fecUncorrectable.led.wasRed:
            response += b"FECUNCOR %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecUncorrectable.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecTranscode.led.isRed:
            response += b"FECCODE %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecTranscode.avgRate)
        elif self.globals.veexPcs.stats.fecTranscode.led.wasRed:
            response += b"FECCODE %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecTranscode.avgRate)
        index += 1
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if self.globals.veexPcs.stats.syncHdr[lane].led.isRed:
                response += b"SYNCHDR-%d %d 1 %.2e," % (lane,lane+index,self.globals.veexPcs.stats.syncHdr[lane].avgRate)
            elif self.globals.veexPcs.stats.syncHdr[lane].led.wasRed:
                response += b"SYNCHDR-%d %d 0 %.2e," % (lane,lane+index,self.globals.veexPcs.stats.syncHdr[lane].avgRate)
        index += self.globals.veexPcs.stats.rxVirtLaneCount
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if self.globals.veexPcs.stats.alignMark[lane].led.isRed:
                response += b"ALMARK-%d %d 1 %.2e," % (lane,lane+index,self.globals.veexPcs.stats.alignMark[lane].avgRate)
            elif self.globals.veexPcs.stats.alignMark[lane].led.wasRed:
                response += b"ALMARK-%d %d 0 %.2e," % (lane,lane+index,self.globals.veexPcs.stats.alignMark[lane].avgRate)
        index += self.globals.veexPcs.stats.rxVirtLaneCount
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if self.globals.veexPcs.stats.bip8[lane].led.isRed:
                response += b"BIP8-%d %d 1 %.2e," % (lane,lane+index,self.globals.veexPcs.stats.bip8[lane].avgRate)
            elif self.globals.veexPcs.stats.bip8[lane].led.wasRed:
                response += b"BIP8-%d %d 0 %.2e," % (lane,lane+index,self.globals.veexPcs.stats.bip8[lane].avgRate)
        index += self.globals.veexPcs.stats.rxVirtLaneCount
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if self.globals.veexPcs.stats.bit[lane].led.isRed:
                response += b"BIT-%d %d 1 %.2e," % (lane,lane+index,self.globals.veexPcs.stats.bit[lane].avgRate)
            elif self.globals.veexPcs.stats.bit[lane].led.wasRed:
                response += b"BIT-%d %d 0 %.2e," % (lane,lane+index,self.globals.veexPcs.stats.bit[lane].avgRate)
        index += self.globals.veexPcs.stats.rxVirtLaneCount
        for lane in range(16):
            if self.globals.veexPcs.stats.fecCorrectableSymbolLane[lane].led.isRed:
                response += b"FECCORSYM-%d %d 1 %.2e," % (lane,lane+index,self.globals.veexPcs.stats.fecCorrectableSymbolLane[lane].avgRate)
            elif self.globals.veexPcs.stats.fecCorrectableSymbolLane[lane].led.wasRed:
                response += b"FECCORSYM-%d %d 0 %.2e," % (lane,lane+index,self.globals.veexPcs.stats.fecCorrectableSymbolLane[lane].avgRate)
        index += 16
        for lane in range(16):
            if self.globals.veexPcs.stats.fecCorrectableBitLane[lane].led.isRed:
                response += b"FECCORBIT-%d %d 1 %.2e," % (lane,lane+index,self.globals.veexPcs.stats.fecCorrectableBitLane[lane].avgRate)
            elif self.globals.veexPcs.stats.fecCorrectableBitLane[lane].led.wasRed:
                response += b"FECCORBIT-%d %d 0 %.2e," % (lane,lane+index,self.globals.veexPcs.stats.fecCorrectableBitLane[lane].avgRate)
        index += 16
        if self.globals.veexPcs.stats.fecChanACorrectableCw.led.isRed:
            response += b"FECCORCW %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanACorrectableCw.avgRate)
        elif self.globals.veexPcs.stats.fecChanACorrectableCw.led.wasRed:
            response += b"FECCORCW %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanACorrectableCw.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanACorrectableSymbol.led.isRed:
            response += b"FECCORSYMA %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanACorrectableSymbol.avgRate)
        elif self.globals.veexPcs.stats.fecChanACorrectableSymbol.led.wasRed:
            response += b"FECCORSYMA %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanACorrectableSymbol.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanACorrectableBit.led.isRed:
            response += b"FECCORBITA %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanACorrectableBit.avgRate)
        elif self.globals.veexPcs.stats.fecChanACorrectableBit.led.wasRed:
            response += b"FECCORBITA %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanACorrectableBit.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanACorrectableOnes.led.isRed:
            response += b"FECCORONEA %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanACorrectableOnes.avgRate)
        elif self.globals.veexPcs.stats.fecChanACorrectableOnes.led.wasRed:
            response += b"FECCORONEA %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanACorrectableOnes.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanACorrectableZeros.led.isRed:
            response += b"FECCORZEROA %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanACorrectableZeros.avgRate)
        elif self.globals.veexPcs.stats.fecChanACorrectableZeros.led.wasRed:
            response += b"FECCORZEROA %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanACorrectableZeros.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanAUncorrectable.led.isRed:
            response += b"FECUNCORA %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanAUncorrectable.avgRate)
        elif self.globals.veexPcs.stats.fecChanAUncorrectable.led.wasRed:
            response += b"FECUNCORA %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanAUncorrectable.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanBCorrectableCw.led.isRed:
            response += b"FECCORCWB %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanBCorrectableCw.avgRate)
        elif self.globals.veexPcs.stats.fecChanBCorrectableCw.led.wasRed:
            response += b"FECCORCWB %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanBCorrectableCw.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanBCorrectableSymbol.led.isRed:
            response += b"FECCORSYMB %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanBCorrectableSymbol.avgRate)
        elif self.globals.veexPcs.stats.fecChanBCorrectableSymbol.led.wasRed:
            response += b"FECCORSYMB %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanBCorrectableSymbol.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanBCorrectableBit.led.isRed:
            response += b"FECCORBITB %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanBCorrectableBit.avgRate)
        elif self.globals.veexPcs.stats.fecChanBCorrectableBit.led.wasRed:
            response += b"FECCORBITB %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanBCorrectableBit.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanBCorrectableOnes.led.isRed:
            response += b"FECCORONEB %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanBCorrectableOnes.avgRate)
        elif self.globals.veexPcs.stats.fecChanBCorrectableOnes.led.wasRed:
            response += b"FECCORONEB %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanBCorrectableOnes.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanBCorrectableZeros.led.isRed:
            response += b"FECCORZEROB %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanBCorrectableZeros.avgRate)
        elif self.globals.veexPcs.stats.fecChanBCorrectableZeros.led.wasRed:
            response += b"FECCORZEROB %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanBCorrectableZeros.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanBUncorrectable.led.isRed:
            response += b"FECUNCORB %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanBUncorrectable.avgRate)
        elif self.globals.veexPcs.stats.fecChanBUncorrectable.led.wasRed:
            response += b"FECUNCORB %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanBUncorrectable.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanABCorrectableCw.led.isRed:
            response += b"FECCORCWAB %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanABCorrectableCw.avgRate)
        elif self.globals.veexPcs.stats.fecChanABCorrectableCw.led.wasRed:
            response += b"FECCORCWAB %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanABCorrectableCw.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanABCorrectableSymbol.led.isRed:
            response += b"FECCORSYMAB %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanABCorrectableSymbol.avgRate)
        elif self.globals.veexPcs.stats.fecChanABCorrectableSymbol.led.wasRed:
            response += b"FECCORSYMAB %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanABCorrectableSymbol.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanABCorrectableBit.led.isRed:
            response += b"FECCORBITAB %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanABCorrectableBit.avgRate)
        elif self.globals.veexPcs.stats.fecChanABCorrectableBit.led.wasRed:
            response += b"FECCORBITAB %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanABCorrectableBit.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanABCorrectableOnes.led.isRed:
            response += b"FECCORONEAB %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanABCorrectableOnes.avgRate)
        elif self.globals.veexPcs.stats.fecChanABCorrectableOnes.led.wasRed:
            response += b"FECCORONEAB %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanABCorrectableOnes.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanABCorrectableZeros.led.isRed:
            response += b"FECCORZEROAB %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanABCorrectableZeros.avgRate)
        elif self.globals.veexPcs.stats.fecChanABCorrectableZeros.led.wasRed:
            response += b"FECCORZEROAB %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanABCorrectableZeros.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecChanABUncorrectable.led.isRed:
            response += b"FECUNCORAB %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecChanABUncorrectable.avgRate)
        elif self.globals.veexPcs.stats.fecChanABUncorrectable.led.wasRed:
            response += b"FECUNCORAB %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecChanABUncorrectable.avgRate)
        index += 1
        if self.globals.veexPcs.stats.fecAlignMarkPad.led.isRed:
            response += b"FECALMARKPAD %d 1 %.2e," % (index,self.globals.veexPcs.stats.fecAlignMarkPad.avgRate)
        elif self.globals.veexPcs.stats.fecAlignMarkPad.led.wasRed:
            response += b"FECALMARKPAD %d 0 %.2e," % (index,self.globals.veexPcs.stats.fecAlignMarkPad.avgRate)
        index += 1
        if len(response) == 0:
            response = b"+0"
        else:
            response.rstrip(',')
        return response

    def resSkewSecs(self,parameters):
        '''**RES:SKEW:Secs?** -
        Queries the number of Skew alarm seconds for all Logical/PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
            if len(response) != 0:
                response += b", "
            response += b"%d" % self.globals.veexPcs.stats.laneSkew[lane].secs
        return response

    def resSyncHdrAvg(self,parameters):
        '''**RES:SYNCHDR:AVE?** -
        Queries the average Synchronization Header error rate for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        else:
            for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%.2e" % self.globals.veexPcs.stats.syncHdr[lane].avgRate
        return response

    def resSyncHdrCount(self,parameters):
        '''**RES:SYNCHDR:COUNt?** -
        Queries the Synchronization Header error count for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        else:
            for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%d" % self.globals.veexPcs.stats.syncHdr[lane].count
        return response

    def resSyncHdrRate(self,parameters):
        '''**RES:SYNCHDR:RATe?** -
        Queries the current Synchronization Header error rate for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        response = b""
        if self.globals.veexPcs.stats.rxVirtLaneCount <= 0:
            response = b"No Lanes"
        else:
            for lane in range(self.globals.veexPcs.stats.rxVirtLaneCount):
                if len(response) != 0:
                    response += b", "
                response += b"%.2e" % self.globals.veexPcs.stats.syncHdr[lane].currRate
        return response

    def resAlignMarkTotalAvg(self,parameters):
        '''**RES:TOTALALMARK:AVE?** -
        Queries the combined total average Alignment Marker error rate for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.totalAlignMark.avgRate

    def resAlignMarkTotalCount(self,parameters):
        '''**RES:TOTALALMARK:COUNt?** -
        Queries the combined total Alignment Marker error count for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.totalAlignMark.count
    
    def resAlignMarkTotalRate(self,parameters):
        '''**RES:TOTALALMARK:RATe?** -
        Queries the combined total current Alignment Marker error rate for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.totalAlignMark.currRate

    def resBip8TotalAvg(self,parameters):
        '''**RES:TOTALBIP8:AVE?** -
        Queries the combined total average BIP-8 error rate for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.totalBip8.avgRate

    def resBip8TotalCount(self,parameters):
        '''**RES:TOTALBIP8:COUNt?** -
        Queries the combined total BIP-8 error count for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.totalBip8.count
    
    def resBip8TotalRate(self,parameters):
        '''**RES:TOTALBIP8:RATe?** -
        Queries the combined total current BIP-8 error rate for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.totalBip8.currRate

    def resBitTotalAvg(self,parameters):
        '''**RES:TOTALBIT:AVE?** -
        Queries the combined total average BIT error rate for all PCS lane positions.
        '''
        self.globals.veexPhy.stats.update()
        return b"%.2e" % self.globals.veexPhy.stats.totalBit.avgRate

    def resBitTotalCount(self,parameters):
        '''**RES:TOTALBIT:COUNt?** -
        Queries the combined total BIT error count for all PCS lane positions.
        '''
        self.globals.veexPhy.stats.update()
        return b"%d" % self.globals.veexPhy.stats.totalBit.count
    
    def resBitTotalRate(self,parameters):
        '''**RES:TOTALBIT:RATe?** -
        Queries the combined total current BIT error rate for all PCS lane positions.
        '''
        self.globals.veexPhy.stats.update()
        return b"%.2e" % self.globals.veexPhy.stats.totalBit.currRate

    def resSyncHdrTotalAvg(self,parameters):
        '''**RES:TOTALSYNCHDR:AVE?** -
        Queries the combined total average Synchronization Header error rate for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.totalSyncHdr.avgRate

    def resSyncHdrTotalCount(self,parameters):
        '''**RES:TOTALSYNCHDR:COUNt?** -
        Queries the combined total Synchronization Header error count for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        return b"%d" % self.globals.veexPcs.stats.totalSyncHdr.count
    
    def resSyncHdrTotalRate(self,parameters):
        '''**RES:TOTALSYNCHDR:RATe?** -
        Queries the combined total current Synchronization Header error rate for all PCS lane positions.
        '''
        self.globals.veexPcs.stats.update()
        return b"%.2e" % self.globals.veexPcs.stats.totalSyncHdr.currRate


# This table contains all the system SCPI commands. Note that queries must
# come before the matching setting commands. Also if two commands start with
# the same text then the longer one must come first.
commandTable = [
    Cmnd(b"TX:ALarm:OPTicaltype?",     ScpiMld.getTxAlarmOptType),
    Cmnd(b"TX:ALarm:OPTicaltype",      ScpiMld.setTxAlarmOptType),
    Cmnd(b"TX:ALarm:TYPE?",            ScpiMld.getTxAlarmVirType),
    Cmnd(b"TX:ALarm:TYPE",             ScpiMld.setTxAlarmVirType),
    Cmnd(b"TX:COUPled?",               ScpiMld.getTxCoupled),
    Cmnd(b"TX:COUPled",                ScpiMld.setTxCoupled),
    Cmnd(b"TX:CLOCK?",                 ScpiMld.getTxClock),
    Cmnd(b"TX:CLOCK",                  ScpiMld.setTxClock),
    Cmnd(b"TX:ERRor:BURSTPERIOD?",     ScpiMld.getTxErrBurst),
    Cmnd(b"TX:ERRor:BURSTPERIOD",      ScpiMld.setTxErrBurst),
    Cmnd(b"TX:ERRor:BURSTSIZE?",       ScpiMld.getTxErrBurstSize),
    Cmnd(b"TX:ERRor:BURSTSIZE",        ScpiMld.setTxErrBurstSize),
    Cmnd(b"TX:ERRor:RATE?",            ScpiMld.getTxErrRate),
    Cmnd(b"TX:ERRor:RATE",             ScpiMld.setTxErrRate),    
    Cmnd(b"TX:ERRor:TYPE?",            ScpiMld.getTxErrType),
    Cmnd(b"TX:ERRor:TYPE",             ScpiMld.setTxErrType),    
    Cmnd(b"TX:EYECLOCK?",              ScpiMld.getEyeClockSource),
    Cmnd(b"TX:EYECLOCK",               ScpiMld.setEyeClockSource),   
    Cmnd(b"TX:FREQuency?",             ScpiMld.getTxFreq),
    Cmnd(b"TX:FREQOFFset:PPM?",        ScpiMld.getTxFreqOffsetPpm),
    Cmnd(b"TX:FREQOFFset:HZ?",         ScpiMld.getTxFreqOffsetHz),
    Cmnd(b"TX:FREQOFFset:LINE?",       ScpiMld.getTxFreqOffLine),
    Cmnd(b"TX:FREQOFFset:LINE",        ScpiMld.setTxFreqOffLine),
    Cmnd(b"TX:INTerface?",             ScpiMld.getTxRxInterface),
    Cmnd(b"TX:INTerface",              ScpiMld.setTxRxInterface),
    Cmnd(b"TX:LANE:COUNT:LOGical?",    ScpiMld.getTxLaneCountLog),
    Cmnd(b"TX:LANE:COUNT:OPTical?",    ScpiMld.getTxLaneCountOptical),
    Cmnd(b"TX:LANE:COUNT:PCS?",        ScpiMld.getTxLaneCountPcs),
    Cmnd(b"TX:LANE:COUNT:PHYsical?",   ScpiMld.getTxLaneCountHost),
    Cmnd(b"TX:LANE:MAP?",              ScpiMld.getTxLaneMap),
    Cmnd(b"TX:LANE:MAP",               ScpiMld.setTxLaneMap),
    Cmnd(b"TX:LANE:SKEW?",             ScpiMld.getTxLaneSkew),
    Cmnd(b"TX:LANE:SKEW",              ScpiMld.setTxLaneSkew),
    Cmnd(b"TX:LASER?",                 ScpiMld.getTxLaser),
    Cmnd(b"TX:LASER",                  ScpiMld.setTxLaser),
    Cmnd(b"TX:LASERPUP?",              ScpiMld.getTxLaserPwrUp),
    Cmnd(b"TX:LASERPUP",               ScpiMld.setTxLaserPwrUp),
    Cmnd(b"TX:OUTTHRESHold?",          ScpiMld.getTxOutThresh),
    Cmnd(b"TX:OUTTHRESHold",           ScpiMld.setTxOutThresh),
    Cmnd(b"TX:PATTern?",               ScpiMld.getTxPattern),
    Cmnd(b"TX:PATTern",                ScpiMld.setTxPattern),
    Cmnd(b"TX:POSTEMPH?",              ScpiMld.getTxPostEmph),
    Cmnd(b"TX:POSTEMPH",               ScpiMld.setTxPostEmph),
    Cmnd(b"TX:PREEMPH?",               ScpiMld.getTxPreEmph),
    Cmnd(b"TX:PREEMPH",                ScpiMld.setTxPreEmph),
    Cmnd(b"TX:SWING?",                 ScpiMld.getTxSwing),
    Cmnd(b"TX:SWING",                  ScpiMld.setTxSwing),

    Cmnd(b"RX:COUPled?",               ScpiMld.getTxCoupled),
    Cmnd(b"RX:COUPled",                ScpiMld.setTxCoupled),
    Cmnd(b"RX:FREQuency?",             ScpiMld.getRxFreq),
    Cmnd(b"RX:FREQOFFset:PPM?",        ScpiMld.getRxFreqOffsetPpm),
    Cmnd(b"RX:FREQOFFset:HZ?",         ScpiMld.getRxFreqOffsetHz),
    Cmnd(b"RX:HISERALARM?",            ScpiMld.getDisableHiSer),
    Cmnd(b"RX:HISERALARM",             ScpiMld.setDisableHiSer),
    Cmnd(b"RX:HISERPERIOD?",           ScpiMld.getHiSerPeriod),
    Cmnd(b"RX:HISERPERIOD",            ScpiMld.setHiSerPeriod),
    Cmnd(b"RX:INTerface?",             ScpiMld.getTxRxInterface),
    Cmnd(b"RX:INTerface",              ScpiMld.setTxRxInterface),
    Cmnd(b"RX:LANE:COUNT:OPT?",        ScpiMld.getRxLaneCountOptical),
    Cmnd(b"RX:LANE:COUNT:PHY?",        ScpiMld.getRxLaneCountHost),
    Cmnd(b"RX:LANE:COUNT:LOG?",        ScpiMld.getRxLaneCountOtl),
    Cmnd(b"RX:LANE:COUNT:PCS?",        ScpiMld.getRxLaneCountPcs),
    Cmnd(b"RX:LANE:MAP?",              ScpiMld.getRxLaneMap),
    Cmnd(b"RX:LANE:SKEW:BITS?",        ScpiMld.getRxLaneSkewBits),
    Cmnd(b"RX:LANE:SKEW:PS?",          ScpiMld.getRxLaneSkewPs),
    Cmnd(b"RX:MAXFREQOFFset:Hz?",      ScpiMld.getRxFreqOffsetHzMax),
    Cmnd(b"RX:MAXFREQOFFset:PPM?",     ScpiMld.getRxFreqOffsetPpmMax),
    Cmnd(b"RX:MAXFREQuency?",          ScpiMld.getRxFreqMax),
    Cmnd(b"RX:MAXOPPBB?",              ScpiMld.getRxOppBBMax),
    Cmnd(b"RX:MINFREQOFFset:Hz?",      ScpiMld.getRxFreqOffsetHzMin),
    Cmnd(b"RX:MINFREQOFFset:PPM?",     ScpiMld.getRxFreqOffsetPpmMin),
    Cmnd(b"RX:MINFREQuency?",          ScpiMld.getRxFreqMin),
    Cmnd(b"RX:MINOPPBB?",              ScpiMld.getRxOppBBMin),
    Cmnd(b"RX:OPPBB?",                 ScpiMld.getRxOppBB),
    Cmnd(b"RX:OPPLANE?",               ScpiMld.getModuleDataRxPower),
    Cmnd(b"RX:OUTTHRESHold?",          ScpiMld.getRxOutThreshhold),
    Cmnd(b"RX:OUTTHRESHold",           ScpiMld.setRxOutThreshhold),
    Cmnd(b"RX:PATTern?",               ScpiMld.getRxPattern),
    Cmnd(b"RX:PATTern",                ScpiMld.setRxPattern),
    Cmnd(b"RX:PWRLOWT?",               ScpiMld.getRxPowLowThreshhold),
    Cmnd(b"RX:PWRLOWT",                ScpiMld.setRxPowLowThreshhold),
    Cmnd(b"RX:SERACTTHRESHold?",       ScpiMld.getSerDegradedActivate),
    Cmnd(b"RX:SERACTTHRESHold",        ScpiMld.setSerDegradedActivate),
    Cmnd(b"RX:SERDEACTTHRESHold?",     ScpiMld.getSerDegradedDeactivate),
    Cmnd(b"RX:SERDEACTTHRESHold",      ScpiMld.setSerDegradedDeactivate),
    Cmnd(b"RX:SERDEGINTER?",           ScpiMld.getSerDegradedInterval),
    Cmnd(b"RX:SERDEGINTER",            ScpiMld.setSerDegradedInterval),
    Cmnd(b"RX:SKEWTHRESHold?",         ScpiMld.getRxSkewThreshhold),
    Cmnd(b"RX:SKEWTHRESHold",          ScpiMld.setRxSkewThreshhold),
    
    Cmnd(b"RES:AIS:Secs?",             ScpiMld.resAisSecs),
    #Cmnd(b"RES:AL:AIS?",               ScpiMld.resAlarmAisState),
    Cmnd(b"RES:AL:ALMARK?",            ScpiMld.resAlarmAlignMarkState),
    Cmnd(b"RES:AL:BIP8?",              ScpiMld.resAlarmBip8State),
    Cmnd(b"RES:AL:BIT?",               ScpiMld.resAlarmBitState),
    Cmnd(b"RES:AL:BLKLOC?",            ScpiMld.resAlarmBlockLockState),
    Cmnd(b"RES:AL:BLOCK?",             ScpiMld.resAlarmBlockState),
    Cmnd(b"RES:AL:CLOCK?",             ScpiMld.resAlarmClockState),
    Cmnd(b"RES:AL:FECALMARKPAD?",      ScpiMld.resAlarmFecAlignMarkPadState),
    Cmnd(b"RES:AL:FECCODE?",           ScpiMld.resAlarmFecTranscodeState),
    Cmnd(b"RES:AL:FECCORBIT?",         ScpiMld.resAlarmFecCorrState),
    Cmnd(b"RES:AL:FECCORBIT:A?",       ScpiMld.resAlarmFecCorrBitAState),
    Cmnd(b"RES:AL:FECCORBIT:AB?",      ScpiMld.resAlarmFecCorrBitABState),
    Cmnd(b"RES:AL:FECCORBIT:B?",       ScpiMld.resAlarmFecCorrBitBState),
    Cmnd(b"RES:AL:FECCORBITLANE?",     ScpiMld.resAlarmFecCorrBitLaneState),
    Cmnd(b"RES:AL:FECCORCW?",          ScpiMld.resAlarmFecCorrCwState),
    Cmnd(b"RES:AL:FECCORCW:A?",        ScpiMld.resAlarmFecCorrCwAState),
    Cmnd(b"RES:AL:FECCORCW:AB?",       ScpiMld.resAlarmFecCorrCwABState),
    Cmnd(b"RES:AL:FECCORCW:B?",        ScpiMld.resAlarmFecCorrCwBState),
    Cmnd(b"RES:AL:FECCORONES:A?",      ScpiMld.resAlarmFecCorrOnesAState),
    Cmnd(b"RES:AL:FECCORONES:AB?",     ScpiMld.resAlarmFecCorrOnesABState),
    Cmnd(b"RES:AL:FECCORONES:B?",      ScpiMld.resAlarmFecCorrOnesBState),
    Cmnd(b"RES:AL:FECCORSYM?",         ScpiMld.resAlarmFecCorrSymbolState),
    Cmnd(b"RES:AL:FECCORSYM:A?",       ScpiMld.resAlarmFecCorrSymAState),
    Cmnd(b"RES:AL:FECCORSYM:AB?",      ScpiMld.resAlarmFecCorrSymABState),
    Cmnd(b"RES:AL:FECCORSYM:B?",       ScpiMld.resAlarmFecCorrSymBState),
    Cmnd(b"RES:AL:FECCORSYMLANE?",     ScpiMld.resAlarmFecCorrSymbolLaneState),
    Cmnd(b"RES:AL:FECCORZEROS:A?",     ScpiMld.resAlarmFecCorrZerosAState),
    Cmnd(b"RES:AL:FECCORZEROS:AB?",    ScpiMld.resAlarmFecCorrZerosABState),
    Cmnd(b"RES:AL:FECCORZEROS:B?",     ScpiMld.resAlarmFecCorrZerosBState),
    Cmnd(b"RES:AL:FECLOA?",            ScpiMld.resAlarmFecLoaState),
    Cmnd(b"RES:AL:FECUNCOR?",          ScpiMld.resAlarmFecUncorrState),
    Cmnd(b"RES:AL:FECUNCOR:A?",        ScpiMld.resAlarmFecUnCorrAState),
    Cmnd(b"RES:AL:FECUNCOR:AB?",       ScpiMld.resAlarmFecUnCorrABState),
    Cmnd(b"RES:AL:FECUNCOR:B?",        ScpiMld.resAlarmFecUnCorrBState),
    Cmnd(b"RES:AL:FREQWIDE?",          ScpiMld.resAlarmFreqWideState),
    Cmnd(b"RES:AL:HIBER?",             ScpiMld.resAlarmHiBerState),
    Cmnd(b"RES:AL:HISER?",             ScpiMld.resAlarmHiSerState),
    Cmnd(b"RES:AL:LANESUM?",           ScpiMld.resAlarmLaneSummaryState),
    Cmnd(b"RES:AL:LOA?",               ScpiMld.resAlarmLoaState),
    Cmnd(b"RES:AL:LOALM?",             ScpiMld.resAlarmLoAlmState),
    Cmnd(b"RES:AL:LOAMPS?",            ScpiMld.resAlarmFecLoampsState),
    #Cmnd(b"RES:AL:LOF?",               ScpiMld.resAlarmLofState),
    #Cmnd(b"RES:AL:LOR?",               ScpiMld.resAlarmLorState),
    Cmnd(b"RES:AL:LOS?",               ScpiMld.resAlarmLosState),
    Cmnd(b"RES:AL:MODULESTATUS?",      ScpiMld.resAlarmSummaryModuleState),
    #Cmnd(b"RES:AL:OOF?",               ScpiMld.resAlarmOofState),
    #Cmnd(b"RES:AL:OOR?",               ScpiMld.resAlarmOorState),
    Cmnd(b"RES:AL:PAT?",               ScpiMld.resAlarmPatSyncState),
    Cmnd(b"RES:AL:PAUSED?",            ScpiMld.resAlarmPausedState),
    Cmnd(b"RES:AL:RXPWRHIALARM?",      ScpiMld.resAlarmRxPowerHighAlarmThresholdState),
    Cmnd(b"RES:AL:RXPWRHIWARN?",       ScpiMld.resAlarmRxPowerHighWarningThresholdState),
    Cmnd(b"RES:AL:RXPWRLOALARM?",      ScpiMld.resAlarmRxPowerLowAlarmThresholdState),
    Cmnd(b"RES:AL:RXPWRLOWARN?",       ScpiMld.resAlarmRxPowerLowWarningThresholdState),
    Cmnd(b"RES:AL:SKEW?",              ScpiMld.resAlarmSkewState),
    Cmnd(b"RES:AL:SUMMary?",           ScpiMld.resAlarmSummaryState),
    Cmnd(b"RES:AL:SYNCHDR?",           ScpiMld.resAlarmSyncHdrState),
    Cmnd(b"RES:AL:TEMPHIALARM?",       ScpiMld.resAlarmTempHighAlarmThresholdState),
    Cmnd(b"RES:AL:TEMPHIWARN?",        ScpiMld.resAlarmTempHighWarningThresholdState),
    Cmnd(b"RES:AL:TEMPLOALARM?",       ScpiMld.resAlarmTempLowAlarmThresholdState),
    Cmnd(b"RES:AL:TEMPLOWARN?",        ScpiMld.resAlarmTempLowWarningThresholdState),
    Cmnd(b"RES:AL:TXBIASHIALARM?",     ScpiMld.resAlarmTxBiasHighAlarmThresholdState),
    Cmnd(b"RES:AL:TXBIASHIWARN?",      ScpiMld.resAlarmTxBiasHighWarningThresholdState),
    Cmnd(b"RES:AL:TXBIASLOALARM?",     ScpiMld.resAlarmTxBiasLowAlarmThresholdState),
    Cmnd(b"RES:AL:TXBIASLOWARN?",      ScpiMld.resAlarmTxBiasLowWarningThresholdState),
    Cmnd(b"RES:AL:TXPWRHIALARM?",      ScpiMld.resAlarmTxPowerHighAlarmThresholdState),
    Cmnd(b"RES:AL:TXPWRHIWARN?",       ScpiMld.resAlarmTxPowerHighWarningThresholdState),
    Cmnd(b"RES:AL:TXPWRLOALARM?",      ScpiMld.resAlarmTxPowerLowAlarmThresholdState),
    Cmnd(b"RES:AL:TXPWRLOWARN?",       ScpiMld.resAlarmTxPowerLowWarningThresholdState),
    Cmnd(b"RES:AL:VCCHIALARM?",        ScpiMld.resAlarmVccHighAlarmThresholdState),
    Cmnd(b"RES:AL:VCCHIWARN?",         ScpiMld.resAlarmVccHighWarningThresholdState),
    Cmnd(b"RES:AL:VCCLOALARM?",        ScpiMld.resAlarmVccLowAlarmThresholdState),
    Cmnd(b"RES:AL:VCCLOWARN?",         ScpiMld.resAlarmVccLowWarningThresholdState),
    Cmnd(b"RES:ALMARK:AVErage?",       ScpiMld.resAlignMarkAvg),
    Cmnd(b"RES:ALMARK:COUNt?",         ScpiMld.resAlignMarkCount),
    Cmnd(b"RES:ALMARK:RATe?",          ScpiMld.resAlignMarkRate),
    Cmnd(b"RES:BIP8:AVErage?",         ScpiMld.resBip8Avg),
    Cmnd(b"RES:BIP8:COUNt?",           ScpiMld.resBip8Count),
    Cmnd(b"RES:BIP8:RATe?",            ScpiMld.resBip8Rate),
    Cmnd(b"RES:BIT:AVErage?",          ScpiMld.resBitAvg),
    Cmnd(b"RES:BIT:COUNt?",            ScpiMld.resBitCount),
    Cmnd(b"RES:BIT:RATe?",             ScpiMld.resBitRate),
    Cmnd(b"RES:BLKLOC:Secs?",          ScpiMld.resBlockLockSecs),
    Cmnd(b"RES:CLOCK:Secs?",           ScpiMld.resClockSecs),
    Cmnd(b"RES:CPPOWERLOSS:Secs?",     ScpiMld.resPowerSecs),
    Cmnd(b"RES:DEGSER:Secs?",          ScpiMld.resDegSerSecs),
    
    Cmnd(b"RES:EVENTLOG?",             ScpiMld.getEventLog),
    Cmnd(b"RES:FECALMARKPAD:AVE?",     ScpiMld.resFecAlignMarkPadAvg),
    Cmnd(b"RES:FECALMARKPAD:COUNt?",   ScpiMld.resFecAlignMarkPadCount),
    Cmnd(b"RES:FECALMARKPAD:RATe?",    ScpiMld.resFecAlignMarkPadRate),
    Cmnd(b"RES:FECANALYSIS:COUNt?",    ScpiMld.resFecCorSymCountCount),
    Cmnd(b"RES:FECANALYSIS:PERCENT?",  ScpiMld.resFecCorSymCountPct),
    Cmnd(b"RES:FECCODE:AVE?",          ScpiMld.resFecTranscodeAvg),
    Cmnd(b"RES:FECCODE:COUNt?",        ScpiMld.resFecTranscodeCount),
    Cmnd(b"RES:FECCODE:RATe?",         ScpiMld.resFecTranscodeRate),
    Cmnd(b"RES:FECCORBITLANE:AVE?",    ScpiMld.resFecCorrBitLaneAvg),
    Cmnd(b"RES:FECCORBITLANE:COUNt?",  ScpiMld.resFecCorrBitLaneCount),
    Cmnd(b"RES:FECCORBITLANE:RATe?",   ScpiMld.resFecCorrBitLaneRate),
    Cmnd(b"RES:FECCORBIT:AVE?",        ScpiMld.resFecCorrBitLaneAvg),
    Cmnd(b"RES:FECCORBIT:COUNt?",      ScpiMld.resFecCorrBitLaneCount),
    Cmnd(b"RES:FECCORBIT:RATe?",       ScpiMld.resFecCorrBitLaneRate),
    Cmnd(b"RES:FECCORBIT:A:AVE?",      ScpiMld.resFecCorrBitAAvg),
    Cmnd(b"RES:FECCORBIT:A:COUNt?",    ScpiMld.resFecCorrBitACount),
    Cmnd(b"RES:FECCORBIT:A:RATe?",     ScpiMld.resFecCorrBitARate),
    Cmnd(b"RES:FECCORBIT:AB:AVE?",     ScpiMld.resFecCorrBitABAvg),
    Cmnd(b"RES:FECCORBIT:AB:COUNt?",   ScpiMld.resFecCorrBitABCount),
    Cmnd(b"RES:FECCORBIT:AB:RATe?",    ScpiMld.resFecCorrBitABRate),
    Cmnd(b"RES:FECCORBIT:B:AVE?",      ScpiMld.resFecCorrBitBAvg),
    Cmnd(b"RES:FECCORBIT:B:COUNt?",    ScpiMld.resFecCorrBitBCount),
    Cmnd(b"RES:FECCORBIT:B:RATe?",     ScpiMld.resFecCorrBitBRate),
    Cmnd(b"RES:FECCORCW:A:AVE?",       ScpiMld.resFecCorrCwAAvg),
    Cmnd(b"RES:FECCORCW:A:COUNt?",     ScpiMld.resFecCorrCwACount),
    Cmnd(b"RES:FECCORCW:A:RATe?",      ScpiMld.resFecCorrCwARate),
    Cmnd(b"RES:FECCORCW:AB:AVE?",      ScpiMld.resFecCorrCwABAvg),
    Cmnd(b"RES:FECCORCW:AB:COUNt?",    ScpiMld.resFecCorrCwABCount),
    Cmnd(b"RES:FECCORCW:AB:RATe?",     ScpiMld.resFecCorrCwABRate),
    Cmnd(b"RES:FECCORCW:B:AVE?",       ScpiMld.resFecCorrCwBAvg),
    Cmnd(b"RES:FECCORCW:B:COUNt?",     ScpiMld.resFecCorrCwBCount),
    Cmnd(b"RES:FECCORCW:B:RATe?",      ScpiMld.resFecCorrCwBRate),
    Cmnd(b"RES:FECCORONES:A:AVE?",     ScpiMld.resFecCorrOnesAAvg),
    Cmnd(b"RES:FECCORONES:A:COUNt?",   ScpiMld.resFecCorrOnesACount),
    Cmnd(b"RES:FECCORONES:A:RATe?",    ScpiMld.resFecCorrOnesARate),
    Cmnd(b"RES:FECCORONES:AB:AVE?",    ScpiMld.resFecCorrOnesABAvg),
    Cmnd(b"RES:FECCORONES:AB:COUNt?",  ScpiMld.resFecCorrOnesABCount),
    Cmnd(b"RES:FECCORONES:AB:RATe?",   ScpiMld.resFecCorrOnesABRate),
    Cmnd(b"RES:FECCORONES:B:AVE?",     ScpiMld.resFecCorrOnesBAvg),
    Cmnd(b"RES:FECCORONES:B:COUNt?",   ScpiMld.resFecCorrOnesBCount),
    Cmnd(b"RES:FECCORONES:B:RATe?",    ScpiMld.resFecCorrOnesBRate),
    Cmnd(b"RES:FECCORR:AVE?",          ScpiMld.resFecCorrAvg),
    Cmnd(b"RES:FECCORR:COUNt?",        ScpiMld.resFecCorrCount),
    Cmnd(b"RES:FECCORR:RATe?",         ScpiMld.resFecCorrRate),
    Cmnd(b"RES:FECCORSYM:AVE?",        ScpiMld.resFecCorrSymbolAvg),
    Cmnd(b"RES:FECCORSYM:COUNt?",      ScpiMld.resFecCorrSymbolCount),
    Cmnd(b"RES:FECCORSYM:RATe?",       ScpiMld.resFecCorrSymbolRate),
    Cmnd(b"RES:FECCORSYM:A:AVE?",      ScpiMld.resFecCorrSymbolAAvg),
    Cmnd(b"RES:FECCORSYM:A:COUNt?",    ScpiMld.resFecCorrSymbolACount),
    Cmnd(b"RES:FECCORSYM:A:RATe?",     ScpiMld.resFecCorrSymbolARate),
    Cmnd(b"RES:FECCORSYM:AB:AVE?",     ScpiMld.resFecCorrSymbolABAvg),
    Cmnd(b"RES:FECCORSYM:AB:COUNt?",   ScpiMld.resFecCorrSymbolABCount),
    Cmnd(b"RES:FECCORSYM:AB:RATe?",    ScpiMld.resFecCorrSymbolABRate),
    Cmnd(b"RES:FECCORSYM:B:AVE?",      ScpiMld.resFecCorrSymbolBAvg),
    Cmnd(b"RES:FECCORSYM:B:COUNt?",    ScpiMld.resFecCorrSymbolBCount),
    Cmnd(b"RES:FECCORSYM:B:RATe?",     ScpiMld.resFecCorrSymbolBRate),
    Cmnd(b"RES:FECCORSYMLANE:AVE?",    ScpiMld.resFecCorrSymbolLaneAvg),
    Cmnd(b"RES:FECCORSYMLANE:COUNt?",  ScpiMld.resFecCorrSymbolLaneCount),
    Cmnd(b"RES:FECCORSYMLANE:RATe?",   ScpiMld.resFecCorrSymbolLaneRate),
    Cmnd(b"RES:FECCORZEROS:A:AVE?",    ScpiMld.resFecCorrZerosAAvg),
    Cmnd(b"RES:FECCORZEROS:A:COUNt?",  ScpiMld.resFecCorrZerosACount),
    Cmnd(b"RES:FECCORZEROS:A:RATe?",   ScpiMld.resFecCorrZerosARate),
    Cmnd(b"RES:FECCORZEROS:AB:AVE?",   ScpiMld.resFecCorrZerosABAvg),
    Cmnd(b"RES:FECCORZEROS:AB:COUNt?", ScpiMld.resFecCorrZerosABCount),
    Cmnd(b"RES:FECCORZEROS:AB:RATe?",  ScpiMld.resFecCorrZerosABRate),
    Cmnd(b"RES:FECCORZEROS:B:AVE?",    ScpiMld.resFecCorrZerosBAvg),
    Cmnd(b"RES:FECCORZEROS:B:COUNt?",  ScpiMld.resFecCorrZerosBCount),
    Cmnd(b"RES:FECCORZEROS:B:RATe?",   ScpiMld.resFecCorrZerosBRate),
    Cmnd(b"RES:FECLOA:Secs?",          ScpiMld.resFecLoaSecs),
    Cmnd(b"RES:FECUNCOR:AVE?",         ScpiMld.resFecUncorrAvg),
    Cmnd(b"RES:FECUNCOR:COUNt?",       ScpiMld.resFecUncorrCount),
    Cmnd(b"RES:FECUNCOR:RATe?",        ScpiMld.resFecUncorrRate),
    Cmnd(b"RES:FECUNCOR:A:AVE?",       ScpiMld.resFecUncorrAAvg),
    Cmnd(b"RES:FECUNCOR:A:COUNt?",     ScpiMld.resFecUncorrACount),
    Cmnd(b"RES:FECUNCOR:A:RATe?",      ScpiMld.resFecUncorrARate),
    Cmnd(b"RES:FECUNCOR:AB:AVE?",      ScpiMld.resFecUncorrABAvg),
    Cmnd(b"RES:FECUNCOR:AB:COUNt?",    ScpiMld.resFecUncorrABCount),
    Cmnd(b"RES:FECUNCOR:AB:RATe?",     ScpiMld.resFecUncorrABRate),
    Cmnd(b"RES:FECUNCOR:B:AVE?",       ScpiMld.resFecUncorrBAvg),
    Cmnd(b"RES:FECUNCOR:B:COUNt?",     ScpiMld.resFecUncorrBCount),
    Cmnd(b"RES:FECUNCOR:B:RATe?",      ScpiMld.resFecUncorrBRate),
    Cmnd(b"RES:FREQWIDE:Secs?",        ScpiMld.resFreqwideSecs),
    Cmnd(b"RES:HIBER:Secs?",           ScpiMld.resHiBerSecs),
    Cmnd(b"RES:HISER:Secs?",           ScpiMld.resHiSerSecs),
    Cmnd(b"RES:LOA:Secs?",             ScpiMld.resLoaSecs),
    Cmnd(b"RES:LOALM:Secs?",           ScpiMld.resLoAlmSecs),
    Cmnd(b"RES:LOAMPS:Secs?",          ScpiMld.resFecLoampsSecs),
    #Cmnd(b"RES:LOF:Secs?",             ScpiMld.resLofSecs),
    #Cmnd(b"RES:LOR:Secs?",             ScpiMld.resLorSecs),
    Cmnd(b"RES:LOS:Secs?",             ScpiMld.resLosSecs),
    Cmnd(b"RES:MODULE:RXPWR:HIALARM:Secs?",    ScpiMld.resModuleRxPowerHighAlarmSecs),
    Cmnd(b"RES:MODULE:RXPWR:HIWARN:Secs?",     ScpiMld.resModuleRxPowerHighWarningSecs),
    Cmnd(b"RES:MODULE:RXPWR:LOALARM:Secs?",    ScpiMld.resModuleRxPowerLowAlarmSecs),
    Cmnd(b"RES:MODULE:RXPWR:LOWARN:Secs?",     ScpiMld.resModuleRxPowerLowWarningSecs),
    Cmnd(b"RES:MODULE:TEMP:HIALARM:Secs?",     ScpiMld.resModuleTempHighAlarmSecs),
    Cmnd(b"RES:MODULE:TEMP:HIWARN:Secs?",      ScpiMld.resModuleTempHighWarningSecs),
    Cmnd(b"RES:MODULE:TEMP:LOALARM:Secs?",     ScpiMld.resModuleTempLowAlarmSecs),
    Cmnd(b"RES:MODULE:TEMP:LOWARN:Secs?",      ScpiMld.resModuleTempLowWarningSecs),
    Cmnd(b"RES:MODULE:TXBIAS:HIALARM:Secs?",   ScpiMld.resModuleTxBiasHighAlarmSecs),
    Cmnd(b"RES:MODULE:TXBIAS:HIWARN:Secs?",    ScpiMld.resModuleTxBiasHighWarningSecs),
    Cmnd(b"RES:MODULE:TXBIAS:LOALARM:Secs?",   ScpiMld.resModuleTxBiasLowAlarmSecs),
    Cmnd(b"RES:MODULE:TXBIAS:LOWARN:Secs?",    ScpiMld.resModuleTxBiasLowWarningSecs),
    Cmnd(b"RES:MODULE:TXPWR:HIALARM:Secs?",    ScpiMld.resModuleTxPowerHighAlarmSecs),
    Cmnd(b"RES:MODULE:TXPWR:HIWARN:Secs?",     ScpiMld.resModuleTxPowerHighWarningSecs),
    Cmnd(b"RES:MODULE:TXPWR:LOALARM:Secs?",    ScpiMld.resModuleTxPowerLowAlarmSecs),
    Cmnd(b"RES:MODULE:TXPWR:LOWARN:Secs?",     ScpiMld.resModuleTxPowerLowWarningSecs),
    Cmnd(b"RES:MODULE:VCC:HIALARM:Secs?",      ScpiMld.resModuleVccHighAlarmSecs),
    Cmnd(b"RES:MODULE:VCC:HIWARN:Secs?",       ScpiMld.resModuleVccHighWarningSecs),
    Cmnd(b"RES:MODULE:VCC:LOALARM:Secs?",      ScpiMld.resModuleVccLowAlarmSecs),
    Cmnd(b"RES::MODULE:VCC:LOWARN:Secs?",      ScpiMld.resModuleVccLowWarningSecs),
    #Cmnd(b"RES:OOF:Secs?",              ScpiMld.resOofSecs),
    #Cmnd(b"RES:OOR:Secs?",              ScpiMld.resOorSecs),
    Cmnd(b"RES:PATsync:Secs?",          ScpiMld.resPatSyncSecs),
    Cmnd(b"RES:PAUSED:Secs?",           ScpiMld.resPausedSecs),
    Cmnd(b"RES:PWRHOT:Secs?",           ScpiMld.resPwrHotSecs),
    Cmnd(b"RES:PWRLOW:Secs?",           ScpiMld.resPwrLowSecs),
    Cmnd(b"RES:PWRWARM:Secs?",          ScpiMld.resPwrWarmSecs),
    Cmnd(b"RES:SCANALARMS?",            ScpiMld.resScanAlarms),
    Cmnd(b"RES:SCANERRORS?",            ScpiMld.resScanErrors),
    Cmnd(b"RES:SKEW:Secs?",             ScpiMld.resSkewSecs),
    Cmnd(b"RES:SYNCHDR:AVE?",           ScpiMld.resSyncHdrAvg),
    Cmnd(b"RES:SYNCHDR:COUNt?",         ScpiMld.resSyncHdrCount),
    Cmnd(b"RES:SYNCHDR:RATe?",          ScpiMld.resSyncHdrRate),
    Cmnd(b"RES:TOTALALMARK:AVE?",       ScpiMld.resAlignMarkTotalAvg),
    Cmnd(b"RES:TOTALALMARK:COUNt?",     ScpiMld.resAlignMarkTotalCount),
    Cmnd(b"RES:TOTALALMARK:RATe?",      ScpiMld.resAlignMarkTotalRate),
    Cmnd(b"RES:TOTALBIP8:AVE?",         ScpiMld.resBip8TotalAvg),
    Cmnd(b"RES:TOTALBIP8:COUNt?",       ScpiMld.resBip8TotalCount),
    Cmnd(b"RES:TOTALBIP8:RATe?",        ScpiMld.resBip8TotalRate),
    Cmnd(b"RES:TOTALBIT:AVE?",          ScpiMld.resBitTotalAvg),
    Cmnd(b"RES:TOTALBIT:COUNt?",        ScpiMld.resBitTotalCount),
    Cmnd(b"RES:TOTALBIT:RATe?",         ScpiMld.resBitTotalRate),
    Cmnd(b"RES:TOTALSYNCHDR:AVE?",      ScpiMld.resSyncHdrTotalAvg),
    Cmnd(b"RES:TOTALSYNCHDR:COUNt?",    ScpiMld.resSyncHdrTotalCount),
    Cmnd(b"RES:TOTALSYNCHDR:RATe?",     ScpiMld.resSyncHdrTotalRate),
    ]



# This converts the above table into a tree of lists that can be searched
# for commands. Doing this here and not in the class init means it is done
# once at boot and not at the start of each user session.
commandTreeRoot = []
ParseUtils.processCommandTableIntoTree(commandTable, commandTreeRoot)


if __name__ == "__main__":
    pass

