# Thermostat - This is the Python code used to demonstrate
# the functionality of the thermostat that we have prototyped throughout
# the course. 
#
# This code works with the test circuit that was built for module 7.
#
# Functionality:
# The thermostat has three states: off, heat, cool
# The lights will represent the state that the thermostat is in.

# If the thermostat is set to off, the lights will both be off.
#
# If the thermostat is set to heat, the Red LED will be fading in 
# and out if the current temperature is blow the set temperature;
# otherwise, the Red LED will be on solid.
#
# If the thermostat is set to cool, the Blue LED will be fading in 
# and out if the current temperature is above the set temperature;
# otherwise, the Blue LED will be on solid.
#
# One button will cycle through the three states of the thermostat.
#
# One button will raise the setpoint by a degree.
#
# One button will lower the setpoint by a degree.
#
# The LCD will display the date and time on one line and
# alternate the second line between the current temperature and 
# the state of the thermostat along with its set temperature.
#
# The Thermostat will send a status update to the TemperatureServer
# over the serial port every 30 seconds in a comma-delimited string
# including the state of the thermostat, the current temperature
# in degrees Fahrenheit, and the setpoint of the thermostat.
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1          Initial Development
#
#    2          CB - Revised document to follow PEP industry best
#               practices with documentation
#
#    3          CB - Implemented logic per the system requirements.
#------------------------------------------------------------------

# Import necessary to provide timing in the main loop
from time import sleep
from datetime import datetime

# Imports required to allow us to build a fully functional state machine
from statemachine import StateMachine, State

# Imports necessary to provide connectivity to the thermostat sensor and the I2C bus
import board
import adafruit_ahtx0

# These are the packages that we need to pull in so that we can work with the GPIO interface on the Raspberry Pi board
# and work with the 16x2 LCD

# import board - already imported for I2C connectivity
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

# This imports the Python serial package to handle communications over the Raspberry Pi's serial port.
import serial

# Imports required to handle our Button, and our PWMLED devices
from gpiozero import Button, PWMLED

# This package is necessary so that we can delegate the blinking lights to their own thread so that more work can be
# done at the same time.
from threading import Thread

# This is needed to get coherent matching of temperatures.
from math import floor

# DEBUG flag - boolean value to indicate whether to print status messages on the console of the program
DEBUG = True

# Create an I2C instance so that we can communicate with devices on the I2C bus.
i2c = board.I2C()

# Initialize our Temperature and Humidity sensor
thSensor = adafruit_ahtx0.AHTx0(i2c)

# Initialize our serial connection because we imported the entire package instead of just importing Serial and some of
# the other flags from the serial package, we need to reference those objects with dot notation.
# e.g. ser = serial.Serial
ser = serial.Serial(
        port='/dev/ttyS0',              # This would be /dev/ttyAM0 prior to Raspberry Pi 3
        baudrate = 115200,              # This sets the speed of the serial interface in bits/seconds
        parity=serial.PARITY_NONE,      # Disable parity
        stopbits=serial.STOPBITS_ONE,   # Serial protocol will use one stop bit
        bytesize=serial.EIGHTBITS,      # We are using 8-bit bytes
        timeout=1                       # Configure a 1-second timeout
)

# Our two LEDs, utilizing GPIO 18, and GPIO 23
redLight = PWMLED(18)
blueLight = PWMLED(23)

class ManagedDisplay:
    """
    ManagedDisplay - Class intended to manage the 16x2 Display. This code is largely taken from the work done in module
    4, and converted into a class so that we can more easily consume the operational capabilities.
    """
    def __init__(self):
        """
        Set up the six GPIO lines to communicate with the display. This leverages the digitalio class to handle digital
        outputs on the GPIO lines. There is also an analagous class for analog IO.

        You need to make sure that the port mappings match the physical wiring of the display interface to the GPIO
        interface. Compatible with all versions of RPI as of Jan. 2019
        """
        self.lcd_rs = digitalio.DigitalInOut(board.D17)
        self.lcd_en = digitalio.DigitalInOut(board.D27)
        self.lcd_d4 = digitalio.DigitalInOut(board.D5)
        self.lcd_d5 = digitalio.DigitalInOut(board.D6)
        self.lcd_d6 = digitalio.DigitalInOut(board.D13)
        self.lcd_d7 = digitalio.DigitalInOut(board.D26)

        # Modify this if you have a different sized character LCD
        self.lcd_columns = 16
        self.lcd_rows = 2

        # Initialise the lcd class
        self.lcd = characterlcd.Character_LCD_Mono(
            self.lcd_rs,
            self.lcd_en,
            self.lcd_d4,
            self.lcd_d5,
            self.lcd_d6,
            self.lcd_d7,
            self.lcd_columns,
            self.lcd_rows
        )

        # wipe LCD screen before we start
        self.lcd.clear()


    def cleanup_display(self):
        """
        cleanup_display - Method used to clean up the digitalIO lines that are used to run the display.
        """
        self.lcd.clear() # Clear the LCD first - otherwise we won't be abe to update it.
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()

    def clear(self):
        """
        clear - Convenience method used to clear the display
        """
        self.lcd.clear()

    def update_screen(self, message):
        """
        update_screen - Convenience method used to update the message.
        """
        self.lcd.clear()
        self.lcd.message = message

    # End class ManagedDisplay definition

