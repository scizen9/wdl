# -----------------------------------------------------------------------------
# @file     wdlParser.py
# @brief    parser for the Waveform Development Language
# @author   David Hale
# @date     2016-xx-xx
# @modified 2016-03-28 DH
# 
# This is the parser for the Waveform Development Language (WDL).
# -----------------------------------------------------------------------------
import Lexer as lexer
from Symbols import *


gotMain      = False
token        = None
board        = []
chan         = []
paramList    = []
paramNames   = []
subroutines  = []
level        = 0
lastTime     = 0
maxTime      = 0
timeStamps   = {}
waveformName = ""

# -----------------------------------------------------------------------------
# @fn     dq
# @brief  wrap double quotes around a string
# @param  string, s
# @return string, s
# -----------------------------------------------------------------------------
def dq(s):
    """
    wrap double quotes around a string 's' and return quoted string
    """
    return '"%s"' %s

# -----------------------------------------------------------------------------
# @fn     getToken
# @brief  assign next token from source text to global var
# @param  none
# @return none
# -----------------------------------------------------------------------------
def getToken():
    """
    Gets the next token from the source text and assigns it to the
    global variable 'token'.
    """
    global token
    token = lexer.get()

# -----------------------------------------------------------------------------
# @fn     found
# @brief  
# @param  token type
# @return True or False
# -----------------------------------------------------------------------------
def found(argTokenType):
        """
        """
        if token.type.upper() == argTokenType.upper():
                return True
        return False

# -----------------------------------------------------------------------------
# @fn     error
# @brief  
# @param  msg
# @return none
# -----------------------------------------------------------------------------
def error(msg):
    """
    """
    token.abort(msg)

# -----------------------------------------------------------------------------
# @fn     consume
# @brief  
# @param  argTokenType
# @return none
# -----------------------------------------------------------------------------
def consume(argTokenType):
    """
    Consume a token of a given type and get the next token.
    If the current token is NOT of the expected type, then
    raise an error.
    """
    if token.type.upper() == argTokenType.upper():
        getToken()
    else:
        print "ERROR"
        error("expected " + dq(argTokenType) + 
              " but got " + token.show(align=False) )

# -----------------------------------------------------------------------------
# @fn     timelabel
# @brief  
# @param  none
# @return none
# -----------------------------------------------------------------------------
def timelabel():
    """
    """
    global token
    global timeStamps
    global lastTime

    # if there is an equal sign then a label has been assigned to this time
    if found("="):
        consume("=")
        timeStamps[token.cargo] = lastTime
        consume(IDENTIFIER)

# -----------------------------------------------------------------------------
# @fn     time
# @brief  
# @param  none
# @return none
# -----------------------------------------------------------------------------
def time():
    """
    """
    global lastTime
    global maxTime
    global timeStamps

    eqn = ""

    if found("SET"):
        return

    if found(".+"):
        prevTime = lastTime
        consume(".+")
    else:
        prevTime = 0

    eqn += str( prevTime ) + "+"

    while not found(":"):
        if found(IDENTIFIER):
            if token.cargo in timeStamps:
                eqn += str( timeStamps[token.cargo] )
            else:
                print "Unresolved symbol " + dq(token.cargo)
            consume(IDENTIFIER)
        else:
            eqn += token.cargo
            getToken()
    consume(":")
    lastTime = int( eval(eqn) )

    # need to remember the max time, for the RETURN
    if lastTime > maxTime:
        maxTime = lastTime

    # line starts with a number for a time
#   if found(NUMBER):
#       lastTime = token.cargo
#       consume(NUMBER)
#       consume(":")
#   # or line can start with a label
#   elif found(IDENTIFIER):
#       # if a label, then it has to have been already defined
#       if token.cargo in timeStamps:
#           eqn += timeStamps[token.cargo]
#       else:
#           print "Unresolved symbol " + dq(token.cargo)

#   # if line starts with nothing then we use the same time as the previous line

