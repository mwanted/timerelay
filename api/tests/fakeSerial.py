# fakeSerial.py
# D. Thiebaut
# A very crude simulator for PySerial assuming it
# is emulating an Arduino.

from collections import defaultdict

arduino = defaultdict(lambda: b"ERROR", key="some_value")
arduino["pw\n"] = b"OK\n"
arduino["ssa10\n"] = b"OK\n"
arduino["sg\n"] = b"A: off_delay: 0\nA: mode:      0\nA: count:     0\nB: off_delay: 0\nB: mode:      0\nB: count:     0\nOK\n"
arduino["wrong\n"] = b"wrong answer"
arduino["wrong2\n"] = b"wrong\n\nanswer"
arduino["pg\n"] = b"A: guard_time: 2\nA: short_time: 10\nA: off_delay:  600\nA: mode:       2\nB: guard_time: 2\nB: short_time: 10\nB: off_delay:  600\nB: mode:       2\nOK\n"
arduino["psam0\n"] = b"OK\n"
arduino["psas2\n"] = b"OK\n"
arduino["psag20\n"] = b"OK\n"
arduino["psad600\n"] = b"OK\n"

# a Serial class emulator 
class Serial:

    ## init(): the constructor.  Many of the arguments have default values
    # and can be skipped when calling the constructor.
    def __init__( self, port='COM1', baudrate = 19200, timeout=1,
                  bytesize = 8, parity = 'N', stopbits = 1, xonxoff=0,
                  rtscts = 0):
        self.name     = port
        self.port     = port
        self.timeout  = timeout
        self.parity   = parity
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.xonxoff  = xonxoff
        self.rtscts   = rtscts
        self._isOpen  = True
        self._receivedData = ""
        self._data = "It was the best of times.\nIt was the worst of times.\n"

    ## isOpen()
    # returns True if the port to the Arduino is open.  False otherwise
    def isOpen( self ):
        return self._isOpen

    def reset_input_buffer( self ):
    	  self._data = ""

    def flush( self ):
    	  pass

    ## open()
    # opens the port
    def open( self ):
        self._isOpen = True

    ## close()
    # closes the port
    def close( self ):
        self._isOpen = False

    ## write()
    # writes a string of characters to the Arduino
    def write( self, string ):
        #print( 'Arduino got: "' + string.decode('ASCII') + '"' )
        self._receivedData += string.decode('ASCII')
        self._data = string + arduino[string.lower().decode('ASCII')]

    ## read()
    # reads n characters from the fake Arduino. Actually n characters
    # are read from the string _data and returned to the caller.
    def read( self, size=1 ):
        s = self._data[0:size]
        #print( "read: now self._data = ", self._data )
        return s

    ## readline()
    # reads characters from the fake Arduino until a \n is found.
    def readline( self ):
        returnIndex = self._data.index( "\n" )
        if returnIndex != -1:
            s = self._data[0:returnIndex+1]
            self._data = self._data[returnIndex+1:]
            return s
        else:
            return ""

    ## __str__()
    # returns a string representation of the serial class
    def __str__( self ):
        return  "Serial<id=0xa81c10, open=%s>( port='%s', baudrate=%d," \
               % ( str(self.isOpen), self.port, self.baudrate ) \
               + " bytesize=%d, parity='%s', stopbits=%d, xonxoff=%d, rtscts=%d)"\
               % ( self.bytesize, self.parity, self.stopbits, self.xonxoff,
                   self.rtscts )
                   
                   