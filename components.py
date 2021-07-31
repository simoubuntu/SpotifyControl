import requests
import datetime
import subprocess

import shared as sh

class tokens:
    def __init__(self):

        try:
            self.refreshTk = sh.usr.current()['refTkn']
        except:
            self.refreshTk = None
        
        self.base64Tk = sh.settings['Spotify']['base64Tk']

        self.authTk = None
        self.authExp = None

        if self.refreshTk != None:
            self.update()

        return

    def update(self):

        req = requests.post('https://accounts.spotify.com/api/token', data = {'grant_type':'refresh_token','refresh_token':self.refreshTk}, headers={'Authorization': f'Basic {self.base64Tk}'})
        try:
            self.authTk = req.json()['access_token']
            expiresIn = req.json()['expires_in']
            self.authExp = datetime.datetime.now() + datetime.timedelta(seconds=(expiresIn-60))
        except:
            sh.lcd.clear()
            sh.lcd.message = 'Error updating\ntokens'


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
    
    def change(self, newRef):

        self.refreshTk = newRef

        self.update()

        return

class user:
    def __init__(self):

        self.active = None
        self.users = list()

        try:
            usersFile = open('./SpotifyControl/users.db', 'r')

            self.active = int(usersFile.readline()[:-1])

            while True:

                curUsr = dict()
                curUsr['name'] = usersFile.readline()[:-1]
                curUsr['refTkn'] = usersFile.readline()[:-1]
                curUsr['playlistId'] = usersFile.readline()[:-1]
                curUsr['username'] = usersFile.readline()[:-1]
                curUsr['devPassword'] = usersFile.readline()[:-1]

                if curUsr['name'] == '':
                    break

                self.users.append(curUsr)

            usersFile.close()

        except FileNotFoundError:
            usersFile = open('./SpotifyControl/users.db', 'w')
            usersFile.write(' ')
            usersFile.close()
            sh.lcd.message = 'No users. Go to\n' + sh.settings['Device']['address']

        except ValueError:
            usersFile = open('./SpotifyControl/users.db', 'w')
            usersFile.write(' ')
            usersFile.close()
            sh.lcd.message = 'Bad users db. Go to\n' + sh.settings['Device']['address']

        return

    def save(self):

        usersFile = open('./SpotifyControl/users.db', 'w')

        usersFile.write(str(self.active) + '\n')

        for u in self.users:
            usersFile.write(str(u['name']) + '\n')
            usersFile.write(str(u['refTkn']) + '\n')
            usersFile.write(str(u['playlistId']) + '\n')
            usersFile.write(str(u['username']) + '\n')
            usersFile.write(str(u['devPassword']) + '\n')

        usersFile.close()

        return

    def add(self, name, refTkn):

        reply = requests.get('https://api.spotify.com/v1/me', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'})

        curUsr = dict()
        curUsr['name'] = name
        curUsr['refTkn'] = refTkn
        curUsr['playlistId'] = None
        curUsr['username'] = reply.json()['id']
        curUsr['devPassword'] = None

        self.users.append(curUsr)

        self.save()

        self.switch('last')

        return

    def switch(self, target = None):
        # The procedure automatically goes to the next user in the list. Use target variable to customize this behaviour

        if target == None:
            if (self.active + 1) == len(self.users):
                self.active = 0

            else:
                self.active += 1

        elif target == 'last':
            self.active = len(self.users) - 1

        elif target not in range(len(self.users)):
            raise IndexError

        else:
            self.active = target

        sh.tkn.refreshTk = self.users[self.active]['refTkn']
        sh.tkn.update()

        self.save()

        return self.users[self.active]['name']

    def current(self):
        result = self.users[self.active]

        return result

class libreSpotContainer:
    def __init__(self):
        self.status = False

        return
    
    def activate(self, curUsr):
        self.instance = subprocess.Popen(["/usr/bin/librespot", "--name", f"Stereo {curUsr['name']}", "--device-type", "speaker", "--backend", "alsa", "--bitrate", "320", "--disable-audio-cache", "--enable-volume-normalisation", "--volume-ctrl", "linear", "--initial-volume", "100", "--username", curUsr['username'], "--password", curUsr['devPassword'], "--onevent", "/home/pi/SpotifyControl/onevent.sh"])
        self.status = True

        return
    def deactivate(self):
        self.instance.terminate()
        self.status = False

        return