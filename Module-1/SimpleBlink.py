#
# SimpleBlink.py - This is the Python code that will be used
# to demonstrate accessing the GPIO interface on the Raspberry Pi
# and making an LED blink when attached to GPIO line 18.
#
# This script is designed to work with the circuit first built in
# assignment 1-4. It should continue to function throughout the
# course.
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1.1        Added exception handler to intercept the CTRL-C
#               Keyboard interrup to process GPIO line cleanup
#    1          Initial Development
#------------------------------------------------------------------

# Load the GPIO interface from the Raspberry Pi Python Module
# The GPIO interface will be available through the GPIO object
import RPi.GPIO as GPIO

# Load the time module so that we can utilize the sleep method to 
# inject a pause into our operation
import time

# Setup the GPIO interface
#
# 1. Turn off warnings for now - they can be useful for debugging more
#    complex code.
# 2. Tell the GPIO library we are using Broadcom pin-numbering. The 
#    Raspberry Pi CPU is manufactured by Broadcom, and they have a 
#    specific numbering scheme for the GPIO pins. It does not match
#    the layout on the header. However, the Broadcom pin numbering is
#    what is printed on the GPIO Breakout Board, so this should match!
# 3. Tell the GPIO library that we are using GPIO line 18, and that 
#    we are using it for Output. When this state is configured, setting
#    the GPIO line to true will provide positive voltage on that pin.
#    Based on the circuit we have built, positive voltage on the GPIO
#    pin will flow through the LED, through the resistor to the ground
#    pin and the LED will light up. 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

# Setup a continuous loop for testing. This loop will run until
# the program is interrupted (i.e. Ctrl-C from the command line running
# the program). Please Note: If something goes wrong with the exception
# handler, the light may stay on. 
#
# If this happens, you can restart the script and try killing it again, 
# or you can run the GPIO-18-OFF.py script provided with this module.
#
# We set a variable to use to cleanly exit the WHILE loop
repeat = True
while repeat:

    # We use exception handling here to make sure we catch the keyboard
    # interrupt (Ctrl-C) and cleanup the GPIO environment accordingly.
    try:
        # Set GPIO line 18 to True - enable output voltage, and then pause
        # for time.sleep(#) where the argument is a number of seconds
        # This turns the LED ON
        GPIO.output(18, True)
        time.sleep(1)

        # Set GPIO line 18 to False - disable output voltage, and then pause
        # for time.sleep(#) where the argument is a number of seconds
        # This turns the LED OFF
        GPIO.output(18, False)
        time.sleep(1)
    except KeyboardInterrupt:
        # If we reach this line we have executed a Ctrl-C to kill the 
        # Script, so let the user know we are cleaning up
        print("Cleaning Up GPIO Lines and Exiting program...")

        # Execute the cleanup of all pins that we have used in this script.
        # This does not have any impact on pins not used in this program.
        GPIO.cleanup()

        # Tell the loop that we are done.
        repeat = False
