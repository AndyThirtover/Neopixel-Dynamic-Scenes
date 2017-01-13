import threading
import Queue
import logging
import time
from neopixel import *
from meter import *


# LED strip configuration:
LED_COUNT   = 24      # Number of LED pixels.
LED_PIN     = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA     = 5       # DMA channel to use for generating signal (try 5)
LED_INVERT  = False   # True to invert the signal (when using NPN transistor level shift)

MAX = 128
COUNT = 0

NEO_RUN = True

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT)
# Intialize the library (must be called once before other functions).
strip.begin()

neo_jobs = Queue.Queue()  # This is the queue to drop neo jobs onto
neo_event = threading.Event()

def neo_queue(neo_event):
    while NEO_RUN:
        if neo_event.wait(.1):
            neo_event.clear()
            time.sleep(.5)
            job = neo_jobs.get()
            print ('Queued:' + str(job))
            if job == 'neo_off':
                neoOff(strip)
            elif job == 'centre_fade':
                centre_fade(strip,128,128,64)
            elif job == 'rotate':
                rotate()
            elif job == 'alarm':
                alarm(Color(0,255,0),Color(0,8,0))
            elif job == 'fade_out':
                fade_out(strip)
            elif job == 'meter':
                meter_thread = threading.Thread(name='Meter',
                                                target=random_meter,
                                                args=(strip,12,24,neo_event,Color(0,MAX,0),Color(1,0,1),))
                meter_thread.start()

            elif job == 'meter2':
                meter2_thread = threading.Thread(name='Meter',
                                                target=random_meter,
                                                args=(strip,0,12,neo_event,Color(MAX/2,0,MAX/2),Color(2,0,0),0.9,))
                meter2_thread.start()




def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        if not neo_event.is_set():
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
        else:
            break

def neoOff(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
        strip.show()

def rotate():
    global COUNT
    while not neo_event.is_set():
        colorWipe(strip, Color(MAX, 0, 0))  # Red wipe
        colorWipe(strip, Color(0, MAX, 0))  # Blue wipe
        colorWipe(strip, Color(0, 0, MAX))  # Green wipe
        COUNT += 3
        #print ("Rotate Called ")

def quarter(segment,value):
    neoOff(strip)
    seg=int(segment)
    for i in range((seg-1)*(strip.numPixels()/4),seg*(strip.numPixels()/4)):
        strip.setPixelColor(i,value)
        strip.show()

def alarm(highlight, background, wait_ms=50):
	while not neo_event.is_set():
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
            if not neo_event.is_set():
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
    while run and (not neo_event.is_set()):
        run = False
        for i in range(LED_COUNT):
            current = strip.getPixelColor(i)
            r,g,b = int_to_rgb(current)
            strip.setPixelColor(i,Color(light_floor(r,1),light_floor(g,1),light_floor(b,1)))
            if not_zero(r,g,b):
                run = True
        strip.show()


