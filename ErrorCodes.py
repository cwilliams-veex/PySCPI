###############################################################################
#
# Copyright 2018-2019, VeEX, Inc.
# All Rights Reserved.
#
# $Workfile:   ErrorCodes.py  $
# $Revision: 21493 $
# $Author: patrickellis $
# $Date: 2020-04-08 15:00:55 -0400 (Wed, 08 Apr 2020) $
#
# DESCRIPTION:
#    Module with SCPI error code integer enum constants and functions to
#    convert them to text.
#
###############################################################################

from collections import deque
from enum import IntEnum

# Simple exception to handle signals.
class TcpipServerExit(Exception):
    pass

# An enum list of all the error codes.
class ScpiErrorCode(IntEnum):
    DLI_NO_ERROR                            = 0

    # Common
    DLI_OBJ_NOT_INITIALIZED                 = 101
    DLI_FILE_IO_FAIL                        = 102
    DLI_INSUFFICIENT_MEMORY                 = 103
    DLI_USER_UNAUTHORIZED                   = 104
    DLI_INVALID_PP_INDEX                    = 105
    DLI_OUT_OF_SERVICE                      = 106
    DLI_LICENSE_EXPIRED                     = 107
    DLI_NOT_SUPPORTED_BY_HW                 = 108

    # AccountManager
    DLI_ADMIN_USER_NOT_FOUND                = 201
    DLI_ADMIN_USER_NOT_LOGGED_IN            = 202
    DLI_ADMIN_FAIL_ADD_USER                 = 203
    DLI_ADMIN_FAIL_DEL_USER                 = 204
    DLI_ADMIN_FAIL_USER_LOCK                = 205
    DLI_ADMIN_INVALID_LOGIN_NAME            = 206
    DLI_ADMIN_INVALID_PASSWORD              = 207
    DLI_ADMIN_USER_CANNOT_MODIFY_PRIVIL     = 208
    DLI_ADMIN_REACHED_MAX_LOGGEDIN_USERS    = 209
    DLI_ADMIN_UPGRADE_IN_PROGRESS           = 210
    DLI_ADMIN_USER_ALREADY_LOGGED_IN        = 211

    #  SystemConfig
    DLI_SYS_INIT_FAIL                       = 301
    DLI_SYS_REBOOT_FAIL                     = 302
    DLI_SYS_INVALID_TID                     = 303
    DLI_SYS_SETTCPIPCONFIG_FAIL             = 304
    DLI_SYS_SETASYNCCONFIG_FAIL             = 305
    DLI_SYS_INVALID_ASYNC_PARAM             = 306
    DLI_SYS_CPLD_FAIL                       = 307
    DLI_SYS_INVALID_CPLD_DATA               = 308
    DLI_SYS_INVALID_DATE_TIME               = 309
    DLI_SYS_SERIAL_PORT_BUSY                = 310
    DLI_SYS_SOUND_CARD_FAIL                 = 311
    DLI_SYS_INVALID_GPIB_ADDR               = 312
    DLI_INVALID_LICENSE                     = 313

    # DataManager
    DLI_DATAMGR_INDEX_OUTOF_RANGE           = 401

    # Protocol Handler
    DLI_PROTOMGR_INVALID_PP_TYPE            = 501
    DLI_PROTOMGR_INVALID_ANY_TYPE           = 502
    DLI_PROTOMGR_INVALID_COMMAND_TYPE       = 503
    DLI_PROTOMGR_INVALID_PRESET_COMMAND     = 504
    DLI_PROTOMGR_TESTUNIT_ACTIVE            = 505
    DLI_PROTOMGR_TESTUNIT_LOCKED            = 506
    DLI_PROTOMGR_USERID_NOTFOUND            = 507
    DLI_INVALID_PP_MODE                     = 508
    DLI_PP_NOT_PRESENT                      = 509

    # TestManager
    DLI_INVALID_TESTUNITID                  = 601
    DLI_INVALID_TESTID                      = 602
    DLI_INVALID_LOCK                        = 603

    # Database
    DLI_RECORD_NOT_FOUND                    = 701
    DLI_DUPLICATE_RECORD                    = 702

    # Additions
    DLI_INVALID_REGISTRY_KEY                = 800
    DLI_INVALID_REGISTRY_ENTRY              = 801
    DLI_INCOMPATIBLE_VERSIONS               = 802
    DLI_FAILED_TO_BIND_TO_CORBA             = 803
    DLI_INVALID_IP_ADDRESS                  = 804

    # CATCH-ALL DLI ERROR
    DLI_INTERNAL_UNHANDLED_ERROR            = 900

    # FOR ATM ONLY.
    INVALID_SCRAMBL                         = 901
    INVALID_UOM                             = 902
    INVALID_FOR_CUR_SCOPE                   = 903
    INVALID_FOR_CUR_SETTING                 = 904
    INVALID_ALARM_TYPE                      = 905
    INVALID_ERROR_TYPE                      = 906
    INVALID_NWIMP_TYPE                      = 907
    INVALID_OAM_TYPE                        = 908
    INVALID_AAL_TYPE                        = 909
    INVALID_TRAF_TYPE                       = 910
    INVALID_RX_STATUS                       = 911
    INVALID_TX_STATUS                       = 912
    INVALID_TOGGLE_TYPE                     = 913
    TX_ALREADY_ON                           = 914
    TX_ALREADY_OFF                          = 915
    RX_ALREADY_ON                           = 916
    RX_ALREADY_OFF                          = 917
    INVALID_TABLE_ENTRY                     = 918
    INVALID_SCOPE                           = 919
    INVALID_PMOAM_BLOCK_SIZE                = 920

    INVALID_INTERFACE                       = 921
    INVALID_MAPPING                         = 922
    INVALID_FRAMING                         = 923
    INVALID_PATTERN                         = 924

    NO_MODIFIED_DATA                        = 925
    INVALID_BGRND_SEQNO                     = 926
    INVALID_FOR_CUR_UNI_VERSION             = 927
    INVALID_SVCTEST_TYPE                    = 928
    INVALID_UNI_VERSION                     = 929
    UNHANDLED_EXCEPTION                     = 930
    INVALID_RESULTS                         = 931
    INVALID_SETTINGS                        = 932
    INVALID_ATM_ADDRESS_FORMAT              = 933
    INVALID_UNI_TIMER                       = 934
    INVALID_QOS_CLASS                       = 935
    INVALID_SIG_FILTER_TYPE                 = 936
    INVALID_CALLREF_FLAG                    = 937
    INVALID_SVC_MSG_TYPE                    = 938
    VCC_ENTRY_NOT_SVC                       = 939
    VCC_ENTRY_NOT_O191                      = 940
    INVALID_O191_FLOW_TYPE                  = 941
    INVALID_QOS_TEST_TYPE                   = 942
    GENERIC_QUERY_ERR                       = 943
    GENERIC_SET_ERR                         = 944

    # ****** SCPI Standard Errors ******

    CMD_ERR                                 = -100
    CMD_WRITE_ERR                           = -101
    DATA_TYPE_ERR                           = -104
    PARAMETER_NOT_ALLOWED                   = -108
    MISSING_PARAM                           = -109
    NUMERIC_DATA_ERR                        = -120

    EXECUTION_ERR                           = -200
    CMD_INVALID_FOR_CRNT_CONFIG             = -203
    INIT_IGNORED                            = -213
    DATA_OUT_OF_RANGE                       = -222

    ILLEGAL_PARAM_VALUE                     = -224
    HARDWARE_MISSING                        = -241

    FILE_NOT_FOUND                          = -256
    SYSTEM_CONTROLLER_EXCEPTION             = -300
    SYSTEM_EXCEPTION                        = -310
    ERROR_QUEUE_OVERFLOW                    = -350

