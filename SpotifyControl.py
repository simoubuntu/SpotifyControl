import web
import os

import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

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
  '/previous', 'previous'
)

class index:
    def GET(self):
        return "SpotifyControl ver. 0.0"

class next:
    def GET(self):
        global lcd

        lcd.clear()
        lcd.message = 'Next song!'

        return 'Next song!'
    
class previous:
    def GET(self):
        global lcd

        lcd.clear()
        lcd.message = 'Previous song!'

        return 'Previous song!'

if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()