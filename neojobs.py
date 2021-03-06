import threading
import Queue
import logging
import time
from neopixel import *
from meter import *
import random
import yaml


MAX = 0
config = {}


def read_config(config):
    with open ('neopixels.yaml', 'r') as cfgfile:
        config = yaml.load(cfgfile)

    if not config.has_key('LED_COUNT'):
        config['LED_COUNT'] = 18
    if not config.has_key('LED_PIN'):
        config['LED_PIN'] = 18
    if not config.has_key('LED_STRIP'):
        config['LED_STRIP'] = ws.WS2811_STRIP_GRB
    if not config.has_key('MAX'):
        config['MAX'] = 127
    return config

config = read_config(config)
MAX=config['MAX']

def write_config(config):
    rfile = open('neopixels.yaml','w')
    rfile.write(yaml.dump(config))
    rfile.close()

def process_neo_config(formargs):
    for key, value in formargs.iteritems():
        if 'submit' in key:
            pass
        else: 
            config[key] = int(value)

    if formargs.has_key('LED_COUNT'):
        config['LED_COUNT'] = int(formargs['LED_COUNT'])
    if formargs.has_key('MAX'):
        config['MAX'] = int(formargs['MAX'])
        global MAX
        MAX = int(formargs['MAX'])

    write_config(config)


def config_strip1(config):
    # LED strip 1 configuration:
    LED_COUNT   = config['LED_COUNT']      # Number of LED pixels.
    LED_PIN     = 18     # GPIO pin connected to the pixels (must support PWM!).
    LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA     = 5       # DMA channel to use for generating signal (try 5)
    LED_INVERT  = False   # True to invert the signal (when using NPN transistor level shift)
    #LED_STRIP   = ws.SK6812_STRIP_GBRW
    LED_STRIP   = ws.WS2811_STRIP_GRB
    return Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, 255, 0, LED_STRIP)


#LED strip 2 Configuration

LED2_COUNT   = 24      # Number of LED pixels.
LED2_PIN     = 13      # GPIO pin connected to the pixels (must support PWM!).
LED2_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED2_DMA     = 6       # DMA channel to use for generating signal (try 5)
LED2_INVERT  = False   # True to invert the signal (when using NPN transistor level shift)
LED2_STRIP   = ws.WS2811_STRIP_GRB


RED = Color(128,0,0)
AMBER = Color(128,40,0)
GREEN = Color(0,128,0)
RUN_BLUE = Color(16,96,192)

thread_data = {'count' : 0, 
            'max_brightness' : MAX
            }

# Create NeoPixel object with appropriate configuration.
strip1=config_strip1(config)
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

def red_alarm(strip, event, highlight, background, wait_ms=50):
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


def alarm_cycle(strip, event, highlight, span=3, wait_ms=5):
    previous = []
    for i in range(strip.numPixels()):
        if not event.is_set():
            this_Color = strip.getPixelColor(i)
            previous.append({i:this_Color})
            strip.setPixelColor(i,highlight)
            #print("len {0}, span {1}, wait {2}".format(len(previous),span,wait_ms))
            if len(previous) == span:
                first_previous = previous.pop(0)
                strip.setPixelColor(first_previous.keys()[0], first_previous.values()[0])
            strip.show()
            time.sleep(wait_ms/1000.0)
        else:
            break
    for item in previous:
        if not event.is_set():
            strip.setPixelColor(item.keys()[0],item.values()[0])
            strip.show()
            time.sleep(wait_ms/1000.0)

def alarm(strip, event, highlight, span=4, wait_ms=5):
    event.clear()
    while not event.is_set():
        alarm_cycle(strip,event,highlight,span,wait_ms)


def int_to_rgb(n):
    b = (n & 0xff0000) >> 16
    g = (n & 0x00ff00) >> 8
    r = (n & 0x0000ff)
    return (r, g, b)

def colour_floor(r,g,b,distance,ratio):
    fade = (ratio*1.0)/MAX
    return Color(light_floor(g*fade,distance,g),light_floor(r*fade,distance,r),light_floor(b*fade,distance,b))


def light_floor(value,distance,max=MAX,shallow=True):
    if shallow :
        intensity = value - (distance*2)
    else:
        intensity = value - (distance*distance)
    if intensity < 0:
        return 0
    elif intensity > max:
        return max
    else:
        return int(intensity)

def centre_fade(strip,r,g,b,wait_ms=5):
    for j in range(MAX*2):
        for i in range(72):
            if not strip1_event.is_set():
                l = colour_floor(r,g,b,i,j)
                strip.setPixelColor(72+i,l)
                strip.setPixelColor(71-i,l)
                strip.show()
            else:
                break