# -----------------------------------------------------------------------------
# @fn     set
# @brief  
# @param  none
# @return none
# -----------------------------------------------------------------------------
def set():
    """
    """
    global board
    global chan
    board = []
    chan  = []

    consume("SET")

    # may be a set enclosed in square brackets
    if found("["):
        consume("[")

    while not found(","):
        if found (NUMBER):
            board.append(token.cargo)
        consume(NUMBER)
        consume(":")
        if found (NUMBER):
            chan.append(token.cargo)
        consume(NUMBER)

        if found(","):
            consume(",")
        else:
            break
    if found("]"):
        consume("]")

# -----------------------------------------------------------------------------
# @fn     to
# @brief  
# @param  none
# @return none
# -----------------------------------------------------------------------------
def to():
    """
    """
    global level

    consume("TO")
    # could be a negative number...
    if found("-"):
        # if so, consume the sign and remember it
        consume("-")
        sign=-1.0
    else:
        sign=1.0
    if found(NUMBER):
        # multiply the value by the sign from above (hehe)
        level = str( sign * float(token.cargo) )
    consume(NUMBER)

# -----------------------------------------------------------------------------
# @fn     eol
# @brief  check for end-of-line character
# @param  none
# @return none
# -----------------------------------------------------------------------------
def eol():
    """
    check for the end-of-line character (semi-colon)
    """
    consume(";")

# -----------------------------------------------------------------------------
# @fn     waverules
# @brief  
# @param  none
# @return none
# -----------------------------------------------------------------------------
def waverules():
    """
    """
    time()
    timelabel()
    set()
    to()
    eol()

# -----------------------------------------------------------------------------
# @fn     wavelabel
# @brief  
# @param  none
# @return none
# -----------------------------------------------------------------------------
def wavelabel():
    """
    """
    global waveformName

    if found(IDENTIFIER):
        waveformName = token.cargo
    else:
        print "missing waveform label"

    consume(IDENTIFIER)

# -----------------------------------------------------------------------------
# @fn     waveform
# @brief  
# @param  none
# @return none
# -----------------------------------------------------------------------------
def waveform():
    """
    """
    global token
    global lastTime
    global maxTime
    global level
    global waveformName
    
    # a waveform must start with the "WAVEFORM" keyword, ...
    consume("WAVEFORM")

    # ...followed by a label for the waveform.
    wavelabel()

    print "waveform " + waveformName + ":"

    maxTime = 0

    # Then, until the end of the waveform (delimited by curly brace),
    # check for the waveform rules.
    consume("{")
    while not found("}"):
        waverules()
        for index in range(len(board)):
            print lastTime , board[index], chan[index] , level
    consume("}")

    # "RETURN" marks the end of the waveform output
    print str(maxTime+1) + " RETURN " + waveformName

# -----------------------------------------------------------------------------
# @fn     sequence_label
# @brief  
# @param  none
# @return sequence name
# -----------------------------------------------------------------------------
def sequence_label():
    """
    """
    global token

    if found(IDENTIFIER):
        print "sequence " + token.cargo + ":"
        name = token.cargo
    consume(IDENTIFIER)
    return name

# -----------------------------------------------------------------------------
# @fn     generic_sequence
# @brief  
# @param  optional sequenceName
# @return none
# 
# The optional sequenceName parameter is used for the RETURN statement,
# when applicable.
# -----------------------------------------------------------------------------
def generic_sequence(*sequenceName):
    """
    """
    global token
    # sequence/waveform must start with an open (left) curly brace, {
    consume("{")
    # process until end-of-sequence
    while not found("}"):
        sequenceLine = ""
        # process until end-of-line
        while not found(";"):
            if  ( found(IDENTIFIER) ) and \
                ( token.cargo not in subroutines ) and \
                ( token.cargo not in paramNames ):
                error("undefined symbol " + token.show(align=False) )
            # If token is in the list of subroutines then it must be CALLed
            # and must be followed by parentheses and an optional number
            if token.cargo in subroutines:
                sequenceLine += "CALL " + token.cargo
                consume(IDENTIFIER)
                consume("(")
                # if the next token isn't a closing paren then assume it's a number or param
                if not found(")"):
                    sequenceLine += "(" + token.cargo #+ ")"
            elif found("RETURN"):
                consume("RETURN")
                print "RETURN " + sequenceName[0]
                break
            else:
                sequenceLine += token.cargo
            if found("RETURN"):
                consume("RETURN")
                print "*** RETURN "
                break
            getToken()
            # if next token not a symbol then pad with a space
            if token.cargo not in TwoCharacterSymbols and \
               token.cargo not in OneCharacterSymbols:
                sequenceLine += " "
        # line must end with a semi-colon
        consume(";")
        # won't normally have a 0-length sequenceLine, but could happen during testing
        if len(sequenceLine) > 0:
            print sequenceLine
    # sequence/waveform must end with an close (right) curly brace, }
    consume("}")

