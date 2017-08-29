import threading
import time
import RPi.GPIO as GPIO
import urllib2


# debounce is number of times that sleep_time need to have passed to consider the button pressed.
# keep_out is the time before another button press can be processed.
debounce = 4
sleep_time = 0.05
keep_out = 0.5

buttons = {
            '5':{'url':'http://127.0.0.1:5000/command/neo_off', 'debounce':debounce},
            '6':{'url':'http://127.0.0.1:5000/command/rotate', 'debounce':debounce}
            }


def action(button):
    print ("BUTTON at Pin {0} Activated".format(button))
    try:
        urllib2.urlopen(buttons[button]['url'])
    except:
        print ("FAILED URL: {0}".format(buttons[button]['url']))


def read_button_task(stop_event):
    GPIO.setmode(GPIO.BCM)
    for button in buttons:
        GPIO.setup(int(button), GPIO.IN, pull_up_down=GPIO.PUD_UP)
    while not stop_event.is_set():
        # Have buttons been pressed.
        for button in buttons:
            if not GPIO.input(int(button)):
                buttons[button]['debounce'] -= 1

            if buttons[button]['debounce'] < 0:
                action(button)
                time.sleep(keep_out)
                buttons[button]['debounce'] = debounce
        time.sleep(sleep_time)
    print("=== Stopping Button Thread ===")



if __name__ == "__main__":
    # Tests
    print("URLs may fail during testing, it's the pin numbers that are important")
    running = threading.Event()
    test_thread = threading.Thread(name="testing", target=read_button_task, args=(running,))
    test_thread.start()
    time.sleep(30)
    running.set()