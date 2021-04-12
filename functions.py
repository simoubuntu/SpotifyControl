import datetime
import requests

def updateToken(refreshTk, base64Tk):
    req = requests.post('https://accounts.spotify.com/api/token', data = {'grant_type':'refresh_token','refresh_token':refreshTk}, headers={'Authorization': f'Basic {base64Tk}'})

    authTk = req.json()['access_token']
    expiresIn = req.json()['expires_in']
    expiryTime = datetime.datetime.now() + datetime.timedelta(seconds=expiresIn)

    return authTk, expiryTime