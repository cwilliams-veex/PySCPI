###############################################################################
#
# Copyright 2018-2019, VeEX, Inc.
# All Rights Reserved.
#
# $Workfile:   SessionGlobals.py  $
# $Revision: 20669 $
# $Author: patrickellis $
# $Date: 2019-10-22 20:17:56 -0400 (Tue, 22 Oct 2019) $
#
# DESCRIPTION:
#    Module to process SCPI commands, provided as Bytes strings.
#
###############################################################################

from ErrorCodes import ErrorQueue

class AutoLoginSettings(object):
    '''This class contains the autologin settings. pickle is then used to 
    store them to a file.
    '''

    def __init__(self):
        self.enabled  = False  # True or False for enabled/disabled
        self.username = b""    # Username if enabled
        self.password = b""    # Password if enabled


class SessionGlobals(object):
    '''This class contains session specific global variables.
    '''

    def __init__(self, sessionType, sessionId, ipAddress):
        self.sessionType    = sessionType # Socket type (ie "TCP", "SSL", etc).
        self.sessionId      = sessionId   # ID number of this session
        self.ipAddress      = ipAddress   # TCP/IP address of protobufServer
        self.userName       = b""    # user name that was logged in.
        self.veexChassis    = None   # veexapi object from login
        self.veexProtocol   = None   # veexapi object set by INST command
        self.veexPhy        = None   # veexapi object set by INST command
        self.veexPcs        = None   # veexapi object set by INST command
        self.veexOtl        = None   # veexapi object set by INST command
        self.veexOtn        = None   # veexapi object set by INST command
        self.veexSonetSdh   = None   # veexapi object set by INST command
        self.veexGfp        = None   # veexapi object set by INST command
        self.veexEthernet   = None   # veexapi object set by INST command
        self.veexFibreChan  = None   # veexapi object set by INST command
        self.protocolType   = None   # Which SCPI branch selected by INST
        self.respondAlways  = False  # Setting of SYST:RESP <ALWAYS|STANDARD>
        self.forceLock      = False  # Setting of SYST:LOCK:FORCED <ON|OFF>
        self.legacyResponse = False  # Setting of SYST:LEGACYR <TRUE|FALSE>
        self.autoLogin      = AutoLoginSettings()  # object from above
        self.errorQueue     = ErrorQueue()         # FIFO queue object
        self.chassisIpAddress   = b""   # Used when setting chassis network
        self.chassisSubnetMask  = b""   # Used when setting chassis network
        self.chassisDefRouter   = b""   # Used when setting chassis network
        self.chassisDnsAddress1 = b""   # Used when setting chassis network
        self.chassisDnsAddress2 = b""   # Used when setting chassis network
        #self.ppMode         = None   # C++ SCPI enum ePpMode g_ppMode;

