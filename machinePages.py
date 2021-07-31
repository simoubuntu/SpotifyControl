import web
import requests

import RPi.GPIO as GPIO

import shared as sh

class player:
    def __init__(self):
        self.command = None
        self.message = None
        self.method = None

    def GET(self):

        screenList = ['next', 'previous']

        GPIO.output(sh.receivedPin, GPIO.HIGH)

        if self.command in screenList:
            sh.lcd.clear()
            sh.lcd.message = self.message

        sh.tkn.check()

        if self.method == 'POST':
            req = requests.post(f'https://api.spotify.com/v1/me/player/{self.command}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'})
        elif self.method == 'PUT':
            req = requests.put(f'https://api.spotify.com/v1/me/player/{self.command}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'})

        print(req)
        print(f'  with tk: {sh.tkn.authTk[0:10]}, exp: {sh.tkn.authExp}')

        GPIO.output(sh.receivedPin, GPIO.LOW)

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

        GPIO.output(sh.receivedPin, GPIO.HIGH)

        sh.tkn.check()

        reply = requests.get('https://api.spotify.com/v1/me/player', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'})
        state = reply.json()['shuffle_state']

        if state:
            st = 'false'
        else:
            st = 'true'

        req = requests.put(f'https://api.spotify.com/v1/me/player/shuffle?state={st}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'})

        print(req)
        print(f'  with tk: {sh.tkn.authTk[0:10]}, exp: {sh.tkn.authExp}')

        if state:
            GPIO.output(sh.shufflePin, GPIO.LOW)
        else:
            GPIO.output(sh.shufflePin, GPIO.HIGH)

        GPIO.output(sh.receivedPin, GPIO.LOW)

        return 'Shuffle '+ st

class transferHere:
    def GET(self):

        GPIO.output(sh.receivedPin, GPIO.HIGH)

        sh.lcd.clear()
        sh.lcd.message = 'Transfer here'

        sh.tkn.check()

        devName = sh.settings['Device']['name']
        devId = None

        reply = requests.get('https://api.spotify.com/v1/me/player/devices', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'})

        for elem in reply.json()['devices']:
            if elem['name'] == devName:
                devId = elem['id']

        if devId == None:
            return 'Name Not found'

        data = '{\"device_ids\":[\"'+str(devId)+'\"]}'

        req = requests.put('https://api.spotify.com/v1/me/player', data=data, headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'})

        print(req)
        print(f'  with tk: {sh.tkn.authTk[0:10]}, exp: {sh.tkn.authExp}')

        GPIO.output(sh.receivedPin, GPIO.LOW)

        return 'Transfer here'

class onEvent:
    def POST(self):

        screenEvents = ['start', 'change']
        playingEvents = ['start', 'playing']
        stopEvents = ['paused', 'stop']

        data = web.data().decode("utf-8").split(',')
        trackId = data[0]
        event = data[1]

        reply = requests.get('https://api.spotify.com/v1/me/player', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'})

        shuffleState = reply.json()['shuffle_state']

        if shuffleState:
            GPIO.output(sh.shufflePin, GPIO.HIGH)
        else:
            GPIO.output(sh.shufflePin, GPIO.LOW)

        print(f'onEvent: {event}')

        if event in screenEvents:
            sh.tkn.check()
            reply = requests.get(f'https://api.spotify.com/v1/tracks/{trackId}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'})

            title = reply.json()['name']
            artist = reply.json()['artists'][0]['name']

            sh.lcd.clear()
            sh.lcd.message = f'{title}\n{artist}'

        elif event in playingEvents:
            GPIO.output(sh.playingPin, GPIO.HIGH)
        elif event in stopEvents:
            GPIO.output(sh.playingPin, GPIO.LOW)

        return 'onEvent'

class like:
    def GET(self):

        reply = requests.get('https://api.spotify.com/v1/me/player', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'})
        trackId = reply.json()['item']['uri']

        playlistId = sh.settings['Spotify']['playlistId']

        reply = requests.post(f'https://api.spotify.com/v1/playlists/{playlistId}/tracks?uris={trackId}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'})

        if reply.ok:
            sh.lcd.cursor_position(13,1)
            sh.lcd.message = ' <3'
        else:
            sh.lcd.clear()
            sh.lcd.message = 'Track NOT added\nto favourites'

class switchUser:
    def GET(self):

        name = sh.usr.switch()

        sh.lcd.clear()
        sh.lcd.message = f'User switched to\n{name}'

        return f'User switched to {name}'

