###############################################################################
#
# Copyright 2018-2019, VeEX, Inc.
# All Rights Reserved.
#
# $Workfile:   ParseUtils.py  $
# $Revision: 20616 $
# $Author: patrickellis $
# $Date: 2019-10-15 20:34:48 -0400 (Tue, 15 Oct 2019) $
#
# DESCRIPTION:
#    Module with utilities useful for parsing SCPI commands.
#
###############################################################################

from typing import NamedTuple


class SubCommand(NamedTuple):
    '''A list of these named tuples are returned by preParse. The last tuple
    in the list always has an empty tail.
    '''
    head: bytes    # Command or sub-command.
    tail: bytes    # Remaining unparsed part of the string.


class CommandTableEntry(NamedTuple):
    '''A list of these named tuples are used by the SCPI command handler
    classes to create a list of all the commands handled by that class
    '''
    command: bytes       # Command or query
    callback: bytes      # Function to handle the command returns bytes


class CommandTreeEntry(NamedTuple):
    '''A tree of lists of these named tuples are used by the SCPI command
    handler classes to process all the commands handled by that class
    '''
    subCommand: bytes    # Part of a command or query
    branch: list         # Next branch of the tree if subCommand matches
    callback: bytes      # Function to handle the command that returns bytes


def preParse(buffer, separators = None):
    '''This parses the text buffer into parts (ie. command and subcommands).
    The last tuple in the list always has an empty tail.

    Args:
        buffer (bytes): the string to parse.
        separators (bytes): characters that separate the parts.

    Returns:
        List of SubCommand named tuples
    '''
    # The result of this function is a list of SubCommand named tuples.
    results = []

    # If separators not given then default to commands
    if not separators:
        separators = b' \t:'

    while True:
        # Search for separator location (ie. whitespace or :).
        locationList = [buffer.find(sep) for sep in separators]
        locationList = [x for x in locationList if x >= 0]
        if locationList:
            # There is a separator so handle it.
            separator = min(locationList)
            if separator == 0:
                # First byte is a separator so there were multiple
                # separators in a row, skip it. This should never happen.
                buffer = buffer[1:]
            else:
                # Add the area before the separator as a subcommand and
                # the area after as the tail, stripping any sequential
                # separators.
                newSubCommand = SubCommand(buffer[0:separator],
                                           buffer[separator + 1:].lstrip(separators))
                results.append(newSubCommand)

                # Remove up to and including the separator from the buffer.
                buffer = newSubCommand.tail
        else:
            # List is empty so there is no separator. Append the rest of the
            # command and exit.
            newSubCommand = SubCommand(buffer, b'')
            results.append(newSubCommand)
            buffer = b""
            break

    return results


def preParseCommand(command):
    '''This parses the text command into parts (ie. command and subcommands).
    The last tuple in the list always has an empty tail.

    Args:
        command (bytes): the string to parse.

    Returns:
        List of SubCommand named tuples
    '''
    return preParse(command, B' \t:')


def preParseParameters(parameters):
    '''This parses the text parameters into parts (ie. command and subcommands).
    The last tuple in the list always has an empty tail.

    Args:
        command (bytes): the string to parse.

    Returns:
        List of SubCommand named tuples
    '''
    response = preParse(parameters, B' \t,')
    if (len(response) == 1) and (len(response[0].head) == 0):
        return []
    else:
        return response


def parseCommand(buffer):
    '''This parses the text buffer in the stricter internal command format
    into parts. Each part is separated by a colon and any lower case letters
    aty the end are ignored (ie. RX:PROTOcol? becomes a list of RX and PROTO?).

    Args:
        buffer (bytes): the string to parse.

    Returns:
        List of bytes strings
    '''
    # The result of this function is a list of bytes
    results = []

    # If all the leters are upper case then this would be all that is needed.
    # As it may not be, this is just a raw result which will need further
    # processing.
    rawSplit = buffer.split(b':')
    #print(rawSplit)

    for word in rawSplit:
        if word.isupper():
            # All the letters are uppercase, just copy into results.
            results.append(word)
        else:
            # Some of the letters are lower case. Need to find the first
            # lower case letter.
            for i in range(len(word)):
                if bytes([word[i]]).islower():
                    # Found the lower case letter. Copy the part before it
                    # into results and include ? at the end, if present.
                    if bytes([word[-1]]) == b'?':
                        results.append(word[:i] + b'?')
                    else:
                        results.append(word[:i])
                    break
    return results


def processCommandTableIntoTree(commandTable, commandTreeRoot):
    '''Processes the command table into a tree of subcommands for matching.

    Args:
        commandTable (list of CommandTableEntry named tuples): A list of
            commands and callbacks to turn into a tree.
        commandTreeRoot (list of CommandTreeEntry named tuples): A tree of
            lists of subCommands and callbacks.
    '''
    # Process every entry in the command table.
    for tableEntry in commandTable:
        # parse command into list of subcommands
        subCommandList = parseCommand(tableEntry.command)