# Dictionary used to translate errorCode to a string.
descriptionTable = {
    ScpiErrorCode.DLI_NO_ERROR:                           b"No error",

    # Common
    ScpiErrorCode.DLI_OBJ_NOT_INITIALIZED:                b"Object not initialized",
    ScpiErrorCode.DLI_FILE_IO_FAIL:                       b"File read/write failed",
    ScpiErrorCode.DLI_INSUFFICIENT_MEMORY:                b"Insufficient memory",
    ScpiErrorCode.DLI_USER_UNAUTHORIZED:                  b"Unauthorized user",
    ScpiErrorCode.DLI_INVALID_PP_INDEX:                   b"Invalid protocol processor index",
    ScpiErrorCode.DLI_OUT_OF_SERVICE:                     b"Out of Service",
    ScpiErrorCode.DLI_LICENSE_EXPIRED:                    b"Timed License Expired",
    ScpiErrorCode.DLI_NOT_SUPPORTED_BY_HW:                b"Not supported by hardware",

    # AccountManager
    ScpiErrorCode.DLI_ADMIN_USER_NOT_FOUND:               b"User not found",
    ScpiErrorCode.DLI_ADMIN_USER_NOT_LOGGED_IN:           b"User not logged-in",
    ScpiErrorCode.DLI_ADMIN_FAIL_ADD_USER:                b"Failed to add user",
    ScpiErrorCode.DLI_ADMIN_FAIL_DEL_USER:                b"Failed to delete user",
    ScpiErrorCode.DLI_ADMIN_FAIL_USER_LOCK:               b"Failed to lock user",
    ScpiErrorCode.DLI_ADMIN_INVALID_LOGIN_NAME:           b"Invalid login name",
    ScpiErrorCode.DLI_ADMIN_INVALID_PASSWORD:             b"Invalid password",
    ScpiErrorCode.DLI_ADMIN_USER_CANNOT_MODIFY_PRIVIL:    b"User cannot modify privilege",
    ScpiErrorCode.DLI_ADMIN_REACHED_MAX_LOGGEDIN_USERS:   b"Maximum logged sessions reached",
    ScpiErrorCode.DLI_ADMIN_UPGRADE_IN_PROGRESS:          b"Upgrade in progress",
    ScpiErrorCode.DLI_ADMIN_USER_ALREADY_LOGGED_IN:       b"User already logged-in",

    #  SystemConfig
    ScpiErrorCode.DLI_SYS_INIT_FAIL:                      b"Failed to initialize system",
    ScpiErrorCode.DLI_SYS_REBOOT_FAIL:                    b"Failed to reboot",
    ScpiErrorCode.DLI_SYS_INVALID_TID:                    b"Invalid test ID",
    ScpiErrorCode.DLI_SYS_SETTCPIPCONFIG_FAIL:            b"Failed to configure TCP configuration",
    ScpiErrorCode.DLI_SYS_SETASYNCCONFIG_FAIL:            b"Failed to configure RS232 configuration",
    ScpiErrorCode.DLI_SYS_INVALID_ASYNC_PARAM:            b"Invalid RS232 configuration parameters",
    ScpiErrorCode.DLI_SYS_CPLD_FAIL:                      b"Failed to CPLD",
    ScpiErrorCode.DLI_SYS_INVALID_CPLD_DATA:              b"Invalid CPLD data",
    ScpiErrorCode.DLI_SYS_INVALID_DATE_TIME:              b"Invalid date-time",
    ScpiErrorCode.DLI_SYS_SERIAL_PORT_BUSY:               b"Serial port is busy",
    ScpiErrorCode.DLI_SYS_SOUND_CARD_FAIL:                b"Sound card failed",
    ScpiErrorCode.DLI_SYS_INVALID_GPIB_ADDR:              b"Invalid GPIB address",
    ScpiErrorCode.DLI_INVALID_LICENSE:                    b"Invalid license key",

    # DataManager
    ScpiErrorCode.DLI_DATAMGR_INDEX_OUTOF_RANGE:          b"Data manager, index out of range",

    # Protocol Handler
    ScpiErrorCode.DLI_PROTOMGR_INVALID_PP_TYPE:           b"Protocol manager, invalid PP type",
    ScpiErrorCode.DLI_PROTOMGR_INVALID_ANY_TYPE:          b"Protocol manager, invalid CORBA-ANY",
    ScpiErrorCode.DLI_PROTOMGR_INVALID_COMMAND_TYPE:      b"Protocol manager, invalid command type",
    ScpiErrorCode.DLI_PROTOMGR_INVALID_PRESET_COMMAND:    b"Protocol manager, invalid preset command",
    ScpiErrorCode.DLI_PROTOMGR_TESTUNIT_ACTIVE:           b"Protocol manager, test unit locked by another user",
    ScpiErrorCode.DLI_PROTOMGR_TESTUNIT_LOCKED:           b"Protocol manager, test unit locked.  Only queries can be performed.",
    ScpiErrorCode.DLI_PROTOMGR_USERID_NOTFOUND:           b"Protocol manager, user ID not found",
    ScpiErrorCode.DLI_INVALID_PP_MODE:                    b"Invalid protocol processor mode",
    ScpiErrorCode.DLI_PP_NOT_PRESENT:                     b"Protocol processor not present",

    # TestManager
    ScpiErrorCode.DLI_INVALID_TESTUNITID:                 b"Invalid test unit ID",
    ScpiErrorCode.DLI_INVALID_TESTID:                     b"Invalid test ID",
    ScpiErrorCode.DLI_INVALID_LOCK:                       b"Invalid PP lock attempt",

    # Database
    ScpiErrorCode.DLI_RECORD_NOT_FOUND:                   b"Record not found",
    ScpiErrorCode.DLI_DUPLICATE_RECORD:                   b"Duplicate record",

    # Additions
    ScpiErrorCode.DLI_INVALID_REGISTRY_KEY:               b"Invalid registry key",
    ScpiErrorCode.DLI_INVALID_REGISTRY_ENTRY:             b"Invalid registry entry",
    ScpiErrorCode.DLI_INCOMPATIBLE_VERSIONS:              b"Incompatible versions",
    ScpiErrorCode.DLI_FAILED_TO_BIND_TO_CORBA:            b"Failed to bind to CORBA",
    ScpiErrorCode.DLI_INVALID_IP_ADDRESS:                 b"Invalid IP address",

    # CATCH-ALL DLI ERROR
    ScpiErrorCode.DLI_INTERNAL_UNHANDLED_ERROR:           b"Unhandled internal error",

    # FOR ATM ONLY.
    ScpiErrorCode.INVALID_SCRAMBL:                        b"Invalid scramble",
    ScpiErrorCode.INVALID_UOM:                            b"Invalid UOM",
    ScpiErrorCode.INVALID_FOR_CUR_SCOPE:                  b"Invalid for current scope",
    ScpiErrorCode.INVALID_FOR_CUR_SETTING:                b"Invalid for current setting",
    ScpiErrorCode.INVALID_ALARM_TYPE:                     b"Invalid alarm type",
    ScpiErrorCode.INVALID_ERROR_TYPE:                     b"Invalid error type",
    ScpiErrorCode.INVALID_NWIMP_TYPE:                     b"Invalid NWIMP type",
    ScpiErrorCode.INVALID_OAM_TYPE:                       b"Invalid OAM type",
    ScpiErrorCode.INVALID_AAL_TYPE:                       b"Invalid AAL type",
    ScpiErrorCode.INVALID_TRAF_TYPE:                      b"Invalid traffic type",
    ScpiErrorCode.INVALID_RX_STATUS:                      b"Invalid RX status",
    ScpiErrorCode.INVALID_TX_STATUS:                      b"Invalid TX status",
    ScpiErrorCode.INVALID_TOGGLE_TYPE:                    b"Invalid toggle type",
    ScpiErrorCode.TX_ALREADY_ON:                          b"TX already on",
    ScpiErrorCode.TX_ALREADY_OFF:                         b"TX already off",
    ScpiErrorCode.RX_ALREADY_ON:                          b"RX already off",
    ScpiErrorCode.RX_ALREADY_OFF:                         b"RX already off",
    ScpiErrorCode.INVALID_TABLE_ENTRY:                    b"Invalid table entry",
    ScpiErrorCode.INVALID_SCOPE:                          b"Invalid scope",
    ScpiErrorCode.INVALID_PMOAM_BLOCK_SIZE:               b"Invalid PMOAM block size",

    ScpiErrorCode.INVALID_INTERFACE:                      b"Invalid interface",
    ScpiErrorCode.INVALID_MAPPING:                        b"Invalid mapping",
    ScpiErrorCode.INVALID_FRAMING:                        b"Invalid framing",
    ScpiErrorCode.INVALID_PATTERN:                        b"Invalid pattern",

    ScpiErrorCode.NO_MODIFIED_DATA:                       b"No modified data",
    ScpiErrorCode.INVALID_BGRND_SEQNO:                    b"Invalid background sequence number",
    ScpiErrorCode.INVALID_FOR_CUR_UNI_VERSION:            b"Invalid for current unit version",
    ScpiErrorCode.INVALID_SVCTEST_TYPE:                   b"Invalid SVCTEST type",
    ScpiErrorCode.INVALID_UNI_VERSION:                    b"Invalid UNI version",
    ScpiErrorCode.UNHANDLED_EXCEPTION:                    b"Unhandled exception",
    ScpiErrorCode.INVALID_RESULTS:                        b"Invalid results",
    ScpiErrorCode.INVALID_SETTINGS:                       b"Invalid settings",
    ScpiErrorCode.INVALID_ATM_ADDRESS_FORMAT:             b"Invalid ATM address format",
    ScpiErrorCode.INVALID_UNI_TIMER:                      b"Invalid unit timer",
    ScpiErrorCode.INVALID_QOS_CLASS:                      b"Invalid QOS class",
    ScpiErrorCode.INVALID_SIG_FILTER_TYPE:                b"Invalid signal filter type",
    ScpiErrorCode.INVALID_CALLREF_FLAG:                   b"Invalid callref flag",
    ScpiErrorCode.INVALID_SVC_MSG_TYPE:                   b"Invalid SVC message type",
    ScpiErrorCode.VCC_ENTRY_NOT_SVC:                      b"VCC entry not SVC",
    ScpiErrorCode.VCC_ENTRY_NOT_O191:                     b"VCC entry not O191",
    ScpiErrorCode.INVALID_O191_FLOW_TYPE:                 b"Invalid O191 flow type",
    ScpiErrorCode.INVALID_QOS_TEST_TYPE:                  b"Invalid QOS type",
    ScpiErrorCode.GENERIC_QUERY_ERR:                      b"Unknown query error",
    ScpiErrorCode.GENERIC_SET_ERR:                        b"Unknown set error",

    # ****** SCPI Standard Errors ******

    ScpiErrorCode.CMD_ERR:                                b"Command error",
    ScpiErrorCode.CMD_WRITE_ERR:                          b"Write command error",
    ScpiErrorCode.DATA_TYPE_ERR:                          b"Data type error",
    ScpiErrorCode.PARAMETER_NOT_ALLOWED:                  b"Parameter not allowed",
    ScpiErrorCode.MISSING_PARAM:                          b"Missing parameter",
    ScpiErrorCode.NUMERIC_DATA_ERR:                       b"Numeric data error",

    ScpiErrorCode.EXECUTION_ERR:                          b"Execution error",
    ScpiErrorCode.CMD_INVALID_FOR_CRNT_CONFIG:            b"Command protected",
    ScpiErrorCode.INIT_IGNORED:                           b"Init ignored",
    ScpiErrorCode.DATA_OUT_OF_RANGE:                      b"Data out of range",

    ScpiErrorCode.ILLEGAL_PARAM_VALUE:                    b"Illegal parameter value",
    ScpiErrorCode.HARDWARE_MISSING:                       b"Hardware missing",

    ScpiErrorCode.FILE_NOT_FOUND:                         b"File name not found",
    ScpiErrorCode.SYSTEM_CONTROLLER_EXCEPTION:            b"Device-specific error",
    ScpiErrorCode.SYSTEM_EXCEPTION:                       b"System error",
    ScpiErrorCode.ERROR_QUEUE_OVERFLOW:                   b"Queue overflow",
}


