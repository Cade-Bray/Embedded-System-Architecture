#
# DisplayTest.py - This is the Python code that will be used to test
# the configuration of our display.
#
# This code works with the test circuit that was built for the 
# Module 4 Lab.
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1          Initial Development
#------------------------------------------------------------------

##
## We need to pull in the datetime and sleep objects so that we can 
## read the date and time from the operating system. 
##
from datetime import datetime
from time import sleep

##
## These are the packages that we need to pull in so that we can work
## with the GPIO interface on the Raspberry Pi board and work with
## the 16x2 LCD display
##
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

##
## cleanupDisplay - Method used to cleanup the digitalIO lines that
## are used to run the display.
##
## Arguments - lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7 as
## represented by the placeholder variables a, b, c, d, e, f
##
def cleanupDisplay(a, b, c, d, e, f):
    # Clear the LCD first - otherwise we won't be abe to update it.
    lcd.clear()
    a.deinit()
    b.deinit()
    c.deinit()
    d.deinit()
    e.deinit()
    f.deinit()
    

# Modify this if you have a different sized character LCD
lcd_columns = 16
lcd_rows = 2

##
## Setup the six GPIO lines to communicate with the display.
## This leverages the digitalio class to handle digital 
## outputs on the GPIO lines. There is also an analagous
## class for analog IO.
##
## You need to make sure that the port mappings match the
## physical wiring of the display interface to the 
## GPIO interface.
##
## compatible with all versions of RPI as of Jan. 2019
##
lcd_rs = digitalio.DigitalInOut(board.D17)
lcd_en = digitalio.DigitalInOut(board.D27)
lcd_d4 = digitalio.DigitalInOut(board.D5)
lcd_d5 = digitalio.DigitalInOut(board.D6)
lcd_d6 = digitalio.DigitalInOut(board.D13)
lcd_d7 = digitalio.DigitalInOut(board.D26)

# Initialise the lcd class
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                      lcd_d7, lcd_columns, lcd_rows)

# wipe LCD screen before we start
lcd.clear()

##
## Configure our loop variable
##
repeat = True
while repeat:
    try:

        ## Uncomment the following line and then comment out 
        ## lcd_line_1 = 'Happy\n' in order to set the 
        ## first line of the display to represent the date
        ## and time. Month, Day, Hour, Minute, Second
        ## lcd_line_1 = datetime.now().strftime('%b %d  %H:%M:%S\n')
        lcd_line_1 = 'Happy\n'
        lcd_line_2 = 'Display Day!'

        # combine both lines into one update to the display
        lcd.message = lcd_line_1 + lcd_line_2

        ## Refresh the time every second
        sleep(1)
    except KeyboardInterrupt:
        ##
        ## When the user enters CTRL-C at the console, cleanup the
        ## GPIO pins and exit.
        ##
        cleanupDisplay(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7)
        repeat = False