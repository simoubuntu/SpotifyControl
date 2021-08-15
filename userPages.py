import web
import requests

import RPi.GPIO as GPIO

import shared as sh

header = """<!doctype html>
<html lang='en'>
    <head>
        <meta charset='utf-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
    
        <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css' rel='stylesheet' integrity='sha384-KyZXEAg3QhqLMpG8r+8fhAXLRk2vvoC2f3B09zVXn8CA5QIVfZOJ3BCsw2P0p/We' crossorigin='anonymous'>
    
    </head>
    <body>
        <div class='container my-md-5 my-3' style='max-width: 720px;'>"""

footer = """        </div>
    </body>
</html>"""

class index:
    def GET(self):
        
        global header
        global footer
        
        redirectUrl = sh.settings['Device']['address'] + '/authorized'
        clientId = sh.settings['Spotify']['clientId']
        changeUserUrl = f"https://accounts.spotify.com/authorize?client_id={clientId}&response_type=code&redirect_uri={redirectUrl}&scope=user-read-playback-state%20user-modify-playback-state%20playlist-modify-public%20playlist-modify-private"

        body = header + """                <h2>SpotifyControl</h2>
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
        return body + footer

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

class editUser:
    def GET(self):
        try:
            attr = web.input().attribute
        except AttributeError:
            return 'No option selected'

        try:
            userId = int(web.input().userid)
            if userId > (len(sh.usr.users) - 1):
                return 'Wrong user selected'

        except AttributeError:
            return 'No user selected'

        if attr == 'name':
            attribute = 'Name'
        elif attr == 'credentials':
            attribute = 'Device Password'
        elif attr == 'playlist':
            attribute = 'Playlist ID'
        else:
            return 'Wrong attribute selected'

        content = f"""<html>
    <body>
        <h3>Edit <i>{attribute}</i></h3>
        <form action="storeuserattribute" method="post">
            <label>{attribute}</label>
            <input type='text' name='value'>
            <input type='text' name='attribute' value='{attr}' hidden>
            <input type='text' name='userid' value='{userId}' hidden>
            <input type="submit" value="Submit">
        </form>
    </body>
</html>"""

        return content
        
class storeUserAttribute:
    def POST(self):
        try:
            attr = web.input().attribute
        except AttributeError:
            return 'No option submitted'

        try:
            value = web.input().value
        except AttributeError:
            return 'No value submitted'

        try:
            userId = int(web.input().userid)
            if userId > (len(sh.usr.users) - 1):
                return 'Wrong user submitted'

        except AttributeError:
            return 'No user submitted'

        if attr == 'name':
            sh.usr.users[userId]['name'] = str(value)
        elif attr == 'credentials':
            sh.usr.users[userId]['devPassword'] = str(value)
        elif attr == 'playlist':
            sh.usr.users[userId]['playlistId'] = str(value)
        else:
            return 'Wrong attribute selected'

        sh.usr.save()

        return '<html>Saved!<br><a href="userlist">Back to user list</a></html>'

