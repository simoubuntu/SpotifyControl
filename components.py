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

        try:
            req = requests.post('https://accounts.spotify.com/api/token', data = {'grant_type':'refresh_token','refresh_token':self.refreshTk}, headers={'Authorization': f'Basic {self.base64Tk}'}, timeout = sh.requestsTimeout)
        except Exception as err:
            print(err)
            sh.lcd.clear()
            sh.lcd.message = 'Connection error\nCheck internet!'
            return

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

        try:
            reply = requests.get('https://api.spotify.com/v1/me', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {sh.tkn.authTk}'}, timeout = sh.requestsTimeout)
        except Exception as err:
            print(err)
            sh.lcd.clear()
            sh.lcd.message = 'Connection error\nCheck internet!'
            return

        curUsr = dict()
        curUsr['name'] = name
        curUsr['refTkn'] = refTkn
        curUsr['playlistId'] = None
        curUsr['username'] = reply.json()['id']
        curUsr['devPassword'] = None

        self.users.append(curUsr)

        self.save()

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

    def delete(self, id):
        usr = self.users.pop(id)

        self.save()

        return usr['name'] 

class libreSpotContainer:
    def __init__(self):
        self.status = False

        return
    
    def activate(self, curUsr):
        self.instance = subprocess.Popen(["/usr/bin/librespot", "--name", f"Stereo {curUsr['name']}", "--device-type", "speaker", "--backend", "alsa", "--bitrate", "320", "--disable-audio-cache", "--enable-volume-normalisation", "--volume-ctrl", "linear", "--initial-volume", "100", "--username", curUsr['username'], "--password", curUsr['devPassword'], "--onevent", sh.settings['Device']['onEventPath']])
        self.status = True

        return
    def deactivate(self):
        self.instance.terminate()
        self.status = False

        return

def generateNavbar(pageTitle, backUrl, additionalButtons = None) -> str:
    """generateNavbar creates the HTML code for a customizable navbar

    Args:
        pageTitle (str): string containing the page title
        backUrl (str): string containing the url for the back button
        additionalButtons (tuple or list of tuples, optional): information for the optional buttons. Format (text, url, color).

    Raises:
        TypeError: exception raised when the third argument is not a tuple or a list.

    Returns:
        str: HTML code for the navbar
    """   

    cont = f"""
    <nav class='nav nav-pills py-1 mb-3'>
        <a class='btn btn-light ms-1 me-2' href='{backUrl}'><i class="fas fa-chevron-circle-left me-2"></i>Back</a>
        <div class='vr'></div>
        <h3 class='my-auto mx-4'>{pageTitle}</h3>"""

    if type(additionalButtons) is tuple:
        cont = cont + f"""
        <div class='vr'></div>
        <a class='btn btn-{additionalButtons[2]} ms-2' href='{additionalButtons[1]}'>{additionalButtons[0]}</a>
        """
    elif type(additionalButtons) is list:
        cont = cont + f"""
        <div class='vr'></div>"""

        for ab in additionalButtons:
            cont = cont + f"""
            <a class='btn btn-{ab[2]} ms-2' href='{ab[1]}'>{ab[0]}</a>
            """
    elif additionalButtons == None:
        pass
        
    else:
        raise TypeError

    cont = cont + """
    </nav>
    """

    return cont
