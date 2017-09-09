import os
import sys
import termios
import tty
import pigpio
import time

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
	realBrightness = int(brightness)
	pi.set_PWM_dutycycle(pin, realBrightness)

setLights(RED_PIN, 63)
setLights(GREEN_PIN, 81)
setLights(BLUE_PIN, 181)

time.sleep(0.5)
pi.stop()
