import threading
import Queue
import logging
import time
import random
from neopixel import *

# Meter routines for NeoPixels

def random_meter(strip,start,end,term_event,set_color,unset_color,hold_time=.3):
	term_event.clear()  # will be set by others when we should stop
	last_top = start
	while not term_event.is_set():
		value = random.random()
		top = int((end-start)*value)+start
		while (top != last_top) & (not term_event.is_set()):
			if top > last_top:
				last_top += 1
			else:
				last_top -= 1
			for i in range(start,last_top):
				strip.setPixelColor(i,set_color)
			for i in range(last_top,end):
				strip.setPixelColor(i,unset_color)
			if term_event.wait(hold_time):
				break
			else:
				strip.show()


def value_meter(strip,value,start,end,set_color,unset_color):
	top = int((end-start)*value/(end-start))+start
	for i in range(start,top):
		strip.setPixelColor(i,set_color)
	for i in range(top,end):
		strip.setPixelColor(i,unset_color)
	strip.show()