import multiprocessing
import signal
import threading
import time

from flask import Flask
from flask import jsonify
from flask import render_template

strip_1_queue = multiprocessing.Queue()
strip_2_queue = multiprocessing.Queue()

def rotate(strip):
    while True:
        print('Strip {0} Hello'.format(strip))
        time.sleep(2)



def drive_strip(strip):
    def runner(queue):
        def stop_animation(signum, frame):
        #   threading.

            signal.signal(signal.SIGALRM, stop_animation)
        while True:
            command = queue.get()
            command(strip)
    return runner

def stop_both(proc_a,proc_b):
    time.sleep(30)
    proc_a.terminate()
    proc_b.terminate()


strip_1 = 1
strip_2 = 2


process_1 = multiprocessing.Process(target=drive_strip(strip_1), args=(strip_1_queue,))
process_2 = multiprocessing.Process(target=drive_strip(strip_2), args=(strip_2_queue,))


strip_1_queue.put(rotate)

process_1.start()
process_2.start()




app = Flask(__name__)

@app.route('/')
def index():
    strip_2_queue.put(rotate)
    all_threads = threading.enumerate()
    print (str(all_threads))
    return render_template('index.html', name='No Operation')

@app.route('/queue/<job>')
@app.route('/queue/<job>/<parameter>')
def neo_queue(job, parameter=None):
    if job == 'neo_off':
        print "Process 1 Terminate"
        process_1.terminate()
        process_1.join()
        print ("Process 1 Termination Status: {0}".format(process_1.is_alive()))
    elif job == 'neo_off2':
        stop_both(process_1,process_2)
    elif job == 'centre_fade':
        strip_1_queue.put(rotate)
        print "Would start process 1 again"


    return render_template('index.html', name='Command Queued')


app.run(host='0.0.0.0', debug=True)
