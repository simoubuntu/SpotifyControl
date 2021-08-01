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
        name = web.input().state
        base64Code = sh.settings['Spotify']['base64Tk']
        redirectUrl = sh.settings['Device']['address'] + '/authorized'

        reply = requests.post('https://accounts.spotify.com/api/token', data = {"grant_type":"authorization_code", "code":authCode, "redirect_uri":redirectUrl}, headers={'Authorization': f'Basic {base64Code}'})

        try:
            sh.usr.add(name, reply.json()['refresh_token'])

        except KeyError:
            return reply.text

        sh.lcd.clear()
        sh.lcd.message = 'Login completed!\nReady to play'

        return f'Login completed for {name}'

class userList:
    def GET(self):
        content = """<html>
            <body>
                <h3>User list</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Token</th>
                            <th>Credentials</th>
                            <th>Playlist</th>
                            <th></th>
                            <th></th>
                        </tr>
                    </thead>"""
        for u in sh.usr.users:
            content = content + "       <tbody>\n           <tr>\n"
            content = content + f"              <td>{u['name']}</td>\n"

            if str(u['refTkn']) == 'None':
                tk = 'Err'
            else:
                tk = 'OK'
            content = content + f"              <td>{tk}</td>\n"

            if (str(u['username']) == 'None') | (str(u['devPassword']) == 'None'):
                cred = 'Err'
            else:
                cred = 'OK'
            content = content + f"              <td>{cred}</td>\n"

            if str(u['playlistId']) == 'None':
                pl = 'Empty'
            else:
                pl = 'OK'
            content = content + f"              <td>{pl}</td>\n"

            content = content + f"                            <td><i>Delete</i></td>                         </tr>\n"

        content = content + """                    </tbody>
                </table>
            </body>
        </html>"""

        return content

