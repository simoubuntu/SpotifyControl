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

        <script src="https://kit.fontawesome.com/c28bad8915.js" crossorigin="anonymous"></script>
    
    </head>
    <body>
        <div class='container my-md-5 my-3' style='max-width: 720px;'>
"""

footer = """        </div>
    </body>
</html>"""

symbols = dict()

symbols['ok'] = '<i class="fas fa-check-circle text-success"></i>'
symbols['wrong'] = '<i class="fas fa-times-circle text-danger"></i>'
symbols['delete'] = '<i class="fas fa-trash text-danger"></i>'
symbols['toggleOn'] = '<i class="fas fa-toggle-on text-success"></i>'
symbols['toggleOff'] = '<i class="fas fa-toggle-off text-secondary"></i>'
symbols['forbidden'] = '<i class="fas fa-slash text-secondary"></i>'
symbols['edit'] = '<i class="fas fa-pencil-alt"></i>'

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
                <div class='row'>
                    <a href='userlist' class='btn btn-primary col-sm-4' tabindex='-1' role='button' aria-disabled='true'>Manage users</a>
                </div>
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

        global header
        global footer
        global symbols

        content = header + """                
            <nav class='nav nav-pills py-1 mb-3'>
                <a class='btn btn-light ms-1 me-2' href='..'><i class="fas fa-chevron-circle-left me-2"></i>Back</a>
                <div class='vr'></div>
                <h3 class='my-auto mx-4'>User list</h3>
                <div class='vr'></div>
                <a class='btn btn-primary ms-2' href='newuser'><i class="fas fa-plus-circle me-2"></i>Add new user</a>
            </nav>
            <div class='table-responsive'>
                <table class='table table-striped table-hover'>
                    <caption>Click or touch the symbols to edit properties</caption>
                        <thead>
                            <tr>
                                <th scope='col'>#</th>
                                <th scope='col' class='text-end'>Active</th>
                                <th scope='col'>Name</th>
                                <th scope='col' class='text-center'>Token</th>
                                <th scope='col' class='text-center'>Credentials</th>
                                <th scope='col' class='text-center'>Playlist</th>
                                <th scope='col' class='text-center'>Delete</th>
                            </tr>
                        </thead>
                        <tbody>
                        """
        
        rowCount = 0
        for u in sh.usr.users:

            if (str(u['username']) == 'None') | (str(u['devPassword']) == 'None'):
                cred = symbols['wrong']
                activeToggle = symbols['forbidden']
            else:
                cred = symbols['ok']
                activeToggle = f'<a href="switchuser?id={rowCount}&redirect=userlist">' + symbols['toggleOff'] + '</a>'

            if rowCount == sh.usr.active:
                # strActive = " class='table-primary'"
                strActive = ''
                activeToggle = symbols['toggleOn']
            else:
                strActive = ''

            content = content + f"    <tr{strActive}>\n               <th scope='row'>{rowCount+1}</th>"
            content = content + f"                  <td class='text-end h4'>{activeToggle}</td>\n"
            content = content + f"                  <td><a href='edituser?attribute=name&userid={rowCount}'>{u['name']} {symbols['edit']}</a></td>\n"



            if str(u['refTkn']) == 'None':
                tk = symbols['wrong']
            else:
                tk = symbols['ok']
            content = content + f"                  <td class='text-center'>{tk}</td>\n"

            # Credentials check moved up to avoid the activation of a user without device password
            content = content + f"                  <td class='text-center'><a href='edituser?attribute=credentials&userid={rowCount}'>{cred}</a></td>\n"

            if str(u['playlistId']) == 'None':
                pl = symbols['wrong']
            else:
                pl = symbols['ok']
            content = content + f"                  <td class='text-center'><a href='edituser?attribute=playlist&userid={rowCount}'>{pl}</a></td>\n"

            content = content + f"                                <td class='text-center'><a href='deleteuser?id={rowCount}'>{symbols['delete']}</a></td>                         </tr>\n"

            rowCount += 1

        content = content + """                        </tbody>
                    </table>
                </div>
"""

        return content + footer

class editUser:
    def GET(self):

        global header
        global footer
        
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
            oldValue = sh.usr.users[userId]['name']
            fieldType = 'text'

        elif attr == 'credentials':
            attribute = 'Device Password'
            oldValue = ''
            fieldType = 'password'

        elif attr == 'playlist':
            attribute = 'Playlist ID'
            oldValue = sh.usr.users[userId]['playlistId']
            if oldValue == None:
                oldValue = ''
            fieldType = 'text'

        else:
            return 'Wrong attribute selected'

        content = header + f"""
            <nav class='nav nav-pills py-1 mb-3'>
                <a class='btn btn-light ms-1 me-2' href='userlist'><i class="fas fa-chevron-circle-left me-2"></i>Back</a>
                <div class='vr'></div>
                <h3 class='my-auto mx-4'>Edit <i>{attribute}</i></h3>
            </nav>
        <div class='col-sm-6 col-md-4'>
        <form action='storeuserattribute' method='post'>
            <div class='mb-3'>
                <label class='form-label' for='inputfield'>{attribute}</label>
                <input class='form-control' type='{fieldType}' name='value' value='{oldValue}' placeholder='{attribute}' id='inputfield'>
            </div>
            <input type='text' name='attribute' value='{attr}' hidden>
            <input type='text' name='userid' value='{userId}' hidden>
            <div class='mb-3'>
                <a href='userlist' class='btn btn-secondary'>Back</a>
                <input class='btn btn-primary' type='submit' value='Submit'>
            </div>
        </form></div>""" + footer

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
        
        return """<html><head><meta http-equiv="refresh" content="1; URL='userlist'" /></head>\n<body>Saved!</body></html>"""

class deleteUser:
    def GET(self):
        try:
            id = int(web.input().id)

            reply = sh.usr.delete(id)

            return f'User {reply} deleted successfully!'

        except AttributeError:
            return 'No user id submitted'

        except IndexError:
            return 'Id out of range. Check it please.'