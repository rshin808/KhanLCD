import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BOARD)
gpio.setup(16, gpio.IN, pull_up_down = gpio.PUD_UP)
def my_callback(gpio):
    start = time.time()
    while(gpio.input(16) == 0):
        pass
    end = time.time()
    print str(end - start)
        
try:
    gpio.add_event_detect(16, gpio.FALLING, bouncetime = 300)
    while(True):
        if(gpio.event_detected(16)):
            my_callback(gpio)
       
except KeyboardInterrupt:
    gpio.remove_event_detect(16)
    gpio.cleanup()
