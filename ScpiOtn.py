###############################################################################
#
# Copyright 2018-2019, VeEX, Inc.
# All Rights Reserved.
#
# $Workfile:   ScpiOtn.py  $
# $Revision: 25602 $
# $Author: patrickellis $
# $Date: 2021-12-30 01:33:41 -0500 (Thu, 30 Dec 2021) $
#
# DESCRIPTION:
#    Module to process OTN SCPI commands.
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
#from pip._vendor.urllib3 import response
#from builtins import True, False
#from ctypes.test.test_array_in_pointer import Value
#from Clients.PythonAPI import veexlib
#from pip._internal import self_outdated_check
#from Clients.PySCPI import ParseUtils
#from http.client import responses
#from test.test_pickle import mapping


class ScpiOtn(object):
    #'''This class processes text OTN SCPI commands and returns a text response.
    #
    #Args:
    #    globals (SessionGlobals object): Data class of session variables.
    #'''

    # Dictionary to convert between ProtoBuf enum and SPCI text for TX/RX interface.
    InterfaceTable = {
        veexlib.OTN_INTERFACE_OFF                 : b"NOT_ASSIGNED",
        veexlib.OTN_INTERFACE_2P5G_OTU_1          : b"G709_25G",
        veexlib.OTN_INTERFACE_10G_OTU_2           : b"G709_10G",
        veexlib.OTN_INTERFACE_43G_OTU_3           : b"G709_43G_QSFP",
        veexlib.OTN_INTERFACE_10G_ETHERNET        : b"10_3125G_LAN",
        veexlib.OTN_INTERFACE_11G_OTU_2E          : b"G709_11_095G_LAN",
        veexlib.OTN_INTERFACE_11G_OTU_1E          : b"G709_11_049G_LAN",
        veexlib.OTN_INTERFACE_1G_ETHERNET         : b"1_25G_LAN",
        veexlib.OTN_INTERFACE_44G_OTU_3E1         : b"G709_44_571G_QSFP",
        veexlib.OTN_INTERFACE_8G_FIBRECHAN        : b"8_5G_FIBRECHAN",
        veexlib.OTN_INTERFACE_10G_FIBRECHAN       : b"10_52G_FIBRECHAN",
        veexlib.OTN_INTERFACE_11G_OTU_2F          : b"G709_11_317G_FIBRECHAN",
        veexlib.OTN_INTERFACE_11G_OTU_1F          : b"G709_11_270G_FIBRECHAN",
        veexlib.OTN_INTERFACE_112G_OTU_4_CFP4     : b"G709_112G_CFP",
        veexlib.OTN_INTERFACE_44G_OTU_3E2         : b"G709_44_583G_QSFP",
        veexlib.OTN_INTERFACE_100M_ETHERNET       : b"125M_LAN",
        veexlib.OTN_INTERFACE_10M_ETHERNET        : b"12_5M_LAN",
        veexlib.OTN_INTERFACE_1000T_ETHERNET      : b"1_25G_BASE_T",
        veexlib.OTN_INTERFACE_100T_ETHERNET       : b"125M_BASE_T",
        veexlib.OTN_INTERFACE_10T_ETHERNET        : b"12_5M_BASE_T",
        veexlib.OTN_INTERFACE_4G_FIBRECHAN        : b"4_25G_FIBRECHAN",
        veexlib.OTN_INTERFACE_2G_FIBRECHAN        : b"2_125G_FIBRECHAN",
        veexlib.OTN_INTERFACE_1G_FIBRECHAN        : b"1_0625G_FIBRECHAN",
        veexlib.OTN_INTERFACE_112G_OTU_4_QSFP28   : b"G709_112G_QSFP",
        veexlib.OTN_INTERFACE_2P5G_ETHERNET       : b"3_125G_LAN",
        veexlib.OTN_INTERFACE_2500T_ETHERNET      : b"2_578125G_BASE_T",
        veexlib.OTN_INTERFACE_5000T_ETHERNET      : b"5_15625G_BASE_T",
        veexlib.OTN_INTERFACE_10000T_ETHERNET     : b"10_3125G_BASE_T",
        veexlib.OTN_INTERFACE_614M_CPRI_1         : b"614M_CPRI",
        veexlib.OTN_INTERFACE_1P2G_CPRI_2         : b"1_229G_CPRI",
        veexlib.OTN_INTERFACE_2P5G_CPRI_3         : b"2_458G_CPRI",
        veexlib.OTN_INTERFACE_3G_CPRI_4           : b"3_072G_CPRI",
        veexlib.OTN_INTERFACE_5G_CPRI_5           : b"4_915G_CPRI",
        veexlib.OTN_INTERFACE_6G_CPRI_6           : b"6_144G_CPRI",
        veexlib.OTN_INTERFACE_8G_CPRI_7A          : b"8_11G_CPRI",
        veexlib.OTN_INTERFACE_9G_CPRI_7           : b"9_83G_CPRI",
        veexlib.OTN_INTERFACE_10G_CPRI_8          : b"10_138G_CPRI",
        veexlib.OTN_INTERFACE_12G_CPRI_9          : b"12_165G_CPRI",
        veexlib.OTN_INTERFACE_24G_CPRI_10         : b"24_33G_CPRI",
        veexlib.OTN_INTERFACE_112G_OTU_CN         : b"G709_112G_OTUCN_QSFP",
        veexlib.OTN_INTERFACE_112G_OTU_CN_QSFP56  : b"G709_112G_OTUCN_QSFP56",
        veexlib.OTN_INTERFACE_112G_OTU_4_QSFP56   : b"G709_112G_QSFP56",
        veexlib.OTN_INTERFACE_112G_OTU_4_QSFP_DD28: b"G709_112G_QSFPDD",
        veexlib.OTN_INTERFACE_112G_OTU_4_CFP28    : b"G709_112G_CFP",
        }

    # Dictionary to convert between ProtoBuf enum and SPCI text for OTN Alarm type.
    OtnAlarmTypeTable = {
        veexlib.OTN_ALARM_OFF                   : b"OFF",
        veexlib.OTN_ALARM_CP_POWER_LOSS         : b"POWER",
        veexlib.OTN_ALARM_TEST_PAUSED           : b"PAUSED",  
        veexlib.OTN_ALARM_RX_FREQ_WIDE          : b"FREQWIDE", 
        veexlib.OTN_ALARM_RX_POWER_HOT          : b"RXPWRHOT",   
        veexlib.OTN_ALARM_RX_POWER_LOW          : b"RXPWRLOW", 
        veexlib.OTN_ALARM_CLOCK                 : b"CLOCK", 
        veexlib.OTN_ALARM_LOS                   : b"LOS",
        veexlib.OTN_ALARM_LOF                   : b"LOF",
        veexlib.OTN_ALARM_OOF                   : b"OOF",
        veexlib.OTN_ALARM_LOM                   : b"LOM",
        veexlib.OTN_ALARM_OOM                   : b"OOM",
        veexlib.OTN_ALARM_OTU_AIS               : b"OTUAIS",
        veexlib.OTN_ALARM_OTU_IAE               : b"OTUIAE",
        veexlib.OTN_ALARM_OTU_BDI               : b"OTUBDI",
        veexlib.OTN_ALARM_OTU_SAPI_TIM          : b"OTUSAPITIM",
        veexlib.OTN_ALARM_OTU_DAPI_TIM          : b"OTUDAPITIM",
        veexlib.OTN_ALARM_ODU_AIS               : b"ODUAIS",
        veexlib.OTN_ALARM_ODU_LCK               : b"ODULCK",
        veexlib.OTN_ALARM_ODU_OCI               : b"ODUOCI",
        veexlib.OTN_ALARM_ODU_BDI               : b"ODUBDI",
        veexlib.OTN_ALARM_ODU_SAPI_TIM          : b"ODUSAPITIM",
        veexlib.OTN_ALARM_ODU_DAPI_TIM          : b"ODUDAPITIM",
        veexlib.OTN_ALARM_TCM_1_BDI             : b"TCM1BDI",
        veexlib.OTN_ALARM_TCM_2_BDI             : b"TCM2BDI",
        veexlib.OTN_ALARM_TCM_3_BDI             : b"TCM3BDI",
        veexlib.OTN_ALARM_TCM_4_BDI             : b"TCM4BDI",
        veexlib.OTN_ALARM_TCM_5_BDI             : b"TCM5BDI",
        veexlib.OTN_ALARM_TCM_6_BDI             : b"TCM6BDI",
        veexlib.OTN_ALARM_TCM_1_SAPI_TIM        : b"TCM1SAPITIM",
        veexlib.OTN_ALARM_TCM_2_SAPI_TIM        : b"TCM2SAPITIM",
        veexlib.OTN_ALARM_TCM_3_SAPI_TIM        : b"TCM3SAPITIM",
        veexlib.OTN_ALARM_TCM_4_SAPI_TIM        : b"TCM4SAPITIM",
        veexlib.OTN_ALARM_TCM_5_SAPI_TIM        : b"TCM5SAPITIM",
        veexlib.OTN_ALARM_TCM_6_SAPI_TIM        : b"TCM6SAPITIM",
        veexlib.OTN_ALARM_TCM_1_DAPI_TIM        : b"TCM1DAPITIM",
        veexlib.OTN_ALARM_TCM_2_DAPI_TIM        : b"TCM2DAPITIM",
        veexlib.OTN_ALARM_TCM_3_DAPI_TIM        : b"TCM3DAPITIM",
        veexlib.OTN_ALARM_TCM_4_DAPI_TIM        : b"TCM4DAPITIM",
        veexlib.OTN_ALARM_TCM_5_DAPI_TIM        : b"TCM5DAPITIM",
        veexlib.OTN_ALARM_TCM_6_DAPI_TIM        : b"TCM6DAPITIM",
        veexlib.OTN_ALARM_PATTERN_SYNC          : b"PATTSYNC",
#        veexlib.OTN_ALARM_RX_POWER_WARM        : b"RXPWRWARM",
        veexlib.OTN_ALARM_OPU_PLM               : b"OPUPLM",
        veexlib.OTN_ALARM_ODTU_ODU_AIS          : b"MUXODUAIS",
        veexlib.OTN_ALARM_ODTU_ODU_LCK          : b"MUXODULCK",
        veexlib.OTN_ALARM_ODTU_ODU_OCI          : b"MUXODUOCI",
        veexlib.OTN_ALARM_ODTU_ODU_BDI          : b"MUXODUBDI",
        veexlib.OTN_ALARM_ODTU_ODU_SAPI_TIM     : b"MUXODUSAPITIM",
        veexlib.OTN_ALARM_ODTU_ODU_DAPI_TIM     : b"MUXODUDAPITIM",
        veexlib.OTN_ALARM_ODTU_TCM_1_BDI        : b"MUXTCM1BDI",
        veexlib.OTN_ALARM_ODTU_TCM_2_BDI        : b"MUXTCM2BDI",
        veexlib.OTN_ALARM_ODTU_TCM_3_BDI        : b"MUXTCM3BDI",
        veexlib.OTN_ALARM_ODTU_TCM_4_BDI        : b"MUXTCM4BDI",
        veexlib.OTN_ALARM_ODTU_TCM_5_BDI        : b"MUXTCM5BDI",
        veexlib.OTN_ALARM_ODTU_TCM_6_BDI        : b"MUXTCM6BDI",
        veexlib.OTN_ALARM_ODTU_TCM_1_SAPI_TIM   : b"MUXTCM1SAPITIM",
        veexlib.OTN_ALARM_ODTU_TCM_2_SAPI_TIM   : b"MUXTCM2SAPITIM",
        veexlib.OTN_ALARM_ODTU_TCM_3_SAPI_TIM   : b"MUXTCM3SAPITIM",
        veexlib.OTN_ALARM_ODTU_TCM_4_SAPI_TIM   : b"MUXTCM4SAPITIM",
        veexlib.OTN_ALARM_ODTU_TCM_5_SAPI_TIM   : b"MUXTCM5SAPITIM",
        veexlib.OTN_ALARM_ODTU_TCM_6_SAPI_TIM   : b"MUXTCM6SAPITIM",
        veexlib.OTN_ALARM_ODTU_TCM_1_DAPI_TIM   : b"MUXTCM1DAPITIM",
        veexlib.OTN_ALARM_ODTU_TCM_2_DAPI_TIM   : b"MUXTCM2DAPITIM",
        veexlib.OTN_ALARM_ODTU_TCM_3_DAPI_TIM   : b"MUXTCM3DAPITIM",
        veexlib.OTN_ALARM_ODTU_TCM_4_DAPI_TIM   : b"MUXTCM4DAPITIM",
        veexlib.OTN_ALARM_ODTU_TCM_5_DAPI_TIM   : b"MUXTCM5DAPITIM",
        veexlib.OTN_ALARM_ODTU_TCM_6_DAPI_TIM   : b"MUXTCM6DAPITIM",
        veexlib.OTN_ALARM_ODTU_OPU_PLM          : b"MUXOPUPLM",
        veexlib.OTN_ALARM_ODTU_LOF              : b"MUXLOF",
        veexlib.OTN_ALARM_ODTU_OOF              : b"MUXOOF",
        veexlib.OTN_ALARM_ODTU_LOM              : b"MUXLOM",
        veexlib.OTN_ALARM_ODTU_OOM              : b"MUXOOM",
        veexlib.OTN_ALARM_OTU_BIAE              : b"OTUBIAE",
        veexlib.OTN_ALARM_TCM_1_BIAE            : b"TCM1BIAE",
        veexlib.OTN_ALARM_TCM_2_BIAE            : b"TCM2BIAE",
        veexlib.OTN_ALARM_TCM_3_BIAE            : b"TCM3BIAE",
        veexlib.OTN_ALARM_TCM_4_BIAE            : b"TCM4BIAE",
        veexlib.OTN_ALARM_TCM_5_BIAE            : b"TCM5BIAE",
        veexlib.OTN_ALARM_TCM_6_BIAE            : b"TCM6BIAE",
        veexlib.OTN_ALARM_ODTU_TCM_1_BIAE       : b"MUXTCM1BIAE",
        veexlib.OTN_ALARM_ODTU_TCM_2_BIAE       : b"MUXTCM2BIAE",
        veexlib.OTN_ALARM_ODTU_TCM_3_BIAE       : b"MUXTCM3BIAE",
        veexlib.OTN_ALARM_ODTU_TCM_4_BIAE       : b"MUXTCM4BIAE",
        veexlib.OTN_ALARM_ODTU_TCM_5_BIAE       : b"MUXTCM5BIAE",
        veexlib.OTN_ALARM_ODTU_TCM_6_BIAE       : b"MUXTCM6BIAE",
        veexlib.OTN_ALARM_OPU_C8_SYNC           : b"OPUCMSYNC",
#        veexlib.OTN_ALARM_ODU_SD_FW            : b"",
#        veexlib.OTN_ALARM_ODU_SF_FW            : b"",
#        veexlib.OTN_ALARM_ODU_SD_BW            : b"",
#        veexlib.OTN_ALARM_ODU_SF_BW            : b"",
        veexlib.OTN_ALARM_OPU_FREQ_WIDE         : b"OPUFREQWIDE",
        veexlib.OTN_ALARM_ODTU_OPU_FREQ_WIDE    : b"MUXOPUFREQWIDE",
        veexlib.OTN_ALARM_OPU_AIS               : b"OPUAIS",
        veexlib.OTN_ALARM_OPU_CSF               : b"OPUCSF",
        veexlib.OTN_ALARM_ODTU_OPU_CSF          : b"MUXOPUCSF",
        veexlib.OTN_ALARM_LOOMFI                : b"LOOMFI",
        veexlib.OTN_ALARM_OOOMFI                : b"OOOMFI",
        veexlib.OTN_ALARM_FEC_STRESS            : b"FECSTRESS",            
        veexlib.OTN_ALARM_ODTU_0_OPU_FREQ_WIDE  : b"MUX0_OPUFREQWIDE", 
        veexlib.OTN_ALARM_ODTU_0_LOF            : b"MUX0_LOF",
        veexlib.OTN_ALARM_ODTU_0_OOF            : b"MUX0_OOF",
        veexlib.OTN_ALARM_ODTU_0_LOM            : b"MUX0_LOM",
        veexlib.OTN_ALARM_ODTU_0_OOM            : b"MUX0_OOM",
        veexlib.OTN_ALARM_ODTU_0_ODU_AIS        : b"MUX0_ODUAIS",
        veexlib.OTN_ALARM_ODTU_0_ODU_LCK        : b"MUX0_ODULCK",
        veexlib.OTN_ALARM_ODTU_0_ODU_OCI        : b"MUX0_ODUOCI",
        veexlib.OTN_ALARM_ODTU_0_ODU_BDI        : b"MUX0_ODUBDI",
        veexlib.OTN_ALARM_ODTU_0_ODU_SAPI_TIM   : b"MUX0_ODUSAPITIM",
        veexlib.OTN_ALARM_ODTU_0_ODU_DAPI_TIM   : b"MUX0_ODUDAPITIM",
        veexlib.OTN_ALARM_ODTU_0_OPU_C8_SYNC    : b"MUX0_OPUCMSYNC",
        veexlib.OTN_ALARM_ODTU_0_OPU_PLM        : b"MUX0_OPUPLM",
        veexlib.OTN_ALARM_ODTU_0_OPU_CSF        : b"MUX0_OPUCSF",
        veexlib.OTN_ALARM_ODTU_0_TCM_1_BDI      : b"MUX0_TCM1BDI",
        veexlib.OTN_ALARM_ODTU_0_TCM_2_BDI      : b"MUX0_TCM2BDI",
        veexlib.OTN_ALARM_ODTU_0_TCM_3_BDI      : b"MUX0_TCM3BDI",
        veexlib.OTN_ALARM_ODTU_0_TCM_4_BDI      : b"MUX0_TCM4BDI",
        veexlib.OTN_ALARM_ODTU_0_TCM_5_BDI      : b"MUX0_TCM5BDI",
        veexlib.OTN_ALARM_ODTU_0_TCM_6_BDI      : b"MUX0_TCM6BDI",
        veexlib.OTN_ALARM_ODTU_0_TCM_1_BIAE     : b"MUX0_TCM1BIAE",
        veexlib.OTN_ALARM_ODTU_0_TCM_2_BIAE     : b"MUX0_TCM2BIAE",
        veexlib.OTN_ALARM_ODTU_0_TCM_3_BIAE     : b"MUX0_TCM3BIAE",
        veexlib.OTN_ALARM_ODTU_0_TCM_4_BIAE     : b"MUX0_TCM4BIAE",
        veexlib.OTN_ALARM_ODTU_0_TCM_5_BIAE     : b"MUX0_TCM5BIAE",
        veexlib.OTN_ALARM_ODTU_0_TCM_6_BIAE     : b"MUX0_TCM6BIAE",
        veexlib.OTN_ALARM_ODTU_0_TCM_1_SAPI_TIM : b"MUX0_TCM1SAPITIM",
        veexlib.OTN_ALARM_ODTU_0_TCM_2_SAPI_TIM : b"MUX0_TCM2SAPITIM",
        veexlib.OTN_ALARM_ODTU_0_TCM_3_SAPI_TIM : b"MUX0_TCM3SAPITIM",
        veexlib.OTN_ALARM_ODTU_0_TCM_4_SAPI_TIM : b"MUX0_TCM4SAPITIM",
        veexlib.OTN_ALARM_ODTU_0_TCM_5_SAPI_TIM : b"MUX0_TCM5SAPITIM",
        veexlib.OTN_ALARM_ODTU_0_TCM_6_SAPI_TIM : b"MUX0_TCM6SAPITIM",
        veexlib.OTN_ALARM_ODTU_0_TCM_1_DAPI_TIM : b"MUX0_TCM1DAPITIM",
        veexlib.OTN_ALARM_ODTU_0_TCM_2_DAPI_TIM : b"MUX0_TCM2DAPITIM",
        veexlib.OTN_ALARM_ODTU_0_TCM_3_DAPI_TIM : b"MUX0_TCM3DAPITIM",
        veexlib.OTN_ALARM_ODTU_0_TCM_4_DAPI_TIM : b"MUX0_TCM4DAPITIM",
        veexlib.OTN_ALARM_ODTU_0_TCM_5_DAPI_TIM : b"MUX0_TCM5DAPITIM",
        veexlib.OTN_ALARM_ODTU_0_TCM_6_DAPI_TIM : b"MUX0_TCM6DAPITIM",    
        veexlib.OTN_ALARM_ODTU_1_OPU_FREQ_WIDE  : b"MUX1_OPUFREQWIDE",   
        veexlib.OTN_ALARM_ODTU_1_LOF            : b"MUX1_LOF",
        veexlib.OTN_ALARM_ODTU_1_OOF            : b"MUX1_OOF",
        veexlib.OTN_ALARM_ODTU_1_LOM            : b"MUX1_LOM",
        veexlib.OTN_ALARM_ODTU_1_OOM            : b"MUX1_OOM",
        veexlib.OTN_ALARM_ODTU_1_ODU_AIS        : b"MUX1_ODUAIS",
        veexlib.OTN_ALARM_ODTU_1_ODU_LCK        : b"MUX1_ODULCK",
        veexlib.OTN_ALARM_ODTU_1_ODU_OCI        : b"MUX1_ODUOCI",
        veexlib.OTN_ALARM_ODTU_1_ODU_BDI        : b"MUX1_ODUBDI",
        veexlib.OTN_ALARM_ODTU_1_ODU_SAPI_TIM   : b"MUX1_ODUSAPITIM",
        veexlib.OTN_ALARM_ODTU_1_ODU_DAPI_TIM   : b"MUX1_ODUDAPITIM",
        veexlib.OTN_ALARM_ODTU_1_OPU_C8_SYNC    : b"MUX1_OPUCMSYNC",
        veexlib.OTN_ALARM_ODTU_1_OPU_PLM        : b"MUX1_OPUPLM",
        veexlib.OTN_ALARM_ODTU_1_OPU_CSF        : b"MUX1_OPUCSF",
        veexlib.OTN_ALARM_ODTU_1_TCM_1_BDI      : b"MUX1_TCM1BDI",
        veexlib.OTN_ALARM_ODTU_1_TCM_2_BDI      : b"MUX1_TCM2BDI",
        veexlib.OTN_ALARM_ODTU_1_TCM_3_BDI      : b"MUX1_TCM3BDI",
        veexlib.OTN_ALARM_ODTU_1_TCM_4_BDI      : b"MUX1_TCM4BDI",
        veexlib.OTN_ALARM_ODTU_1_TCM_5_BDI      : b"MUX1_TCM5DI",
        veexlib.OTN_ALARM_ODTU_1_TCM_6_BDI      : b"MUX1_TCM6BDI",
        veexlib.OTN_ALARM_ODTU_1_TCM_1_BIAE     : b"MUX1_TCM1BIAE",
        veexlib.OTN_ALARM_ODTU_1_TCM_2_BIAE     : b"MUX1_TCM2BIAE",
        veexlib.OTN_ALARM_ODTU_1_TCM_3_BIAE     : b"MUX1_TCM3BIAE",
        veexlib.OTN_ALARM_ODTU_1_TCM_4_BIAE     : b"MUX1_TCM4BIAE",
        veexlib.OTN_ALARM_ODTU_1_TCM_5_BIAE     : b"MUX1_TCM5BIAE",
        veexlib.OTN_ALARM_ODTU_1_TCM_6_BIAE     : b"MUX1_TCM6BIAE",
        veexlib.OTN_ALARM_ODTU_1_TCM_1_SAPI_TIM : b"MUX1_TCM1SAPITIM",
        veexlib.OTN_ALARM_ODTU_1_TCM_2_SAPI_TIM : b"MUX1_TCM2SAPITIM",
        veexlib.OTN_ALARM_ODTU_1_TCM_3_SAPI_TIM : b"MUX1_TCM3SAPITIM",
        veexlib.OTN_ALARM_ODTU_1_TCM_4_SAPI_TIM : b"MUX1_TCM4SAPITIM",
        veexlib.OTN_ALARM_ODTU_1_TCM_5_SAPI_TIM : b"MUX1_TCM5SAPITIM",
        veexlib.OTN_ALARM_ODTU_1_TCM_6_SAPI_TIM : b"MUX1_TCM6SAPITIM",
        veexlib.OTN_ALARM_ODTU_1_TCM_1_DAPI_TIM : b"MUX1_TCM1DAPITIM",
        veexlib.OTN_ALARM_ODTU_1_TCM_2_DAPI_TIM : b"MUX1_TCM2DAPITIM",
        veexlib.OTN_ALARM_ODTU_1_TCM_3_DAPI_TIM : b"MUX1_TCM3DAPITIM",
        veexlib.OTN_ALARM_ODTU_1_TCM_4_DAPI_TIM : b"MUX1_TCM4DAPITIM",
        veexlib.OTN_ALARM_ODTU_1_TCM_5_DAPI_TIM : b"MUX1_TCM5DAPITIM",
        veexlib.OTN_ALARM_ODTU_1_TCM_6_DAPI_TIM : b"MUX1_TCM6DAPITIM",  
        veexlib.OTN_ALARM_ODTU_2_OPU_FREQ_WIDE  : b"MUX2_OPUFREQWIDE",    
        veexlib.OTN_ALARM_ODTU_2_LOF            : b"MUX2_LOF",
        veexlib.OTN_ALARM_ODTU_2_OOF            : b"MUX2_OOF",
        veexlib.OTN_ALARM_ODTU_2_LOM            : b"MUX2_LOM",
        veexlib.OTN_ALARM_ODTU_2_OOM            : b"MUX2_OOM",
        veexlib.OTN_ALARM_ODTU_2_ODU_AIS        : b"MUX2_ODUAIS",
        veexlib.OTN_ALARM_ODTU_2_ODU_LCK        : b"MUX2_ODULCK",
        veexlib.OTN_ALARM_ODTU_2_ODU_OCI        : b"MUX2_ODUOCI",
        veexlib.OTN_ALARM_ODTU_2_ODU_BDI        : b"MUX2_ODUBDI",
        veexlib.OTN_ALARM_ODTU_2_ODU_SAPI_TIM   : b"MUX2_ODUSAPITIM",
        veexlib.OTN_ALARM_ODTU_2_ODU_DAPI_TIM   : b"MUX2_ODUDAPITIM",    
        veexlib.OTN_ALARM_ODTU_2_OPU_C8_SYNC    : b"MUX2_OPUCMSYNC",
        veexlib.OTN_ALARM_ODTU_2_OPU_PLM        : b"MUX2_OPUPLM",
        veexlib.OTN_ALARM_ODTU_2_OPU_CSF        : b"MUX2_OPUCSF",
        veexlib.OTN_ALARM_ODTU_2_TCM_1_BDI      : b"MUX2_TCM1BDI",
        veexlib.OTN_ALARM_ODTU_2_TCM_2_BDI      : b"MUX2_TCM2BDI",
        veexlib.OTN_ALARM_ODTU_2_TCM_3_BDI      : b"MUX2_TCM3BDI",
        veexlib.OTN_ALARM_ODTU_2_TCM_4_BDI      : b"MUX2_TCM4BDI",
        veexlib.OTN_ALARM_ODTU_2_TCM_5_BDI      : b"MUX2_TCM5BDI",
        veexlib.OTN_ALARM_ODTU_2_TCM_6_BDI      : b"MUX2_TCM6BDI",
        veexlib.OTN_ALARM_ODTU_2_TCM_1_BIAE     : b"MUX2_TCM1BIAE",
        veexlib.OTN_ALARM_ODTU_2_TCM_2_BIAE     : b"MUX2_TCM2BIAE",
        veexlib.OTN_ALARM_ODTU_2_TCM_3_BIAE     : b"MUX2_TCM3BIAE",
        veexlib.OTN_ALARM_ODTU_2_TCM_4_BIAE     : b"MUX2_TCM4BIAE",
        veexlib.OTN_ALARM_ODTU_2_TCM_5_BIAE     : b"MUX2_TCM5BIAE",
        veexlib.OTN_ALARM_ODTU_2_TCM_6_BIAE     : b"MUX2_TCM6BIAE",
        veexlib.OTN_ALARM_ODTU_2_TCM_1_SAPI_TIM : b"MUX2_TCM1SAPITIM",
        veexlib.OTN_ALARM_ODTU_2_TCM_2_SAPI_TIM : b"MUX2_TCM2SAPITIM",
        veexlib.OTN_ALARM_ODTU_2_TCM_3_SAPI_TIM :  b"MUX2_TCM3SAPITIM",
        veexlib.OTN_ALARM_ODTU_2_TCM_4_SAPI_TIM :  b"MUX2_TCM4SAPITIM",
        veexlib.OTN_ALARM_ODTU_2_TCM_5_SAPI_TIM :  b"MUX2_TCM5SAPITIM",
        veexlib.OTN_ALARM_ODTU_2_TCM_6_SAPI_TIM :  b"MUX2_TCM6SAPITIM",
        veexlib.OTN_ALARM_ODTU_2_TCM_1_DAPI_TIM :  b"MUX2_TCM1DAPITIM",
        veexlib.OTN_ALARM_ODTU_2_TCM_2_DAPI_TIM :  b"MUX2_TCM2DAPITIM",
        veexlib.OTN_ALARM_ODTU_2_TCM_3_DAPI_TIM :  b"MUX2_TCM3DAPITIM",
        veexlib.OTN_ALARM_ODTU_2_TCM_4_DAPI_TIM :  b"MUX2_TCM4DAPITIM",
        veexlib.OTN_ALARM_ODTU_2_TCM_5_DAPI_TIM :  b"MUX2_TCM5DAPITIM",
        veexlib.OTN_ALARM_ODTU_2_TCM_6_DAPI_TIM :  b"MUX2_TCM6DAPITIM",  
        veexlib.OTN_ALARM_ODTU_3_OPU_FREQ_WIDE  :  b"MUX3_OPUFREQWIDE", 
        veexlib.OTN_ALARM_ODTU_3_LOF            :  b"MUX3_LOF",
        veexlib.OTN_ALARM_ODTU_3_OOF            :  b"MUX3_OOF",
        veexlib.OTN_ALARM_ODTU_3_LOM            :  b"MUX3_LOM",
        veexlib.OTN_ALARM_ODTU_3_OOM            :  b"MUX3_OOM",
        veexlib.OTN_ALARM_ODTU_3_ODU_AIS        :  b"MUX3_ODUAIS",
        veexlib.OTN_ALARM_ODTU_3_ODU_LCK        :  b"MUX3_ODULCK",
        veexlib.OTN_ALARM_ODTU_3_ODU_OCI        :  b"MUX3_ODUOCI",
        veexlib.OTN_ALARM_ODTU_3_ODU_BDI        :  b"MUX3_ODUBDI",
        veexlib.OTN_ALARM_ODTU_3_ODU_SAPI_TIM   :  b"MUX3_ODUSAPITIM",
        veexlib.OTN_ALARM_ODTU_3_ODU_DAPI_TIM   :  b"MUX3_ODUDAPITIM",      
        veexlib.OTN_ALARM_ODTU_3_OPU_C8_SYNC    :  b"MUX3_OPUCMSYNC",
        veexlib.OTN_ALARM_ODTU_3_OPU_PLM        :  b"MUX3_OPUPLM",
        veexlib.OTN_ALARM_ODTU_3_OPU_CSF        :  b"MUX3_OPUCSF",  
        veexlib.OTN_ALARM_ODTU_3_TCM_1_BDI      :  b"MUX3_TCM1BDI",
        veexlib.OTN_ALARM_ODTU_3_TCM_2_BDI      :  b"MUX3_TCM2BDI",
        veexlib.OTN_ALARM_ODTU_3_TCM_3_BDI      :  b"MUX3_TCM3BDI",
        veexlib.OTN_ALARM_ODTU_3_TCM_4_BDI      :  b"MUX3_TCM4BDI",
        veexlib.OTN_ALARM_ODTU_3_TCM_5_BDI      :  b"MUX3_TCM5BDI",
        veexlib.OTN_ALARM_ODTU_3_TCM_6_BDI      :  b"MUX3_TCM6BDI",
        veexlib.OTN_ALARM_ODTU_3_TCM_1_BIAE     :  b"MUX3_TCM1BIAE",
        veexlib.OTN_ALARM_ODTU_3_TCM_2_BIAE     :  b"MUX3_TCM2BIAE",
        veexlib.OTN_ALARM_ODTU_3_TCM_3_BIAE     :  b"MUX3_TCM3BIAE",
        veexlib.OTN_ALARM_ODTU_3_TCM_4_BIAE     :  b"MUX3_TCM4BIAE",
        veexlib.OTN_ALARM_ODTU_3_TCM_5_BIAE     :  b"MUX3_TCM5BIAE",
        veexlib.OTN_ALARM_ODTU_3_TCM_6_BIAE     :  b"MUX3_TCM6BIAE",
        veexlib.OTN_ALARM_ODTU_3_TCM_1_SAPI_TIM :  b"MUX3_TCM1SAPITIM",
        veexlib.OTN_ALARM_ODTU_3_TCM_2_SAPI_TIM :  b"MUX3_TCM2SAPITIM",
        veexlib.OTN_ALARM_ODTU_3_TCM_3_SAPI_TIM :  b"MUX3_TCM3SAPITIM",
        veexlib.OTN_ALARM_ODTU_3_TCM_4_SAPI_TIM :  b"MUX3_TCM4SAPITIM",
        veexlib.OTN_ALARM_ODTU_3_TCM_5_SAPI_TIM :  b"MUX3_TCM5SAPITIM",
        veexlib.OTN_ALARM_ODTU_3_TCM_6_SAPI_TIM :  b"MUX3_TCM6SAPITIM",
        veexlib.OTN_ALARM_ODTU_3_TCM_1_DAPI_TIM :  b"MUX3_TCM1DAPITIM",
        veexlib.OTN_ALARM_ODTU_3_TCM_2_DAPI_TIM :  b"MUX3_TCM2DAPITIM",
        veexlib.OTN_ALARM_ODTU_3_TCM_3_DAPI_TIM :  b"MUX3_TCM3DAPITIM",
        veexlib.OTN_ALARM_ODTU_3_TCM_4_DAPI_TIM :  b"MUX3_TCM4DAPITIM",
        veexlib.OTN_ALARM_ODTU_3_TCM_5_DAPI_TIM :  b"MUX3_TCM5DAPITIM",
        veexlib.OTN_ALARM_ODTU_3_TCM_6_DAPI_TIM :  b"MUX3_TCM6DAPITIM",  
        }

    # Dictionary to convert between ProtoBuf enum and SPCI text for OTN Error type.
    OtnErrorTypeTable = {
        veexlib.OTN_ERR_NONE                              : b"NONE",
        veexlib.OTN_ERR_FRAME                             : b"FRAME",
        veexlib.OTN_ERR_MFAS                              : b"MFAS",
        veexlib.OTN_ERR_FEC_UNCOR                         : b"FECUNCOR",
        veexlib.OTN_ERR_FEC_COR                           : b"FECCOR",
        veexlib.OTN_ERR_OTU_BIP8                          : b"OTUBIP8",
        veexlib.OTN_ERR_OTU_BEI                           : b"OTUBEI",
        veexlib.OTN_ERR_ODU_BIP8                          : b"ODUBIP8",
        veexlib.OTN_ERR_ODU_BEI                           : b"ODUBEI",
        veexlib.OTN_ERR_TCM_1_BIP8                        : b"TCM1BIP8",
        veexlib.OTN_ERR_TCM_2_BIP8                        : b"TCM2BIP8",
        veexlib.OTN_ERR_TCM_3_BIP8                        : b"TCM3BIP8",
        veexlib.OTN_ERR_TCM_4_BIP8                        : b"TCM4BIP8",
        veexlib.OTN_ERR_TCM_5_BIP8                        : b"TCM5BIP8",
        veexlib.OTN_ERR_TCM_6_BIP8                        : b"TCM6BIP8",
        veexlib.OTN_ERR_TCM_1_BEI                         : b"TCM1BEI",
        veexlib.OTN_ERR_TCM_2_BEI                         : b"TCM2BEI",
        veexlib.OTN_ERR_TCM_3_BEI                         : b"TCM3BEI",
        veexlib.OTN_ERR_TCM_4_BEI                         : b"TCM4BEI",
        veexlib.OTN_ERR_TCM_5_BEI                         : b"TCM5BEI",
        veexlib.OTN_ERR_TCM_6_BEI                         : b"TCM6BEI",
        veexlib.OTN_ERR_BIT                               : b"BIT",
        veexlib.OTN_ERR_ALARM_BURST_OTU_IAE               : b"ERR_ALARM_BURST_OTUIAE",
        veexlib.OTN_ERR_ALARM_BURST_OTU_BDI               : b"ERR_ALARM_BURST_OTUBDI",
        veexlib.OTN_ERR_ALARM_BURST_ODU_AIS               : b"ERR_ALARM_BURST_ODUAIS",
        veexlib.OTN_ERR_ALARM_BURST_ODU_LCK               : b"ERR_ALARM_BURST_ODULCK",
        veexlib.OTN_ERR_ALARM_BURST_ODU_OCI               : b"ERR_ALARM_BURST_ODUOCI",
        veexlib.OTN_ERR_ALARM_BURST_ODU_BDI               : b"ERR_ALARM_BURST_ODUBDI",
        veexlib.OTN_ERR_ALARM_BURST_TCM_1_BDI             : b"ERR_ALARM_BURST_TCM1BDI",
        veexlib.OTN_ERR_ALARM_BURST_TCM_2_BDI             : b"ERR_ALARM_BURST_TCM2BDI",
        veexlib.OTN_ERR_ALARM_BURST_TCM_3_BDI             : b"ERR_ALARM_BURST_TCM3BDI",
        veexlib.OTN_ERR_ALARM_BURST_TCM_4_BDI             : b"ERR_ALARM_BURST_TCM4BDI",
        veexlib.OTN_ERR_ALARM_BURST_TCM_5_BDI             : b"ERR_ALARM_BURST_TCM5BDI",
        veexlib.OTN_ERR_ALARM_BURST_TCM_6_BDI             : b"ERR_ALARM_BURST_TCM6BDI",
        veexlib.OTN_ERR_ODTU_ODU_BIP8                     : b"MUXODUBIP8",
        veexlib.OTN_ERR_ODTU_ODU_BEI                      : b"MUXODUBEI",
        veexlib.OTN_ERR_ODTU_TCM_1_BIP8                   : b"MUXTCM1BIP8",
        veexlib.OTN_ERR_ODTU_TCM_2_BIP8                   : b"MUXTCM2BIP8",
        veexlib.OTN_ERR_ODTU_TCM_3_BIP8                   : b"MUXTCM3BIP8",
        veexlib.OTN_ERR_ODTU_TCM_4_BIP8                   : b"MUXTCM4BIP8",
        veexlib.OTN_ERR_ODTU_TCM_5_BIP8                   : b"MUXTCM5BIP8",
        veexlib.OTN_ERR_ODTU_TCM_6_BIP8                   : b"MUXTCM6BIP8",
        veexlib.OTN_ERR_ODTU_TCM_1_BEI                    : b"MUXTCM1BEI",
        veexlib.OTN_ERR_ODTU_TCM_2_BEI                    : b"MUXTCM2BEI",
        veexlib.OTN_ERR_ODTU_TCM_3_BEI                    : b"MUXTCM3BEI",
        veexlib.OTN_ERR_ODTU_TCM_4_BEI                    : b"MUXTCM4BEI",
        veexlib.OTN_ERR_ODTU_TCM_5_BEI                    : b"MUXTCM5BEI",
        veexlib.OTN_ERR_ODTU_TCM_6_BEI                    : b"MUXTCM6BEI",
        veexlib.OTN_ERR_ODTU_FRAME                        : b"MUXFRAME",
        veexlib.OTN_ERR_ODTU_MFAS                         : b"MUXMFAS",
#        veexlib.OTN_ERR_ODTU_ALARM_BURST_ODU_AIS          : b"",
#        veexlib.OTN_ERR_ODTU_ALARM_BURST_ODU_LCK          : b"",
#        veexlib.OTN_ERR_ODTU_ALARM_BURST_ODU_OCI          : b"",
#        veexlib.OTN_ERR_ODTU_ALARM_BURST_ODU_BDI          : b"",
#        veexlib.OTN_ERR_ODTU_ALARM_BURST_TCM_1_BDI        : b"",
#        veexlib.OTN_ERR_ODTU_ALARM_BURST_TCM_2_BDI        : b"",
#        veexlib.OTN_ERR_ODTU_ALARM_BURST_TCM_3_BDI        : b"",
#        veexlib.OTN_ERR_ODTU_ALARM_BURST_TCM_4_BDI        : b"",
#        veexlib.OTN_ERR_ODTU_ALARM_BURST_TCM_5_BDI        : b"",
#        veexlib.OTN_ERR_ODTU_ALARM_BURST_TCM_6_BDI        : b"",
#        veexlib.OTN_ERR_ALARM_BURST_OTU_BIAE              : b"",
        veexlib.OTN_ERR_ALARM_BURST_TCM_1_BIAE            : b"ERR_ALARM_BURST_TCM1BIAE",
        veexlib.OTN_ERR_ALARM_BURST_TCM_2_BIAE            : b"ERR_ALARM_BURST_TCM2BIAE",
        veexlib.OTN_ERR_ALARM_BURST_TCM_3_BIAE            : b"ERR_ALARM_BURST_TCM3BIAE",
        veexlib.OTN_ERR_ALARM_BURST_TCM_4_BIAE            : b"ERR_ALARM_BURST_TCM4BIAE",
        veexlib.OTN_ERR_ALARM_BURST_TCM_5_BIAE            : b"ERR_ALARM_BURST_TCM5BIAE",
        veexlib.OTN_ERR_ALARM_BURST_TCM_6_BIAE            : b"ERR_ALARM_BURST_TCM6BIAE",
#         veexlib.OTN_ERR_ODTU_ALARM_BURST_TCM_1_BIAE       : b"",
#         veexlib.OTN_ERR_ODTU_ALARM_BURST_TCM_2_BIAE       : b"",
#         veexlib.OTN_ERR_ODTU_ALARM_BURST_TCM_3_BIAE       : b"",
#         veexlib.OTN_ERR_ODTU_ALARM_BURST_TCM_4_BIAE       : b"",
#         veexlib.OTN_ERR_ODTU_ALARM_BURST_TCM_5_BIAE       : b"",
#         veexlib.OTN_ERR_ODTU_ALARM_BURST_TCM_6_BIAE       : b"",
        veexlib.OTN_ERR_ODTU_OPU_C8_CRC_8                 : b"MUXCMCRC8",
#        veexlib.OTN_ERR_ALARM_BURST_ODTU_OPU_C8_SYNC      : b"",
        veexlib.OTN_ERR_OPU_C8_CRC_8                      : b"CMCRC8",
#        veexlib.OTN_ERR_ALARM_BURST_OPU_C8_SYNC           : b"",
#        veexlib.OTN_ERR_ALARM_BURST_OPU_AIS               : b"",
#        veexlib.OTN_ERR_ALARM_BURST_OPU_CSF               : b"",
#        veexlib.OTN_ERR_ODTU_ALARM_BURST_OPU_CSF          : b"",
        veexlib.OTN_ERR_OMFI                              : b"OMFI",
#        veexlib.OTN_ERR_ALARM_BURST_OMFI                  : b"",
        veexlib.OTN_ERR_BLOCK_1027B                       : b"LAN_1027BBLOCK",
        veexlib.OTN_ERR_LAN_OTN_BIP8_LANE1                : b"LAN0_OTNBIP8",
        veexlib.OTN_ERR_LAN_OTN_BIP8_LANE2                : b"LAN1_OTNBIP8",
        veexlib.OTN_ERR_LAN_OTN_BIP8_LANE3                : b"LAN2_OTNBIP8",
        veexlib.OTN_ERR_LAN_OTN_BIP8_LANE4                : b"LAN3_OTNBIP8",
        veexlib.OTN_ERR_LAN_PCS_BIP8_LANE1                : b"LAN0_PCSBIP8",
        veexlib.OTN_ERR_LAN_PCS_BIP8_LANE2                : b"LAN1_PCSBIP8",
        veexlib.OTN_ERR_LAN_PCS_BIP8_LANE3                : b"LAN2_PCSBIP8",
        veexlib.OTN_ERR_LAN_PCS_BIP8_LANE4                : b"LAN3_PCSBIP8",
        veexlib.OTN_ERR_ODTU_0_FRAME                      : b"MUX0_FRAME",
        veexlib.OTN_ERR_ODTU_0_MFAS                       : b"MUX0_MFAS",
        veexlib.OTN_ERR_ODTU_0_ODU_BIP8                   : b"MUX0_ODUBIP8",
        veexlib.OTN_ERR_ODTU_0_ODU_BEI                    : b"MUX0_ODUBEI",
        veexlib.OTN_ERR_ODTU_0_OPU_C8_CRC_8               : b"MUX0_OPUC8CRC8",
        veexlib.OTN_ERR_ODTU_0_TCM_1_BIP8                 : b"MUX0_TCM1BIP8",
        veexlib.OTN_ERR_ODTU_0_TCM_2_BIP8                 : b"MUX0_TCM2BIP8",
        veexlib.OTN_ERR_ODTU_0_TCM_3_BIP8                 : b"MUX0_TCM3BIP8",
        veexlib.OTN_ERR_ODTU_0_TCM_4_BIP8                 : b"MUX0_TCM4BIP8",
        veexlib.OTN_ERR_ODTU_0_TCM_5_BIP8                 : b"MUX0_TCM5BIP8",
        veexlib.OTN_ERR_ODTU_0_TCM_6_BIP8                 : b"MUX0_TCM6BIP8",
        veexlib.OTN_ERR_ODTU_0_TCM_1_BEI                  : b"MUX0_TCM1BEI",
        veexlib.OTN_ERR_ODTU_0_TCM_2_BEI                  : b"MUX0_TCM2BEI",
        veexlib.OTN_ERR_ODTU_0_TCM_3_BEI                  : b"MUX0_TCM3BEI",
        veexlib.OTN_ERR_ODTU_0_TCM_4_BEI                  : b"MUX0_TCM4BEI",
        veexlib.OTN_ERR_ODTU_0_TCM_5_BEI                  : b"MUX0_TCM5BEI",
        veexlib.OTN_ERR_ODTU_0_TCM_6_BEI                  : b"MUX0_TCM6BEI",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_ODU_AIS        : b"MUX0_ERR_ALARM_BURST_ODUAIS",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_ODU_LCK        : b"MUX0_ERR_ALARM_BURST_ODULCK",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_ODU_OCI        : b"MUX0_ERR_ALARM_BURST_ODUOCI",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_ODU_BDI        : b"MUX0_ERR_ALARM_BURST_ODUBDI",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_OPU_C8_SYNC    : b"MUX0_ERR_ALARM_BURST_OPUCMSYNC",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_OPU_CSF        : b"MUX0_ERR_ALARM_BURST_OPUCSF",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_TCM_1_BDI      : b"MUX0_ERR_ALARM_BURST_TCM1BDI",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_TCM_2_BDI      : b"MUX0_ERR_ALARM_BURST_TCM2BDI",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_TCM_3_BDI      : b"MUX0_ERR_ALARM_BURST_TCM3BDI",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_TCM_4_BDI      : b"MUX0_ERR_ALARM_BURST_TCM4BDI",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_TCM_5_BDI      : b"MUX0_ERR_ALARM_BURST_TCM5BDI",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_TCM_6_BDI      : b"MUX0_ERR_ALARM_BURST_TCM6BDI",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_TCM_1_BIAE     : b"MUX0_ERR_ALARM_BURST_TCM1BIAE",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_TCM_2_BIAE     : b"MUX0_ERR_ALARM_BURST_TCM2BIAE",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_TCM_3_BIAE     : b"MUX0_ERR_ALARM_BURST_TCM3BIAE",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_TCM_4_BIAE     : b"MUX0_ERR_ALARM_BURST_TCM4BIAE",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_TCM_5_BIAE     : b"MUX0_ERR_ALARM_BURST_TCM5BIAE",
        veexlib.OTN_ERR_ODTU_0_ALARM_BURST_TCM_6_BIAE     : b"MUX0_ERR_ALARM_BURST_TCM6BIAE",
        veexlib.OTN_ERR_ODTU_1_FRAME                      : b"MUX1_FRAME",
        veexlib.OTN_ERR_ODTU_1_MFAS                       : b"MUX1_MFAS",
        veexlib.OTN_ERR_ODTU_1_ODU_BIP8                   : b"MUX1_ODUBIP8",
        veexlib.OTN_ERR_ODTU_1_ODU_BEI                    : b"MUX1_ODUBEI",
        veexlib.OTN_ERR_ODTU_1_OPU_C8_CRC_8               : b"MUX1_OPUC8CRC8",
        veexlib.OTN_ERR_ODTU_1_TCM_1_BIP8                 : b"MUX1_TCM1BIP8",
        veexlib.OTN_ERR_ODTU_1_TCM_2_BIP8                 : b"MUX1_TCM2BIP8",
        veexlib.OTN_ERR_ODTU_1_TCM_3_BIP8                 : b"MUX1_TCM3BIP8",
        veexlib.OTN_ERR_ODTU_1_TCM_4_BIP8                 : b"MUX1_TCM4BIP8",
        veexlib.OTN_ERR_ODTU_1_TCM_5_BIP8                 : b"MUX1_TCM5BIP8",
        veexlib.OTN_ERR_ODTU_1_TCM_6_BIP8                 : b"MUX1_TCM6BIP8",
        veexlib.OTN_ERR_ODTU_1_TCM_1_BEI                  : b"MUX1_TCM1BEI",
        veexlib.OTN_ERR_ODTU_1_TCM_2_BEI                  : b"MUX1_TCM2BEI",
        veexlib.OTN_ERR_ODTU_1_TCM_3_BEI                  : b"MUX1_TCM3BEI",
        veexlib.OTN_ERR_ODTU_1_TCM_4_BEI                  : b"MUX1_TCM4BEI",
        veexlib.OTN_ERR_ODTU_1_TCM_5_BEI                  : b"MUX1_TCM5BEI",
        veexlib.OTN_ERR_ODTU_1_TCM_6_BEI                  : b"MUX1_TCM6BEI",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_ODU_AIS        : b"MUX1_ERR_ALARM_BURST_ODUAIS",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_ODU_LCK        : b"MUX1_ERR_ALARM_BURST_ODULCK",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_ODU_OCI        : b"MUX1_ERR_ALARM_BURST_ODUOCI",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_ODU_BDI        : b"MUX1_ERR_ALARM_BURST_ODUBDI",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_OPU_C8_SYNC    : b"MUX1_ERR_ALARM_BURST_OPUCMSYNC",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_OPU_CSF        : b"MUX1_ERR_ALARM_BURST_OPUCSF",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_TCM_1_BDI      : b"MUX1_ERR_ALARM_BURST_TCM1BDI",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_TCM_2_BDI      : b"MUX1_ERR_ALARM_BURST_TCM2BDI",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_TCM_3_BDI      : b"MUX1_ERR_ALARM_BURST_TCM3BDI",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_TCM_4_BDI      : b"MUX1_ERR_ALARM_BURST_TCM4BDI",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_TCM_5_BDI      : b"MUX1_ERR_ALARM_BURST_TCM5BDI",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_TCM_6_BDI      : b"MUX1_ERR_ALARM_BURST_TCM6BDI",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_TCM_1_BIAE     : b"MUX1_ERR_ALARM_BURST_TCM1BIAE",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_TCM_2_BIAE     : b"MUX1_ERR_ALARM_BURST_TCM2BIAE",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_TCM_3_BIAE     : b"MUX1_ERR_ALARM_BURST_TCM3BIAE",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_TCM_4_BIAE     : b"MUX1_ERR_ALARM_BURST_TCM4BIAE",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_TCM_5_BIAE     : b"MUX1_ERR_ALARM_BURST_TCM5BIAE",
        veexlib.OTN_ERR_ODTU_1_ALARM_BURST_TCM_6_BIAE     : b"MUX1_ERR_ALARM_BURST_TCM6BIAE",
        veexlib.OTN_ERR_ODTU_2_FRAME                      : b"MUX2_FRAME",
        veexlib.OTN_ERR_ODTU_2_MFAS                       : b"MUX2_MFAS",
        veexlib.OTN_ERR_ODTU_2_ODU_BIP8                   : b"MUX2_ODUBIP8",
        veexlib.OTN_ERR_ODTU_2_ODU_BEI                    : b"MUX2_ODUBEI",
        veexlib.OTN_ERR_ODTU_2_OPU_C8_CRC_8               : b"MUX2_OPUC8CRC8",
        veexlib.OTN_ERR_ODTU_2_TCM_1_BIP8                 : b"MUX2_TCM1BIP8",
        veexlib.OTN_ERR_ODTU_2_TCM_2_BIP8                 : b"MUX2_TCM2BIP8",
        veexlib.OTN_ERR_ODTU_2_TCM_3_BIP8                 : b"MUX2_TCM3BIP8",
        veexlib.OTN_ERR_ODTU_2_TCM_4_BIP8                 : b"MUX2_TCM4BIP8",
        veexlib.OTN_ERR_ODTU_2_TCM_5_BIP8                 : b"MUX2_TCM5BIP8",
        veexlib.OTN_ERR_ODTU_2_TCM_6_BIP8                 : b"MUX2_TCM56BIP8",
        veexlib.OTN_ERR_ODTU_2_TCM_1_BEI                  : b"MUX2_TCM1BEI",
        veexlib.OTN_ERR_ODTU_2_TCM_2_BEI                  : b"MUX2_TCM2BEI",
        veexlib.OTN_ERR_ODTU_2_TCM_3_BEI                  : b"MUX2_TCM3BEI",
        veexlib.OTN_ERR_ODTU_2_TCM_4_BEI                  : b"MUX2_TCM4BEI",
        veexlib.OTN_ERR_ODTU_2_TCM_5_BEI                  : b"MUX2_TCM5BEI",
        veexlib.OTN_ERR_ODTU_2_TCM_6_BEI                  : b"MUX2_TCM6BEI",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_ODU_AIS        : b"MUX2_ERR_ALARM_BURST_ODUAIS",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_ODU_LCK        : b"MUX2_ERR_ALARM_BURST_ODULCK",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_ODU_OCI        : b"MUX2_ERR_ALARM_BURST_ODUOCI",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_ODU_BDI        : b"MUX2_ERR_ALARM_BURST_ODUBDI",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_OPU_C8_SYNC    : b"MUX2_ERR_ALARM_BURST_OPUCMSYNC",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_OPU_CSF        : b"MUX2_ERR_ALARM_BURST_OPUCSF",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_TCM_1_BDI      : b"MUX2_ERR_ALARM_BURST_TCM1BDI",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_TCM_2_BDI      : b"MUX2_ERR_ALARM_BURST_TCM2BDI",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_TCM_3_BDI      : b"MUX2_ERR_ALARM_BURST_TCM3BDI",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_TCM_4_BDI      : b"MUX2_ERR_ALARM_BURST_TCM4BDI",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_TCM_5_BDI      : b"MUX2_ERR_ALARM_BURST_TCM5BDI",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_TCM_6_BDI      : b"MUX2_ERR_ALARM_BURST_TCM6BDI",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_TCM_1_BIAE     : b"MUX2_ERR_ALARM_BURST_TCM1BIAE",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_TCM_2_BIAE     : b"MUX2_ERR_ALARM_BURST_TCM2BIAE",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_TCM_3_BIAE     : b"MUX2_ERR_ALARM_BURST_TCM3BIAE",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_TCM_4_BIAE     : b"MUX2_ERR_ALARM_BURST_TCM4BIAE",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_TCM_5_BIAE     : b"MUX2_ERR_ALARM_BURST_TCM5BIAE",
        veexlib.OTN_ERR_ODTU_2_ALARM_BURST_TCM_6_BIAE     : b"MUX2_ERR_ALARM_BURST_TCM6BIAE",
        veexlib.OTN_ERR_ODTU_3_FRAME                      : b"MUX3_FRAME",
        veexlib.OTN_ERR_ODTU_3_MFAS                       : b"MUX3_MFAS",
        veexlib.OTN_ERR_ODTU_3_ODU_BIP8                   : b"MUX3_ODUBIP8",
        veexlib.OTN_ERR_ODTU_3_ODU_BEI                    : b"MUX3_ODUBEI",
        veexlib.OTN_ERR_ODTU_3_OPU_C8_CRC_8               : b"MUX3_OPUC8CRC8",
        veexlib.OTN_ERR_ODTU_3_TCM_1_BIP8                 : b"MUX3_TCM1BIP8",
        veexlib.OTN_ERR_ODTU_3_TCM_2_BIP8                 : b"MUX3_TCM2BIP8",
        veexlib.OTN_ERR_ODTU_3_TCM_3_BIP8                 : b"MUX3_TCM3BIP8",
        veexlib.OTN_ERR_ODTU_3_TCM_4_BIP8                 : b"MUX3_TCM4BIP8",
        veexlib.OTN_ERR_ODTU_3_TCM_5_BIP8                 : b"MUX3_TCM5BIP8",
        veexlib.OTN_ERR_ODTU_3_TCM_6_BIP8                 : b"MUX3_TCM6BIP8",
        veexlib.OTN_ERR_ODTU_3_TCM_1_BEI                  : b"MUX3_TCM1BEI",
        veexlib.OTN_ERR_ODTU_3_TCM_2_BEI                  : b"MUX3_TCM2BEI",
        veexlib.OTN_ERR_ODTU_3_TCM_3_BEI                  : b"MUX3_TCM3BEI",
        veexlib.OTN_ERR_ODTU_3_TCM_4_BEI                  : b"MUX3_TCM4BEI",
        veexlib.OTN_ERR_ODTU_3_TCM_5_BEI                  : b"MUX3_TCM5BEI",
        veexlib.OTN_ERR_ODTU_3_TCM_6_BEI                  : b"MUX3_TCM6BEI",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_ODU_AIS        : b"MUX3_ERR_ALARM_BURST_ODUAIS",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_ODU_LCK        : b"MUX3_ERR_ALARM_BURST_ODULCK",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_ODU_OCI        : b"MUX3_ERR_ALARM_BURST_ODUOCI",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_ODU_BDI        : b"MUX3_ERR_ALARM_BURST_ODUBDI",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_OPU_C8_SYNC    : b"MUX3_ERR_ALARM_BURST_OPUCMSYNC",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_OPU_CSF        : b"MUX3_ERR_ALARM_BURST_OPUCSF",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_TCM_1_BDI      : b"MUX3_ERR_ALARM_BURST_TCM1BDI",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_TCM_2_BDI      : b"MUX3_ERR_ALARM_BURST_TCM2BDI",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_TCM_3_BDI      : b"MUX3_ERR_ALARM_BURST_TCM3BDI",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_TCM_4_BDI      : b"MUX3_ERR_ALARM_BURST_TCM4BDI",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_TCM_5_BDI      : b"MUX3_ERR_ALARM_BURST_TCM5BDI",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_TCM_6_BDI      : b"MUX3_ERR_ALARM_BURST_TCM6BDI",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_TCM_1_BIAE     : b"MUX3_ERR_ALARM_BURST_TCM1BIAE",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_TCM_2_BIAE     : b"MUX3_ERR_ALARM_BURST_TCM2BIAE",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_TCM_3_BIAE     : b"MUX3_ERR_ALARM_BURST_TCM3BIAE",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_TCM_4_BIAE     : b"MUX3_ERR_ALARM_BURST_TCM4BIAE",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_TCM_5_BIAE     : b"MUX3_ERR_ALARM_BURST_TCM5BIAE",
        veexlib.OTN_ERR_ODTU_3_ALARM_BURST_TCM_6_BIAE     : b"MUX3_ERR_ALARM_BURST_TCM6BIAE",
        veexlib.OTN_ERR_FRAME_OTUCN_SYNC                  : b"FRAME_OTUCN_SYNC",
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

    def getTxAlarmType(self, parameters):
        '''**TX:ALarm:TYPE?** -
        Query the alarm type being generated.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.alarmGenType in ScpiOtn.OtnAlarmTypeTable.keys():
            response = ScpiOtn.OtnAlarmTypeTable[self.globals.veexOtn.sets.alarmGenType]   
        else:
            response = response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setTxAlarmType(self, parameters):
        '''**TX:ALarm:TYPE:<alarm>** -
        Sets the alarm type, and begins generating that alarm.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for key, value in ScpiOtn.OtnAlarmTypeTable.items():
                if paramList[0].head.upper().startswith(value):
                    self.globals.veexOtn.sets.alarmGenType = key
                    return None
            response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxCoupled(self, parameters):
        '''**TX:COUPled? and RX:COUPled?** -
        Query if coupled or independent.
        '''
        self.globals.veexOtn.sets.update()
        if (self.globals.veexOtn.sets.settingsControl == veexlib.COUPLED_TX_INTO_RX) or \
           (self.globals.veexOtn.sets.settingsControl == veexlib.COUPLED_RX_INTO_TX):
            response = b"YES"
        elif self.globals.veexOtn.sets.settingsControl == veexlib.INDEPENDENT_TX_RX:
            response = b"NO"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setTxCoupled(self, parameters):
        '''**TX:COUPled <YES|NO> and RX:COUPled <YES|NO>** -
        Sets to coupled or independent.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"YES"):
                self.globals.veexOtn.sets.settingsControl = veexlib.COUPLED_TX_INTO_RX
            elif paramList[0].head.upper().startswith(b"NO"):
                self.globals.veexOtn.sets.settingsControl = veexlib.INDEPENDENT_TX_RX
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response


    def getTxClock(self, parameters):
        '''**TX:CLOCK?** -
        Query the TX clock reference source.
        '''
        self.globals.veexOtn.sets.update()
        if self.globals.veexOtn.sets.clockType == veexlib.CLOCK_INTERNAL:
            response = b"INT"
        elif self.globals.veexOtn.sets.clockType == veexlib.CLOCK_RECOVERED:
            response = b"LOOP"
        elif self.globals.veexOtn.sets.clockType == veexlib.CLOCK_BITS_SETS:
            response = b"BITS/SETS"
        elif self.globals.veexOtn.sets.clockType == veexlib.CLOCK_BITS:
            response = b"BITS"
        elif self.globals.veexOtn.sets.clockType == veexlib.CLOCK_SETS:
            response = b"SETS"
        elif self.globals.veexOtn.sets.clockType == veexlib.CLOCK_EXT_8KHZ:
            response = b"EXT8KHZ"
        elif self.globals.veexOtn.sets.clockType == veexlib.CLOCK_EXT_BITS:
            response = b"EXT1_5MHZ"
        elif self.globals.veexOtn.sets.clockType == veexlib.CLOCK_EXT_SETS:
            response = b"EXT2MHZ"
        elif self.globals.veexOtn.sets.clockType == veexlib.CLOCK_EXT_10MHZ:
            response = b"EXT10MHZ"
        elif self.globals.veexOtn.sets.clockType == veexlib.CLOCK_SYNC:
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
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"INT"):
                self.globals.veexOtn.sets.clockType = veexlib.CLOCK_INTERNAL
            elif paramList[0].head.upper().startswith(b"LOOP"):
                self.globals.veexOtn.sets.clockType = veexlib.CLOCK_RECOVERED
            elif paramList[0].head.upper().startswith(b"BITS/SETS"):
                self.globals.veexOtn.sets.clockType = veexlib.CLOCK_BITS_SETS
            elif paramList[0].head.upper().startswith(b"BITS"):
                self.globals.veexOtn.sets.clockType = veexlib.CLOCK_BITS
            elif paramList[0].head.upper().startswith(b"SETS"):
                self.globals.veexOtn.sets.clockType = veexlib.CLOCK_SETS
            elif paramList[0].head.upper().startswith(b"EXT8KHZ"):
                self.globals.veexOtn.sets.clockType = veexlib.CLOCK_EXT_8KHZ
            elif paramList[0].head.upper().startswith(b"EXT1_5MHZ"):
                self.globals.veexOtn.sets.clockType = veexlib.CLOCK_EXT_BITS
            elif paramList[0].head.upper().startswith(b"EXT2MHZ"):
                self.globals.veexOtn.sets.clockType = veexlib.CLOCK_EXT_SETS
            elif paramList[0].head.upper().startswith(b"EXT10MHZ"):
                self.globals.veexOtn.sets.clockType = veexlib.CLOCK_EXT_10MHZ
            elif paramList[0].head.upper().startswith(b"SYNC"):
                self.globals.veexOtn.sets.clockType = veexlib.CLOCK_SYNC
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxDataInvert(self, parameters):
        #'''**TX:DATAINVERT?** -
        #Query the transmit Data Inversion mode for the 43GHz NRZ-DPSK transponder.
        #'''
        self.globals.veexOtn.sets.update()
        if self.globals.veexOtn.sets.txDataInvert:
            response = b"ON"
        else:
            response = b"OFF"
        return response

    def setTxDataInvert(self, parameters):
        #'''**TX:DATAINVERT <ON|OFF>** -
        #Enables or Disables the transmit Data Inversion option for the 43GHz NRZ-DPSK transponder.
        #'''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ON"):
                self.globals.veexOtn.sets.txDataInvert = True
            elif paramList[0].head.upper().startswith(b"OFF"):
                self.globals.veexOtn.sets.txDataInvert = False
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxErrBurst(self, parameters):
        '''**TX:ERRor:BURSTPERIOD?** -
        Query the value of the transmit Error Burst Period. Value returned in frames.
        '''
        self.globals.veexOtn.sets.update()
        return b"%d" % self.globals.veexOtn.sets.errorGenBurstPeriod

    def setTxErrBurst(self, parameters):
        '''**TX:ERRor:BURSTPERIOD:<value>** -
        Sets the value of the transmit Error Burst Period.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            burstPeriod = ParseUtils.checkNumeric(paramList[0].head)
            if burstPeriod >= 0 and burstPeriod <= 1048575:
                self.globals.veexOtn.sets.update()
                errorType = self.globals.veexOtn.sets.errorGenType
                burstSizeNum = self.globals.veexOtn.sets.errorGenBurstSize
                self.globals.veexOtn.sets.setErrorGenBurst(errorType,burstSizeNum,burstPeriod)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxErrBurstSize(self, parameters):
        '''**TX:ERRor:BURSTSIZE?** -
        Query the value of the transmit Error Burst Size. Value returned in frames.
        '''
        self.globals.veexOtn.sets.update()
        return b"%d" % self.globals.veexOtn.sets.errorGenBurstSize

    def setTxErrBurstSize(self, parameters):
        '''**TX:ERRor:BURSTSIZE:<value>** -
        Sets the value of the transmit Error Burst Size.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            burstSizeNum = ParseUtils.checkNumeric(paramList[0].head)
            if burstSizeNum >= 0 and burstSizeNum <= 65535:
                self.globals.veexOtn.sets.update()
                errorType = self.globals.veexOtn.sets.errorGenType
                burstPeriod = self.globals.veexOtn.sets.errorGenBurstPeriod
                self.globals.veexOtn.sets.setErrorGenBurst(errorType,burstSizeNum,burstPeriod)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxErrRate(self, parameters):
        '''**TX:ERRor:RATE?** -
        Query the error rate and returns the value as given in the command.
        '''
        self.globals.veexOtn.sets.update()
        return b"%.2e" % self.globals.veexOtn.sets.errorGenRate

    def setTxErrRate(self, parameters):
        '''**TX:ERRor:RATE <rate>** -
        Sets the transmit Error generation rate.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"SINGLE"):
                self.globals.veexOtn.insertSingleError(self.globals.veexOtn.sets.errorGenType)
            elif paramList[0].head.upper().startswith(b"0"):
                self.globals.veexOtn.sets.errorGenRate = 0.0
            elif ParseUtils.isFloatE(paramList[0].head):
                self.globals.veexOtn.sets.errorGenRate = float(paramList[0].head)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxErrType(self, parameters):
        '''**TX:ERRor:TYPE?** -
        Query the error type selected for the OTN protocol processor.
        '''
        self.globals.veexOtn.sets.update()
        if self.globals.veexOtn.sets.errorGenType in ScpiOtn.OtnErrorTypeTable.keys():
            response = ScpiOtn.OtnErrorTypeTable[self.globals.veexOtn.sets.errorGenType]
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setTxErrType(self, parameters):
        '''**TX:ERRor:TYPE:<error>** -
        Sets the error insertion type.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for key, value in ScpiOtn.OtnErrorTypeTable.items():
                if paramList[0].head.upper().startswith(value):
                    self.globals.veexOtn.sets.errorGenType = key
                    return None
            response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxFec(self, parameters):
        '''**TX:FEC?** -
        Query the receive FEC mode setting.
        '''
        self.globals.veexOtn.sets.update()
        if self.globals.veexOtn.sets.txFecDisable:
            response = b"DISABLED"
        else:
            response = b"ENABLED"
        return response

    def setTxFec(self, parameters):
        '''**TX:FEC <DISABLED|ENABLED>** -
        Sets the state of the transmit Forward Error Correction (FEC) mode.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.txFecDisable = True
            elif paramList[0].head.upper().startswith(b"ENABLED"):
                self.globals.veexOtn.sets.txFecDisable = False
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxMuxFlexRate(self, parameters):
        '''**TX:FLEXRATE?** -
        Query the transmit Data Rate for ODU Flex Mappings, in Mbps.
        '''
        self.globals.veexOtn.sets.update()
        return b"%0.9f Mbps" % (float(self.globals.veexOtn.sets.txFlexDataRate) / 1.0e6,)

    def setTxMuxFlexRate(self, parameters):
        '''**TX:FLEXRATE <rate>** -
        Sets the transmit Data Rate for ODU Flex Mappings, in Mbps.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if ParseUtils.isFloatSdh(paramList[0].head):
                fInValue = float(paramList[0].head)
                if fInValue > 10.0:
                    self.globals.veexOtn.sets.txFlexDataRate = fInValue * 1.0e6
                else:
                    response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
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
        self.globals.veexOtn.sets.update()
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

    def getTxInterface(self, parameters):
        '''**TX:INTerface?** -
        Query the selected transmit interface.
        '''
        self.globals.veexOtn.sets.update()
        if self.globals.veexOtn.sets.txInterface in ScpiOtn.InterfaceTable.keys():
            response = ScpiOtn.InterfaceTable[self.globals.veexOtn.sets.txInterface]
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setTxInterface(self, parameters):
        '''**TX:INTerface:<interface>** -
        Sets the transmit OTN, ETHERNET, FIBRE CHANNEL or CPRI interface rate/speed/type, for the specified Module types.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for key, value in ScpiOtn.InterfaceTable.items():
                if paramList[0].head.upper().startswith(value):
                    self.globals.veexOtn.sets.txInterface = key
                    return None
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
        self.globals.veexPhy.sets.update()
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
        self.globals.veexOtn.sets.update()
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

    def getTxLaserType(self, parameters):
        '''**TX:LASERTYPE?** -
        Query the lasers transmit wavelength, in nm.
        '''
        self.globals.veexOtn.sets.update()
        self.globals.veexOtn.stats.update()
        response = b""
#        if (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_2P5G_OTU_1) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_2P5G_ETHERNET) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_1G_ETHERNET) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_100M_ETHERNET) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_10M_ETHERNET) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_1G_FIBRECHAN) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_2G_FIBRECHAN) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_4G_FIBRECHAN) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_614M_CPRI_1) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_1P2G_CPRI_2) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_2P5G_CPRI_3) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_3G_CPRI_4):
#            freqWave = float(self.globals.veexOtn.stats.txWavelength) / 1000.0
#        elif (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_10000T_ETHERNET) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_5000T_ETHERNET) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_2500T_ETHERNET) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_1000T_ETHERNET) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_100T_ETHERNET) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_10T_ETHERNET):
#            freqWave = float(self.globals.veexOtn.stats.txWavelength) / 1000.0
#            if (freqWave < 0.0009) or (freqWave > 0.0011):
#                freqWave = 0;
#        elif (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_10G_OTU_2) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_10G_ETHERNET) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_11G_OTU_2E) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_11G_OTU_1E) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_8G_FIBRECHAN) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_10G_FIBRECHAN) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_11G_OTU_2F) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_11G_OTU_1F) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_5G_CPRI_5) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_6G_CPRI_6) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_8G_CPRI_7A) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_9G_CPRI_7) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_10G_CPRI_8) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_12G_CPRI_9) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_24G_CPRI_10):
#            # Double Check : txWavelengthPortC 
#            freqWave = float(self.globals.veexOtn.stats.txWavelength) / 1000.0
#        elif (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_43G_OTU_3) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_112G_CFP_OTU_4) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_112G_OTU_4) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_112G_QSFP56_OTU_4) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_44G_OTU_3E1) or \
#             (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_44G_OTU_3E2):
#            # Double Check : txWavelengthPortD
#            freqWave = float(self.globals.veexOtn.stats.txWavelength) / 1000.0

        freqWave = self.globals.veexOtn.stats.txWavelength
        if freqWave > -0.0001 and freqWave < 0.0001:
            if self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_OFF:
                response = b"Not Assigned"
            elif (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_10000T_ETHERNET) or \
                 (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_5000T_ETHERNET) or \
                 (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_2500T_ETHERNET) or \
                 (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_1000T_ETHERNET) or \
                 (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_100T_ETHERNET) or \
                 (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_10T_ETHERNET):   
                response = b"Electrical LAN"
            else:
                response = b"Unknown nm"
        elif freqWave > 0.0009 and freqWave < 0.0011:
            response = b"No Module"
        elif freqWave > 0.0019 and freqWave < 0.0021:
            response = b"MLD"
        else:
            response = b"%0.3f nm" % freqWave
        if self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_OFF:
            response = b"Not Assigned"
        return response

    def getTxMapping(self, parameters):
        '''**TX:MAPping?** -
        Query the selected transmit mapping for the OTN processor.
        '''
        self.globals.veexOtn.sets.update()
        paramCount = 1
        response = b""
        if self.globals.veexOtn.sets.odtu3TxMapping != veexlib.OTN_MAP_NONE:
            paramCount += 1
        if self.globals.veexOtn.sets.odtu2TxMapping != veexlib.OTN_MAP_NONE:
            paramCount += 1
        if self.globals.veexOtn.sets.odtu1TxMapping != veexlib.OTN_MAP_NONE:
            paramCount += 1
        for i in range(paramCount):
            if len(response) == 0:
                mapping = self.globals.veexOtn.sets.txMapping
            elif self.globals.veexOtn.sets.odtu3TxMapping != veexlib.OTN_MAP_NONE:
                mapping = self.globals.veexOtn.sets.odtu3TxMapping
            elif self.globals.veexOtn.sets.odtu2TxMapping != veexlib.OTN_MAP_NONE:
                mapping = self.globals.veexOtn.sets.odtu2TxMapping
            elif self.globals.veexOtn.sets.odtu1TxMapping != veexlib.OTN_MAP_NONE:
                mapping = self.globals.veexOtn.sets.odtu1TxMapping

            if mapping == veexlib.OTN_MAP_UNFRAMED_BERT:
                response += b"UNFRAMED_BERT"
            elif mapping == veexlib.OTN_MAP_SONET_SDH_ASYNC:
                response += b"SONETSDH_ASYNC"
            elif mapping == veexlib.OTN_MAP_SONET_SDH_SYNC:
                response += b"SONETSDH_SYNC"
            elif mapping == veexlib.OTN_MAP_OPU_PRBS:
                response += b"PRBS"
            elif mapping == veexlib.OTN_MAP_OPU_NULL:
                response += b"NULL_CLIENT"
            elif mapping == veexlib.OTN_MAP_OPU_GFP:
                response += b"OPU_GFP"
            elif mapping == veexlib.OTN_MAP_OPU_WAN:
                response += b"OPU_WAN"
            elif mapping == veexlib.OTN_MAP_ETHERNET:
                response += b"OPU_LAN"
            elif mapping == veexlib.OTN_MAP_ODTU_12_PT_20:
                if self.globals.veexOtn.sets.isTxMultiChanMapping == True:
                    response += b"MULTI_ODTU12"
                else:
                    response += b"ODTU12"
            elif mapping == veexlib.OTN_MAP_ODU2E_ETHERNET_SYNC:
                response += b"OPU_LAN_SYNC"
            elif mapping == veexlib.OTN_MAP_ODU2E_ETHERNET_ASYNC:
                response += b"OPU_LAN_ASYNC"    
            elif mapping == veexlib.OTN_MAP_ODTU_13_PT_20:
                if self.globals.veexOtn.sets.isTxMultiChanMapping == True:
                    response += b"MULTI_ODTU13"
                else:
                    response += b"ODTU13"
            elif mapping == veexlib.OTN_MAP_ODTU_23_PT_20:
                if self.globals.veexOtn.sets.isTxMultiChanMapping == True:
                    response += b"MULTI_ODTU23"
                else:
                    response += b"ODTU23"  
            elif mapping == veexlib.OTN_MAP_ODTU_01_PT_20:
                if self.globals.veexOtn.sets.isTxMultiChanMapping == True:
                    response += b"MULTI_ODTU01"
                else:
                    response += b"ODTU01"  
            elif mapping == veexlib.OTN_MAP_ODU_FLEX_PT_21:
                response += b"ODUFLEX"
            elif mapping == veexlib.OTN_MAP_ODU3E_ETHERNET:
                response += b"QUAD_10G_LAN"
            elif mapping == veexlib.OTN_MAP_OPU_GFP_EXTENDED:
                response += b"GFP_10G_LAN"
            elif mapping == veexlib.OTN_MAP_FIBRECHAN:
                response += b"FIBRECHAN"
            elif mapping == veexlib.OTN_MAP_ODU2F_FIBRECHAN_SYNC:
                response += b"OPU_FIBRECHAN_SYNC"
            elif mapping == veexlib.OTN_MAP_ODU2F_FIBRECHAN_ASYNC:
                response += b"OPU_FIBRECHAN_ASYNC"
            elif mapping == veexlib.OTN_MAP_ODTU_02_PT_21:
                if self.globals.veexOtn.sets.isTxMultiChanMapping == True:
                    response += b"MULTI_ODTU02"
                else:
                    response += b"ODTU02" 
            elif mapping == veexlib.OTN_MAP_ODTU_03_PT_21:
                if self.globals.veexOtn.sets.isTxMultiChanMapping == True:
                    response += b"MULTI_ODTU03"
                else:
                    response += b"ODTU03" 
            elif mapping == veexlib.OTN_MAP_ODTU_04_PT_21:
                if self.globals.veexOtn.sets.isTxMultiChanMapping == True:
                    response += b"MULTI_ODTU04"
                else:
                    response += b"ODTU04" 
            elif mapping == veexlib.OTN_MAP_OPU_40G_ETHERNET:
                response += b"OPU_41G_LAN"
            elif mapping == veexlib.OTN_MAP_OPU_100G_ETHERNET:
                response += b"OPU_103G_LAN"
            elif mapping == veexlib.OTN_MAP_ODTU_14_PT_21:
                if self.globals.veexOtn.sets.isTxMultiChanMapping == True:
                    response += b"MULTI_ODTU14"
                else:
                    response += b"ODTU14" 
            elif mapping == veexlib.OTN_MAP_ODTU_24_PT_21:
                if self.globals.veexOtn.sets.isTxMultiChanMapping == True:
                    response += b"MULTI_ODTU24"
                else:
                    response += b"ODTU24"         
            elif mapping == veexlib.OTN_MAP_ODTU_34_PT_21:
                response += b"ODTU34"
            elif mapping == veexlib.OTN_MAP_ODTU_2E3_PT_21:
                response += b"ODTU2E3"
            elif mapping == veexlib.OTN_MAP_ODTU_2E4_PT_21:
                if self.globals.veexOtn.sets.isTxMultiChanMapping == True:
                    response += b"MULTI_ODTU2E4"
                else:
                    response += b"ODTU2E4"
            
            elif mapping == veexlib.OTN_MAP_ODTU_12_PT_21:
                if self.globals.veexOtn.sets.isTxMultiChanMapping == True:
                    response += b"MULTI_ODTU12_PT_21"
                else:
                    response += b"ODTU12_PT_21"   
            elif mapping == veexlib.OTN_MAP_ODTU_13_PT_21:
                if self.globals.veexOtn.sets.isTxMultiChanMapping == True:
                    response += b"MULTI_ODTU13_PT_21"
                else:
                    response += b"ODTU13_PT_21"   
            elif mapping == veexlib.OTN_MAP_ODTU_23_PT_21:
                if self.globals.veexOtn.sets.isTxMultiChanMapping == True:
                    response += b"MULTI_ODTU23_PT_21"
                else:
                    response += b"ODTU23_PT_21"   
            elif mapping == veexlib.OTN_MAP_OPU_40G_ETHERNET_PRBS:
                response += b"OPU_41G_PRBS"
            elif mapping == veexlib.OTN_MAP_OPU_40G_ETHERNET_NULL:
                response += b"OPU_41G_NULL"
            else:
                return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
            if i != paramCount - 1:
                response += b","
        return response

    def setTxMapping(self, parameters):
        '''**TX:MAPping:<mapping>** -
        Sets the transmit mapping, for the specified Circuit Pack types,
        based on the unit!/s licensed configuration.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            txMapping = veexlib.OTN_MAP_NONE
            odtu1Mapping = veexlib.OTN_MAP_NONE
            odtu2Mapping = veexlib.OTN_MAP_NONE
            odtu3Mapping = veexlib.OTN_MAP_NONE
            muxTxIsParallelMapping = False
            for paramCount in range(len(paramList)):
                if paramList[paramCount].head.upper().startswith(b"UNFRAMED_BERT"):
                    mapping = veexlib.OTN_MAP_UNFRAMED_BERT
                elif paramList[paramCount].head.upper().startswith(b"SONETSDH_ASYNC"):
                    mapping = veexlib.OTN_MAP_SONET_SDH_ASYNC
                elif paramList[paramCount].head.upper().startswith(b"SONETSDH_SYNC"):
                    mapping = veexlib.OTN_MAP_SONET_SDH_SYNC
                elif paramList[paramCount].head.upper().startswith(b"PRBS"):
                    mapping = veexlib.OTN_MAP_OPU_PRBS
                elif paramList[paramCount].head.upper().startswith(b"NULL_CLIENT"):
                    mapping = veexlib.OTN_MAP_OPU_NULL
                elif paramList[paramCount].head.upper().startswith(b"OPU_GFP"):
                    mapping = veexlib.OTN_MAP_OPU_GFP
                elif paramList[paramCount].head.upper().startswith(b"OPU_WAN"):
                    mapping = veexlib.OTN_MAP_OPU_WAN
                elif paramList[paramCount].head.upper().startswith(b"OPU_LAN"):
                    mapping = veexlib.OTN_MAP_ETHERNET
                elif paramList[paramCount].head.upper().startswith(b"ODTU12_PT_21"):
                    mapping = veexlib.OTN_MAP_ODTU_12_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU12"):
                    mapping = veexlib.OTN_MAP_ODTU_12_PT_20
                elif paramList[paramCount].head.upper().startswith(b"OPU_LAN_SYNC"):
                    mapping = veexlib.OTN_MAP_ODU2E_ETHERNET_SYNC
                elif paramList[paramCount].head.upper().startswith(b"OPU_LAN_ASYNC"):
                    mapping = veexlib.OTN_MAP_ODU2E_ETHERNET_ASYNC
                elif paramList[paramCount].head.upper().startswith(b"ODTU13_PT_21"):
                    mapping = veexlib.OTN_MAP_ODTU_13_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU13"):
                    mapping = veexlib.OTN_MAP_ODTU_13_PT_20
                elif paramList[paramCount].head.upper().startswith(b"ODTU23_PT_21"):
                    mapping = veexlib.OTN_MAP_ODTU_23_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU23"):
                    mapping = veexlib.OTN_MAP_ODTU_23_PT_20
                elif paramList[paramCount].head.upper().startswith(b"ODTU01"):
                    mapping = veexlib.OTN_MAP_ODTU_01_PT_20
                elif paramList[paramCount].head.upper().startswith(b"ODUFLEX"):
                    mapping = veexlib.OTN_MAP_ODU_FLEX_PT_21
                elif paramList[paramCount].head.upper().startswith(b"QUAD_10G_LAN"):
                    mapping = veexlib.OTN_MAP_ODU3E_ETHERNET
                elif paramList[paramCount].head.upper().startswith(b"GFP_10G_LAN"):
                    mapping = veexlib.OTN_MAP_OPU_GFP_EXTENDED
                elif paramList[paramCount].head.upper().startswith(b"FIBRECHAN"):
                    mapping = veexlib.OTN_MAP_FIBRECHAN
                elif paramList[paramCount].head.upper().startswith(b"OPU_FIBRECHAN_SYNC"):
                    mapping = veexlib.OTN_MAP_ODU2F_FIBRECHAN_SYNC
                elif paramList[paramCount].head.upper().startswith(b"OPU_FIBRECHAN_ASYNC"):
                    mapping = veexlib.OTN_MAP_ODU2F_FIBRECHAN_ASYNC
                elif paramList[paramCount].head.upper().startswith(b"ODTU02"):
                    mapping = veexlib.OTN_MAP_ODTU_02_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU03"):
                    mapping = veexlib.OTN_MAP_ODTU_03_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU04"):
                    mapping = veexlib.OTN_MAP_ODTU_04_PT_21
                elif paramList[paramCount].head.upper().startswith(b"4G_FIBRECHAN"):
                    mapping = veexlib.OTN_MAP_ODU_FLEX_4G_FC
                elif paramList[paramCount].head.upper().startswith(b"8_5G_FIBRECHAN"):
                    mapping = veexlib.OTN_MAP_ODU_FLEX_8G_FC
                elif paramList[paramCount].head.upper().startswith(b"OPU_41G_LAN"):
                    mapping = veexlib.OTN_MAP_OPU_40G_ETHERNET
                elif paramList[paramCount].head.upper().startswith(b"OPU_103G_LAN"):
                    mapping = veexlib.OTN_MAP_OPU_100G_ETHERNET
                elif paramList[paramCount].head.upper().startswith(b"ODTU14"):
                    mapping = veexlib.OTN_MAP_ODTU_14_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU24"):
                    mapping = veexlib.OTN_MAP_ODTU_24_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU34"):
                    mapping = veexlib.OTN_MAP_ODTU_34_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU2E3"):
                    mapping = veexlib.OTN_MAP_ODTU_2E3_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU2E3"):
                    mapping = veexlib.OTN_MAP_ODTU_2E4_PT_21
                elif paramList[paramCount].head.upper().startswith(b"OPU_41G_PRBS"):
                    mapping = veexlib.OTN_MAP_OPU_40G_ETHERNET_PRBS
                elif paramList[paramCount].head.upper().startswith(b"OPU_41G_NULL"):
                    mapping = veexlib.OTN_MAP_OPU_40G_ETHERNET_NULL
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU03"):
                    mapping = veexlib.OTN_MAP_ODTU_03_PT_21
                    muxTxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU13_PT_21"):
                    mapping = veexlib.OTN_MAP_ODTU_13_PT_21
                    muxTxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU13"):
                    mapping = veexlib.OTN_MAP_ODTU_13_PT_21
                    muxTxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU23_PT_21"):
                    mapping = veexlib.OTN_MAP_ODTU_23_PT_21
                    muxTxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU23"):
                    mapping = veexlib.OTN_MAP_ODTU_23_PT_20
                    muxTxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU04"):
                    mapping = veexlib.OTN_MAP_ODTU_04_PT_21
                    muxTxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU14"):
                    mapping = veexlib.OTN_MAP_ODTU_14_PT_21
                    muxTxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU24"):
                    mapping = veexlib.OTN_MAP_ODTU_24_PT_21
                    muxTxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU2E4"):
                    mapping = veexlib.OTN_MAP_ODTU_2E4_PT_21
                    muxTxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU01"):
                    mapping = veexlib.OTN_MAP_ODTU_01_PT_20
                    muxTxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU02"):
                    mapping = veexlib.OTN_MAP_ODTU_02_PT_21
                    muxTxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU12_PT_21"):
                    mapping = veexlib.OTN_MAP_ODTU_12_PT_21
                    muxTxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU12"):
                    mapping = veexlib.OTN_MAP_ODTU_12_PT_20
                    muxTxIsParallelMapping = True
                else:
                    return self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)

                if paramCount == 0:
                    txMapping = mapping
                elif paramCount == 1:
                    odtu3Mapping = mapping
                elif paramCount == 2:
                    odtu2Mapping = mapping
                elif paramCount == 3:
                    odtu1Mapping = mapping
            if len(paramList) == 1 and txMapping != veexlib.OTN_MAP_ODTU_34_PT_21:
                if (txMapping == veexlib.OTN_MAP_ODTU_24_PT_21) or \
                   (txMapping == veexlib.OTN_MAP_ODTU_23_PT_21) or \
                   (txMapping == veexlib.OTN_MAP_ODTU_23_PT_20):
                    odtu2Mapping = odtu3Mapping;
                else:
                    odtu1Mapping = odtu3Mapping;
                odtu3Mapping = veexlib.OTN_MAP_NONE
            elif len(paramList) == 2 and txMapping != veexlib.OTN_MAP_ODTU_34_PT_21:    
                if (txMapping == veexlib.OTN_MAP_ODTU_24_PT_21) or \
                   (txMapping == veexlib.OTN_MAP_ODTU_23_PT_21) or \
                   (txMapping == veexlib.OTN_MAP_ODTU_23_PT_20):
                    odtu1Mapping = odtu2Mapping;
                    odtu2Mapping = odtu3Mapping;
                    odtu3Mapping = veexlib.OTN_MAP_NONE
            elif len(paramList) == 2 and txMapping == veexlib.OTN_MAP_ODTU_34_PT_21:
                if (odtu3Mapping == veexlib.OTN_MAP_ODTU_13_PT_20) or \
                   (odtu3Mapping == veexlib.OTN_MAP_ODTU_13_PT_21):
                    odtu1Mapping = odtu2Mapping;
                    odtu2Mapping = veexlib.OTN_MAP_NONE 
            elif len(paramList) == 2 and txMapping == veexlib.OTN_MAP_ODTU_12_PT_21:
                # Special case for old interface 'PB_OTN_MAP_ODTU_012_PT_21', change to mutli-level
                if odtu3Mapping == veexlib.OTN_MAP_ODTU_01_PT_20:
                    odtu1Mapping = odtu3Mapping
                    odtu3Mapping = veexlib.OTN_MAP_NONE
            elif len(paramList) == 2 and txMapping == veexlib.OTN_MAP_ODTU_12_PT_20:
                # Special case for old interface 'PB_OTN_MAP_ODTU_012_PT_20', change to mutli-level
                if odtu3Mapping == veexlib.OTN_MAP_ODTU_01_PT_20:
                    odtu1Mapping = odtu3Mapping
                    odtu3Mapping = veexlib.OTN_MAP_NONE
                
            # Double Check : Is it need to handle the presend route here?
            if muxTxIsParallelMapping == False:
                self.globals.veexOtn.sets.setTxMapping(txMapping,odtu3Mapping,odtu2Mapping,odtu1Mapping)
            else:
                self.globals.veexOtn.sets.setTxMultiChanMapping(txMapping)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxMultiChanPattern(self, parameters):
        '''**TX:MCPATT?** -
        Query the ODU Multi-Channel mapping structures for the ODU-n Add/Drop MUX mapping.
        '''
        self.globals.veexOtn.sets.update()
        response = b"TBD"
#        slots = 1
#        slotSpaces = 1
#        if (self.globals.veexOtn.sets.txMapping == veexlib.OTN_MAP_ODTU_12_PT_21) or \
#           (self.globals.veexOtn.sets.txMapping == veexlib.OTN_MAP_ODTU_13_PT_21):
#            slots = 2
#        elif (self.globals.veexOtn.sets.txMapping == veexlib.OTN_MAP_ODTU_23_PT_21) or \
#             (self.globals.veexOtn.sets.txMapping == veexlib.OTN_MAP_ODTU_2E3_PT_21) or \
#             (self.globals.veexOtn.sets.txMapping == veexlib.OTN_MAP_ODTU_2E4_PT_21):
#            slots = 8
#        if (self.globals.veexOtn.sets.txMapping == veexlib.OTN_MAP_ODTU_12_PT_21) or \
#           (self.globals.veexOtn.sets.txMapping == veexlib.OTN_MAP_ODTU_02_PT_21):
#            slotSpaces = 8
#        elif (self.globals.veexOtn.sets.txMapping == veexlib.OTN_MAP_ODTU_13_PT_21) or \
#             (self.globals.veexOtn.sets.txMapping == veexlib.OTN_MAP_ODTU_2E3_PT_21) or \
#             (self.globals.veexOtn.sets.txMapping == veexlib.OTN_MAP_ODTU_03_PT_21) or \
#             (self.globals.veexOtn.sets.txMapping == veexlib.OTN_MAP_ODTU_23_PT_21):
#            slotSpaces = 32
#        elif (self.globals.veexOtn.sets.txMapping == veexlib.OTN_MAP_ODTU_2E4_PT_21):
#            slotSpaces = 80

        return response

    def setTxMultiChanPattern(self, parameters):
        '''**TX:MCPATT:<structure>** -
        Sets entire transmit ODU-n Multi-Channel mapping structures for multi-channel ODTU mappings,
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = b"TBD"

        return response

    def txGetOhIntrAct(self, parameters):
        '''**TX:OH:INTRusive:ACT?** -
        Query whether the ACT is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM_ACT]:
            response = b"YES"
        return response

    def txGetOhIntrApspcc(self, parameters):
        '''**TX:OH:INTRusive:APSPCC?** -
        Query whether the APSPCC is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_APS_PCC]:
            response = b"YES"
        return response

    def txGetOhIntrExp(self, parameters):
        '''**TX:OH:INTRusive:EXP?** -
        Query whether the EXP is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_EXP]:
            response = b"YES"
        return response

    def txGetOhIntrFas(self, parameters):
        '''**TX:OH:INTRusive:FAS?** -
        Query whether the FAS is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_FAS]:
            response = b"YES"
        return response

    def txGetOhIntrFtfl(self, parameters):
        '''**TX:OH:INTRusive:FTFL?** -
        Query whether the FTFL is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_FTFL]:
            response = b"YES"
        return response

    def txGetOhIntrGcc0(self, parameters):
        '''**TX:OH:INTRusive:GCC0?** -
        Query whether the GCC0 is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_GCC0]:
            response = b"YES"
        return response

    def txGetOhIntrGcc1(self, parameters):
        '''**TX:OH:INTRusive:GCC1?** -
        Query whether the GCC1 is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_GCC1]:
            response = b"YES"
        return response

    def txGetOhIntrGcc2(self, parameters):
        '''**TX:OH:INTRusive:GCC2?** -
        Query whether the GCC2 is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_GCC2]:
            response = b"YES"
        return response

    def txGetOhIntrJcnjo(self, parameters):
        '''**TX:OH:INTRusive:JCNJO?** -
        Query whether the JCNJO is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_OPU_JC_NJO]:
            response = b"YES"
        return response

    def txGetOhIntrMfas(self, parameters):
        '''**TX:OH:INTRusive:MFAS?** -
        Query whether the MFAS is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_MFAS]:
            response = b"YES"
        return response

    def txGetOhIntrOdures1(self, parameters):
        '''**TX:OH:INTRusive:ODURES1?** -
        Query whether the ODURES1 is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_RES1]:
            response = b"YES"
        return response

    def txGetOhIntrOdures2(self, parameters):
        '''**TX:OH:INTRusive:ODURES2?** -
        Query whether the ODURES2 is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_RES2]:
            response = b"YES"
        return response

    def txGetOhIntrOpures1(self, parameters):
        '''**TX:OH:INTRusive:OPURES?** -
        Query whether the OPURES is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_OPU_RES]:
            response = b"YES"
        return response

    def txGetOhIntrOtures(self, parameters):
        '''**TX:OH:INTRusive:OTURES?** -
        Query whether the OTURES is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_RES]:
            response = b"YES"
        return response

    def txGetOhIntrPm(self, parameters):
        '''**TX:OH:INTRusive:PM?** -
        Query whether the PM is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_PM]:
            response = b"YES"
        return response

    def txGetOhIntrPsi(self, parameters):
        '''**TX:OH:INTRusive:PSI?** -
        Query whether the PSI is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_OPU_PSI]:
            response = b"YES"
        return response

    def txGetOhIntrSm(self, parameters):
        '''**TX:OH:INTRusive:SM?** -
        Query whether the SM is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_SM]:
            response = b"YES"
        return response

    def txGetOhIntrTcm1(self, parameters):
        '''**TX:OH:INTRusive:TCM1?** -
        Query whether the TCM1 is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM1]:
            response = b"YES"
        return response

    def txGetOhIntrTcm2(self, parameters):
        '''**TX:OH:INTRusive:TCM2?** -
        Query whether the TCM2 is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM2]:
            response = b"YES"
        return response

    def txGetOhIntrTcm3(self, parameters):
        '''**TX:OH:INTRusive:TCM3?** -
        Query whether the TCM3 is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM3]:
            response = b"YES"
        return response

    def txGetOhIntrTcm4(self, parameters):
        '''**TX:OH:INTRusive:TCM4?** -
        Query whether the TCM4 is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM4]:
            response = b"YES"
        return response

    def txGetOhIntrTcm5(self, parameters):
        '''**TX:OH:INTRusive:TCM5?** -
        Query whether the TCM5 is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM5]:
            response = b"YES"
        return response

    def txGetOhIntrTcm6(self, parameters):
        '''**TX:OH:INTRusive:TCM6?** -
        Query whether the TCM1 is set to Intrusive (YES) or Non-Intrusive (NO).
        '''
        self.globals.veexOtn.sets.update()
        response = b"NO"
        if self.globals.veexOtn.sets.txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM6]:
            response = b"YES"
        return response

    def txSetOhIntrAct(self, parameters):
        '''**TX:OH:INTRusive:ACT <YES|NO>** -
        When Passthru mode is ON, the ACT overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM_ACT] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM_ACT] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrApspcc(self, parameters):
        '''**TX:OH:INTRusive:APSPCC <YES|NO>** -
        When Passthru mode is ON, the APSPCC overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_APS_PCC] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_APS_PCC] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrExp(self, parameters):
        '''**TX:OH:INTRusive:EXP <YES|NO>** -
        When Passthru mode is ON, the EXP overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_EXP] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_EXP] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrFas(self, parameters):
        '''**TX:OH:INTRusive:FAS <YES|NO>** -
        When Passthru mode is ON, the FAS overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_FAS] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_FAS] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrFtfl(self, parameters):
        '''**TX:OH:INTRusive:FTFL <YES|NO>** -
        When Passthru mode is ON, the FTFL overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_FTFL] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_FTFL] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrGcc0(self, parameters):
        '''**TX:OH:INTRusive:GCC0 <YES|NO>** -
        When Passthru mode is ON, the GCC0 overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_GCC0] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_GCC0] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrGcc1(self, parameters):
        '''**TX:OH:INTRusive:GCC1 <YES|NO>** -
        When Passthru mode is ON, the GCC1 overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_GCC1] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_GCC1] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrGcc2(self, parameters):
        '''**TX:OH:INTRusive:GCC2 <YES|NO>** -
        When Passthru mode is ON, the GCC2 overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_GCC2] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_GCC2] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrJcnjo(self, parameters):
        '''**TX:OH:INTRusive:JCNJO <YES|NO>** -
        When Passthru mode is ON, the JCNJO overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OPU_JC_NJO] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OPU_JC_NJO] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrMfas(self, parameters):
        '''**TX:OH:INTRusive:MFAS <YES|NO>** -
        When Passthru mode is ON, the MFAS overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_MFAS] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_MFAS] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrOdures1(self, parameters):
        '''**TX:OH:INTRusive:ODURES1 <YES|NO>** -
        When Passthru mode is ON, the ODURES1 overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_RES1] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_RES1] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrOdures2(self, parameters):
        '''**TX:OH:INTRusive:ODURES2 <YES|NO>** -
        When Passthru mode is ON, the ODURES2 overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_RES2] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_RES2] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrOpures1(self, parameters):
        '''**TX:OH:INTRusive:OPURES <YES|NO>** -
        When Passthru mode is ON, the OPURES overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OPU_RES] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OPU_RES] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrOtures(self, parameters):
        '''**TX:OH:INTRusive:OTURES <YES|NO>** -
        When Passthru mode is ON, the OTURES overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_RES] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_RES] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrPm(self, parameters):
        '''**TX:OH:INTRusive:PM <YES|NO>** -
        When Passthru mode is ON, the PM overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_PM] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_PM] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrPsi(self, parameters):
        '''**TX:OH:INTRusive:PSI <YES|NO>** -
        When Passthru mode is ON, the PSI overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OPU_PSI] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OPU_PSI] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrSm(self, parameters):
        '''**TX:OH:INTRusive:SM <YES|NO>** -
        When Passthru mode is ON, the SM overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_SM] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_OTU_SM] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrTcm1(self, parameters):
        '''**TX:OH:INTRusive:TCM1 <YES|NO>** -
        When Passthru mode is ON, the TCM1 overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM1] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM1] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrTcm2(self, parameters):
        '''**TX:OH:INTRusive:TCM2 <YES|NO>** -
        When Passthru mode is ON, the TCM2 overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM2] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM2] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrTcm3(self, parameters):
        '''**TX:OH:INTRusive:TCM3 <YES|NO>** -
        When Passthru mode is ON, the TCM3 overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM3] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM3] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrTcm4(self, parameters):
        '''**TX:OH:INTRusive:TCM4 <YES|NO>** -
        When Passthru mode is ON, the TCM4 overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM4] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM4] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrTcm5(self, parameters):
        '''**TX:OH:INTRusive:TCM5 <YES|NO>** -
        When Passthru mode is ON, the TCM5 overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM5] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM5] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhIntrTcm6(self, parameters):
        '''**TX:OH:INTRusive:TCM6 <YES|NO>** -
        When Passthru mode is ON, the TCM6 overhead bytes can be set to Intrusive or Non-Intrusive.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper().startswith(b"YES"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM6] = True
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            elif paramList[0].head.upper().startswith(b"NO"):
                txIntrudeOn = self.globals.veexOtn.sets.txIntrudeOn
                txIntrudeOn[veexlib.OTN_INTRUDE_ON_ODU_TCM6] = False
                self.globals.veexOtn.sets.txIntrudeOn = txIntrudeOn
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txOhOdu2Aps1(self, parameters):
        '''**TX:OH:ODU:APS1?** -
        Query the selected ODU APS/PCC1 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_APS_PCC_1]

    def txOhOdu2Aps2(self, parameters):
        '''**TX:OH:ODU:APS2?** -
        Query the selected ODU APS/PCC2 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_APS_PCC_2]

    def txOhOdu2Aps3(self, parameters):
        '''**TX:OH:ODU:APS3?** -
        Query the selected ODU APS/PCC3 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_APS_PCC_3]

    def txOhOdu2Aps4(self, parameters):
        '''**TX:OH:ODU:APS4?** -
        Query the selected ODU APS/PCC4 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_APS_PCC_4]

    def txOhOdu1Bei(self, parameters):
        '''**TX:OH:ODU:BEI?** -
        Query the selected ODU BEI overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_PM_BEI]

    def txOhOdu1BfFault(self, parameters):
        '''**TX:OH:ODU:BFTFL:FAULT?** -
        Query the selected ODU BFTFL:FAULT overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduBackwardFtflFault

    def txOhOdu1BfOi(self, parameters):
        '''**TX:OH:ODU:BFTFL:OI?** -
        Query the selected ODU BFTFL:OI overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return self.globals.veexOtn.sets.oduBackwardFtflOI.encode()[:9]

    def txOhOdu1BfOs(self, parameters):
        '''**TX:OH:ODU:BFTFL:OS?** -
        Query the selected ODU BFTFL:OS overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return self.globals.veexOtn.sets.oduBackwardFtflOS.encode()[:118]

    def txOhOdu1FfFault(self, parameters):
        '''**TX:OH:ODU:FFTFL:FAULT?** -
        Query the selected ODU FFTFL:FAULT overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduForwardFtflFault

    def txOhOdu1FfOi(self, parameters):
        '''**TX:OH:ODU:FFTFL:OI?** -
        Query the selected ODU FFTFL:OI overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return self.globals.veexOtn.sets.oduForwardFtflOI.encode()[:9]

    def txOhOdu1FfOs(self, parameters):
        '''**TX:OH:ODU:FFTFL:OS?** -
        Query the selected ODU FFTFL:OS overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return self.globals.veexOtn.sets.oduForwardFtflOS.encode()[:118]

    def txOhOdu1Dapi(self, parameters):
        '''**TX:OH:ODU:DAPI?** -
        Query the selected ODU DAPI overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduPmTtiDapi.encode()[:15]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhOdu2Exp1(self, parameters):
        '''**TX:OH:ODU:EXP1?** -
        Query the selected ODU EXP1 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_EXP_1]

    def txOhOdu2Exp2(self, parameters):
        '''**TX:OH:ODU:EXP2?** -
        Query the selected ODU EXP2 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_EXP_2]

    def txOhOdu2Gcc11(self, parameters):
        '''**TX:OH:ODU:GCC11?** -
        Query the selected ODU GCC11 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_GCC1_1]

    def txOhOdu2Gcc12(self, parameters):
        '''**TX:OH:ODU:GCC12?** -
        Query the selected ODU GCC12 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_GCC1_2]

    def txOhOdu2Gcc21(self, parameters):
        '''**TX:OH:ODU:GCC21?** -
        Query the selected ODU GCC21 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_GCC2_1]

    def txOhOdu2Gcc22(self, parameters):
        '''**TX:OH:ODU:GCC22?** -
        Query the selected ODU GCC22 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_GCC2_2]

    def txOhOdu2Res1(self, parameters):
        '''**TX:OH:ODU:RES1?** -
        Query the selected ODU RES1 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_RES_1]

    def txOhOdu2Res2(self, parameters):
        '''**TX:OH:ODU:RES2?** -
        Query the selected ODU RES2 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_RES_2]

    def txOhOdu2Res3(self, parameters):
        '''**TX:OH:ODU:PMANDTCM?** -
        Query the selected ODU PMANDTCM overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_RES_3]

    def txOhOdu2Res4(self, parameters):
        '''**TX:OH:ODU:RES4?** -
        Query the selected ODU RES4 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_RES_4]

    def txOhOdu2Res5(self, parameters):
        '''**TX:OH:ODU:RES5?** -
        Query the selected ODU RES5 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_RES_5]

    def txOhOdu2Res6(self, parameters):
        '''**TX:OH:ODU:RES6?** -
        Query the selected ODU RES6 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_RES_6]

    def txOhOdu2Res7(self, parameters):
        '''**TX:OH:ODU:RES7?** -
        Query the selected ODU RES7 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_RES_7]

    def txOhOdu2Res8(self, parameters):
        '''**TX:OH:ODU:RES8?** -
        Query the selected ODU RES8 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_RES_8]

    def txOhOdu2Res9(self, parameters):
        '''**TX:OH:ODU:RES9?** -
        Query the selected ODU RES9 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_RES_9]

    def txOhOdu1Sapi(self, parameters):
        '''**TX:OH:ODU:SAPI?** -
        Query the selected ODU SAPI overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduPmTtiSapi.encode()[:15]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhOdu1Specific(self, parameters):
        '''**TX:OH:ODU:SPECIFIC?** -
        Query the selected ODU SPECIFIC overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return self.globals.veexOtn.sets.oduPmTtiSpecific.encode()[:15]

    def txOhOdu2TcmAct(self, parameters):
        '''**TX:OH:ODU:TCMACT?** -
        Query the selected ODU TCMACT overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_TCM_ACT]

    def txSetOhOdu2Aps1(self, parameters):
        '''**TX:OH:ODU:APS1:<value>** -
        Sets the transmit value for the specified ODU APS/PCC1 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_APS_PCC_1] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Aps2(self, parameters):
        '''**TX:OH:ODU:APS2:<value>** -
        Sets the transmit value for the specified ODU APS/PCC2 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_APS_PCC_2] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Aps3(self, parameters):
        '''**TX:OH:ODU:APS3:<value>** -
        Sets the transmit value for the specified ODU APS/PCC3 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_APS_PCC_3] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Aps4(self, parameters):
        '''**TX:OH:ODU:APS4:<value>** -
        Sets the transmit value for the specified ODU APS/PCC4 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_APS_PCC_4] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu1Bei(self, parameters):
        '''**TX:OH:ODU:BEI:<value>** -
        Sets the transmit value for the specified ODU BEI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_PM_BEI] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu1BfFault(self, parameters):
        '''**TX:OH:ODU:BFTFL:FAULT:<value>** -
        Sets the transmit value for the specified ODU BFTFL:FAULT overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.oduBackwardFtflFault = value
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu1BfOi(self, parameters):
        '''**TX:OH:ODU:BFTFL:OI:<value>** -
        Sets the transmit value for the specified ODU BFTFL:OI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 9:
                oduBackwardFtflOI = paramString[:9]
            else:
                oduBackwardFtflOI = paramString[:]
            self.globals.veexOtn.sets.oduBackwardFtflOI = oduBackwardFtflOI
        else:
            self.globals.veexOtn.sets.oduBackwardFtflOI = b""
        return response

    def txSetOhOdu1BfOs(self, parameters):
        '''**TX:OH:ODU:BFTFL:OS:<value>** -
        Sets the transmit value for the specified ODU BFTFL:OS overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 118:
                oduBackwardFtflOS = paramString[:118]
            else:
                oduBackwardFtflOS = paramString[:]
            self.globals.veexOtn.sets.oduBackwardFtflOS = oduBackwardFtflOS
        else:
            self.globals.veexOtn.sets.oduBackwardFtflOS = b""
        return response

    def txSetOhOdu1Dapi(self, parameters):
        '''**TX:OH:ODU:DAPI:<value>** -
        Sets the transmit value for the specified ODU DAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            self.globals.veexOtn.sets.oduPmTtiDapi = dapi
        else:
            self.globals.veexOtn.sets.oduPmTtiDapi = b""
        return response

    def txSetOhOdu2Exp1(self, parameters):
        '''**TX:OH:ODU:EXP1:<value>** -
        Sets the transmit value for the specified ODU EXP1 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_EXP_1] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Exp2(self, parameters):
        '''**TX:OH:ODU:EXP2:<value>** -
        Sets the transmit value for the specified ODU EXP2 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_EXP_2] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu1FfFault(self, parameters):
        '''**TX:OH:ODU:FFTFL:FAULT:<value>** -
        Sets the transmit value for the specified ODU FFTFL:FAULT overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.oduForwardFtflFault = value
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu1FfOi(self, parameters):
        '''**TX:OH:ODU:FFTFL:OI:<value>** -
        Sets the transmit value for the specified ODU FFTFL:OI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 9:
                oduForwardFtflOI = paramString[:9]
            else:
                oduForwardFtflOI = paramString[:]
            self.globals.veexOtn.sets.oduForwardFtflOI = oduForwardFtflOI
        else:
            self.globals.veexOtn.sets.oduForwardFtflOI = b""
        return response

    def txSetOhOdu1FfOs(self, parameters):
        '''**TX:OH:ODU:FFTFL:OS:<value>** -
        Sets the transmit value for the specified ODU FFTFL:OS overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 118:
                oduForwardFtflOS = paramString[:118]
            else:
                oduForwardFtflOS = paramString[:]
            self.globals.veexOtn.sets.oduForwardFtflOS = oduForwardFtflOS
        else:
            self.globals.veexOtn.sets.oduForwardFtflOS = b""
        return response

    def txSetOhOdu2Gcc11(self, parameters):
        '''**TX:OH:ODU:GCC11:<value>** -
        Sets the transmit value for the specified ODU GCC11 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_GCC1_1] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Gcc12(self, parameters):
        '''**TX:OH:ODU:GCC12:<value>** -
        Sets the transmit value for the specified ODU GCC12 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_GCC1_2] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Gcc21(self, parameters):
        '''**TX:OH:ODU:GCC21:<value>** -
        Sets the transmit value for the specified ODU GCC21 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_GCC2_1] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Gcc22(self, parameters):
        '''**TX:OH:ODU:GCC22:<value>** -
        Sets the transmit value for the specified ODU GCC22 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_GCC2_2] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Res1(self, parameters):
        '''**TX:OH:ODU:RES1:<value>** -
        Sets the transmit value for the specified ODU RES1 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_RES_1] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Res2(self, parameters):
        '''**TX:OH:ODU:RES2:<value>** -
        Sets the transmit value for the specified ODU RES2 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_RES_2] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Res3(self, parameters):
        '''**TX:OH:ODU:PMANDTCM:<value>** -
        Sets the transmit value for the specified ODU PMANDTCM overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_RES_3] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Res4(self, parameters):
        '''**TX:OH:ODU:RES4:<value>** -
        Sets the transmit value for the specified ODU RES4 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_RES_4] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Res5(self, parameters):
        '''**TX:OH:ODU:RES5:<value>** -
        Sets the transmit value for the specified ODU RES5 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_RES_5] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Res6(self, parameters):
        '''**TX:OH:ODU:RES6:<value>** -
        Sets the transmit value for the specified ODU RES6 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_RES_6] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Res7(self, parameters):
        '''**TX:OH:ODU:RES7:<value>** -
        Sets the transmit value for the specified ODU RES7 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_RES_7] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Res8(self, parameters):
        '''**TX:OH:ODU:RES8:<value>** -
        Sets the transmit value for the specified ODU RES8 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_RES_8] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu2Res9(self, parameters):
        '''**TX:OH:ODU:RES9:<value>** -
        Sets the transmit value for the specified ODU RES9 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_RES_9] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOdu1Sapi(self, parameters):
        '''**TX:OH:ODU:SAPI:<value>** -
        Sets the transmit value for the specified ODU SAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            self.globals.veexOtn.sets.oduPmTtiSapi = sapi
        else:
            self.globals.veexOtn.sets.oduPmTtiSapi = b""
        return response

    def txSetOhOdu1Specific(self, parameters):
        '''**TX:OH:ODU:SPECIFIC:<value>** -
        Sets the transmit value for the specified ODU SPECIFIC overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 32:
                sapi = paramString[:32]
            else:
                sapi = paramString[:]
            self.globals.veexOtn.sets.oduPmTtiSpecific = sapi
        else:
            self.globals.veexOtn.sets.oduPmTtiSpecific = b""
        return response

    def txSetOhOdu2TcmAct(self, parameters):
        '''**TX:OH:ODU:TCMACT:<value>** -
        Sets the transmit value for the specified ODU TCMACT overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_TCM_ACT] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txOhOpuPsi(self, parameters):
        '''**TX:OH:OPU:PSI0?** -
        Query the specified OPU PSI0 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.opuOh[veexlib.OTN_OPU_OH_PSI]

    def txOhOpuRes1(self, parameters):
        '''**TX:OH:OPU:RES1?** -
        Query the specified OPU RES1 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.opuOh[veexlib.OTN_OPU_OH_RES_1]

    def txOhOpuRes2(self, parameters):
        '''**TX:OH:OPU:RES2?** -
        Query the specified OPU RES2 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.opuOh[veexlib.OTN_OPU_OH_RES_2]

    def txOhOpuRes3(self, parameters):
        '''**TX:OH:OPU:RES3?** -
        Query the specified OPU RES3 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.opuOh[veexlib.OTN_OPU_OH_RES_3]

    def txOhOpuJc1(self, parameters):
        '''**TX:OH:OPU:JC1?** -
        Query the specified OPU JC1 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.opuOh[veexlib.OTN_OPU_OH_JC_1]

    def txOhOpuJc2(self, parameters):
        '''**TX:OH:OPU:JC2?** -
        Query the specified OPU JC2 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.opuOh[veexlib.OTN_OPU_OH_JC_2]

    def txOhOpuJc3(self, parameters):
        '''**TX:OH:OPU:JC3?** -
        Query the specified OPU JC3 overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.opuOh[veexlib.OTN_OPU_OH_JC_3]

    def txOhOpuNjo(self, parameters):
        '''**TX:OH:OPU:NJO?** -
        Query the specified OPU NJO overhead byte value being transmitted.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.opuOh[veexlib.OTN_OPU_OH_NJO]

    def txOhOpuMsi(self, parameters):
        '''**TX:OH:OPU:MSI? <slot>** -
        Query the specified OPU MSI overhead byte value being transmitted.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ALL"):
                iIndex = 0
            else:
                iIndex = ParseUtils.checkNumeric(paramList[0].head)
            if iIndex >= 0:
                if (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_112G_OTU_4) or \
                   (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_112G_CFP_OTU_4):
                    msiByteCount = 80
                elif (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_43G_OTU_3) or \
                     (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_44G_OTU_3E1) or \
                     (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_44G_OTU_3E2):
                    msiByteCount = 32
                elif (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_10G_OTU_2) or \
                     (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_11G_OTU_2E) or \
                     (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_11G_OTU_2F):
                    msiByteCount = 8
                elif (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_2P5G_OTU_1) or \
                     (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_11G_OTU_1E) or \
                     (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_11G_OTU_1F):
                    msiByteCount = 2
                else:
                    msiByteCount = -1
                if iIndex <= msiByteCount:
                    if iIndex == 0:
                        for i in range(msiByteCount-1):
                            response += b"#H%02X, " % self.globals.veexOtn.sets.opuMsi[i]
                        response += b"#H%02X" % self.globals.veexOtn.sets.opuMsi[msiByteCount-1]
                    else:
                        response = b"#H%02X" % self.globals.veexOtn.sets.opuMsi[iIndex-1]
                else:
                    response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOpuJust(self, parameters):
        '''**TX:OH:OPU:JUSTification:<POS|NEG>** -
        Sets the transmit value for the specified OPU JUST overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        self.globals.veexOtn.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"POS"):
                self.globals.veexOtn.singleJustify(veexlib.OTN_JUST_POSITIVE)
            elif paramList[0].head.upper().startswith(b"NEG"):
                self.globals.veexOtn.singleJustify(veexlib.OTN_JUST_NEGATIVE)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOpuRes1(self, parameters):
        '''**TX:OH:OPU:RES1:<value>** -
        Sets the transmit value for the specified OPU RES1 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                opuOh = self.globals.veexOtn.sets.opuOh
                opuOh[veexlib.OTN_OPU_OH_RES_1] = value
                self.globals.veexOtn.sets.opuOh = opuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOpuRes2(self, parameters):
        '''**TX:OH:OPU:RES2:<value>** -
        Sets the transmit value for the specified OPU RES2 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                opuOh = self.globals.veexOtn.sets.opuOh
                opuOh[veexlib.OTN_OPU_OH_RES_2] = value
                self.globals.veexOtn.sets.opuOh = opuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOpuRes3(self, parameters):
        '''**TX:OH:OPU:RES3:<value>** -
        Sets the transmit value for the specified OPU RES3 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                opuOh = self.globals.veexOtn.sets.opuOh
                opuOh[veexlib.OTN_OPU_OH_RES_3] = value
                self.globals.veexOtn.sets.opuOh = opuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOpuJc1(self, parameters):
        '''**TX:OH:OPU:JC1:<value>** -
        Sets the transmit value for the specified OPU JC1 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                opuOh = self.globals.veexOtn.sets.opuOh
                opuOh[veexlib.OTN_OPU_OH_JC_1] = value
                self.globals.veexOtn.sets.opuOh = opuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOpuJc2(self, parameters):
        '''**TX:OH:OPU:JC2:<value>** -
        Sets the transmit value for the specified OPU JC2 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                opuOh = self.globals.veexOtn.sets.opuOh
                opuOh[veexlib.OTN_OPU_OH_JC_2] = value
                self.globals.veexOtn.sets.opuOh = opuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOpuJc3(self, parameters):
        '''**TX:OH:OPU:JC3:<value>** -
        Sets the transmit value for the specified OPU JC3 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                opuOh = self.globals.veexOtn.sets.opuOh
                opuOh[veexlib.OTN_OPU_OH_JC_3] = value
                self.globals.veexOtn.sets.opuOh = opuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOpuNjo(self, parameters):
        '''**TX:OH:OPU:NJO:<value>** -
        Sets the transmit value for the specified OPU NJO overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                opuOh = self.globals.veexOtn.sets.opuOh
                opuOh[veexlib.OTN_OPU_OH_NJO] = value
                self.globals.veexOtn.sets.opuOh = opuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOpuPsi(self, parameters):
        '''**TX:OH:OPU:PSI0:<value>** -
        Sets the transmit value for the specified OPU PSI0 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                opuOh = self.globals.veexOtn.sets.opuOh
                opuOh[veexlib.OTN_OPU_OH_PSI] = value
                self.globals.veexOtn.sets.opuOh = opuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOpuMsi(self, parameters):
        '''**TX:OH:OPU:MSI:<slot> <value>** -
        Sets the transmit value for the specified OPU MSI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            arrMsiVal = self.globals.veexOtn.sets.opuMsi
            if paramList[0].head.upper().startswith(b"ALL"):
                for index in range(len(paramList)-1):
                    value = ParseUtils.checkNumeric(paramList[index+1].head)
                    if value >= 0 and value <= 255:
                        arrMsiVal[index] = value
                    else:
                        response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            else:
                if (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_112G_CFP_OTU_4) or \
                   (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_112G_OTU_4) or \
                   (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_112G_QSFP56_OTU_4):
                    msiByteCount = 80
                elif (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_43G_OTU_3) or \
                     (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_44G_OTU_3E1) or \
                     (self.globals.veexOtn.sets.txInterface == veexlib.OTN_INTERFACE_44G_OTU_3E2):
                    msiByteCount = 32
                else:
                    msiByteCount = 16
                index = ParseUtils.checkNumeric(paramList[0].head)
                if index < 1 or index > msiByteCount:
                    response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
                if len(paramList) >= 2:
                    value = ParseUtils.checkNumeric(paramList[1].head)
                    if value >= 0 and value <= 255:
                        arrMsiVal[index-1] = value
                    else:
                        response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
                else:
                    response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
            self.globals.veexOtn.sets.opuMsi = arrMsiVal
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txOhOtuBei(self, parameters):
        '''**TX:OH:OTU:BEI?** -
        Query the TX OTU BEI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.otuOh[veexlib.OTN_OTU_OH_SM_BEI]

    def txOhOtuDapi(self, parameters):
        '''**TX:OH:OTU:DAPI?** -
        Query the TX OTU DAPI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.otuSmTtiDapi.encode()[:15]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhOtuGcc1(self, parameters):
        '''**TX:OH:OTU:GCC01?** -
        Query the TX OTU GCC01 overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.otuOh[veexlib.OTN_OTU_OH_GCC0_1]

    def txOhOtuGcc2(self, parameters):
        '''**TX:OH:OTU:GCC02?** -
        Query the TX OTU GCC02 overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.otuOh[veexlib.OTN_OTU_OH_GCC0_2]

    def txOhOtuOa11(self, parameters):
        '''**TX:OH:OTU:OA1:1?** -
        Query the TX OTU OA1:1 overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.otuOh[veexlib.OTN_OTU_OH_FAS_OA1_1]

    def txOhOtuOa12(self, parameters):
        '''**TX:OH:OTU:OA1:2?** -
        Query the TX OTU OA1:2 overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.otuOh[veexlib.OTN_OTU_OH_FAS_OA1_2]

    def txOhOtuOa13(self, parameters):
        '''**TX:OH:OTU:OA1:3?** -
        Query the TX OTU OA1:3 overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.otuOh[veexlib.OTN_OTU_OH_FAS_OA1_3]

    def txOhOtuOa21(self, parameters):
        '''**TX:OH:OTU:OA2:1?** -
        Query the TX OTU OA2:1 overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.otuOh[veexlib.OTN_OTU_OH_FAS_OA2_1]

    def txOhOtuOa22(self, parameters):
        '''**TX:OH:OTU:OA2:2?** -
        Query the TX OTU OA2:2 overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.otuOh[veexlib.OTN_OTU_OH_FAS_OA2_2]

    def txOhOtuOa23(self, parameters):
        '''**TX:OH:OTU:OA2:3?** -
        Query the TX OTU OA2:3 overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.otuOh[veexlib.OTN_OTU_OH_FAS_OA2_3]

    def getTxOhOtuRes1(self, parameters):
        '''**TX:OH:OTU:RES1?** -
        Query the TX OTU RES1 overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.otuOh[veexlib.OTN_OTU_OH_OSMC]

    def txOhOtuRes2(self, parameters):
        '''**TX:OH:OTU:RES2?** -
        Query the TX OTU RES2 overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.otuOh[veexlib.OTN_OTU_OH_RES_2]

    def txOhOtuSapi(self, parameters):
        '''**TX:OH:OTU:SAPI?** -
        Query the TX OTU SAPI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.otuSmTtiSapi.encode()[:15]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhOtuSpecific(self, parameters):
        '''**TX:OH:OTU:SPECIFIC?** -
        Query the TX OTU SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.otuSmTtiSpecific.encode()[:32]
        response = response
        return response

    def txSetOhOtuBei(self, parameters):
        '''**TX:OH:OTU:BEI <value>** -
        Set the TX OTU BEI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                otuOh = self.globals.veexOtn.sets.otuOh
                otuOh[veexlib.OTN_OTU_OH_SM_BEI] = value
                self.globals.veexOtn.sets.otuOh = otuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOtuDapi(self, parameters):
        '''**TX:OH:OTU:DAPI <value>** -
        Set the TX OTU DAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            self.globals.veexOtn.sets.otuSmTtiDapi = dapi
        else:
            self.globals.veexOtn.sets.otuSmTtiDapi = b""
        return response

    def txSetOhOtuGcc1(self, parameters):
        '''**TX:OH:OTU:GCC01 <value>** -
        Set the TX OTU GCC01 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                otuOh = self.globals.veexOtn.sets.otuOh
                otuOh[veexlib.OTN_OTU_OH_GCC0_1] = value
                self.globals.veexOtn.sets.otuOh = otuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOtuGcc2(self, parameters):
        '''**TX:OH:OTU:GCC02 <value>** -
        Set the TX OTU GCC02 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                otuOh = self.globals.veexOtn.sets.otuOh
                otuOh[veexlib.OTN_OTU_OH_GCC0_2] = value
                self.globals.veexOtn.sets.otuOh = otuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOtuOa11(self, parameters):
        '''**TX:OH:OTU:OA1:1 <value>** -
        Set the TX OTU OA1:1 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                otuOh = self.globals.veexOtn.sets.otuOh
                otuOh[veexlib.OTN_OTU_OH_FAS_OA1_1] = value
                self.globals.veexOtn.sets.otuOh = otuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOtuOa12(self, parameters):
        '''**TX:OH:OTU:OA1:2 <value>** -
        Set the TX OTU OA1:2 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                otuOh = self.globals.veexOtn.sets.otuOh
                otuOh[veexlib.OTN_OTU_OH_FAS_OA1_2] = value
                self.globals.veexOtn.sets.otuOh = otuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOtuOa13(self, parameters):
        '''**TX:OH:OTU:OA1:3 <value>** -
        Set the TX OTU OA1:3 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                otuOh = self.globals.veexOtn.sets.otuOh
                otuOh[veexlib.OTN_OTU_OH_FAS_OA1_3] = value
                self.globals.veexOtn.sets.otuOh = otuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOtuOa21(self, parameters):
        '''**TX:OH:OTU:OA2:1 <value>** -
        Set the TX OTU OA2:1 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                otuOh = self.globals.veexOtn.sets.otuOh
                otuOh[veexlib.OTN_OTU_OH_FAS_OA2_1] = value
                self.globals.veexOtn.sets.otuOh = otuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOtuOa22(self, parameters):
        '''**TX:OH:OTU:OA2:2 <value>** -
        Set the TX OTU OA2:2 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                otuOh = self.globals.veexOtn.sets.otuOh
                otuOh[veexlib.OTN_OTU_OH_FAS_OA2_2] = value
                self.globals.veexOtn.sets.otuOh = otuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOtuOa23(self, parameters):
        '''**TX:OH:OTU:OA2:3 <value>** -
        Set the TX OTU OA2:3 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                otuOh = self.globals.veexOtn.sets.otuOh
                otuOh[veexlib.OTN_OTU_OH_FAS_OA2_3] = value
                self.globals.veexOtn.sets.otuOh = otuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def setTxOhOtuRes1(self, parameters):
        '''**TX:OH:OTU:RES1 <value>** -
        Set the TX OTU RES1 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                otuOh = self.globals.veexOtn.sets.otuOh
                otuOh[veexlib.OTN_OTU_OH_OSMC] = value
                self.globals.veexOtn.sets.otuOh = otuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOtuRes2(self, parameters):
        '''**TX:OH:OTU:RES2 <value>** -
        Set the TX OTU RES2 overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.update()
                otuOh = self.globals.veexOtn.sets.otuOh
                otuOh[veexlib.OTN_OTU_OH_RES_2] = value
                self.globals.veexOtn.sets.otuOh = otuOh
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhOtuSapi(self, parameters):
        '''**TX:OH:OTU:SAPI <value>** -
        Set the TX OTU SAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            self.globals.veexOtn.sets.otuSmTtiSapi = sapi
        else:
            self.globals.veexOtn.sets.otuSmTtiSapi = b""
        return response

    def txSetOhOtuSpecific(self, parameters):
        '''**TX:OH:OTU:SPECIFIC <value>** -
        Set the TX OTU SPECIFIC overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 32:
                specific = paramString[:32]
            else:
                specific = paramString[:]
            self.globals.veexOtn.sets.otuSmTtiSpecific = specific
        else:
            self.globals.veexOtn.sets.otuSmTtiSpecific = b""
        return response

    def txOhTcm1Bei(self, parameters):
        '''**TX:OH:TCM1:BEI?** -
        Query the TX TCM1 BEI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_TCM1_BEI]

    def txOhTcm1Dapi(self, parameters):
        '''**TX:OH:TCM1:DAPI?** -
        Query the TX TCM1 DAPI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiDapi[0].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhTcm1Sapi(self, parameters):
        '''**TX:OH:TCM1:SAPI?** -
        Query the TX TCM1 SAPI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiSapi[0].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhTcm1Specific(self, parameters):
        '''**TX:OH:TCM1:SPECIFIC?** -
        Query the TX TCM1 SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return self.globals.veexOtn.sets.oduTcmTtiSpecific[0].encode()[:]

    def txSetOhTcm1Bei(self, parameters):
        '''**TX:OH:TCM1:BEI:<value>** -
        Set the TX TCM1 BEI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value >= 0 and value <= 255:
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_TCM1_BEI] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhTcm1Dapi(self, parameters):
        '''**TX:OH:TCM1:DAPI:<value>** -
        Set the TX TCM1 DAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiDapi(1, dapi)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiDapi(1, b"")
        return response

    def txSetOhTcm1Sapi(self, parameters):
        '''**TX:OH:TCM1:SAPI:<value>** -
        Set the TX TCM1 SAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiSapi(1, sapi)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiSapi(1, b"")
        return response

    def txSetOhTcm1Specific(self, parameters):
        '''**TX:OH:TCM1:SPECIFIC:<value>** -
        Set the TX TCM1 SPECIFIC overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 32:
                specific = paramString[:32]
            else:
                specific = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiSpecific(1, specific)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiSpecific(1, b"")
        return response

    def txOhTcm2Bei(self, parameters):
        '''**TX:OH:TCM2:BEI?** -
        Query the TX TCM2 BEI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_TCM2_BEI]

    def txOhTcm2Dapi(self, parameters):
        '''**TX:OH:TCM2:DAPI?** -
        Query the TX TCM2 DAPI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiDapi[1].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response
    def txOhTcm2Sapi(self, parameters):
        '''**TX:OH:TCM2:SAPI?** -
        Query the TX TCM2 SAPI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiSapi[1].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhTcm2Specific(self, parameters):
        '''**TX:OH:TCM2:SPECIFIC?** -
        Query the TX TCM2 SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return self.globals.veexOtn.sets.oduTcmTtiSpecific[1].encode()[:]

    def txSetOhTcm2Bei(self, parameters):
        '''**TX:OH:TCM2:BEI:<value>** -
        Set the TX TCM2 BEI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value >= 0 and value <= 255:
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_TCM2_BEI] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhTcm2Dapi(self, parameters):
        '''**TX:OH:TCM2:DAPI:<value>** -
        Set the TX TCM2 DAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiDapi(2, dapi)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiDapi(2, b"")
        return response

    def txSetOhTcm2Sapi(self, parameters):
        '''**TX:OH:TCM2:SAPI:<value>** -
        Set the TX TCM2 SAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiSapi(2, sapi)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiSapi(2, b"")
        return response

    def txSetOhTcm2Specific(self, parameters):
        '''**TX:OH:TCM2:SPECIFIC:<value>** -
        Set the TX TCM2 SPECIFIC overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 32:
                specific = paramString[:32]
            else:
                specific = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiSpecific(2, specific)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiSpecific(2, b"")
        return response

    def txOhTcm3Bei(self, parameters):
        '''**TX:OH:TCM3:BEI?** -
        Query the TX TCM3 BEI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_TCM3_BEI]

    def txOhTcm3Dapi(self, parameters):
        '''**TX:OH:TCM3:DAPI?** -
        Query the TX TCM3 DAPI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiDapi[2].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhTcm3Sapi(self, parameters):
        '''**TX:OH:TCM3:SAPI?** -
        Query the TX TCM3 SAPI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiSapi[2].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhTcm3Specific(self, parameters):
        '''**TX:OH:TCM3:SPECIFIC?** -
        Query the TX TCM3 SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return self.globals.veexOtn.sets.oduTcmTtiSpecific[2].encode()[:]

    def txSetOhTcm3Bei(self, parameters):
        '''**TX:OH:TCM3:BEI:<value>** -
        Set the TX TCM3 BEI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value >= 0 and value <= 255:
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_TCM3_BEI] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhTcm3Dapi(self, parameters):
        '''**TX:OH:TCM3:DAPI:<value>** -
        Set the TX TCM3 DAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiDapi(3, dapi)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiDapi(3, b"")
        return response

    def txSetOhTcm3Sapi(self, parameters):
        '''**TX:OH:TCM3:SAPI:<value>** -
        Set the TX TCM3 SAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiSapi(3, sapi)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiSapi(3, b"")
        return response

    def txSetOhTcm3Specific(self, parameters):
        '''**TX:OH:TCM3:SPECIFIC:<value>** -
        Set the TX TCM3 SPECIFIC overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 32:
                specific = paramString[:32]
            else:
                specific = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiSpecific(3, specific)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiSpecific(3, b"")
        return response


    def txOhTcm4Bei(self, parameters):
        '''**TX:OH:TCM4:BEI?** -
        Query the TX TCM4 BEI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_TCM4_BEI]

    def txOhTcm4Dapi(self, parameters):
        '''**TX:OH:TCM4:DAPI?** -
        Query the TX TCM4 DAPI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiDapi[3].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhTcm4Sapi(self, parameters):
        '''**TX:OH:TCM4:SAPI?** -
        Query the TX TCM4 SAPI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiSapi[3].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhTcm4Specific(self, parameters):
        '''**TX:OH:TCM4:SPECIFIC?** -
        Query the TX TCM4 SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return self.globals.veexOtn.sets.oduTcmTtiSpecific[3].encode()[:]

    def txSetOhTcm4Bei(self, parameters):
        '''**TX:OH:TCM4:BEI:<value>** -
        Set the TX TCM4 BEI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value >= 0 and value <= 255:
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_TCM4_BEI] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhTcm4Dapi(self, parameters):
        '''**TX:OH:TCM4:DAPI:<value>** -
        Set the TX TCM4 DAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiDapi(4, dapi)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiDapi(4, b"")
        return response

    def txSetOhTcm4Sapi(self, parameters):
        '''**TX:OH:TCM4:SAPI:<value>** -
        Set the TX TCM4 SAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiSapi(4, sapi)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiSapi(4, b"")
        return response

    def txSetOhTcm4Specific(self, parameters):
        '''**TX:OH:TCM4:SPECIFIC:<value>** -
        Set the TX TCM4 SPECIFIC overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 32:
                specific = paramString[:32]
            else:
                specific = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiSpecific(4, specific)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiSpecific(4, b"")
        return response

    def txOhTcm5Bei(self, parameters):
        '''**TX:OH:TCM5:BEI?** -
        Query the TX TCM5 BEI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_TCM5_BEI]

    def txOhTcm5Dapi(self, parameters):
        '''**TX:OH:TCM5:DAPI?** -
        Query the TX TCM5 DAPI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiDapi[4].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhTcm5Sapi(self, parameters):
        '''**TX:OH:TCM5:SAPI?** -
        Query the TX TCM5 SAPI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiSapi[4].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhTcm5Specific(self, parameters):
        '''**TX:OH:TCM5:SPECIFIC?** -
        Query the TX TCM5 SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return self.globals.veexOtn.sets.oduTcmTtiSpecific[4].encode()[:]

    def txSetOhTcm5Bei(self, parameters):
        '''**TX:OH:TCM5:BEI:<value>** -
        Set the TX TCM5 BEI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value >= 0 and value <= 255:
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_TCM5_BEI] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhTcm5Dapi(self, parameters):
        '''**TX:OH:TCM5:DAPI:<value>** -
        Set the TX TCM5 DAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiDapi(5, dapi)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiDapi(5, b"")
        return response

    def txSetOhTcm5Sapi(self, parameters):
        '''**TX:OH:TCM5:SAPI:<value>** -
        Set the TX TCM5 SAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiSapi(5, sapi)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiSapi(5, b"")
        return response

    def txSetOhTcm5Specific(self, parameters):
        '''**TX:OH:TCM5:SPECIFIC:<value>** -
        Set the TX TCM5 SPECIFIC overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 32:
                specific = paramString[:32]
            else:
                specific = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiSpecific(5, specific)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiSpecific(5, b"")
        return response

    def txOhTcm6Bei(self, parameters):
        '''**TX:OH:TCM6:BEI?** -
        Query the TX TCM6 BEI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.oduOh[veexlib.OTN_ODU_OH_TCM6_BEI]

    def txOhTcm6Dapi(self, parameters):
        '''**TX:OH:TCM6:DAPI?** -
        Query the TX TCM6 DAPI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiDapi[5].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhTcm6Sapi(self, parameters):
        '''**TX:OH:TCM6:SAPI?** -
        Query the TX TCM6 SAPI overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiSapi[5].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def txOhTcm6Specific(self, parameters):
        '''**TX:OH:TCM6:SPECIFIC?** -
        Query the TX TCM6 SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return self.globals.veexOtn.sets.oduTcmTtiSpecific[5].encode()[:]

    def txSetOhTcm6Bei(self, parameters):
        '''**TX:OH:TCM6:BEI:<value>** -
        Set the TX TCM6 BEI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value >= 0 and value <= 255:
                self.globals.veexOtn.sets.update()
                oduOh = self.globals.veexOtn.sets.oduOh
                oduOh[veexlib.OTN_ODU_OH_TCM6_BEI] = value
                self.globals.veexOtn.sets.oduOh = oduOh
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def txSetOhTcm6Dapi(self, parameters):
        '''**TX:OH:TCM6:DAPI:<value>** -
        Set the TX TCM6 DAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiDapi(6, dapi)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiDapi(6, b"")
        return response

    def txSetOhTcm6Sapi(self, parameters):
        '''**TX:OH:TCM6:SAPI:<value>** -
        Set the TX TCM6 SAPI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiSapi(6, sapi)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiSapi(6, b"")
        return response

    def txSetOhTcm6Specific(self, parameters):
        '''**TX:OH:TCM6:SPECIFIC:<value>** -
        Set the TX TCM6 SPECIFIC overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) > 32:
                specific = paramString[:32]
            else:
                specific = paramString[:]
            self.globals.veexOtn.sets.setOduTcmTtiSpecific(6, specific)
        else:
            self.globals.veexOtn.sets.setOduTcmTtiSpecific(6, b"")
        return response

    def getTxOpuFreqOffset(self, parameters):
        '''**TX:OPUFREQOffset?** -
        Query the current transmitted OPU justification frequency offset value in PPM.
        '''
        self.globals.veexOtn.sets.update()
        fInValue = self.globals.veexOtn.sets.opuFreqOffset
        if math.isclose(fInValue, 0.00, rel_tol = 0.000001):
            response = b"OFF"
        else:
            response = b"%0.2f ppm" % fInValue
        return response

    def setTxOpuFreqOffset(self, parameters):
        '''**TX:OPUFREQOffset:<offset>** -
        Sets the transmitted OPU justification frequency offset value, in increments of 0.1 PPM.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if ParseUtils.isFloatSdh(paramList[0].head):
                fInValue = float(paramList[0].head)
                self.globals.veexOtn.sets.update()
                self.globals.veexOtn.sets.opuFreqOffset = fInValue
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getOTUCn(self, parameters):
        '''**TX:OTUCN? and RX:OTUCN?** -
        Query the list of configured OTUCn interface Slices,
        '''
        self.globals.veexOtn.sets.update()
        response = b"TBD"
        return response

    def setOTUCn(self, parameters):
        '''**TX:OTUCN:<parameters> and RX:OTUCN:<parameters>** -
        Synchronizes the transmit OTN interfaces on one or more 100G ports.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = b"TBD"
        return response

    def getTxFreqThreshhold(self, parameters):
        '''**TX:OUTTHRESHold?** -
        Query the Transmit Clock Loss Threshold alarm +/- value (in ppm).
        '''
        self.globals.veexOtn.sets.update()
        fInValue = self.globals.veexOtn.sets.txFreqTolerance
        if math.isclose(fInValue, 0.00, rel_tol = 0.000001):
            response = b"OFF"
        else:
            response = b"%0.1f ppm" % fInValue
        return response

    def setTxFreqThreshhold(self, parameters):
        '''**TX:OUTTHRESHold <offset>** -
        Sets the +/- value (in ppm) for the Transmit Clock Loss Threshold alarm.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if ParseUtils.isFloatSdh(paramList[0].head):
                fInValue = float(paramList[0].head)
                self.globals.veexOtn.sets.update()
                self.globals.veexOtn.sets.txFreqTolerance = fInValue
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxPassthru(self, parameters):
        '''**TX:PASSthru?** -
        Query the passthru mode is enabled state.
        '''
        self.globals.veexOtn.sets.update()
        if self.globals.veexOtn.sets.passthruMode:
            response = b"ON"
        else:
            response = b"OFF"
        return response

    def setTxPassthru(self, parameters):
        '''**TX:PASSthru <ON|OFF>** -
        Sets the passthru mode enable/disable state.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        self.globals.veexOtn.sets.update()
        response = None
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ON"):
                self.globals.veexOtn.sets.passthruMode = True
            elif paramList[0].head.upper().startswith(b"OFF"):
                self.globals.veexOtn.sets.passthruMode = False
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxPattern(self, parameters):
        '''**TX:PATTern?<container>** -
        Query the protocol processor for the pattern it is sending.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.txPattern == veexlib.OTN_PATTERN_LIVE:
            response = b"LIVE"
        elif self.globals.veexOtn.sets.txPattern == veexlib.OTN_PATTERN_PRBS_9:
            response = b"PRBS9"
        elif self.globals.veexOtn.sets.txPattern == veexlib.OTN_PATTERN_PRBS_9_INV:
            response = b"PRBS9INV"
        elif self.globals.veexOtn.sets.txPattern == veexlib.OTN_PATTERN_PRBS_11:
            response = b"PRBS11"
        elif self.globals.veexOtn.sets.txPattern == veexlib.OTN_PATTERN_PRBS_11_INV:
            response = b"PRBS11INV"
        elif self.globals.veexOtn.sets.txPattern == veexlib.OTN_PATTERN_PRBS_15:
            response = b"PRBS15"
        elif self.globals.veexOtn.sets.txPattern == veexlib.OTN_PATTERN_PRBS_15_INV:
            response = b"PRBS15INV"
        elif self.globals.veexOtn.sets.txPattern == veexlib.OTN_PATTERN_PRBS_20:
            response = b"PRBS20"
        elif self.globals.veexOtn.sets.txPattern == veexlib.OTN_PATTERN_PRBS_20_INV:
            response = b"PRBS20INV"
        elif self.globals.veexOtn.sets.txPattern == veexlib.OTN_PATTERN_PRBS_23:
            response = b"PRBS23"
        elif self.globals.veexOtn.sets.txPattern == veexlib.OTN_PATTERN_PRBS_23_INV:
            response = b"PRBS23INV"
        elif self.globals.veexOtn.sets.txPattern == veexlib.OTN_PATTERN_PRBS_31:
            response = b"PRBS31"
        elif self.globals.veexOtn.sets.txPattern == veexlib.OTN_PATTERN_PRBS_31_INV:
            response = b"PRBS31INV"
        elif self.globals.veexOtn.sets.txPattern == veexlib.OTN_PATTERN_USER:
            bValue = bin(self.globals.veexOtn.sets.txUserPattern)
            response = b"#B" + bValue.encode()[2:]
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_PATTERN)
        return response

    def setTxPattern(self, parameters):
        '''**TX:PATTern:<pattern> <container>** -
        Sets the transmit payload pattern.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"LIVE"):
                self.globals.veexOtn.sets.txPattern = veexlib.OTN_PATTERN_LIVE
            elif paramList[0].head.upper().startswith(b"PRBS9INV"):
                self.globals.veexOtn.sets.txPattern = veexlib.OTN_PATTERN_PRBS_9_INV
            elif paramList[0].head.upper().startswith(b"PRBS9"):
                self.globals.veexOtn.sets.txPattern = veexlib.OTN_PATTERN_PRBS_9
            elif paramList[0].head.upper().startswith(b"PRBS11INV"):
                self.globals.veexOtn.sets.txPattern = veexlib.OTN_PATTERN_PRBS_11_INV
            elif paramList[0].head.upper().startswith(b"PRBS11"):
                self.globals.veexOtn.sets.txPattern = veexlib.OTN_PATTERN_PRBS_11
            elif paramList[0].head.upper().startswith(b"PRBS15INV"):
                self.globals.veexOtn.sets.txPattern = veexlib.OTN_PATTERN_PRBS_15_INV
            elif paramList[0].head.upper().startswith(b"PRBS15"):
                self.globals.veexOtn.sets.txPattern = veexlib.OTN_PATTERN_PRBS_15
            elif paramList[0].head.upper().startswith(b"PRBS20INV"):
                self.globals.veexOtn.sets.txPattern = veexlib.OTN_PATTERN_PRBS_20_INV
            elif paramList[0].head.upper().startswith(b"PRBS20"):
                self.globals.veexOtn.sets.txPattern = veexlib.OTN_PATTERN_PRBS_20
            elif paramList[0].head.upper().startswith(b"PRBS23INV"):
                self.globals.veexOtn.sets.txPattern = veexlib.OTN_PATTERN_PRBS_23_INV
            elif paramList[0].head.upper().startswith(b"PRBS23"):
                self.globals.veexOtn.sets.txPattern = veexlib.OTN_PATTERN_PRBS_23
            elif paramList[0].head.upper().startswith(b"PRBS31INV"):
                self.globals.veexOtn.sets.txPattern = veexlib.OTN_PATTERN_PRBS_31_INV
            elif paramList[0].head.upper().startswith(b"PRBS31"):
                self.globals.veexOtn.sets.txPattern = veexlib.OTN_PATTERN_PRBS_31
            else:
                value = ParseUtils.checkNumeric(paramList[0].head)
                if value >= 0:
                    self.globals.veexOtn.sets.txUserPattern = value
                else:
                    response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxRtdAction(self, parameters):
        '''**TX:RTD:ACTION?** -
        Query the Round-Trip Delay (RTD).
        '''
        self.globals.veexOtn.stats.update()
#        response = b""
        if self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_SDT_ST_STOPPED:
            return b"APS STOP"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_SDT_ST_ARMED:
            return b"ARMED APS SINGLE"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_SDT_ST_RUNNING:
            return b"RUNNING APS SINGLE"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_SDT_ST_CONT_ARM:
            return b"ARMED APS CONTINUOUS"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_SDT_ST_CONT_RUN:
            return b"RUNNING APS CONTINUOUS"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_STOPPED:
            return b"RTD STOP"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_ARMED:
            return b"ARMED RTD SINGLE"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_RUNNING:
            return b"RUNNING RTD SINGLE"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_CONT_ARM:
            return b"ARMED RTD CONTINUOUS"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_CONT_RUN:
            return b"RUNNING RTD CONTINUOUS"
        else:
            return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
#        else:
#            response = self._errorResponse(ScpiErrorCode.INVALID_PATTERN)
#        return response

    def setTxRtdAction(self, parameters):
        '''**TX:RTD:ACTION <CONTinuos|SINGle|STOP>** -
        Starts and stops the Round-Trip Delay (RTD) function.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.stats.update()
            if (self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_SDT_ST_ARMED) or \
               (self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_SDT_ST_RUNNING) or \
               (self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_SDT_ST_CONT_ARM) or \
               (self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_SDT_ST_CONT_RUN):
                response = self._errorResponse(ScpiErrorCode.CMD_INVALID_FOR_CRNT_CONFIG)
            if paramList[0].head.upper().startswith(b"STOP"):
                self.globals.veexOtn.sets.sdtSwitchState = veexlib.OTN_RTD_STOPPED
            elif paramList[0].head.upper().startswith(b"SING"):
                self.globals.veexOtn.sets.sdtSwitchState = veexlib.OTN_RTD_ARMED
            elif paramList[0].head.upper().startswith(b"CONT"):
                self.globals.veexOtn.sets.sdtSwitchState = veexlib.OTN_RTD_CONT_ARM
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxRtdDmBit(self, parameters):
        '''**TX:RTD:DM?** -
        Query the RTD!/s Delay Measurement overhead byte setting.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        uDmSelect = self.globals.veexOtn.sets.rtdDmSelect
        if uDmSelect & veexlib.OTN_RTD_DM_SELECT_PM:
            response = b"PM"
        elif uDmSelect & veexlib.OTN_RTD_DM_SELECT_TCM1:
            response = b"TCM1"
        elif uDmSelect & veexlib.OTN_RTD_DM_SELECT_TCM2:
            response = b"TCM2"
        elif uDmSelect & veexlib.OTN_RTD_DM_SELECT_TCM3:
            response = b"TCM3"
        elif uDmSelect & veexlib.OTN_RTD_DM_SELECT_TCM4:
            response = b"TCM4"
        elif uDmSelect & veexlib.OTN_RTD_DM_SELECT_TCM5:
            response = b"TCM5"
        elif uDmSelect & veexlib.OTN_RTD_DM_SELECT_TCM6:
            response = b"TCM6"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setTxRtdDmBit(self, parameters):
        '''**TX:RTD:DM <overhead>** -
        Sets the RTD!/s Delay Measurement overhead byte setting.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"PM"):
                self.globals.veexOtn.sets.rtdDmSelect = veexlib.OTN_RTD_DM_SELECT_PM
            elif paramList[0].head.upper().startswith(b"TCM1"):
                self.globals.veexOtn.sets.rtdDmSelect = veexlib.OTN_RTD_DM_SELECT_TCM1
            elif paramList[0].head.upper().startswith(b"TCM2"):
                self.globals.veexOtn.sets.rtdDmSelect = veexlib.OTN_RTD_DM_SELECT_TCM2
            elif paramList[0].head.upper().startswith(b"TCM3"):
                self.globals.veexOtn.sets.rtdDmSelect = veexlib.OTN_RTD_DM_SELECT_TCM3
            elif paramList[0].head.upper().startswith(b"TCM4"):
                self.globals.veexOtn.sets.rtdDmSelect = veexlib.OTN_RTD_DM_SELECT_TCM4
            elif paramList[0].head.upper().startswith(b"TCM5"):
                self.globals.veexOtn.sets.rtdDmSelect = veexlib.OTN_RTD_DM_SELECT_TCM5
            elif paramList[0].head.upper().startswith(b"TCM6"):
                self.globals.veexOtn.sets.rtdDmSelect = veexlib.OTN_RTD_DM_SELECT_TCM6
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxApsGoodFrames(self, parameters):
        '''**TX:RTD:GOOD:FRAME?** -
        Query the RTD!/s Consecutive Good Frames Required.
        '''
        self.globals.veexOtn.sets.update()
        member = self.globals.veexOtn.sets.sdtDrop
        return b"%d frames" % self.globals.veexOtn.sets.sdtSwitchStopCount[member]

    def setTxApsGoodFrames(self, parameters):
        '''**TX:RTD:GOOD:FRAME <value>** -
        Sets the value for the RTD!/s Consecutive Good Frames Required.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value >= 1 or value <= 16383:
                self.globals.veexOtn.sets.update()
                member = self.globals.veexOtn.sets.sdtDrop
                sdtSwitchStopCount = self.globals.veexOtn.sets.sdtSwitchStopCount
                sdtSwitchStopCount[member] = value
                self.globals.veexOtn.sets.sdtSwitchStopCount = sdtSwitchStopCount
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxApsGoodTime(self, parameters):
        '''**TX:RTD:GOOD:TIME?** -
        Query the RTD!/s Consecutive Good Time Required.
        '''
        self.globals.veexOtn.sets.update()
        member = self.globals.veexOtn.sets.sdtDrop
        fval = float(self.globals.veexOtn.sets.sdtSwitchStopCount[member]) / \
               self.globals.veexOtn.sets.sdtSwitchFrameRate * 1000.0
        return b"%.3f msec" % fval

    def setTxApsGoodTime(self, parameters):
        '''**TX:RTD:GOOD:TIME <value>** -
        Sets a value, in milliseconds, for the RTD!/s Consecutive Good Time
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if ParseUtils.isFloatSdh(paramList[0].head):
                fval = float(paramList[0].head)
                if fval >= 0.125 and fval <= 2047.876:
                    self.globals.veexOtn.sets.update()
#                    member = self.globals.veexOtn.sets.sdtDrop
#                    self.globals.veexOtn.sets.sdtSwitchStopCount[member] = (fval * self.globals.veexOtn.sets.sdtSwitchFrameRate) / 1000.0
                    sdtSwitchStopCount = self.globals.veexOtn.sets.sdtSwitchStopCount
                    sdtSwitchStopCount[0] = (fval * self.globals.veexOtn.sets.sdtSwitchFrameRate) / 1000.0
                    self.globals.veexOtn.sets.sdtSwitchStopCount = sdtSwitchStopCount
                else:
                    response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxRtdOduLevel(self, parameters):
        '''**TX:RTD:ODTULEVEL? and SD:ODTULEVEL?** -
        Query which ODU level the Round-Trip Delay (RTD) trigger is currently set to use,
        '''
        self.globals.veexOtn.sets.update()
        return b"%d" % (self.globals.veexOtn.sets.sdtOdtuLevel - 1,)

    def setTxRtdOduLevel(self, parameters):
        '''**TX:RTD:ODTULEVEL:<0|1|2|3|4> and SD:ODTULEVEL:<0|1|2|3|4>** -
        Sets the ODU level the Round-Trip Delay (RTD) trigger is based on,
        when configured for an ODTU A/D MUX Mapping.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value == 0:
                self.globals.veexOtn.sets.sdtOdtuLevel = veexlib.OTN_SDT_ODTU_LEVEL_ODU_0
            elif value == 1:
                self.globals.veexOtn.sets.sdtOdtuLevel = veexlib.OTN_SDT_ODTU_LEVEL_ODU_1
            elif value == 2:
                self.globals.veexOtn.sets.sdtOdtuLevel = veexlib.OTN_SDT_ODTU_LEVEL_ODU_2
            elif value == 3:
                self.globals.veexOtn.sets.sdtOdtuLevel = veexlib.OTN_SDT_ODTU_LEVEL_ODU_3
            elif value == 4:
                self.globals.veexOtn.sets.sdtOdtuLevel = veexlib.OTN_SDT_ODTU_LEVEL_ODU_4
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxScramble(self, parameters):
        '''**TX:SCRAMBLE?** -
        Query the state of transmit OTN frame scrambling mode.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.txScrambleDisable:
            response = b"DISABLED"
        else:
            response = b"ENABLED"
        return response

    def setTxScramble(self, parameters):
        '''**TX:SCRAMBLE:<ENABLED|DISABLED>** -
        Sets the state of the transmit OTN frame scrambling mode.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.txScrambleDisable = True
            elif paramList[0].head.upper().startswith(b"ENABLED"):
                self.globals.veexOtn.sets.txScrambleDisable = False
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTxTrigger(self, parameters):
        '''**TX:TRIG?** -
        Query the Trigger In action.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.inTriggerAction == 0:
            response = b"NONE"
        elif self.globals.veexOtn.sets.inTriggerAction == 1:
            response = b"RESTART"
        elif self.globals.veexOtn.sets.inTriggerAction == 2:
            response = b"INSERT ERROR"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setTxTrigger(self, parameters):
        '''**TX:TRIG:<NONE|RESTART|INSERT ERROR>** -
        Sets the Trigger In action to be performed when a +5v pulse is detected on the Trigger In SMA connector.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"NONE"):
                self.globals.veexOtn.sets.inTriggerAction = 0
            elif paramList[0].head.upper().startswith(b"RESTART"):
                self.globals.veexOtn.sets.inTriggerAction = 1
            elif paramList[0].head.upper().startswith(b"INSERT ERROR"):
                self.globals.veexOtn.sets.inTriggerAction = 2
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getDisableLofReset(self, parameters):
        '''**RX:AUTORECOVER?** -
        Query the value of the signal auto-recovery method
        '''
        self.globals.veexOtn.sets.update()
        if self.globals.veexOtn.sets.disableLofReset:
            return b"ALTERNATE"
        else:
            return b"DEFAULT"

    def setDisableLofReset(self, parameters):
        '''**RX:AUTORECOVER:<method>** -
        Sets the RX Signal Auto-Recovery Method to either the Default method or the Alternate method.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"DEFAULT"):
                self.globals.veexOtn.sets.disableLofReset = False
            elif paramList[0].head.upper().startswith(b"ALTERNATE"):
                self.globals.veexOtn.sets.disableLofReset = True
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getArmTrigger(self, parameters):
        '''**RX:CAP:ARM?** -
        Query the received ODU Flex Data Rate, in Mbps.
        '''
        self.globals.veexOtn.stats.update()
        if (self.globals.veexOtn.stats.captureDataState == veexlib.OTN_OH_CAPTURE_WAIT_FOR_TRIG) or \
           (self.globals.veexOtn.stats.captureDataState == veexlib.OTN_OH_CAPTURE_RUNNING):
            return b"ON"
        else:
            return b"OFF"

    def armTrigger(self, parameters):
        '''**RX:CAP:ARM:<mode>** -
        Enables or Disables the overhead Byte Capture feature.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ON"):
                self.globals.veexOtn.sets.captureTrigger = True
            elif paramList[0].head.upper().startswith(b"OFF"):
                self.globals.veexOtn.sets.captureTrigger = False
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getByteSelect(self, parameters):
        '''**RX:CAP:BYTE?** -
        Queries the selected overhead byte to be captured
        '''
        self.globals.veexOtn.sets.update()
        if self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OTU_OH_CAPTURE_SELECT_FAS_OA1_1:
            return b"OTUFASOA11"
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OTU_OH_CAPTURE_SELECT_FAS_OA1_2:
            return b"OTUFASOA12",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OTU_OH_CAPTURE_SELECT_FAS_OA1_3:
            return b"OTUFASOA13",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OTU_OH_CAPTURE_SELECT_FAS_OA2_1:
            return b"OTUFASOA21",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OTU_OH_CAPTURE_SELECT_FAS_OA2_2:
            return b"OTUFASOA22",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OTU_OH_CAPTURE_SELECT_FAS_OA2_3:
            return b"OTUFASOA23",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OTU_OH_CAPTURE_SELECT_MFAS:
            return b"OTUMFAS",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OTU_OH_CAPTURE_SELECT_SM_TTI:
            return b"OTUSMTTI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OTU_OH_CAPTURE_SELECT_SM_BIP:
            return b"OTUSMBIP",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OTU_OH_CAPTURE_SELECT_SM_BEI:
            return b"OTUSMBEI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OTU_OH_CAPTURE_SELECT_GCC0_1:
            return b"OTUGCC01",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OTU_OH_CAPTURE_SELECT_GCC0_2:
            return b"OTUGCC02",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OTU_OH_CAPTURE_SELECT_OSMC:
            return b"OTUOSMC",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OTU_OH_CAPTURE_SELECT_RES_2:
            return b"OTURES2",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OPU_OH_CAPTURE_SELECT_RES_1:
            return b"OPURES1",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OPU_OH_CAPTURE_SELECT_JC_1:
            return b"OPUJC1",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_1:
            return b"ODURES1",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_2:
            return b"ODURES2",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_3:
            return b"ODURES3",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM_ACT:
            return b"ODUTCMACT",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM6_TTI:
            return b"ODUTCM6TTI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM6_BIP:
            return b"ODUTCM6BIP",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM6_BEI:
            return b"ODUTCM6BEI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM5_TTI:
            return b"ODUTCM5TTI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM5_BIP:
            return b"ODUTCM5BIP",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM5_BEI:
            return b"ODUTCM5BEI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM4_TTI:
            return b"ODUTCM4TTI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM4_BIP:
            return b"ODUTCM4BIP",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM4_BEI:
            return b"ODUTCM4BEI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_FTFL:
            return b"ODUFTFL",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OPU_OH_CAPTURE_SELECT_RES_2:
            return b"OPURES2",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OPU_OH_CAPTURE_SELECT_JC_2:
            return b"OPUJC2",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM3_TTI:
            return b"ODUTCM3TTI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM3_BIP:
            return b"ODUTCM3BIP",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM3_BEI:
            return b"ODUTCM3BEI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM2_TTI:
            return b"ODUTCM2TTI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM2_BIP:
            return b"ODUTCM2BIP",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM2_BEI:
            return b"ODUTCM2BEI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM1_TTI:
            return b"ODUTCM1TTI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM1_BIP:
            return b"ODUTCM1BIP",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM1_BEI:
            return b"ODUTCM1BEI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_PM_TTI:
            return b"ODUPMTTI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_PM_BIP:
            return b"ODUPMBPI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_PM_BEI:
            return b"ODUPMBEI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_EXP_1:
            return b"ODUEXP1",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_EXP_2:
            return b"ODUEXP2",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OPU_OH_CAPTURE_SELECT_RES_3:
            return b"OPURES3",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OPU_OH_CAPTURE_SELECT_JC_3:
            return b"OPUJC3",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_GCC1_1:
            return b"ODUGCC11",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_GCC1_2:
            return b"ODUGCC12",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_GCC2_1:
            return b"ODUGCC21",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_GCC2_2:
            return b"ODUGCC22",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_APS_PCC_1:
            return b"ODUAPSPCC1",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_APS_PCC_2:
            return b"ODUAPSPCC2",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_APS_PCC_3:
            return b"ODUAPSPCC3",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_APS_PCC_4:
            return b"ODUAPSPCC4",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_4:
            return b"ODURES4",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_5:
            return b"ODURES5",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_6:
            return b"ODURES6",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_7:
            return b"ODURES7",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_8:
            return b"ODURES8",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_9:
            return b"ODURES9",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OPU_OH_CAPTURE_SELECT_PSI:
            return b"OPUPSI",
        elif self.globals.veexOtn.sets.ohCaptureByteSelect == veexlib.OTN_OPU_OH_CAPTURE_SELECT_NJO:
            return b"OPUNJO"
        else:
            return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setByteSelect(self, parameters):
        '''**RX:CAP:BYTE:<byte>** -
        Sets the desired overhead byte for the !0Byte Select!1 option, used in the receive Byte Capture feature.
        '''
        dictByteSelect = {
            b"OTUFASOA11"  : veexlib.OTN_OTU_OH_CAPTURE_SELECT_FAS_OA1_1,
            b"OTUFASOA12"  : veexlib.OTN_OTU_OH_CAPTURE_SELECT_FAS_OA1_2,
            b"OTUFASOA13"  : veexlib.OTN_OTU_OH_CAPTURE_SELECT_FAS_OA1_3,
            b"OTUFASOA21"  : veexlib.OTN_OTU_OH_CAPTURE_SELECT_FAS_OA2_1,
            b"OTUFASOA22"  : veexlib.OTN_OTU_OH_CAPTURE_SELECT_FAS_OA2_2,
            b"OTUFASOA23"  : veexlib.OTN_OTU_OH_CAPTURE_SELECT_FAS_OA2_3,
            b"OTUMFAS"     : veexlib.OTN_OTU_OH_CAPTURE_SELECT_MFAS,
            b"OTUSMTTI"    : veexlib.OTN_OTU_OH_CAPTURE_SELECT_SM_TTI,
            b"OTUSMBIP"    : veexlib.OTN_OTU_OH_CAPTURE_SELECT_SM_BIP,
            b"OTUSMBEI"    : veexlib.OTN_OTU_OH_CAPTURE_SELECT_SM_BEI,
            b"OTUGCC01"    : veexlib.OTN_OTU_OH_CAPTURE_SELECT_GCC0_1,
            b"OTUGCC02"    : veexlib.OTN_OTU_OH_CAPTURE_SELECT_GCC0_2,
            b"OTUOSMC"     : veexlib.OTN_OTU_OH_CAPTURE_SELECT_OSMC,
            b"OTURES2"     : veexlib.OTN_OTU_OH_CAPTURE_SELECT_RES_2,
            b"OPURES1"     : veexlib.OTN_OPU_OH_CAPTURE_SELECT_RES_1,
            b"OPUJC1"      : veexlib.OTN_OPU_OH_CAPTURE_SELECT_JC_1,
            b"ODURES1"     : veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_1,
            b"ODURES2"     : veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_2,
            b"ODURES3"     : veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_3,
            b"ODUTCMACT"   : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM_ACT,
            b"ODUTCM6TTI"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM6_TTI,
            b"ODUTCM6BIP"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM6_BIP,
            b"ODUTCM6BEI"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM6_BEI,
            b"ODUTCM5TTI"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM5_TTI,
            b"ODUTCM5BIP"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM5_BIP,
            b"ODUTCM5BEI"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM5_BEI,
            b"ODUTCM4TTI"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM4_TTI,
            b"ODUTCM4BIP"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM4_BIP,
            b"ODUTCM4BEI"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM4_BEI,
            b"ODUFTFL"     : veexlib.OTN_ODU_OH_CAPTURE_SELECT_FTFL,
            b"OPURES2"     : veexlib.OTN_OPU_OH_CAPTURE_SELECT_RES_2,
            b"OPUJC2"      : veexlib.OTN_OPU_OH_CAPTURE_SELECT_JC_2,
            b"ODUTCM3TTI"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM3_TTI,
            b"ODUTCM3BIP"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM3_BIP,
            b"ODUTCM3BEI"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM3_BEI,
            b"ODUTCM2TTI"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM2_TTI,
            b"ODUTCM2BIP"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM2_BIP,
            b"ODUTCM2BEI"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM2_BEI,
            b"ODUTCM1TTI"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM1_TTI,
            b"ODUTCM1BIP"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM1_BIP,
            b"ODUTCM1BEI"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_TCM1_BEI,
            b"ODUPMTTI"    : veexlib.OTN_ODU_OH_CAPTURE_SELECT_PM_TTI,
            b"ODUPMBPI"    : veexlib.OTN_ODU_OH_CAPTURE_SELECT_PM_BIP,
            b"ODUPMBEI"    : veexlib.OTN_ODU_OH_CAPTURE_SELECT_PM_BEI,
            b"ODUEXP1"     : veexlib.OTN_ODU_OH_CAPTURE_SELECT_EXP_1,
            b"ODUEXP2"     : veexlib.OTN_ODU_OH_CAPTURE_SELECT_EXP_2,
            b"OPURES3"     : veexlib.OTN_OPU_OH_CAPTURE_SELECT_RES_3,
            b"OPUJC3"      : veexlib.OTN_OPU_OH_CAPTURE_SELECT_JC_3,
            b"ODUGCC11"    : veexlib.OTN_ODU_OH_CAPTURE_SELECT_GCC1_1,
            b"ODUGCC12"    : veexlib.OTN_ODU_OH_CAPTURE_SELECT_GCC1_2,
            b"ODUGCC21"    : veexlib.OTN_ODU_OH_CAPTURE_SELECT_GCC2_1,
            b"ODUGCC22"    : veexlib.OTN_ODU_OH_CAPTURE_SELECT_GCC2_2,
            b"ODUAPSPCC1"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_APS_PCC_1,
            b"ODUAPSPCC2"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_APS_PCC_2,
            b"ODUAPSPCC3"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_APS_PCC_3,
            b"ODUAPSPCC4"  : veexlib.OTN_ODU_OH_CAPTURE_SELECT_APS_PCC_4,
            b"ODURES4"     : veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_4,
            b"ODURES5"     : veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_5,
            b"ODURES6"     : veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_6,
            b"ODURES7"     : veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_7,
            b"ODURES8"     : veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_8,
            b"ODURES9"     : veexlib.OTN_ODU_OH_CAPTURE_SELECT_RES_9,
            b"OPUPSI"      : veexlib.OTN_OPU_OH_CAPTURE_SELECT_PSI,
            b"OPUNJO"      : veexlib.OTN_OPU_OH_CAPTURE_SELECT_NJO
            }
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            if paramList[0].head.upper() in dictByteSelect.keys():
                matchValue = self.globals.veexOtn.sets.ohCaptureMatchValue
                trigger = self.globals.veexOtn.sets.captureTrigger
                byteSelect = dictByteSelect[paramList[0].head.upper()]
                position = self.globals.veexOtn.sets.ohCapturePosition
                self.globals.veexOtn.sets.setOhCaptureSettings(trigger,matchValue,position,byteSelect)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getMatchValue(self, parameters):
        '''**RX:CAP:MATCH?** -
        Queries the capture match value.
        '''
        self.globals.veexOtn.sets.update()
        return b"%X" % self.globals.veexOtn.sets.ohCaptureMatchValue

    def setMatchValue(self, parameters):
        '''**RX:CAP:MATCH:<value>** -
        Sets the match value (in hexadecimal format), for !0Byte Equal!1 or !0Not Equal!1 triggers.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            value = ParseUtils.asciiToHexSdh(paramList[0].head)
            if value >= 0:
                matchValue = value
                trigger = self.globals.veexOtn.sets.captureTrigger
                byteSelect = self.globals.veexOtn.sets.ohCaptureByteSelect
                position = self.globals.veexOtn.sets.ohCapturePosition
                self.globals.veexOtn.sets.setOhCaptureSettings(trigger,matchValue,position,byteSelect)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getTriggerPos(self, parameters):
        '''**RX:CAP:POS?** -
        Queries the number of Bytes to capture after trigger occurs.
        '''
        self.globals.veexOtn.sets.update()
        return b"%d" % self.globals.veexOtn.sets.ohCapturePosition

    def setTriggerPos(self, parameters):
        '''**RX:CAP:POS:<value>** -
        Sets the number of Bytes to capture after trigger occurs.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            position = ParseUtils.checkNumeric(paramList[0].head)
            if (position >= 0) and (position <= 255):
                self.globals.veexOtn.sets.update()
                trigger = self.globals.veexOtn.sets.captureTrigger
                matchValue = self.globals.veexOtn.sets.ohCaptureMatchValue
                byteSelect = self.globals.veexOtn.sets.ohCaptureByteSelect
                self.globals.veexOtn.sets.setOhCaptureSettings(trigger,matchValue,position,byteSelect)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def displayCapture(self, parameters):
        '''**RX:CAP:REPORT?** -
        Query the Overhead Byte Capture Results
        '''
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.captureDataState == veexlib.OTN_OH_OH_CAPTURE_DONE:
            for iRow in range(256):
                if iRow == 256 - 1:
                    response += b"%d, %X " % (iRow, self.globals.veexOtn.stats.captureData[iRow])
                else:
                    response += b"%d, %X | " % (iRow, self.globals.veexOtn.stats.captureData[iRow])
        else:
            response = b"Capture Not Done"
        return response

    def getSlot(self, parameters):
        '''**RX:CAP:SLOT?** -
        Queries the selected Slot number for the SOH byte to be captured.
        '''
        return b""

    def setSlot(self, parameters):
        '''**RX:CAP:SLOT:<value>** -
        Sets the Slot number for the SOH byte to be captured.
        '''
        response = b""
        return response

    def getTrigger(self, parameters):
        '''**RX:CAP:TRIG?** -
        Queries the capture trigger setting.
        '''
        self.globals.veexOtn.sets.update()
        iTrigger = self.globals.veexOtn.sets.captureTrigger
        if iTrigger == veexlib.OTN_OH_TRIG_FRAME_ERROR:
            return b"FRAMEERROR"
        elif iTrigger == veexlib.OTN_OH_TRIG_BIT_ERROR:
            return b"BITERROR"
        elif iTrigger == veexlib.OTN_OH_TRIG_FEC_CORR_ERROR:
            return b"FECCORRERROR"
        elif iTrigger == veexlib.OTN_OH_TRIG_FEC_UNCORR_ERROR:
            return b"FECUNCORRERROR"
        elif iTrigger == veexlib.OTN_OH_TRIG_MFAS_ERROR:
            return b"MFASERROR"
        elif iTrigger == veexlib.OTN_OH_TRIG_OTU_BIP8_ERROR:
            return b"OTUBIP8ERROR"
        elif iTrigger == veexlib.OTN_OH_TRIG_OTU_BEI_ERROR:
            return b"OTUBEIERROR"
        elif iTrigger == veexlib.OTN_OH_TRIG_ODU_BIP8_ERROR:
            return b"ODUBIP8ERROR"
        elif iTrigger == veexlib.OTN_OH_TRIG_ODU_BEI_ERROR:
            return b"ODUBEIERROR"
        elif iTrigger == veexlib.OTN_OH_TRIG_OTU_LOM_ERROR:
            return b"LOMALARM"
        elif iTrigger == veexlib.OTN_OH_TRIG_OTU_OOM_ERROR:
            return b"OOMALARM"
        elif iTrigger == veexlib.OTN_OH_TRIG_OTU_AIS_ERROR:
            return b"OTUAISALARM"
        elif iTrigger == veexlib.OTN_OH_TRIG_OTU_IAE_ERROR:
            return b"OTUIAEALARM"
        elif iTrigger == veexlib.OTN_OH_TRIG_OTU_BDI_ERROR:
            return b"OTUBDIALARM"
        elif iTrigger == veexlib.OTN_OH_TRIG_ODU_AIS_ERROR:
            return b"ODUAISALARM"
        elif iTrigger == veexlib.OTN_OH_TRIG_ODU_OCI_ERROR:
            return b"ODUOCIALARM"
        elif iTrigger == veexlib.OTN_OH_TRIG_ODU_LCK_ERROR:
            return b"ODULCKALARM"
        elif iTrigger == veexlib.OTN_OH_TRIG_ODU_BDI_ERROR:
            return b"ODUBDIALARM"
        elif iTrigger == veexlib.OTN_OH_TRIG_POS_JUSTIFY:
            return b"POSJUSTIFY"
        elif iTrigger == veexlib.OTN_OH_TRIG_NEG_JUSTIFY:
            return b"NEGJUSTIFY"
        elif iTrigger == veexlib.OTN_OH_TRIG_BYTE_EQUAL:
            return b"BYTEEQUAL"
        elif iTrigger == veexlib.OTN_OH_TRIG_BYTE_NOT_EQUAL:
            return b"BYTENOTEQUAL"
        elif iTrigger == veexlib.OTN_OH_TRIG_MANUAL:
            return b"MANUAL"
        else:
            return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setTrigger(self, parameters):
        '''**RX:CAP:TRIG:<trigger>** -
        Sets the desired Capture Trigger option, used in the receive Overhead Byte Capture feature.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            matchValue = self.globals.veexOtn.sets.ohCaptureMatchValue
            byteSelect = self.globals.veexOtn.sets.ohCaptureByteSelect
            position = self.globals.veexOtn.sets.ohCapturePosition
            if paramList[0].head.upper().startswith(b"FRAMEERROR"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_FRAME_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"BITERROR"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_BIT_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"MFASERROR"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_MFAS_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"FECCORRERROR"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_FEC_CORR_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"FECUNCORRERROR"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_FEC_UNCORR_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"OTUBIP8ERROR"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_OTU_BIP8_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"OTUBEIERROR"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_OTU_BEI_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"ODUBIP8ERROR"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_ODU_BIP8_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"ODUBEIERROR"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_ODU_BEI_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"LOMALARM"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_OTU_LOM_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"OOMALARM"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_OTU_OOM_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"OTUAISALARM"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_OTU_AIS_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"OTUIAEALARM"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_OTU_IAE_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"OTUBDIALARM"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_OTU_BDI_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"ODUAISALARM"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_ODU_AIS_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"ODUOCIALARM"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_ODU_OCI_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"ODULCKALARM"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_ODU_LCK_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"ODUBDIALARM"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_ODU_BDI_ERROR,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"POSJUSTIFY"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_POS_JUSTIFY,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"NEGJUSTIFY"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_NEG_JUSTIFY,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"BYTEEQUAL"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_BYTE_EQUAL,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"BYTENOTEQUAL"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_BYTE_NOT_EQUAL,matchValue,position,byteSelect)
            elif paramList[0].head.upper().startswith(b"MANUAL"):
                self.globals.veexOtn.sets.setOhCaptureSettings(veexlib.OTN_OH_TRIG_MANUAL,matchValue,position,byteSelect)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxDataInvert(self, parameters):
        #'''**RX:DATAINVERT?** -
        #Queries the receive Data Inversion mode for the 43GHz NRZ-DPSK transponder.
        #'''
        self.globals.veexOtn.sets.update()
        if self.globals.veexOtn.sets.rxDataInvert == 1:
            return b"ON"
        elif self.globals.veexOtn.sets.rxDataInvert == 0:
            return b"OFF"
        else:
            return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRxDataInvert(self, parameters):
        #'''**RX:DATAINVERT <mode>** -
        #Enables or Disables the receive Data Inversion option for the 43GHz NRZ-DPSK transponder.
        #'''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ON"):
                self.globals.veexOtn.sets.rxDataInvert = 1
            elif paramList[0].head.upper().startswith(b"OFF"):
                self.globals.veexOtn.sets.rxDataInvert = 0
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxFec(self, parameters):
        '''**RX:FEC?** -
        Query the receive FEC mode setting.
        '''
        self.globals.veexOtn.sets.update()
        if self.globals.veexOtn.sets.rxFecDisable == 1:
            return b"DISABLED"
        elif self.globals.veexOtn.sets.rxFecDisable == 0:
            return b"ENABLED"
        else:
            return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRxFec(self, parameters):
        '''**RX:FEC:<mode>** -
        Sets the state of the receive Forward Error Correction (FEC) mode.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ENABLED"):
                self.globals.veexOtn.sets.rxFecDisable = 0
            elif paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.rxFecDisable = 1
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxMuxFlexRate(self, parameters):
        '''**RX:FLEXRATE?** -
        Query the received ODU Flex Data Rate, in Mbps.
        '''
        self.globals.veexOtn.stats.update()
        return b"%0.9f Mbps" % (self.globals.veexOtn.stats.rxFlexDataRate / 1.0e6,)

    def getRxMuxFlexRateExpected(self, parameters):
        '''**RX:FLEXRATEEXP?** -
        Queries the Expected received ODU Flex Data Rate, in Mbps.
        '''
        self.globals.veexOtn.sets.update()
        return b"%0.9f Mbps" % (self.globals.veexOtn.sets.rxFlexDataRateExpected / 1.0e6,)

    def setRxMuxFlexRateExpected(self, parameters):
        '''**RX:FLEXRATEEXP <rate>** -
        Set the Expected received ODU Flex Data Rate, in Mbps.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if ParseUtils.isFloatSdh(paramList[0].head):
                fVal = float(paramList[0].head)
                self.globals.veexOtn.sets.rxFlexDataRateExpected = fVal * 1.0e6
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxOpuJustLevel(self, parameters):
        '''**RX:FLEXRATEOFF?** -
        Query the received ODU Flex Frequency Offset value, in PPM.
        '''
        self.globals.veexOtn.stats.update()
        lineFreq = float(self.globals.veexOtn.stats.justFreqOffset)
#        self.globals.veexOtn.sets.update()
#        if self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODU_FLEX:
#            return b"%0.3f ppm" % lineFreq
#        else:
        return b"%0.2f ppm" % lineFreq

    def getRxFreq(self, parameters):
        '''**RX:FREQuency?** -
        Query the measured RX line frequency. Would use PHY stats, but that is
        per lane.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d Hz" % self.globals.veexOtn.stats.freqRx

    def getRxFreqOffsetPpm(self, parameters):
        '''**RX:FREQOFFset:PPM?** -
        Query the offset from nominal measured RX line frequency in PPM.
        Would use PHY stats, but that is per lane.
        '''
        self.globals.veexOtn.stats.update()
        return b"%0.2f ppm" % self.globals.veexOtn.stats.freqOffsetRxPpm

    def getRxFreqOffsetHz(self, parameters):
        '''**RX:FREQOFFset:HZ?** -
        Query the offset from nominal measured RX line frequency in Hz.
        Would use PHY stats, but that is per lane.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d Hz" % self.globals.veexOtn.stats.freqOffsetRxHz

    def getRxInterface(self, parameters):
        '''**RX:INTerface?** -
        Query the selected receive interface.
        '''
        self.globals.veexOtn.sets.update()
        if self.globals.veexOtn.sets.rxInterface in ScpiOtn.InterfaceTable.keys():
            response = ScpiOtn.InterfaceTable[self.globals.veexOtn.sets.rxInterface]
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setRxInterface(self, parameters):
        '''**RX:INTerface:<interface>** -
        Sets the receive OTN, ETHERNET, FIBRE CHANNEL or CPRI interface rate/speed/type,
        for the specified Module types.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for key, value in ScpiOtn.InterfaceTable.items():
                if paramList[0].head.upper().startswith(value):
                    self.globals.veexOtn.sets.rxInterface = key
                    return None
            response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxMapping(self, parameters):
        '''**RX:MAPping?** -
        Query the selected receive mapping for the OTN processor.
        '''
        self.globals.veexOtn.sets.update()
        paramCount = 1
        response = b""
        if self.globals.veexOtn.sets.odtu3RxMapping != veexlib.OTN_MAP_NONE:
            paramCount += 1
        if self.globals.veexOtn.sets.odtu2RxMapping != veexlib.OTN_MAP_NONE:
            paramCount += 1
        if self.globals.veexOtn.sets.odtu1RxMapping != veexlib.OTN_MAP_NONE:
            paramCount += 1
        for i in range(paramCount):
            if len(response) == 0:
                mapping = self.globals.veexOtn.sets.rxMapping
            elif self.globals.veexOtn.sets.odtu3RxMapping != veexlib.OTN_MAP_NONE:
                mapping = self.globals.veexOtn.sets.odtu3RxMapping
            elif self.globals.veexOtn.sets.odtu2RxMapping != veexlib.OTN_MAP_NONE:
                mapping = self.globals.veexOtn.sets.odtu2RxMapping
            elif self.globals.veexOtn.sets.odtu1RxMapping != veexlib.OTN_MAP_NONE:
                mapping = self.globals.veexOtn.sets.odtu1RxMapping

            if mapping == veexlib.OTN_MAP_UNFRAMED_BERT:
                response += b"UNFRAMED_BERT"
            elif mapping == veexlib.OTN_MAP_SONET_SDH_ASYNC:
                response += b"SONETSDH_ASYNC"
            elif mapping == veexlib.OTN_MAP_SONET_SDH_SYNC:
                response += b"SONETSDH_SYNC"
            elif mapping == veexlib.OTN_MAP_OPU_PRBS:
                response += b"PRBS"
            elif mapping == veexlib.OTN_MAP_OPU_NULL:
                response += b"NULL_CLIENT"
            elif mapping == veexlib.OTN_MAP_OPU_GFP:
                response += b"OPU_GFP"
            elif mapping == veexlib.OTN_MAP_OPU_WAN:
                response += b"OPU_WAN"
            elif mapping == veexlib.OTN_MAP_ETHERNET:
                response += b"OPU_LAN"
            elif mapping == veexlib.OTN_MAP_ODTU_12_PT_20:
                if self.globals.veexOtn.sets.isRxMultiChanMapping == True:
                    response += b"MULTI_ODTU12"
                else:
                    response += b"ODTU12"
            elif mapping == veexlib.OTN_MAP_ODU2E_ETHERNET_SYNC:
                response += b"OPU_LAN_SYNC"
            elif mapping == veexlib.OTN_MAP_ODU2E_ETHERNET_ASYNC:
                response += b"OPU_LAN_ASYNC"    
            elif mapping == veexlib.OTN_MAP_ODTU_13_PT_20:
                if self.globals.veexOtn.sets.isRxMultiChanMapping == True:
                    response += b"MULTI_ODTU13"
                else:
                    response += b"ODTU13"
            elif mapping == veexlib.OTN_MAP_ODTU_23_PT_20:
                if self.globals.veexOtn.sets.isRxMultiChanMapping == True:
                    response += b"MULTI_ODTU23"
                else:
                    response += b"ODTU23"  
            elif mapping == veexlib.OTN_MAP_ODTU_01_PT_20:
                if self.globals.veexOtn.sets.isRxMultiChanMapping == True:
                    response += b"MULTI_ODTU01"
                else:
                    response += b"ODTU01"  
            elif mapping == veexlib.OTN_MAP_ODU_FLEX_PT_21:
                response += b"ODUFLEX"
            elif mapping == veexlib.OTN_MAP_ODU3E_ETHERNET:
                response += b"QUAD_10G_LAN"
            elif mapping == veexlib.OTN_MAP_OPU_GFP_EXTENDED:
                response += b"GFP_10G_LAN"
            elif mapping == veexlib.OTN_MAP_FIBRECHAN:
                response += b"FIBRECHAN"
            elif mapping == veexlib.OTN_MAP_ODU2F_FIBRECHAN_SYNC:
                response += b"OPU_FIBRECHAN_SYNC"
            elif mapping == veexlib.OTN_MAP_ODU2F_FIBRECHAN_ASYNC:
                response += b"OPU_FIBRECHAN_ASYNC"
            elif mapping == veexlib.OTN_MAP_ODTU_02_PT_21:
                if self.globals.veexOtn.sets.isRxMultiChanMapping == True:
                    response += b"MULTI_ODTU02"
                else:
                    response += b"ODTU02" 
            elif mapping == veexlib.OTN_MAP_ODTU_03_PT_21:
                if self.globals.veexOtn.sets.isRxMultiChanMapping == True:
                    response += b"MULTI_ODTU03"
                else:
                    response += b"ODTU03" 
            elif mapping == veexlib.OTN_MAP_ODTU_04_PT_21:
                if self.globals.veexOtn.sets.isRxMultiChanMapping == True:
                    response += b"MULTI_ODTU04"
                else:
                    response += b"ODTU04" 
            elif mapping == veexlib.OTN_MAP_OPU_40G_ETHERNET:
                response += b"OPU_41G_LAN"
            elif mapping == veexlib.OTN_MAP_OPU_100G_ETHERNET:
                response += b"OPU_103G_LAN"
            elif mapping == veexlib.OTN_MAP_ODTU_14_PT_21:
                if self.globals.veexOtn.sets.isRxMultiChanMapping == True:
                    response += b"MULTI_ODTU14"
                else:
                    response += b"ODTU14" 
            elif mapping == veexlib.OTN_MAP_ODTU_24_PT_21:
                if self.globals.veexOtn.sets.isRxMultiChanMapping == True:
                    response += b"MULTI_ODTU24"
                else:
                    response += b"ODTU24"         
            elif mapping == veexlib.OTN_MAP_ODTU_34_PT_21:
                response += b"ODTU34"
            elif mapping == veexlib.OTN_MAP_ODTU_2E3_PT_21:
                response += b"ODTU2E3"
            elif mapping == veexlib.OTN_MAP_ODTU_2E4_PT_21:
                if self.globals.veexOtn.sets.isRxMultiChanMapping == True:
                    response += b"MULTI_ODTU2E4"
                else:
                    response += b"ODTU2E4"
            
            elif mapping == veexlib.OTN_MAP_ODTU_12_PT_21:
                if self.globals.veexOtn.sets.isRxMultiChanMapping == True:
                    response += b"MULTI_ODTU12_PT_21"
                else:
                    response += b"ODTU12_PT_21"   
            elif mapping == veexlib.OTN_MAP_ODTU_13_PT_21:
                if self.globals.veexOtn.sets.isRxMultiChanMapping == True:
                    response += b"MULTI_ODTU13_PT_21"
                else:
                    response += b"ODTU13_PT_21"   
            elif mapping == veexlib.OTN_MAP_ODTU_23_PT_21:
                if self.globals.veexOtn.sets.isRxMultiChanMapping == True:
                    response += b"MULTI_ODTU23_PT_21"
                else:
                    response += b"ODTU23_PT_21"   
            elif mapping == veexlib.OTN_MAP_OPU_40G_ETHERNET_PRBS:
                response += b"OPU_41G_PRBS"
            elif mapping == veexlib.OTN_MAP_OPU_40G_ETHERNET_NULL:
                response += b"OPU_41G_NULL"
            else:
                return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
            if i != paramCount - 1:
                response += b","
        return response

    def setRxMapping(self, parameters):
        '''**RX:MAPping:<mapping>** -
        Sets the receive mapping, for the specified Circuit Pack types, based on the unit!/s licensed configuration.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            rxMapping = veexlib.OTN_MAP_NONE
            odtu1Mapping = veexlib.OTN_MAP_NONE
            odtu2Mapping = veexlib.OTN_MAP_NONE
            odtu3Mapping = veexlib.OTN_MAP_NONE
            muxRxIsParallelMapping = False
            for paramCount in range(len(paramList)):
                if paramList[paramCount].head.upper().startswith(b"UNFRAMED_BERT"):
                    mapping = veexlib.OTN_MAP_UNFRAMED_BERT
                elif paramList[paramCount].head.upper().startswith(b"SONETSDH_ASYNC"):
                    mapping = veexlib.OTN_MAP_SONET_SDH_ASYNC
                elif paramList[paramCount].head.upper().startswith(b"SONETSDH_SYNC"):
                    mapping = veexlib.OTN_MAP_SONET_SDH_SYNC
                elif paramList[paramCount].head.upper().startswith(b"PRBS"):
                    mapping = veexlib.OTN_MAP_OPU_PRBS
                elif paramList[paramCount].head.upper().startswith(b"NULL_CLIENT"):
                    mapping = veexlib.OTN_MAP_OPU_NULL
                elif paramList[paramCount].head.upper().startswith(b"OPU_GFP"):
                    mapping = veexlib.OTN_MAP_OPU_GFP
                elif paramList[paramCount].head.upper().startswith(b"OPU_WAN"):
                    mapping = veexlib.OTN_MAP_OPU_WAN
                elif paramList[paramCount].head.upper().startswith(b"OPU_LAN"):
                    mapping = veexlib.OTN_MAP_ETHERNET
                elif paramList[paramCount].head.upper().startswith(b"ODTU12_PT_21"):
                    mapping = veexlib.OTN_MAP_ODTU_12_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU12"):
                    mapping = veexlib.OTN_MAP_ODTU_12_PT_20
                elif paramList[paramCount].head.upper().startswith(b"OPU_LAN_SYNC"):
                    mapping = veexlib.OTN_MAP_ODU2E_ETHERNET_SYNC
                elif paramList[paramCount].head.upper().startswith(b"OPU_LAN_ASYNC"):
                    mapping = veexlib.OTN_MAP_ODU2E_ETHERNET_ASYNC
                elif paramList[paramCount].head.upper().startswith(b"ODTU13_PT_21"):
                    mapping = veexlib.OTN_MAP_ODTU_13_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU13"):
                    mapping = veexlib.OTN_MAP_ODTU_13_PT_20
                elif paramList[paramCount].head.upper().startswith(b"ODTU23_PT_21"):
                    mapping = veexlib.OTN_MAP_ODTU_23_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU23"):
                    mapping = veexlib.OTN_MAP_ODTU_23_PT_20
                elif paramList[paramCount].head.upper().startswith(b"ODTU01"):
                    mapping = veexlib.OTN_MAP_ODTU_01_PT_20
                elif paramList[paramCount].head.upper().startswith(b"ODUFLEX"):
                    mapping = veexlib.OTN_MAP_ODU_FLEX_PT_21
                elif paramList[paramCount].head.upper().startswith(b"QUAD_10G_LAN"):
                    mapping = veexlib.OTN_MAP_ODU3E_ETHERNET
                elif paramList[paramCount].head.upper().startswith(b"GFP_10G_LAN"):
                    mapping = veexlib.OTN_MAP_OPU_GFP_EXTENDED
                elif paramList[paramCount].head.upper().startswith(b"FIBRECHAN"):
                    mapping = veexlib.OTN_MAP_FIBRECHAN
                elif paramList[paramCount].head.upper().startswith(b"OPU_FIBRECHAN_SYNC"):
                    mapping = veexlib.OTN_MAP_ODU2F_FIBRECHAN_SYNC
                elif paramList[paramCount].head.upper().startswith(b"OPU_FIBRECHAN_ASYNC"):
                    mapping = veexlib.OTN_MAP_ODU2F_FIBRECHAN_ASYNC
                elif paramList[paramCount].head.upper().startswith(b"ODTU02"):
                    mapping = veexlib.OTN_MAP_ODTU_02_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU03"):
                    mapping = veexlib.OTN_MAP_ODTU_03_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU04"):
                    mapping = veexlib.OTN_MAP_ODTU_04_PT_21
                elif paramList[paramCount].head.upper().startswith(b"4G_FIBRECHAN"):
                    mapping = veexlib.OTN_MAP_ODU_FLEX_4G_FC
                elif paramList[paramCount].head.upper().startswith(b"8_5G_FIBRECHAN"):
                    mapping = veexlib.OTN_MAP_ODU_FLEX_8G_FC
                elif paramList[paramCount].head.upper().startswith(b"OPU_41G_LAN"):
                    mapping = veexlib.OTN_MAP_OPU_40G_ETHERNET
                elif paramList[paramCount].head.upper().startswith(b"OPU_103G_LAN"):
                    mapping = veexlib.OTN_MAP_OPU_100G_ETHERNET
                elif paramList[paramCount].head.upper().startswith(b"ODTU14"):
                    mapping = veexlib.OTN_MAP_ODTU_14_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU24"):
                    mapping = veexlib.OTN_MAP_ODTU_24_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU34"):
                    mapping = veexlib.OTN_MAP_ODTU_34_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU2E3"):
                    mapping = veexlib.OTN_MAP_ODTU_2E3_PT_21
                elif paramList[paramCount].head.upper().startswith(b"ODTU2E3"):
                    mapping = veexlib.OTN_MAP_ODTU_2E4_PT_21
                elif paramList[paramCount].head.upper().startswith(b"OPU_41G_PRBS"):
                    mapping = veexlib.OTN_MAP_OPU_40G_ETHERNET_PRBS
                elif paramList[paramCount].head.upper().startswith(b"OPU_41G_NULL"):
                    mapping = veexlib.OTN_MAP_OPU_40G_ETHERNET_NULL
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU03"):
                    mapping = veexlib.OTN_MAP_ODTU_03_PT_21
                    muxRxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU13_PT_21"):
                    mapping = veexlib.OTN_MAP_ODTU_13_PT_21
                    muxRxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU13"):
                    mapping = veexlib.OTN_MAP_ODTU_13_PT_21
                    muxRxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU23_PT_21"):
                    mapping = veexlib.OTN_MAP_ODTU_23_PT_21
                    muxRxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU23"):
                    mapping = veexlib.OTN_MAP_ODTU_23_PT_20
                    muxRxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU04"):
                    mapping = veexlib.OTN_MAP_ODTU_04_PT_21
                    muxRxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU14"):
                    mapping = veexlib.OTN_MAP_ODTU_14_PT_21
                    muxRxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU24"):
                    mapping = veexlib.OTN_MAP_ODTU_24_PT_21
                    muxRxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU2E4"):
                    mapping = veexlib.OTN_MAP_ODTU_2E4_PT_21
                    muxRxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU01"):
                    mapping = veexlib.OTN_MAP_ODTU_01_PT_20
                    muxRxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU02"):
                    mapping = veexlib.OTN_MAP_ODTU_02_PT_21
                    muxRxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU12_PT_21"):
                    mapping = veexlib.OTN_MAP_ODTU_12_PT_21
                    muxRxIsParallelMapping = True
                elif paramList[paramCount].head.upper().startswith(b"MULTI_ODTU12"):
                    mapping = veexlib.OTN_MAP_ODTU_12_PT_20
                    muxRxIsParallelMapping = True
                else:
                    return self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)

                if paramCount == 0:
                    rxMapping = mapping
                elif paramCount == 1:
                    odtu3Mapping = mapping
                elif paramCount == 2:
                    odtu2Mapping = mapping
                elif paramCount == 3:
                    odtu1Mapping = mapping
            if len(paramList) == 1 and rxMapping != veexlib.OTN_MAP_ODTU_34_PT_21:
                if (rxMapping == veexlib.OTN_MAP_ODTU_24_PT_21) or \
                   (rxMapping == veexlib.OTN_MAP_ODTU_23_PT_21) or \
                   (rxMapping == veexlib.OTN_MAP_ODTU_23_PT_20):
                    odtu2Mapping = odtu3Mapping;
                else:
                    odtu1Mapping = odtu3Mapping;
                odtu3Mapping = veexlib.OTN_MAP_NONE
            elif len(paramList) == 2 and rxMapping != veexlib.OTN_MAP_ODTU_34_PT_21:    
                if (rxMapping == veexlib.OTN_MAP_ODTU_24_PT_21) or \
                   (rxMapping == veexlib.OTN_MAP_ODTU_23_PT_21) or \
                   (rxMapping == veexlib.OTN_MAP_ODTU_23_PT_20):
                    odtu1Mapping = odtu2Mapping;
                    odtu2Mapping = odtu3Mapping;
                    odtu3Mapping = veexlib.OTN_MAP_NONE
            elif len(paramList) == 2 and rxMapping == veexlib.OTN_MAP_ODTU_34_PT_21:
                if (odtu3Mapping == veexlib.OTN_MAP_ODTU_13_PT_20) or \
                   (odtu3Mapping == veexlib.OTN_MAP_ODTU_13_PT_21):
                    odtu1Mapping = odtu2Mapping;
                    odtu2Mapping = veexlib.OTN_MAP_NONE 
            elif len(paramList) == 2 and rxMapping == veexlib.OTN_MAP_ODTU_12_PT_21:
                # Special case for old interface 'PB_OTN_MAP_ODTU_012_PT_21', change to mutli-level
                if odtu3Mapping == veexlib.OTN_MAP_ODTU_01_PT_20:
                    odtu1Mapping = odtu3Mapping
                    odtu3Mapping = veexlib.OTN_MAP_NONE
            elif len(paramList) == 2 and rxMapping == veexlib.OTN_MAP_ODTU_12_PT_20:
                # Special case for old interface 'PB_OTN_MAP_ODTU_012_PT_20', change to mutli-level
                if odtu3Mapping == veexlib.OTN_MAP_ODTU_01_PT_20:
                    odtu1Mapping = odtu3Mapping
                    odtu3Mapping = veexlib.OTN_MAP_NONE
                
            # Double Check : Is it need to handle the presend route here?
            if muxRxIsParallelMapping == False:
                self.globals.veexOtn.sets.setRxMapping(rxMapping,odtu3Mapping,odtu2Mapping,odtu1Mapping)
            else:
                self.globals.veexOtn.sets.setRxMultiChanMapping(rxMapping)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxMultiChanPattern(self, parameters):
        '''**RX:MCPATT?** -
        Queries the expected ODU Multi-Channel mapping structures for the ODU-n Add/Drop MUX mapping.
        '''
        self.globals.veexOtn.sets.update()
        return b"TBD"

    def setRxMultiChanPattern(self, parameters):
        '''**RX:MCPATT <structure>** -
        Sets entire receive ODU-n Multi-Channel mapping structures for multi-channel ODTU mappings,
        including each channel!/s individual payload pattern, and ODU-0 Tributary Slot #!/s if applicable.
        '''
        return b"TBD"

    def getRxOduPm(self, parameters):
        '''**RX:ODUPM?** -
        Queries the mode of the ODU PM TIM Alarm Reporting option.
        '''
        self.globals.veexOtn.sets.update()
        if self.globals.veexOtn.sets.oduPmTimAlarmEnable == True:
            return b"ENABLED"
        elif self.globals.veexOtn.sets.oduPmTimAlarmEnable == False:
            return b"DISABLED"
        else:
            return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setRxOduPm(self, parameters):
        '''**RX:ODUPM:<option>** -
        Sets the mode of the ODU PM TIM Alarm Reporting option.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ENABLED"):
                self.globals.veexOtn.sets.oduPmTimAlarmEnable = True
            elif paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.oduPmTimAlarmEnable = False
            else:
                return self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            return self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def rxOhTcm1Bei(self, parameters):
        '''**RX:OH:TCM1:BEI?** -
        Query the RX TCM1 BEI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM1_BEI]

    def rxOhTcm1Bip8(self, parameters):
        '''**RX:OH:TCM1:BIP8?** -
        Query the RX TCM1 BIP8 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM1_BIP]

    def rxOhTcm1Dapi(self, parameters):
        '''**RX:OH:TCM1:DAPI?** -
        Query the RX TCM1 DAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.oduTcmTtiDapi[0].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm1DapiExp(self, parameters):
        '''**RX:OH:TCM1:DAPIEXP?** -
        Query the RX TCM1 DAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[0].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm1Sapi(self, parameters):
        '''**RX:OH:TCM1:SAPI?** -
        Query the RX TCM1 SAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.oduTcmTtiSapi[0].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm1SapiExp(self, parameters):
        '''**RX:OH:TCM1:SAPIEXP?** -
        Query the RX TCM1 SAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[0].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm1Specific(self, parameters):
        '''**RX:OH:TCM1:SPECIFIC?** -
        Query the RX TCM1 SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return self.globals.veexOtn.stats.oduTcmTtiSpecific[0].encode()[:]

    def rxOhTcm1Tti(self, parameters):
        '''**RX:OH:TCM1:TTI?** -
        Query the RX TCM1 TTI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM1_TTI]

    def rxOhTcm2Bei(self, parameters):
        '''**RX:OH:TCM2:BEI?** -
        Query the RX TCM2 BEI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM2_BEI]

    def rxOhTcm2Bip8(self, parameters):
        '''**RX:OH:TCM2:BIP8?** -
        Query the RX TCM2 BIP8 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM2_BIP]

    def rxOhTcm2Dapi(self, parameters):
        '''**RX:OH:TCM2:DAPI?** -
        Query the RX TCM2 DAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.oduTcmTtiDapi[1].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm2DapiExp(self, parameters):
        '''**RX:OH:TCM2:DAPIEXP?** -
        Query the RX TCM2 DAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[1].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm2Sapi(self, parameters):
        '''**RX:OH:TCM2:SAPI?** -
        Query the RX TCM2 SAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.oduTcmTtiSapi[1].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm2SapiExp(self, parameters):
        '''**RX:OH:TCM2:SAPIEXP?** -
        Query the RX TCM2 SAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[1].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm2Specific(self, parameters):
        '''**RX:OH:TCM2:SPECIFIC?** -
        Query the RX TCM2 SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return self.globals.veexOtn.stats.oduTcmTtiSpecific[1].encode()[:]

    def rxOhTcm2Tti(self, parameters):
        '''**RX:OH:TCM2:TTI?** -
        Query the RX TCM2 TTI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM2_TTI]

    def rxOhTcm3Bei(self, parameters):
        '''**RX:OH:TCM3:BEI?** -
        Query the RX TCM3 BEI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM3_BEI]

    def rxOhTcm3Bip8(self, parameters):
        '''**RX:OH:TCM3:BIP8?** -
        Query the RX TCM3 BIP8 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM3_BIP]


    def rxOhTcm3Dapi(self, parameters):
        '''**RX:OH:TCM3:DAPI?** -
        Query the RX TCM3 DAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.oduTcmTtiDapi[2].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm3DapiExp(self, parameters):
        '''**RX:OH:TCM3:DAPIEXP?** -
        Query the RX TCM3 DAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[2].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm3Sapi(self, parameters):
        '''**RX:OH:TCM3:SAPI?** -
        Query the RX TCM3 SAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.oduTcmTtiSapi[2].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm3SapiExp(self, parameters):
        '''**RX:OH:TCM3:SAPIEXP?** -
        Query the RX TCM3 SAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[2].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm3Specific(self, parameters):
        '''**RX:OH:TCM3:SPECIFIC?** -
        Query the RX TCM3 SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return self.globals.veexOtn.stats.oduTcmTtiSpecific[2].encode()[:]

    def rxOhTcm3Tti(self, parameters):
        '''**RX:OH:TCM3:TTI?** -
        Query the RX TCM3 TTI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM3_TTI]

    def rxOhTcm4Bei(self, parameters):
        '''**RX:OH:TCM4:BEI?** -
        Query the RX TCM4 BEI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM4_BEI]

    def rxOhTcm4Bip8(self, parameters):
        '''**RX:OH:TCM4:BIP8?** -
        Query the RX TCM4 BIP8 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM4_BIP]


    def rxOhTcm4Dapi(self, parameters):
        '''**RX:OH:TCM4:DAPI?** -
        Query the RX TCM4 DAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.oduTcmTtiDapi[3].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm4DapiExp(self, parameters):
        '''**RX:OH:TCM4:DAPIEXP?** -
        Query the RX TCM4 DAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[3].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm4Sapi(self, parameters):
        '''**RX:OH:TCM4:SAPI?** -
        Query the RX TCM4 SAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.oduTcmTtiSapi[3].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm4SapiExp(self, parameters):
        '''**RX:OH:TCM4:SAPIEXP?** -
        Query the RX TCM4 SAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[3].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm4Specific(self, parameters):
        '''**RX:OH:TCM4:SPECIFIC?** -
        Query the RX TCM4 SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return self.globals.veexOtn.stats.oduTcmTtiSpecific[3].encode()[:]

    def rxOhTcm4Tti(self, parameters):
        '''**RX:OH:TCM4:TTI?** -
        Query the RX TCM4 TTI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM4_TTI]

    def rxOhTcm5Bei(self, parameters):
        '''**RX:OH:TCM5:BEI?** -
        Query the RX TCM5 BEI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM5_BEI]

    def rxOhTcm5Bip8(self, parameters):
        '''**RX:OH:TCM5:BIP8?** -
        Query the RX TCM5 BIP8 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM5_BIP]

    def rxOhTcm5Dapi(self, parameters):
        '''**RX:OH:TCM5:DAPI?** -
        Query the RX TCM5 DAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.oduTcmTtiDapi[4].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm5DapiExp(self, parameters):
        '''**RX:OH:TCM5:DAPIEXP?** -
        Query the RX TCM5 DAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[4].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm5Sapi(self, parameters):
        '''**RX:OH:TCM5:SAPI?** -
        Query the RX TCM5 SAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.oduTcmTtiSapi[4].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm5SapiExp(self, parameters):
        '''**RX:OH:TCM5:SAPIEXP?** -
        Query the RX TCM5 SAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[4].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm5Specific(self, parameters):
        '''**RX:OH:TCM5:SPECIFIC?** -
        Query the RX TCM5 SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return self.globals.veexOtn.stats.oduTcmTtiSpecific[4].encode()[:]

    def rxOhTcm5Tti(self, parameters):
        '''**RX:OH:TCM5:TTI?** -
        Query the RX TCM5 TTI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM5_TTI]

    def rxOhTcm6Bei(self, parameters):
        '''**RX:OH:TCM6:BEI?** -
        Query the RX TCM6 BEI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM6_BEI]

    def rxOhTcm6Bip8(self, parameters):
        '''**RX:OH:TCM6:BIP8?** -
        Query the RX TCM6 BIP8 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM6_BIP]

    def rxOhTcm6Dapi(self, parameters):
        '''**RX:OH:TCM6:DAPI?** -
        Query the RX TCM6 DAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.oduTcmTtiDapi[5].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm6DapiExp(self, parameters):
        '''**RX:OH:TCM6:DAPIEXP?** -
        Query the RX TCM6 DAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[5].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm6Sapi(self, parameters):
        '''**RX:OH:TCM6:SAPI?** -
        Query the RX TCM6 SAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.oduTcmTtiSapi[5].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm6SapiExp(self, parameters):
        '''**RX:OH:TCM6:SAPIEXP?** -
        Query the RX TCM6 SAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[5].encode()[:]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhTcm6Specific(self, parameters):
        '''**RX:OH:TCM6:SPECIFIC?** -
        Query the RX TCM6 SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return self.globals.veexOtn.stats.oduTcmTtiSpecific[5].encode()[:]

    def rxOhTcm6Tti(self, parameters):
        '''**RX:OH:TCM6:TTI?** -
        Query the RX TCM6 TTI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM6_TTI]

    def rxOhTcm1SapiExpt(self, parameters):
        '''**RX:OH:TCM1:SAPIEXP** -
        Sets the expected receive value for the TCM1 SAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            dapi = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[0].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(1,sapi,dapi)
        else:
            dapi = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[0].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(1,b"",dapi)
        return response

    def rxOhTcm1DapiExpt(self, parameters):
        '''**RX:OH:TCM1:DAPIEXP** -
        Sets the expected receive value for the TCM1 DAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            sapi = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[0].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(1,sapi,dapi)
        else:
            sapi = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[0].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(1,sapi,b"")
        return response

    def rxOhTcm2SapiExpt(self, parameters):
        '''**RX:OH:TCM2:SAPIEXP** -
        Sets the expected receive value for the TCM2 SAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            dapi = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[1].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(2,sapi,dapi)
        else:
            dapi = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[1].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(2,b"",dapi)
        return response

    def rxOhTcm2DapiExpt(self, parameters):
        '''**RX:OH:TCM2:DAPIEXP** -
        Sets the expected receive value for the TCM2 DAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            sapi = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[1].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(2,sapi,dapi)
        else:
            sapi = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[1].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(2,sapi,b"")
        return response

    def rxOhTcm3SapiExpt(self, parameters):
        '''**RX:OH:TCM3:SAPIEXP** -
        Sets the expected receive value for the TCM3 SAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            dapi = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[2].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(3,sapi,dapi)
        else:
            dapi = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[2].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(3,b"",dapi)
        return response

    def rxOhTcm3DapiExpt(self, parameters):
        '''**RX:OH:TCM3:DAPIEXP** -
        Sets the expected receive value for the TCM3 DAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            sapi = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[2].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(3,sapi,dapi)
        else:
            sapi = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[2].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(3,sapi,b"")
        return response

    def rxOhTcm4SapiExpt(self, parameters):
        '''**RX:OH:TCM4:SAPIEXP** -
        Sets the expected receive value for the TCM4 SAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            dapi = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[3].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(4,sapi,dapi)
        else:
            dapi = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[3].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(4,b"",dapi)
        return response

    def rxOhTcm4DapiExpt(self, parameters):
        '''**RX:OH:TCM4:DAPIEXP** -
        Sets the expected receive value for the TCM4 DAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            sapi = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[3].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(4,sapi,dapi)
        else:
            sapi = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[3].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(4,sapi,b"")
        return response

    def rxOhTcm5SapiExpt(self, parameters):
        '''**RX:OH:TCM5:SAPIEXP** -
        Sets the expected receive value for the TCM5 SAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            dapi = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[4].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(5,sapi,dapi)
        else:
            dapi = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[4].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(5,b"",dapi)
        return response

    def rxOhTcm5DapiExpt(self, parameters):
        '''**RX:OH:TCM5:DAPIEXP** -
        Sets the expected receive value for the TCM5 DAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            sapi = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[4].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(5,sapi,dapi)
        else:
            sapi = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[4].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(5,sapi,b"")
        return response

    def rxOhTcm6SapiExpt(self, parameters):
        '''**RX:OH:TCM6:SAPIEXP** -
        Sets the expected receive value for the TCM6 SAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            dapi = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[5].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(6,sapi,dapi)
        else:
            dapi = self.globals.veexOtn.sets.oduTcmTtiExpectedDapi[5].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(6,b"",dapi)
        return response

    def rxOhTcm6DapiExpt(self, parameters):
        '''**RX:OH:TCM6:DAPIEXP** -
        Sets the expected receive value for the TCM6 DAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            sapi = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[5].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(6,sapi,dapi)
        else:
            sapi = self.globals.veexOtn.sets.oduTcmTtiExpectedSapi[5].encode()[:15]
            self.globals.veexOtn.sets.setOduTcmTtiExpected(6,sapi,b"")
        return response

    def rxOhOdu2Aps1(self, parameters):
        '''**RX:OH:ODU:APS1?** -
        Query the specified ODU APS1 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_APS_PCC_1]

    def rxOhOdu2Aps2(self, parameters):
        '''**RX:OH:ODU:APS2?** -
        Query the specified ODU APS2 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_APS_PCC_2]

    def rxOhOdu2Aps3(self, parameters):
        '''**RX:OH:ODU:APS3?** -
        Query the specified ODU APS3 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_APS_PCC_3]

    def rxOhOdu2Aps4(self, parameters):
        '''**RX:OH:ODU:APS4?** -
        Query the specified ODU APS4 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_APS_PCC_4]

    def rxOhOdu1Bei(self, parameters):
        '''**RX:OH:ODU:BEI?** -
        Query the specified ODU BEI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_PM_BEI]

    def rxOhOdu1BfFault(self, parameters):
        '''**RX:OH:ODU:BFTFL:FAULT?** -
        Query the specified ODU BFTFL FAULT overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduBackwardFtflFault

    def rxOhOdu1BfOi(self, parameters):
        '''**RX:OH:ODU:BFTFL:OI?** -
        Query the specified ODU BFTFL OI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return self.globals.veexOtn.stats.oduBackwardFtflOI.encode()[:9]

    def rxOhOdu1BfOs(self, parameters):
        '''**RX:OH:ODU:BFTFL:OS?** -
        Query the specified ODU BFTFL OS overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return self.globals.veexOtn.stats.oduBackwardFtflOS.encode()[:118]

    def rxOhOdu1Dapi(self, parameters):
        '''**RX:OH:ODU:DAPI?** -
        Query the specified ODU DAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.oduPmTtiDapi.encode()[:15]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhOdu1DapiExp(self, parameters):
        '''**RX:OH:ODU:DAPIEXP?** -
        Query the specified ODU DAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduPmTtiExpectedDapi.encode()[:15]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhOdu2Exp1(self, parameters):
        '''**RX:OH:ODU:EXP1?** -
        Query the specified ODU EXP1 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_EXP_1]

    def rxOhOdu2Exp2(self, parameters):
        '''**RX:OH:ODU:EXP2?** -
        Query the specified ODU EXP2 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_EXP_2]

    def rxOhOdu1FfFault(self, parameters):
        '''**RX:OH:ODU:FFTFL:FAULT?** -
        Query the specified ODU FFTFL FAULT overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduForwardFtflFault

    def rxOhOdu1FfOi(self, parameters):
        '''**RX:OH:ODU:FFTFL:OI?** -
        Query the specified ODU FFTFL OI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return self.globals.veexOtn.stats.oduForwardFtflOI.encode()[:9]

    def rxOhOdu1FfOs(self, parameters):
        '''**RX:OH:ODU:FFTFL:OS?** -
        Query the specified ODU FFTFL OS overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return self.globals.veexOtn.stats.oduForwardFtflOS.encode()[:118]

    def rxOhOdu2Gcc11(self, parameters):
        '''**RX:OH:ODU:GCC11?** -
        Query the specified ODU GCC11 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_GCC1_1]

    def rxOhOdu2Gcc12(self, parameters):
        '''**RX:OH:ODU:GCC12?** -
        Query the specified ODU GCC12 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_GCC1_2]

    def rxOhOdu2Gcc21(self, parameters):
        '''**RX:OH:ODU:GCC21?** -
        Query the specified ODU GCC21 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_GCC2_1]


    def rxOhOdu2Gcc22(self, parameters):
        '''**RX:OH:ODU:GCC22?** -
        Query the specified ODU GCC22 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_GCC2_2]

    def rxOhOdu2Res1(self, parameters):
        '''**RX:OH:ODU:RES1?** -
        Query the specified ODU RES1 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_RES_1]

    def rxOhOdu2Res2(self, parameters):
        '''**RX:OH:ODU:RES2?** -
        Query the specified ODU RES2 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_RES_2]

    def rxOhOdu2Res3(self, parameters):
        '''**RX:OH:ODU:PMANDTCM?** -
        Query the specified ODU PMANDTCM overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_RES_3]

    def rxOhOdu2Res4(self, parameters):
        '''**RX:OH:ODU:RES4?** -
        Query the specified ODU RES4 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_RES_4]

    def rxOhOdu2Res5(self, parameters):
        '''**RX:OH:ODU:RES5?** -
        Query the specified ODU RES5 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_RES_5]

    def rxOhOdu2Res6(self, parameters):
        '''**RX:OH:ODU:RES6?** -
        Query the specified ODU RES6 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_RES_6]

    def rxOhOdu2Res7(self, parameters):
        '''**RX:OH:ODU:RES7?** -
        Query the specified ODU RES7 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_RES_7]

    def rxOhOdu2Res8(self, parameters):
        '''**RX:OH:ODU:RES8?** -
        Query the specified ODU RES8 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_RES_8]

    def rxOhOdu2Res9(self, parameters):
        '''**RX:OH:ODU:RES9?** -
        Query the specified ODU RES9 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_RES_9]

    def rxOhOdu1Sapi(self, parameters):
        '''**RX:OH:ODU:SAPI?** -
        Query the specified ODU SAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.oduPmTtiSapi.encode()[:15]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhOdu1SapiExp(self, parameters):
        '''**RX:OH:ODU:SAPIEXP?** -
        Query the specified ODU SAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.oduPmTtiExpectedSapi.encode()[:15]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhOdu1Specific(self, parameters):
        '''**RX:OH:ODU:SPECIFIC?** -
        Query the specified ODU SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return self.globals.veexOtn.stats.oduPmTtiSpecific.encode()[:15]

    def rxOhOdu2TcmAct(self, parameters):
        '''**RX:OH:ODU:TCMACT?** -
        Query the specified ODU TCMACT overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.oduOh[veexlib.OTN_ODU_OH_TCM_ACT]
    
    def rxOhOdu1SapiExpt(self, parameters):
        '''**RX:OH:ODU:SAPIEXP** -
        Sets the expected receive value for the ODU SAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            dapi = self.globals.veexOtn.sets.oduPmTtiExpectedDapi.encode()[:15]
            self.globals.veexOtn.sets.setOduPmTtiExpected(sapi,dapi)
        else:
            dapi = self.globals.veexOtn.sets.oduPmTtiExpectedDapi.encode()[:15]
            self.globals.veexOtn.sets.setOduPmTtiExpected(b"",dapi)
        return response

    def rxOhOdu1DapiExpt(self, parameters):
        '''**RX:OH:ODU:DAPIEXP** -
        Sets the expected receive value for the ODU DAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            sapi = self.globals.veexOtn.sets.oduPmTtiExpectedSapi.encode()[:15]
            self.globals.veexOtn.sets.setOduPmTtiExpected(sapi,dapi)
        else:
            sapi = self.globals.veexOtn.sets.oduPmTtiExpectedSapi.encode()[:15]
            self.globals.veexOtn.sets.setOduPmTtiExpected(sapi,b"")
        return response

    def rxOhOpuRes1(self, parameters):
        '''**RX:OH:OPU:RES1?** -
        Query the specified OPU RES1 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.opuOh[veexlib.OTN_OPU_OH_RES_1]

    def rxOhOpuPsiExp(self, parameters):
        '''**RX:OH:OPU:PSIEXP?** -
        Query the specified OPU PSIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        return b"#H%02X" % self.globals.veexOtn.sets.opuPtExpected

    def setOhOpuPsiExp(self, parameters):
        '''**RX:OH:OPU:PSIEXP:<value>** -
        Sets the expected receive value for the specified OPU PSIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 0) and (value <= 255):
                self.globals.veexOtn.sets.opuPtExpected = value
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def rxOhOpuRes3(self, parameters):
        '''**RX:OH:OPU:RES3?** -
        Query the specified OPU RES3 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.opuOh[veexlib.OTN_OPU_OH_RES_3]

    def rxOhOpuJc1(self, parameters):
        '''**RX:OH:OPU:JC1?** -
        Query the specified OPU JC1 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.opuOh[veexlib.OTN_OPU_OH_JC_1]

    def rxOhOpuJc2(self, parameters):
        '''**RX:OH:OPU:JC2?** -
        Query the specified OPU JC2 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.opuOh[veexlib.OTN_OPU_OH_JC_2]

    def rxOhOpuJc3(self, parameters):
        '''**RX:OH:OPU:JC3?** -
        Query the specified OPU JC3 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.opuOh[veexlib.OTN_OPU_OH_JC_3]

    def rxOhOpuNjo(self, parameters):
        '''**RX:OH:OPU:NJO?** -
        Query the specified OPU NJO overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.opuOh[veexlib.OTN_OPU_OH_NJO]

    def rxOhOpuPsi(self, parameters):
        '''**RX:OH:OPU:PSI?** -
        Query the specified RX OPU PSI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.opuOh[veexlib.OTN_OPU_OH_PSI]

    def rxOhOpuRes2(self, parameters):
        '''**RX:OH:OPU:RES2?** -
        Query the specified RX OPU RES2 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.opuOh[veexlib.OTN_OPU_OH_RES_2]

    def rxOhOpuMsi(self, parameters):
        '''**RX:OH:OPU:MSI? <slot>** -
        Query the specified RX OPU MSI overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ALL"):
                iIndex = 0
            else:
                iIndex = ParseUtils.checkNumeric(paramList[0].head)
            if iIndex >= 0:
                if (self.globals.veexOtn.sets.rxInterface == veexlib.OTN_INTERFACE_112G_OTU_4) or \
                   (self.globals.veexOtn.sets.rxInterface == veexlib.OTN_INTERFACE_112G_CFP_OTU_4):
                    msiByteCount = 80
                elif (self.globals.veexOtn.sets.rxInterface == veexlib.OTN_INTERFACE_43G_OTU_3) or \
                     (self.globals.veexOtn.sets.rxInterface == veexlib.OTN_INTERFACE_44G_OTU_3E1) or \
                     (self.globals.veexOtn.sets.rxInterface == veexlib.OTN_INTERFACE_44G_OTU_3E2):
                    msiByteCount = 32
                elif (self.globals.veexOtn.sets.rxInterface == veexlib.OTN_INTERFACE_10G_OTU_2) or \
                     (self.globals.veexOtn.sets.rxInterface == veexlib.OTN_INTERFACE_11G_OTU_2E) or \
                     (self.globals.veexOtn.sets.rxInterface == veexlib.OTN_INTERFACE_11G_OTU_2F):
                    msiByteCount = 8
                elif (self.globals.veexOtn.sets.rxInterface == veexlib.OTN_INTERFACE_2P5G_OTU_1) or \
                     (self.globals.veexOtn.sets.rxInterface == veexlib.OTN_INTERFACE_11G_OTU_1E) or \
                     (self.globals.veexOtn.sets.rxInterface == veexlib.OTN_INTERFACE_11G_OTU_1F):
                    msiByteCount = 2
                else:
                    msiByteCount = -1
                self.globals.veexOtn.stats.update()
                if iIndex <= msiByteCount:
                    if iIndex == 0:
                        for i in range(msiByteCount-1):
                            response += b"#H%02X, " % self.globals.veexOtn.stats.opuMsi[i]
                        response += b"#H%02X" % self.globals.veexOtn.stats.opuMsi[msiByteCount-1]
                    else:
                        response = b"#H%02X" % self.globals.veexOtn.stats.opuMsi[iIndex-1]
                else:
                    response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def rxOhOtuBei(self, parameters):
        '''**RX:OH:OTU:BEI?** -
        Query the RX OTU BEI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.otuOh[veexlib.OTN_OTU_OH_SM_BEI]

    def rxOhOtuBip8(self, parameters):
        '''**RX:OH:OTU:BIP8?** -
        Query the RX OTU BIP8 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.otuOh[veexlib.OTN_OTU_OH_SM_BIP]

    def rxOhOtuDapi(self, parameters):
        '''**RX:OH:OTU:DAPI?** -
        Query the RX OTU DAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.otuSmTtiDapi.encode()[:15]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhOtuDapiExp(self, parameters):
        '''**RX:OH:OTU:DAPIEXP?** -
        Query the RX OTU DAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.otuSmTtiExpectedDapi.encode()[:15]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhOtuDapiExpt(self, parameters):
        '''**RX:OH:OTU:DAPIEXP:<value>** -
        Sets the expected receive value for the specified OTU DAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                dapi = paramString[:15]
            else:
                dapi = paramString[:]
            sapi = self.globals.veexOtn.sets.otuSmTtiExpectedSapi.encode()[:15]
            self.globals.veexOtn.sets.setOtuSmTtiExpected(sapi,dapi)
        else:
            sapi = self.globals.veexOtn.sets.otuSmTtiExpectedSapi.encode()[:15]
            self.globals.veexOtn.sets.setOtuSmTtiExpected(sapi,b"")
        return response

    def rxOhOtuGcc1(self, parameters):
        '''**RX:OH:OTU:GCC01?** -
        Query the RX OTU GCC01 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.otuOh[veexlib.OTN_OTU_OH_GCC0_1]

    def rxOhOtuGcc2(self, parameters):
        '''**RX:OH:OTU:GCC02?** -
        Query the RX OTU GCC02 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.otuOh[veexlib.OTN_OTU_OH_GCC0_2]

    def rxOhOtuOa11(self, parameters):
        '''**RX:OH:OTU:OA1:1?** -
        Query the RX OTU OA1:1 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.otuOh[veexlib.OTN_OTU_OH_FAS_OA1_1]

    def rxOhOtuOa12(self, parameters):
        '''**RX:OH:OTU:OA1:2?** -
        Query the RX OTU OA1:2 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.otuOh[veexlib.OTN_OTU_OH_FAS_OA1_2]

    def rxOhOtuOa13(self, parameters):
        '''**RX:OH:OTU:OA1:3?** -
        Query the RX OTU OA1:3 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.otuOh[veexlib.OTN_OTU_OH_FAS_OA1_3]

    def rxOhOtuOa21(self, parameters):
        '''**RX:OH:OTU:OA2:1?** -
        Query the RX OTU OA2:1 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.otuOh[veexlib.OTN_OTU_OH_FAS_OA2_1]

    def rxOhOtuOa22(self, parameters):
        '''**RX:OH:OTU:OA2:2?** -
        Query the RX OTU OA2:2 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.otuOh[veexlib.OTN_OTU_OH_FAS_OA2_2]

    def rxOhOtuOa23(self, parameters):
        '''**RX:OH:OTU:OA2:3?** -
        Query the RX OTU OA2:3 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.otuOh[veexlib.OTN_OTU_OH_FAS_OA2_3]

    def rxOhOtuRes1(self, parameters):
        '''**RX:OH:OTU:RES1?** -
        Query the RX OTU RES1 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.otuOh[veexlib.OTN_OTU_OH_OSMC]

    def rxOhOtuRes2(self, parameters):
        '''**RX:OH:OTU:RES2?** -
        Query the RX OTU RES2 overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.otuOh[veexlib.OTN_OTU_OH_RES_2]

    def rxOhOtuSapi(self, parameters):
        '''**RX:OH:OTU:SAPI?** -
        Query the RX OTU SAPI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.otuSmTtiSapi.encode()[:15]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhOtuSapiExp(self, parameters):
        '''**RX:OH:OTU:SAPIEXP?** -
        Query the RX OTU SAPIEXP overhead byte.
        '''
        self.globals.veexOtn.sets.update()
        response = self.globals.veexOtn.sets.otuSmTtiExpectedSapi.encode()[:15]
        if len(response.lstrip(b' ')) == 0:
            return b"NONE"
        return response

    def rxOhOtuSapiExpt(self, parameters):
        '''**RX:OH:OTU:SAPIEXP:<value>** -
        Sets the expected receive value for the specified OTU SAPIEXP overhead byte.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            for i in range(len(paramList)):
                if i == 0:
                    paramString = paramList[i].head[:]
                else:
                    paramString += b" " + paramList[i].head[:]
            if len(paramString) >= 15:
                sapi = paramString[:15]
            else:
                sapi = paramString[:]
            dapi = self.globals.veexOtn.sets.otuSmTtiExpectedDapi.encode()[:15]
            self.globals.veexOtn.sets.setOtuSmTtiExpected(sapi,dapi)
        else:
            dapi = self.globals.veexOtn.sets.otuSmTtiExpectedDapi.encode()[:15]
            self.globals.veexOtn.sets.setOtuSmTtiExpected(b"",dapi)
        return response

    def rxOhOtuSpecific(self, parameters):
        '''**RX:OH:OTU:SPECIFIC?** -
        Query the RX OTU SPECIFIC overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        response = self.globals.veexOtn.stats.otuSmTtiSpecific.encode()[:32]
        response = response
        return response

    def rxOhOtuTti(self, parameters):
        '''**RX:OH:OTU:TTI?** -
        Query the RX OTU TTI overhead byte.
        '''
        self.globals.veexOtn.stats.update()
        return b"#H%02X" % self.globals.veexOtn.stats.otuOh[veexlib.OTN_OTU_OH_SM_TTI]

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

    def getRxOpuJustLevel(self, parameters):
        '''**RX:OPUJUST?** -
        Query the OPU Justify Frequency Offset. Returns value in PPM.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2f ppm" % (float(self.globals.veexOtn.stats.justFreqOffset),)

    def getRxOpuPlm(self, parameters):
        '''**RX:OPUPLM?** -
        Query the PLM alarm reporting mode for OPU.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.opuPlmAlarmEnable == True:
            response = b"ENABLED"
        elif self.globals.veexOtn.sets.opuPlmAlarmEnable == False:
            response = b"DISABLED"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setRxOpuPlm(self, parameters):
        '''**RX:OPUPLM:<ENABLED|DISABLED>** -
        Sets the PLM alarm reporting mode for OPU.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ENABLED"):
                self.globals.veexOtn.sets.opuPlmAlarmEnable = True
            elif paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.opuPlmAlarmEnable = False
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getOpuFreqThreshhold(self, parameters):
        '''**RX:OPUTHRESHold?** -
        Query the receive OPU Out of Frequency Threshold value for the OPU Frequency Wide alarm.
        Returns the threshold value in PPM, or OFF (0.0 PPM).
        '''
        self.globals.veexOtn.sets.update()
        fInValue = self.globals.veexOtn.sets.opuFreqTolerance
        if math.isclose(fInValue, 0.00, rel_tol = 0.000001):
            return b"OFF"
        return b"%0.1f ppm" % fInValue

    def setOpuFreqThreshhold(self, parameters):
        '''**RX:OPUTHRESHold <threshold>** -
        Sets the +/- value (in ppm) for the received OPU Out of Frequency Threshold value.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if ParseUtils.isFloatSdh(paramList[0].head):
                freqTolerance = float(paramList[0].head)
                if math.isclose(freqTolerance, 0.00, rel_tol = 0.00001) or \
                   (freqTolerance >= 0.00) or (freqTolerance <= 65.9):
                    self.globals.veexOtn.sets.opuFreqTolerance = freqTolerance
                else:
                    response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            else:
                response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxOtuSm(self, parameters):
        '''**RX:OTUSM?** -
        Query the mode of the OTU SM TIM Alarm Reporting option.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.otuSmTimAlarmEnable == True:
            response = b"ENABLED"
        elif self.globals.veexOtn.sets.otuSmTimAlarmEnable == False:
            response = b"DISABLED"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setRxOtuSm(self, parameters):
        '''**RX:OTUSM:<ENABLED|DISABLED>** -
        Sets the mode of the OTU SM TIM Alarm Reporting option.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"ENABLED"):
                self.globals.veexOtn.sets.otuSmTimAlarmEnable = True
            elif paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.otuSmTimAlarmEnable = False
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxFreqThreshhold(self, parameters):
        '''**RX:OUTTHRESHold?** -
        the receive Out of Frequency Threshold value for the Frequency Wide alarm.
        Returns the threshold value in PPM, or OFF (0.0 PPM).
        '''
        self.globals.veexOtn.sets.update()
        fInValue = self.globals.veexOtn.sets.rxFreqTolerance
        if math.isclose(fInValue, 0.00, rel_tol = 0.000001):
            return b"OFF"
        return b"%0.1f ppm" % fInValue

    def setRxFreqThreshhold(self, parameters):
        '''**RX:OUTTHRESHold:<value>** -
        Sets the +/- value (in ppm) for the received Out of Frequency Threshold value.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if ParseUtils.isFloatSdh(paramList[0].head):
                freqTolerance = float(paramList[0].head)
                if math.isclose(freqTolerance, 0.00, rel_tol = 0.00001) or \
                   (freqTolerance >= 0.00) or (freqTolerance <= 300.0):
                    self.globals.veexOtn.sets.rxFreqTolerance = freqTolerance
                else:
                    response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
            else:
                response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxPattern(self, parameters):
        '''**RX:PATTern? <container>** -
        Query the expected receive pattern.
        Returns a binary pattern for user-defined bit string or a predefined pattern.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.rxPattern == veexlib.OTN_PATTERN_LIVE:
            response = b"LIVE"
        elif self.globals.veexOtn.sets.rxPattern == veexlib.OTN_PATTERN_PRBS_9:
            response = b"PRBS9"
        elif self.globals.veexOtn.sets.rxPattern == veexlib.OTN_PATTERN_PRBS_9_INV:
            response = b"PRBS9INV"
        elif self.globals.veexOtn.sets.rxPattern == veexlib.OTN_PATTERN_PRBS_11:
            response = b"PRBS11"
        elif self.globals.veexOtn.sets.rxPattern == veexlib.OTN_PATTERN_PRBS_11_INV:
            response = b"PRBS11INV"
        elif self.globals.veexOtn.sets.rxPattern == veexlib.OTN_PATTERN_PRBS_15:
            response = b"PRBS15"
        elif self.globals.veexOtn.sets.rxPattern == veexlib.OTN_PATTERN_PRBS_15_INV:
            response = b"PRBS15INV"
        elif self.globals.veexOtn.sets.rxPattern == veexlib.OTN_PATTERN_PRBS_20:
            response = b"PRBS20"
        elif self.globals.veexOtn.sets.rxPattern == veexlib.OTN_PATTERN_PRBS_20_INV:
            response = b"PRBS20INV"
        elif self.globals.veexOtn.sets.rxPattern == veexlib.OTN_PATTERN_PRBS_23:
            response = b"PRBS23"
        elif self.globals.veexOtn.sets.rxPattern == veexlib.OTN_PATTERN_PRBS_23_INV:
            response = b"PRBS23INV"
        elif self.globals.veexOtn.sets.rxPattern == veexlib.OTN_PATTERN_PRBS_31:
            response = b"PRBS31"
        elif self.globals.veexOtn.sets.rxPattern == veexlib.OTN_PATTERN_PRBS_31_INV:
            response = b"PRBS31INV"
        elif self.globals.veexOtn.sets.rxPattern == veexlib.OTN_PATTERN_USER:
            bValue = bin(self.globals.veexOtn.sets.rxUserPattern)
            response = b"#B" + bValue.encode()[2:]
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_PATTERN)
        return response

    def setRxPattern(self, parameters):
        '''**RX:PATTern:<pattern> <container>** -
        Sets the receive payload pattern. Payload patterns can be a numeric user-defined bit pattern, or a predefined pattern.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"LIVE"):
                self.globals.veexOtn.sets.rxPattern = veexlib.OTN_PATTERN_LIVE
            elif paramList[0].head.upper().startswith(b"PRBS9INV"):
                self.globals.veexOtn.sets.rxPattern = veexlib.OTN_PATTERN_PRBS_9_INV
            elif paramList[0].head.upper().startswith(b"PRBS9"):
                self.globals.veexOtn.sets.rxPattern = veexlib.OTN_PATTERN_PRBS_9
            elif paramList[0].head.upper().startswith(b"PRBS11INV"):
                self.globals.veexOtn.sets.rxPattern = veexlib.OTN_PATTERN_PRBS_11_INV
            elif paramList[0].head.upper().startswith(b"PRBS11"):
                self.globals.veexOtn.sets.rxPattern = veexlib.OTN_PATTERN_PRBS_11
            elif paramList[0].head.upper().startswith(b"PRBS15INV"):
                self.globals.veexOtn.sets.rxPattern = veexlib.OTN_PATTERN_PRBS_15_INV
            elif paramList[0].head.upper().startswith(b"PRBS15"):
                self.globals.veexOtn.sets.rxPattern = veexlib.OTN_PATTERN_PRBS_15
            elif paramList[0].head.upper().startswith(b"PRBS20INV"):
                self.globals.veexOtn.sets.rxPattern = veexlib.OTN_PATTERN_PRBS_20_INV
            elif paramList[0].head.upper().startswith(b"PRBS20"):
                self.globals.veexOtn.sets.rxPattern = veexlib.OTN_PATTERN_PRBS_20
            elif paramList[0].head.upper().startswith(b"PRBS23INV"):
                self.globals.veexOtn.sets.rxPattern = veexlib.OTN_PATTERN_PRBS_23_INV
            elif paramList[0].head.upper().startswith(b"PRBS23"):
                self.globals.veexOtn.sets.rxPattern = veexlib.OTN_PATTERN_PRBS_23
            elif paramList[0].head.upper().startswith(b"PRBS31INV"):
                self.globals.veexOtn.sets.rxPattern = veexlib.OTN_PATTERN_PRBS_31_INV
            elif paramList[0].head.upper().startswith(b"PRBS31"):
                self.globals.veexOtn.sets.rxPattern = veexlib.OTN_PATTERN_PRBS_31
            else:
                value = ParseUtils.checkNumeric(paramList[0].head)
                if value >= 0:
                    self.globals.veexOtn.sets.rxUserPattern = value
                else:
                    response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxPowLowThreshhold(self, parameters):
        '''**RX:PWRLOWT?** -
        Query the Power Low Threshold Alarm value.
        Returns value in dBm or OFF.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        fInValue = self.globals.veexOtn.sets.rxPowerMinimum
        if math.isclose(fInValue, -100.0, rel_tol = 0.01):
            response = b"OFF"
        else:
            response = b"%0.1f dBm" % fInValue
        return response

    def setRxPowLowThreshhold(self, parameters):
        '''**RX:PWRLOWT:<value>** -
        Sets the value for the Power Low Threshold Alarm.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if ParseUtils.isFloatSdh(paramList[0].head):
                powerLowThresh = float(paramList[0].head)
                if powerLowThresh >= -100.0 and powerLowThresh <= 0.0:
                    self.globals.veexOtn.sets.rxPowerMinimum = powerLowThresh
                else:
                    response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxScramble(self, parameters):
        '''**RX:SCRAMBLE?** -
        Query the state of receive OTN frame scrambling mode.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.rxScrambleDisable == True:
            response = b"DISABLED"
        elif self.globals.veexOtn.sets.rxScrambleDisable == False:
            response = b"ENABLED"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setRxScramble(self, parameters):
        '''**RX:SCRAMBLE:<DISABLED|ENABLED>** -
        Sets the state of the receive OTN frame scrambling mode.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.rxScrambleDisable = True
            elif paramList[0].head.upper().startswith(b"ENABLED"):
                self.globals.veexOtn.sets.rxScrambleDisable = False
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxTcm1(self, parameters):
        '''**RX:TCM1?** -
        Query the error and alarm reporting mode for TCM #1.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.oduTcmAlarmEnable[0] == veexlib.OTN_ODU_TCM_ALARM_DISABLE:
            response = b"DISABLED"
        elif self.globals.veexOtn.sets.oduTcmAlarmEnable[0] == veexlib.OTN_ODU_TCM_ALARM_ENABLE_NO_TIM:
            response = b"ENABLED no TIM"
        elif self.globals.veexOtn.sets.oduTcmAlarmEnable[0] == veexlib.OTN_ODU_TCM_ALARM_ENABLE_WITH_TIM:
            response = b"ENABLED with TIM"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setRxTcm1(self, parameters):
        '''**RX:TCM1:<DISABLED|ENABLED WITH TIM|ENABLED NO TIM>** -
        Sets the error and alarm reporting mode for TCM #1.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        print("%d" % (paramList[0].head.upper().startswith(b"ENABLED") and paramList[1].head.upper().startswith(b"WITH") and paramList[2].head.upper().startswith(b"TIM"),))
        if len(paramList) >= 3:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(1,veexlib.OTN_ODU_TCM_ALARM_DISABLE)
            elif paramList[0].head.upper().startswith(b"ENABLED") and \
                 paramList[1].head.upper().startswith(b"NO") and \
                 paramList[2].head.upper().startswith(b"TIM"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(1,veexlib.OTN_ODU_TCM_ALARM_ENABLE_NO_TIM)
            elif paramList[0].head.upper().startswith(b"ENABLED") and \
                 paramList[1].head.upper().startswith(b"WITH") and \
                 paramList[2].head.upper().startswith(b"TIM"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(1,veexlib.OTN_ODU_TCM_ALARM_ENABLE_WITH_TIM)
            else:
                print("1 %d %d %d" % (paramList[0].head.upper().startswith(b"ENABLED"), paramList[1].head.upper().startswith(b"WITH"), paramList[2].head.upper().startswith(b"TIM")))
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        elif len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(1,veexlib.OTN_ODU_TCM_ALARM_DISABLE)
            else:
                print("2 %d %d %d" % (paramList[0].head.upper().startswith(b"ENABLED"), paramList[1].head.upper().startswith(b"WITH"), paramList[2].head.upper().startswith(b"TIM")))
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            print("3 %d %d %d" % (paramList[0].head.upper().startswith(b"ENABLED"), paramList[1].head.upper().startswith(b"WITH"), paramList[2].head.upper().startswith(b"TIM")))
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxTcm2(self, parameters):
        '''**RX:TCM2?** -
        Query the error and alarm reporting mode for TCM #2.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.oduTcmAlarmEnable[1] == veexlib.OTN_ODU_TCM_ALARM_DISABLE:
            response = b"DISABLED"
        elif self.globals.veexOtn.sets.oduTcmAlarmEnable[1] == veexlib.OTN_ODU_TCM_ALARM_ENABLE_NO_TIM:
            response = b"ENABLED no TIM"
        elif self.globals.veexOtn.sets.oduTcmAlarmEnable[1] == veexlib.OTN_ODU_TCM_ALARM_ENABLE_WITH_TIM:
            response = b"ENABLED with TIM"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setRxTcm2(self, parameters):
        '''**RX:TCM2:<DISABLED|ENABLED WITH TIM|ENABLED NO TIM>** -
        Sets the error and alarm reporting mode for TCM #2.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 3:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(2,veexlib.OTN_ODU_TCM_ALARM_DISABLE)
            elif paramList[0].head.upper().startswith(b"ENABLED") and \
                 paramList[1].head.upper().startswith(b"NO") and \
                 paramList[2].head.upper().startswith(b"TIM"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(2,veexlib.OTN_ODU_TCM_ALARM_ENABLE_NO_TIM)
            elif paramList[0].head.upper().startswith(b"ENABLED") and \
                 paramList[1].head.upper().startswith(b"WITH") and \
                 paramList[2].head.upper().startswith(b"TIM"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(2,veexlib.OTN_ODU_TCM_ALARM_ENABLE_WITH_TIM)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        elif len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(2,veexlib.OTN_ODU_TCM_ALARM_DISABLE)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxTcm3(self, parameters):
        '''**RX:TCM3?** -
        Query the error and alarm reporting mode for TCM #3.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.oduTcmAlarmEnable[2] == veexlib.OTN_ODU_TCM_ALARM_DISABLE:
            response = b"DISABLED"
        elif self.globals.veexOtn.sets.oduTcmAlarmEnable[2] == veexlib.OTN_ODU_TCM_ALARM_ENABLE_NO_TIM:
            response = b"ENABLED no TIM"
        elif self.globals.veexOtn.sets.oduTcmAlarmEnable[2] == veexlib.OTN_ODU_TCM_ALARM_ENABLE_WITH_TIM:
            response = b"ENABLED with TIM"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setRxTcm3(self, parameters):
        '''**RX:TCM3:<DISABLED|ENABLED WITH TIM|ENABLED NO TIM>** -
        Sets the error and alarm reporting mode for TCM #3.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 3:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(3,veexlib.OTN_ODU_TCM_ALARM_DISABLE)
            elif paramList[0].head.upper().startswith(b"ENABLED") and \
                 paramList[1].head.upper().startswith(b"NO") and \
                 paramList[2].head.upper().startswith(b"TIM"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(3,veexlib.OTN_ODU_TCM_ALARM_ENABLE_NO_TIM)
            elif paramList[0].head.upper().startswith(b"ENABLED") and \
                 paramList[1].head.upper().startswith(b"WITH") and \
                 paramList[2].head.upper().startswith(b"TIM"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(3,veexlib.OTN_ODU_TCM_ALARM_ENABLE_WITH_TIM)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        elif len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(3,veexlib.OTN_ODU_TCM_ALARM_DISABLE)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxTcm4(self, parameters):
        '''**RX:TCM4?** -
        Query the error and alarm reporting mode for TCM #4.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.oduTcmAlarmEnable[3] == veexlib.OTN_ODU_TCM_ALARM_DISABLE:
            response = b"DISABLED"
        elif self.globals.veexOtn.sets.oduTcmAlarmEnable[3] == veexlib.OTN_ODU_TCM_ALARM_ENABLE_NO_TIM:
            response = b"ENABLED no TIM"
        elif self.globals.veexOtn.sets.oduTcmAlarmEnable[3] == veexlib.OTN_ODU_TCM_ALARM_ENABLE_WITH_TIM:
            response = b"ENABLED with TIM"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setRxTcm4(self, parameters):
        '''**RX:TCM4:<DISABLED|ENABLED WITH TIM|ENABLED NO TIM>** -
        Sets the error and alarm reporting mode for TCM #4.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 3:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(4,veexlib.OTN_ODU_TCM_ALARM_DISABLE)
            elif paramList[0].head.upper().startswith(b"ENABLED") and \
                 paramList[1].head.upper().startswith(b"NO") and \
                 paramList[2].head.upper().startswith(b"TIM"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(4,veexlib.OTN_ODU_TCM_ALARM_ENABLE_NO_TIM)
            elif paramList[0].head.upper().startswith(b"ENABLED") and \
                 paramList[1].head.upper().startswith(b"WITH") and \
                 paramList[2].head.upper().startswith(b"TIM"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(4,veexlib.OTN_ODU_TCM_ALARM_ENABLE_WITH_TIM)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        elif len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(4,veexlib.OTN_ODU_TCM_ALARM_DISABLE)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxTcm5(self, parameters):
        '''**RX:TCM5?** -
        Query the error and alarm reporting mode for TCM #5.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.oduTcmAlarmEnable[4] == veexlib.OTN_ODU_TCM_ALARM_DISABLE:
            response = b"DISABLED"
        elif self.globals.veexOtn.sets.oduTcmAlarmEnable[4] == veexlib.OTN_ODU_TCM_ALARM_ENABLE_NO_TIM:
            response = b"ENABLED no TIM"
        elif self.globals.veexOtn.sets.oduTcmAlarmEnable[4] == veexlib.OTN_ODU_TCM_ALARM_ENABLE_WITH_TIM:
            response = b"ENABLED with TIM"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setRxTcm5(self, parameters):
        '''**RX:TCM5:<DISABLED|ENABLED WITH TIM|ENABLED NO TIM>** -
        Sets the error and alarm reporting mode for TCM #5.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 3:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(5,veexlib.OTN_ODU_TCM_ALARM_DISABLE)
            elif paramList[0].head.upper().startswith(b"ENABLED") and \
                 paramList[1].head.upper().startswith(b"NO") and \
                 paramList[2].head.upper().startswith(b"TIM"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(5,veexlib.OTN_ODU_TCM_ALARM_ENABLE_NO_TIM)
            elif paramList[0].head.upper().startswith(b"ENABLED") and \
                 paramList[1].head.upper().startswith(b"WITH") and \
                 paramList[2].head.upper().startswith(b"TIM"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(5,veexlib.OTN_ODU_TCM_ALARM_ENABLE_WITH_TIM)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        elif len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(5,veexlib.OTN_ODU_TCM_ALARM_DISABLE)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxTcm6(self, parameters):
        '''**RX:TCM6?** -
        Query the error and alarm reporting mode for TCM #6.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.oduTcmAlarmEnable[5] == veexlib.OTN_ODU_TCM_ALARM_DISABLE:
            response = b"DISABLED"
        elif self.globals.veexOtn.sets.oduTcmAlarmEnable[5] == veexlib.OTN_ODU_TCM_ALARM_ENABLE_NO_TIM:
            response = b"ENABLED no TIM"
        elif self.globals.veexOtn.sets.oduTcmAlarmEnable[5] == veexlib.OTN_ODU_TCM_ALARM_ENABLE_WITH_TIM:
            response = b"ENABLED with TIM"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setRxTcm6(self, parameters):
        '''**RX:TCM6:<DISABLED|ENABLED WITH TIM|ENABLED NO TIM>** -
        Sets the error and alarm reporting mode for TCM #6.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 3:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(6,veexlib.OTN_ODU_TCM_ALARM_DISABLE)
            elif paramList[0].head.upper().startswith(b"ENABLED") and \
                 paramList[1].head.upper().startswith(b"NO") and \
                 paramList[2].head.upper().startswith(b"TIM"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(6,veexlib.OTN_ODU_TCM_ALARM_ENABLE_NO_TIM)
            elif paramList[0].head.upper().startswith(b"ENABLED") and \
                 paramList[1].head.upper().startswith(b"WITH") and \
                 paramList[2].head.upper().startswith(b"TIM"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(6,veexlib.OTN_ODU_TCM_ALARM_ENABLE_WITH_TIM)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        elif len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"DISABLED"):
                self.globals.veexOtn.sets.setOduTcmAlarmEnable(6,veexlib.OTN_ODU_TCM_ALARM_DISABLE)
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getRxTrigger(self, parameters):
        '''**RX:TRIG?** -
        Query the Trigger Out criteria.
        '''
        self.globals.veexOtn.sets.update()
        response = b""
        if self.globals.veexOtn.sets.outTriggerSrc == 0:
            response = b"NONE"
        elif self.globals.veexOtn.sets.outTriggerSrc == 1:
            response = b"LOF"
        elif self.globals.veexOtn.sets.outTriggerSrc == 2:
            response = b"OOF"
        elif self.globals.veexOtn.sets.outTriggerSrc == 3:
            response = b"LOM"
        elif self.globals.veexOtn.sets.outTriggerSrc == 4:
            response = b"OOM"
        elif self.globals.veexOtn.sets.outTriggerSrc == 5:
            response = b"OTU_AIS"
        elif self.globals.veexOtn.sets.outTriggerSrc == 6:
            response = b"OTU_IAE"
        elif self.globals.veexOtn.sets.outTriggerSrc == 7:
            response = b"OTU_BDI"
        elif self.globals.veexOtn.sets.outTriggerSrc == 8:
            response = b"ODU_AIS"
        elif self.globals.veexOtn.sets.outTriggerSrc == 9:
            response = b"ODU_LCK"
        elif self.globals.veexOtn.sets.outTriggerSrc == 10:
            response = b"ODU_OCI"
        elif self.globals.veexOtn.sets.outTriggerSrc == 11:
            response = b"ODU_BDI"
        elif self.globals.veexOtn.sets.outTriggerSrc == 12:
            response = b"FRAME"
        elif self.globals.veexOtn.sets.outTriggerSrc == 13:
            response = b"MFAS"
        elif self.globals.veexOtn.sets.outTriggerSrc == 14:
            response = b"FEC_UNCOR"
        elif self.globals.veexOtn.sets.outTriggerSrc == 15:
            response = b"FEC_COR"
        elif self.globals.veexOtn.sets.outTriggerSrc == 16:
            response = b"OTU_BIP8"
        elif self.globals.veexOtn.sets.outTriggerSrc == 17:
            response = b"OTU_BEI"
        elif self.globals.veexOtn.sets.outTriggerSrc == 18:
            response = b"ODU_BIP8"
        elif self.globals.veexOtn.sets.outTriggerSrc == 19:
            response = b"ODU_BEI"
        elif self.globals.veexOtn.sets.outTriggerSrc == 20:
            response = b"BIT"
        elif self.globals.veexOtn.sets.outTriggerSrc == 21:
            response = b"JUST_INCREMENT"
        elif self.globals.veexOtn.sets.outTriggerSrc == 22:
            response = b"JUST_DECREMENT"
        elif self.globals.veexOtn.sets.outTriggerSrc == 23:
            response = b"FRAME_PULSE"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setRxTrigger(self, parameters):
        '''**RX:TRIG:<criteria>** -
        Sets the Trigger Out criteria, which when received a +5v pulse is sent to the Trigger Out SMA connector.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        self.globals.veexOtn.sets.update()
        if len(paramList) >= 1:
            if paramList[0].head.upper().startswith(b"NONE"):
                self.globals.veexOtn.sets.outTriggerSrc = 0
            elif paramList[0].head.upper().startswith(b"FRAME_PULSE"):
                self.globals.veexOtn.sets.outTriggerSrc = 23
            elif paramList[0].head.upper().startswith(b"LOF"):
                self.globals.veexOtn.sets.outTriggerSrc = 1
            elif paramList[0].head.upper().startswith(b"OOF"):
                self.globals.veexOtn.sets.outTriggerSrc = 2
            elif paramList[0].head.upper().startswith(b"LOM"):
                self.globals.veexOtn.sets.outTriggerSrc = 3
            elif paramList[0].head.upper().startswith(b"OOM"):
                self.globals.veexOtn.sets.outTriggerSrc = 4
            elif paramList[0].head.upper().startswith(b"OTU_AIS"):
                self.globals.veexOtn.sets.outTriggerSrc = 5
            elif paramList[0].head.upper().startswith(b"OTU_AIE"):
                self.globals.veexOtn.sets.outTriggerSrc = 6
            elif paramList[0].head.upper().startswith(b"OTU_BDI"):
                self.globals.veexOtn.sets.outTriggerSrc = 7
            elif paramList[0].head.upper().startswith(b"ODU_AIS"):
                self.globals.veexOtn.sets.outTriggerSrc = 8
            elif paramList[0].head.upper().startswith(b"ODU_LCK"):
                self.globals.veexOtn.sets.outTriggerSrc = 9
            elif paramList[0].head.upper().startswith(b"ODU_OCI"):
                self.globals.veexOtn.sets.outTriggerSrc = 10
            elif paramList[0].head.upper().startswith(b"ODU_BDI"):
                self.globals.veexOtn.sets.outTriggerSrc = 11
            elif paramList[0].head.upper().startswith(b"FRAME"):
                self.globals.veexOtn.sets.outTriggerSrc = 12
            elif paramList[0].head.upper().startswith(b"MFAS"):
                self.globals.veexOtn.sets.outTriggerSrc = 13
            elif paramList[0].head.upper().startswith(b"FEC_UNCOR"):
                self.globals.veexOtn.sets.outTriggerSrc = 14
            elif paramList[0].head.upper().startswith(b"FEC_COR"):
                self.globals.veexOtn.sets.outTriggerSrc = 15
            elif paramList[0].head.upper().startswith(b"OTU_BIP8"):
                self.globals.veexOtn.sets.outTriggerSrc = 16
            elif paramList[0].head.upper().startswith(b"OTU_BEI"):
                self.globals.veexOtn.sets.outTriggerSrc = 17
            elif paramList[0].head.upper().startswith(b"ODU_BIP8"):
                self.globals.veexOtn.sets.outTriggerSrc = 18
            elif paramList[0].head.upper().startswith(b"ODU_BEI"):
                self.globals.veexOtn.sets.outTriggerSrc = 19
            elif paramList[0].head.upper().startswith(b"BIT"):
                self.globals.veexOtn.sets.outTriggerSrc = 20
            elif paramList[0].head.upper().startswith(b"JUST_INCREMENT"):
                self.globals.veexOtn.sets.outTriggerSrc = 21
            elif paramList[0].head.upper().startswith(b"JUST_DECREMENT"):
                self.globals.veexOtn.sets.outTriggerSrc = 22
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getResLofLed(self, parameters):
        '''**RES:AL:LOF?** -
        Query the ON/OFF LED state for LOF alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.lof.led.isRed else b"OFF"

    def getResLosLed(self, parameters):
        '''**RES:AL:LOS?** -
        Query the ON/OFF LED state for LOS alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.los.led.isRed else b"OFF"

    def getResLomLed(self, parameters):
        '''**RES:AL:LOM?** -
        Query the ON/OFF LED state for LOM alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.lom.led.isRed else b"OFF"

    def getResLoomfiLed(self, parameters):
        '''**RES:AL:LOOMFI?** -
        Query the ON/OFF LED state for LOOMFI alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.loomfi.led.isRed else b"OFF"

    def getResOduAisLed(self, parameters):
        '''**RES:AL:ODUAIS?** -
        Query the ON/OFF LED state for ODU:AIS alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.oduAis.led.isRed else b"OFF"

    def getResOduBdiLed(self, parameters):
        '''**RES:AL:ODUBDI?** -
        Query the ON/OFF LED state for ODU:BDI alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.oduBdi.led.isRed else b"OFF"

    def getResOduLckLed(self, parameters):
        '''**RES:AL:ODULCK?** -
        Query the ON/OFF LED state for ODU:LCK alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.oduLck.led.isRed else b"OFF"

    def getResOduOciLed(self, parameters):
        '''**RES:AL:ODUOCI?** -
        Query the ON/OFF LED state for ODU:OCI alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.oduOci.led.isRed else b"OFF"

    def getResOofLed(self, parameters):
        '''**RES:AL:OOF?** -
        Query the ON/OFF LED state for OOF alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.oof.led.isRed else b"OFF"

    def getResOomLed(self, parameters):
        '''**RES:AL:OOM?** -
        Query the ON/OFF LED state for OOM alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.oom.led.isRed else b"OFF"

    def getResOoomfiLed(self, parameters):
        '''**RES:AL:OOOMFI?** -
        Query the ON/OFF LED state for OOOMFI alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.ooomfi.led.isRed else b"OFF"

    def getResOpuAisLed(self, parameters):
        '''**RES:AL:OPUAIS?** -
        Query the ON/OFF LED state for OPU:AIS alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.opuAis.led.isRed else b"OFF"

    def getResOpuC8SyncLed(self, parameters):
        '''**RES:AL:OPUCMSYNC?** -
        Query the ON/OFF LED state for OPU:CM SYNC alarm ?.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.opuC8Sync.led.isRed else b"OFF"

    def getResOpuCsfLed(self, parameters):
        '''**RES:AL:OPUCSF?** -
        Query the ON/OFF LED state for OPU:CSF alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.opuCsf.led.isRed else b"OFF"

    def getResOpuFreWideLed(self, parameters):
        '''**RES:AL:OPUFREQWIDE?** -
        Query the ON/OFF LED state for OPU:FREQ WIDE alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.opuFreqWide.led.isRed else b"OFF"

    def getResOpuPlmLed(self, parameters):
        '''**RES:AL:OPUPLM?** -
        Query the ON/OFF LED state for OPU:PLM alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.opuPlm.led.isRed else b"OFF"

    def getResOtuAisLed(self, parameters):
        '''**RES:AL:OTUAIS?** -
        Query the ON/OFF LED state for OTU:AIS alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.otuAis.led.isRed else b"OFF"

    def getResOtuBdiLed(self, parameters):
        '''**RES:AL:OTUBDI?** -
        Query the ON/OFF LED state for OTU:BDI alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.otuBdi.led.isRed else b"OFF"

    def getResOtuBiaeLed(self, parameters):
        '''**RES:AL:OTUBIAE?** -
        Query the ON/OFF LED state for OTU:BIAE alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.otuBiae.led.isRed else b"OFF"

    def getResOtuIaeLed(self, parameters):
        '''**RES:AL:OTUIAE?** -
        Query the ON/OFF LED state for OTU:IAE alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.otuIae.led.isRed else b"OFF"

    def getResPatSynLed(self, parameters):
        '''**RES:AL:PATsync?** -
        Query the ON/OFF LED state for PAT SYNC alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.patternSync.led.isRed else b"OFF"

    def getResPausedLed(self, parameters):
        '''**RES:AL:PAUSED?** -
        Query the ON/OFF LED state for Paused alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.ppPaused.led.isRed else b"OFF"

    def getResTcm1BdLed(self, parameters):
        '''**RES:AL:TCM1BDI?** -
        Query the ON/OFF LED state for TCM1:BDI alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.tcmBdi[0].led.isRed else b"OFF"

    def getResTcm2BdLed(self, parameters):
        '''**RES:AL:TCM2BDI?** -
        Query the ON/OFF LED state for TCM2:BDI alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.tcmBdi[1].led.isRed else b"OFF"

    def getResTcm3BdLed(self, parameters):
        '''**RES:AL:TCM3BDI?** -
        Query the ON/OFF LED state for TCM3:BDI alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.tcmBdi[2].led.isRed else b"OFF"

    def getResTcm4BdLed(self, parameters):
        '''**RES:AL:TCM4BDI?** -
        Query the ON/OFF LED state for TCM4:BDI alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.tcmBdi[3].led.isRed else b"OFF"

    def getResTcm5BdLed(self, parameters):
        '''**RES:AL:TCM5BDI?** -
        Query the ON/OFF LED state for TCM5:BDI alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.tcmBdi[4].led.isRed else b"OFF"

    def getResTcm6BdLed(self, parameters):
        '''**RES:AL:TCM6BDI?** -
        Query the ON/OFF LED state for TCM6:BDI alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.tcmBdi[5].led.isRed else b"OFF"

    def getResTcm1BiaeLed(self, parameters):
        '''**RES:AL:TCM1BIAE?** -
        Query the ON/OFF LED state for TCM1:BIAE alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.tcmBiae[0].led.isRed else b"OFF"

    def getResTcm2BiaeLed(self, parameters):
        '''**RES:AL:TCM2BIAE?** -
        Query the ON/OFF LED state for TCM2:BIAE alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.tcmBiae[1].led.isRed else b"OFF"

    def getResTcm3BiaeLed(self, parameters):
        '''**RES:AL:TCM3BIAE?** -
        Query the ON/OFF LED state for TCM3:BIAE alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.tcmBiae[2].led.isRed else b"OFF"

    def getResTcm4BiaeLed(self, parameters):
        '''**RES:AL:TCM4BIAE?** -
        Query the ON/OFF LED state for TCM4:BIAE alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.tcmBiae[3].led.isRed else b"OFF"

    def getResTcm5BiaeLed(self, parameters):
        '''**RES:AL:TCM5BIAE?** -
        Query the ON/OFF LED state for TCM5:BIAE alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.tcmBiae[4].led.isRed else b"OFF"

    def getResTcm6BiaeLed(self, parameters):
        '''**RES:AL:TCM6BIAE?** -
        Query the ON/OFF LED state for TCM6:BIAE alarm.
        '''
        self.globals.veexOtn.stats.update()
        return b"ON" if self.globals.veexOtn.stats.tcmBiae[5].led.isRed else b"OFF"

    def bitAvgErrRate(self, parameters):
        '''**RES:BIT:AVE?** -
        Query the BIT average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.bit.avgRate

    def bitErrCount(self, parameters):
        '''**RES:BIT:COUNt?** -
        Query the BIT error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.bit.count

    def bitErrRate(self, parameters):
        '''**RES:BIT:RATe?** -
        Query the BIT current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.bit.currRate

    def getResClockAlrm(self, parameters):
        '''**RES:CLOCK:Secs?** -
        Query the number of TX Clock Loss alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.clock.secs

    def c8Crc8AvgErrRate(self, parameters):
        '''**RES:CMCRC8:AVE?** -
        Query the OPU:CM CRC8 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.opuC8Crc8.avgRate

    def c8Crc8ErrCount(self, parameters):
        '''**RES:CMCRC8:COUNt?** -
        Query the OPU:CM CRC8 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.opuC8Crc8.count

    def c8Crc8ErrRate(self, parameters):
        '''**RES:CMCRC8:RATe?** -
        Query the OPU:CM CRC8 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.opuC8Crc8.currRate

    def resPowerSecs(self, parameters):
        '''**RES:CPPOWERLOSS:Secs?** -
        Query the number of A/C power loss alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.cpPowerLoss.secs

    def getEventLog(self, parameters):
        '''**RES:EVENTLOG <StartRecord>?** -
        Queries the events listed in the Event Log, up to a maximum of 64 events,
        starting with the <StartRecord> number specified.
        Note: TODO....
        '''
        self.globals.veexOtn.stats.update()
        return b"TBD"

    def fecCorrAvgErrRate(self, parameters):
        '''**RES:FEC:CORR:AVE?** -
        Query the FEC:COR average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.fecCorrected.avgRate

    def fecCorrErrCount(self, parameters):
        '''**RES:FEC:CORR:COUNt?** -
        Query the FEC:COR error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.fecCorrected.count

    def fecCorrErrRate(self, parameters):
        '''**RES:FEC:CORR:RATe?** -
        Query the FEC:COR current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.fecCorrected.currRate

    def fecUncAvgErrRate(self, parameters):
        '''**RES:FEC:UNCORR:AVE?** -
        Query the FEC:UNCOR average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.fecUncorrected.avgRate

    def fecUncErrCount(self, parameters):
        '''**RES:FEC:UNCORR:COUNt?** -
        Query the FEC:UNCOR error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.fecUncorrected.count

    def fecUncErrRate(self, parameters):
        '''**RES:FEC:UNCORR:RATe?** -
        Query the FEC:UNCOR current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.fecUncorrected.currRate

    def frameAvgErrRate(self, parameters):
        '''**RES:FRAME:AVE?** -
        Query the FRAME average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.frame.avgRate

    def frameErrCount(self, parameters):
        '''**RES:FRAME:COUNt?** -
        Query the FRAME error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.frame.count

    def frameErrRate(self, parameters):
        '''**RES:FRAME:RATe?** -
        Query the FRAME current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.frame.currRate

    def getResFreWideAlrm(self, parameters):
        '''**RES:FREQWIDE:Secs?** -
        Query the number of Frequency Wide alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.rxFreqWide.secs

    def getResPjcsCount(self, parameters):
        '''**RES:JUSTification:Secs?** -
        Query the number of Justification Seconds for Async SONETSDH mappings.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.justifySecs

    def lan1027bBlockAvgErrRate(self, parameters):
        '''**RES:LAN:1027BBLOCK:AVE?** -
        Query the LAN 1027B BLOCK average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.block1027b.avgRate

    def lan1027bBlockErrCount(self, parameters):
        '''**RES:LAN:1027BBLOCK:COUNt?** -
        Query the LAN 1027B BLOCK error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.block1027b.count

    def lan1027bBlockErrRate(self, parameters):
        '''**RES:LAN:1027BBLOCK:RATe?** -
        Query the LAN 1027B BLOCK current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.block1027b.currRate

    def lan0OtnBip8AvgErrRate(self, parameters):
        '''**RES:LAN0:OTNBIP8:AVE?** -
        Query the LAN OTN:BIP8 on Lane 0 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanOtnBip8[0].avgRate

    def lan0OtnBip8ErrCount(self, parameters):
        '''**RES:LAN0:OTNBIP8:COUNt?** -
        Query the LAN OTN:BIP8 on Lane 0 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.lanOtnBip8[0].count

    def lan0OtnBip8ErrRate(self, parameters):
        '''**RES:LAN0:OTNBIP8:RATe?** -
        Query the LAN OTN:BIP8 on Lane 0 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanOtnBip8[0].currRate

    def lan1OtnBip8AvgErrRate(self, parameters):
        '''**RES:LAN1:OTNBIP8:AVE?** -
        Query the LAN OTN:BIP8 on Lane 1 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanOtnBip8[1].avgRate

    def lan1OtnBip8ErrCount(self, parameters):
        '''**RES:LAN1:OTNBIP8:COUNt?** -
        Query the LAN OTN:BIP8 on Lane 1 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.lanOtnBip8[1].count

    def lan1OtnBip8ErrRate(self, parameters):
        '''**RES:LAN1:OTNBIP8:RATe?** -
        Query the LAN OTN:BIP8 on Lane 1 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanOtnBip8[1].currRate

    def lan2OtnBip8AvgErrRate(self, parameters):
        '''**RES:LAN2:OTNBIP8:AVE?** -
        Query the LAN OTN:BIP8 on Lane 2 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanOtnBip8[2].avgRate

    def lan2OtnBip8ErrCount(self, parameters):
        '''**RES:LAN2:OTNBIP8:COUNt?** -
        Query the LAN OTN:BIP8 on Lane 2 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.lanOtnBip8[2].count

    def lan2OtnBip8ErrRate(self, parameters):
        '''**RES:LAN2:OTNBIP8:RATe?** -
        Query the LAN OTN:BIP8 on Lane 2 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanOtnBip8[2].currRate

    def lan3OtnBip8AvgErrRate(self, parameters):
        '''**RES:LAN3:OTNBIP8:AVE?** -
        Query the LAN OTN:BIP8 on Lane 3 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanOtnBip8[3].avgRate

    def lan3OtnBip8ErrCount(self, parameters):
        '''**RES:LAN3:OTNBIP8:COUNt?** -
        Query the LAN OTN:BIP8 on Lane 3 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.lanOtnBip8[3].count

    def lan3OtnBip8ErrRate(self, parameters):
        '''**RES:LAN3:OTNBIP8:RATe?** -
        Query the LAN OTN:BIP8 on Lane 3 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanOtnBip8[3].currRate

    def lan0PcsBip8AvgErrRate(self, parameters):
        '''**RES:LAN0:PCSBIP8:AVE?** -
        Query the LAN PCS:BIP8 on Lane 0 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanPcsBip8[0].avgRate

    def lan0PcsBip8ErrCount(self, parameters):
        '''**RES:LAN0:PCSBIP8:COUNt?** -
        Query the LAN PCS:BIP8 on Lane 0 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.lanPcsBip8[0].count

    def lan0PcsBip8ErrRate(self, parameters):
        '''**RES:LAN0:PCSBIP8:RATe?** -
        Query the LAN PCS:BIP8 on Lane 0 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanPcsBip8[0].currRate

    def lan1PcsBip8AvgErrRate(self, parameters):
        '''**RES:LAN1:PCSBIP8:AVE?** -
        Query the LAN PCS:BIP8 on Lane 1 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanPcsBip8[1].avgRate

    def lan1PcsBip8ErrCount(self, parameters):
        '''**RES:LAN1:PCSBIP8:COUNt?** -
        Query the LAN PCS:BIP8 on Lane 1 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.lanPcsBip8[1].count

    def lan1PcsBip8ErrRate(self, parameters):
        '''**RES:LAN1:PCSBIP8:RATe?** -
        Query the LAN PCS:BIP8 on Lane 1 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanPcsBip8[1].currRate

    def lan2PcsBip8AvgErrRate(self, parameters):
        '''**RES:LAN2:PCSBIP8:AVE?** -
        Query the LAN PCS:BIP8 on Lane 2 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanPcsBip8[2].avgRate

    def lan2PcsBip8ErrCount(self, parameters):
        '''**RES:LAN2:PCSBIP8:COUNt?** -
        Query the LAN PCS:BIP8 on Lane 2 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.lanPcsBip8[2].count

    def lan2PcsBip8ErrRate(self, parameters):
        '''**RES:LAN2:PCSBIP8:RATe?** -
        Query the LAN PCS:BIP8 on Lane 2 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanPcsBip8[2].currRate

    def lan3PcsBip8AvgErrRate(self, parameters):
        '''**RES:LAN3:PCSBIP8:AVE?** -
        Query the LAN PCS:BIP8 on Lane 3 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanPcsBip8[3].avgRate

    def lan3PcsBip8ErrCount(self, parameters):
        '''**RES:LAN3:PCSBIP8:COUNt?** -
        Query the LAN PCS:BIP8 on Lane 3 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.lanPcsBip8[3].count

    def lan3PcsBip8ErrRate(self, parameters):
        '''**RES:LAN3:PCSBIP8:RATe?** -
        Query the LAN PCS:BIP8 on Lane 3 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.lanPcsBip8[3].currRate

    def getResLofAlrm(self, parameters):
        '''**RES:LOF:Secs?** -
        Query the number of LOF alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.lof.secs

    def getResLomAlrm(self, parameters):
        '''**RES:LOM:Secs?** -
        Query the number of LOM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.lom.secs

    def getResLoomfiAlrm(self, parameters):
        '''**RES:LOOMFI:Secs?** -
        Query the number of LOOMFI alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.loomfi.secs

    def getResLosAlrm(self, parameters):
        '''**RES:LOS:Secs?** -
        Query the number of seconds LOS alarm has been active.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.los.secs

    def getMultiChanSummary(self, parameters):
        '''**RES:MC:SUMmary? <channels>** -
        When the OTN Mapping is configured for a Multi-Channel payload structure,
        Query all of the Error or Alarm states for the select channel number(s).
        Note: TODO....
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = b"TBD"

        self.globals.veexOtn.stats.update()
        return response

    def mfasAvgErrRate(self, parameters):
        '''**RES:MFAS:AVE?** -
        Query the MFAS average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.mfas.avgRate

    def mfasErrCount(self, parameters):
        '''**RES:MFAS:COUNt?** -
        Query the MFAS error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.mfas.count

    def mfasErrRate(self, parameters):
        '''**RES:MFAS:RATe?** -
        Query the MFAS current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.mfas.currRate

    def getResNpjcCount(self, parameters):
        '''**RES:NEGJUSTification:COUN?** -
        Query the Negative Justification count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.negJustify.count

    def oduBeiAvgErrRate(self, parameters):
        '''**RES:ODU:BEI:AVE?** -
        Query the ODU:BEI average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.oduBei.avgRate

    def oduBeiErrCount(self, parameters):
        '''**RES:ODU:BEI:COUNt?** -
        Query the ODU:BEI error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.oduBei.count

    def oduBeiErrRate(self, parameters):
        '''**RES:ODU:BEI:RATe?** -
        Query the ODU:BEI current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.oduBei.currRate

    def oduBip8AvgErrRate(self, parameters):
        '''**RES:ODU:BIP8:AVE?** -
        Query the ODU:BIP8 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.oduBip8.avgRate

    def oduBip8ErrCount(self, parameters):
        '''**RES:ODU:BIP8:COUNt?** -
        Query the ODU:BIP8 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.oduBip8.count

    def oduBip8ErrRate(self, parameters):
        '''**RES:ODU:BIP8:RATe?** -
        Query the ODU:BIP8 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.oduBip8.currRate

    def getResOduAisAlrm(self, parameters):
        '''**RES:ODUAIS:Secs?** -
        Query the number of ODU:AIS alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.oduAis.secs

    def getResOduBdiAlrm(self, parameters):
        '''**RES:ODUBDI:Secs?** -
        Query the number of ODU:BDI alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.oduBdi.secs

    def getResOduDapAlrm(self, parameters):
        '''**RES:ODUDAPI:Secs?** -
        Query the number of ODU:DAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.oduDapiTim.secs

    def getResOduLckAlrm(self, parameters):
        '''**RES:ODULCK:Secs?** -
        Query the number of ODU:LCK alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.oduLck.secs

    def getResOduOciAlrm(self, parameters):
        '''**RES:ODUOCI:Secs?** -
        Query the number of ODU:OCI alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.oduOci.secs

    def getResOduSapAlrm(self, parameters):
        '''**RES:ODUSAPI:Secs?** -
        Query the number of ODU:SAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.oduSapiTim.secs

    def omfiAvgErrRate(self, parameters):
        '''**RES:OMFI:AVE?** -
        Query the OMFI average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.omfi.avgRate

    def omfiErrCount(self, parameters):
        '''**RES:OMFI:COUNt?** -
        Query the OMFI error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.omfi.count

    def omfiErrRate(self, parameters):
        '''**RES:OMFI:RATe?** -
        Query the OMFI current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.omfi.currRate


    def getResOofAlrm(self, parameters):
        '''**RES:OOF:Secs?** -
        Query the number of OOF alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.oof.secs

    def getResOomAlrm(self, parameters):
        '''**RES:OOM:Secs?** -
        Query the number of OOM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.oom.secs

    def getResOoomfiAlrm(self, parameters):
        '''**RES:OOOMFI:Secs?** -
        Query the number of OOOMFI alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.ooomfi.secs

    def getResOpuAisAlrm(self, parameters):
        '''**RES:OPUAIS:Secs?** -
        Query the number of OPU:AIS alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.opuAis.secs

    def getResOpuC8SyncAlrm(self, parameters):
        '''**RES:OPUCMSYNC:Secs?** -
        Query the number of OPU:CM SYNC alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.opuC8Sync.secs

    def getResOpuCsfAlrm(self, parameters):
        '''**RES:OPUCSF:Secs?** -
        Query the number of OPU:CSF alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.opuCsf.secs

    def getResOpuFreWideAlrm(self, parameters):
        '''**RES:OPUFREQWIDE:Secs?** -
        Query the number of OPU:Freguency Wide alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.opuFreqWide.secs

    def getResOpuPlmAlrm(self, parameters):
        '''**RES:OPUPLM:Secs?** -
        Query the number of OPU:PLM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.opuPlm.secs

    def otuBeiAvgErrRate(self, parameters):
        '''**RES:OTU:BEI:AVE?** -
        Query the average OTU BEI error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.otuBei.avgRate

    def otuBeiErrCount(self, parameters):
        '''**RES:OTU:BEI:COUNt?** -
        Query the count of OTU BEI errors.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.otuBei.count

    def otuBeiErrRate(self, parameters):
        '''**RES:OTU:BEI:RATe?** -
        Query the current OTU BEI error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.otuBei.currRate

    def otuBip8AvgErrRate(self, parameters):
        '''**RES:OTU:BIP8:AVE?** -
        Query the average OTU BIP8 error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.otuBip8.avgRate

    def otuBip8ErrCount(self, parameters):
        '''**RES:OTU:BIP8:COUNt?** -
        Query the count of OTU BIP8 errors.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.otuBip8.count

    def otuBip8ErrRate(self, parameters):
        '''**RES:OTU:BIP8:RATe?** -
        Query the current OTU BIP8 error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.otuBip8.currRate

    def getResOtuAisAlrm(self, parameters):
        '''**RES:OTUAIS:Secs?** -
        Query the number of OTU:AIS alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.otuAis.secs

    def getResOtuBdiAlrm(self, parameters):
        '''**RES:OTUBDI:Secs?** -
        Query the number of OTU:BDI alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.otuBdi.secs

    def getResOtuBiaeAlrm(self, parameters):
        '''**RES:OTUBIAE:Secs?** -
        Query the number of OTU:BIAE alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.otuBiae.secs

    def getResOtuDapAlrm(self, parameters):
        '''**RES:OTUDAPI:Secs?** -
        Query the number of OTU:DAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.otuDapiTim.secs

    def getResOtuIaeAlrm(self, parameters):
        '''**RES:OTUIAE:Secs?** -
        Query the number of OTU:IAE alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.otuIae.secs

    def getResOtuSapAlrm(self, parameters):
        '''**RES:OTUSAPI:Secs?** -
        Query the number of OTU:SAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.otuSapiTim.secs

    def getResPatSynAlrm(self, parameters):
        '''**RES:PATsync:Secs?** -
        Query the number of Pat Sync alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.patternSync.secs

    def getResPausedAlrm(self, parameters):
        '''**RES:PAUSED:Secs?** -
        Query the number of seconds the active test has been Paused.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.ppPaused.secs

    def getResPpjcCount(self, parameters):
        '''**RES:POSJUSTification:COUN?** -
        Query the Positive Justification count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.posJustify.count

    def getResPwrHotAlrm(self, parameters):
        '''**RES:PWRHOT:Secs?** -
        Query the number of Power Hot alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.rxPowerHot.secs

    def getResPwrLowAlrm(self, parameters):
        '''**RES:PWRLOW:Secs?** -
        Query the number of Power Low alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.rxPowerLow.secs

    def getResPwrWarmAlrm(self, parameters):
        '''**RES:PWRWARM:Secs?** -
        Query the number of Power Warm alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.rxPowerWarm.secs

    def getResApsFrameLast(self, parameters):
        '''**RES:RTD:FRAME:LAST?** -
        Query the current/last Round Trip Delay duration (measured in frames) of an RTD test.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d frames" % self.globals.veexOtn.stats.sdtSwitchTime

    def getResApsFrameMax(self, parameters):
        '''**RES:RTD:FRAME:MAX?** -
        Query the slowest Round Trip Delay duration (measured in frames) of an RTD test.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d frames" % self.globals.veexOtn.stats.maxSdtSwitchTime

    def getResApsFrameMin(self, parameters):
        '''**RES:RTD:FRAME:MIN?** -
        Query the fastest Round Trip Delay duration (measured in frames) of an RTD test.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d frames" % self.globals.veexOtn.stats.minSdtSwitchTime

    def getResApsState(self, parameters):
        '''**RES:RTD:STATE?** -
        Query the current status of the Round Trip Delay State.
        '''
        self.globals.veexOtn.stats.update()
        if self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_STOPPED:
            response = b"RTD STOP"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_ARMED:
            response = b"ARMED RTD SINGLE"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_RUNNING:
            response = b"RUNNING RTD SINGLE"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_CONT_ARM:
            response = b"ARMED RTD CONTINUOUS"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_CONT_RUN:
            response = b"RUNNING RTD CONTINUOUS"
        else:
            response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def getResApsTimeLast(self, parameters):
        '''**RES:RTD:TIME:LAST?** -
        Query the current/last Round Trip Delay duration (measured in seconds) of an RTD test.
        '''
        self.globals.veexOtn.stats.update()
        time = float(self.globals.veexOtn.stats.sdtSwitchTime) / self.globals.veexOtn.stats.sdtSwitchFrameRate
        return b"%.6f seconds" % (time * 1000.0,)

    def getResApsTimeMax(self, parameters):
        '''**RES:RTD:TIME:MAX?** -
        Query the slowest Round Trip Delay duration (measured in seconds) of an RTD test.
        '''
        self.globals.veexOtn.stats.update()
        time = float(self.globals.veexOtn.stats.maxSdtSwitchTime) / self.globals.veexOtn.stats.sdtSwitchFrameRate
        return b"%.6f seconds" % (time * 1000.0,)

    def getResApsTimeMin(self, parameters):
        '''**RES:RTD:TIME:MIN?** -
        Query the fastest Round Trip Delay duration (measured in seconds) of an RTD test.
        '''
        self.globals.veexOtn.stats.update()
        time = float(self.globals.veexOtn.stats.minSdtSwitchTime) / self.globals.veexOtn.stats.sdtSwitchFrameRate
        return b"%.6f seconds" % (time * 1000.0,)

    def getResRxC8Plus1(self, parameters):
        '''**RES:RXCMJUST:PLUS1?** -
        Query the number of GMP Cm frames received for the specific Cm justification criteria.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.rxGmpC8Plus1.count
 
    def getResRxC8Plus2(self, parameters):
        '''**RES:RXCMJUST:PLUS2?** -
        Query the number of GMP Cm frames received for the specific Cm justification criteria.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.rxGmpC8Plus2.count

    def getResRxC8Minus1(self, parameters):
        '''**RES:RXCMJUST:MINUS1?** -
        Query the number of GMP Cm frames received for the specific Cm justification criteria.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.rxGmpC8Minus1.count

    def getResRxC8Minus2(self, parameters):
        '''**RES:RXCMJUST:MINUS2?** -
        Query the number of GMP Cm frames received for the specific Cm justification criteria.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.rxGmpC8Minus2.count

    def getResRxC8Gtr2(self, parameters):
        '''**RES:RXCMJUST:GTR2?** -
        Query the number of GMP Cm frames received for the specific Cm justification criteria.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.rxGmpC8Gtr2.count

    def getResRxC8Lt2(self, parameters):
        '''**RES:RXCMJUST:LT2?** -
        Query the number of GMP Cm frames received for the specific Cm justification criteria.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.rxGmpC8Lt2.count

    def getResRxC8GtrItu(self, parameters):
        '''**RES:RXCMJUST:GTRITU?** -
        Query the number of GMP Cm frames received for the specific Cm justification criteria.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.rxGmpC8GtrItu.count

    def getResRxC8LtItu(self, parameters):
        '''**RES:RXCMJUST:LTITU?** -
        Query the number of GMP Cm frames received for the specific Cm justification criteria.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.rxGmpC8LtItu.count

    def getRxC8Max(self, parameters):
        '''**RES:RXCMMAX?** -
        Query the Maximum GMP Cm justification value received during the current test.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.rxGmpC8Largest

    def getRxC8Min(self, parameters):
        '''**RES:RXCMMIN?** -
        Query the Minimum GMP Cm justification value received during the current test.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.rxGmpC8Smallest

    def _getAlarmToken(self, cxName, cxIndex, protoAlarm):
        '''Used to help processors complete a string of current Alarms
        '''
        retVal = b""
        csSeconds = b"%d" % protoAlarm.secs
        if protoAlarm.led.isRed:
            retVal = cxName + b" " + cxIndex + b" 1 " + csSeconds + b","
        elif protoAlarm.led.wasRed:
            retVal = cxName + b" " + cxIndex + b" 0 " + csSeconds + b","
        return retVal

    def getCurrentAlarms(self, parameters):
        '''**RES:SCANALARMS?** -
        Query all ALARM results statistics and returns a list of any currently active or previously active alarms.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        self.globals.veexOtn.sets.update()
        self.globals.veexOtn.stats.update()
        muxLevel = -1
        isMuxMapping = False
        if len(paramList) >= 1:
            muxLevel = ParseUtils.checkNumeric(paramList[0].head)
            if muxLevel > veexlib.OTN_ODTU_LEVEL_ODU_3 or muxLevel < 0:
                return self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
        if muxLevel == -1:
            muxLevel = self.globals.veexOtn.stats.odtuStatsLevel
            if (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_01_PT_20) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_02_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_12_PT_20) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_12_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_03_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_13_PT_20) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_13_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_23_PT_20) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_23_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_2E3_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_04_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_14_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_24_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_2E4_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_34_PT_21):
                isMuxMapping = True
            if muxLevel > veexlib.OTN_ODTU_LEVEL_ODU_3 and isMuxMapping == True:
                return self._errorResponse(ScpiErrorCode.INVALID_SETTINGS)
            elif isMuxMapping == False:
                muxLevel = -1
        response += ScpiOtn._getAlarmToken(b"Paused",b"0",self.globals.veexOtn.stats.testPaused)
        response += ScpiOtn._getAlarmToken(b"LOS",b"1",self.globals.veexOtn.stats.los)
        response += ScpiOtn._getAlarmToken(b"LOF",b"2",self.globals.veexOtn.stats.lof)
        response += ScpiOtn._getAlarmToken(b"OOF",b"3",self.globals.veexOtn.stats.oof)
        response += ScpiOtn._getAlarmToken(b"Lom",b"4",self.globals.veexOtn.stats.lom)
        response += ScpiOtn._getAlarmToken(b"Oom",b"5",self.globals.veexOtn.stats.oom)
        response += ScpiOtn._getAlarmToken(b"OtuAis",b"6",self.globals.veexOtn.stats.otuAis)
        response += ScpiOtn._getAlarmToken(b"OtuIae",b"7",self.globals.veexOtn.stats.otuIae)
        response += ScpiOtn._getAlarmToken(b"OtuBdi",b"8",self.globals.veexOtn.stats.otuBdi)
        response += ScpiOtn._getAlarmToken(b"OtuSapiTim",b"9",self.globals.veexOtn.stats.otuSapiTim)
        response += ScpiOtn._getAlarmToken(b"OtuDapiTim",b"10",self.globals.veexOtn.stats.otuDapiTim)
        response += ScpiOtn._getAlarmToken(b"OduAis",b"11",self.globals.veexOtn.stats.oduAis)
        response += ScpiOtn._getAlarmToken(b"OduLck",b"12",self.globals.veexOtn.stats.oduLck)
        response += ScpiOtn._getAlarmToken(b"OduOci",b"13",self.globals.veexOtn.stats.oduOci)
        response += ScpiOtn._getAlarmToken(b"OduBdi",b"14",self.globals.veexOtn.stats.oduBdi)
        response += ScpiOtn._getAlarmToken(b"OduSapiTim",b"15",self.globals.veexOtn.stats.oduSapiTim)
        response += ScpiOtn._getAlarmToken(b"OduDapiTim",b"16",self.globals.veexOtn.stats.oduDapiTim)
        response += ScpiOtn._getAlarmToken(b"OpuPlm",b"17",self.globals.veexOtn.stats.opuPlm)
        response += ScpiOtn._getAlarmToken(b"OpuAis",b"18",self.globals.veexOtn.stats.opuAis)
        response += ScpiOtn._getAlarmToken(b"OpuCsf",b"19",self.globals.veexOtn.stats.opuCsf)
        response += ScpiOtn._getAlarmToken(b"Loomfi",b"20",self.globals.veexOtn.stats.loomfi)
        response += ScpiOtn._getAlarmToken(b"Ooomfi",b"21",self.globals.veexOtn.stats.ooomfi)
        response += ScpiOtn._getAlarmToken(b"OpuCmSync",b"22",self.globals.veexOtn.stats.opuC8Sync)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            response += ScpiOtn._getAlarmToken(b"MuxLof",b"23",self.globals.veexOtn.odtuStats[muxLevel].lof)
            response += ScpiOtn._getAlarmToken(b"MuxOof",b"24",self.globals.veexOtn.odtuStats[muxLevel].oof)
            response += ScpiOtn._getAlarmToken(b"MuxLom",b"25",self.globals.veexOtn.odtuStats[muxLevel].lom)
            response += ScpiOtn._getAlarmToken(b"MuxOom",b"26",self.globals.veexOtn.odtuStats[muxLevel].oom)
            response += ScpiOtn._getAlarmToken(b"MuxOduAis",b"27",self.globals.veexOtn.odtuStats[muxLevel].oduAis)
            response += ScpiOtn._getAlarmToken(b"MuxOduLck",b"28",self.globals.veexOtn.odtuStats[muxLevel].oduLck)
            response += ScpiOtn._getAlarmToken(b"MuxOduOci",b"29",self.globals.veexOtn.odtuStats[muxLevel].oduOci)
            response += ScpiOtn._getAlarmToken(b"MuxOduBdi",b"30",self.globals.veexOtn.odtuStats[muxLevel].oduBdi)
            response += ScpiOtn._getAlarmToken(b"MuxOduSapiTim",b"31",self.globals.veexOtn.odtuStats[muxLevel].oduSapiTim)
            response += ScpiOtn._getAlarmToken(b"MuxOduDapiTim",b"32",self.globals.veexOtn.odtuStats[muxLevel].oduDapiTim)
            response += ScpiOtn._getAlarmToken(b"MuxOpuPlm",b"33",self.globals.veexOtn.odtuStats[muxLevel].opuPlm)
            response += ScpiOtn._getAlarmToken(b"MuxOpuCsf",b"34",self.globals.veexOtn.odtuStats[muxLevel].opuCsf)
            response += ScpiOtn._getAlarmToken(b"MuxOpuCmSync",b"35",self.globals.veexOtn.odtuStats[muxLevel].opuC8Sync)
        else:
            response += ScpiOtn._getAlarmToken(b"MuxLof",b"23",self.globals.veexOtn.stats.odtuLof)
            response += ScpiOtn._getAlarmToken(b"MuxOof",b"24",self.globals.veexOtn.stats.odtuOof)
            response += ScpiOtn._getAlarmToken(b"MuxLom",b"25",self.globals.veexOtn.stats.odtuLom)
            response += ScpiOtn._getAlarmToken(b"MuxOom",b"26",self.globals.veexOtn.stats.odtuOom)
            response += ScpiOtn._getAlarmToken(b"MuxOduAis",b"27",self.globals.veexOtn.stats.odtuOduAis)
            response += ScpiOtn._getAlarmToken(b"MuxOduLck",b"28",self.globals.veexOtn.stats.odtuOduLck)
            response += ScpiOtn._getAlarmToken(b"MuxOduOci",b"29",self.globals.veexOtn.stats.odtuOduOci)
            response += ScpiOtn._getAlarmToken(b"MuxOduBdi",b"30",self.globals.veexOtn.stats.odtuOduBdi)
            response += ScpiOtn._getAlarmToken(b"MuxOduSapiTim",b"31",self.globals.veexOtn.stats.odtuOduSapiTim)
            response += ScpiOtn._getAlarmToken(b"MuxOduDapiTim",b"32",self.globals.veexOtn.stats.odtuOduDapiTim)
            response += ScpiOtn._getAlarmToken(b"MuxOpuPlm",b"33",self.globals.veexOtn.stats.odtuOpuPlm)
            response += ScpiOtn._getAlarmToken(b"MuxOpuCsf",b"34",self.globals.veexOtn.stats.odtuOpuCsf)
            response += ScpiOtn._getAlarmToken(b"MuxOpuCmSync",b"35",self.globals.veexOtn.stats.odtuOpuC8Sync)
        response += ScpiOtn._getAlarmToken(b"PatSync",b"36",self.globals.veexOtn.stats.patternSync)
        response += ScpiOtn._getAlarmToken(b"FreqWide",b"37",self.globals.veexOtn.stats.rxFreqWide)
        response += ScpiOtn._getAlarmToken(b"PowerHot",b"38",self.globals.veexOtn.stats.rxPowerHot)
        response += ScpiOtn._getAlarmToken(b"PowerWarm",b"39",self.globals.veexOtn.stats.rxPowerWarm)
        response += ScpiOtn._getAlarmToken(b"PowerLow",b"40",self.globals.veexOtn.stats.rxPowerLow)
        response += ScpiOtn._getAlarmToken(b"OtuBiae",b"41",self.globals.veexOtn.stats.otuBiae)
        response += ScpiOtn._getAlarmToken(b"Tcm1Bdi",b"42",self.globals.veexOtn.stats.tcmBdi[0])
        response += ScpiOtn._getAlarmToken(b"Tcm2Bdi",b"43",self.globals.veexOtn.stats.tcmBdi[1])
        response += ScpiOtn._getAlarmToken(b"Tcm3Bdi",b"44",self.globals.veexOtn.stats.tcmBdi[2])
        response += ScpiOtn._getAlarmToken(b"Tcm4Bdi",b"45",self.globals.veexOtn.stats.tcmBdi[3])
        response += ScpiOtn._getAlarmToken(b"Tcm5Bdi",b"46",self.globals.veexOtn.stats.tcmBdi[4])
        response += ScpiOtn._getAlarmToken(b"Tcm6Bdi",b"47",self.globals.veexOtn.stats.tcmBdi[5])
        response += ScpiOtn._getAlarmToken(b"Tcm1SapiTim",b"48",self.globals.veexOtn.stats.tcmSapiTim[0])
        response += ScpiOtn._getAlarmToken(b"Tcm2SapiTim",b"49",self.globals.veexOtn.stats.tcmSapiTim[1])
        response += ScpiOtn._getAlarmToken(b"Tcm3SapiTim",b"50",self.globals.veexOtn.stats.tcmSapiTim[2])
        response += ScpiOtn._getAlarmToken(b"Tcm4SapiTim",b"51",self.globals.veexOtn.stats.tcmSapiTim[3])
        response += ScpiOtn._getAlarmToken(b"Tcm5SapiTim",b"52",self.globals.veexOtn.stats.tcmSapiTim[4])
        response += ScpiOtn._getAlarmToken(b"Tcm6SapiTim",b"53",self.globals.veexOtn.stats.tcmSapiTim[5])
        response += ScpiOtn._getAlarmToken(b"Tcm1DapiTim",b"54",self.globals.veexOtn.stats.tcmDapiTim[0])
        response += ScpiOtn._getAlarmToken(b"Tcm2DapiTim",b"55",self.globals.veexOtn.stats.tcmDapiTim[1])
        response += ScpiOtn._getAlarmToken(b"Tcm3DapiTim",b"56",self.globals.veexOtn.stats.tcmDapiTim[2])
        response += ScpiOtn._getAlarmToken(b"Tcm4DapiTim",b"57",self.globals.veexOtn.stats.tcmDapiTim[3])
        response += ScpiOtn._getAlarmToken(b"Tcm5DapiTim",b"58",self.globals.veexOtn.stats.tcmDapiTim[4])
        response += ScpiOtn._getAlarmToken(b"Tcm6DapiTim",b"59",self.globals.veexOtn.stats.tcmDapiTim[5])
        response += ScpiOtn._getAlarmToken(b"Tcm1Biae",b"60",self.globals.veexOtn.stats.tcmBiae[0])
        response += ScpiOtn._getAlarmToken(b"Tcm2Biae",b"61",self.globals.veexOtn.stats.tcmBiae[1])
        response += ScpiOtn._getAlarmToken(b"Tcm3Biae",b"62",self.globals.veexOtn.stats.tcmBiae[2])
        response += ScpiOtn._getAlarmToken(b"Tcm4Biae",b"63",self.globals.veexOtn.stats.tcmBiae[3])
        response += ScpiOtn._getAlarmToken(b"Tcm5Biae",b"64",self.globals.veexOtn.stats.tcmBiae[4])
        response += ScpiOtn._getAlarmToken(b"Tcm6Biae",b"65",self.globals.veexOtn.stats.tcmBiae[5])
        if muxLevel != -1:
            response += ScpiOtn._getAlarmToken(b"MuxTcm1Bdi",b"66",self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[0])
            response += ScpiOtn._getAlarmToken(b"MuxTcm2Bdi",b"67",self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[1])
            response += ScpiOtn._getAlarmToken(b"MuxTcm3Bdi",b"68",self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[2])
            response += ScpiOtn._getAlarmToken(b"MuxTcm4Bdi",b"69",self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[3])
            response += ScpiOtn._getAlarmToken(b"MuxTcm5Bdi",b"70",self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[4])
            response += ScpiOtn._getAlarmToken(b"MuxTcm6Bdi",b"71",self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[5])
            response += ScpiOtn._getAlarmToken(b"MuxTcm1SapiTim",b"72",self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[0])
            response += ScpiOtn._getAlarmToken(b"MuxTcm2SapiTim",b"73",self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[1])
            response += ScpiOtn._getAlarmToken(b"MuxTcm3SapiTim",b"74",self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[2])
            response += ScpiOtn._getAlarmToken(b"MuxTcm4SapiTim",b"75",self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[3])
            response += ScpiOtn._getAlarmToken(b"MuxTcm5SapiTim",b"76",self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[4])
            response += ScpiOtn._getAlarmToken(b"MuxTcm6SapiTim",b"77",self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[5])
            response += ScpiOtn._getAlarmToken(b"MuxTcm1DapiTim",b"78",self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[0])
            response += ScpiOtn._getAlarmToken(b"MuxTcm2DapiTim",b"79",self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[1])
            response += ScpiOtn._getAlarmToken(b"MuxTcm3DapiTim",b"80",self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[2])
            response += ScpiOtn._getAlarmToken(b"MuxTcm4DapiTim",b"81",self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[3])
            response += ScpiOtn._getAlarmToken(b"MuxTcm5DapiTim",b"82",self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[4])
            response += ScpiOtn._getAlarmToken(b"MuxTcm6DapiTim",b"83",self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[5])
            response += ScpiOtn._getAlarmToken(b"MuxTcm1Biae",b"84",self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[0])
            response += ScpiOtn._getAlarmToken(b"MuxTcm2Biae",b"85",self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[1])
            response += ScpiOtn._getAlarmToken(b"MuxTcm3Biae",b"86",self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[2])
            response += ScpiOtn._getAlarmToken(b"MuxTcm4Biae",b"87",self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[3])
            response += ScpiOtn._getAlarmToken(b"MuxTcm5Biae",b"88",self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[4])
            response += ScpiOtn._getAlarmToken(b"MuxTcm6Biae",b"89",self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[5])    
        else:
            response += ScpiOtn._getAlarmToken(b"MuxTcm1Bdi",b"66",self.globals.veexOtn.stats.odtuTcmBdi[0])
            response += ScpiOtn._getAlarmToken(b"MuxTcm2Bdi",b"67",self.globals.veexOtn.stats.odtuTcmBdi[1])
            response += ScpiOtn._getAlarmToken(b"MuxTcm3Bdi",b"68",self.globals.veexOtn.stats.odtuTcmBdi[2])
            response += ScpiOtn._getAlarmToken(b"MuxTcm4Bdi",b"69",self.globals.veexOtn.stats.odtuTcmBdi[3])
            response += ScpiOtn._getAlarmToken(b"MuxTcm5Bdi",b"70",self.globals.veexOtn.stats.odtuTcmBdi[4])
            response += ScpiOtn._getAlarmToken(b"MuxTcm6Bdi",b"71",self.globals.veexOtn.stats.odtuTcmBdi[5])
            response += ScpiOtn._getAlarmToken(b"MuxTcm1SapiTim",b"72",self.globals.veexOtn.stats.odtuTcmSapiTim[0])
            response += ScpiOtn._getAlarmToken(b"MuxTcm2SapiTim",b"73",self.globals.veexOtn.stats.odtuTcmSapiTim[1])
            response += ScpiOtn._getAlarmToken(b"MuxTcm3SapiTim",b"74",self.globals.veexOtn.stats.odtuTcmSapiTim[2])
            response += ScpiOtn._getAlarmToken(b"MuxTcm4SapiTim",b"75",self.globals.veexOtn.stats.odtuTcmSapiTim[3])
            response += ScpiOtn._getAlarmToken(b"MuxTcm5SapiTim",b"76",self.globals.veexOtn.stats.odtuTcmSapiTim[4])
            response += ScpiOtn._getAlarmToken(b"MuxTcm6SapiTim",b"77",self.globals.veexOtn.stats.odtuTcmSapiTim[5])
            response += ScpiOtn._getAlarmToken(b"MuxTcm1DapiTim",b"78",self.globals.veexOtn.stats.odtuTcmDapiTim[0])
            response += ScpiOtn._getAlarmToken(b"MuxTcm2DapiTim",b"79",self.globals.veexOtn.stats.odtuTcmDapiTim[1])
            response += ScpiOtn._getAlarmToken(b"MuxTcm3DapiTim",b"80",self.globals.veexOtn.stats.odtuTcmDapiTim[2])
            response += ScpiOtn._getAlarmToken(b"MuxTcm4DapiTim",b"81",self.globals.veexOtn.stats.odtuTcmDapiTim[3])
            response += ScpiOtn._getAlarmToken(b"MuxTcm5DapiTim",b"82",self.globals.veexOtn.stats.odtuTcmDapiTim[4])
            response += ScpiOtn._getAlarmToken(b"MuxTcm6DapiTim",b"83",self.globals.veexOtn.stats.odtuTcmDapiTim[5])
            response += ScpiOtn._getAlarmToken(b"MuxTcm1Biae",b"84",self.globals.veexOtn.stats.odtuTcmBiae[0])
            response += ScpiOtn._getAlarmToken(b"MuxTcm2Biae",b"85",self.globals.veexOtn.stats.odtuTcmBiae[1])
            response += ScpiOtn._getAlarmToken(b"MuxTcm3Biae",b"86",self.globals.veexOtn.stats.odtuTcmBiae[2])
            response += ScpiOtn._getAlarmToken(b"MuxTcm4Biae",b"87",self.globals.veexOtn.stats.odtuTcmBiae[3])
            response += ScpiOtn._getAlarmToken(b"MuxTcm5Biae",b"88",self.globals.veexOtn.stats.odtuTcmBiae[4])
            response += ScpiOtn._getAlarmToken(b"MuxTcm6Biae",b"89",self.globals.veexOtn.stats.odtuTcmBiae[5])    
        response += ScpiOtn._getAlarmToken(b"TxClockLoss",b"90",self.globals.veexOtn.stats.clock)
        response += ScpiOtn._getAlarmToken(b"OpuFreqWide",b"91",self.globals.veexOtn.stats.opuFreqWide)   
        if muxLevel != -1:
            response += ScpiOtn._getAlarmToken(b"MuxOpuFreqWide",b"92",self.globals.veexOtn.odtuStats[muxLevel].opuFreqWide)
        else:
            response += ScpiOtn._getAlarmToken(b"MuxOpuFreqWide",b"92",self.globals.veexOtn.stats.odtuOpuFreqWide)
        if len(response) == 0:
            response = b"+0"
        return response

    def _getErrorToken(self, cxName, cxIndex, protoError):
        '''Used to help processors complete a string of current Errors
        '''
        retVal = b""
        csErrorRate = b"%.2e" % protoError.avgRate
        if protoError.led.isRed:
            retVal = cxName + b" " + cxIndex + b" 1 " + csErrorRate + b","
        elif protoError.led.wasRed:
            retVal = cxName + b" " + cxIndex + b" 0 " + csErrorRate + b","
        return retVal
     
    def getCurrentErrors(self, parameters):
        '''**RES:SCANERRORS?** -
        Query all ERROR results statistics and returns a list of any currently active or previously active errors.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        self.globals.veexOtn.sets.update()
        self.globals.veexOtn.stats.update()
        muxLevel = -1
        isMuxMapping = False
        if len(paramList) >= 1:
            muxLevel = ParseUtils.checkNumeric(paramList[0].head)
            if muxLevel > veexlib.OTN_ODTU_LEVEL_ODU_3  or muxLevel < 0:
                return self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
        if muxLevel == -1:
            muxLevel = self.globals.veexOtn.stats.odtuStatsLevel
            if (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_01_PT_20) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_02_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_12_PT_20) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_12_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_03_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_13_PT_20) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_13_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_23_PT_20) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_23_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_2E3_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_04_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_14_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_24_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_2E4_PT_21) or \
               (self.globals.veexOtn.sets.rxMapping == veexlib.OTN_MAP_ODTU_34_PT_21):
                isMuxMapping = True
            if muxLevel > veexlib.OTN_ODTU_LEVEL_ODU_3 and isMuxMapping == True:
                return self._errorResponse(ScpiErrorCode.INVALID_SETTINGS)
            elif isMuxMapping == False:
                muxLevel = -1
        response += ScpiOtn._getErrorToken(b"Frame",b"0",self.globals.veexOtn.stats.frame)
        response += ScpiOtn._getErrorToken(b"Mfas",b"1",self.globals.veexOtn.stats.mfas)
        response += ScpiOtn._getErrorToken(b"FecUncorrected",b"2",self.globals.veexOtn.stats.fecUncorrected)
        response += ScpiOtn._getErrorToken(b"FecCorrected",b"3",self.globals.veexOtn.stats.fecCorrected)
        response += ScpiOtn._getErrorToken(b"OtuBip8",b"4",self.globals.veexOtn.stats.otuBip8)
        response += ScpiOtn._getErrorToken(b"OtuBei",b"5",self.globals.veexOtn.stats.otuBei)
        response += ScpiOtn._getErrorToken(b"OduBip8",b"6",self.globals.veexOtn.stats.oduBip8)
        response += ScpiOtn._getErrorToken(b"OduBei",b"7",self.globals.veexOtn.stats.oduBei)
        response += ScpiOtn._getErrorToken(b"OpuCmCrc8",b"8",self.globals.veexOtn.stats.opuC8Crc8)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            response += ScpiOtn._getErrorToken(b"MuxFrame",b"9",self.globals.veexOtn.odtuStats[muxLevel].frame)
            response += ScpiOtn._getErrorToken(b"MuxMfas",b"10",self.globals.veexOtn.odtuStats[muxLevel].mfas)
            response += ScpiOtn._getErrorToken(b"MuxOduBip8",b"11",self.globals.veexOtn.odtuStats[muxLevel].oduBip8)
            response += ScpiOtn._getErrorToken(b"MuxOduBei",b"12",self.globals.veexOtn.odtuStats[muxLevel].oduBei)
            response += ScpiOtn._getErrorToken(b"Omfi",b"13",self.globals.veexOtn.stats.omfi)
            response += ScpiOtn._getErrorToken(b"MuxOpuCmCrc8",b"14",self.globals.veexOtn.odtuStats[muxLevel].opuC8Crc8)
        else:
            response += ScpiOtn._getErrorToken(b"MuxFrame",b"9",self.globals.veexOtn.stats.odtuFrame)
            response += ScpiOtn._getErrorToken(b"MuxMfas",b"10",self.globals.veexOtn.stats.odtuMfas)
            response += ScpiOtn._getErrorToken(b"MuxOduBip8",b"11",self.globals.veexOtn.stats.odtuOduBip8)
            response += ScpiOtn._getErrorToken(b"MuxOduBei",b"12",self.globals.veexOtn.stats.odtuOduBei)
            response += ScpiOtn._getErrorToken(b"Omfi",b"13",self.globals.veexOtn.stats.omfi)
            response += ScpiOtn._getErrorToken(b"MuxOpuCmCrc8",b"14",self.globals.veexOtn.stats.odtuOpuC8Crc8)
        response += ScpiOtn._getErrorToken(b"BIT",b"15",self.globals.veexOtn.stats.bit)
        response += ScpiOtn._getErrorToken(b"Lan1027bBlock",b"16",self.globals.veexOtn.stats.block1027b)
        response += ScpiOtn._getErrorToken(b"Lan0OtnBip8",b"17",self.globals.veexOtn.stats.lanOtnBip8[0])
        response += ScpiOtn._getErrorToken(b"Lan1OtnBip8",b"18",self.globals.veexOtn.stats.lanOtnBip8[1])
        response += ScpiOtn._getErrorToken(b"Lan2OtnBip8",b"19",self.globals.veexOtn.stats.lanOtnBip8[2])
        response += ScpiOtn._getErrorToken(b"Lan3OtnBip8",b"20",self.globals.veexOtn.stats.lanOtnBip8[3])
        response += ScpiOtn._getErrorToken(b"Lan0PcsBip8",b"21",self.globals.veexOtn.stats.lanPcsBip8[0])
        response += ScpiOtn._getErrorToken(b"Lan1PcsBip8",b"22",self.globals.veexOtn.stats.lanPcsBip8[1])
        response += ScpiOtn._getErrorToken(b"Lan2PcsBip8",b"23",self.globals.veexOtn.stats.lanPcsBip8[2])
        response += ScpiOtn._getErrorToken(b"Lan3PcsBip8",b"24",self.globals.veexOtn.stats.lanPcsBip8[3])   
        response += ScpiOtn._getErrorToken(b"Tcm1Bip8",b"25",self.globals.veexOtn.stats.tcmBip8[0])
        response += ScpiOtn._getErrorToken(b"Tcm2Bip8",b"26",self.globals.veexOtn.stats.tcmBip8[1])
        response += ScpiOtn._getErrorToken(b"Tcm3Bip8",b"27",self.globals.veexOtn.stats.tcmBip8[2])
        response += ScpiOtn._getErrorToken(b"Tcm4Bip8",b"28",self.globals.veexOtn.stats.tcmBip8[3])
        response += ScpiOtn._getErrorToken(b"Tcm5Bip8",b"29",self.globals.veexOtn.stats.tcmBip8[4])
        response += ScpiOtn._getErrorToken(b"Tcm6Bip8",b"30",self.globals.veexOtn.stats.tcmBip8[5])
        response += ScpiOtn._getErrorToken(b"Tcm1Bei",b"31",self.globals.veexOtn.stats.tcmBei[0])
        response += ScpiOtn._getErrorToken(b"Tcm2Bei",b"32",self.globals.veexOtn.stats.tcmBei[1])
        response += ScpiOtn._getErrorToken(b"Tcm3Bei",b"33",self.globals.veexOtn.stats.tcmBei[2])
        response += ScpiOtn._getErrorToken(b"Tcm4Bei",b"34",self.globals.veexOtn.stats.tcmBei[3])
        response += ScpiOtn._getErrorToken(b"Tcm5Bei",b"35",self.globals.veexOtn.stats.tcmBei[4])
        response += ScpiOtn._getErrorToken(b"Tcm6Bei",b"36",self.globals.veexOtn.stats.tcmBei[5])
        if muxLevel != -1:
            response += ScpiOtn._getErrorToken(b"MuxTcm1Bip8",b"37",self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[0])
            response += ScpiOtn._getErrorToken(b"MuxTcm2Bip8",b"38",self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[1])
            response += ScpiOtn._getErrorToken(b"MuxTcm3Bip8",b"39",self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[2])
            response += ScpiOtn._getErrorToken(b"MuxTcm4Bip8",b"40",self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[3])
            response += ScpiOtn._getErrorToken(b"MuxTcm5Bip8",b"41",self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[4])
            response += ScpiOtn._getErrorToken(b"MuxTcm6Bip8",b"42",self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[5])
            response += ScpiOtn._getErrorToken(b"MuxTcm1Bei",b"43",self.globals.veexOtn.odtuStats[muxLevel].tcmBei[0])
            response += ScpiOtn._getErrorToken(b"MuxTcm2Bei",b"44",self.globals.veexOtn.odtuStats[muxLevel].tcmBei[1])
            response += ScpiOtn._getErrorToken(b"MuxTcm3Bei",b"45",self.globals.veexOtn.odtuStats[muxLevel].tcmBei[2])
            response += ScpiOtn._getErrorToken(b"MuxTcm4Bei",b"46",self.globals.veexOtn.odtuStats[muxLevel].tcmBei[3])
            response += ScpiOtn._getErrorToken(b"MuxTcm5Bei",b"47",self.globals.veexOtn.odtuStats[muxLevel].tcmBei[4])
            response += ScpiOtn._getErrorToken(b"MuxTcm6Bei",b"48",self.globals.veexOtn.odtuStats[muxLevel].tcmBei[5])       
        else:
            response += ScpiOtn._getErrorToken(b"MuxTcm1Bip8",b"37",self.globals.veexOtn.stats.odtuTcmBip8[0])
            response += ScpiOtn._getErrorToken(b"MuxTcm2Bip8",b"38",self.globals.veexOtn.stats.odtuTcmBip8[1])
            response += ScpiOtn._getErrorToken(b"MuxTcm3Bip8",b"39",self.globals.veexOtn.stats.odtuTcmBip8[2])
            response += ScpiOtn._getErrorToken(b"MuxTcm4Bip8",b"40",self.globals.veexOtn.stats.odtuTcmBip8[3])
            response += ScpiOtn._getErrorToken(b"MuxTcm5Bip8",b"41",self.globals.veexOtn.stats.odtuTcmBip8[4])
            response += ScpiOtn._getErrorToken(b"MuxTcm6Bip8",b"42",self.globals.veexOtn.stats.odtuTcmBip8[5])
            response += ScpiOtn._getErrorToken(b"MuxTcm1Bei",b"43",self.globals.veexOtn.stats.odtuTcmBei[0])
            response += ScpiOtn._getErrorToken(b"MuxTcm2Bei",b"44",self.globals.veexOtn.stats.odtuTcmBei[1])
            response += ScpiOtn._getErrorToken(b"MuxTcm3Bei",b"45",self.globals.veexOtn.stats.odtuTcmBei[2])
            response += ScpiOtn._getErrorToken(b"MuxTcm4Bei",b"46",self.globals.veexOtn.stats.odtuTcmBei[3])
            response += ScpiOtn._getErrorToken(b"MuxTcm5Bei",b"47",self.globals.veexOtn.stats.odtuTcmBei[4])
            response += ScpiOtn._getErrorToken(b"MuxTcm6Bei",b"48",self.globals.veexOtn.stats.odtuTcmBei[5])     
        if len(response) == 0:
            response = b"+0"  
        return response

    def tcm1BeiAvgErrRate(self, parameters):
        '''**RES:TCM1:BEI:AVE?** -
        Query the TCM1:BEI average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBei[0].avgRate

    def tcm1BeiErrCount(self, parameters):
        '''**RES:TCM1:BEI:COUNt?** -
        Query the TCM1:BEI error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBei[0].count

    def tcm1BeiErrRate(self, parameters):
        '''**RES:TCM1:BEI:RATe?** -
        Query the TCM1:BEI current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBei[0].currRate

    def tcm1Bip8AvgErrRate(self, parameters):
        '''**RES:TCM1:BIP8:AVE?** -
        Query the TCM1:BIP2 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBip8[0].avgRate

    def tcm1Bip8ErrCount(self, parameters):
        '''**RES:TCM1:BIP8:COUNt?** -
        Query the TCM1:BIP8 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBip8[0].count

    def tcm1Bip8ErrRate(self, parameters):
        '''**RES:TCM1:BIP8:RATe?** -
        Query the TCM1:BIP2 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBip8[0].currRate

    def getResTcm1BdAlrm(self, parameters):
        '''**RES:TCM1BDI:Secs?** -
        Query the number of TCM1:BDI alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBdi[0].secs

    def getResTcm1BiaeAlrm(self, parameters):
        '''**RES:TCM1BIAE:Secs?** -
        Query the number of TCM1:BIAE alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBiae[0].secs

    def getResTcm1DaAlrm(self, parameters):
        '''**RES:TCM1DAPI:Secs?** -
        Query the number of TCM1:DAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmDapiTim[0].secs

    def getResTcm1SaAlrm(self, parameters):
        '''**RES:TCM1SAPI:Secs?** -
        Query the number of TCM1:SAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmSapiTim[0].secs

    def tcm2BeiAvgErrRate(self, parameters):
        '''**RES:TCM2:BEI:AVE?** -
        Query the TCM2:BEI average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBei[1].avgRate

    def tcm2BeiErrCount(self, parameters):
        '''**RES:TCM2:BEI:COUNt?** -
        Query the TCM2:BEI error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBei[1].count

    def tcm2BeiErrRate(self, parameters):
        '''**RES:TCM2:BEI:RATe?** -
        Query the TCM2:BEI current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBei[1].currRate

    def tcm2Bip8AvgErrRate(self, parameters):
        '''**RES:TCM2:BIP8:AVE?** -
        Query the TCM2:BIP8 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBip8[1].avgRate

    def tcm2Bip8ErrCount(self, parameters):
        '''**RES:TCM2:BIP8:COUNt?** -
        Query the TCM2:BIP8 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBip8[1].count

    def tcm2Bip8ErrRate(self, parameters):
        '''**RES:TCM2:BIP8:RATe?** -
        Query the TCM2:BIP8 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBip8[1].currRate

    def getResTcm2BdAlrm(self, parameters):
        '''**RES:TCM2BDI:Secs?** -
        Query the number of TCM2:BDI alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBdi[1].secs

    def getResTcm2BiaeAlrm(self, parameters):
        '''**RES:TCM2BIAE:Secs?** -
        Query the number of TCM2:BIAE alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBiae[1].secs

    def getResTcm2DaAlrm(self, parameters):
        '''**RES:TCM2DAPI:Secs?** -
        Query the number of TCM2:DAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmDapiTim[1].secs

    def getResTcm2SaAlrm(self, parameters):
        '''**RES:TCM2SAPI:Secs?** -
        Query the number of TCM2:SAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmSapiTim[1].secs

    def tcm3BeiAvgErrRate(self, parameters):
        '''**RES:TCM3:BEI:AVE?** -
        Query the TCM3:BEI average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBei[2].avgRate

    def tcm3BeiErrCount(self, parameters):
        '''**RES:TCM3:BEI:COUNt?** -
        Query the TCM3:BEI error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBei[2].count

    def tcm3BeiErrRate(self, parameters):
        '''**RES:TCM3:BEI:RATe?** -
        Query the TCM3:BEI current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBei[2].currRate

    def tcm3Bip8AvgErrRate(self, parameters):
        '''**RES:TCM3:BIP8:AVE?** -
        Query the TCM3:BIP8 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBip8[2].avgRate

    def tcm3Bip8ErrCount(self, parameters):
        '''**RES:TCM3:BIP8:COUNt?** -
        Query the TCM3:BIP8 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBip8[2].count

    def tcm3Bip8ErrRate(self, parameters):
        '''**RES:TCM3:BIP8:RATe?** -
        Query the TCM3:BIP8 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBip8[2].currRate

    def getResTcm3BdAlrm(self, parameters):
        '''**RES:TCM3BDI:Secs?** -
        Query the number of TCM3:BDI alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBdi[2].secs

    def getResTcm3BiaeAlrm(self, parameters):
        '''**RES:TCM3BIAE:Secs?** -
        Query the number of TCM3:BIAE alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBiae[2].secs

    def getResTcm3DaAlrm(self, parameters):
        '''**RES:TCM3DAPI:Secs?** -
        Query the number of TCM3:DAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmDapiTim[2].secs

    def getResTcm3SaAlrm(self, parameters):
        '''**RES:TCM3SAPI:Secs?** -
        Query the number of TCM3:SAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmSapiTim[2].secs

    def tcm4BeiAvgErrRate(self, parameters):
        '''**RES:TCM4:BEI:AVE?** -
        Query the TCM4:BEI average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBei[3].avgRate

    def tcm4BeiErrCount(self, parameters):
        '''**RES:TCM4:BEI:COUNt?** -
        Query the TCM4:BEI error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBei[3].count

    def tcm4BeiErrRate(self, parameters):
        '''**RES:TCM4:BEI:RATe?** -
        Query the TCM4:BEI current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBei[3].currRate

    def tcm4Bip8AvgErrRate(self, parameters):
        '''**RES:TCM4:BIP8:AVE?** -
        Query the TCM4:BIP8 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBip8[3].avgRate

    def tcm4Bip8ErrCount(self, parameters):
        '''**RES:TCM4:BIP8:COUNt?** -
        Query the TCM4:BIP8 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBip8[3].count

    def tcm4Bip8ErrRate(self, parameters):
        '''**RES:TCM4:BIP8:RATe?** -
        Query the TCM4:BIP8 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBip8[3].currRate

    def getResTcm4BdAlrm(self, parameters):
        '''**RES:TCM4BDI:Secs?** -
        Query the number of TCM4:BDI alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBdi[3].secs

    def getResTcm4BiaeAlrm(self, parameters):
        '''**RES:TCM4BIAE:Secs?** -
        Query the number of TCM4:BIAE alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBiae[3].secs

    def getResTcm4DaAlrm(self, parameters):
        '''**RES:TCM4DAPI:Secs?** -
        Query the number of TCM4:DAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmDapiTim[3].secs

    def getResTcm4SaAlrm(self, parameters):
        '''**RES:TCM4SAPI:Secs?** -
        Query the number of TCM4:SAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmSapiTim[3].secs

    def tcm5BeiAvgErrRate(self, parameters):
        '''**RES:TCM5:BEI:AVE?** -
        Query the TCM5:BEI average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBei[4].avgRate

    def tcm5BeiErrCount(self, parameters):
        '''**RES:TCM5:BEI:COUNt?** -
        Query the TCM5:BEI error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBei[4].count

    def tcm5BeiErrRate(self, parameters):
        '''**RES:TCM5:BEI:RATe?** -
        Query the TCM5:BEI current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBei[4].currRate

    def tcm5Bip8AvgErrRate(self, parameters):
        '''**RES:TCM5:BIP8:AVE?** -
        Query the TCM5:BIP8 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBip8[4].avgRate

    def tcm5Bip8ErrCount(self, parameters):
        '''**RES:TCM5:BIP8:COUNt?** -
        Query the TCM5:BIP8 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBip8[4].count

    def tcm5Bip8ErrRate(self, parameters):
        '''**RES:TCM5:BIP8:RATe?** -
        Query the TCM5:BIP8 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBip8[4].currRate

    def getResTcm5BdAlrm(self, parameters):
        '''**RES:TCM5BDI:Secs?** -
        Query the number of TCM5:BDI alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBdi[4].secs

    def getResTcm5BiaeAlrm(self, parameters):
        '''**RES:TCM5BIAE:Secs?** -
        Query the number of TCM5:BIAE alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBiae[4].secs

    def getResTcm5DaAlrm(self, parameters):
        '''**RES:TCM5DAPI:Secs?** -
        Query the number of TCM5:DAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmDapiTim[4].secs

    def getResTcm5SaAlrm(self, parameters):
        '''**RES:TCM5SAPI:Secs?** -
        Query the number of TCM5:SAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmSapiTim[4].secs

    def tcm6BeiAvgErrRate(self, parameters):
        '''**RES:TCM6:BEI:AVE?** -
        Query the TCM6:BEI average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBei[5].avgRate

    def tcm6BeiErrCount(self, parameters):
        '''**RES:TCM6:BEI:COUNt?** -
        Query the TCM6:BEI error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBei[5].count

    def tcm6BeiErrRate(self, parameters):
        '''**RES:TCM6:BEI:RATe?** -
        Query the TCM6:BEI current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBei[5].currRate

    def tcm6Bip8AvgErrRate(self, parameters):
        '''**RES:TCM6:BIP8:AVE?** -
        Query the TCM6:BIP8 average error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBip8[5].avgRate

    def tcm6Bip8ErrCount(self, parameters):
        '''**RES:TCM6:BIP8:COUNt?** -
        Query the TCM6:BIP8 error count.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBip8[5].count

    def tcm6Bip8ErrRate(self, parameters):
        '''**RES:TCM6:BIP8:RATe?** -
        Query the TCM6:BIP8 current error rate.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.2e" % self.globals.veexOtn.stats.tcmBip8[5].currRate

    def getResTcm6BdAlrm(self, parameters):
        '''**RES:TCM6BDI:Secs?** -
        Query the number of TCM6:BDI alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBdi[5].secs

    def getResTcm6BiaeAlrm(self, parameters):
        '''**RES:TCM6BIAE:Secs?** -
        Query the number of TCM6:BIAE alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmBiae[5].secs

    def getResTcm6DaAlrm(self, parameters):
        '''**RES:TCM6DAPI:Secs?** -
        Query the number of TCM6:DAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmDapiTim[5].secs

    def getResTcm6SaAlrm(self, parameters):
        '''**RES:TCM6SAPI:Secs?** -
        Query the number of TCM6:SAPI TIM alarm seconds.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.tcmSapiTim[5].secs

    def getResTxC8Plus1(self, parameters):
        '''**RES:TXCMJUST:PLUS1?** -
        Query the number of GMP Cm frames transmitted for the specific Cm justification criteria.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.txGmpC8Plus1.count

    def getResTxC8Plus2(self, parameters):
        '''**RES:TXCMJUST:PLUS2?** -
        Query the number of GMP Cm frames transmitted for the specific Cm justification criteria.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.txGmpC8Plus2.count

    def getResTxC8Minus1(self, parameters):
        '''**RES:TXCMJUST:MINUS1?** -
        Query the number of GMP Cm frames transmitted for the specific Cm justification criteria.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.txGmpC8Minus1.count  

    def getResTxC8Minus2(self, parameters):
        '''**RES:TXCMJUST:MINUS2?** -
        Query the number of GMP Cm frames transmitted for the specific Cm justification criteria.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.txGmpC8Minus2.count

    def getResTxC8Gtr2(self, parameters):
        '''**RES:TXCMJUST:GTR2?** -
        Query the number of GMP Cm frames transmitted for the specific Cm justification criteria.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.txGmpC8Gtr2.count

    def getResTxC8Lt2(self, parameters):
        '''**RES:TXCMJUST:LT2?** -
        Query the number of GMP Cm frames transmitted for the specific Cm justification criteria.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.txGmpC8Lt2.count

    def getTxC8Max(self, parameters):
        '''**RES:TXCMMAX?** -
        Query the Maximum GMP Cm justification value transmitted during the current test.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.txGmpC8Largest

    def getTxC8Min(self, parameters):
        '''**RES:TXCMMIN?** -
        Query the Minimum GMP Cm justification value transmitted during the current test.
        '''
        self.globals.veexOtn.stats.update()
        return b"%d" % self.globals.veexOtn.stats.txGmpC8Smallest

    def getSDState(self, parameters):
        '''**SD:ACTION?** -
        Query the current status of the SD test.
        '''
        self.globals.veexOtn.stats.update()
        if self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_SDT_ST_STOPPED:
            return b"INACTIVE"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_SDT_ST_ARMED:
            return b"ARMED SINGLE"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_SDT_ST_RUNNING:
            return b"MEASURING SINGLE"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_SDT_ST_CONT_ARM:
            return b"ARMED CONTINUOUS"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_SDT_ST_CONT_RUN:
            return b"MEASURING CONTINUOUS"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_STOPPED:
            return b"INACTIVE"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_ARMED:
            return b"ARMED SINGLE RTD"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_RUNNING:
            return b"MEASURING SINGLE RTD"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_CONT_ARM:
            return b"ARMED CONTINUOUS RTD"
        elif self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_CONT_RUN:
            return b"MEASURING CONTINUOUS RTD"
        else:
            return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)

    def setSDAction(self, parameters):
        '''**SD:ACTION:<CONTinuos|SINGle|STOP>** -
        Starts and stops SD mode.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            self.globals.veexOtn.stats.update()
            if (self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_ARMED) or \
               (self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_RUNNING) or \
               (self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_CONT_ARM) or \
               (self.globals.veexOtn.stats.sdtSwitchState == veexlib.OTN_RTD_CONT_RUN):
                response = self._errorResponse(ScpiErrorCode.CMD_INVALID_FOR_CRNT_CONFIG)
            if paramList[0].head.upper().startswith(b"STOP"):
                self.globals.veexOtn.sets.armSdtSwitch(veexlib.OTN_SDT_RTD_STOP)
            elif paramList[0].head.upper().startswith(b"SING"):
                self.globals.veexOtn.sets.armSdtSwitch(veexlib.OTN_SDT_ARM_SINGLE)
            elif paramList[0].head.upper().startswith(b"CONT"):
                self.globals.veexOtn.sets.armSdtSwitch(veexlib.OTN_SDT_ARM_CONTINUOUS)
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getSDAvgFrame(self, parameters):
        '''**SD:AVGFRAME?** -
        Queries the calculated Average frame length for each SD event,
        based on total number of events since the test was started.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.1f" % (self.globals.veexOtn.stats.avgSdtSwitchTime * 1.00,)

    def getSDAvgTime(self, parameters):
        '''**SD:AVGTIME?** -
        Queries the calculated Average time measurement for each SD event,
        based on total number of events since the test was started.
        '''
        self.globals.veexOtn.stats.update()
        time = float(self.globals.veexOtn.stats.avgSdtSwitchTime) / self.globals.veexOtn.stats.sdtSwitchFrameRate
        return b"%.3f ms" % (time * 1000.0,)

    def getApsDetail(self, parameters):
        '''**SD:CHANnel?** -
        Queries which of the ODU-n channel numbers is selected for the Service Disruption test,
        when configured for an ODTU Multi-Channel payload structure.
        '''
        self.globals.veexOtn.sets.update()
        return b"%d" % (self.globals.veexOtn.sets.sdtDrop + 1,)

    def setApsDetail(self, parameters):
        '''**SD:CHANnel <channel>** -
        When the OTN is configured for an ODTU Multi-Channel mapping and the SD ODTU Level is configured for the lowest ODU A/D level,
        this command selects which ODU-n channel is to be configured for the Service Disruption test.
        '''
        self.globals.veexOtn.sets.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if value < 0:
                response = self._errorResponse(ScpiErrorCode.DATA_TYPE_ERR)
            else:
                sdtDropHigh = self.globals.veexOtn.sets.sdtDrop
                if (value < 1) or (value > sdtDropHigh) or \
                   (self.globals.veexOtn.sets.rxMultiChanPattern[value-1] == veexlib.OTN_PATTERN_BACKGROUND):
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                else:
                    self.globals.veexOtn.sets.sdtDrop = value - 1
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getSDCriteria(self, parameters):
        '''**SD:CRITeria?** -
        Queries the Protection Switch Criteria selected.
        '''
        self.globals.veexOtn.sets.update()
        member = self.globals.veexOtn.sets.sdtDrop
        response = b""
        if self.globals.veexOtn.sets.sdtCriteriaMask[member] == 0:
            response = b"NONE"
        else:
            if (self.globals.veexOtn.sets.sdtCriteriaMask[member] & veexlib.OTN_SDT_ST_TRIG_OOF_MASK) != 0:
                response += b"OOF,"
            if (self.globals.veexOtn.sets.sdtCriteriaMask[member] & veexlib.OTN_SDT_ST_TRIG_OTU_AIS_MASK) != 0:
                response += b"OTUAIS,"
            if (self.globals.veexOtn.sets.sdtCriteriaMask[member] & veexlib.OTN_SDT_ST_TRIG_OTU_BIP8_MASK) != 0:
                response += b"OTUBIP8,"
            if (self.globals.veexOtn.sets.sdtCriteriaMask[member] & veexlib.OTN_SDT_ST_TRIG_ODU_AIS_MASK) != 0:
                response += b"ODUAIS,"
            if (self.globals.veexOtn.sets.sdtCriteriaMask[member] & veexlib.OTN_SDT_ST_TRIG_ODU_BIP8_MASK) != 0:
                response += b"ODUBIP8,"
            if (self.globals.veexOtn.sets.sdtCriteriaMask[member] & veexlib.OTN_SDT_ST_TRIG_BIT_MASK) != 0:
                response += b"BIT,"
            if len(response) < 1:
                response = self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
        return response

    def setSDCriteria(self, parameters):
        '''**SD:CRITeria:<criteria>** -
        Sets the Protection Switch Criteria used to trigger the SD measurements.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        mask = 0
        if len(paramList) >= 1:
            self.globals.veexOtn.sets.update()
            for i in range(len(paramList)):
                if paramList[i].head.upper().startswith(b"BIT"):
                    mask |= veexlib.OTN_SDT_ST_TRIG_BIT_MASK
                elif paramList[i].head.upper().startswith(b"OOF"):
                    mask |= veexlib.OTN_SDT_ST_TRIG_OOF_MASK
                elif paramList[i].head.upper().startswith(b"OTUAIS"):
                    mask |= veexlib.OTN_SDT_ST_TRIG_OTU_AIS_MASK
                elif paramList[i].head.upper().startswith(b"OTUBIP8"):
                    mask |= veexlib.OTN_SDT_ST_TRIG_OTU_BIP8_MASK
                elif paramList[i].head.upper().startswith(b"ODUAIS"):
                    mask |= veexlib.OTN_SDT_ST_TRIG_ODU_AIS_MASK
                elif paramList[i].head.upper().startswith(b"ODUBIP8"):
                    mask |= veexlib.OTN_SDT_ST_TRIG_ODU_BIP8_MASK
            if mask != 0:
                self.globals.veexOtn.sets.sdtCriteriaMask = mask
            else:
                response = self._errorResponse(ScpiErrorCode.INVALID_SETTINGS)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getSDCurFrame(self, parameters):
        '''**SD:CURFRAME?** -
        Queries the most Current SD frame measurement recorded.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.1f frames" % (self.globals.veexOtn.stats.sdtSwitchTime * 1.00,)

    def getSDCurTime(self, parameters):
        '''**SD:CURTIME?** -
        Queries the most Current SD time measurement recorded.
        '''
        self.globals.veexOtn.stats.update()
        time = float(self.globals.veexOtn.stats.sdtSwitchTime) / self.globals.veexOtn.stats.sdtSwitchFrameRate
        return b"%.3f ms" % (time * 1000.0,)

    def getSDGoodFrame(self, parameters):
        '''**SD:GOODFRAME?** -
        Queries the Consecutive Good Frames Required value for the SD function.
        '''
        self.globals.veexOtn.sets.update()
        member = self.globals.veexOtn.sets.sdtDrop
        return b"%.1f frames" % (self.globals.veexOtn.sets.sdtSwitchStopCount[member] * 1.0,)

    def setSDGoodFrame(self, parameters):
        '''**SD:GOODFRAME:<value>** -
        Sets a value, in frames, for the Consecutive Good Frames Required setting (error-free frames)
        that must elapse before any accumulating SD measurements will stop, for each event.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            value = ParseUtils.checkNumeric(paramList[0].head)
            if (value >= 1) and (value <= 16383):
                self.globals.veexOtn.sets.update()
                if (value > self.globals.veexOtn.sets.sdtDrop) or (self.globals.veexOtn.sets.rxMultiChanPattern == veexlib.OTN_PATTERN_BACKGROUND):
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                else:
                    self.globals.veexOtn.sets.sdtSwitchStopCount = value
            else:
                response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getSDGoodTime(self, parameters):
        '''**SD:GOODTIME?** -
        Queries the Consecutive Good Time Required value for the SD function.
        '''
        self.globals.veexOtn.sets.update()
        self.globals.veexOtn.stats.update()
        member = self.globals.veexOtn.sets.sdtDrop
        time = float(self.globals.veexOtn.sets.sdtSwitchStopCount[member]) / self.globals.veexOtn.stats.sdtSwitchFrameRate
        return b"%.3f ms" % (time * 1000.0,)

    def setSDGoodTime(self, parameters):
        '''**SD:GOODTIME:<value>** -
        Sets a value, in milliseconds, for the Consecutive Good Time Required setting (error-free time)
        that must elapse before the accumulating SD measurements will stop, for each event.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 1:
            if ParseUtils.isFloatSdh(paramList[0].head):
                self.globals.veexOtn.stats.update()
                fVal = float(paramList[0].head)
                if (fVal < (1000.0 / self.globals.veexOtn.stats.sdtSwitchFrameRate)) or \
                   (fVal > (16384 * 1000.0 / self.globals.veexOtn.stats.sdtSwitchFrameRate)):
                    response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                else:
                    iVal = int(fVal * self.globals.veexOtn.stats.sdtSwitchFrameRate / 1000.0)
                    self.globals.veexOtn.sets.sdtSwitchStopCount = iVal
            else:
                response = self._errorResponse(ScpiErrorCode.ILLEGAL_PARAM_VALUE)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response

    def getSDMaxFrame(self, parameters):
        '''**SD:MAXFRAME?** -
        Queries the Maximum frame measurement, out of the total number of SD events since the test was started.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.1f frames" % (self.globals.veexOtn.stats.maxSdtSwitchTime * 1.0,)

    def getSDMaxTime(self, parameters):
        '''**SD:MAXTIME?** -
        Queries the Maximum time measurement, out of the total number of SD events since the test was started.
        '''
        self.globals.veexOtn.stats.update()
        time = float(self.globals.veexOtn.stats.maxSdtSwitchTime) / self.globals.veexOtn.stats.sdtSwitchFrameRate
        return b"%0.3f seconds" % (time * 1000.0,)

    def getSDMinFrame(self, parameters):
        '''**SD:MINFRAME?** -
        Queries the Minimum frame measurement, out of the total number of SD events since the test was started.
        '''
        self.globals.veexOtn.stats.update()
        return b"%.1f frames" % (self.globals.veexOtn.stats.minSdtSwitchTime * 1.0,)

    def getSDMinTime(self, parameters):
        '''**SD:MINTIME?** -
        Queries the Minimum time measurement, out of the total number of SD events since the test was started.
        '''
        self.globals.veexOtn.stats.update()
        time = float(self.globals.veexOtn.stats.minSdtSwitchTime) / self.globals.veexOtn.stats.sdtSwitchFrameRate
        return b"%0.3f seconds" % (time * 1000.0,)

    def getSDRecentFrame(self, parameters):
        '''**SD:RECFRAME?** -
        Queries the ten most Recent SD frame measurements recorded.
        '''
        self.globals.veexOtn.stats.update()
        response = b""
        for i in range(10):
            response += b"%d frames, " % self.globals.veexOtn.stats.recentSdtSwitchTimes[i]
        return response

    def getSDRecentTime(self, parameters):
        '''**SD:RECTIME?** -
        Queries the ten most Recent SD time measurements recorded.
        '''
        self.globals.veexOtn.stats.update()
        response = b""
        for i in range(10):
            time = float(self.globals.veexOtn.stats.recentSdtSwitchTimes[i]) / self.globals.veexOtn.stats.sdtSwitchFrameRate
            response += b"%0.3f ms, " % (time * 1000.0,)
        return response

    def doModuleSfpRead(self, parameters):
        '''**MODULE:READ? <address> <page> (optional)** -
        Reads the SFP's 2-wire (I2C) interface for "upper page" serial address specified in the SFF-8472 Reference.
        '''
        self.globals.veexOtn.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        if len(paramList) >= 1:
            i2cAddress = ParseUtils.checkNumeric(paramList[0].head)
            if len(paramList) == 1:
                i2cPage = 0
            else:
                i2cPage = ParseUtils.checkNumeric(paramList[1].head)
            if (i2cAddress < 0) or (i2cAddress > 255) or (i2cPage < 0) or (i2cPage > 4):
                response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
            elif i2cPage == 0:
                data = self.globals.veexOtn.readSfpIdRegister(i2cAddress)
                if data < 0:
                    response = self._errorResponse(ScpiErrorCode.GENERIC_QUERY_ERR) 
                else:
                    response = b"%02Xh" % data
            else:
                data = self.globals.veexOtn.readSfpDiagRegister(i2cAddress)
                if data < 0:
                    response = self._errorResponse(ScpiErrorCode.GENERIC_QUERY_ERR) 
                else:
                    response = b"%02Xh" % data       
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response
            
    def doModuleSfpWrite(self, parameters):
        '''**MODULE:WRITE <value> <address> <page> (optional)** -
        Writes a user-specified byte value (in hex) to the specified address and option page number.
        '''
        self.globals.veexOtn.update()
        paramList = ParseUtils.preParseParameters(parameters)
        response = None
        if len(paramList) >= 2:
            i2cData = ParseUtils.checkNumeric(paramList[0].head)
            i2cAddress = ParseUtils.checkNumeric(paramList[1].head)
            if len(paramList) == 2:
                i2cPage = 0
            else:
                i2cPage = ParseUtils.checkNumeric(paramList[2].head)
            if (i2cData < 0) or (i2cData > 255) or \
               (i2cAddress < 0) or (i2cAddress > 255) or \
               (i2cPage < 0) or (i2cPage > 4):
                response = self._errorResponse(ScpiErrorCode.NUMERIC_DATA_ERR)
            elif i2cPage == 0:
                if self.globals.veexOtn.writeSfpIdRegister(i2cData,i2cAddress) == False:
                    response = self._errorResponse(ScpiErrorCode.GENERIC_QUERY_ERR)
            else:
                if self.globals.veexOtn.writeSfpDiagRegister(i2cData,i2cAddress) == False:
                    response = self._errorResponse(ScpiErrorCode.GENERIC_QUERY_ERR)
        else:
            response = self._errorResponse(ScpiErrorCode.MISSING_PARAM)
        return response   

    def getModuleSfpInfoConnectorType(self, parameters):
        '''**MODULE:INFO:CONNECTORTYPE?** -
        Queries the SFP module's Connector Type.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            if self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x00:
                response = b"Undefined"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x01:
                response = b"SC"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x02:
                response = b"FibreChan 1"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x03:
                response = b"FibreChan 2"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x04:
                response = b"BNC/TNC"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x05:
                response = b"FibreChan coax"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x06:
                response = b"Fiber Jack"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x07:
                response = b"LC"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x08:
                response = b"MT-RJ"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x09:
                response = b"MU"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x0A:
                response = b"SG"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x0B:
                response = b"Optical Pigtail"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x0C:
                response = b"MPO 1x12"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x0D:
                response = b"MPO 2x16"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x20:
                response = b"HSSDC II"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x21:
                response = b"Copper Pigtail"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x22:
                response = b"RJ45"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x23:
                response = b"No Connector"
            elif self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x24:
                response = b"MXC 2x16"
            else:
                response = b"Reserved"
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 
     
    def getModuleSfpInfoDateCode(self, parameters):
        '''**MODULE:INFO:DATECODE?** -
        Queries the SFP module's vendor (manufacturer) date in the format YYMMDD.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            response += b"%s" % self.globals.veexOtn.stats.sfpI2cInfo.dateCode
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response      
    
    def getModuleSfpInfoEncoding(self, parameters):
        '''**MODULE:INFO:ENCODING?** -
        Queries the SFP module's high-speed serial encoding algorithm value..
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            if self.globals.veexOtn.stats.sfpI2cInfo.encoding == 0x00:
                response = b"Unspecified"
            elif self.globals.veexOtn.stats.sfpI2cInfo.encoding == 0x01:
                response = b"8B/10B"
            elif self.globals.veexOtn.stats.sfpI2cInfo.encoding == 0x02:
                response = b"4B/5B"
            elif self.globals.veexOtn.stats.sfpI2cInfo.encoding == 0x03:
                response = b"NRZ"
            elif self.globals.veexOtn.stats.sfpI2cInfo.encoding == 0x04:
                response = b"SONET Scrambled"
            elif self.globals.veexOtn.stats.sfpI2cInfo.encoding == 0x05:
                response = b"64B/66B"
            elif self.globals.veexOtn.stats.sfpI2cInfo.encoding == 0x06:
                response = b"Manchester"
            elif self.globals.veexOtn.stats.sfpI2cInfo.encoding == 0x07:
                response = b"256B/257B"
            elif self.globals.veexOtn.stats.sfpI2cInfo.encoding == 0x08:
                response = b"PAM4"
            else:
                response = b"Reserved"
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response   
            
    def getModuleSfpInfoModuleId(self, parameters):
        '''**MODULE:INFO:ID?** -
        Queries the SFP module's form-factor Identifier code.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            if self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x00:
                response = b"Unspecified"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x01:
                response = b"GBIC"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x02:
                response = b"Soldered"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x03:
                response = b"SFP/SFP+"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x04:
                response = b"300 pin VSBI"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x05:
                response = b"XENPAK"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x06:
                response = b"XFP"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x07:
                response = b"XFF"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x08:
                response = b"XFP-E"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x09:
                response = b"XPAK"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x0A:
                response = b"X2"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x0B:
                response = b"DWDM-SFP"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x0C:
                response = b"QSFP"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x0D:
                response = b"QSFP+"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x0E:
                response = b"CXP"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x0F:
                response = b"Shielded 4x"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x10:
                response = b"Shielded 8x"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x11:
                response = b"QSFP28"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x12:
                response = b"CFP2"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x13:
                response = b"CDFP(1/2)"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x14:
                response = b"Shielded 4x Fanout"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x15:
                response = b"Shielded 8x Fanout"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x16:
                response = b"CDFP(3)"
            elif self.globals.veexOtn.stats.sfpI2cInfo.moduleId == 0x17:
                response = b"microQSFP"
            else:
                response = b"Reserved"
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response

    def getModuleSfpInfoLength50um(self, parameters):
        '''**MODULE:INFO:LENGTH50UM?** -
        Queries the SFP module's link length (50um, OM2) in units of 10 meters.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            if self.globals.veexOtn.stats.sfpI2cInfo.lengthOM2 == 0xFF:
                response = b"> 2540m OM2 fiber"
            elif self.globals.veexOtn.stats.sfpI2cInfo.lengthOM2 == 0x00:
                response = b"N/A"
            else:
                response = b"%dm OM2 fiber" % (self.globals.veexOtn.stats.sfpI2cInfo.lengthOM2 * 10,)
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response
    
    def getModuleSfpInfoLength62_5um(self, parameters):
        '''**MODULE:INFO:LENGTH62_5UM?** -
        Queries the SFP module's link length (62.5um, OM1) in units of 10 meters.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            if self.globals.veexOtn.stats.sfpI2cInfo.lengthOM1 == 0xFF:
                response = b"> 2540m OM1 fiber"
            elif self.globals.veexOtn.stats.sfpI2cInfo.lengthOM1 == 0x00:
                response = b"N/A"
            else:
                response = b"%dm OM1 fiber" % (self.globals.veexOtn.stats.sfpI2cInfo.lengthOM1 * 10,)
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 

    def getModuleSfpInfoLengthOm3(self, parameters):
        '''**MODULE:INFO:LENGTHOM3?** -
        Queries the SFP module's link length (50um, OM3) in units of 10 meters.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            if self.globals.veexOtn.stats.sfpI2cInfo.lengthOM3 == 0xFF:
                response = b"> 2540m OM3 fiber"
            elif self.globals.veexOtn.stats.sfpI2cInfo.lengthOM3 == 0x00:
                response = b"N/A"
            else:
                response = b"%dm OM3 fiber" % (self.globals.veexOtn.stats.sfpI2cInfo.lengthOM3 * 10,)
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 
    
    def getModuleSfpInfoLengthOm4(self, parameters):
        '''**MODULE:INFO:LENGTHOM4?** -
        Queries the SFP module's link length (50um, OM4) in units of 10 meters.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            isRJ45 = False
            if self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x22:
                isRJ45 = True
            elif (self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x00) and \
                 ((self.globals.veexOtn.stats.sfpI2cInfo.transceiverCodes[3] & 0x08) != 0):
                isRJ45 = True
            if isRJ45 == False:
                if self.globals.veexOtn.stats.sfpI2cInfo.lengthOM4 == 0xFF:
                    response = b"> 2540m OM4 fiber"
                elif self.globals.veexOtn.stats.sfpI2cInfo.lengthOM4 == 0x00:
                    response = b"N/A"
                else:
                    response = b"%dm OM4 fiber" % (self.globals.veexOtn.stats.sfpI2cInfo.lengthOM4 * 10,)
            else:
                if self.globals.veexOtn.stats.sfpI2cInfo.lengthOM4 == 0xFF:
                    response = b"> 2540m copper"
                elif self.globals.veexOtn.stats.sfpI2cInfo.lengthOM4 == 0x00:
                    response = b"N/A"
                else:
                    response = b"%dm copper" % (self.globals.veexOtn.stats.sfpI2cInfo.lengthOM4 * 10,)
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 

    def getModuleSfpInfoLengthSmf(self, parameters):
        '''**MODULE:INFO:LENGTHSMF?** -
        Queries the SFP module's link length (single mode) in units of 100 meters.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            if self.globals.veexOtn.stats.sfpI2cInfo.lengthSMF2 == 0xFF:
                response = b"> 25.4km single mode fiber"
            elif self.globals.veexOtn.stats.sfpI2cInfo.lengthSMF2 == 0x00:
                response = b"N/A"
            else:
                response = b"%dm single mode fiber" % (self.globals.veexOtn.stats.sfpI2cInfo.lengthSMF2 * 100,)
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 
    
    def getModuleSfpInfoLengthSmfKm(self, parameters):
        '''**MODULE:INFO:LENGTHSMFKM?** -
        Queries the SFP module's link length (single mode) in kilometers.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            if self.globals.veexOtn.stats.sfpI2cInfo.lengthSMF1 == 0xFF:
                response = b"> 254km single mode fiber"
            elif self.globals.veexOtn.stats.sfpI2cInfo.lengthSMF1 == 0x00:
                response = b"N/A"
            else:
                response = b"%dkm single mode fiber" % self.globals.veexOtn.stats.sfpI2cInfo.lengthSMF1
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 

    def getModuleSfpInfoNominalRate(self, parameters):
        '''**MODULE:INFO:NOMRATE?** -
        Queries the SFP module's Nominal bit rate in units of 100 MBd.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            if self.globals.veexOtn.stats.sfpI2cInfo.brNominal == 0xFF:
                response = b"%dMBd +/-%d%%" % (self.globals.veexOtn.stats.sfpI2cInfo.brMax * 250, self.globals.veexOtn.stats.sfpI2cInfo.brMin,)
            else:
                response = b"%dMBd +%d%%/-%d%%" % (self.globals.veexOtn.stats.sfpI2cInfo.brNominal * 100, self.globals.veexOtn.stats.sfpI2cInfo.brMax, self.globals.veexOtn.stats.sfpI2cInfo.brMin,)
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 
    
    def getModuleSfpInfoPartNumber(self, parameters):
        '''**MODULE:INFO:PARTNUMBER?** -
        Queries the SFP module's Vendor Part Number in ASCII.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            response += b"%s" % self.globals.veexOtn.stats.sfpI2cInfo.vendorPartNum
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 

    def getModuleSfpInfoPower(self, parameters):
        '''**MODULE:INFO:POWERCLASS?** -
        Queries the SFP module's Power Level Declaration.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            if (self.globals.veexOtn.stats.sfpI2cInfo.options0 & 0x22) == 0x22:
                response = b"Power Level 3"
            elif (self.globals.veexOtn.stats.sfpI2cInfo.options0 & 0x22) == 0x02:
                response = b"Power Level 2"
            else:
                response = b"Power Level 1"
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 
    
    def getModuleSfpInfoModulePresent(self, parameters):
        '''**MODULE:INFO:PRESENT?** -
        Queries the SFP module is currently plugged in.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 0:
            response = b"NO"
        else:
            response = b"YES"
        return response 

    def getModuleSfpInfoRateIdentifier(self, parameters):
        '''**MODULE:INFO:RATEIDENTIFIER?** -
        Queries the SFP module's rate identifier.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            if self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x00:
                response = b"Unspecified"
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x01:
                response = b"SFF-8079"
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x02:
                response = b"SFF-8431"
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x03:
                response = b"Unspecified *"
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x04:
                response = b"SFF-8431"
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x05:
                response = b"Unspecified *"
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x06:
                response = b"SFF-8431"
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x07:
                response = b"Unspecified *"
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x08:
                response = b"FC-PI-5"
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x09:
                response = b"Unspecified *"
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x0A:
                response = b"FC-PI-5" 
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x0B:
                response = b"Unspecified *"
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x0C:
                response = b"FC-PI-6" 
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x0D:
                response = b"Unspecified *"
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x0E:
                response = b"10/8G" 
            elif self.globals.veexOtn.stats.sfpI2cInfo.rateIdentifier == 0x0F:
                response = b"Unspecified *"
            else:
                response = b"Unallocated"
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 

    def getModuleSfpInfoRxPower(self, parameters):
        '''**MODULE:INFO:RXPOWER?** -
        Queries the SFP module's Max and Min RX Power Alarm values in dBm.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            isRJ45 = False
            if self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x22:
                isRJ45 = True
            elif (self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x00) and \
                 ((self.globals.veexOtn.stats.sfpI2cInfo.transceiverCodes[3] & 0x08) != 0):
                isRJ45 = True
                
            if (self.globals.veexOtn.stats.sfpI2cInfo.rxPowerHighAlarm == 0) or (isRJ45 == True):
                csRxPowerHighAlarm = b"N/A"
            else:
                csRxPowerHighAlarm = b"%.2f" % (self.globals.veexOtn.stats.sfpI2cInfo.rxPowerHighAlarm / 100.0,)
            if (self.globals.veexOtn.stats.sfpI2cInfo.rxPowerLowAlarm == 0) or (isRJ45 == True):
                csRxPowerLowAlarm = b"N/A"
            else:
                csRxPowerLowAlarm = b"%.2f" % (self.globals.veexOtn.stats.sfpI2cInfo.rxPowerLowAlarm / 100.0,)
            response = b"Max %sdBm, Min %sdBm" % (csRxPowerHighAlarm,csRxPowerLowAlarm,)
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 

    def getModuleSfpInfoSerialNumber(self, parameters):
        '''**MODULE:INFO:SERIALNUMBER?** -
        Queries the SFP module's Vendor Serial Number in ASCII.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            response += b"%s" % self.globals.veexOtn.stats.sfpI2cInfo.vendorSerialNum
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 

    def getModuleSfpInfoTxPower(self, parameters):
        '''**MODULE:INFO:TXPOWER?** -
        Queries the SFP module's Max and Min TX Power Alarm values in dBm.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            isRJ45 = False
            if self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x22:
                isRJ45 = True
            elif (self.globals.veexOtn.stats.sfpI2cInfo.connectorType == 0x00) and \
                 ((self.globals.veexOtn.stats.sfpI2cInfo.transceiverCodes[3] & 0x08) != 0):
                isRJ45 = True
                
            if (self.globals.veexOtn.stats.sfpI2cInfo.txPowerHighAlarm == 0) or (isRJ45 == True):
                csTxPowerHighAlarm = b"N/A"
            else:
                csTxPowerHighAlarm = b"%.2f" % (self.globals.veexOtn.stats.sfpI2cInfo.txPowerHighAlarm / 100.0,)
            if (self.globals.veexOtn.stats.sfpI2cInfo.txPowerLowAlarm == 0) or (isRJ45 == True):
                csTxPowerLowAlarm = b"N/A"
            else:
                csTxPowerLowAlarm = b"%.2f" % (self.globals.veexOtn.stats.sfpI2cInfo.txPowerLowAlarm / 100.0,)
            response = b"Max %sdBm, Min %sdBm" % (csTxPowerHighAlarm,csTxPowerLowAlarm,)
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 

    def getModuleSfpInfoVendorName(self, parameters):
        '''**MODULE:INFO:VENDORNAME?** -
        Queries the SFP module's Vendor (manufacturer) Name in ASCII.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            response += b"%s" % self.globals.veexOtn.stats.sfpI2cInfo.vendorName
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 

    def getModuleSfpInfoVendorOui(self, parameters):
        '''**MODULE:INFO:VENDOROUI?** -
        Queries the SFP module's Vendor OUI.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            response += b"%06Xh" % ((self.globals.veexOtn.stats.sfpI2cInfo.vendorOui[0] << 16)+ \
                                    (self.globals.veexOtn.stats.sfpI2cInfo.vendorOui[1] << 8)+  \
                                    self.globals.veexOtn.stats.sfpI2cInfo.vendorOui[2])
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 

    def getModuleSfpInfoVendorRev(self, parameters):
        '''**MODULE:INFO:VENDORREV?** -
        Queries the SFP module's Vendor Revision in ASCII.
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            response += b"%s" % self.globals.veexOtn.stats.sfpI2cInfo.vendorRev
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 

    def getModuleSfpInfoWavelength(self, parameters):
        '''**MODULE:INFO:WAVELENGTH?** -
        Queries the SFP module's Nominal laser wavelength in nm or copper cable attenuation in dB
        '''  
        self.globals.veexOtn.stats.update()
        response = b""
        if self.globals.veexOtn.stats.sfpI2cInfo.modulePresent == 1:
            if self.globals.veexOtn.stats.sfpI2cInfo.wavelength == 0:
                response = b"Undefined"
            else:
                response = b"%dnm" % self.globals.veexOtn.stats.sfpI2cInfo.wavelength
        else:
            response = self._errorResponse(ScpiErrorCode.HARDWARE_MISSING)  
        return response 
    
    def _getMuxLevel(self,parameters):
        '''Get current Multi-Level.
        '''
        paramList = ParseUtils.preParseParameters(parameters)
        response = b""
        muxLevel = -1
        if len(paramList) >= 1:
            muxLevel = ParseUtils.checkNumeric(paramList[0].head)
            if muxLevel > veexlib.OTN_ODTU_LEVEL_ODU_3  or muxLevel < 0:
                response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                muxLevel = -1
                return (muxLevel, response)
        if muxLevel == -1:
            self.globals.veexOtn.stats.update()
            muxLevel = self.globals.veexOtn.stats.odtuStatsLevel
            if muxLevel > veexlib.OTN_ODTU_LEVEL_ODU_3:
                response = self._errorResponse(ScpiErrorCode.DATA_OUT_OF_RANGE)
                muxLevel = -1
                return (muxLevel, response)
        return (muxLevel, response)
    
    def getResMuxLofLed(self, parameters):
        '''**RES:AL:MUXLOF? <level>** -
        Reports the ODU-n LOF LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].lof.led.isRed else b"OFF"
        return response
    
    def getResMuxLomLed(self, parameters):
        '''**RES:AL:MUXLOM? <level>** -
        Reports the Add/Drop OTU LOM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].lom.led.isRed else b"OFF"
        return response
    
    def getResMuxOduAisLed(self, parameters):
        '''**RES:AL:MUXODUAIS? <level>** -
        Reports the Add/Drop ODU LOM AIS state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].oduAis.led.isRed else b"OFF"
        return response
    
    def getResMuxOduBdiLed(self, parameters):
        '''**RES:AL:MUXODUBDI? <level>** -
        Reports the Add/Drop ODU BDI LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].oduBdi.led.isRed else b"OFF"
        return response
    
    def getResMuxOduDapLed(self, parameters):
        '''**RES:AL:MUXODUDAPITIM? <level>** -
        Reports the Add/Drop ODU DAPI TIM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].oduDapiTim.led.isRed else b"OFF"
        return response
    
    def getResMuxOduLckLed(self, parameters):
        '''**RES:AL:MUXODULCK? <level>** -
        Reports the Add/Drop ODU LCK LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].oduLck.led.isRed else b"OFF"
        return response
    
    def getResMuxOduOciLed(self, parameters):
        '''**RES:AL:MUXODUOCI? <level>** -
        Reports the Add/Drop ODU OCI LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].oduOci.led.isRed else b"OFF"
        return response
    
    def getResMuxOduSapLed(self, parameters):
        '''**RES:AL:MUXODUSAPITIM? <level>** -
        Reports the Add/Drop ODU SAPI TIM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].oduSapiTim.led.isRed else b"OFF"
        return response
    
    def getResMuxOofLed(self, parameters):
        '''**RES:AL:MUXOOF? <level>** -
        Reports the Add/Drop OTU OOF LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].oof.led.isRed else b"OFF"
        return response
    
    def getResMuxOomLed(self, parameters):
        '''**RES:AL:MUXOOM? <level>** -
        Reports the Add/Drop OTU OOM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].oom.led.isRed else b"OFF"
        return response
    
    def getResMuxOpuC8SyncLed(self, parameters):
        '''**RES:AL:MUXOPUCMSYNC? <level>** -
        Reports the Add/Drop OPU CM SYNC LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].opuC8Sync.led.isRed else b"OFF"
        return response
    
    def getResMuxOpuCsfLed(self, parameters):
        '''**RES:AL:MUXOPUCSF? <level>** -
        Reports the Add/Drop OPU CSF LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].opuCsf.led.isRed else b"OFF"
        return response
    
    def getResMuxOpuFreWideLed(self, parameters):
        '''**RES:AL:MUXOPUFREQWIDE? <level>** -
        Reports the Add/Drop OPU Frequency Wide alarm LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].opuFreqWide.led.isRed else b"OFF"
        return response
    
    def getResMuxOpuPlmLed(self, parameters):
        '''**RES:AL:MUXOPUPLM? <level>** -
        Reports the Add/Drop OPU PLM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].opuPlm.led.isRed else b"OFF"
        return response
    
    def getResMuxTcm1BdLed(self, parameters):
        '''**RES:AL:MUXTCM1BDI? <level>** -
        Reports the Add/Drop TCM1 BDI LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[0].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm1BiaeLed(self, parameters):
        '''**RES:AL:MUXTCM1BIAE? <level>** -
        Reports the Add/Drop TCM1 BIAE LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[0].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm1DaLed(self, parameters):
        '''**RES:AL:MUXTCM1DAPITIM? <level>** -
        Reports the Add/Drop TCM1 DAPI TIM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[0].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm1SaLed(self, parameters):
        '''**RES:AL:MUXTCM1SAPITIM? <level>** -
        Reports the Add/Drop TCM1 SAPI TIM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[0].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm2BdLed(self, parameters):
        '''**RES:AL:MUXTCM2BDI? <level>** -
        Reports the Add/Drop TCM2 BDI LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[1].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm2BiaeLed(self, parameters):
        '''**RES:AL:MUXTCM2BIAE? <level>** -
        Reports the Add/Drop TCM2 BIAE LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[1].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm2DaLed(self, parameters):
        '''**RES:AL:MUXTCM2DAPITIM? <level>** -
        Reports the Add/Drop TCM2 DAPI TIM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[1].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm2SaLed(self, parameters):
        '''**RES:AL:MUXTCM2SAPITIM? <level>** -
        Reports the Add/Drop TCM2 SAPI TIM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[1].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm3BdLed(self, parameters):
        '''**RES:AL:MUXTCM3BDI? <level>** -
        Reports the Add/Drop TCM3 BDI LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[2].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm3BiaeLed(self, parameters):
        '''**RES:AL:MUXTCM3BIAE? <level>** -
        Reports the Add/Drop TCM1 BIAE LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[2].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm3DaLed(self, parameters):
        '''**RES:AL:MUXTCM3DAPITIM? <level>** -
        Reports the Add/Drop TCM3 DAPI TIM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[2].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm3SaLed(self, parameters):
        '''**RES:AL:MUXTCM3SAPITIM? <level>** -
        Reports the Add/Drop TCM3 SAPI TIM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[2].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm4BdLed(self, parameters):
        '''**RES:AL:MUXTCM4BDI? <level>** -
        Reports the Add/Drop TCM4 BDI LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[3].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm4BiaeLed(self, parameters):
        '''**RES:AL:MUXTCM4BIAE? <level>** -
        Reports the Add/Drop TCM4 BIAE LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[3].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm4DaLed(self, parameters):
        '''**RES:AL:MUXTCM4DAPITIM? <level>** -
        Reports the Add/Drop TCM4 DAPI TIM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[3].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm4SaLed(self, parameters):
        '''**RES:AL:MUXTCM4SAPITIM? <level>** -
        Reports the Add/Drop TCM4 SAPI TIM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[3].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm5BdLed(self, parameters):
        '''**RES:AL:MUXTCM5BDI? <level>** -
        Reports the Add/Drop TCM5 BDI LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[4].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm5BiaeLed(self, parameters):
        '''**RES:AL:MUXTCM5BIAE? <level>** -
        Reports the Add/Drop TCM5 BIAE LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[4].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm5DaLed(self, parameters):
        '''**RES:AL:MUXTCM5DAPITIM? <level>** -
        Reports the Add/Drop TCM5 DAPI TIM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[4].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm5SaLed(self, parameters):
        '''**RES:AL:MUXTCM5SAPITIM? <level>** -
        Reports the Add/Drop TCM5 SAPI TIM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[4].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm6BdLed(self, parameters):
        '''**RES:AL:MUXTCM6BDI? <level>** -
        Reports the Add/Drop TCM6 BDI LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[5].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm6BiaeLed(self, parameters):
        '''**RES:AL:MUXTCM6BIAE? <level>** -
        Reports the Add/Drop TCM6 BIAE LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[5].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm6DaLed(self, parameters):
        '''**RES:AL:MUXTCM6DAPITIM? <level>** -
        Reports the Add/Drop TCM6 DAPI TIM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[5].led.isRed else b"OFF"
        return response
    
    def getResMuxTcm6SaLed(self, parameters):
        '''**RES:AL:MUXTCM6SAPITIM? <level>** -
        Reports the Add/Drop TCM6 SAPI TIM LED state for the (ON or OFF)
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"ON" if self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[5].led.isRed else b"OFF"
        return response
    
    def muxC8Crc8AvgErrRate(self, parameters):
        '''**RES:MUXCMCRC8:AVE? <level>** -
        Reports the Add/Drop OPU CM CRC8 average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].opuC8Crc8.avgRate
        return response

    def muxC8Crc8ErrCount(self, parameters):
        '''**RES:MUXCMCRC8:COUNt? <level>** -
        Reports the Add/Drop OPU CM CRC8 error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].opuC8Crc8.count
        return response
    
    def muxC8Crc8ErrRate(self, parameters):
        '''**RES:MUXCMCRC8:RATe? <level>** -
        Reports the Add/Drop OPU CM CRC8 current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].opuC8Crc8.currRate
        return response

    def muxFrameAvgErrRate(self, parameters):
        '''**RES:MUXFRAME:AVE? <level>** -
        Reports the Add/Drop OTU FRAME average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].frame.avgRate
        return response

    def muxFrameErrCount(self, parameters):
        '''**RES:MUXFRAME:COUNt? <level>** -
        Reports the Add/Drop OTU FRAME error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].frame.count
        return response
    
    def muxFrameErrRate(self, parameters):
        '''**RES:MUXFRAME:RATe? <level>** -
        Reports the Add/Drop OTU FRAME current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].frame.currRate
        return response

    def getResMuxLofAlrm(self, parameters):
        '''**RES:MUXLOF:SECS? <level>** -
        Reports the Add/Drop OTU LOF alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].lof.secs
        return response
    
    def getResMuxLomAlrm(self, parameters):
        '''**RES:MUXLOM:SECS? <level>** -
        Reports the Add/Drop OTU LOM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].lom.secs
        return response

    def muxMfasAvgErrRate(self, parameters):
        '''**RES:MUXMFAS:AVE? <level>** -
        Reports the Add/Drop OTU MFAS average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].mfas.avgRate
        return response

    def muxMfasErrCount(self, parameters):
        '''**RES:MUXMFAS:COUNt? <level>** -
        Reports the Add/Drop OTU MFAS error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].mfas.count
        return response
    
    def muxMfasErrRate(self, parameters):
        '''**RES:MUXMFAS:RATe? <level>** -
        Reports the Add/Drop OTU MFAS current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].mfas.currRate
        return response

    def muxOduBeiAvgErrRate(self, parameters):
        '''**RES:MUXODU:BEI:AVE? <level>** -
        Reports the Add/Drop ODU BEI average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].oduBei.avgRate
        return response

    def muxOduBeiErrCount(self, parameters):
        '''**RES:MUXODU:BEI:COUNt? <level>** -
        Reports the Add/Drop ODU BEI error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].oduBei.count
        return response
    
    def muxOduBeiErrRate(self, parameters):
        '''**RES:MUXODU:BEI:RATe? <level>** -
        Reports the Add/Drop ODU BEI current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].oduBei.currRate
        return response

    def muxOduBip8AvgErrRate(self, parameters):
        '''**RES:MUXODU:BIP8:AVE? <level>** -
        Reports the Add/Drop ODU BIP8 average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].oduBip8.avgRate
        return response

    def muxOduBip8ErrCount(self, parameters):
        '''**RES:MUXODU:BIP8:COUNt? <level>** -
        Reports the Add/Drop ODU BIP8 error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].oduBip8.count
        return response
    
    def muxOduBip8ErrRate(self, parameters):
        '''**RES:MUXODU:BIP8:RATe? <level>** -
        Reports the Add/Drop ODU BIP8 current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].oduBip8.currRate
        return response

    def getResMuxOduAisAlrm(self, parameters):
        '''**RES:MUXODUAIS:SECS? <level>** -
        Reports the Add/Drop ODU AIS alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].oduAis.secs
        return response

    def getResMuxOduBdiAlrm(self, parameters):
        '''**RES:MUXODUBDI:SECS? <level>** -
        Reports the Add/Drop ODU BDI alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].oduBdi.secs
        return response

    def getResMuxOduDaAlrm(self, parameters):
        '''**RES:MUXODUDAPITIM:SECS? <level>** -
        Reports the Add/Drop ODU DAPI TIM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].oduDapiTim.secs
        return response

    def getResMuxOduLckAlrm(self, parameters):
        '''**RES:MUXODULCK:SECS? <level>** -
        Reports the Add/Drop ODU LCK alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].oduLck.secs
        return response

    def getResMuxOduOciAlrm(self, parameters):
        '''**RES:MUXODUOCI:SECS? <level>** -
        Reports the Add/Drop ODU OCI alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].oduOci.secs
        return response

    def getResMuxOduSaAlrm(self, parameters):
        '''**RES:MUXODUSAPITIM:SECS? <level>** -
        Reports the Add/Drop ODU SAPI TIM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].oduSapiTim.secs
        return response

    def getResMuxOofAlrm(self, parameters):
        '''**RES:MUXOOF:SECS? <level>** -
        Reports the Add/Drop OTU OOF alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].oof.secs
        return response

    def getResMuxOomAlrm(self, parameters):
        '''**RES:MUXOOM:SECS? <level>** -
        Reports the Add/Drop OTU OOM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].oom.secs
        return response

    def getResMuxOpuC8SyncAlrm(self, parameters):
        '''**RES:MUXOPUCMSYNC:SECS? <level>** -
        Reports the Add/Drop OPU CM SYNC alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].opuC8Sync.secs
        return response

    def getResMuxOpuCsfAlrm(self, parameters):
        '''**RES:MUXOPUCSF:SECS? <level>** -
        Reports the Add/Drop OPU CSF alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].opuCsf.secs
        return response

    def getResMuxOpuFreWideAlrm(self, parameters):
        '''**RES:MUXOPUFREQWIDE:SECS? <level>** -
        Reports the Add/Drop OPU Frequency Wide alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].opuFreqWide.secs
        return response

    def getResMuxPjcsCount(self, parameters):
        '''**RES:MUXOPUJUST:SECS? <level>** -
        Reports the Add/Drop OPU Frequency Justification seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].justifySecs
        return response

    def getResMuxNpjcCount(self, parameters):
        '''**RES:MUXOPUNEGJUST:COUNt? <level>** -
        Reports the Add/Drop OPU Negative Freq. Justification count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].negJustify.count
        return response

    def getResMuxOpuPlmAlrm(self, parameters):
        '''**RES:MUXOPUPLM:SECS? <level>** -
        Reports the Add/Drop OPU PSI-0 PLM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].opuPlm.secs
        return response

    def getResMuxPpjcCount(self, parameters):
        '''**RES:MUXOPUPOSJUST:COUNt? <level>** -
        Reports the Add/Drop OPU Positive Freq. Justification count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].posJustify.count
        return response

    def tcmMux1BeiAvgErrRate(self, parameters):
        '''**RES:MUXTCM1:BEI:AVE? <level>** -
        Reports the Add/Drop TCM1 BEI average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[0].avgRate
        return response

    def tcmMux1BeiErrCount(self, parameters):
        '''**RES:MUXTCM1:BEI:COUNt? <level>** -
        Reports the Add/Drop TCM1 BEI error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[0].count
        return response
    
    def tcmMux1BeiErrRate(self, parameters):
        '''**RES:MUXTCM1:BEI:RATe? <level>** -
        Reports the Add/Drop TCM1 BEI current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[0].currRate
        return response
    
    def tcmMux1Bip8AvgErrRate(self, parameters):
        '''**RES:MUXTCM1:BIP8:AVE? <level>** -
        Reports the Add/Drop TCM1 BIP8 average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[0].avgRate
        return response

    def tcmMux1Bip8ErrCount(self, parameters):
        '''**RES:MUXTCM1:BIP8:COUNt? <level>** -
        Reports the Add/Drop TCM1 BIP8 error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[0].count
        return response
    
    def tcmMux1Bip8ErrRate(self, parameters):
        '''**RES:MUXTCM1:BIP8:RATe? <level>** -
        Reports the Add/Drop TCM1 BIP8 current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[0].currRate
        return response

    def getResMuxTcm1BdAlrm(self, parameters):
        '''**RES:MUXTCM1BDI:SECS? <level>** -
        Reports the Add/Drop TCM1 BDI alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[0].secs
        return response

    def getResMuxTcm1BiaeAlrm(self, parameters):
        '''**RES:MUXTCM1BIAE:SECS? <level>** -
        Reports the Add/Drop TCM1 BIAE alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[0].secs
        return response

    def getResMuxTcm1DaAlrm(self, parameters):
        '''**RES:MUXTCM1DAPITIM:SECS? <level>** -
        Reports the Add/Drop TCM1 DAPI TIM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[0].secs
        return response

    def getResMuxTcm1SaAlrm(self, parameters):
        '''**RES:MUXTCM1SAPITIM:SECS? <level>** -
        Reports the Add/Drop TCM1 SAPI TIM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[0].secs
        return response

    def tcmMux2BeiAvgErrRate(self, parameters):
        '''**RES:MUXTCM2:BEI:AVE? <level>** -
        Reports the Add/Drop TCM2 BEI average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[1].avgRate
        return response

    def tcmMux2BeiErrCount(self, parameters):
        '''**RES:MUXTCM2:BEI:COUNt? <level>** -
        Reports the Add/Drop TCM2 BEI error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[1].count
        return response
    
    def tcmMux2BeiErrRate(self, parameters):
        '''**RES:MUXTCM2:BEI:RATe? <level>** -
        Reports the Add/Drop TCM2 BEI current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[1].currRate
        return response
    
    def tcmMux2Bip8AvgErrRate(self, parameters):
        '''**RES:MUXTCM2:BIP8:AVE? <level>** -
        Reports the Add/Drop TCM2 BIP8 average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[1].avgRate
        return response

    def tcmMux2Bip8ErrCount(self, parameters):
        '''**RES:MUXTCM2:BIP8:COUNt? <level>** -
        Reports the Add/Drop TCM2 BIP8 error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[1].count
        return response
    
    def tcmMux2Bip8ErrRate(self, parameters):
        '''**RES:MUXTCM2:BIP8:RATe? <level>** -
        Reports the Add/Drop TCM2 BIP8 current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[1].currRate
        return response

    def getResMuxTcm2BdAlrm(self, parameters):
        '''**RES:MUXTCM2BDI:SECS? <level>** -
        Reports the Add/Drop TCM2 BDI alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[1].secs
        return response

    def getResMuxTcm2BiaeAlrm(self, parameters):
        '''**RES:MUXTCM2BIAE:SECS? <level>** -
        Reports the Add/Drop TCM2 BIAE alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[1].secs
        return response

    def getResMuxTcm2DaAlrm(self, parameters):
        '''**RES:MUXTCM2DAPITIM:SECS? <level>** -
        Reports the Add/Drop TCM2 DAPI TIM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[1].secs
        return response

    def getResMuxTcm2SaAlrm(self, parameters):
        '''**RES:MUXTCM2SAPITIM:SECS? <level>** -
        Reports the Add/Drop TCM2 SAPI TIM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[1].secs
        return response

    def tcmMux3BeiAvgErrRate(self, parameters):
        '''**RES:MUXTCM3:BEI:AVE? <level>** -
        Reports the Add/Drop TCM3 BEI average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[2].avgRate
        return response

    def tcmMux3BeiErrCount(self, parameters):
        '''**RES:MUXTCM3:BEI:COUNt? <level>** -
        Reports the Add/Drop TCM3 BEI error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[2].count
        return response
    
    def tcmMux3BeiErrRate(self, parameters):
        '''**RES:MUXTCM3:BEI:RATe? <level>** -
        Reports the Add/Drop TCM3 BEI current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[2].currRate
        return response
    
    def tcmMux3Bip8AvgErrRate(self, parameters):
        '''**RES:MUXTCM3:BIP8:AVE? <level>** -
        Reports the Add/Drop TCM3 BIP8 average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[2].avgRate
        return response

    def tcmMux3Bip8ErrCount(self, parameters):
        '''**RES:MUXTCM3:BIP8:COUNt? <level>** -
        Reports the Add/Drop TCM3 BIP8 error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[2].count
        return response
    
    def tcmMux3Bip8ErrRate(self, parameters):
        '''**RES:MUXTCM3:BIP8:RATe? <level>** -
        Reports the Add/Drop TCM3 BIP8 current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[2].currRate
        return response

    def getResMuxTcm3BdAlrm(self, parameters):
        '''**RES:MUXTCM3BDI:SECS? <level>** -
        Reports the Add/Drop TCM3 BDI alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[2].secs
        return response

    def getResMuxTcm3BiaeAlrm(self, parameters):
        '''**RES:MUXTCM3BIAE:SECS? <level>** -
        Reports the Add/Drop TCM3 BIAE alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[2].secs
        return response

    def getResMuxTcm3DaAlrm(self, parameters):
        '''**RES:MUXTCM3DAPITIM:SECS? <level>** -
        Reports the Add/Drop TCM3 DAPI TIM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[2].secs
        return response

    def getResMuxTcm3SaAlrm(self, parameters):
        '''**RES:MUXTCM3SAPITIM:SECS? <level>** -
        Reports the Add/Drop TCM3 SAPI TIM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[2].secs
        return response

    def tcmMux4BeiAvgErrRate(self, parameters):
        '''**RES:MUXTCM4:BEI:AVE? <level>** -
        Reports the Add/Drop TCM4 BEI average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[3].avgRate
        return response

    def tcmMux4BeiErrCount(self, parameters):
        '''**RES:MUXTCM4:BEI:COUNt? <level>** -
        Reports the Add/Drop TCM4 BEI error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[3].count
        return response
    
    def tcmMux4BeiErrRate(self, parameters):
        '''**RES:MUXTCM4:BEI:RATe? <level>** -
        Reports the Add/Drop TCM4 BEI current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[3].currRate
        return response
    
    def tcmMux4Bip8AvgErrRate(self, parameters):
        '''**RES:MUXTCM4:BIP8:AVE? <level>** -
        Reports the Add/Drop TCM4 BIP8 average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[3].avgRate
        return response

    def tcmMux4Bip8ErrCount(self, parameters):
        '''**RES:MUXTCM4:BIP8:COUNt? <level>** -
        Reports the Add/Drop TCM4 BIP8 error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[3].count
        return response
    
    def tcmMux4Bip8ErrRate(self, parameters):
        '''**RES:MUXTCM4:BIP8:RATe? <level>** -
        Reports the Add/Drop TCM4 BIP8 current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[3].currRate
        return response

    def getResMuxTcm4BdAlrm(self, parameters):
        '''**RES:MUXTCM4BDI:SECS? <level>** -
        Reports the Add/Drop TCM4 BDI alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[3].secs
        return response

    def getResMuxTcm4BiaeAlrm(self, parameters):
        '''**RES:MUXTCM4BIAE:SECS? <level>** -
        Reports the Add/Drop TCM4 BIAE alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[3].secs
        return response

    def getResMuxTcm4DaAlrm(self, parameters):
        '''**RES:MUXTCM4DAPITIM:SECS? <level>** -
        Reports the Add/Drop TCM4 DAPI TIM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[3].secs
        return response

    def getResMuxTcm4SaAlrm(self, parameters):
        '''**RES:MUXTCM4SAPITIM:SECS? <level>** -
        Reports the Add/Drop TCM4 SAPI TIM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[3].secs
        return response
    
    

    def tcmMux5BeiAvgErrRate(self, parameters):
        '''**RES:MUXTCM5:BEI:AVE? <level>** -
        Reports the Add/Drop TCM5 BEI average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[4].avgRate
        return response

    def tcmMux5BeiErrCount(self, parameters):
        '''**RES:MUXTCM5:BEI:COUNt? <level>** -
        Reports the Add/Drop TCM5 BEI error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[4].count
        return response
    
    def tcmMux5BeiErrRate(self, parameters):
        '''**RES:MUXTCM5:BEI:RATe? <level>** -
        Reports the Add/Drop TCM5 BEI current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[4].currRate
        return response
    
    def tcmMux5Bip8AvgErrRate(self, parameters):
        '''**RES:MUXTCM5:BIP8:AVE? <level>** -
        Reports the Add/Drop TCM5 BIP8 average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[4].avgRate
        return response

    def tcmMux5Bip8ErrCount(self, parameters):
        '''**RES:MUXTCM5:BIP8:COUNt? <level>** -
        Reports the Add/Drop TCM5 BIP8 error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[4].count
        return response
    
    def tcmMux5Bip8ErrRate(self, parameters):
        '''**RES:MUXTCM5:BIP8:RATe? <level>** -
        Reports the Add/Drop TCM5 BIP8 current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[4].currRate
        return response

    def getResMuxTcm5BdAlrm(self, parameters):
        '''**RES:MUXTCM5BDI:SECS? <level>** -
        Reports the Add/Drop TCM5 BDI alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[4].secs
        return response

    def getResMuxTcm5BiaeAlrm(self, parameters):
        '''**RES:MUXTCM5BIAE:SECS? <level>** -
        Reports the Add/Drop TCM5 BIAE alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[4].secs
        return response

    def getResMuxTcm5DaAlrm(self, parameters):
        '''**RES:MUXTCM5DAPITIM:SECS? <level>** -
        Reports the Add/Drop TCM5 DAPI TIM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[4].secs
        return response

    def getResMuxTcm5SaAlrm(self, parameters):
        '''**RES:MUXTCM5SAPITIM:SECS? <level>** -
        Reports the Add/Drop TCM5 SAPI TIM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[4].secs
        return response

    def tcmMux6BeiAvgErrRate(self, parameters):
        '''**RES:MUXTCM6:BEI:AVE? <level>** -
        Reports the Add/Drop TCM6 BEI average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[5].avgRate
        return response

    def tcmMux6BeiErrCount(self, parameters):
        '''**RES:MUXTCM6:BEI:COUNt? <level>** -
        Reports the Add/Drop TCM6 BEI error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[5].count
        return response
    
    def tcmMux6BeiErrRate(self, parameters):
        '''**RES:MUXTCM6:BEI:RATe? <level>** -
        Reports the Add/Drop TCM6 BEI current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBei[5].currRate
        return response
    
    def tcmMux6Bip8AvgErrRate(self, parameters):
        '''**RES:MUXTCM6:BIP8:AVE? <level>** -
        Reports the Add/Drop TCM6 BIP8 average error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[5].avgRate
        return response

    def tcmMux6Bip8ErrCount(self, parameters):
        '''**RES:MUXTCM6:BIP8:COUNt? <level>** -
        Reports the Add/Drop TCM6 BIP8 error count.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[5].count
        return response
    
    def tcmMux6Bip8ErrRate(self, parameters):
        '''**RES:MUXTCM6:BIP8:RATe? <level>** -
        Reports the Add/Drop TCM6 BIP8 current error rate.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%.2e" % self.globals.veexOtn.odtuStats[muxLevel].tcmBip8[5].currRate
        return response

    def getResMuxTcm6BdAlrm(self, parameters):
        '''**RES:MUXTCM6BDI:SECS? <level>** -
        Reports the Add/Drop TCM6 BDI alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBdi[5].secs
        return response

    def getResMuxTcm6BiaeAlrm(self, parameters):
        '''**RES:MUXTCM6BIAE:SECS? <level>** -
        Reports the Add/Drop TCM6 BIAE alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmBiae[5].secs
        return response

    def getResMuxTcm6DaAlrm(self, parameters):
        '''**RES:MUXTCM6DAPITIM:SECS? <level>** -
        Reports the Add/Drop TCM6 DAPI TIM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmDapiTim[5].secs
        return response

    def getResMuxTcm6SaAlrm(self, parameters):
        '''**RES:MUXTCM6SAPITIM:SECS? <level>** -
        Reports the Add/Drop TCM6 SAPI TIM alarm seconds.
        '''
        muxLevel, response = self._getMuxLevel(parameters)
        if muxLevel != -1:
            self.globals.veexOtn.odtuStats[muxLevel].update()
            return b"%d" % self.globals.veexOtn.odtuStats[muxLevel].tcmSapiTim[5].secs
        return response
                
    
# This table contains all the system SCPI commands. Note that queries must
# come before the matching setting commands. Also if two commands start with
# the same text then the longer one must come first.
commandTable = [
    Cmnd(b"TX:ALarm:TYPE?",            ScpiOtn.getTxAlarmType),
    Cmnd(b"TX:ALarm:TYPE",             ScpiOtn.setTxAlarmType),
    Cmnd(b"TX:CLOCK?",                 ScpiOtn.getTxClock),
    Cmnd(b"TX:CLOCK",                  ScpiOtn.setTxClock),
    Cmnd(b"TX:COUPled?",               ScpiOtn.getTxCoupled),
    Cmnd(b"TX:COUPled",                ScpiOtn.setTxCoupled),
    Cmnd(b"TX:DATAINVERT?",            ScpiOtn.getTxDataInvert),
    Cmnd(b"TX:DATAINVERT",             ScpiOtn.setTxDataInvert),
    Cmnd(b"TX:ERRor:BURSTPERIOD?",     ScpiOtn.getTxErrBurst),
    Cmnd(b"TX:ERRor:BURSTPERIOD",      ScpiOtn.setTxErrBurst),
    Cmnd(b"TX:ERRor:BURSTSIZE?",       ScpiOtn.getTxErrBurstSize),
    Cmnd(b"TX:ERRor:BURSTSIZE",        ScpiOtn.setTxErrBurstSize),
    Cmnd(b"TX:ERRor:RATE?",            ScpiOtn.getTxErrRate),
    Cmnd(b"TX:ERRor:RATE",             ScpiOtn.setTxErrRate),
    Cmnd(b"TX:ERRor:TYPE?",            ScpiOtn.getTxErrType),
    Cmnd(b"TX:ERRor:TYPE",             ScpiOtn.setTxErrType),
    Cmnd(b"TX:FEC?",                   ScpiOtn.getTxFec),
    Cmnd(b"TX:FEC",                    ScpiOtn.setTxFec),
    Cmnd(b"TX:FLEXRATE?",              ScpiOtn.getTxMuxFlexRate),
    Cmnd(b"TX:FLEXRATE",               ScpiOtn.setTxMuxFlexRate),
    Cmnd(b"TX:FREQOFFset:PPM?",        ScpiOtn.getTxFreqOffsetPpm),
    Cmnd(b"TX:FREQOFFset:HZ?",         ScpiOtn.getTxFreqOffsetHz),
    Cmnd(b"TX:FREQOFFset:LINE?",       ScpiOtn.getTxFreqOffLine),
    Cmnd(b"TX:FREQOFFset:LINE",        ScpiOtn.setTxFreqOffLine),
    Cmnd(b"TX:FREQuency?",             ScpiOtn.getTxFreq),
    Cmnd(b"TX:INTerface?",             ScpiOtn.getTxInterface),
    Cmnd(b"TX:INTerface",              ScpiOtn.setTxInterface),
    Cmnd(b"TX:LASERPUP?",              ScpiOtn.getTxLaserPwrUp),
    Cmnd(b"TX:LASERPUP",               ScpiOtn.setTxLaserPwrUp),
    Cmnd(b"TX:LASERTYPE?",             ScpiOtn.getTxLaserType),
    Cmnd(b"TX:LASER?",                 ScpiOtn.getTxLaser),
    Cmnd(b"TX:LASER",                  ScpiOtn.setTxLaser),

    Cmnd(b"TX:MAPping?",               ScpiOtn.getTxMapping),
    Cmnd(b"TX:MAPping",                ScpiOtn.setTxMapping),
    Cmnd(b"TX:MCPATT?",                ScpiOtn.getTxMultiChanPattern),
    Cmnd(b"TX:MCPATT",                 ScpiOtn.setTxMultiChanPattern),
    Cmnd(b"TX:OH:INTRusive:ACT?",      ScpiOtn.txGetOhIntrAct),
    Cmnd(b"TX:OH:INTRusive:APSPCC?",   ScpiOtn.txGetOhIntrApspcc),
    Cmnd(b"TX:OH:INTRusive:EXP?",      ScpiOtn.txGetOhIntrExp),
    Cmnd(b"TX:OH:INTRusive:FAS?",      ScpiOtn.txGetOhIntrFas),
    Cmnd(b"TX:OH:INTRusive:FTFL?",     ScpiOtn.txGetOhIntrFtfl),
    Cmnd(b"TX:OH:INTRusive:GCC0?",     ScpiOtn.txGetOhIntrGcc0),
    Cmnd(b"TX:OH:INTRusive:GCC1?",     ScpiOtn.txGetOhIntrGcc1),
    Cmnd(b"TX:OH:INTRusive:GCC2?",     ScpiOtn.txGetOhIntrGcc2),
    Cmnd(b"TX:OH:INTRusive:JCNJO?",    ScpiOtn.txGetOhIntrJcnjo),
    Cmnd(b"TX:OH:INTRusive:MFAS?",     ScpiOtn.txGetOhIntrMfas),
    Cmnd(b"TX:OH:INTRusive:ODURES1?",  ScpiOtn.txGetOhIntrOdures1),
    Cmnd(b"TX:OH:INTRusive:ODURES2?",  ScpiOtn.txGetOhIntrOdures2),
    Cmnd(b"TX:OH:INTRusive:OPURES?",   ScpiOtn.txGetOhIntrOpures1),
    Cmnd(b"TX:OH:INTRusive:OTURES?",   ScpiOtn.txGetOhIntrOtures),
    Cmnd(b"TX:OH:INTRusive:PM?",       ScpiOtn.txGetOhIntrPm),
    Cmnd(b"TX:OH:INTRusive:PSI?",      ScpiOtn.txGetOhIntrPsi),
    Cmnd(b"TX:OH:INTRusive:SM?",       ScpiOtn.txGetOhIntrSm),
    Cmnd(b"TX:OH:INTRusive:TCM1?",     ScpiOtn.txGetOhIntrTcm1),
    Cmnd(b"TX:OH:INTRusive:TCM2?",     ScpiOtn.txGetOhIntrTcm2),
    Cmnd(b"TX:OH:INTRusive:TCM3?",     ScpiOtn.txGetOhIntrTcm3),
    Cmnd(b"TX:OH:INTRusive:TCM4?",     ScpiOtn.txGetOhIntrTcm4),
    Cmnd(b"TX:OH:INTRusive:TCM5?",     ScpiOtn.txGetOhIntrTcm5),
    Cmnd(b"TX:OH:INTRusive:TCM6?",     ScpiOtn.txGetOhIntrTcm6),
    Cmnd(b"TX:OH:INTRusive:ACT",       ScpiOtn.txSetOhIntrAct),
    Cmnd(b"TX:OH:INTRusive:APSPCC",    ScpiOtn.txSetOhIntrApspcc),
    Cmnd(b"TX:OH:INTRusive:EXP",       ScpiOtn.txSetOhIntrExp),
    Cmnd(b"TX:OH:INTRusive:FAS",       ScpiOtn.txSetOhIntrFas),
    Cmnd(b"TX:OH:INTRusive:FTFL",      ScpiOtn.txSetOhIntrFtfl),
    Cmnd(b"TX:OH:INTRusive:GCC0",      ScpiOtn.txSetOhIntrGcc0),
    Cmnd(b"TX:OH:INTRusive:GCC1",      ScpiOtn.txSetOhIntrGcc1),
    Cmnd(b"TX:OH:INTRusive:GCC2",      ScpiOtn.txSetOhIntrGcc2),
    Cmnd(b"TX:OH:INTRusive:JCNJO",     ScpiOtn.txSetOhIntrJcnjo),
    Cmnd(b"TX:OH:INTRusive:MFAS",      ScpiOtn.txSetOhIntrMfas),
    Cmnd(b"TX:OH:INTRusive:ODURES1",   ScpiOtn.txSetOhIntrOdures1),
    Cmnd(b"TX:OH:INTRusive:ODURES2",   ScpiOtn.txSetOhIntrOdures2),
    Cmnd(b"TX:OH:INTRusive:OPURES",    ScpiOtn.txSetOhIntrOpures1),
    Cmnd(b"TX:OH:INTRusive:OTURES",    ScpiOtn.txSetOhIntrOtures),
    Cmnd(b"TX:OH:INTRusive:PM",        ScpiOtn.txSetOhIntrPm),
    Cmnd(b"TX:OH:INTRusive:PSI",       ScpiOtn.txSetOhIntrPsi),
    Cmnd(b"TX:OH:INTRusive:SM",        ScpiOtn.txSetOhIntrSm),
    Cmnd(b"TX:OH:INTRusive:TCM1",      ScpiOtn.txSetOhIntrTcm1),
    Cmnd(b"TX:OH:INTRusive:TCM2",      ScpiOtn.txSetOhIntrTcm2),
    Cmnd(b"TX:OH:INTRusive:TCM3",      ScpiOtn.txSetOhIntrTcm3),
    Cmnd(b"TX:OH:INTRusive:TCM4",      ScpiOtn.txSetOhIntrTcm4),
    Cmnd(b"TX:OH:INTRusive:TCM5",      ScpiOtn.txSetOhIntrTcm5),
    Cmnd(b"TX:OH:INTRusive:TCM6",      ScpiOtn.txSetOhIntrTcm6),

    Cmnd(b"TX:OH:ODU:APS1?",           ScpiOtn.txOhOdu2Aps1),
    Cmnd(b"TX:OH:ODU:APS2?",           ScpiOtn.txOhOdu2Aps2),
    Cmnd(b"TX:OH:ODU:APS3?",           ScpiOtn.txOhOdu2Aps3),
    Cmnd(b"TX:OH:ODU:APS4?",           ScpiOtn.txOhOdu2Aps4),
    Cmnd(b"TX:OH:ODU:BEI?",            ScpiOtn.txOhOdu1Bei),
    Cmnd(b"TX:OH:ODU:BFTFL:FAULT?",    ScpiOtn.txOhOdu1BfFault),
    Cmnd(b"TX:OH:ODU:BFTFL:OI?",       ScpiOtn.txOhOdu1BfOi),
    Cmnd(b"TX:OH:ODU:BFTFL:OS?",       ScpiOtn.txOhOdu1BfOs),
    Cmnd(b"TX:OH:ODU:DAPI?",           ScpiOtn.txOhOdu1Dapi),
    Cmnd(b"TX:OH:ODU:EXP1?",           ScpiOtn.txOhOdu2Exp1),
    Cmnd(b"TX:OH:ODU:EXP2?",           ScpiOtn.txOhOdu2Exp2),
    Cmnd(b"TX:OH:ODU:FFTFL:FAULT?",    ScpiOtn.txOhOdu1FfFault),
    Cmnd(b"TX:OH:ODU:FFTFL:OI?",       ScpiOtn.txOhOdu1FfOi),
    Cmnd(b"TX:OH:ODU:FFTFL:OS?",       ScpiOtn.txOhOdu1FfOs),
    Cmnd(b"TX:OH:ODU:GCC11?",          ScpiOtn.txOhOdu2Gcc11),
    Cmnd(b"TX:OH:ODU:GCC12?",          ScpiOtn.txOhOdu2Gcc12),
    Cmnd(b"TX:OH:ODU:GCC21?",          ScpiOtn.txOhOdu2Gcc21),
    Cmnd(b"TX:OH:ODU:GCC22?",          ScpiOtn.txOhOdu2Gcc22),
    Cmnd(b"TX:OH:ODU:RES1?",           ScpiOtn.txOhOdu2Res1),
    Cmnd(b"TX:OH:ODU:RES2?",           ScpiOtn.txOhOdu2Res2),
    Cmnd(b"TX:OH:ODU:PMANDTCM?",       ScpiOtn.txOhOdu2Res3),
    Cmnd(b"TX:OH:ODU:RES3?",           ScpiOtn.txOhOdu2Res3),
    Cmnd(b"TX:OH:ODU:RES4?",           ScpiOtn.txOhOdu2Res4),
    Cmnd(b"TX:OH:ODU:RES5?",           ScpiOtn.txOhOdu2Res5),
    Cmnd(b"TX:OH:ODU:RES6?",           ScpiOtn.txOhOdu2Res6),
    Cmnd(b"TX:OH:ODU:RES7?",           ScpiOtn.txOhOdu2Res7),
    Cmnd(b"TX:OH:ODU:RES8?",           ScpiOtn.txOhOdu2Res8),
    Cmnd(b"TX:OH:ODU:RES9?",           ScpiOtn.txOhOdu2Res9),
    Cmnd(b"TX:OH:ODU:SAPI?",           ScpiOtn.txOhOdu1Sapi),
    Cmnd(b"TX:OH:ODU:SPECIFIC?",       ScpiOtn.txOhOdu1Specific),
    Cmnd(b"TX:OH:ODU:TCMACT?",         ScpiOtn.txOhOdu2TcmAct),
    Cmnd(b"TX:OH:ODU:PMANDTCM?",       ScpiOtn.txOhOdu2Res3),

    Cmnd(b"TX:OH:ODU:APS1",            ScpiOtn.txSetOhOdu2Aps1),
    Cmnd(b"TX:OH:ODU:APS2",            ScpiOtn.txSetOhOdu2Aps2),
    Cmnd(b"TX:OH:ODU:APS3",            ScpiOtn.txSetOhOdu2Aps3),
    Cmnd(b"TX:OH:ODU:APS4",            ScpiOtn.txSetOhOdu2Aps4),
    Cmnd(b"TX:OH:ODU:BEI",             ScpiOtn.txSetOhOdu1Bei),
    Cmnd(b"TX:OH:ODU:BFTFL:FAULT",     ScpiOtn.txSetOhOdu1BfFault),
    Cmnd(b"TX:OH:ODU:BFTFL:OI",        ScpiOtn.txSetOhOdu1BfOi),
    Cmnd(b"TX:OH:ODU:BFTFL:OS",        ScpiOtn.txSetOhOdu1BfOs),
    Cmnd(b"TX:OH:ODU:DAPI",            ScpiOtn.txSetOhOdu1Dapi),
    Cmnd(b"TX:OH:ODU:EXP1",            ScpiOtn.txSetOhOdu2Exp1),
    Cmnd(b"TX:OH:ODU:EXP2",            ScpiOtn.txSetOhOdu2Exp2),
    Cmnd(b"TX:OH:ODU:FFTFL:FAULT",     ScpiOtn.txSetOhOdu1FfFault),
    Cmnd(b"TX:OH:ODU:FFTFL:OI",        ScpiOtn.txSetOhOdu1FfOi),
    Cmnd(b"TX:OH:ODU:FFTFL:OS",        ScpiOtn.txSetOhOdu1FfOs),
    Cmnd(b"TX:OH:ODU:GCC11",           ScpiOtn.txSetOhOdu2Gcc11),
    Cmnd(b"TX:OH:ODU:GCC12",           ScpiOtn.txSetOhOdu2Gcc12),
    Cmnd(b"TX:OH:ODU:GCC21",           ScpiOtn.txSetOhOdu2Gcc21),
    Cmnd(b"TX:OH:ODU:GCC22",           ScpiOtn.txSetOhOdu2Gcc22),
    Cmnd(b"TX:OH:ODU:RES1",            ScpiOtn.txSetOhOdu2Res1),
    Cmnd(b"TX:OH:ODU:RES2",            ScpiOtn.txSetOhOdu2Res2),
    Cmnd(b"TX:OH:ODU:PMANDTCM",        ScpiOtn.txSetOhOdu2Res3),
    Cmnd(b"TX:OH:ODU:RES3",            ScpiOtn.txSetOhOdu2Res3),
    Cmnd(b"TX:OH:ODU:RES4",            ScpiOtn.txSetOhOdu2Res4),
    Cmnd(b"TX:OH:ODU:RES5",            ScpiOtn.txSetOhOdu2Res5),
    Cmnd(b"TX:OH:ODU:RES6",            ScpiOtn.txSetOhOdu2Res6),
    Cmnd(b"TX:OH:ODU:RES7",            ScpiOtn.txSetOhOdu2Res7),
    Cmnd(b"TX:OH:ODU:RES8",            ScpiOtn.txSetOhOdu2Res8),
    Cmnd(b"TX:OH:ODU:RES9",            ScpiOtn.txSetOhOdu2Res9),
    Cmnd(b"TX:OH:ODU:SAPI",            ScpiOtn.txSetOhOdu1Sapi),
    Cmnd(b"TX:OH:ODU:SPECIFIC",        ScpiOtn.txSetOhOdu1Specific),
    Cmnd(b"TX:OH:ODU:TCMACT",          ScpiOtn.txSetOhOdu2TcmAct),
    Cmnd(b"TX:OH:ODU:PMANDTCM",        ScpiOtn.txSetOhOdu2Res3),

    Cmnd(b"TX:OH:OPU:PSI0?",           ScpiOtn.txOhOpuPsi),
    Cmnd(b"TX:OH:OPU:RES1?",           ScpiOtn.txOhOpuRes1),
    Cmnd(b"TX:OH:OPU:RES2?",           ScpiOtn.txOhOpuRes2),
    Cmnd(b"TX:OH:OPU:RES3?",           ScpiOtn.txOhOpuRes3),
    Cmnd(b"TX:OH:OPU:JC1?",            ScpiOtn.txOhOpuJc1),
    Cmnd(b"TX:OH:OPU:JC2?",            ScpiOtn.txOhOpuJc2),
    Cmnd(b"TX:OH:OPU:JC3?",            ScpiOtn.txOhOpuJc3),
    Cmnd(b"TX:OH:OPU:NJO?",            ScpiOtn.txOhOpuNjo),
    Cmnd(b"TX:OH:OPU:RES5?",           ScpiOtn.txOhOpuJc1),
    Cmnd(b"TX:OH:OPU:RES6?",           ScpiOtn.txOhOpuJc2),
    Cmnd(b"TX:OH:OPU:RES7?",           ScpiOtn.txOhOpuJc3),
    Cmnd(b"TX:OH:OPU:RES8?",           ScpiOtn.txOhOpuNjo),
    Cmnd(b"TX:OH:OPU:MSI?",            ScpiOtn.txOhOpuMsi),
    Cmnd(b"TX:OH:OPU:JUSTification",   ScpiOtn.txSetOhOpuJust),
    Cmnd(b"TX:OH:OPU:RES1",            ScpiOtn.txSetOhOpuRes1),
    Cmnd(b"TX:OH:OPU:RES2",            ScpiOtn.txSetOhOpuRes2),
    Cmnd(b"TX:OH:OPU:RES3",            ScpiOtn.txSetOhOpuRes3),
    Cmnd(b"TX:OH:OPU:RES5",            ScpiOtn.txSetOhOpuJc1),
    Cmnd(b"TX:OH:OPU:RES6",            ScpiOtn.txSetOhOpuJc2),
    Cmnd(b"TX:OH:OPU:RES7",            ScpiOtn.txSetOhOpuJc3),
    Cmnd(b"TX:OH:OPU:RES8",            ScpiOtn.txSetOhOpuNjo),
    Cmnd(b"TX:OH:OPU:PSI0",            ScpiOtn.txSetOhOpuPsi),
    Cmnd(b"TX:OH:OPU:MSI",             ScpiOtn.txSetOhOpuMsi),

    Cmnd(b"TX:OH:OTU:BEI?",            ScpiOtn.txOhOtuBei),
    Cmnd(b"TX:OH:OTU:DAPI?",           ScpiOtn.txOhOtuDapi),
    Cmnd(b"TX:OH:OTU:GCC01?",          ScpiOtn.txOhOtuGcc1),
    Cmnd(b"TX:OH:OTU:GCC02?",          ScpiOtn.txOhOtuGcc2),
    Cmnd(b"TX:OH:OTU:OA1:1?",          ScpiOtn.txOhOtuOa11),
    Cmnd(b"TX:OH:OTU:OA1:2?",          ScpiOtn.txOhOtuOa12),
    Cmnd(b"TX:OH:OTU:OA1:3?",          ScpiOtn.txOhOtuOa13),
    Cmnd(b"TX:OH:OTU:OA2:1?",          ScpiOtn.txOhOtuOa21),
    Cmnd(b"TX:OH:OTU:OA2:2?",          ScpiOtn.txOhOtuOa22),
    Cmnd(b"TX:OH:OTU:OA2:3?",          ScpiOtn.txOhOtuOa23),
    Cmnd(b"TX:OH:OTU:RES1?",           ScpiOtn.getTxOhOtuRes1),
    Cmnd(b"TX:OH:OTU:RES2?",           ScpiOtn.txOhOtuRes2),
    Cmnd(b"TX:OH:OTU:SAPI?",           ScpiOtn.txOhOtuSapi),
    Cmnd(b"TX:OH:OTU:SPECIFIC?",       ScpiOtn.txOhOtuSpecific),
    Cmnd(b"TX:OH:OTU:BEI",             ScpiOtn.txSetOhOtuBei),
    Cmnd(b"TX:OH:OTU:DAPI",            ScpiOtn.txSetOhOtuDapi),
    Cmnd(b"TX:OH:OTU:GCC01",           ScpiOtn.txSetOhOtuGcc1),
    Cmnd(b"TX:OH:OTU:GCC02",           ScpiOtn.txSetOhOtuGcc2),
    Cmnd(b"TX:OH:OTU:OA1:1",           ScpiOtn.txSetOhOtuOa11),
    Cmnd(b"TX:OH:OTU:OA1:2",           ScpiOtn.txSetOhOtuOa12),
    Cmnd(b"TX:OH:OTU:OA1:3",           ScpiOtn.txSetOhOtuOa13),
    Cmnd(b"TX:OH:OTU:OA2:1",           ScpiOtn.txSetOhOtuOa21),
    Cmnd(b"TX:OH:OTU:OA2:2",           ScpiOtn.txSetOhOtuOa22),
    Cmnd(b"TX:OH:OTU:OA2:3",           ScpiOtn.txSetOhOtuOa23),
    Cmnd(b"TX:OH:OTU:RES1",            ScpiOtn.setTxOhOtuRes1),
    Cmnd(b"TX:OH:OTU:RES2",            ScpiOtn.txSetOhOtuRes2),
    Cmnd(b"TX:OH:OTU:SAPI",            ScpiOtn.txSetOhOtuSapi),
    Cmnd(b"TX:OH:OTU:SPECIFIC",        ScpiOtn.txSetOhOtuSpecific),

    Cmnd(b"TX:OH:TCM1:BEI?",           ScpiOtn.txOhTcm1Bei),
    Cmnd(b"TX:OH:TCM1:DAPI?",          ScpiOtn.txOhTcm1Dapi),
    Cmnd(b"TX:OH:TCM1:SAPI?",          ScpiOtn.txOhTcm1Sapi),
    Cmnd(b"TX:OH:TCM1:SPECIFIC?",      ScpiOtn.txOhTcm1Specific),
    Cmnd(b"TX:OH:TCM1:BEI",            ScpiOtn.txSetOhTcm1Bei),
    Cmnd(b"TX:OH:TCM1:DAPI",           ScpiOtn.txSetOhTcm1Dapi),
    Cmnd(b"TX:OH:TCM1:SAPI",           ScpiOtn.txSetOhTcm1Sapi),
    Cmnd(b"TX:OH:TCM1:SPECIFIC",       ScpiOtn.txSetOhTcm1Specific),
    Cmnd(b"TX:OH:TCM2:BEI?",           ScpiOtn.txOhTcm2Bei),
    Cmnd(b"TX:OH:TCM2:DAPI?",          ScpiOtn.txOhTcm2Dapi),
    Cmnd(b"TX:OH:TCM2:SAPI?",          ScpiOtn.txOhTcm2Sapi),
    Cmnd(b"TX:OH:TCM2:SPECIFIC?",      ScpiOtn.txOhTcm2Specific),
    Cmnd(b"TX:OH:TCM2:BEI",            ScpiOtn.txSetOhTcm2Bei),
    Cmnd(b"TX:OH:TCM2:DAPI",           ScpiOtn.txSetOhTcm2Dapi),
    Cmnd(b"TX:OH:TCM2:SAPI",           ScpiOtn.txSetOhTcm2Sapi),
    Cmnd(b"TX:OH:TCM2:SPECIFIC",       ScpiOtn.txSetOhTcm2Specific),
    Cmnd(b"TX:OH:TCM3:BEI?",           ScpiOtn.txOhTcm3Bei),
    Cmnd(b"TX:OH:TCM3:DAPI?",          ScpiOtn.txOhTcm3Dapi),
    Cmnd(b"TX:OH:TCM3:SAPI?",          ScpiOtn.txOhTcm3Sapi),
    Cmnd(b"TX:OH:TCM3:SPECIFIC?",      ScpiOtn.txOhTcm3Specific),
    Cmnd(b"TX:OH:TCM3:BEI",            ScpiOtn.txSetOhTcm3Bei),
    Cmnd(b"TX:OH:TCM3:DAPI",           ScpiOtn.txSetOhTcm3Dapi),
    Cmnd(b"TX:OH:TCM3:SAPI",           ScpiOtn.txSetOhTcm3Sapi),
    Cmnd(b"TX:OH:TCM3:SPECIFIC",       ScpiOtn.txSetOhTcm3Specific),
    Cmnd(b"TX:OH:TCM4:BEI?",           ScpiOtn.txOhTcm4Bei),
    Cmnd(b"TX:OH:TCM4:DAPI?",          ScpiOtn.txOhTcm4Dapi),
    Cmnd(b"TX:OH:TCM4:SAPI?",          ScpiOtn.txOhTcm4Sapi),
    Cmnd(b"TX:OH:TCM4:SPECIFIC?",      ScpiOtn.txOhTcm4Specific),
    Cmnd(b"TX:OH:TCM4:BEI",            ScpiOtn.txSetOhTcm4Bei),
    Cmnd(b"TX:OH:TCM4:DAPI",           ScpiOtn.txSetOhTcm4Dapi),
    Cmnd(b"TX:OH:TCM4:SAPI",           ScpiOtn.txSetOhTcm4Sapi),
    Cmnd(b"TX:OH:TCM4:SPECIFIC",       ScpiOtn.txSetOhTcm4Specific),
    Cmnd(b"TX:OH:TCM5:BEI?",           ScpiOtn.txOhTcm5Bei),
    Cmnd(b"TX:OH:TCM5:DAPI?",          ScpiOtn.txOhTcm5Dapi),
    Cmnd(b"TX:OH:TCM5:SAPI?",          ScpiOtn.txOhTcm5Sapi),
    Cmnd(b"TX:OH:TCM5:SPECIFIC?",      ScpiOtn.txOhTcm5Specific),
    Cmnd(b"TX:OH:TCM5:BEI",            ScpiOtn.txSetOhTcm5Bei),
    Cmnd(b"TX:OH:TCM5:DAPI",           ScpiOtn.txSetOhTcm5Dapi),
    Cmnd(b"TX:OH:TCM5:SAPI",           ScpiOtn.txSetOhTcm5Sapi),
    Cmnd(b"TX:OH:TCM5:SPECIFIC",       ScpiOtn.txSetOhTcm5Specific),
    Cmnd(b"TX:OH:TCM6:BEI?",           ScpiOtn.txOhTcm6Bei),
    Cmnd(b"TX:OH:TCM6:DAPI?",          ScpiOtn.txOhTcm6Dapi),
    Cmnd(b"TX:OH:TCM6:SAPI?",          ScpiOtn.txOhTcm6Sapi),
    Cmnd(b"TX:OH:TCM6:SPECIFIC?",      ScpiOtn.txOhTcm6Specific),
    Cmnd(b"TX:OH:TCM6:BEI",            ScpiOtn.txSetOhTcm6Bei),
    Cmnd(b"TX:OH:TCM6:DAPI",           ScpiOtn.txSetOhTcm6Dapi),
    Cmnd(b"TX:OH:TCM6:DAPI",           ScpiOtn.txSetOhTcm6Sapi),
    Cmnd(b"TX:OH:TCM6:SPECIFIC",       ScpiOtn.txSetOhTcm6Specific),

    Cmnd(b"TX:OPUFREQOffset?",         ScpiOtn.getTxOpuFreqOffset),
    Cmnd(b"TX:OPUFREQOffset",          ScpiOtn.setTxOpuFreqOffset),
    Cmnd(b"TX:OTUCN?",                 ScpiOtn.getOTUCn),
    Cmnd(b"TX:OTUCN",                  ScpiOtn.setOTUCn),
    Cmnd(b"TX:OUTTHRESHold?",          ScpiOtn.getTxFreqThreshhold),
    Cmnd(b"TX:OUTTHRESHold",           ScpiOtn.setTxFreqThreshhold),
    Cmnd(b"TX:PASSthru?",              ScpiOtn.getTxPassthru),
    Cmnd(b"TX:PASSthru",               ScpiOtn.setTxPassthru),

    Cmnd(b"TX:PATTern?",               ScpiOtn.getTxPattern),
    Cmnd(b"TX:PATTern",                ScpiOtn.setTxPattern),

    Cmnd(b"TX:RTD:ACTION?",            ScpiOtn.getTxRtdAction),
    Cmnd(b"TX:RTD:ACTION",             ScpiOtn.setTxRtdAction),
    Cmnd(b"TX:RTD:DM?",                ScpiOtn.getTxRtdDmBit),
    Cmnd(b"TX:RTD:DM",                 ScpiOtn.setTxRtdDmBit),
    Cmnd(b"TX:RTD:GOOD:FRAME?",        ScpiOtn.getTxApsGoodFrames),
    Cmnd(b"TX:RTD:GOOD:FRAME",         ScpiOtn.setTxApsGoodFrames),
    Cmnd(b"TX:RTD:GOOD:TIME?",         ScpiOtn.getTxApsGoodTime),
    Cmnd(b"TX:RTD:GOOD:TIME",          ScpiOtn.setTxApsGoodTime),
    Cmnd(b"TX:RTD:ODTULEVEL?",         ScpiOtn.getTxRtdOduLevel),
    Cmnd(b"TX:RTD:ODTULEVEL",          ScpiOtn.setTxRtdOduLevel),
    Cmnd(b"TX:SCRAMBLE?",              ScpiOtn.getTxScramble),
    Cmnd(b"TX:SCRAMBLE",               ScpiOtn.setTxScramble),
    Cmnd(b"TX:TRIG?",                  ScpiOtn.getTxTrigger),
    Cmnd(b"TX:TRIG",                   ScpiOtn.setTxTrigger),

    Cmnd(b"RX:AUTORECOVER?",           ScpiOtn.getDisableLofReset),
    Cmnd(b"RX:AUTORECOVER",            ScpiOtn.setDisableLofReset),
    Cmnd(b"RX:CAP:ARM?",               ScpiOtn.getArmTrigger),
    Cmnd(b"RX:CAP:ARM",                ScpiOtn.armTrigger),
    Cmnd(b"RX:CAP:BYTE?",              ScpiOtn.getByteSelect),
    Cmnd(b"RX:CAP:BYTE",               ScpiOtn.setByteSelect),
    Cmnd(b"RX:CAP:MATCH?",             ScpiOtn.getMatchValue),
    Cmnd(b"RX:CAP:MATCH",              ScpiOtn.setMatchValue),
    Cmnd(b"RX:CAP:POS?",               ScpiOtn.getTriggerPos),
    Cmnd(b"RX:CAP:POS",                ScpiOtn.setTriggerPos),
    Cmnd(b"RX:CAP:REPORT?",            ScpiOtn.displayCapture),

    Cmnd(b"RX:CAP:SLOT?",              ScpiOtn.getSlot),
    Cmnd(b"RX:CAP:SLOT",               ScpiOtn.setSlot),
    Cmnd(b"RX:CAP:TRIG?",              ScpiOtn.getTrigger),
    Cmnd(b"RX:CAP:TRIG",               ScpiOtn.setTrigger),
    Cmnd(b"RX:COUPled?",               ScpiOtn.getTxCoupled),
    Cmnd(b"RX:COUPled",                ScpiOtn.setTxCoupled),
    Cmnd(b"RX:DATAINVERT?",            ScpiOtn.getRxDataInvert),
    Cmnd(b"RX:DATAINVERT",             ScpiOtn.setRxDataInvert),
    Cmnd(b"RX:FEC?",                   ScpiOtn.getRxFec),
    Cmnd(b"RX:FEC",                    ScpiOtn.setRxFec),
    Cmnd(b"RX:FLEXRATE?",              ScpiOtn.getRxMuxFlexRate),
    Cmnd(b"RX:FLEXRATEEXP?",           ScpiOtn.getRxMuxFlexRateExpected),
    Cmnd(b"RX:FLEXRATEEXP",            ScpiOtn.setRxMuxFlexRateExpected),
    Cmnd(b"RX:FLEXRATEOFF?",           ScpiOtn.getRxOpuJustLevel),
    Cmnd(b"RX:FREQuency?",             ScpiOtn.getRxFreq),
    Cmnd(b"RX:FREQOFFset:PPM?",        ScpiOtn.getRxFreqOffsetPpm),
    Cmnd(b"RX:FREQOFFset:HZ?",         ScpiOtn.getRxFreqOffsetHz),

    Cmnd(b"RX:INTerface?",             ScpiOtn.getRxInterface),
    Cmnd(b"RX:INTerface",              ScpiOtn.setRxInterface),
    Cmnd(b"RX:MAPping?",               ScpiOtn.getRxMapping),
    Cmnd(b"RX:MAPping",                ScpiOtn.setRxMapping),
    Cmnd(b"RX:MCPATT?",                ScpiOtn.getRxMultiChanPattern),
    Cmnd(b"RX:MCPATT",                 ScpiOtn.setRxMultiChanPattern),
    Cmnd(b"RX:ODUPM?",                 ScpiOtn.getRxOduPm),
    Cmnd(b"RX:ODUPM",                  ScpiOtn.setRxOduPm),

    Cmnd(b"RX:OH:TCM1:BEI?",           ScpiOtn.rxOhTcm1Bei),
    Cmnd(b"RX:OH:TCM1:BIP8?",          ScpiOtn.rxOhTcm1Bip8),
    Cmnd(b"RX:OH:TCM1:DAPIEXP?",       ScpiOtn.rxOhTcm1DapiExp),
    Cmnd(b"RX:OH:TCM1:DAPI?",          ScpiOtn.rxOhTcm1Dapi),
    Cmnd(b"RX:OH:TCM1:SAPIEXP?",       ScpiOtn.rxOhTcm1SapiExp),
    Cmnd(b"RX:OH:TCM1:SAPI?",          ScpiOtn.rxOhTcm1Sapi),
    Cmnd(b"RX:OH:TCM1:SPECIFIC?",      ScpiOtn.rxOhTcm1Specific),
    Cmnd(b"RX:OH:TCM1:TTI?",           ScpiOtn.rxOhTcm1Tti),
    Cmnd(b"RX:OH:TCM2:BEI?",           ScpiOtn.rxOhTcm2Bei),
    Cmnd(b"RX:OH:TCM2:BIP8?",          ScpiOtn.rxOhTcm2Bip8),
    Cmnd(b"RX:OH:TCM2:DAPIEXP?",       ScpiOtn.rxOhTcm2DapiExp),
    Cmnd(b"RX:OH:TCM2:DAPI?",          ScpiOtn.rxOhTcm2Dapi),
    Cmnd(b"RX:OH:TCM2:SAPIEXP?",       ScpiOtn.rxOhTcm2SapiExp),
    Cmnd(b"RX:OH:TCM2:SAPI?",          ScpiOtn.rxOhTcm2Sapi),
    Cmnd(b"RX:OH:TCM2:SPECIFIC?",      ScpiOtn.rxOhTcm2Specific),
    Cmnd(b"RX:OH:TCM2:TTI?",           ScpiOtn.rxOhTcm2Tti),
    Cmnd(b"RX:OH:TCM3:BEI?",           ScpiOtn.rxOhTcm3Bei),
    Cmnd(b"RX:OH:TCM3:BIP8?",          ScpiOtn.rxOhTcm3Bip8),
    Cmnd(b"RX:OH:TCM3:DAPIEXP?",       ScpiOtn.rxOhTcm3DapiExp),
    Cmnd(b"RX:OH:TCM3:DAPI?",          ScpiOtn.rxOhTcm3Dapi),
    Cmnd(b"RX:OH:TCM3:SAPIEXP?",       ScpiOtn.rxOhTcm3SapiExp),
    Cmnd(b"RX:OH:TCM3:SAPI?",          ScpiOtn.rxOhTcm3Sapi),
    Cmnd(b"RX:OH:TCM3:SPECIFIC?",      ScpiOtn.rxOhTcm3Specific),
    Cmnd(b"RX:OH:TCM3:TTI?",           ScpiOtn.rxOhTcm3Tti),
    Cmnd(b"RX:OH:TCM4:BEI?",           ScpiOtn.rxOhTcm4Bei),
    Cmnd(b"RX:OH:TCM4:BIP8?",          ScpiOtn.rxOhTcm4Bip8),
    Cmnd(b"RX:OH:TCM4:DAPIEXP?",       ScpiOtn.rxOhTcm4DapiExp),
    Cmnd(b"RX:OH:TCM4:DAPI?",          ScpiOtn.rxOhTcm4Dapi),
    Cmnd(b"RX:OH:TCM4:SAPIEXP?",       ScpiOtn.rxOhTcm4SapiExp),
    Cmnd(b"RX:OH:TCM4:SAPI?",          ScpiOtn.rxOhTcm4Sapi),
    Cmnd(b"RX:OH:TCM4:SPECIFIC?",      ScpiOtn.rxOhTcm4Specific),
    Cmnd(b"RX:OH:TCM4:TTI?",           ScpiOtn.rxOhTcm4Tti),
    Cmnd(b"RX:OH:TCM5:BEI?",           ScpiOtn.rxOhTcm5Bei),
    Cmnd(b"RX:OH:TCM5:BIP8?",          ScpiOtn.rxOhTcm5Bip8),
    Cmnd(b"RX:OH:TCM5:DAPIEXP?",       ScpiOtn.rxOhTcm5DapiExp),
    Cmnd(b"RX:OH:TCM5:DAPI?",          ScpiOtn.rxOhTcm5Dapi),
    Cmnd(b"RX:OH:TCM5:SAPIEXP?",       ScpiOtn.rxOhTcm5SapiExp),
    Cmnd(b"RX:OH:TCM5:SAPI?",          ScpiOtn.rxOhTcm5Sapi),
    Cmnd(b"RX:OH:TCM5:SPECIFIC?",      ScpiOtn.rxOhTcm5Specific),
    Cmnd(b"RX:OH:TCM5:TTI?",           ScpiOtn.rxOhTcm5Tti),
    Cmnd(b"RX:OH:TCM6:BEI?",           ScpiOtn.rxOhTcm6Bei),
    Cmnd(b"RX:OH:TCM6:BIP8?",          ScpiOtn.rxOhTcm6Bip8),
    Cmnd(b"RX:OH:TCM6:DAPIEXP?",       ScpiOtn.rxOhTcm6DapiExp),
    Cmnd(b"RX:OH:TCM6:DAPI?",          ScpiOtn.rxOhTcm6Dapi),
    Cmnd(b"RX:OH:TCM6:SAPIEXP?",       ScpiOtn.rxOhTcm6SapiExp),
    Cmnd(b"RX:OH:TCM6:SAPI?",          ScpiOtn.rxOhTcm6Sapi),
    Cmnd(b"RX:OH:TCM6:SPECIFIC?",      ScpiOtn.rxOhTcm6Specific),
    Cmnd(b"RX:OH:TCM6:TTI?",           ScpiOtn.rxOhTcm6Tti),
    Cmnd(b"RX:OH:TCM1:SAPIEXP",        ScpiOtn.rxOhTcm1SapiExpt),
    Cmnd(b"RX:OH:TCM1:DAPIEXP",        ScpiOtn.rxOhTcm1DapiExpt),
    Cmnd(b"RX:OH:TCM2:SAPIEXP",        ScpiOtn.rxOhTcm2SapiExpt),
    Cmnd(b"RX:OH:TCM2:DAPIEXP",        ScpiOtn.rxOhTcm2DapiExpt),
    Cmnd(b"RX:OH:TCM3:SAPIEXP",        ScpiOtn.rxOhTcm3SapiExpt),
    Cmnd(b"RX:OH:TCM3:DAPIEXP",        ScpiOtn.rxOhTcm3DapiExpt),
    Cmnd(b"RX:OH:TCM4:SAPIEXP",        ScpiOtn.rxOhTcm4SapiExpt),
    Cmnd(b"RX:OH:TCM4:DAPIEXP",        ScpiOtn.rxOhTcm4DapiExpt),
    Cmnd(b"RX:OH:TCM5:SAPIEXP",        ScpiOtn.rxOhTcm5SapiExpt),
    Cmnd(b"RX:OH:TCM5:DAPIEXP",        ScpiOtn.rxOhTcm5DapiExpt),
    Cmnd(b"RX:OH:TCM6:SAPIEXP",        ScpiOtn.rxOhTcm6SapiExpt),
    Cmnd(b"RX:OH:TCM6:DAPIEXP",        ScpiOtn.rxOhTcm6DapiExpt),

    Cmnd(b"RX:OH:ODU:APS1?",           ScpiOtn.rxOhOdu2Aps1),
    Cmnd(b"RX:OH:ODU:APS2?",           ScpiOtn.rxOhOdu2Aps2),
    Cmnd(b"RX:OH:ODU:APS3?",           ScpiOtn.rxOhOdu2Aps3),
    Cmnd(b"RX:OH:ODU:APS4?",           ScpiOtn.rxOhOdu2Aps4),
    Cmnd(b"RX:OH:ODU:BEI?",            ScpiOtn.rxOhOdu1Bei),
    Cmnd(b"RX:OH:ODU:BFTFL:FAULT?",    ScpiOtn.rxOhOdu1BfFault),
    Cmnd(b"RX:OH:ODU:BFTFL:OI?",       ScpiOtn.rxOhOdu1BfOi),
    Cmnd(b"RX:OH:ODU:BFTFL:OS?",       ScpiOtn.rxOhOdu1BfOs),
    Cmnd(b"RX:OH:ODU:DAPIEXP?",        ScpiOtn.rxOhOdu1DapiExp),
    Cmnd(b"RX:OH:ODU:DAPI?",           ScpiOtn.rxOhOdu1Dapi),
    Cmnd(b"RX:OH:ODU:EXP1?",           ScpiOtn.rxOhOdu2Exp1),
    Cmnd(b"RX:OH:ODU:EXP2?",           ScpiOtn.rxOhOdu2Exp2),
    Cmnd(b"RX:OH:ODU:FFTFL:FAULT?",    ScpiOtn.rxOhOdu1FfFault),
    Cmnd(b"RX:OH:ODU:FFTFL:OI?",       ScpiOtn.rxOhOdu1FfOi),
    Cmnd(b"RX:OH:ODU:FFTFL:OS?",       ScpiOtn.rxOhOdu1FfOs),
    Cmnd(b"RX:OH:ODU:GCC11?",          ScpiOtn.rxOhOdu2Gcc11),
    Cmnd(b"RX:OH:ODU:GCC12?",          ScpiOtn.rxOhOdu2Gcc12),
    Cmnd(b"RX:OH:ODU:GCC21?",          ScpiOtn.rxOhOdu2Gcc21),
    Cmnd(b"RX:OH:ODU:GCC22?",          ScpiOtn.rxOhOdu2Gcc22),
    Cmnd(b"RX:OH:ODU:RES1?",           ScpiOtn.rxOhOdu2Res1),
    Cmnd(b"RX:OH:ODU:RES2?",           ScpiOtn.rxOhOdu2Res2),
    Cmnd(b"RX:OH:ODU:PMANDTCM?",       ScpiOtn.rxOhOdu2Res3),
    Cmnd(b"RX:OH:ODU:RES3?",           ScpiOtn.rxOhOdu2Res3),
    Cmnd(b"RX:OH:ODU:RES4?",           ScpiOtn.rxOhOdu2Res4),
    Cmnd(b"RX:OH:ODU:RES5?",           ScpiOtn.rxOhOdu2Res5),
    Cmnd(b"RX:OH:ODU:RES6?",           ScpiOtn.rxOhOdu2Res6),
    Cmnd(b"RX:OH:ODU:RES7?",           ScpiOtn.rxOhOdu2Res7),
    Cmnd(b"RX:OH:ODU:RES8?",           ScpiOtn.rxOhOdu2Res8),
    Cmnd(b"RX:OH:ODU:RES9?",           ScpiOtn.rxOhOdu2Res9),
    Cmnd(b"RX:OH:ODU:SAPIEXP?",        ScpiOtn.rxOhOdu1SapiExp),
    Cmnd(b"RX:OH:ODU:SAPI?",           ScpiOtn.rxOhOdu1Sapi),
    Cmnd(b"RX:OH:ODU:SPECIFIC?",       ScpiOtn.rxOhOdu1Specific),
    Cmnd(b"RX:OH:ODU:TCMACT?",         ScpiOtn.rxOhOdu2TcmAct),
    Cmnd(b"RX:OH:ODU:SAPIEXP",         ScpiOtn.rxOhOdu1SapiExpt),
    Cmnd(b"RX:OH:ODU:DAPIEXP",         ScpiOtn.rxOhOdu1DapiExpt),

    Cmnd(b"RX:OH:OPU:RES1?",           ScpiOtn.rxOhOpuRes1),
    Cmnd(b"RX:OH:OPU:PSIEXP?",         ScpiOtn.rxOhOpuPsiExp),
    Cmnd(b"RX:OH:OPU:PSIEXP",          ScpiOtn.setOhOpuPsiExp),
    Cmnd(b"RX:OH:OPU:RES3?",           ScpiOtn.rxOhOpuRes3),
    Cmnd(b"RX:OH:OPU:JC1?",            ScpiOtn.rxOhOpuJc1),
    Cmnd(b"RX:OH:OPU:JC2?",            ScpiOtn.rxOhOpuJc2),
    Cmnd(b"RX:OH:OPU:JC3?",            ScpiOtn.rxOhOpuJc3),
    Cmnd(b"RX:OH:OPU:NJO?",            ScpiOtn.rxOhOpuNjo),
    Cmnd(b"RX:OH:OPU:RES5?",           ScpiOtn.rxOhOpuJc1),
    Cmnd(b"RX:OH:OPU:RES6?",           ScpiOtn.rxOhOpuJc2),
    Cmnd(b"RX:OH:OPU:RES7?",           ScpiOtn.rxOhOpuJc3),
    Cmnd(b"RX:OH:OPU:RES8?",           ScpiOtn.rxOhOpuNjo),
    Cmnd(b"RX:OH:OPU:PSI?",            ScpiOtn.rxOhOpuPsi),
    Cmnd(b"RX:OH:OPU:RES2?",           ScpiOtn.rxOhOpuRes2),
    Cmnd(b"RX:OH:OPU:MSI?",            ScpiOtn.rxOhOpuMsi),

    Cmnd(b"RX:OH:OTU:BEI?",            ScpiOtn.rxOhOtuBei),
    Cmnd(b"RX:OH:OTU:BIP8?",           ScpiOtn.rxOhOtuBip8),
    Cmnd(b"RX:OH:OTU:DAPIEXP?",        ScpiOtn.rxOhOtuDapiExp),
    Cmnd(b"RX:OH:OTU:DAPIEXP",         ScpiOtn.rxOhOtuDapiExpt),
    Cmnd(b"RX:OH:OTU:DAPI?",           ScpiOtn.rxOhOtuDapi),
    Cmnd(b"RX:OH:OTU:GCC01?",          ScpiOtn.rxOhOtuGcc1),
    Cmnd(b"RX:OH:OTU:GCC02?",          ScpiOtn.rxOhOtuGcc2),
    Cmnd(b"RX:OH:OTU:OA1:1?",          ScpiOtn.rxOhOtuOa11),
    Cmnd(b"RX:OH:OTU:OA1:2?",          ScpiOtn.rxOhOtuOa12),
    Cmnd(b"RX:OH:OTU:OA1:3?",          ScpiOtn.rxOhOtuOa13),
    Cmnd(b"RX:OH:OTU:OA2:1?",          ScpiOtn.rxOhOtuOa21),
    Cmnd(b"RX:OH:OTU:OA2:2?",          ScpiOtn.rxOhOtuOa22),
    Cmnd(b"RX:OH:OTU:OA2:3?",          ScpiOtn.rxOhOtuOa23),
    Cmnd(b"RX:OH:OTU:RES1?",           ScpiOtn.rxOhOtuRes1),
    Cmnd(b"RX:OH:OTU:RES2?",           ScpiOtn.rxOhOtuRes2),
    Cmnd(b"RX:OH:OTU:SAPIEXP?",        ScpiOtn.rxOhOtuSapiExp),
    Cmnd(b"RX:OH:OTU:SAPIEXP",         ScpiOtn.rxOhOtuSapiExpt),
    Cmnd(b"RX:OH:OTU:SAPI?",           ScpiOtn.rxOhOtuSapi),
    Cmnd(b"RX:OH:OTU:SPECIFIC?",       ScpiOtn.rxOhOtuSpecific),
    Cmnd(b"RX:OH:OTU:TTI?",            ScpiOtn.rxOhOtuTti),

    Cmnd(b"RX:OPP?",                   ScpiOtn.getRxOptPwr),
    Cmnd(b"RX:OPUJUST?",               ScpiOtn.getRxOpuJustLevel),
    Cmnd(b"RX:OPUPLM?",                ScpiOtn.getRxOpuPlm),
    Cmnd(b"RX:OPUPLM",                 ScpiOtn.setRxOpuPlm),
    Cmnd(b"RX:OPUTHRESHold?",          ScpiOtn.getOpuFreqThreshhold),
    Cmnd(b"RX:OPUTHRESHold",           ScpiOtn.setOpuFreqThreshhold),
    Cmnd(b"RX:OTUCN?",                 ScpiOtn.getOTUCn),
    Cmnd(b"RX:OTUCN",                  ScpiOtn.setOTUCn),
    Cmnd(b"RX:OTUSM?",                 ScpiOtn.getRxOtuSm),
    Cmnd(b"RX:OTUSM",                  ScpiOtn.setRxOtuSm),
    Cmnd(b"RX:OUTTHRESHold?",          ScpiOtn.getRxFreqThreshhold),
    Cmnd(b"RX:OUTTHRESHold",           ScpiOtn.setRxFreqThreshhold),

    Cmnd(b"RX:PATTern?",               ScpiOtn.getRxPattern),
    Cmnd(b"RX:PATTern",                ScpiOtn.setRxPattern),
    Cmnd(b"RX:PWRLOWT?",               ScpiOtn.getRxPowLowThreshhold),
    Cmnd(b"RX:PWRLOWT",                ScpiOtn.setRxPowLowThreshhold),
    Cmnd(b"RX:SCRAMBLE?",              ScpiOtn.getRxScramble),
    Cmnd(b"RX:SCRAMBLE",               ScpiOtn.setRxScramble),
    Cmnd(b"RX:TCM1?",                  ScpiOtn.getRxTcm1),
    Cmnd(b"RX:TCM1",                   ScpiOtn.setRxTcm1),
    Cmnd(b"RX:TCM2?",                  ScpiOtn.getRxTcm2),
    Cmnd(b"RX:TCM2",                   ScpiOtn.setRxTcm2),
    Cmnd(b"RX:TCM3?",                  ScpiOtn.getRxTcm3),
    Cmnd(b"RX:TCM3",                   ScpiOtn.setRxTcm3),
    Cmnd(b"RX:TCM4?",                  ScpiOtn.getRxTcm4),
    Cmnd(b"RX:TCM4",                   ScpiOtn.setRxTcm4),
    Cmnd(b"RX:TCM5?",                  ScpiOtn.getRxTcm5),
    Cmnd(b"RX:TCM5",                   ScpiOtn.setRxTcm5),
    Cmnd(b"RX:TCM6?",                  ScpiOtn.getRxTcm6),
    Cmnd(b"RX:TCM6",                   ScpiOtn.setRxTcm6),
    Cmnd(b"RX:TRIG?",                  ScpiOtn.getRxTrigger),
    Cmnd(b"RX:TRIG",                   ScpiOtn.setRxTrigger),

    Cmnd(b"RES:AL:LOF?",               ScpiOtn.getResLofLed),
    Cmnd(b"RES:AL:LOS?",               ScpiOtn.getResLosLed),
    Cmnd(b"RES:AL:LOM?",               ScpiOtn.getResLomLed),
    Cmnd(b"RES:AL:LOOMFI?",            ScpiOtn.getResLoomfiLed),
    Cmnd(b"RES:AL:ODUAIS?",            ScpiOtn.getResOduAisLed),
    Cmnd(b"RES:AL:ODUBDI?",            ScpiOtn.getResOduBdiLed),
    Cmnd(b"RES:AL:ODULCK?",            ScpiOtn.getResOduLckLed),
    Cmnd(b"RES:AL:ODUOCI?",            ScpiOtn.getResOduOciLed),
    Cmnd(b"RES:AL:OOF?",               ScpiOtn.getResOofLed),
    Cmnd(b"RES:AL:OOM?",               ScpiOtn.getResOomLed),
    Cmnd(b"RES:AL:OOOMFI?",            ScpiOtn.getResOoomfiLed),
    Cmnd(b"RES:AL:OPUAIS?",            ScpiOtn.getResOpuAisLed),
    Cmnd(b"RES:AL:OPUCMSYNC?",         ScpiOtn.getResOpuC8SyncLed),
    Cmnd(b"RES:AL:OPUCSF?",            ScpiOtn.getResOpuCsfLed),
    Cmnd(b"RES:AL:OPUFREQWIDE?",       ScpiOtn.getResOpuFreWideLed),
    Cmnd(b"RES:AL:OPUPLM?",            ScpiOtn.getResOpuPlmLed),
    Cmnd(b"RES:AL:OTUAIS?",            ScpiOtn.getResOtuAisLed),
    Cmnd(b"RES:AL:OTUBDI?",            ScpiOtn.getResOtuBdiLed),
    Cmnd(b"RES:AL:OTUBIAE?",           ScpiOtn.getResOtuBiaeLed),
    Cmnd(b"RES:AL:OTUIAE?",            ScpiOtn.getResOtuIaeLed),
    Cmnd(b"RES:AL:PATsync?",           ScpiOtn.getResPatSynLed),
    Cmnd(b"RES:AL:PAUSED?",            ScpiOtn.getResPausedLed),
    Cmnd(b"RES:AL:TCM1BDI?",           ScpiOtn.getResTcm1BdLed),
    Cmnd(b"RES:AL:TCM1BIAE?",          ScpiOtn.getResTcm1BiaeLed),
    Cmnd(b"RES:AL:TCM2BDI?",           ScpiOtn.getResTcm2BdLed),
    Cmnd(b"RES:AL:TCM2BIAE?",          ScpiOtn.getResTcm2BiaeLed),
    Cmnd(b"RES:AL:TCM3BDI?",           ScpiOtn.getResTcm3BdLed),
    Cmnd(b"RES:AL:TCM3BIAE?",          ScpiOtn.getResTcm3BiaeLed),
    Cmnd(b"RES:AL:TCM4BDI?",           ScpiOtn.getResTcm4BdLed),
    Cmnd(b"RES:AL:TCM4BIAE?",          ScpiOtn.getResTcm4BiaeLed),
    Cmnd(b"RES:AL:TCM5BDI?",           ScpiOtn.getResTcm5BdLed),
    Cmnd(b"RES:AL:TCM5BIAE?",          ScpiOtn.getResTcm5BiaeLed),
    Cmnd(b"RES:AL:TCM6BDI?",           ScpiOtn.getResTcm6BdLed),
    Cmnd(b"RES:AL:TCM6BIAE?",          ScpiOtn.getResTcm6BiaeLed),
    Cmnd(b"RES:BIT:AVE?",              ScpiOtn.bitAvgErrRate),
    Cmnd(b"RES:BIT:COUNt?",            ScpiOtn.bitErrCount),
    Cmnd(b"RES:BIT:RATe?",             ScpiOtn.bitErrRate),
    Cmnd(b"RES:CLOCK:Secs?",           ScpiOtn.getResClockAlrm),
    Cmnd(b"RES:CMCRC8:AVE?",           ScpiOtn.c8Crc8AvgErrRate),
    Cmnd(b"RES:CMCRC8:COUNt?",         ScpiOtn.c8Crc8ErrCount),
    Cmnd(b"RES:CMCRC8:RATe?",          ScpiOtn.c8Crc8ErrRate),
    Cmnd(b"RES:CPPOWERLOSS:Secs?",     ScpiOtn.resPowerSecs),

    Cmnd(b"RES:EVENTLOG",              ScpiOtn.getEventLog),
    Cmnd(b"RES:FEC:CORR:AVE?",         ScpiOtn.fecCorrAvgErrRate),
    Cmnd(b"RES:FEC:CORR:COUNt?",       ScpiOtn.fecCorrErrCount),
    Cmnd(b"RES:FEC:CORR:RATe?",        ScpiOtn.fecCorrErrRate),
    Cmnd(b"RES:FEC:UNCORR:AVE?",       ScpiOtn.fecUncAvgErrRate),
    Cmnd(b"RES:FEC:UNCORR:COUNt?",     ScpiOtn.fecUncErrCount),
    Cmnd(b"RES:FEC:UNCORR:RATe?",      ScpiOtn.fecUncErrRate),
    Cmnd(b"RES:FRAME:AVE?",            ScpiOtn.frameAvgErrRate),
    Cmnd(b"RES:FRAME:COUNt?",          ScpiOtn.frameErrCount),
    Cmnd(b"RES:FRAME:RATe?",           ScpiOtn.frameErrRate),
    Cmnd(b"RES:FREQWIDE:Secs?",        ScpiOtn.getResFreWideAlrm),
    Cmnd(b"RES:JUSTification:Secs?",   ScpiOtn.getResPjcsCount),
    Cmnd(b"RES:LAN:1027BBLOCK:AVE?",   ScpiOtn.lan1027bBlockAvgErrRate),
    Cmnd(b"RES:LAN:1027BBLOCK:COUNt?", ScpiOtn.lan1027bBlockErrCount),
    Cmnd(b"RES:LAN:1027BBLOCK:RATe?",  ScpiOtn.lan1027bBlockErrRate),
    Cmnd(b"RES:LAN0:OTNBIP8:AVE?",     ScpiOtn.lan0OtnBip8AvgErrRate),
    Cmnd(b"RES:LAN0:OTNBIP8:COUNt?",   ScpiOtn.lan0OtnBip8ErrCount),
    Cmnd(b"RES:LAN0:OTNBIP8:RATe?",    ScpiOtn.lan0OtnBip8ErrRate),
    Cmnd(b"RES:LAN1:OTNBIP8:AVE?",     ScpiOtn.lan1OtnBip8AvgErrRate),
    Cmnd(b"RES:LAN1:OTNBIP8:COUNt?",   ScpiOtn.lan1OtnBip8ErrCount),
    Cmnd(b"RES:LAN1:OTNBIP8:RATe?",    ScpiOtn.lan1OtnBip8ErrRate),
    Cmnd(b"RES:LAN2:OTNBIP8:AVE?",     ScpiOtn.lan2OtnBip8AvgErrRate),
    Cmnd(b"RES:LAN2:OTNBIP8:COUNt?",   ScpiOtn.lan2OtnBip8ErrCount),
    Cmnd(b"RES:LAN2:OTNBIP8:RATe?",    ScpiOtn.lan2OtnBip8ErrRate),
    Cmnd(b"RES:LAN3:OTNBIP8:AVE?",     ScpiOtn.lan3OtnBip8AvgErrRate),
    Cmnd(b"RES:LAN3:OTNBIP8:COUNt?",   ScpiOtn.lan3OtnBip8ErrCount),
    Cmnd(b"RES:LAN3:OTNBIP8:RATe?",    ScpiOtn.lan3OtnBip8ErrRate),
    Cmnd(b"RES:LAN0:PCSBIP8:AVE?",     ScpiOtn.lan0PcsBip8AvgErrRate),
    Cmnd(b"RES:LAN0:PCSBIP8:COUNt?",   ScpiOtn.lan0PcsBip8ErrCount),
    Cmnd(b"RES:LAN0:PCSBIP8:RATe?",    ScpiOtn.lan0PcsBip8ErrRate),
    Cmnd(b"RES:LAN1:PCSBIP8:AVE?",     ScpiOtn.lan1PcsBip8AvgErrRate),
    Cmnd(b"RES:LAN1:PCSBIP8:COUNt?",   ScpiOtn.lan1PcsBip8ErrCount),
    Cmnd(b"RES:LAN1:PCSBIP8:RATe?",    ScpiOtn.lan1PcsBip8ErrRate),
    Cmnd(b"RES:LAN2:PCSBIP8:AVE?",     ScpiOtn.lan2PcsBip8AvgErrRate),
    Cmnd(b"RES:LAN2:PCSBIP8:COUNt?",   ScpiOtn.lan2PcsBip8ErrCount),
    Cmnd(b"RES:LAN2:PCSBIP8:RATe?",    ScpiOtn.lan2PcsBip8ErrRate),
    Cmnd(b"RES:LAN3:PCSBIP8:AVE?",     ScpiOtn.lan3PcsBip8AvgErrRate),
    Cmnd(b"RES:LAN3:PCSBIP8:COUNt?",   ScpiOtn.lan3PcsBip8ErrCount),
    Cmnd(b"RES:LAN3:PCSBIP8:RATe?",    ScpiOtn.lan3PcsBip8ErrRate),
    Cmnd(b"RES:LOF:Secs?",             ScpiOtn.getResLofAlrm),
    Cmnd(b"RES:LOM:Secs?",             ScpiOtn.getResLomAlrm),
    Cmnd(b"RES:LOOMFI:Secs?",          ScpiOtn.getResLoomfiAlrm),
    Cmnd(b"RES:LOS:Secs?",             ScpiOtn.getResLosAlrm),

    Cmnd(b"RES:MC:SUMmary?",           ScpiOtn.getMultiChanSummary),
    Cmnd(b"RES:MFAS:AVE?",             ScpiOtn.mfasAvgErrRate),
    Cmnd(b"RES:MFAS:COUNt?",           ScpiOtn.mfasErrCount),
    Cmnd(b"RES:MFAS:RATe?",            ScpiOtn.mfasErrRate),
    Cmnd(b"RES:NEGJUSTification:COUN?",ScpiOtn.getResNpjcCount),
    Cmnd(b"RES:ODUAIS:Secs?",          ScpiOtn.getResOduAisAlrm),
    Cmnd(b"RES:ODUBDI:Secs?",          ScpiOtn.getResOduBdiAlrm),
    Cmnd(b"RES:ODUDAPI:Secs?",         ScpiOtn.getResOduDapAlrm),
    Cmnd(b"RES:ODULCK:Secs?",          ScpiOtn.getResOduLckAlrm),
    Cmnd(b"RES:ODUOCI:Secs?",          ScpiOtn.getResOduOciAlrm),
    Cmnd(b"RES:ODUSAPI:Secs?",         ScpiOtn.getResOduSapAlrm),
    Cmnd(b"RES:ODU:BEI:AVE?",          ScpiOtn.oduBeiAvgErrRate),
    Cmnd(b"RES:ODU:BEI:COUNt?",        ScpiOtn.oduBeiErrCount),
    Cmnd(b"RES:ODU:BEI:RATe?",         ScpiOtn.oduBeiErrRate),
    Cmnd(b"RES:ODU:BIP8:AVE?",         ScpiOtn.oduBip8AvgErrRate),
    Cmnd(b"RES:ODU:BIP8:COUNt?",       ScpiOtn.oduBip8ErrCount),
    Cmnd(b"RES:ODU:BIP8:RATe?",        ScpiOtn.oduBip8ErrRate),
    Cmnd(b"RES:OMFI:AVE?",             ScpiOtn.omfiAvgErrRate),
    Cmnd(b"RES:OMFI:COUNt?",           ScpiOtn.omfiErrCount),
    Cmnd(b"RES:OMFI:RATe?",            ScpiOtn.omfiErrRate),
    Cmnd(b"RES:OOF:Secs?",             ScpiOtn.getResOofAlrm),
    Cmnd(b"RES:OOM:Secs?",             ScpiOtn.getResOomAlrm),
    Cmnd(b"RES:OOOMFI:Secs?",          ScpiOtn.getResOoomfiAlrm),
    Cmnd(b"RES:OPUAIS:Secs?",          ScpiOtn.getResOpuAisAlrm),
    Cmnd(b"RES:OPUCMSYNC:Secs?",       ScpiOtn.getResOpuC8SyncAlrm),
    Cmnd(b"RES:OPUCSF:Secs?",          ScpiOtn.getResOpuCsfAlrm),
    Cmnd(b"RES:OPUFREQWIDE:Secs?",     ScpiOtn.getResOpuFreWideAlrm),
    Cmnd(b"RES:OPUPLM:Secs?",          ScpiOtn.getResOpuPlmAlrm),
    Cmnd(b"RES:OTUAIS:Secs?",          ScpiOtn.getResOtuAisAlrm),
    Cmnd(b"RES:OTUBDI:Secs?",          ScpiOtn.getResOtuBdiAlrm),
    Cmnd(b"RES:OTUBIAE:Secs?",         ScpiOtn.getResOtuBiaeAlrm),
    Cmnd(b"RES:OTUDAPI:Secs?",         ScpiOtn.getResOtuDapAlrm),
    Cmnd(b"RES:OTUIAE:Secs?",          ScpiOtn.getResOtuIaeAlrm),
    Cmnd(b"RES:OTUSAPI:Secs?",         ScpiOtn.getResOtuSapAlrm),
    Cmnd(b"RES:OTU:BEI:AVE?",          ScpiOtn.otuBeiAvgErrRate),
    Cmnd(b"RES:OTU:BEI:COUNt?",        ScpiOtn.otuBeiErrCount),
    Cmnd(b"RES:OTU:BEI:RATe?",         ScpiOtn.otuBeiErrRate),
    Cmnd(b"RES:OTU:BIP8:AVE?",         ScpiOtn.otuBip8AvgErrRate),
    Cmnd(b"RES:OTU:BIP8:COUNt?",       ScpiOtn.otuBip8ErrCount),
    Cmnd(b"RES:OTU:BIP8:RATe?",        ScpiOtn.otuBip8ErrRate),
    Cmnd(b"RES:PATsync:Secs?",         ScpiOtn.getResPatSynAlrm),
    Cmnd(b"RES:PAUSED:Secs?",          ScpiOtn.getResPausedAlrm),
    Cmnd(b"RES:POSJUSTification:COUN?",ScpiOtn.getResPpjcCount),
    Cmnd(b"RES:PWRHOT:Secs?",          ScpiOtn.getResPwrHotAlrm),
    Cmnd(b"RES:PWRLOW:Secs?",          ScpiOtn.getResPwrLowAlrm),
    Cmnd(b"RES:PWRWARM:Secs?",         ScpiOtn.getResPwrWarmAlrm),
    Cmnd(b"RES:RTD:FRAME:LAST?",       ScpiOtn.getResApsFrameLast),
    Cmnd(b"RES:RTD:FRAME:MAX?",        ScpiOtn.getResApsFrameMax),
    Cmnd(b"RES:RTD:FRAME:MIN?",        ScpiOtn.getResApsFrameMin),
    Cmnd(b"RES:RTD:STATE?",            ScpiOtn.getResApsState),
    Cmnd(b"RES:RTD:TIME:LAST?",        ScpiOtn.getResApsTimeLast),
    Cmnd(b"RES:RTD:TIME:MAX?",         ScpiOtn.getResApsTimeMax),
    Cmnd(b"RES:RTD:TIME:MIN?",         ScpiOtn.getResApsTimeMin),
    Cmnd(b"RES:RXCMJUST:PLUS1?",       ScpiOtn.getResRxC8Plus1),
    Cmnd(b"RES:RXCMJUST:PLUS2?",       ScpiOtn.getResRxC8Plus2),
    Cmnd(b"RES:RXCMJUST:MINUS1?",      ScpiOtn.getResRxC8Minus1),
    Cmnd(b"RES:RXCMJUST:MINUS2?",      ScpiOtn.getResRxC8Minus2),
    Cmnd(b"RES:RXCMJUST:GTR2?",        ScpiOtn.getResRxC8Gtr2),
    Cmnd(b"RES:RXCMJUST:LT2?",         ScpiOtn.getResRxC8Lt2),
    Cmnd(b"RES:RXCMJUST:GTRITU?",      ScpiOtn.getResRxC8GtrItu),
    Cmnd(b"RES:RXCMJUST:LTITU?",       ScpiOtn.getResRxC8LtItu),
    Cmnd(b"RES:RXCMMAX?",              ScpiOtn.getRxC8Max),
    Cmnd(b"RES:RXCMMIN?",              ScpiOtn.getRxC8Min),

    Cmnd(b"RES:SCANALARMS?",           ScpiOtn.getCurrentAlarms),

    Cmnd(b"RES:SCANERRORS?",           ScpiOtn.getCurrentErrors),
    Cmnd(b"RES:TCM1BDI:Secs?",         ScpiOtn.getResTcm1BdAlrm),
    Cmnd(b"RES:TCM1BIAE:Secs?",        ScpiOtn.getResTcm1BiaeAlrm),
    Cmnd(b"RES:TCM1DAPI:Secs?",        ScpiOtn.getResTcm1DaAlrm),
    Cmnd(b"RES:TCM1SAPI:Secs?",        ScpiOtn.getResTcm1SaAlrm),
    Cmnd(b"RES:TCM1:BEI:AVE?",         ScpiOtn.tcm1BeiAvgErrRate),
    Cmnd(b"RES:TCM1:BEI:COUNt?",       ScpiOtn.tcm1BeiErrCount),
    Cmnd(b"RES:TCM1:BEI:RATe?",        ScpiOtn.tcm1BeiErrRate),
    Cmnd(b"RES:TCM1:BIP8:AVE?",        ScpiOtn.tcm1Bip8AvgErrRate),
    Cmnd(b"RES:TCM1:BIP8:COUNt?",      ScpiOtn.tcm1Bip8ErrCount),
    Cmnd(b"RES:TCM1:BIP8:RATe?",       ScpiOtn.tcm1Bip8ErrRate),
    Cmnd(b"RES:TCM2BDI:Secs?",         ScpiOtn.getResTcm2BdAlrm),
    Cmnd(b"RES:TCM2BIAE:Secs?",        ScpiOtn.getResTcm2BiaeAlrm),
    Cmnd(b"RES:TCM2DAPI:Secs?",        ScpiOtn.getResTcm2DaAlrm),
    Cmnd(b"RES:TCM2SAPI:Secs?",        ScpiOtn.getResTcm2SaAlrm),
    Cmnd(b"RES:TCM2:BEI:AVE?",         ScpiOtn.tcm2BeiAvgErrRate),
    Cmnd(b"RES:TCM2:BEI:COUNt?",       ScpiOtn.tcm2BeiErrCount),
    Cmnd(b"RES:TCM2:BEI:RATe?",        ScpiOtn.tcm2BeiErrRate),
    Cmnd(b"RES:TCM2:BIP8:AVE?",        ScpiOtn.tcm2Bip8AvgErrRate),
    Cmnd(b"RES:TCM2:BIP8:COUNt?",      ScpiOtn.tcm2Bip8ErrCount),
    Cmnd(b"RES:TCM2:BIP8:RATe?",       ScpiOtn.tcm2Bip8ErrRate),
    Cmnd(b"RES:TCM3BDI:Secs?",         ScpiOtn.getResTcm3BdAlrm),
    Cmnd(b"RES:TCM3BIAE:Secs?",        ScpiOtn.getResTcm3BiaeAlrm),
    Cmnd(b"RES:TCM3DAPI:Secs?",        ScpiOtn.getResTcm3DaAlrm),
    Cmnd(b"RES:TCM3SAPI:Secs?",        ScpiOtn.getResTcm3SaAlrm),
    Cmnd(b"RES:TCM3:BEI:AVE?",         ScpiOtn.tcm3BeiAvgErrRate),
    Cmnd(b"RES:TCM3:BEI:COUNt?",       ScpiOtn.tcm3BeiErrCount),
    Cmnd(b"RES:TCM3:BEI:RATe?",        ScpiOtn.tcm3BeiErrRate),
    Cmnd(b"RES:TCM3:BIP8:AVE?",        ScpiOtn.tcm3Bip8AvgErrRate),
    Cmnd(b"RES:TCM3:BIP8:COUNt?",      ScpiOtn.tcm3Bip8ErrCount),
    Cmnd(b"RES:TCM3:BIP8:RATe?",       ScpiOtn.tcm3Bip8ErrRate),
    Cmnd(b"RES:TCM4BDI:Secs?",         ScpiOtn.getResTcm4BdAlrm),
    Cmnd(b"RES:TCM4BIAE:Secs?",        ScpiOtn.getResTcm4BiaeAlrm),
    Cmnd(b"RES:TCM4DAPI:Secs?",        ScpiOtn.getResTcm4DaAlrm),
    Cmnd(b"RES:TCM4SAPI:Secs?",        ScpiOtn.getResTcm4SaAlrm),
    Cmnd(b"RES:TCM4:BEI:AVE?",         ScpiOtn.tcm4BeiAvgErrRate),
    Cmnd(b"RES:TCM4:BEI:COUNt?",       ScpiOtn.tcm4BeiErrCount),
    Cmnd(b"RES:TCM4:BEI:RATe?",        ScpiOtn.tcm4BeiErrRate),
    Cmnd(b"RES:TCM4:BIP8:AVE?",        ScpiOtn.tcm4Bip8AvgErrRate),
    Cmnd(b"RES:TCM4:BIP8:COUNt?",      ScpiOtn.tcm4Bip8ErrCount),
    Cmnd(b"RES:TCM4:BIP8:RATe?",       ScpiOtn.tcm4Bip8ErrRate),
    Cmnd(b"RES:TCM5BDI:Secs?",         ScpiOtn.getResTcm5BdAlrm),
    Cmnd(b"RES:TCM5BIAE:Secs?",        ScpiOtn.getResTcm5BiaeAlrm),
    Cmnd(b"RES:TCM5DAPI:Secs?",        ScpiOtn.getResTcm5DaAlrm),
    Cmnd(b"RES:TCM5SAPI:Secs?",        ScpiOtn.getResTcm5SaAlrm),
    Cmnd(b"RES:TCM5:BEI:AVE?",         ScpiOtn.tcm5BeiAvgErrRate),
    Cmnd(b"RES:TCM5:BEI:COUNt?",       ScpiOtn.tcm5BeiErrCount),
    Cmnd(b"RES:TCM5:BEI:RATe?",        ScpiOtn.tcm5BeiErrRate),
    Cmnd(b"RES:TCM5:BIP8:AVE?",        ScpiOtn.tcm5Bip8AvgErrRate),
    Cmnd(b"RES:TCM5:BIP8:COUNt?",      ScpiOtn.tcm5Bip8ErrCount),
    Cmnd(b"RES:TCM5:BIP8:RATe?",       ScpiOtn.tcm5Bip8ErrRate),
    Cmnd(b"RES:TCM6BDI:Secs?",         ScpiOtn.getResTcm6BdAlrm),
    Cmnd(b"RES:TCM6BIAE:Secs?",        ScpiOtn.getResTcm6BiaeAlrm),
    Cmnd(b"RES:TCM6DAPI:Secs?",        ScpiOtn.getResTcm6DaAlrm),
    Cmnd(b"RES:TCM6SAPI:Secs?",        ScpiOtn.getResTcm6SaAlrm),
    Cmnd(b"RES:TCM6:BEI:AVE?",         ScpiOtn.tcm6BeiAvgErrRate),
    Cmnd(b"RES:TCM6:BEI:COUNt?",       ScpiOtn.tcm6BeiErrCount),
    Cmnd(b"RES:TCM6:BEI:RATe?",        ScpiOtn.tcm6BeiErrRate),
    Cmnd(b"RES:TCM6:BIP8:AVE?",        ScpiOtn.tcm6Bip8AvgErrRate),
    Cmnd(b"RES:TCM6:BIP8:COUNt?",      ScpiOtn.tcm6Bip8ErrCount),
    Cmnd(b"RES:TCM6:BIP8:RATe?",       ScpiOtn.tcm6Bip8ErrRate),
    
    Cmnd(b"RES:TXCMJUST:PLUS1?",       ScpiOtn.getResTxC8Plus1),
    Cmnd(b"RES:TXCMJUST:PLUS2?",       ScpiOtn.getResTxC8Plus2),
    Cmnd(b"RES:TXCMJUST:MINUS1?",      ScpiOtn.getResTxC8Minus1),
    Cmnd(b"RES:TXCMJUST:MINUS2?",      ScpiOtn.getResTxC8Minus2),
    Cmnd(b"RES:TXCMJUST:GTR2?",        ScpiOtn.getResTxC8Gtr2),
    Cmnd(b"RES:TXCMJUST:LT2?",         ScpiOtn.getResTxC8Lt2),
    
    Cmnd(b"RES:TXCMMAX?",              ScpiOtn.getTxC8Max),
    Cmnd(b"RES:TXCMMIN?",              ScpiOtn.getTxC8Min),

    Cmnd(b"SD:ACTION?",                ScpiOtn.getSDState),
    Cmnd(b"SD:ACTION",                 ScpiOtn.setSDAction),
    Cmnd(b"SD:AVGFRAME?",              ScpiOtn.getSDAvgFrame),
    Cmnd(b"SD:AVGTIME?",               ScpiOtn.getSDAvgTime),
    Cmnd(b"SD:CHANnel?",               ScpiOtn.getApsDetail),

    Cmnd(b"SD:CHANnel",                ScpiOtn.setApsDetail),
    Cmnd(b"SD:CRITeria?",              ScpiOtn.getSDCriteria),
    Cmnd(b"SD:CRITeria",               ScpiOtn.setSDCriteria),
    Cmnd(b"SD:CURFRAME?",              ScpiOtn.getSDCurFrame),
    Cmnd(b"SD:CURTIME?",               ScpiOtn.getSDCurTime),
    Cmnd(b"SD:GOODFRAME?",             ScpiOtn.getSDGoodFrame),
    Cmnd(b"SD:GOODFRAME",              ScpiOtn.setSDGoodFrame),
    Cmnd(b"SD:GOODTIME?",              ScpiOtn.getSDGoodTime),
    Cmnd(b"SD:GOODTIME",               ScpiOtn.setSDGoodTime),
    Cmnd(b"SD:MAXFRAME?",              ScpiOtn.getSDMaxFrame),
    Cmnd(b"SD:MAXTIME?",               ScpiOtn.getSDMaxTime),
    Cmnd(b"SD:MINFRAME?",              ScpiOtn.getSDMinFrame),
    Cmnd(b"SD:MINTIME?",               ScpiOtn.getSDMinTime),
    Cmnd(b"SD:ODTULEVEL?",             ScpiOtn.getTxRtdOduLevel),
    Cmnd(b"SD:ODTULEVEL",              ScpiOtn.setTxRtdOduLevel),
    Cmnd(b"SD:RECFRAME?",              ScpiOtn.getSDRecentFrame),
    Cmnd(b"SD:RECTIME?",               ScpiOtn.getSDRecentTime),
    
    Cmnd(b"MODULE:READ?",              ScpiOtn.doModuleSfpRead),
    Cmnd(b"MODULE:WRITE",              ScpiOtn.doModuleSfpWrite),
    Cmnd(b"MODULE:INFO:CONNECTORTYPE?", ScpiOtn.getModuleSfpInfoConnectorType),
    Cmnd(b"MODULE:INFO:DATECODE?",     ScpiOtn.getModuleSfpInfoDateCode),
    Cmnd(b"MODULE:INFO:ENCODING?",     ScpiOtn.getModuleSfpInfoEncoding),
    Cmnd(b"MODULE:INFO:ID?",           ScpiOtn.getModuleSfpInfoModuleId),
    Cmnd(b"MODULE:INFO:LENGTH50UM?",   ScpiOtn.getModuleSfpInfoLength50um),
    Cmnd(b"MODULE:INFO:LENGTH62_5UM?", ScpiOtn.getModuleSfpInfoLength62_5um),
    Cmnd(b"MODULE:INFO:LENGTHOM3?",    ScpiOtn.getModuleSfpInfoLengthOm3),
    Cmnd(b"MODULE:INFO:LENGTHOM4?",    ScpiOtn.getModuleSfpInfoLengthOm4),
    Cmnd(b"MODULE:INFO:LENGTHSMF?",    ScpiOtn.getModuleSfpInfoLengthSmf),
    Cmnd(b"MODULE:INFO:LENGTHSMFKM?",  ScpiOtn.getModuleSfpInfoLengthSmfKm),
    Cmnd(b"MODULE:INFO:NOMRATE?",      ScpiOtn.getModuleSfpInfoNominalRate),
    Cmnd(b"MODULE:INFO:PARTNUMBER?",   ScpiOtn.getModuleSfpInfoPartNumber),
    Cmnd(b"MODULE:INFO:POWERCLASS?",   ScpiOtn.getModuleSfpInfoPower),
    Cmnd(b"MODULE:INFO:PRESENT?",      ScpiOtn.getModuleSfpInfoModulePresent),
    Cmnd(b"MODULE:INFO:RATEIDENTIFIER?", ScpiOtn.getModuleSfpInfoRateIdentifier),
    Cmnd(b"MODULE:INFO:RXPOWER?",      ScpiOtn.getModuleSfpInfoRxPower),
    Cmnd(b"MODULE:INFO:SERIALNUMBER?", ScpiOtn.getModuleSfpInfoSerialNumber),
    Cmnd(b"MODULE:INFO:TXPOWER?",      ScpiOtn.getModuleSfpInfoTxPower),
    Cmnd(b"MODULE:INFO:VENDORNAME?",   ScpiOtn.getModuleSfpInfoVendorName),
    Cmnd(b"MODULE:INFO:VENDOROUI?",    ScpiOtn.getModuleSfpInfoVendorOui),
    Cmnd(b"MODULE:INFO:VENDORREV?",    ScpiOtn.getModuleSfpInfoVendorRev),
    Cmnd(b"MODULE:INFO:WAVELENGTH?",   ScpiOtn.getModuleSfpInfoWavelength),
    
    Cmnd(b"RES:AL:MUXLOF?",            ScpiOtn.getResMuxLofLed),
    Cmnd(b"RES:AL:MUXLOM?",            ScpiOtn.getResMuxLomLed),
    Cmnd(b"RES:AL:MUXODUAIS?",         ScpiOtn.getResMuxOduAisLed),
    Cmnd(b"RES:AL:MUXODUBDI?",         ScpiOtn.getResMuxOduBdiLed),
    Cmnd(b"RES:AL:MUXODUDAPITIM?",     ScpiOtn.getResMuxOduDapLed),
    Cmnd(b"RES:AL:MUXODULCK?",         ScpiOtn.getResMuxOduLckLed),
    Cmnd(b"RES:AL:MUXODUOCI?",         ScpiOtn.getResMuxOduOciLed),
    Cmnd(b"RES:AL:MUXODUSAPITIM?",     ScpiOtn.getResMuxOduSapLed),
    Cmnd(b"RES:AL:MUXOOF?",            ScpiOtn.getResMuxOofLed),
    Cmnd(b"RES:AL:MUXOOM?",            ScpiOtn.getResMuxOomLed),
    Cmnd(b"RES:AL:MUXOPUCMSYNC?",      ScpiOtn.getResMuxOpuC8SyncLed),
    Cmnd(b"RES:AL:MUXOPUCSF?",         ScpiOtn.getResMuxOpuCsfLed),
    Cmnd(b"RES:AL:MUXOPUFREQWIDE?",    ScpiOtn.getResMuxOpuFreWideLed),
    Cmnd(b"RES:AL:MUXOPUPLM?",         ScpiOtn.getResMuxOpuPlmLed),
    Cmnd(b"RES:AL:MUXTCM1BDI?",        ScpiOtn.getResMuxTcm1BdLed),
    Cmnd(b"RES:AL:MUXTCM1BIAE?",       ScpiOtn.getResMuxTcm1BiaeLed),
    Cmnd(b"RES:AL:MUXTCM1DAPITIM?",    ScpiOtn.getResMuxTcm1DaLed),
    Cmnd(b"RES:AL:MUXTCM1SAPITIM?",    ScpiOtn.getResMuxTcm1SaLed),
    Cmnd(b"RES:AL:MUXTCM2BDI?",        ScpiOtn.getResMuxTcm2BdLed),
    Cmnd(b"RES:AL:MUXTCM2BIAE?",       ScpiOtn.getResMuxTcm2BiaeLed),
    Cmnd(b"RES:AL:MUXTCM2DAPITIM?",    ScpiOtn.getResMuxTcm2DaLed),
    Cmnd(b"RES:AL:MUXTCM2SAPITIM?",    ScpiOtn.getResMuxTcm2SaLed),
    Cmnd(b"RES:AL:MUXTCM3BDI?",        ScpiOtn.getResMuxTcm3BdLed),
    Cmnd(b"RES:AL:MUXTCM3BIAE?",       ScpiOtn.getResMuxTcm3BiaeLed),
    Cmnd(b"RES:AL:MUXTCM3DAPITIM?",    ScpiOtn.getResMuxTcm3DaLed),
    Cmnd(b"RES:AL:MUXTCM3SAPITIM?",    ScpiOtn.getResMuxTcm3SaLed),
    Cmnd(b"RES:AL:MUXTCM4BDI?",        ScpiOtn.getResMuxTcm4BdLed),
    Cmnd(b"RES:AL:MUXTCM4BIAE?",       ScpiOtn.getResMuxTcm4BiaeLed),
    Cmnd(b"RES:AL:MUXTCM4DAPITIM?",    ScpiOtn.getResMuxTcm4DaLed),
    Cmnd(b"RES:AL:MUXTCM4SAPITIM?",    ScpiOtn.getResMuxTcm4SaLed),
    Cmnd(b"RES:AL:MUXTCM5BDI?",        ScpiOtn.getResMuxTcm5BdLed),
    Cmnd(b"RES:AL:MUXTCM5BIAE?",       ScpiOtn.getResMuxTcm5BiaeLed),
    Cmnd(b"RES:AL:MUXTCM5DAPITIM?",    ScpiOtn.getResMuxTcm5DaLed),
    Cmnd(b"RES:AL:MUXTCM5SAPITIM?",    ScpiOtn.getResMuxTcm5SaLed),
    Cmnd(b"RES:AL:MUXTCM6BDI?",        ScpiOtn.getResMuxTcm6BdLed),
    Cmnd(b"RES:AL:MUXTCM6BIAE?",       ScpiOtn.getResMuxTcm6BiaeLed),
    Cmnd(b"RES:AL:MUXTCM6DAPITIM?",    ScpiOtn.getResMuxTcm6DaLed),
    Cmnd(b"RES:AL:MUXTCM6SAPITIM?",    ScpiOtn.getResMuxTcm6SaLed),
    Cmnd(b"RES:MUXCMCRC8:AVE?",        ScpiOtn.muxC8Crc8AvgErrRate),
    Cmnd(b"RES:MUXCMCRC8:COUNt?",      ScpiOtn.muxC8Crc8ErrCount),
    Cmnd(b"RES:MUXCMCRC8:RATe?",       ScpiOtn.muxC8Crc8ErrRate),
    Cmnd(b"RES:MUXFRAME:AVE?",         ScpiOtn.muxFrameAvgErrRate),
    Cmnd(b"RES:MUXFRAME:COUNt?",       ScpiOtn.muxFrameErrCount),
    Cmnd(b"RES:MUXFRAME:RATe?",        ScpiOtn.muxFrameErrRate),
    Cmnd(b"RES:MUXLOF:SECS?",          ScpiOtn.getResMuxLofAlrm),
    Cmnd(b"RES:MUXLOM:SECS?",          ScpiOtn.getResMuxLomAlrm),
    Cmnd(b"RES:MUXMFAS:AVE?",          ScpiOtn.muxMfasAvgErrRate),
    Cmnd(b"RES:MUXMFAS:COUNt?",        ScpiOtn.muxMfasErrCount),
    Cmnd(b"RES:MUXMFAS:RATe?",         ScpiOtn.muxMfasErrRate),
    Cmnd(b"RES:MUXODU:BEI:AVE?",       ScpiOtn.muxOduBeiAvgErrRate),
    Cmnd(b"RES:MUXODU:BEI:COUNt?",     ScpiOtn.muxOduBeiErrCount),
    Cmnd(b"RES:MUXODU:BEI:RATe?",      ScpiOtn.muxOduBeiErrRate),
    Cmnd(b"RES:MUXODU:BIP8:AVE?",      ScpiOtn.muxOduBip8AvgErrRate),
    Cmnd(b"RES:MUXODU:BIP8:COUNt?",    ScpiOtn.muxOduBip8ErrCount),
    Cmnd(b"RES:MUXODU:BIP8:RATe?",     ScpiOtn.muxOduBip8ErrRate),
    Cmnd(b"RES:MUXODUAIS:SECS?",       ScpiOtn.getResMuxOduAisAlrm),
    Cmnd(b"RES:MUXODUBDI:SECS?",       ScpiOtn.getResMuxOduBdiAlrm),
    Cmnd(b"RES:MUXODUDAPITIM:SECS?",   ScpiOtn.getResMuxOduDaAlrm),
    Cmnd(b"RES:MUXODULCK:SECS?",       ScpiOtn.getResMuxOduLckAlrm),
    Cmnd(b"RES:MUXODUOCI:SECS?",       ScpiOtn.getResMuxOduOciAlrm),
    Cmnd(b"RES:MUXODUSAPITIM:SECS?",   ScpiOtn.getResMuxOduSaAlrm),
    Cmnd(b"RES:MUXOOF:SECS?",          ScpiOtn.getResMuxOofAlrm),
    Cmnd(b"RES:MUXOOM:SECS?",          ScpiOtn.getResMuxOomAlrm),
    Cmnd(b"RES:MUXOPUCMSYNC:SECS?",    ScpiOtn.getResMuxOpuC8SyncAlrm),
    Cmnd(b"RES:MUXOPUCSF:SECS?",       ScpiOtn.getResMuxOpuCsfAlrm),
    Cmnd(b"RES:MUXOPUFREQWIDE:SECS?",  ScpiOtn.getResMuxOpuFreWideAlrm),
    Cmnd(b"RES:MUXOPUJUST:SECS?",      ScpiOtn.getResMuxPjcsCount),
    Cmnd(b"RES:MUXOPUNEGJUST:COUNt?",  ScpiOtn.getResMuxNpjcCount),
    Cmnd(b"RES:MUXOPUPLM:SECS?",       ScpiOtn.getResMuxOpuPlmAlrm),
    Cmnd(b"RES:MUXOPUPOSJUST:COUNt?",  ScpiOtn.getResMuxPpjcCount),
    Cmnd(b"RES:MUXTCM1:BEI:AVE?",      ScpiOtn.tcmMux1BeiAvgErrRate),
    Cmnd(b"RES:MUXTCM1:BEI:COUNt?",    ScpiOtn.tcmMux1BeiErrCount),
    Cmnd(b"RES:MUXTCM1:BEI:RATe?",     ScpiOtn.tcmMux1BeiErrRate),
    Cmnd(b"RES:MUXTCM1:BIP8:AVE?",     ScpiOtn.tcmMux1Bip8AvgErrRate),
    Cmnd(b"RES:MUXTCM1:BIP8:COUNt?",   ScpiOtn.tcmMux1Bip8ErrCount),
    Cmnd(b"RES:MUXTCM1:BIP8:RATe?",    ScpiOtn.tcmMux1Bip8ErrRate),
    Cmnd(b"RES:MUXTCM1BDI:SECS?",      ScpiOtn.getResMuxTcm1BdAlrm),
    Cmnd(b"RES:MUXTCM1BIAE:SECS?",     ScpiOtn.getResMuxTcm1BiaeAlrm),
    Cmnd(b"RES:MUXTCM1DAPITIM:SECS?",  ScpiOtn.getResMuxTcm1DaAlrm),
    Cmnd(b"RES:MUXTCM1SAPITIM:SECS?",  ScpiOtn.getResMuxTcm1SaAlrm),
    Cmnd(b"RES:MUXTCM2:BEI:AVE?",      ScpiOtn.tcmMux2BeiAvgErrRate),
    Cmnd(b"RES:MUXTCM2:BEI:COUNt?",    ScpiOtn.tcmMux2BeiErrCount),
    Cmnd(b"RES:MUXTCM2:BEI:RATe?",     ScpiOtn.tcmMux2BeiErrRate),
    Cmnd(b"RES:MUXTCM2:BIP8:AVE?",     ScpiOtn.tcmMux2Bip8AvgErrRate),
    Cmnd(b"RES:MUXTCM2:BIP8:COUNt?",   ScpiOtn.tcmMux2Bip8ErrCount),
    Cmnd(b"RES:MUXTCM2:BIP8:RATe?",    ScpiOtn.tcmMux2Bip8ErrRate),
    Cmnd(b"RES:MUXTCM2BDI:SECS?",      ScpiOtn.getResMuxTcm2BdAlrm),
    Cmnd(b"RES:MUXTCM2BIAE:SECS?",     ScpiOtn.getResMuxTcm2BiaeAlrm),
    Cmnd(b"RES:MUXTCM2DAPITIM:SECS?",  ScpiOtn.getResMuxTcm2DaAlrm),
    Cmnd(b"RES:MUXTCM2SAPITIM:SECS?",  ScpiOtn.getResMuxTcm2SaAlrm),
    Cmnd(b"RES:MUXTCM3:BEI:AVE?",      ScpiOtn.tcmMux3BeiAvgErrRate),
    Cmnd(b"RES:MUXTCM3:BEI:COUNt?",    ScpiOtn.tcmMux3BeiErrCount),
    Cmnd(b"RES:MUXTCM3:BEI:RATe?",     ScpiOtn.tcmMux3BeiErrRate),
    Cmnd(b"RES:MUXTCM3:BIP8:AVE?",     ScpiOtn.tcmMux3Bip8AvgErrRate),
    Cmnd(b"RES:MUXTCM3:BIP8:COUNt?",   ScpiOtn.tcmMux3Bip8ErrCount),
    Cmnd(b"RES:MUXTCM3:BIP8:RATe?",    ScpiOtn.tcmMux3Bip8ErrRate),
    Cmnd(b"RES:MUXTCM3BDI:SECS?",      ScpiOtn.getResMuxTcm3BdAlrm),
    Cmnd(b"RES:MUXTCM3BIAE:SECS?",     ScpiOtn.getResMuxTcm3BiaeAlrm),
    Cmnd(b"RES:MUXTCM3DAPITIM:SECS?",  ScpiOtn.getResMuxTcm3DaAlrm),
    Cmnd(b"RES:MUXTCM3SAPITIM:SECS?",  ScpiOtn.getResMuxTcm3SaAlrm),
    Cmnd(b"RES:MUXTCM4:BEI:AVE?",      ScpiOtn.tcmMux4BeiAvgErrRate),
    Cmnd(b"RES:MUXTCM4:BEI:COUNt?",    ScpiOtn.tcmMux4BeiErrCount),
    Cmnd(b"RES:MUXTCM4:BEI:RATe?",     ScpiOtn.tcmMux4BeiErrRate),
    Cmnd(b"RES:MUXTCM4:BIP8:AVE?",     ScpiOtn.tcmMux4Bip8AvgErrRate),
    Cmnd(b"RES:MUXTCM4:BIP8:COUNt?",   ScpiOtn.tcmMux4Bip8ErrCount),
    Cmnd(b"RES:MUXTCM4:BIP8:RATe?",    ScpiOtn.tcmMux4Bip8ErrRate),
    Cmnd(b"RES:MUXTCM4BDI:SECS?",      ScpiOtn.getResMuxTcm4BdAlrm),
    Cmnd(b"RES:MUXTCM4BIAE:SECS?",     ScpiOtn.getResMuxTcm4BiaeAlrm),
    Cmnd(b"RES:MUXTCM4DAPITIM:SECS?",  ScpiOtn.getResMuxTcm4DaAlrm),
    Cmnd(b"RES:MUXTCM4SAPITIM:SECS?",  ScpiOtn.getResMuxTcm4SaAlrm),
    Cmnd(b"RES:MUXTCM5:BEI:AVE?",      ScpiOtn.tcmMux5BeiAvgErrRate),
    Cmnd(b"RES:MUXTCM5:BEI:COUNt?",    ScpiOtn.tcmMux5BeiErrCount),
    Cmnd(b"RES:MUXTCM5:BEI:RATe?",     ScpiOtn.tcmMux5BeiErrRate),
    Cmnd(b"RES:MUXTCM5:BIP8:AVE?",     ScpiOtn.tcmMux5Bip8AvgErrRate),
    Cmnd(b"RES:MUXTCM5:BIP8:COUNt?",   ScpiOtn.tcmMux5Bip8ErrCount),
    Cmnd(b"RES:MUXTCM5:BIP8:RATe?",    ScpiOtn.tcmMux5Bip8ErrRate),
    Cmnd(b"RES:MUXTCM5BDI:SECS?",      ScpiOtn.getResMuxTcm5BdAlrm),
    Cmnd(b"RES:MUXTCM5BIAE:SECS?",     ScpiOtn.getResMuxTcm5BiaeAlrm),
    Cmnd(b"RES:MUXTCM5DAPITIM:SECS?",  ScpiOtn.getResMuxTcm5DaAlrm),
    Cmnd(b"RES:MUXTCM5SAPITIM:SECS?",  ScpiOtn.getResMuxTcm5SaAlrm),
    Cmnd(b"RES:MUXTCM6:BEI:AVE?",      ScpiOtn.tcmMux6BeiAvgErrRate),
    Cmnd(b"RES:MUXTCM6:BEI:COUNt?",    ScpiOtn.tcmMux6BeiErrCount),
    Cmnd(b"RES:MUXTCM6:BEI:RATe?",     ScpiOtn.tcmMux6BeiErrRate),
    Cmnd(b"RES:MUXTCM6:BIP8:AVE?",     ScpiOtn.tcmMux6Bip8AvgErrRate),
    Cmnd(b"RES:MUXTCM6:BIP8:COUNt?",   ScpiOtn.tcmMux6Bip8ErrCount),
    Cmnd(b"RES:MUXTCM6:BIP8:RATe?",    ScpiOtn.tcmMux6Bip8ErrRate),
    Cmnd(b"RES:MUXTCM6BDI:SECS?",      ScpiOtn.getResMuxTcm6BdAlrm),
    Cmnd(b"RES:MUXTCM6BIAE:SECS?",     ScpiOtn.getResMuxTcm6BiaeAlrm),
    Cmnd(b"RES:MUXTCM6DAPITIM:SECS?",  ScpiOtn.getResMuxTcm6DaAlrm),
    Cmnd(b"RES:MUXTCM6SAPITIM:SECS?",  ScpiOtn.getResMuxTcm6SaAlrm),
    ]



# This converts the above table into a tree of lists that can be searched
# for commands. Doing this here and not in the class init means it is done
# once at boot and not at the start of each user session.
commandTreeRoot = []
ParseUtils.processCommandTableIntoTree(commandTable, commandTreeRoot)


if __name__ == "__main__":
    pass