#        print(tableEntry.command)

        # Loop through all the subcommands
        treeNode = commandTreeRoot
        for subCommand in subCommandList:
            # Search the Nth level of the command tree for the subcommand.
            foundNode = None
            for node in treeNode:
#                print(treeNode)
                if node.subCommand == subCommand:
                    # Found a match so this subCommand was already in
                    # the tree.
                    foundNode = node
                    break

            # If this subCommand was not in the tree. Create a new tree
            # entry and add it to the tree.
            if not foundNode:
                if subCommand is subCommandList[-1]:
                    # This is the last subCommand in the list. Create a new
                    # node with the callback.
                    foundNode = CommandTreeEntry (subCommand, [], tableEntry.callback)
#                    print("Added terminal node", subCommand)
                else:
                    # This is NOT the last subCommand in the list. Create a new
                    # node without the callback.
                    foundNode = CommandTreeEntry (subCommand, [], None)
#                    print("Added sub-node", subCommand)
                treeNode.append(foundNode)
#                print("   Added", treeNode[-1])
            # Whether command was found or added, follow the branch.
            treeNode = foundNode.branch

#    print(commandTreeRoot)

def searchCommandTree(parsedCommand, commandTreeRoot):
    '''Searches the command tree for a command.

    Args:
        parsedCommand (List of SubCommand named tuples): The command that
            needs to be found.
        commandTreeRoot (list of CommandTreeEntry named tuples): A tree of
            lists of subCommands and callbacks.

    Returns:
        callback, bytes: Tuple of the function for handling this command and
                         bytes string of parameters. Callback is None if
                         command not found.
    '''
    treeNode = commandTreeRoot
    foundNode = None
#    print("  command", parsedCommand)

    # Loop through all the subcommands
    for subCommand in parsedCommand:
        # Search the Nth level of the command tree for the subcommand.
        foundNode = None
        for node in treeNode:
#            print("cmnd %s sub %s" % (subCommand.head.upper(), node.subCommand))
            if node.subCommand.endswith(b'?') and subCommand.head.endswith(b'?'):
                # Matching with a query with a query. Know the ? at end matchs,
                # just need to match the previous text.
                if subCommand.head[:-1].upper().startswith(node.subCommand[:-1]):
                    # Found a match so this subCommand is in the tree.
                    foundNode = node
#                    print("MATCH")
                    break
            elif node.subCommand.endswith(b'?') or subCommand.head.endswith(b'?'):
                # Matching query to non-query. This never matches
                pass
            else:
                # Matching non-query to non-query. Match the entire text.
                if subCommand.head.upper().startswith(node.subCommand):
                    # Found a match so this subCommand is in the tree.
                    foundNode = node
#                    print("MATCH")
                    break

        if foundNode:
            # Match was found, either return the callback function or follow
            # the branch if the callback is None.
            if foundNode.callback:
#                print("returning A", foundNode.callback, subCommand.tail)
                return (foundNode.callback, subCommand.tail)
            else:
#                print("branch", foundNode.branch)
                treeNode = foundNode.branch
        else:
            # Match not found, return None
#            print("returning None")
            return (None, b"")

    # Made it here so the entire command matched, so there are not parameters.
    # Return the handler function for this command and an empty parameter
    # string. If the command is not complete then this will return None.
#    print("returning B", foundNode.callback, b"")
    if foundNode:
        return (foundNode.callback, b"")
    else:
        return (None, b"")


def isErrorRateFormat(rateString):
    ''' To check whether string is in a given N.NNe-NN format or not
    '''
    rateString = rateString.upper()
    if (len(rateString) == 8)      and \
       (rateString[0:1].isdigit()) and \
       (rateString[1:2] == b'.')   and \
       (rateString[2:4].isdigit()) and \
       (rateString[4:6] == b'E-')  and \
       (rateString[6:8].isdigit()):
        return True
    else:
        return False


def asciiToBinSdh(asciiString):
    '''Method to convert input binary string to integer value.
    Returns a positive integer or -1 for error.
    '''

    # All the characters in input string must be binary digits.
    if len(asciiString.translate(None, delete = b'01')) != 0:
        return -1

    # Convert the string and return it.
    return int(asciiString, base = 2)


def intToBinSdh(intValue):
    '''Method to convert integer to string of binary digits.
    Returns the binary bytes object.
    '''
    return b'#B' + bytes(bin(intValue), encoding='utf-8')[2:]