def errorDescription(errorCode):
    '''Convert an errorCode to a text version. Uses the descriptionTable
    dictionary to get just the description.

    Args:
        errorCode (int): ScpiErrorCode enum of the error

    Returns:
        Bytes text version of the errorCode
    '''
    return descriptionTable.get(errorCode, b"Unknown error")


def errorResponse(errorCode, globals, addToQueue = True):
    '''Convert an errorCode to the full SCPI response text. Includes the
    connection specific globals for error queue and the legacyResponse flag.
    Legacy response is True return just the integer and False for the integer
    and description.

    Args:
        errorCode (int): ScpiErrorCode enum of the error
        globals (SessionGlobals class): Used for saving error flags and
                                        accessing legacyResponse.
        addToQueue (bool): Normally this adds the errorCode to the error
                           queue in globals but it shouldn't do that if
                           converting the codes from the queue.

    Returns:
        Bytes text version of the errorCode
    '''
    if errorCode < 0:
        if globals.legacyResponse:
            response = b'%-.1d' % errorCode
        else:
            response = b'%-.1d, "%s"' % (errorCode, errorDescription(errorCode))
    else:
        if globals.legacyResponse:
            response = b'%+.1d' % errorCode
        else:
            response = b'%+.1d, "%s"' % (errorCode, errorDescription(errorCode))

    if addToQueue:
        globals.errorQueue.addEntry(errorCode)

    return response


