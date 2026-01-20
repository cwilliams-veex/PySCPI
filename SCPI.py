###############################################################################
#
# Copyright 2018-2019, VeEX, Inc.
# All Rights Reserved.
#
# $Workfile:   SCPI.py  $
# $Revision: 21157 $
# $Author: patrickellis $
# $Date: 2020-01-21 16:01:37 -0500 (Tue, 21 Jan 2020) $
#
# DESCRIPTION:
#    Application to process SCPI commands from various sources.
#
###############################################################################

import sys

# For initial development. Put the relative path to where veexlib is at the
# start of the path. When veexlib is properly installed then this can be removed.
sys.path.insert(0, '../PythonAPI')
sys.path.insert(0, '../PythonAPI/veexlib')
sys.path.insert(0, '../PythonAPI/veexlib/ProtoBuf')

import TcpipServer
import time


# If a command line parameter is given then it is the IP address of the
# protobufServer. Default to localhost if not given.
if len(sys.argv) > 1:
    ipAddress = sys.argv[1]
else:
    ipAddress = "localhost"


# Call TCP/IP server functions, which create a task and return immediately.
try:
    TcpipServer.tcpipPortListen(port = 8090, ipAddress = ipAddress)
except OSError:
    # port 8090 is in use by C++ SCPI so use port 8092 for debugging in
    # parallel with that.
    TcpipServer.tcpipPortListen(port = 8092, ipAddress = ipAddress)
TcpipServer.tcpipPortListen(port = 8091, ipAddress = ipAddress, useSsl = True)

# Wait until program is forced to exit.
try:
    while True:
        time.sleep(2.0)
except TcpipServer.TcpipServerExit:
    pass
