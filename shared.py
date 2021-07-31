import os
import sys
import configparser

import RPi.GPIO as GPIO

import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

import components as cm

version = 'v0.2.4'

settings = configparser.ConfigParser()
settings.read(os.path.join(sys.path[0], 'settings.conf'))

receivedPin = 11
shufflePin = 9
playingPin = 16

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(shufflePin, GPIO.OUT)
GPIO.setup(receivedPin, GPIO.OUT)
GPIO.setup(playingPin, GPIO.OUT)

# Modify this if you have a different sized character LCD
lcd_columns = 16
lcd_rows = 2

# compatible with all versions of RPI as of Jan. 2019
# v1 - v3B+
lcd_rs = digitalio.DigitalInOut(board.D22)
lcd_en = digitalio.DigitalInOut(board.D17)
lcd_d4 = digitalio.DigitalInOut(board.D25)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d6 = digitalio.DigitalInOut(board.D23)
lcd_d7 = digitalio.DigitalInOut(board.D10)

# Initialise the lcd class
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)

# wipe LCD screen before we start
lcd.clear()
# combine both lines into one update to the display
lcd.message = 'SpotifyControl\n' + version + ' is ready!'

usr = cm.user()
tkn = cm.tokens()

librespot = cm.libreSpotContainer()
librespot.activate(usr.current())