# Initialize our display
screen = ManagedDisplay()

class TemperatureMachine(StateMachine):
    """
    TemperatureMachine - This is our StateMachine implementation class. The purpose of this state machine is to manage
    the three states handled by our thermostat:
        - off
        - heat
        - cool
    """

    def __init__(self):
        # Define the three states for our machine.
        off = State(initial = True) #  off - nothing lit up
        heat = State()              #  red - only red LED fading in and out
        cool = State()              #  blue - only blue LED fading in and out

        # Default temperature setPoint is 72 degrees Fahrenheit
        self.setPoint = 72

        # cycle - event that provides the state machine behavior of transitioning between the three states of our
        # thermostat
        self.cycle = (
            off.to(heat) |
            heat.to(cool) |
            cool.to(off)
        )

    def on_enter_heat(self):
        """
        on_enter_heat - Action performed when the state machine transitions into the 'heat' state
        """
        self.update_lights()
        ## : Add the single line of code necessary to update the
        ## lights on the thermostat. 
        ## Remove this TODO comment block when complete.

        if DEBUG:
            print("* Changing state to heat")

    def on_exit_heat(self):
        """
        on_exit_heat - Action performed when the statemachine transitions out of the 'heat' state.
        """
        self.update_lights()
        ## : Add the single line of code necessary to change the state
        ## of the indicator light when exiting the heat state.
        ## Remove this TODO comment block when complete.

    def on_enter_cool(self):
        """
        on_enter_cool - Action performed when the state machine transitions into the 'cool' state
        """
        self.update_lights()
        ## : Add the single line of code necessary to update the
        ## lights on the thermostat. 
        ## Remove this TODO comment block when complete.

        if DEBUG:
            print("* Changing state to cool")

    def on_exit_cool(self):
        """
        on_exit_cool - Action performed when the statemachine transitions out of the 'cool' state.
        """
        self.update_lights()
        ## : Add the single line of code necessary to change the state
        ## of the indicator light when exiting the cool state.
        ## Remove this TODO comment block when complete.

    def on_enter_off(self):
        """
        on_enter_off - Action performed when the state machine transitions into the 'off' state
        """
        self.update_lights()
        # Pseudocode called for two lines for expected result which I believe was toggling the lights off but how I
        # implemented update_lights() makes it so the lights turn off and not on unless the state is heat or cool.

        ## : Add the two lines of code necessary to change the state
        ## of any indicator lights when entering the off state.
        ## Remove this TODO comment block when complete.

        if DEBUG:
            print("* Changing state to off")

    def process_temp_state_button(self):
        """
        process_temp_state_button - Utility method used to send events to the state machine. This is triggered by the
        button_pressed event handler for our first button
        """
        if DEBUG:
            print("Cycling Temperature State")
        self.send('cycle')
        ## TODO: Add the single line of code necessary to change
        ## the state of the thermostat.
        ## Remove this TODO comment block when complete.

    def process_temp_inc_button(self):
        """
        process_temp_inc_button - Utility method used to update the setPoint for the temperature. This will increase the
        setPoint by a single degree. This is triggered by the button_pressed event handler for our second button
        """
        if DEBUG:
            print("Increasing Set Point")
        self.setPoint += 1
        self.update_lights()
        ## : Add the two lines of code necessary to update
        ## the setPoint of the thermostat and the status lights
        ## within the circuit.
        ## Remove this TODO comment block when complete.

    def process_temp_dec_button(self):
        """
        process_temp_dec_button - Utility method used to update the setPoint for the temperature. This will decrease the
        setPoint by a single degree. This is triggered by the button_pressed event handler for our third button.
        """
        if DEBUG:
            print("Decreasing Set Point")
        self.setPoint -= 1
        self.update_lights()
        ## : Add the two lines of code necessary to update
        ## the setPoint of the thermostat and the status lights
        ## within the circuit.
        ## Remove this TODO comment block when complete.

    def update_lights(self):
        """
        update_lights - Utility method to update the LED indicators on the Thermostat
        """
        temp = floor(get_fahrenheit()) # Make sure we are comparing temperatures in the correct scale
        redLight.off()
        blueLight.off()

        # Verify values for debug purposes
        if DEBUG:
            print(f"State: {self.current_state.id}")
            print(f"SetPoint: {self.setPoint}")
            print(f"Temp: {temp}")

        # Determine visual identifiers
        if self.heat.is_active:
            redLight.pulse()
        elif self.cool.is_active:
            blueLight.pulse()
        ##
        ## : Add the code necessary to update the status
        ## lights in our thermostat circuit. Keep in mind the 
        ## necessary functionality for each light depends on 
        ## both the current state of the thermostat and the 
        ## temperature relative to the setpoint in that state.
        ## You should be able to accomplish this within 20 lines
        ## of code. Remove this TODO comment block when complete.

    def run(self):
        """
        run - kickoff the display management functionality of the thermostat
        """
        my_thread = Thread(target=self.manage_my_display)
        my_thread.start()

    @staticmethod
    def get_fahrenheit():
        """
        Get the temperature in Fahrenheit
        """
        t = thSensor.temperature
        return ((9 / 5) * t) + 32

    def setup_serial_output(self):
        """
        Configure output string for the Thermostat Server
        """

        # System requirements called for the variable to be 'output' but that shadows a function.
        serial_output = f'{self.current_state.id},{self.get_fahrenheit()}F,{self.setPoint}F'
        ## : Add the code necessary to create the string assigned to
        ## the variable named output that will provide the single 
        ## line of text that will be sent to the TemperatureServer
        ## over the Serial Port (UART). Make sure that this is a 
        ## comma delimited string indicating the current state of the
        ## thermostat, the temperature in degrees Fahrenheit, and the
        ## current setpoint of the thermostat - also in degrees Fahrenheit.
        ## Remove this TODO comment block when complete.

        return serial_output

    # Continue display output
    endDisplay = False

    def manage_my_display(self):
        """
        This function is designed to manage the LCD
        """
        counter = 1
        alt_counter = 1
        while not self.endDisplay:
            # Only display if the DEBUG flag is set
            if DEBUG:
                print("Processing Display Info...")

            # Setup display line 1
            lcd_line_1 = datetime.now().strftime('%b %d  %H:%M:%S\n')

            # Setup Display Line 2
            lcd_line_2 = ''
            if alt_counter < 6:
                lcd_line_2 = f"T:{self.get_fahrenheit():0.1f}F"
                ##
                ## : Add the code necessary to setup the second line
                ## of the LCD display to include the current temperature in
                ## degrees Fahrenheit. 
                ## Remove this TODO comment block when complete.

                alt_counter = alt_counter + 1
            else:
                lcd_line_2 += f" S:{self.setPoint}F"
                ##
                ## : Add the code necessary to setup the second line
                ## of the LCD display to include the current state of the
                ## thermostat and the current temperature setpoint in 
                ## degrees Fahrenheit. 
                ## Remove this TODO comment block when complete.

                alt_counter = alt_counter + 1
                if alt_counter >= 11:
                    # Run the routine to update the lights every 10 seconds to keep operations smooth
                    self.update_lights()
                    alt_counter = 1

            # Update Display
            screen.update_screen(lcd_line_1 + lcd_line_2)

            # Update server every 30 seconds
            if DEBUG:
               print(f"Counter: {counter}")
            if (counter % 30) == 0:
                msg = self.setup_serial_output()
                ser.write(msg.encode('utf-8'))
                ##
                ## : Add the single line of code necessary to send
                ## our current state information to the TemperatureServer
                ## over the Serial Port (UART). Be sure to use the 
                ## setup_serial_output function previously defined.
                ## Remove this TODO comment block when complete.

                counter = 1
            else:
                counter = counter + 1
            sleep(1)

        # Cleanup display
        screen.cleanup_display()

    # End class TemperatureMachine definition

