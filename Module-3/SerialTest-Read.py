#
# SerialTest-Read.py - This is the Python code that will be used
# to demonstrate reading from the Raspberry Pi's serial port using
# the UART. This script requires a USB -> TTL cable to be installed
# to provide the serial connection to the Raspberry Pi. 
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1          Initial Development
#------------------------------------------------------------------

# This imports the Python serial package to handle communications over the
# Raspberry Pi's serial port. 
import serial

# Because we imported the entire package instead of just importing Serial and
# some of the other flags from the serial package, we need to reference those
# objects with dot notation.
#
# e.g. ser = serial.Serial
#
ser = serial.Serial(
        port='/dev/ttyS0', # This would be /dev/ttyAM0 prior to Raspberry Pi 3
        baudrate = 115200, # This sets the speed of the serial interface in
                           # bits/second
        parity=serial.PARITY_NONE,      # Disable parity
        stopbits=serial.STOPBITS_ONE,   # Serial protocol will use one stop bit
        bytesize=serial.EIGHTBITS,      # We are using 8-bit bytes 
        timeout=1          # Configure a 1-second timeout
)

# Configure our loop variable
repeat = True

# Loop until the user hits CTRL-C
while repeat:

        # Read lines from the serial port 1 at a time.
        # This will block until we have data available.
        try:
                # Read a line from the serial port. If there isn't any
                # data available return a blank line
                x = ser.readline()

                # Print the data returned from the serial port
                # Tell the library to decode the byte array as
                # a utf-8 string (default North American english character 
                # set) and do not add an extra newline character because the 
                # input already includes a newline.
                print(x.decode("utf-8"), end='')
        except KeyboardInterrupt:
                # Exit cleanly when the user enters CTRL-C
                repeat = False



                