# -----------------------------------------------------------------------------
# @fn     sequence
# @brief  
# @param  none
# @return none
# -----------------------------------------------------------------------------
def sequence():
    """
    """
    global token
    global subroutines

    sequenceName = sequence_label()
    generic_sequence(sequenceName)

# -----------------------------------------------------------------------------
# @fn     main
# @brief  
# @param  none
# @return none
# -----------------------------------------------------------------------------
def main():
    """
    MAIN is a special sequence which is an infinite loop. Every script has
    a MAIN and every MAIN has a goto MAIN.
    """
    global token
    global gotMain

    if gotMain:
        print "ERROR"
        error("cannot have more than one MAIN")

    consume("MAIN")
    print "sequence MAIN:"
    generic_sequence()
    print "GOTO MAIN"
    gotMain = True

# -----------------------------------------------------------------------------
# @fn     parse_waveform
# @brief  
# @param  sourceText
# @return none
# -----------------------------------------------------------------------------
def parse_waveform(sourceText):
    """
    """
    global token

    lexer.initialize(sourceText)

    while True:
        getToken()
        if token.type == EOF: break
        waveform()

# -----------------------------------------------------------------------------
# @fn     param
# @brief  pulls out params from anywhere in .seq file and stores in a list
# @param  none
# @return none
# -----------------------------------------------------------------------------
def param():
    """
    """
    global token
    global paramList
    global paramNames

    line = "parameter "
    consume("param")
    paramNames.append(token.cargo)
    line += token.cargo
    consume(IDENTIFIER)
    line += token.cargo
    consume("=")
    line += token.cargo
    consume(NUMBER)
    paramList.append(line)

# -----------------------------------------------------------------------------
# @fn     parse_sequence
# @brief  
# @param  sourceText
# @return none
# -----------------------------------------------------------------------------
def parse_sequence(sourceText):
    """
    """
    global token
    global paramList

    lexer.initialize(sourceText)

    getToken()
    param()
    main()

    while True:
        getToken()
        if token.type == EOF: break
        param()
        sequence()

# -----------------------------------------------------------------------------
# @fn     get_subroutines
# @brief  
# @param  sourceText
# @return none
# -----------------------------------------------------------------------------
def get_subroutines(sourceText):
    """
    """
    global token
    global subroutines

    lexer.initialize(sourceText)

    subroutines = []

    while True:
        getToken()
        if token.type == EOF: break
        if found(IDENTIFIER):
            name = token.cargo
            consume(IDENTIFIER)
            if found("{"):
                subroutines.append(name)
                consume("{")
                while not found("}"):
                    getToken()

    return subroutines

# -----------------------------------------------------------------------------
# @fn     get_params
# @brief  
# @param  sourceText
# @return none
# -----------------------------------------------------------------------------
def get_params(sourceText):
    """
    """
    global token
    global paramNames

    lexer.initialize(sourceText)

    while True:
        getToken()
        if token.type == EOF: break
        if found("param"):
            consume("param")
            paramNames.append(token.cargo)
            consume(IDENTIFIER)
            consume("=")
            consume(NUMBER)

    return paramNames

# -----------------------------------------------------------------------------
# @fn     parse
# @brief  parses everything
# @param  sourceText
# @return none
# -----------------------------------------------------------------------------
def parse(sourceText):
    """
    """
    global token
    global paramList

    lexer.initialize(sourceText)

    getToken()
    while True:
        if token.type == EOF:
            break
        elif found("WAVEFORM"):
            waveform()
        elif found("param"):
            param()
        elif found("MAIN"):
            main()
        elif found(IDENTIFIER):
            sequence()
        else:
            error("unrecognized token " + token.show(align=False) )
            break

    for p in paramList:
        print p
