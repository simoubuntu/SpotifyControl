import web
import os
import configparser
import requests
import datetime
import functions as fn

import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

class tokens:
    def __init__(self, refreshTk, base64Tk):
        self.refreshTk = refreshTk
        self.base64Tk = base64Tk
        self.authTk = None
        self.authExp = None
        self.update()

    def update(self):
        req = requests.post('https://accounts.spotify.com/api/token', data = {'grant_type':'refresh_token','refresh_token':self.refreshTk}, headers={'Authorization': f'Basic {self.base64Tk}'})

        self.authTk = req.json()['access_token']
        expiresIn = req.json()['expires_in']
        self.authExp = datetime.datetime.now() + datetime.timedelta(seconds=(expiresIn-60))


    def check(self):
        if datetime.datetime.now() > self.authExp:
            self.update()
        else:
            pass

settings = configparser.ConfigParser()
settings.read('settings.conf')
tkn = tokens(settings['Spotify']['refreshTk'],settings['Spotify']['base64Tk'])

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
lcd_d7 = digitalio.DigitalInOut(board.D18)

# Initialise the lcd class
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)

# wipe LCD screen before we start
lcd.clear()
# combine both lines into one update to the display
lcd.message = 'web.py\ninitialized'

urls = (
  '/', 'index',
  '/next', 'next',
  '/previous', 'previous',
  '/play', 'play',
  '/pause', 'pause'
)

class index:
    def GET(self):
        return "SpotifyControl ver. 0.0"

class next:
    def GET(self):
        global lcd
        global tkn
        
        lcd.clear()
        lcd.message = 'Next song!'

        req = requests.post('https://api.spotify.com/v1/me/player/next', data = {'grant_type':'refresh_token','refresh_token':tkn.refreshTk}, headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {tkn.authTk}'})

        return req.text
    
class previous:
    def GET(self):
        global lcd

        lcd.clear()
        lcd.message = 'Previous song!'

        return 'Previous song!'

if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()