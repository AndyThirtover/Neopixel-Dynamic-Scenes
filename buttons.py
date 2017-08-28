import datetime
import RPi.GPIO as GPIO

debounce = 10
button_0 = 5
button_1 = 6
sleep_time = 0.001


def action(button_number):
    if button_number == 1:
        neo_queue('rotate')
    else:
        neo_queue('neo_off')
    return button_number



def read_button_task(stop_event):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(button_0,GPIO.IN)
    GPIO.setup(button_1,GPIO.IN)
    count_button_0 = debounce
    count_button_1 = debounce
    while not stop_event:
        # Have buttons been pressed.
        if GPIO.input(button_0):
            count_button_0 -= 1
        if GPIO.input(button_1):
            count_button_1 -= 1

        if count_button_0 < 0:
            action(button_0)
            count_button_0 = debounce
        if count_button_1 < 0:
            action(button_1)
            count_button_1 = debounce

        time.sleep(sleep_time)

