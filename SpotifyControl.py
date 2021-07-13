import web
import os
import sys
import configparser
import requests
import datetime

from time import sleep
import RPi.GPIO as GPIO

import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

version = 'v0.2.1'

class tokens:
    def __init__(self):
        refTokFile = open('./SpotifyControl/refresh.tk', 'r')
        self.refreshTk = refTokFile.readline()
        refTokFile.close()

        self.base64Tk = settings['Spotify']['base64Tk']

        self.authTk = None
        self.authExp = None
        self.update()

    def update(self):
        global lcd

        req = requests.post('https://accounts.spotify.com/api/token', data = {'grant_type':'refresh_token','refresh_token':self.refreshTk}, headers={'Authorization': f'Basic {self.base64Tk}'})
        try:
            self.authTk = req.json()['access_token']
            expiresIn = req.json()['expires_in']
            self.authExp = datetime.datetime.now() + datetime.timedelta(seconds=(expiresIn-60))
        except:
            lcd.clear()
            lcd.message = 'Error updating\ntokens'


    def check(self):
        try:
            if datetime.datetime.now() > self.authExp:
                self.update()
                print('Token updated')
            else:
                pass
        except TypeError:
            self.update()
            print('Token updated with None')

        return self.authExp - datetime.datetime.now()

    def changeRefreshTk(self, newRef, newAuth, expiresIn):
        print('entro')
        refTokFile = open('./SpotifyControl/refresh.tk', 'w')
        refTokFile.write(newRef)
        refTokFile.close()

        self.refreshTk = newRef
        self.authTk = newAuth
        self.authExp = datetime.datetime.now() + datetime.timedelta(seconds=(expiresIn-60))
        return

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
lcd.message = 'SpotifyControl\n'+version+' is ready!'

tkn = tokens()

urls = (
  '/', 'index',
  '/next', 'next',
  '/previous', 'previous',
  '/play', 'play',
  '/pause', 'pause',
  '/shuffle', 'shuffle',
  '/transferhere', 'transferHere',
  '/onevent', 'onEvent',
  '/authorized', 'authorized',
  '/like', 'like'
)

class index:
    def GET(self):
        global settings
        global version
        
        redirectUrl = settings['Device']['address'] + '/authorized'
        clientId = settings['Spotify']['clientId']
        changeUserUrl = f"https://accounts.spotify.com/authorize?client_id={clientId}&response_type=code&redirect_uri={redirectUrl}&scope=user-read-playback-state%20user-modify-playback-state%20playlist-modify-public%20playlist-modify-private"

        body = """<html>
            <body>
                <h2>SpotifyControl</h2>
                <h3>Version """ + version + """</h3>
                <p>Control the playback from Spotify on your Raspberry with simple HTTP requests!</p>
                <p>Current user: """ + "inserire nome" + """</p>
                <button onclick="document.location='""" + changeUserUrl + """'">Change user</p>
            </body>    
        </html>
        """
        return body

class player:
    def __init__(self):
        self.command = None
        self.message = None
        self.method = None

    def GET(self):
        global lcd
        global tkn
        global receivedPin

        screenList = ['next', 'previous']

        GPIO.output(receivedPin, GPIO.HIGH)

        if self.command in screenList:
            lcd.clear()
            lcd.message = self.message

        tkn.check()

        if self.method == 'POST':
            req = requests.post(f'https://api.spotify.com/v1/me/player/{self.command}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {tkn.authTk}'})
        elif self.method == 'PUT':
            req = requests.put(f'https://api.spotify.com/v1/me/player/{self.command}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {tkn.authTk}'})

        print(req)
        print(f'  with tk: {tkn.authTk[0:10]}, exp: {tkn.authExp}')

        GPIO.output(receivedPin, GPIO.LOW)

        return self.message

class next(player):
    def __init__(self):
        self.command = 'next'
        self.message = 'Next song'
        self.method = 'POST'

class previous(player):
    def __init__(self):
        self.command = 'previous'
        self.message = 'Previous song'
        self.method = 'POST'

class play(player):
    def __init__(self):
        self.command = 'play'
        self.message = 'Play'
        self.method = 'PUT'

class pause(player):
    def __init__(self):
        self.command = 'pause'
        self.message = 'Pause'
        self.method = 'PUT'

