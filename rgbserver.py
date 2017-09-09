import os
import sys
import termios
import tty
import pigpio
import time
from flask import Flask, request

app = Flask(__name__)

# Pin numbers
RED_PIN = 17
GREEN_PIN = 22
BLUE_PIN = 24

pi = pigpio.pi()


def updateColor(color, step):
    color += step

    if color > 255:
        return 255
    if color < 0:
        return 0

    return color


def setLights(pin, brightness):
    if brightness < 0:
        brightness = 0
    if brightness > 255:
        brightness = 255

        pi.set_PWM_dutycycle(pin, int(realBrightness))


@app.route('/')
def homepage():
    return 'Pi RGB Server'


@app.route('/set', methods=['POST'])
def setColor():
    color = request.get_json()
    print(color)
    setLights(RED_PIN, color['r'])
    setLights(GREEN_PIN, color['g'])
    setLights(BLUE_PIN, color['b'])

    return 'true'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008)

# pi.stop()
