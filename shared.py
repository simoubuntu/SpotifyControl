import os
import sys
import configparser

import RPi.GPIO as GPIO

import components as cm

version = 'v0.3.9'

settings = configparser.ConfigParser()
settings.read(os.path.join(sys.path[0], 'settings.conf'))

receivedPin = 11
shufflePin = 9
playingPin = 16

requestsTimeout = 10

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(shufflePin, GPIO.OUT)
GPIO.setup(receivedPin, GPIO.OUT)
GPIO.setup(playingPin, GPIO.OUT)

disp = cm.screenManager()

disp.splash('SpotifyControl', version + ' is ready!')

usr = cm.user()
tkn = cm.tokens()

librespot = cm.libreSpotContainer()
librespot.activate(usr.current())