def centre_static(strip,r,g,b, ratio=150):
    for i in range ((strip.numPixels()/2)+1):
        strip.setPixelColor((strip.numPixels()/2)+i,colour_floor(g,r,b,i,ratio))
        strip.setPixelColor((strip.numPixels()/2)-i,colour_floor(g,r,b,i,ratio))
        strip.show()

def blend_int(c,t,step,steps):
    return int(c*(steps-step)/steps) + int(t*step/steps)

def blend_colour(current,target,step,steps):
    rc = current >> 16 & 0xff 
    gc = current >> 8 & 0xff
    bc = current >> 0 & 0xff
    rt = target >> 16 & 0xff
    gt = target >> 8 & 0xff
    bt = target >> 0 & 0xff
    return Color(
            blend_int(rc,rt,step,steps),
            blend_int(gc,gt,step,steps),
            blend_int(bc,bt,step,steps)
        )


def blend_pixel_value(strip,i,left,right):
    return int((left*(strip.numPixels()-i))/strip.numPixels()) + int(right*i/strip.numPixels())
    #print("BV: {0}, LEFT:{1}, RIGHT{2}, INDEX{3}".format(bv,left,right,i))
    #return bv

def blend_to_end(strip,left_colour, right_colour):
    rl = left_colour >> 16 & 0xff 
    gl = left_colour >> 8 & 0xff
    bl = left_colour >> 0 & 0xff
    rr = right_colour >> 16 & 0xff
    gr = right_colour >> 8 & 0xff
    br = right_colour >> 0 & 0xff
    for i in range(strip.numPixels()):
        strip.setPixelColor(i,Color(
                blend_pixel_value(strip,i,rl,rr),
                blend_pixel_value(strip,i,gl,gr),
                blend_pixel_value(strip,i,bl,br))
            )
        strip.show()

def not_zero(a,b,c):
    if (a-1) > 0 or (b-1) > 0 or (c-1) > 0:
        return True
    else:
        return False

def fade_out(strip):
    run = True
    while run:
        run = False
        for i in range(strip.numPixels()):
            current = strip.getPixelColor(i)
            r,g,b = int_to_rgb(current)
            strip.setPixelColor(i,Color(light_floor(r,1),light_floor(g,1),light_floor(b,1)))
            if not_zero(r,g,b):
                run = True
        strip.show()

def random_change(strip,web_param,wait_ms=5):
    strip_seq = []
    for i in range(strip.numPixels()):
        strip_seq.append(i)
    random.shuffle(strip_seq)

    if web_param == 'random':
        new_colour = Color(random.randint(0,128),random.randint(0,128),random.randint(0,128))
    elif web_param == 'red':
        new_colour = RED
    elif web_param == 'amber':
        new_colour = AMBER
    elif web_param == 'green':
        new_colour = GREEN
    elif web_param == 'run':
        new_colour = RUN_BLUE
    elif web_param == 'wash':
        new_colour = Color(config['CWRED'],config['CWGREEN'],config['CWBLUE'])
    else:
        new_colour = Color(2,0,0)


    for p in strip_seq:
        strip.setPixelColor(p,new_colour)
        strip.show()
        time.sleep(wait_ms/1000.0)

def random_pastel(strip,wait_ms=5):
    strip_seq = []
    for i in range(strip.numPixels()):
        strip_seq.append(i)
    random.shuffle(strip_seq)
    for p in strip_seq:
        strip.setPixelColor(p,Color(random.randint(16,192),random.randint(16,140),random.randint(0,32)))
        strip.show()
        time.sleep(wait_ms/1000.0)



def fade_one(strip,event,target_pixel,steps=8):
    current_Color = strip.getPixelColor(target_pixel)
    target_Color = Color(random.randint(16,192),random.randint(16,140),random.randint(0,32))
    for i in range(0,steps):
        if not event.is_set():
            blend = blend_colour(current_Color,target_Color,i,steps)
            strip.setPixelColor(target_pixel,blend)
            strip.show() 
        else:
            break

def twinkle(strip,event,wait_ms=5):
    event.clear()
    while not event.is_set():
        random_pastel(strip,wait_ms)

def twinkle_fade(strip,event,wait_ms=5):
    event.clear()
    #print ("called with wait: {0}".format(wait_ms))
    strip_seq = []
    for i in range(strip.numPixels()):
        strip_seq.append(i)
    random.shuffle(strip_seq)

    while not event.is_set():
        for p in strip_seq:
            if not event.is_set():
                fade_one(strip1,event,p)
                time.sleep(wait_ms/1000.0)
            else:
                break

