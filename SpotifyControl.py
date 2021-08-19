import web

from time import sleep
import RPi.GPIO as GPIO

import userPages        # IT IS USED! DO NOT REMOVE!
import machinePages     # IT IS USED! DO NOT REMOVE!
import shared

urls = (
  '/', 'userPages.index',
  '/next', 'machinePages.next',
  '/previous', 'machinePages.previous',
  '/play', 'machinePages.play',
  '/pause', 'machinePages.pause',
  '/shuffle', 'machinePages.shuffle',
  '/transferhere', 'machinePages.transferHere',
  '/onevent', 'machinePages.onEvent',
  '/authorized', 'userPages.authorized',
  '/like', 'machinePages.like',
  '/switchuser', 'machinePages.switchUser',
  '/userlist', 'userPages.userList',
  '/edituser', 'userPages.editUser',
  '/storeuserattribute', 'userPages.storeUserAttribute',
  '/deleteuser', 'userPages.deleteUser',
  '/adduser', 'userPages.addUser'
)

if __name__ == '__main__':
    GPIO.output(shared.shufflePin, GPIO.HIGH)
    GPIO.output(shared.receivedPin, GPIO.HIGH)
    sleep(1)
    GPIO.output(shared.shufflePin, GPIO.LOW)
    GPIO.output(shared.receivedPin, GPIO.LOW)

    app = web.application(urls, globals())
    app.run()