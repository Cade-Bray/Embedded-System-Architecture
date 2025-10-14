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
#
#    4          CB - Revisited documentation again and cleaned up
#               the file for readability.
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

        @param message is a string to be sent to the LCD screen configured.
        """
        self.lcd.clear()
        self.lcd.message = message

    # End class ManagedDisplay definition


class TemperatureMachine(StateMachine):
    """
    TemperatureMachine - This is our StateMachine implementation class. The purpose of this state machine is to manage
    the three states handled by our thermostat:
        - off
        - heat
        - cool
    """

    def __init__(self, set_point = 72, debugging = true):
        """
        This is the class initializer. This will create the class variables needed. This design choice was made over
        defining the variables outside the init state so that garbage collection can be done quicker as we're not
        defining off|heat|cool state declaration variables as class global variables. To fully utilize this state 
        machine you need to create a medium such as GPIO buttons that have been given a when pressed function for the 
        three processing triggers which are 'process_temp_state_button' for cycling states, 'process_temp_inc_button'
        for processing a set point increment, and finally a 'process_temp_dec_button' for processing a set point
        decrement. If you need an example look at the script at the bottom that is executed in this class's file.

        @param set_point defaulted to 72 degrees. Provide an integer as the default entry temp.
        @param DEBUG Default is true. Change for debugging statements to console to be toggled.
        """

        # Define the three states for our machine.
        off = State(initial = True) #  off - nothing lit up
        heat = State()              #  red - only red LED fading in and out
        cool = State()              #  blue - only blue LED fading in and out

        # Default temperature setPoint is 72 degrees Fahrenheit
        self.setPoint = set_point

        # cycle - event that provides the state machine behavior of transitioning between the three states of our
        # thermostat
        self.cycle = (
            off.to(heat) |
            heat.to(cool) |
            cool.to(off)
        )

        # Continue display output
        self.endDisplay = False

        # DEBUG flag - boolean value to indicate whether to print status messages on the console of the program
        self.DEBUG = debugging

        # Initialize our serial connection because we imported the entire package instead of just importing Serial and some of
        # the other flags from the serial package, we need to reference those objects with dot notation.
        # e.g. ser = serial.Serial
        self.ser = serial.Serial(
            port='/dev/ttyS0',             # This would be /dev/ttyAM0 prior to Raspberry Pi 3
            baudrate=115200,               # This sets the speed of the serial interface in bits/seconds
            parity=serial.PARITY_NONE,     # Disable parity
            stopbits=serial.STOPBITS_ONE,  # Serial protocol will use one stop bit
            bytesize=serial.EIGHTBITS,     # We are using 8-bit bytes
            timeout=1                      # Configure a 1-second timeout
        )

        # Initialize our display
        self.screen = ManagedDisplay()

        # Our two LEDs, utilizing GPIO 18, and GPIO 23
        self.redLight = PWMLED(18)
        self.blueLight = PWMLED(23)

        # Create an I2C instance so that we can communicate with devices on the I2C bus.
        i2c = board.I2C()

        # Initialize our Temperature and Humidity sensor
        self.thSensor = adafruit_ahtx0.AHTx0(i2c)

    def on_enter_heat(self):
        """
        on_enter_heat - Action performed when the state machine transitions into the 'heat' state
        """
        self.update_lights()

        if self.DEBUG:
            print("* Changing state to heat")

    def on_exit_heat(self):
        """
        on_exit_heat - Action performed when the statemachine transitions out of the 'heat' state.
        """
        self.update_lights()

    def on_enter_cool(self):
        """
        on_enter_cool - Action performed when the state machine transitions into the 'cool' state
        """
        self.update_lights()

        if self.DEBUG:
            print("* Changing state to cool")

    def on_exit_cool(self):
        """
        on_exit_cool - Action performed when the statemachine transitions out of the 'cool' state.
        """
        self.update_lights()

    def on_enter_off(self):
        """
        on_enter_off - Action performed when the state machine transitions into the 'off' state
        """
        self.update_lights()
        # Pseudocode called for two lines for expected result which I believe was toggling the lights off but how I
        # implemented update_lights() makes it so the lights turn off and not on unless the state is heat or cool.

        if self.DEBUG:
            print("* Changing state to off")

    def process_temp_state_button(self):
        """
        process_temp_state_button - Utility method used to send events to the state machine. This is triggered by the
        button_pressed event handler for our first button
        """
        if self.DEBUG:
            print("Cycling Temperature State")
        self.send('cycle')

    def process_temp_inc_button(self):
        """
        process_temp_inc_button - Utility method used to update the setPoint for the temperature. This will increase the
        setPoint by a single degree. This is triggered by the button_pressed event handler for our second button
        """
        if self.DEBUG:
            print("Increasing Set Point")
        self.setPoint += 1
        self.update_lights()

    def process_temp_dec_button(self):
        """
        process_temp_dec_button - Utility method used to update the setPoint for the temperature. This will decrease the
        setPoint by a single degree. This is triggered by the button_pressed event handler for our third button.
        """
        if self.DEBUG:
            print("Decreasing Set Point")
        self.setPoint -= 1
        self.update_lights()

    def update_lights(self):
        """
        update_lights - Utility method to update the LED indicators on the Thermostat
        """
        temp = floor(self.get_fahrenheit()) # Make sure we are comparing temperatures in the correct scale
        self.redLight.off()
        self.blueLight.off()

        # Verify values for debug purposes
        if self.DEBUG:
            print(f"State: {self.current_state.id}")
            print(f"SetPoint: {self.setPoint}")
            print(f"Temp: {temp}")

        # Determine visual identifiers
        if self.heat.is_active:
            # Heat is active. Now check if its above or equal to the set point.
            if self.get_fahrenheit() >= self.setPoint:
                # At or above the set point. Per requirements, we should have a solid light.
                self.redLight.on()
            else:
                # Below the heating requirement. Show active status by pulsing the light.
                self.redLight.pulse()

        elif self.cool.is_active:
            # Cooling is active. Now check if its below or equal to the set point.
            if self.get_fahrenheit() <= self.setPoint:
                # No cooling required because we're at or below the set point.
                self.blueLight.on()
            else:
                # Cooling required. Show active state by pulsing the light.
                self.blueLight.pulse()

    def run(self):
        """
        run - kickoff the display management functionality of the thermostat
        """
        my_thread = Thread(target=self.manage_my_display)
        my_thread.start()

    def get_fahrenheit(self):
        """
        Get the temperature in Fahrenheit
        """
        t = self.thSensor.temperature # Retrieves as Celsius.
        return ((9 / 5) * t) + 32     # Convert to Fahrenheit

    def setup_serial_output(self):
        """
        Configure output string for the Thermostat Server
        """
        # System requirements called for the variable to be 'output' but that shadows a function.
        return f'{self.current_state.id},{self.get_fahrenheit()}F,{self.setPoint}F'

    def manage_my_display(self):
        """
        This function is designed to manage the LCD
        """
        counter = 1
        alt_counter = 1
        while not self.endDisplay:
            # Only display if the DEBUG flag is set
            if self.DEBUG:
                print("Processing Display Info...")

            # Setup display line 1
            lcd_line_1 = datetime.now().strftime('%b %d  %H:%M:%S\n')

            # Setup Display Line 2
            if alt_counter < 6:
                # Output the current temp and increment the counter.
                lcd_line_2 = f"Cur Temp:{self.get_fahrenheit():0.1f}F"
                alt_counter = alt_counter + 1
            else:
                # Output the set point and reset the lights and counter if at 10 seconds.
                lcd_line_2 = f"Set Temp:{self.setPoint}F"
                alt_counter = alt_counter + 1

                if alt_counter >= 11:
                    # Run the routine to update the lights every 10 seconds to keep operations smooth
                    self.update_lights()
                    alt_counter = 1

            # Update Display
            self.screen.update_screen(lcd_line_1 + lcd_line_2)

            # Update server every 30 seconds
            if self.DEBUG:
               print(f"Counter: {counter}")

            if (counter % 30) == 0:
                msg = self.setup_serial_output()    # String that's configured in setup_serial_output()
                self.ser.write(msg.encode('utf-8')) # encode and serialize the string.
                counter = 1
            else:
                counter = counter + 1
            sleep(1)

        # Cleanup display
        self.screen.cleanup_display()

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

    # Configure our Red button to use GPIO 25 and to execute the function to increase the setpoint by a degree.
    redButton = Button(25)
    redButton.when_pressed = tsm.process_temp_inc_button

    # Configure our Blue button to use GPIO 12 and to execute the function to decrease the setpoint by a degree.
    blueButton = Button(12)
    blueButton.when_pressed = tsm.process_temp_dec_button

    # Set up loop variable
    repeat = True

    # Repeat until the user creates a keyboard interrupt (CTRL-C)
    while repeat:
        try:
            # wait
            sleep(30)

        except KeyboardInterrupt:
            # Catch the keyboard interrupt (CTRL-C) and exit cleanly we do not need to manually clean up the GPIO pins,
            # the gpiozero library handles that process.
            print("Cleaning up. Exiting...")

            # Stop the loop
            repeat = False

            # Close down the display
            tsm.endDisplay = True
            sleep(1)