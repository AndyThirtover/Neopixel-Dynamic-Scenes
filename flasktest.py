from flask import Flask
from flask_socketio import SocketIO
from flask import jsonify
from flask import render_template
from flask import request
import threading
import logging
import time
import random
from neojobs import *
from buttons import *
import atexit

button_event = threading.Event()
button_thread = threading.Thread(name="Button_Handler", target=read_button_task, args=(button_event,))


def create_app():
    flapp = Flask(__name__)

    def interrupt():
        print ("Shutting down Button Thread")
        global button_thread
        button_thread.set()

    def start_button():
        global button_thread
        button_thread.start()

    start_button()
    atexit.register(interrupt)
    return flapp

app = create_app()
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def do_config(formargs):
    global config
    global buttons
    for key, value in formargs.iteritems():
        if 'submit' in key:
            if value == 'SYSTEM':
                process_neo_config(formargs)
            if value == 'BUTTONS':
                process_button_config(formargs)


def neo_queue(job, parameter=None):
    if job == 'neo_off':
        neoOff(strip1,strip1_event)
    elif job == 'neo_off2':
        neoOff(strip2,strip2_event)
    elif job == 'centre_fade':
        strip1_event.set()
        centre_static(strip1,config['CWRED'],config['CWGREEN'],config['CWBLUE'],config['CWRATIO'])
    elif job == 'centre_fadew2':
        strip1_event.set()
        centre_static(strip1,config['CWRED2'],config['CWGREEN2'],config['CWBLUE2'],config['CWRATIO2'])
    elif job == 'centre_fade2':
        strip1_event.set()
        centre_static(strip1,128,128,254)
    elif job == 'centre_fade3':
        strip1_event.set()
        centre_static(strip1,254,128,128)
    elif 'quarter' in job:
        neoOff(strip1,strip1_event)
        quarter(strip1,parameter,Color(MAX,0,0))
    elif 'blend' in job:
        strip1_event.set()
        blend_to_end(strip1,
            Color(config['CWRED'],config['CWGREEN'],config['CWBLUE']),
            Color(config['CWRED2'],config['CWGREEN2'],config['CWBLUE2']))
    elif 'random_pastel' in job:
        strip1_event.set()
        random_pastel(strip1)
    elif job == 'rotate':
        #neoOff(strip1,strip1_event)
        strip1_event.set()
        rotate_thread = threading.Thread(name='Rotate',
                                         target=rotate,
                                         args=(strip1,strip1_event,))
        rotate_thread.start()

    elif job == 'alarm':
        print("Alarm Parameter: {0}".format(parameter))
        if parameter == 'colour=green':
            fgcolour = Color(0,255,0)
            span = 10
            timing = 200
        else:
            fgcolour = Color(255,0,0)
            span = 4
            timing = 50

        alarm_thread = threading.Thread(name='Alarm',
                                        target=alarm,
                                        args=(strip1,strip1_event,fgcolour,span,timing))

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

    elif 'twinkle' in job:
        strip1_event.set()
        speed = 5
        if parameter:
            speed = int(parameter)
        if job == 'twinkle':
            twinkle_change_thread = threading.Thread(name='Twinkle',
                                        target=twinkle,
                                        args=(strip1,strip1_event,speed))
        if job == 'twinkle_fade':
            twinkle_change_thread = threading.Thread(name='Twinkle_Fade',
                                        target=twinkle_fade,
                                        args=(strip1,strip1_event,speed))
        twinkle_change_thread.start()


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

@app.route('/button_config')
def button_config():
    global buttons
    return jsonify(**buttons)

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

@app.route('/contact')
def show_contact():
    return render_template('contact.html', name='Show Contact Page')

@app.route('/action')
def show_action():
    return render_template('action.html', name='SocketIO Action Page')

@socketio.on('connect')
def handle_connect():
    print ("==================== Accepted Connection")
    socketio.emit('accept', {'name':'NeoPixel Driver'})

@socketio.on('message')
def handle_message(message):
    print('===================== Received message: ' + repr(message))
    socketio.emit('message',{'status':'good'})

@socketio.on('get_count')
def handle_get_count(message):
    global thread_data
    print('===================== Received message: ' + repr(message))
    socketio.emit('count_update',{'count': thread_data['count']})




socketio.run(app, host='0.0.0.0', debug=True)