def asciiToHexSdh(asciiString):
    '''Method to convert input hex string to integer value.
    Returns a positive integer or -1 for error.
    '''

    # All the characters in input string must be hex digits.
    if len(asciiString.translate(None, delete = b'0123456789ABCDEFabcdef')) != 0:
        return -1

    # Convert the string and return it.
    return int(asciiString, base = 16)


def checkNumeric(numericString):
    ''' Check whether the input is Hex, Binary or Decimal text and convert
    to a positive integer if it is. Returns -1 on any error.
    '''
    retVal = -1
    if numericString[0:1] == b'#':
        if numericString[1:2].upper() == b'H':
            retVal = asciiToHexSdh(numericString[2:])
        elif numericString[1:2].upper() == b'B':
            retVal = asciiToBinSdh(numericString[2:])
    elif numericString.isdigit():
        retVal = int(numericString)
    return retVal


def isFloatSdh(floatString):
    ''' To check whether string is a float format or not.
    Valid strings NNN.NNN or -NNN.NNN with no exponent.
    '''
    if len(floatString.translate(None, delete = b'-.0123456789')) != 0:
        # All the characters in input string must be -, . or decimaldigits.
        return False
    elif floatString.rfind(b'-') > 0:
        # Only first character can be -.
        return False
    elif floatString.rfind(b'.') != floatString.find(b'.'):
        # Only one . character is allowed.
        return False
    elif not floatString[-1:].isdigit():
        # Must have a digit in the string
        return False
    else:
        return True


def isFloatE(floatString):
    ''' To check whether string is a float format or not.
    Valid strings N.NNNeNN or -N.NNNe-NN with optional exponent.
    '''
    floatString = floatString.upper()
    if len(floatString.translate(None, delete = b'-.0123456789E')) != 0:
        # All the characters in input string must be -, ., E or decimaldigits.
        return False
    elif floatString.rfind(b'.') != floatString.find(b'.'):
        # Only one . character is allowed.
        return False
    elif floatString.rfind(b'E') != floatString.find(b'E'):
        # Only one E character is allowed.
        return False

    if floatString.find(b'E') >= 0:
        preE = floatString[:floatString.find(b'E')]
        postE = floatString[floatString.find(b'E') + 1:]
        if preE.rfind(b'-') > 0 or postE.rfind(b'-') > 0:
            # Only first character of each part can be -.
            return False
        elif postE.find(b'.') >= 0:
            # No . is allowed in the exponent
            return False
        elif preE.find(b'.') >= 0:
            if not preE[preE.find(b'.') - 1:preE.find(b'.')].isdigit():
                # Must have a digit before the . in mantissa
                return False
            else:
                return True
        elif not preE[-1:].isdigit():
            # Must have a digit in the mantissa
            return False
        else:
            return True
    else:
        if floatString.rfind(b'-') > 0:
            # Only first character can be -.
            return False
        elif floatString.find(b'.') >= 0:
            if not floatString[floatString.find(b'.') - 1:floatString.find(b'.')].isdigit():
                # Must have a digit before the .
                return False
            else:
                return True
        elif not floatString[-1:].isdigit():
            # Must have a digit in the mantissa
            return False
        else:
            return True


if __name__ == "__main__":
    # Do some tests of parseCommand
    print(parseCommand(b'GET:PROTOcol?'))
    print(parseCommand(b'GET:PROTOcol'))
    print(parseCommand(b'GET:PROTO?'))
    print(parseCommand(b'*RST'))

    # Do some tests of preParseCommand
    print(preParseCommand(b'*RST'))
    print(preParseCommand(b'GET PROTO?'))
    print(preParseCommand(b'GET:PROTO?'))
    print(preParseCommand(b'GET   :::   PROTO?'))

    print(isErrorRateFormat(b'1.34e-05'))
    print(isErrorRateFormat(b'12.34e-05'))
    print(isErrorRateFormat(b'12.34e-5'))
    print(asciiToBinSdh(b'0101'))
    print(asciiToBinSdh(b'23'))
    print(intToBinSdh(18))
    print(asciiToHexSdh(b'ABCD'))
    print(asciiToHexSdh(b'ABCDG'))

    print('#######')

    print(isFloatSdh(b'-34'))
    print(isFloatSdh(b'12.34'))
    print(isFloatSdh(b'-23-45'))
    print(isFloatSdh(b'1.2.3.4'))
    print(isFloatSdh(b''))

    print('#######')

    print(isFloatE(b'1.234e-7'))
    print(isFloatE(b'-1.234e-7'))
    print(isFloatE(b'1.234e7'))
    print(isFloatE(b'-1.234e7'))
    print(isFloatE(b'1.234'))
    print(isFloatE(b'-1.234'))
    print(isFloatE(b'-1.234e6.7'))
    print(isFloatE(b'6'))
    print(isFloatE(b''))
    print(isFloatE(b'-'))
    print(isFloatE(b'.456'))
    print(isFloatE(b'e'))

