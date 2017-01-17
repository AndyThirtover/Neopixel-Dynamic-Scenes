from flask import Flask
from flask import jsonify
from flask import render_template
import threading
import logging
import time
from neojobs import *

app = Flask(__name__)

@app.route('/')
def hello_world():
    all_threads = threading.enumerate()
    print (str(all_threads))
    return render_template('index.html', name='No Operation')

@app.route('/json_data')
def json_data():
    global thread_data
    return jsonify(**thread_data)

@app.route('/meter/<stripnumber>/<value>/<start>/<end>')
def do_meter(stripnumber,value,start=0,end=12):
    strips = [strip1,strip2]
    value_meter(strips[int(stripnumber)],int(value),int(start),int(end),Color(255,0,0),Color(8,0,0))
    return render_template('index.html', name='No Operation')


@app.route('/queue/<job>')
def neo_queue(job):
    if job == 'neo_off':
        neoOff(strip1,strip1_event)
    elif job == 'neo_off2':
        neoOff(strip2,strip2_event)
    elif job == 'centre_fade':
        strip1_event.clear()
        centre_fade(strip1,128,128,64)
    elif 'quarter' in job:
        strip1_event.clear()
        quarter(strip1,job[-1],Color(MAX,0,0))
    elif job == 'rotate':
        neoOff(strip1,strip1_event)
        rotate_thread = threading.Thread(name='Rotate',
                                         target=rotate,
                                         args=(strip1,strip1_event,))
        rotate_thread.start()

    elif job == 'alarm':
        neoOff(strip1,strip1_event)
        alarm_thread = threading.Thread(name='Alarm',
                                        target=alarm,
                                        args=(strip1,strip1_event,Color(255,0,0),Color(8,0,0)))
        alarm_thread.start()

    elif job == 'fade_out':
        strip1_event.set()
        fade_thread = threading.Thread(name='FadeOut',
                                        target=fade_out,
                                        args=(strip1,))
        fade_thread.start()

    elif job == 'meter':
        meter_thread = threading.Thread(name='Meter',
                                        target=random_meter,
                                        args=(strip2,12,24,strip2_event,Color(0,MAX,0),Color(1,0,1),))
        meter_thread.start()

    elif job == 'meter2':
        meter2_thread = threading.Thread(name='Meter',
                                        target=random_meter,
                                        args=(strip2,0,12,strip2_event,Color(MAX/2,0,MAX/2),Color(2,0,0),0.9,))
        meter2_thread.start()
    return render_template('index.html', name='Job Queued:' + job)
