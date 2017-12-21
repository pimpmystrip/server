const Gpio = require('pigpio').Gpio;
const { Led, RGBLed } = require('pigpio-components');
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const app = express();
const http = require('http').Server(app);
const io = require('socket.io')(http);
const port = 8008;

const rgbLed = new RGBLed({ red: 17, green: 22, blue: 24 });
const redLed = new Led(17);
const greenLed = new Led(22);
const blueLed = new Led(24);

app.use(bodyParser.json())
app.use(cors());

/* Global Variables */
let currentColor = {
    r: 0,
    g: 255,
    b: 100
};

let globalBrightness = 255;

let fadeColorsInterval, fadeLightsInterval;

redLed.setValue(currentColor.r);
greenLed.setValue(currentColor.g);
blueLed.setValue(currentColor.b);

/* Socket.IO */
io.on('connection', socket => {
    console.log('User connected'); 
    socket.emit('updateColor', currentColor);

    socket.on('disconnect', () => {
        console.log('User disconnected');
    })
})

/* Get Methods */
app.get('/', (req, res) => res.send('RGB Server!'));

app.get('/currentColor', (req, res) => {
    roundColor(currentColor);
    res.json(currentColor)
})

app.get('/state', (req, res) => {
    roundColor(currentColor);

    const state = {
        color: currentColor,
        brightness: globalBrightness
    }

    res.json(state)
})

/* Post Methods */
app.post('/brightness', (req, res) => {
    
    globalBrightness = Math.round(req.body.brightness);

    setLights("red", currentColor.r);
    setLights("green", currentColor.g);
    setLights("blue", currentColor.b);

    res.json(true)
})

app.post('/set', (req, res) => {
    killIntervals();

    currentColor = {
        r: req.body.r,
        g: req.body.g,
        b: req.body.b
    };

    setLights("red", currentColor.r);
    setLights("green", currentColor.g);
    setLights("blue", currentColor.b);

    res.json(true);
})

app.post('/fade', (req, res) => {
    fadeLights(req.body.color, req.body.duration);

    res.json(true);
})

app.post('/fadeColors', (req, res) => {
    if(fadeColorsInterval) {
        clearInterval(fadeColorsInterval);
    }

    let faderColors = req.body.colors;
    let fcLength = faderColors.length;
    let ctr = 0;

    fadeLights(faderColors[ctr++ % fcLength], req.body.duration);
   
    fadeColorsInterval = setInterval(() => {
        if(faderColors.length === 0) {
            clearInterval(fadeColorsInterval);
            return;
        }
        fadeLights(faderColors[ctr++ % fcLength], req.body.duration);
    }, req.body.interval * 1000)
    
    res.json(true);
})

/* Server Subroutines */
function setLights(color, brightness) {
    let realBrightness = brightness * (globalBrightness / 255);
    if(realBrightness > 255) realBrightness = 255;
    if(realBrightness < 0) realBrightness = 0;
    
    realBrightness = Math.round(realBrightness);
    brightness = Math.round(brightness);

    if(color == "red") {
        redLed.setValue(realBrightness)
    }

    if(color == "green") {
        greenLed.setValue(realBrightness)
    }

    if(color == "blue") {
        blueLed.setValue(realBrightness)
    }
    
    io.sockets.emit('updateColor', currentColor);
}

function fadeLights(destColor, duration) {
    // Duration in ms
    let redStep = (destColor.r - currentColor.r) / duration;
    let greenStep = (destColor.g - currentColor.g) / duration;
    let blueStep = (destColor.b - currentColor.b) / duration;

    if(fadeLightsInterval) {
        clearInterval(fadeLightsInterval);
    }

    let fadeInterval = null;
    
    let ctr = 0;

    fadeLightsInterval = setInterval(() => {
        if(ctr >= duration) {
            clearInterval(fadeInterval);
            return;
        }

        currentColor.r += redStep;
        currentColor.g += greenStep;
        currentColor.b += blueStep;
        
        setLights("red", currentColor.r);
        setLights("green", currentColor.g);
        setLights("blue", currentColor.b);

        ++ctr;
    }, 1)

}

function killIntervals() {
    console.log('Killing intervals');

    if(fadeLightsInterval) {
        clearInterval(fadeLightsInterval);
    }

    if(fadeColorsInterval) {
        clearInterval(fadeColorsInterval);
    }
}

function roundColor(color) {
    color.r = Math.round(color.r);
    color.g = Math.round(color.g);
    color.b = Math.round(color.b);
}

http.listen(port, () => console.log(`Server listening on port ${port}`));
