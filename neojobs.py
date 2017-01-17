import threading
import Queue
import logging
import time
from neopixel import *
from meter import *


# LED strip 2 configuration:
LED_COUNT   = 24      # Number of LED pixels.
LED_PIN     = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA     = 5       # DMA channel to use for generating signal (try 5)
LED_INVERT  = False   # True to invert the signal (when using NPN transistor level shift)
LED_STRIP   = ws.SK6812_STRIP_GBRW


#LED strip 2 Configuration

LED2_COUNT   = 24      # Number of LED pixels.
LED2_PIN     = 13      # GPIO pin connected to the pixels (must support PWM!).
LED2_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED2_DMA     = 6       # DMA channel to use for generating signal (try 5)
LED2_INVERT  = False   # True to invert the signal (when using NPN transistor level shift)
LED2_STRIP   = ws.WS2811_STRIP_GRB

MAX = 255

thread_data = {'count' : 0, 
            'max_brightness' : MAX
            }

# Create NeoPixel object with appropriate configuration.
strip1 = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, 255, 0, LED_STRIP)
strip2 = Adafruit_NeoPixel(LED2_COUNT, LED2_PIN, LED2_FREQ_HZ, LED2_DMA, LED2_INVERT, 255, 1, LED2_STRIP)
# Intialize the library (must be called once before other functions).
strip1.begin()
strip2.begin()

neo_jobs = Queue.Queue()  # This is the queue to drop neo jobs onto
strip1_event = threading.Event()
strip2_event = threading.Event()

def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        if not strip1_event.is_set():
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
        else:
            break

def neoOff(strip,event):
    event.set() # tell other threads to stop
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
        strip.show()
    event.set()

def rotate(strip,event):
    event.clear()
    global thread_data
    COUNT = thread_data['count']
    while not event.is_set():
        colorWipe(strip, Color(MAX, 0, 0))  # Red wipe
        colorWipe(strip, Color(0, MAX, 0))  # Blue wipe
        colorWipe(strip, Color(0, 0, MAX))  # Green wipe
        COUNT += 3
        thread_data.update({'count' : COUNT})

def quarter(strip,segment,value):
    seg=int(segment)
    for i in range((seg-1)*(strip.numPixels()/4),seg*(strip.numPixels()/4)):
        strip.setPixelColor(i,value)
        strip.show()

def alarm(strip, event, highlight, background, wait_ms=50):
	event.clear()
	while not event.is_set():
		for i in range(strip.numPixels()):
			for j in range(strip.numPixels()):
				if (j==i):
					strip.setPixelColor(j,highlight)
				else:
					strip.setPixelColor(j,background)
				strip.show()
		    	time.sleep(wait_ms/1000.0)


def int_to_rgb(n):
    b = (n & 0xff0000) >> 16
    g = (n & 0x00ff00) >> 8
    r = (n & 0x0000ff)
    return (r, g, b)

def colour_floor(r,g,b,distance,ratio):
    fade = (ratio*1.0)/MAX
    return Color(light_floor(g*fade,distance,g),light_floor(r*fade,distance,r),light_floor(b*fade,distance,b))


def light_floor(value,distance,max=MAX):
    intensity = value - (distance*distance)
    if intensity < 0:
        return 0
    elif intensity > max:
        return max
    else:
        return int(intensity)

def centre_fade(strip,r,g,b,wait_ms=5):
    for j in range(MAX*2):
        for i in range(12):
            if not strip1_event.is_set():
                l = colour_floor(r,g,b,i,j)
                strip.setPixelColor(12+i,l)
                strip.setPixelColor(11-i,l)
                strip.show()
            else:
                break

def not_zero(a,b,c):
    if (a-1) > 0 or (b-1) > 0 or (c-1) > 0:
        return True
    else:
        return False

def fade_out(strip):
    run = True
    while run:
        run = False
        for i in range(LED_COUNT):
            current = strip.getPixelColor(i)
            r,g,b = int_to_rgb(current)
            strip.setPixelColor(i,Color(light_floor(r,1),light_floor(g,1),light_floor(b,1)))
            if not_zero(r,g,b):
                run = True
        strip.show()


