import web
import requests

import RPi.GPIO as GPIO

import shared as sh

class index:
    def GET(self):
        
        redirectUrl = sh.settings['Device']['address'] + '/authorized'
        clientId = sh.settings['Spotify']['clientId']
        changeUserUrl = f"https://accounts.spotify.com/authorize?client_id={clientId}&response_type=code&redirect_uri={redirectUrl}&scope=user-read-playback-state%20user-modify-playback-state%20playlist-modify-public%20playlist-modify-private"

        body = """<html>
            <body>
                <h2>SpotifyControl</h2>
                <h3>Version """ + sh.version + """</h3>
                <p>Control the playback from Spotify on your Raspberry with simple HTTP requests!</p>
                <p>Current user: """ + "inserire nome" + """</p>
                <div>
                    <h3>Add new user</h3>
                    <form action='""" + changeUserUrl + """'>
                        <label>User name</label>
                        <input type='text' name='state'>
                        <input type='text' name='client_id' value='""" + clientId + """' hidden>
                        <input type='text' name='response_type' value='code' hidden>
                        <input type='text' name='redirect_uri' value='""" + redirectUrl + """' hidden>
                        <input type='text' name='scope' value='user-read-playback-state%20user-modify-playback-state%20playlist-modify-public%20playlist-modify-private' hidden>
                        <input type="submit" value="Submit">
                    </form>
                </div>
            </body>    
        </html>
        """
        return body

class authorized:
    def GET(self):

        authCode = web.input().code
        userName = web.input().state
        base64Code = sh.settings['Spotify']['base64Tk']
        redirectUrl = sh.settings['Device']['address'] + '/authorized'

        reply = requests.post('https://accounts.spotify.com/api/token', data = {"grant_type":"authorization_code", "code":authCode, "redirect_uri":redirectUrl}, headers={'Authorization': f'Basic {base64Code}'})

        try:
            sh.usr.add(userName, reply.json()['refresh_token'])

        except KeyError:
            return reply.text

        sh.lcd.clear()
        sh.lcd.message = 'Login completed!\nReady to play'

        return f'Login completed for {userName}'

