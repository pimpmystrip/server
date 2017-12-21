import os
import sys
import termios
import tty
import pigpio
import time
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

# Global Brightness
global bright
bright = 255

# Colors
global red
global green
global blue

# Pin numbers
RED_PIN = 17
GREEN_PIN = 22
BLUE_PIN = 24

global forceStop
forceStop = False

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
    
    pi.set_PWM_dutycycle(pin, realBrightness)

@app.route('/')
def homepage():
    return 'Pi RGB Server'

@app.route('/currentColor', methods=['GET'])
def currentColor():
    col = {
        'r': red,
        'g': green,
        'b': blue
    }

    return jsonify(col)

@app.route('/state', methods=['GET'])
def getState():
    col = {
        'r': red,
        'g': green,
        'b': blue
    }

    state = {
        'color': col,
        'brightness': bright
    }

    return jsonify(state)

@app.route('/brightness', methods=['POST'])
def setBrightness():
    global bright
    
    content = request.get_json()
    bright = content['brightness']

    if bright > 255:
        bright = 255
    if bright < 0:
        bright = 0

    setLights(RED_PIN, red)
    setLights(GREEN_PIN, green)
    setLights(BLUE_PIN, blue)

    return 'true'

@app.route('/fade', methods=['POST'])
def fadeColors():
    content = request.get_json()
    
    forceStop = True
    duration = content['duration']
    interval = content['interval']
    faderColors = content['colors']
    
    ctr = 0
    time.sleep(0.05)
    forceStop = False
    while(True):
        if forceStop:
            break
        
        color = faderColors[ctr % len(faderColors)]
        fadeColor(color, duration)

        ctr = ctr + 1
        time.sleep(interval)

    return 'true'

@app.route('/set', methods=['POST'])
def setColor():
    global red, green, blue
    
    content = request.get_json()

    red = content['r']
    green = content['g']
    blue = content['b']

    color = {
        'r': content['r'],
        'g': content['g'],
        'b': content['b']
    }

    #fadeColor(color, 250)

    setLights(RED_PIN, red)
    setLights(GREEN_PIN, green)
    setLights(BLUE_PIN, blue)

    return 'true'

def fadeColor(color, duration):
    global red, green, blue
    
    redInterval = (color['r'] - red) / float(duration)
    greenInterval = (color['g'] - green) / float(duration)
    blueInterval = (color['b'] - blue) / float(duration)

    print(redInterval, greenInterval, blueInterval)
 
    for i in range(0, duration):
        red += redInterval
        green += greenInterval
        blue += blueInterval

        setLights(RED_PIN, red)
        setLights(GREEN_PIN, green)
        setLights(BLUE_PIN, blue)

        time.sleep(0.001)

    red = int(red)
    green = int(green)
    blue = int(blue)


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