class ErrorQueue(object):
    '''This class stores a FIFO queue of integer error codes. The size of
    this queue is limited to 100.
    '''

    def __init__(self):
        #self.queue = deque([], 100)
        self.queue = deque()

    def nextError(self):
        '''Returns the oldest error code in the FIFO and removes it from
        the FIFO. Returns None if the queue is empty.
        '''
        try:
            error = self.queue.popleft()
        except IndexError:
            error = None
        return error

    def lastError(self):
        '''Returns the newest error code in the FIFO and empties the FIFO.
        Returns None if the queue is empty.
        '''
        try:
            error = self.queue.pop()
            self.queue.clear()
        except IndexError:
            error = None
        return error

    def errorCount(self):
        '''Returns integer count of how many entries are in the FIFO.

        Args:
            errorCode (int): ScpiErrorCode enum of the error
        '''
        return len(self.queue)

    def addEntry(self, errorCode):
        '''Adds a new error code to the FIFO. If the FIFO hits the size
        limit then it replaces the previous newest entry with overflow
        error.

        Args:
            errorCode (int): ScpiErrorCode enum of the error
        '''
        if self.errorCount() >= 99:
            self.queue[-1] = ScpiErrorCode.ERROR_QUEUE_OVERFLOW
        else:
            self.queue.append(errorCode)


