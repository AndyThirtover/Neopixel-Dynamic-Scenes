from flask import Flask
from flask import render_template
import threading
import logging
import time
from neojobs import *

# Kick off the worker for neopixel jobs.
neo_thread = threading.Thread(name='NeoDaemon', target=neo_queue, args=[neo_event,])
neo_thread.setDaemon(True)
neo_thread.start()

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html', name='No Operation')

@app.route('/wipe')
def wipe():
    neo_jobs.put('rotate')
    neo_event.set()
    return render_template('index.html', name='Wipe Complete', count=COUNT)

@app.route('/alarm')
def do_alarm():
    neo_jobs.put('alarm')
    neo_event.set()
    return render_template('index.html', name='Alarm')

@app.route('/off')
def off():
    neo_jobs.put('neo_off')
    neo_event.set()
    return render_template('index.html', name='Neo Pixels Off')

@app.route('/centre')
def centre():
    neo_jobs.put('centre_fade')
    neo_event.set()
    return render_template('index.html', name='Centre Fade')

@app.route('/fade_out')
def fadetozero():
    neo_jobs.put('fade_out')
    neo_event.set()
    return render_template('index.html', name='Fade Out')

@app.route('/quarter/<segment>')
def do_quarter(segment):
    quarter(segment,Color(MAX,0,0))
    return render_template('index.html', name='Quarter')

@app.route('/queue/<job_name>')
def do_queue(job_name):
    neo_jobs.put(job_name)
    neo_event.set()
    return render_template('index.html', name='Job Queued:' + job_name)



