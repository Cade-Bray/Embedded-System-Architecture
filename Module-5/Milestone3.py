# Milestone3.py - This is the Python code template used to
# set up the structure for Milestone 3. In this milestone, you need
# to demonstrate the capability to productively display a message
# in Morse code utilizing the Red and Blue LEDs. The message should
# change between SOS and OK when the button is pressed using a state
# machine.
#
# This code works with the test circuit that was built for module 5.
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1          Initial Development
#
#    2          Cade Bray - Changed formatting of file to fit PEP
#               requirements per industry standard best practices.
#
#    3          Cade Bray - Implemented milestone logic
#------------------------------------------------------------------

from threading import Thread
from time import sleep  # Import required to allow us to pause for a specified length of time
from gpiozero import Button, LED  # Imports required to handle our Button, and our LED devices
from statemachine import StateMachine, State  # Imports required to allow us to build a fully functional state machine
import adafruit_character_lcd.character_lcd as character_lcd
import board  # 1 of 2. Package for controlling LCD
import digitalio  # 2 of 2 Package for controlling LCD

# DEBUG flag - boolean value to indicate whether to print status messages on the console of the program
DEBUG = True


class ManagedDisplay:
    """ManagedDisplay - Class intended to manage the 16x2 Display"""

    def __init__(self):
        """
        Class Initialization method to set up the display

        Set up the six GPIO lines to communicate with the display. This leverages the digitalio class to handle
        digital outputs on the GPIO lines. There is also an analogous class for analog IO.

        You need to make sure that the port mappings match the physical wiring of the display interface to the GPIO
        interface. Compatible with all versions of RPI as of Jan. 2019.
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
        self.lcd = character_lcd.Character_LCD_Mono(self.lcd_rs, self.lcd_en,
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
        """updateScreen - Convenience method used to update the message."""
        self.lcd.clear()
        self.lcd.message = message

    # End class ManagedDisplay definition


class CWMachine(StateMachine):
    """
    A state machine designed to display morse code messages blinking the red light for a dot, and the blue
    light for a dash.
    """

    # Our two LEDs, utilizing GPIO 18, and GPIO 23
    red_light = LED(18)
    blue_light = LED(23)

    # Set the contents of our messages
    message1 = 'SOS'
    message2 = 'OK'

    # keep track of the active message
    active_message = message1

    # endTransmission - flag used to determine whether we are shutting down
    end_transmission = False

    # Define these states for our machine.
    off = State(initial=True)  #  off - nothing lit up
    dot = State()  #  dot - red lit for 500ms
    dash = State()  #  dash - blue lit for 1500ms
    dot_dash_pause = State()  #  dotDashPause - dark for 250ms
    letter_pause = State()  #  letterPause - dark for 750ms
    word_pause = State()  #  wordPause - dark for 3000ms

    # Initialize our display
    screen_lcd = ManagedDisplay()

    # A dictionary of Morse Code - this is a utility that will allow us to convert any common string into Morse code.
    morse_dict = {
        "A": ".-", "B": "-...", "C": "-.-.", "D": "-..",
        "E": ".", "F": "..-.", "G": "--.", "H": "....",
        "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
        "M": "--", "N": "-.", "O": "---", "P": ".--.",
        "Q": "--.-", "R": ".-.", "S": "...", "T": "-",
        "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
        "Y": "-.--", "Z": "--..", "0": "-----", "1": ".----",
        "2": "..---", "3": "...--", "4": "....-", "5": ".....",
        "6": "-....", "7": "--...", "8": "---..", "9": "----.",
        "+": ".-.-.", "-": "-....-", "/": "-..-.", "=": "-...-",
        ":": "---...", ".": ".-.-.-", "$": "...-..-", "?": "..--..",
        "@": ".--.-.", "&": ".-...", "\"": ".-..-.", "_": "..--.-",
        "|": "--...-", "(": "-.--.-", ")": "-.--.-"
    }

    # do_dot - Event that moves between the off-state (all-lights-off) and a 'dot'
    do_dot = (
            off.to(dot) | dot.to(off)
    )

    # do_dash - Event that moves between the off-state (all-lights-off) and a 'dash'
    do_dash = (
            off.to(dash) | dash.to(off)
    )

    # do_ddp - Event that moves between the off-state (all-lights-off) and a pause between dots and dashes
    do_ddp = (
            off.to(dot_dash_pause) | dot_dash_pause.to(off)
    )

    # do_lp - Event that moves between the off-state (all-lights-off) and a pause between letters
    do_lp = (
            off.to(letter_pause) | letter_pause.to(off)
    )

    # do_wp - Event that moves between the off-state (all-lights-off) and a pause between words
    do_wp = (
            off.to(word_pause) | word_pause.to(off)
    )

    def on_enter_dot(self):
        """on_enter_dot - Action performed when the state machine transitions into the dot state"""
        self.red_light.blink(0.5, 0, 1, False)  # Red light comes on for 500ms

        if DEBUG:
            print("* Changing state to red - dot")

    def on_exit_dot(self):
        """on_exit_dot - Action performed when the statemachine transitions out of the red state."""
        self.red_light.off()  # Red light forced off

    def on_enter_dash(self):
        """on_enter_dash - Action performed when the state machine transitions into the dash state"""
        self.blue_light.blink(1.5, 0, 1, False)  # Blue light comes on for 1500ms

        if DEBUG:
            print("* Changing state to blue - dash")

    def on_exit_dash(self):
        """on_exit_dash - Action performed when the statemachine transitions out of the dash state."""
        self.blue_light.off()  # Blue light forced off

    @staticmethod
    def on_enter_dot_dash_pause():
        """on_enter_dotDashPause - Action performed when the state machine transitions into the dotDashPause state."""
        sleep(0.25)  # wait for 250ms

        if DEBUG:
            print("* Pausing Between Dots/Dashes - 250ms")

    def on_exit_dot_dash_pause(self):
        """on_exit_dot_dash_pause - Action performed when the statemachine transitions out of the dotDashPause state."""
        pass

    @staticmethod
    def on_enter_letter_pause():
        """on_enter_letter_pause - Action performed when the state machine transitions into the letterPause state."""
        sleep(0.75)  # wait for 750ms

        if DEBUG:
            print("* Pausing Between Letters - 750ms")

    def on_exit_letter_pause(self):
        """on_exit_letterPause - Action performed when the statemachine transitions out of the letterPause state."""
        pass

    @staticmethod
    def on_enter_word_pause():
        """on_enter_word_pause - Action performed when the state machine transitions into the wordPause state"""
        sleep(3)  # wait for 3000ms

        if DEBUG:
            print("* Pausing Between Words - 3000ms")

    def on_exit_word_pause(self):
        """on_exit_wordPause - Action performed when the statemachine transitions out of the wordPause state."""
        pass

    def toggle_message(self):
        """toggle_message - method used to switch between message1 and message2"""
        if self.active_message == self.message1:
            self.screen_lcd.update_screen(self.message2)
            self.active_message = self.message2
        else:
            self.screen_lcd.update_screen(self.message1)
            self.active_message = self.message1

        if DEBUG:
            print(f"* Toggling active message to: {self.active_message} ")

    def process_button(self):
        """
        processButton - Utility method used to send events to the state machine. The only thing this event does is
        trigger a change in the outgoing message
        """

        print('*** processButton')
        self.toggle_message()

    def run(self):
        """run - kickoff the transmit functionality in a separate execution thread"""
        my_thread = Thread(target=self.transmit)
        my_thread.start()

    def transmit(self):
        """transmit - utility method used to continuously send a message"""

        # Loop until we are shutdown
        while not self.end_transmission:

            # Display the active message in our 16x2 screen
            self.screen_lcd.update_screen(f"Sending:\n{self.active_message}")

            # Parse message for individual wordsTAM
            word_list = self.active_message.split()

            # Setup counter to determine time buffer after words
            len_words = len(word_list)
            words_counter = 1
            for word in word_list:

                # Setup counter to determine time buffer after letters
                len_word = len(word)
                word_counter = 1
                for char in word:

                    # Convert the character to its string in morse code
                    morse = self.morse_dict.get(char)

                    # Setup counter to determine time buffer after letters
                    len_morse = len(morse)
                    morse_counter = 1
                    for x in morse:
                        match x:
                            case '.':
                                self.on_enter_dot()
                                self.on_exit_dot()
                            case '-':
                                self.on_enter_dash()
                                self.on_exit_dash()

                        # If we are still sending process a dotDashPause event
                        if morse_counter <= len_morse:
                            morse_counter += 1
                            self.on_enter_dot_dash_pause()
                            self.on_exit_dot_dash_pause()

                    # If we are still sending process a letterPause event
                    if word_counter <= len_word:
                        word_counter += 1
                        self.on_enter_letter_pause()
                        self.on_exit_letter_pause()

                # If we are still sending process a wordPause event
                if words_counter <= len_words:
                    words_counter += 1
                    self.on_enter_word_pause()
                    self.on_exit_word_pause()

        # Cleanup the display i.e. clear it
        self.screen_lcd.cleanup_display()

    # End class CWMachine definition


# Initialize our State Machine, and begin transmission
cwMachine = CWMachine()
cwMachine.run()

# greenButton - set up our Button, tied to GPIO 24. Configure the action to be taken when the button is pressed to be
# the execution of the processButton function in our State Machine.
greenButton = Button(24)
greenButton.when_activated = cwMachine.toggle_message

# Setup loop variable
repeat = True
while repeat:  # Repeat until the user creates a keyboard interrupt (CTRL-C)
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
        cwMachine.end_transmission = True
        sleep(1)
