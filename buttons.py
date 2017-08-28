import threading
import time
import RPi.GPIO as GPIO
import urllib2


debounce = 10
button_0 = 5
button_1 = 6
sleep_time = 0.05
keep_out = 1



def action(button_number):
    if button_number == button_1:
        print ("BUTTON 1 Activated")
        urllib2.urlopen('http://127.0.0.1:5000/command/rotate')
    else:
        print ("BUTTON 0 Activated")
        urllib2.urlopen('http://127.0.0.1:5000/command/neo_off')
    return button_number



def read_button_task(stop_event):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(button_0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(button_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    count_button_0 = debounce
    count_button_1 = debounce
    while not stop_event.is_set():
        # Have buttons been pressed.
        if not GPIO.input(button_0):
            count_button_0 -= 1
        if not GPIO.input(button_1):
            count_button_1 -= 1

        if count_button_0 < 0:
            action(button_0)
            time.sleep(keep_out)
            count_button_0 = debounce
        if count_button_1 < 0:
            action(button_1)
            time.sleep(keep_out)
            count_button_1 = debounce
        #print("0 : {0}    1: {1}".format(count_button_0,count_button_1))
        time.sleep(sleep_time)
    print("=== Stopping Button Thread ===")



if __name__ == "__main__":
    # Tests
    running = threading.Event()
    test_thread = threading.Thread(name="testing", target=read_button_task, args=(running,))
    test_thread.start()
    time.sleep(30)
    running.set()