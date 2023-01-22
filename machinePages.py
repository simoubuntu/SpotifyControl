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

        # Screen list is split in toast and print lists.
        printList = ['next']
        toastList = ['previous']

        GPIO.output(sh.receivedPin, GPIO.HIGH)

        if self.command in printList:
            sh.disp.print(self.message)

        if self.command in toastList:
            sh.disp.toast(self.message)

        sh.tkn.check()

        try:
            if self.method == 'POST':
                req = requests.post(f'https://api.spotify.com/v1/me/player/{self.command}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'}, timeout = sh.requestsTimeout)
            elif self.method == 'PUT':
                req = requests.put(f'https://api.spotify.com/v1/me/player/{self.command}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'}, timeout = sh.requestsTimeout)
        except Exception as err:
            print(err)
            sh.disp.print('Connection error','Check internet!')
            GPIO.output(sh.receivedPin, GPIO.LOW)
            return

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

        try:
            reply = requests.get('https://api.spotify.com/v1/me/player', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'}, timeout = sh.requestsTimeout)
        except Exception as err:
            print(err)
            sh.disp.print('Connection error','Check internet!')
            GPIO.output(sh.receivedPin, GPIO.LOW)
            return

        state = reply.json()['shuffle_state']

        if state:
            st = 'false'
        else:
            st = 'true'

        try:
            req = requests.put(f'https://api.spotify.com/v1/me/player/shuffle?state={st}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'}, timeout = sh.requestsTimeout)
        except Exception as err:
            print(err)
            sh.disp.print('Connection error','Check internet!')
            GPIO.output(sh.receivedPin, GPIO.LOW)
            return

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

        sh.disp.activate()

        sh.disp.print('Transfer here')

        sh.tkn.check()

        devName = "Stereo " + sh.usr.current()['name']
        devId = None

        try:
            reply = requests.get('https://api.spotify.com/v1/me/player/devices', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'}, timeout = sh.requestsTimeout)
        except Exception as err:
            print(err)
            sh.disp.print('Connection error\nCheck internet!')
            GPIO.output(sh.receivedPin, GPIO.LOW)
            return

        for elem in reply.json()['devices']:
            if elem['name'] == devName:
                devId = elem['id']

        if devId == None:
            sh.disp.print('Device not found.','Try again!')
            return 'Name Not found'

        data = '{\"device_ids\":[\"'+str(devId)+'\"]}'

        try:
            req = requests.put('https://api.spotify.com/v1/me/player', data=data, headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'}, timeout = sh.requestsTimeout)
        except Exception as err:
            print(err)
            sh.disp.print('Connection error\nCheck internet!')
            GPIO.output(sh.receivedPin, GPIO.LOW)
            return

        print(req)
        print(f'  with tk: {sh.tkn.authTk[0:10]}, exp: {sh.tkn.authExp}')

        GPIO.output(sh.receivedPin, GPIO.LOW)

        return 'Transfer here'

class onEvent:
    def POST(self):

        screenEvents = ['started', 'changed']
        playingEvents = ['started', 'playing']
        stopEvents = ['paused', 'stopped']

        data = web.data().decode("utf-8").split(',')
        trackId = data[0]
        event = data[1]

        try: 
            reply = requests.get('https://api.spotify.com/v1/me/player', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'}, timeout = sh.requestsTimeout)
        except Exception as err:
            print(err)
            sh.disp.print('Connection error','Check internet!')
            return

        try:
            shuffleState = reply.json()['shuffle_state']

            if shuffleState:
                GPIO.output(sh.shufflePin, GPIO.HIGH)
            else:
                GPIO.output(sh.shufflePin, GPIO.LOW)
                
        except:
            print('Error while reading shuffle status')

        print(f'onEvent: {event}')

        if event in screenEvents:
            sh.tkn.check()

            try:
                reply = requests.get(f'https://api.spotify.com/v1/tracks/{trackId}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'}, timeout = sh.requestsTimeout)
            except Exception as err:
                print(err)
                sh.disp.print('Connection error','Check internet!')
                return

            title = reply.json()['name']
            artist = reply.json()['artists'][0]['name']

            sh.disp.print(title,artist)

        elif event in playingEvents:
            GPIO.output(sh.playingPin, GPIO.HIGH)
        elif event in stopEvents:
            GPIO.output(sh.playingPin, GPIO.LOW)

        return 'onEvent'

class like:
    def GET(self):

        GPIO.output(sh.receivedPin, GPIO.HIGH)

        try:
            reply = requests.get('https://api.spotify.com/v1/me/player', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'}, timeout = sh.requestsTimeout)
        except Exception as err:
            print(err)
            sh.disp.print('Connection error','Check internet!')
            GPIO.output(sh.receivedPin, GPIO.LOW)
            return

        trackId = reply.json()['item']['uri']

        playlistId = sh.settings['Spotify']['playlistId']

        try:
            reply = requests.post(f'https://api.spotify.com/v1/playlists/{playlistId}/tracks?uris={trackId}', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'}, timeout = sh.requestsTimeout)
        except Exception as err:
            print(err)
            sh.disp.print('Connection error','Check internet!')
            GPIO.output(sh.receivedPin, GPIO.LOW)
            return

        if reply.ok:
            sh.disp.toast('Track added','to favourites!',3)
        else:
            sh.disp.toast('Track NOT added','to favourites',5)
        
        GPIO.output(sh.receivedPin, GPIO.LOW)

class switchUser:
    def GET(self):
        
        sh.librespot.deactivate()

        try:
            redirect = web.input().redirect
            redString = f"""<html><head><meta http-equiv="refresh" content="0; URL='{redirect}'" /></head>\n"""
        
        except AttributeError:
            redString = ''

        try:
            id = int(web.input().id)
            name = sh.usr.switch(id)

        except AttributeError:
            name = sh.usr.switch()

        sh.librespot.activate(sh.usr.current())

        sh.disp.print(f'User switched to\n{name}')

        return redString + f'User switched to {name}'

class userInfo:
    def GET(self):
        
        pag = sh.disp.infoPage
        
        print('Ciao')

        if pag == 0:
            name = sh.usr.users[sh.usr.active]['name']
            sh.disp.toast('User name:',name,2)
            sh.disp.infoPage = 1

        if pag == 1:
            if (str(sh.usr.users[sh.usr.active]['username']) == 'None') | (str(sh.usr.users[sh.usr.active]['devPassword']) == 'None'):
                txt = 'Smth wrong :('
            else:
                txt = 'All good! :)'

            sh.disp.toast('Spotify creds:',txt,2)
            sh.disp.infoPage = 2
            
        if pag == 2:
            if str(sh.usr.users[sh.usr.active]['playlistId']) == 'None':
                txt = 'Not set :('
            else:
                txt = 'Set! :)'

            sh.disp.toast('Spotify creds:',txt,2)
            sh.disp.infoPage = 3

        if pag == 3:
            sh.disp.print('IP address:',str(sh.settings['Device']['address']))
            sh.disp.infoPage = 0

        #  TODO
        # if pag == 4:
        #     Restore current track info

        print(f'userInfo, page {pag}')

        return f'userInfo, page {pag}'