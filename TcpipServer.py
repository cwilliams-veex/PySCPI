###############################################################################
#
# Copyright 2018-2019, VeEX, Inc.
# All Rights Reserved.
#
# $Workfile:   TcpipServer.py  $
# $Revision: 21493 $
# $Author: patrickellis $
# $Date: 2020-04-08 15:00:55 -0400 (Wed, 08 Apr 2020) $
#
# DESCRIPTION:
#    Module to read SCPI commands from standard and SSL/TLS TCP/IP sockets.
#
###############################################################################

import pickle
import signal
import socket
import ssl
import threading
import time
from ErrorCodes import TcpipServerExit
from ScpiEngine import ScpiEngine


# If echoTest is True then act as an echo server instead of a SCPI server.
# Defualt to SCPI.
echoTest = False

# Each connaction is assigned a session ID that is an incremeting integer.
nextSessionId = 1

# Simple exception to handle signals.
#class TcpipServerExit(Exception):
#    pass

def service_shutdown(signum, frame):
    '''This function is called when a signal happens and raises the
    TcpipServerExit exception. That causes the main loop to exit.
    '''
    if echoTest:
        print('Caught signal %d' % signum)
    raise TcpipServerExit

# Setup to handle these two signals. SIGTERM is the default for the kill
# command and SIGINT is from control-C.
signal.signal(signal.SIGTERM, service_shutdown)
signal.signal(signal.SIGINT, service_shutdown)


class TcpipSessionThread(threading.Thread):
    '''This thread class handles reading SCPI commands from a TCP/IP socket.
    Bytes from the socket are combined into commands, separated by CR or LF.
    Each user that connects will have it's own socket and task.

    Args:
        sessionSocket (socket class): The socket object to recv commands and
                                      send responses over.
        sessionType (string): The type of socket (ie "TCP", "SSL", etc).
        sessionId (int): The ID number assiged to the socket. Used for
                         response messages.
        ipAddress (string): The IP address of the protobuf server to connect to.
    '''

    def __init__(self, sessionSocket, sessionType, sessionId, ipAddress):
        threading.Thread.__init__(self)
        self.sessionSocket = sessionSocket
        self.sessionType = sessionType
        self.sessionId = sessionId
        self.ipAddress = ipAddress
        self.scpiEngine = ScpiEngine(sessionType, sessionId, ipAddress)

        # Setting this as daemon means this thread will be killed if the
        # main thread exits. Without this the program will freeze forever,
        # until each thread exits. This allows control-C and signals to
        # work as expected.
        self.daemon = True

    def run(self):
        '''This is the task function. when it returns the task ends.
        '''

        # Debug code.
        if echoTest:
            self.sessionSocket.send(b'Thank you for connecting. Type CLOSE to exit.\n\r')

        # buffer is data read from the socket. It can contain only part of a
        # command or multiple commands. Either case must be handled.
        buffer = b""

        # command is the string up to, but not including, the end-of-line.
        command = b""

        # Read the autoLogin settings from a file.
        try:
            with open('autologin.pickle', 'rb') as f:
                autoLogin = pickle.load(f)
            if autoLogin.enabled:
                print('autologin')
                self.scpiEngine.processCommand(b'LOGIN %s %s' % \
                                              (autoLogin.username, \
                                               autoLogin.password))
        except FileNotFoundError as error:
            # If file doesn't exist then autoLogin is disabled.
            pass
        except pickle.UnpicklingError as error:
            # If unpickle fails then autoLogin is disabled.
            pass


        # Loop until CLOSE sets exitTask to True.
        exitTask = False
        while not exitTask:
            # If buffer is empty then need to get some data to fill it.
            if len(buffer) == 0:
                try:
                    # Fill buffer with data from the socket. Small 256 byte
                    # size means less time wasted on string handling below.
                    buffer = self.sessionSocket.recv(256)
                except socket.timeout as e:
                    # timeout expired, try again
                    continue
                except socket.error as e:
                    # Something else happened, handle error, exit, etc.
                    # Has never happened yet, so exit should never happen.
                    print("socket.error")
                    print (e)

                    # Logout the user if one is logged in.
                    self.scpiEngine.processCommand(b'LOGOUT')

                    # Close the connection with the client and end the thread
                    self.sessionSocket.shutdown(socket.SHUT_RDWR)
                    self.sessionSocket.close()
                    return
                else:
                    if len(buffer) == 0:
                        # Shutdown of socket on other end.
                        #print ('orderly shutdown on other end')

                        # Logout the user if one is logged in.
                        self.scpiEngine.processCommand(b'LOGOUT')

                        # Close the connection with the client and end the thread
                        self.sessionSocket.shutdown(socket.SHUT_RDWR)
                        self.sessionSocket.close()
                        return
                    else:
                        # Got a message, data is already in the buffer. Replace
                        # all CR with LF so searching for end of line is easier.
                        buffer = buffer.replace(b'\r', b'\n')

            # Search for end-of-line
            endOfLine = buffer.find(b'\n')
            if endOfLine < 0:
                # There is no end-of-line, append the whole buffer to the
                # command and empty the buffer.
                command += buffer
                buffer = b""
            else:
                # There is an end-of-line so handle the command.
                if endOfLine == 0:
                    # First byte is an end-of-line. This is either an empty
                    # line or the comand was in previous buffers. Remove the
                    # end-of-line from the buffer, nothing to add to command.
                    buffer = buffer[1:]
                else:
                    # Append the buffer up to the end-of-line to the command
                    # and remove up to and including the end-of-line from the
                    # buffer.
                    command += buffer[0:endOfLine]
                    buffer = buffer[endOfLine + 1:]

                # If user is typing commands by hand then need to handle
                # backspace key as deleting characters.
                editedCommand = b''
                for i in range(len(command)):
                    if command[i] == 8:    #'\b':
                        if len(editedCommand) != 0:
                            editedCommand = editedCommand[:-1]
                    else:
                        editedCommand += bytes([command[i]])
                #print(command, "->", editedCommand)
                command = editedCommand

                # There was an end-of-line so we have a command but want to
                # ignore any blank commands
                command = command.lstrip(b" \t:").rstrip()
                if len(command) != 0:
                    # There is a real command.
                    if echoTest:
                        # Upper case and return command as an echo server.
                        response = command.upper()
                        response2 = self.scpiEngine.processCommand(command)
                    else:
                        # Process as a SCPI command.
                        #response = command
                        response = self.scpiEngine.processCommand(command)

                    # Send the response, if there is one, back to the user.
                    if response and (len(response) != 0):
                        self.sessionSocket.send(response + b'\r\n')

                    # If this was a CLOSE command then done. The logging
                    # out of the protobuf server was done as part of SCPI
                    # command handling.
                    if command.upper().startswith(b"CLOSE"):
                        exitTask = True

                    # Done, empty for the next command.
                    command = b""

        # Debug code.
        if echoTest:
            self.sessionSocket.send(b'Thank you for exiting\n\r')

        # Close the connection with the client
        self.sessionSocket.shutdown(socket.SHUT_RDWR)
        self.sessionSocket.close()