# Added an execution for the file statement because I want to use the graphing calls of the statemachine defined in
# this file for documentation.
if __name__ == '__main__':

    # Set up our State Machine
    tsm = TemperatureMachine()
    tsm.run()


    # Configure our green button to use GPIO 24 and to execute the method to cycle the thermostat when pressed.
    greenButton = Button(24)
    greenButton.when_pressed = tsm.process_temp_state_button
    ## : Add the single line of code necessary to assign
    ## a function to be triggered when the button is pushed to
    ## change the state of our thermostat.
    ## Remove this TODO comment block when complete.

    # Configure our Red button to use GPIO 25 and to execute the function to increase the setpoint by a degree.
    redButton = Button(25)
    redButton.when_pressed = tsm.process_temp_inc_button
    ## : Add the single line of code necessary to assign
    ## a function to be triggered when the button is pushed to
    ## increase the setpoint by one degree Fahrenheit.
    ## Remove this TODO comment block when complete.

    # Configure our Blue button to use GPIO 12 and to execute the function to decrease the setpoint by a degree.
    blueButton = Button(12)
    blueButton.when_pressed = tsm.process_temp_dec_button
    ## : Add the single line of code necessary to assign
    ## a function to be triggered when the button is pushed to
    ## increase the setpoint by one degree Fahrenheit.
    ## Remove this TODO comment block when complete.

    # Set up loop variable
    repeat = True

    # Repeat until the user creates a keyboard interrupt (CTRL-C)
    while repeat:
        try:
            # wait
            sleep(30)

        except KeyboardInterrupt:
            # Catch the keyboard interrupt (CTRL-C) and exit cleanly
            # we do not need to manually clean up the GPIO pins, the
            # gpiozero library handles that process.
            print("Cleaning up. Exiting...")

            # Stop the loop
            repeat = False

            # Close down the display
            tsm.endDisplay = True
            sleep(1)