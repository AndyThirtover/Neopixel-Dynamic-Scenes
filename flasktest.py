from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
import threading
import logging
import time
import random
from neojobs import *

app = Flask(__name__)

def do_config(formargs):
    global config
    config_change = False
    for key, value in formargs.iteritems():
        if 'submit' in key:
            pass
        else: 
            config[key] = int(value)

    if formargs.has_key('LED_COUNT'):
        config['LED_COUNT'] = int(formargs['LED_COUNT'])
        config_change = True
    if formargs.has_key('MAX'):
        config['MAX'] = int(formargs['MAX'])
        global MAX
        MAX = int(formargs['MAX'])
        config_change = True

    if config_change:
        write_config(config)

def neo_queue(job, parameter=None):
    if job == 'neo_off':
        neoOff(strip1,strip1_event)
    elif job == 'neo_off2':
        neoOff(strip2,strip2_event)
    elif job == 'centre_fade':
        global config
        strip1_event.clear()
        centre_static(strip1,config['CWRED'],config['CWGREEN'],config['CWBLUE'],config['CWRATIO'])
    elif job == 'centre_fade2':
        strip1_event.clear()
        centre_static(strip1,128,128,254)
    elif job == 'centre_fade3':
        strip1_event.clear()
        centre_static(strip1,254,128,128)
    elif 'quarter' in job:
        neoOff(strip1,strip1_event)
        quarter(strip1,parameter,Color(MAX,0,0))
    elif job == 'rotate':
        neoOff(strip1,strip1_event)
        rotate_thread = threading.Thread(name='Rotate',
                                         target=rotate,
                                         args=(strip1,strip1_event,))
        rotate_thread.start()

    elif job == 'alarm':
        neoOff(strip1,strip1_event)

        if parameter == 'check':
            bgcolour = Color(4,4,0)
            fgcolour = Color(0,128,0)
            timing = 500
        else:
            bgcolour = Color(8,0,0)
            fgcolour = Color(255,0,0)
            timing = 50

        alarm_thread = threading.Thread(name='Alarm',
                                        target=alarm,
                                        args=(strip1,strip1_event,fgcolour,bgcolour,timing))

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

    elif 'random_change' in job:
        strip1_event.set()
        speed = 5
        if not parameter:
            parameter = "random"
        random_change_thread = threading.Thread(name='RandomChange',
                                        target=random_change,
                                        args=(strip1,parameter,speed))
        random_change_thread.start()


@app.route('/')
def hello_world():
    all_threads = threading.enumerate()
    print (str(all_threads))
    return render_template('index.html', name='No Operation')

@app.route('/config')
def show_config():
    do_config(request.args)
    return render_template('config.html', name='No Operation')

@app.route('/json_data')
def json_data():
    global thread_data
    return jsonify(**thread_data)

@app.route('/json_config')
def json_config():
    global config
    return jsonify(**config)

@app.route('/meter/<stripnumber>/<value>')
@app.route('/meter/<stripnumber>/<value>/<start>/<end>')
def do_meter(stripnumber,value,start=0,end=12):
    strips = [strip1,strip2]
    value_meter(strips[int(stripnumber)],int(value),int(start),int(end),Color(255,0,0),Color(8,0,0))
    return render_template('index.html', name='No Operation')


@app.route('/queue/<job>')
@app.route('/queue/<job>/<parameter>')
def index_do(job, parameter=None):
    neo_queue(job,parameter)
    return render_template('index.html', name='Job Queued:' + job)

@app.route('/command')
@app.route('/command/<job>')
@app.route('/command/<job>/<parameter>')
def command_queue(job="NoJob", parameter=None):
    neo_queue(job,parameter)
    return render_template('command.html', name='Job Queued:' + job)

@app.route('/docs')
def show_docs():
    return render_template('docs.html', name='Show Docs')


app.run(host='0.0.0.0', debug=True)
