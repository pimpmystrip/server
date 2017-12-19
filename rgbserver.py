import os
import sys
import termios
import tty
import pigpio
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Global Brightness
bright = 255

# Colors
global red
global green
global blue

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
    brightness = int(brightness)

    if brightness < 0:
        brightness = 0
    if brightness > 255:
        brightness = 255

    realBrightness = int(int(brightness) * (float(bright) / 255.0))
    
    print(realBrightness)

    pi.set_PWM_dutycycle(pin, realBrightness)


@app.route('/')
def homepage():
    return 'Pi RGB Server'

@app.route('/currentColor')
def currentColor():
    col = {
        'r': red,
        'g': green,
        'b': blue
    }

    return jsonify(col)


@app.route('/set', methods=['POST'])
def setColor():
    global red, green, blue

    red = request.form['r']
    green = request.form['g']
    blue = request.form['b']

    setLights(RED_PIN, red)
    setLights(GREEN_PIN, green)
    setLights(BLUE_PIN, blue)

    return 'true'

if __name__ == '__main__':
    red = 0
    green = 30
    blue = 30

    setLights(RED_PIN, red)
    setLights(GREEN_PIN, green)
    setLights(BLUE_PIN, blue)

    app.debug = True
    app.run(host='0.0.0.0', port=8008)

# pi.stop()