class TcpipServerThread(threading.Thread):
    '''This thread class handles listening on a TCP/IP port for connections
    from users. A socket is opened for each connection and a task is created
    to handle commands over that socket.

    Args:
        serverSocket (socket class): The server socket object to listen on.
        ipAddress (string): The IP address of the protobuf server to connect to.
        sslContext (): If SSL/TLS sockets sre to be used then this is the
                       required context object. None means use normal sockets.
    '''

    def __init__(self, serverSocket, ipAddress, sslContext = None):
        threading.Thread.__init__(self)
        self.serverSocket = serverSocket
        self.ipAddress    = ipAddress
        self.sslContext   = sslContext

        # Setting this as daemon means this thread will be killed if the
        # main thread exits. Without this the program will freeze forever,
        # until each thread exits. This allows control-C and signals to
        # work as expected.
        self.daemon = True

    def run(self):
        global nextSessionId

        # Loop forever or until interrupted or an error occurs.
        try:
            while True:
                try:
                    newSocket, addr = self.serverSocket.accept()
                except socket.timeout as e:
                    # timeout expired, try again
                    #print("socket.timeout")
                    continue
                except socket.error as e:
                    # Something else happened, handle error, exit, etc.
                    # Has never happened yet, so exit should never happen.
                    print("socket.error")
                    print (e)
                    raise TcpipServerExit
                else:
                    sessionId = nextSessionId
                    nextSessionId += 1

                    print ('Opened TCP/IP connection from', addr, "sessionId:", sessionId)

                    # Create and start a thread to handle this socket
                    if self.sslContext:
                        # Wrap the server socket with a TLS layer.
                        newSslSocket = self.sslContext.wrap_socket(newSocket, server_side=True)
                        newThread = TcpipSessionThread(newSslSocket, b"SSL", sessionId, self.ipAddress)
                    else:
                        newThread = TcpipSessionThread(newSocket, b"TCP", sessionId, self.ipAddress)
                    newThread.start()

        except TcpipServerExit:
            print("close server")
            self.serverSocket.close()
            return


def tcpipPortListen(port, ipAddress, useSsl = False):
    '''Opens a server socket at the given port (8090 for SCPI) and creates a
    task to listen for connections.

    Args:
        port (int): The TCP/IP port of the server socket to listen on.
        ipAddress (string): The IP address of the protobuf server to connect to.
        useSsl (bool): True if this is an SSL/TLS socket, otherwise a normal socket.
    '''

    if useSsl:
        # Create an SSL context to use
        sslContext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        sslContext.load_cert_chain(certfile="host.cert", keyfile="host.key")

    # Create a socket object.
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind to the port.
    serverSocket.bind(('', port))

    # Set socket timeout to 2 seconds so that signals can be handled.
    serverSocket.settimeout(2.0)

    # Put the socket into listen mode.
    serverSocket.listen(2)

    if useSsl:
        print ("Listening for SSL connections on port %d" % port)
    else:
        print ("Listening for TCP/IP connections on port %d" % port)

    # Create and start a thread to listen for connections.
    if useSsl:
        tcpipThread = TcpipServerThread(serverSocket, ipAddress, sslContext)
    else:
        tcpipThread = TcpipServerThread(serverSocket, ipAddress)
    tcpipThread.start()


if __name__ == "__main__":
    # Do an echo server test, listening to port 8090.
    echoTest = True
    tcpipPortListen(port = 8090)
#    tcpipPortListen(port = 8090, useSsl = True)

    # Wait until program is forced to exit.
    try:
        while True:
            time.sleep(2.0)
    except TcpipServerExit:
        pass