class shuffle:
    def GET(self):
        global lcd
        global tkn
        global receivedPin

        GPIO.output(receivedPin, GPIO.HIGH)

        tkn.check()

        reply = requests.get('https://api.spotify.com/v1/me/player', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {tkn.authTk}'})
        state = reply.json()['shuffle_state']

        if state:
            st = 'false'
        else:
            st = 'true'

        req = requests.put(f'https://api.spotify.com/v1/me/player/shuffle?state={st}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {tkn.authTk}'})

        print(req)
        print(f'  with tk: {tkn.authTk[0:10]}, exp: {tkn.authExp}')

        if state:
            GPIO.output(shufflePin, GPIO.LOW)
        else:
            GPIO.output(shufflePin, GPIO.HIGH)

        GPIO.output(receivedPin, GPIO.LOW)

        return 'Shuffle '+ st

class transferHere:
    def GET(self):
        global lcd
        global tkn
        global receivedPin
        global settings

        GPIO.output(receivedPin, GPIO.HIGH)

        lcd.clear()
        lcd.message = 'Transfer here'

        tkn.check()

        devName = settings['Device']['name']
        devId = None

        reply = requests.get('https://api.spotify.com/v1/me/player/devices', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {tkn.authTk}'})

        for elem in reply.json()['devices']:
            if elem['name'] == devName:
                devId = elem['id']

        if devId == None:
            return 'Name Not found'

        data = '{\"device_ids\":[\"'+str(devId)+'\"]}'

        req = requests.put('https://api.spotify.com/v1/me/player', data=data, headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {tkn.authTk}'})

        print(req)
        print(f'  with tk: {tkn.authTk[0:10]}, exp: {tkn.authExp}')

        GPIO.output(receivedPin, GPIO.LOW)

        return 'Transfer here'

class onEvent:
    def POST(self):
        global tkn

        screenEvents = ['start', 'change']
        playingEvents = ['start', 'playing']
        stopEvents = ['paused', 'stop']

        data = web.data().decode("utf-8").split(',')
        trackId = data[0]
        event = data[1]

        reply = requests.get('https://api.spotify.com/v1/me/player', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {tkn.authTk}'})

        shuffleState = reply.json()['shuffle_state']

        if shuffleState:
            GPIO.output(shufflePin, GPIO.HIGH)
        else:
            GPIO.output(shufflePin, GPIO.LOW)

        print(f'onEvent: {event}')

        if event in screenEvents:
            tkn.check()
            reply = requests.get(f'https://api.spotify.com/v1/tracks/{trackId}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {tkn.authTk}'})

            title = reply.json()['name']
            artist = reply.json()['artists'][0]['name']

            lcd.clear()
            lcd.message = f'{title}\n{artist}'

        elif event in playingEvents:
            GPIO.output(playingPin, GPIO.HIGH)
        elif event in stopEvents:
            GPIO.output(playingPin, GPIO.LOW)

        return 'onEvent'

class authorized:
    def GET(self):
        global tkn
        global lcd

        authCode = web.input('code').code
        base64Code = settings['Spotify']['base64Tk']
        redirectUrl = settings['Device']['address'] + '/authorized'

        reply = requests.post('https://accounts.spotify.com/api/token', data = {"grant_type":"authorization_code", "code":authCode, "redirect_uri":redirectUrl}, headers={'Authorization': f'Basic {base64Code}'})

        try:
            tkn.changeRefreshTk(reply.json()['refresh_token'], reply.json()['access_token'], reply.json()['expires_in'])
        except KeyError:
            return reply.text

        lcd.clear()
        lcd.message = 'Login completed!\nReady to play'

        return 'Login completed'

class like:
    def GET(self):
        global tkn
        global lcd
        global settings

        reply = requests.get('https://api.spotify.com/v1/me/player', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {tkn.authTk}'})
        trackId = reply.json()['item']['uri']

        playlistId = settings['Spotify']['playlistId']

        reply = requests.post(f'https://api.spotify.com/v1/playlists/{playlistId}/tracks?uris={trackId}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {tkn.authTk}'})

        if reply.ok:
            lcd.cursor_position(13,1)
            lcd.message = ' <3'
        else:
            lcd.clear()
            lcd.message = 'Track NOT added\nto favourites'



if __name__ == '__main__':
    GPIO.output(shufflePin, GPIO.HIGH)
    GPIO.output(receivedPin, GPIO.HIGH)
    sleep(1)
    GPIO.output(shufflePin, GPIO.LOW)
    GPIO.output(receivedPin, GPIO.LOW)

    app = web.application(urls, globals())
    app.run()