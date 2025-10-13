#
# TemperatureSensorIntegration.py - This is the Python code template 
# used to demonstrate the integration of the temperature sensor with
# some of our other components. 
#
# The goal of this module will be to display the temperature on our 
# 16x2 display, and when the button is pressed switch between 
# displaying the temperature in Celsius or Fahrenheit. 
#
# We will manage transitions between temperature scales with a state
# machine.
#
# This code works with the test circuit that was built for module 6.
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1          Initial Development
#    2          CB - Revised file to adhere to PEP requirements on
#                    documentation and docstrings.
#    3          CB - Adjusted process button to toggle temp unit.
#------------------------------------------------------------------

#Imports required to handle our Button, and our LED devices
from gpiozero import Button, LED

# Imports required to allow us to build a fully functional state machine
from statemachine import StateMachine, State

# Import required to allow us to pause for a specified length of time
from time import sleep
from datetime import datetime

# These are the packages that we need to pull in so that we can work with the GPIO interface on the Raspberry Pi board
# and work with the 16x2 LCD
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

# This is the package we need for our Temperature Sensor
import adafruit_ahtx0

# Threads are required so that we can manage multiple tasks at the same time
from threading import Thread

# DEBUG flag - boolean value to indicate whether to print status messages on the console of the program
DEBUG = True


class ManagedDisplay:
    """
    ManagedDisplay - Class intended to manage the 16x2 Display. This code is largely taken from the work done in
    module 4, and converted into a class so that we can more easily consume the operational capabilities.
    """

    def __init__(self):
        """
        Set up the six GPIO lines to communicate with the display. This leverages the digitalio class to handle
        digital outputs on the GPIO lines. There is also an analagous class for analog IO. You need to make sure that
        the port mappings match the physical wiring of the display interface to the GPIO interface. Compatible with
        all versions of RPI as of Jan. 2019
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
        self.lcd = characterlcd.Character_LCD_Mono(self.lcd_rs, self.lcd_en, 
                    self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7, 
                    self.lcd_columns, self.lcd_rows)

        # wipe LCD screen before we start
        self.lcd.clear()

    def cleanup_display(self):
        """cleanup_display - Method used to clean up the digitalIO lines that are used to run the display."""
        # Clear the LCD first - otherwise we won't be abe to update it.
        self.lcd.clear()
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()

    def clear(self):
        """clear - Convenience method used to clear the display"""
        self.lcd.clear()

    def update_screen(self, message):
        """update_screen - Convenience method used to update the message."""
        self.lcd.clear()
        self.lcd.message = message

    # End class ManagedDisplay definition
    

class TempMachine(StateMachine):
    """
    TempMachine - This is our StateMachine implementation class. The purpose of this state machine is to maintain the
    necessary state to display temperature information in Celsius or Fahrenheit
    """

    # Our two LEDs, utilizing GPIO 18, and GPIO 23
    redLight = LED(18)
    blueLight = LED(23)

    # Set the contents of our scale
    scale1 = 'F'
    scale2 = 'C'

    # keep track of the active scale
    activeScale = scale2

    # Define these states for our machine.
    # Celsius - default
    # Fahrenheit
    Celsius = State(initial = True)
    Fahrenheit = State()

    # Configure our display
    screen = ManagedDisplay()

    # Configure our temperature sensor
    i2c = board.I2C()
    thSensor = adafruit_ahtx0.AHTx0(i2c)

    # doDot - Event that moves between the off-state (all-lights-off) and a 'dot'
    cycle = (
        Celsius.to(Fahrenheit) | Fahrenheit.to(Celsius)
    )

    def on_enter_celsius(self):
        """on_enter_Celsius - Action performed when the state machine transitions into the Celsius state"""
        self.activeScale = self.scale2
        if DEBUG:
            print("* Changing state to Celsius")

    def on_enter_fahrenheit(self):
        """on_enter_Fahrenheit - Action performed when the state machine transitions into the Celsius state"""
        self.activeScale = self.scale1
        if DEBUG:
            print("* Changing state to Fahrenheit")


    def process_button(self):
        """
        processButton - Utility method used to send events to the state machine. This event triggers a change in state to
        swap between Fahrenheit and Celsius output
        """
        print('*** processButton')

        # Toggle temp unit
        if self.activeScale == self.scale1:
            self.activeScale = self.scale2
        else:
            self.activeScale = self.scale1

        self.send("cycle")

    def run(self):
        """run - kickoff the display management functionality in a separate execution thread."""
        my_thread = Thread(target=self.display_temp)
        my_thread.start()

    def get_fahrenheit(self):
        """Get the temperature in Fahrenheit"""
        t = self.thSensor.temperature
        return ((9 / 5) * t) + 32

    def get_celsius(self):
        """Get the temperature in Celsius"""
        return self.thSensor.temperature

    def get_rh(self):
        """Get the Relative Humidity"""
        return self.thSensor.relative_humidity

    # Flag to indicate whether to shut down the thread
    endDisplay = False

    def display_temp(self):
        """
        displayTemp - utility method used to continuously update the display. We will be putting the date and time in row
        1, and the Temperature and Relative Humidity in Row 2.
        """
        while not self.endDisplay: # Loop until we are shutdown

            # Setup line 1
            line1 = datetime.now().strftime('%b %d  %H:%M:%S\n')

            # Setup line 2
            if self.activeScale == 'C':
                line2 = f"T:{self.get_celsius():0.1f}C H:{self.get_rh():0.1f}%"
            else:
                line2 = f"T:{self.get_fahrenheit():0.1f}F H:{self.get_rh():0.1f}%"

            self.screen.update_screen(line1 + line2)
            sleep(1)

        # Cleanup the display i.e. clear it
        self.screen.cleanup_display()
    # End class CWMachine definition


# Initialize our State Machine, and begin transmission
tempMachine = TempMachine()
tempMachine.run()

# greenButton - set up our Button, tied to GPIO 24. Configure the action to be taken when the button is pressed to be the
# execution of the processButton function in our State Machine
greenButton = Button(24)
greenButton.when_pressed = tempMachine.process_button

# Setup loop variable
repeat = True

# Repeat until the user creates a keyboard interrupt (CTRL-C)
while repeat:
    try:
        # Only display if the DEBUG flag is set
        if DEBUG:
            print("Killing time in a loop...")

        # sleep for 20 seconds at a time. This value is not crucial, all the work for this application is handled by the
        # Button.when_pressed event process
        sleep(20)
    except KeyboardInterrupt:
        # Catch the keyboard interrupt (CTRL-C) and exit cleanly we do not need to manually clean up the GPIO pins, the
        # gpiozero library handles that process.
        print("Cleaning up. Exiting...")

        # Stop the loop
        repeat = False
        
        # Cleanly exit the state machine after completing the last message
        tempMachine.endDisplay = True
        sleep(1)