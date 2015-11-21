"""
    File: encoder2b.py
    By  : Reed Shinsato
    Desc: This implements the class for the encoder.
"""

# Libraries
import RPi.GPIO as gpio
import time

PINS = {
    "ENCA" : 26,
    "ENCB" : 16,
    "ENCC" : 15,
}

class Encoder2b:
    """
        Constructor
        Param: PINS, The pins of the encoder.
    """
    def __init__(self, PINS):
        self._ENCA = int(PINS["ENCA"])
        self._ENCB = int(PINS["ENCB"])
        self._ENCC = int(PINS["ENCC"])
        self._state = 0

    """
        This initializes the encoder.
        Param: gpio, The Raspberry Pi gpio object.
    """
    def init_encoder(self, gpio):
        gpio.setup(self._ENCA, gpio.IN, pull_up_down = gpio.PUD_UP)
        gpio.setup(self._ENCB, gpio.IN, pull_up_down = gpio.PUD_UP)
        gpio.setup(self._ENCC, gpio.IN, pull_up_down = gpio.PUD_UP)
        gpio.add_event_detect(self._ENCC, gpio.FALLING, bouncetime = 0)
        gpio.add_event_detect(self._ENCA, gpio.FALLING, bouncetime = 0)
        gpio.add_event_detect(self._ENCB, gpio.FALLING, bouncetime = 0)

    
    def __get_state(self, gpio, A, B):
        if(A == True and B == False):
            return 2
        elif(A == False and B == True):
            return 1 
        else:
            return 0

    
    """
        This determines how long the encoder button has been held.
        Param: gpio, The Raspberry Pi gpio object.  
    """
    def wait_hold(self, gpio):       
        if(gpio.event_detected(self._ENCC) == True):
            start = time.time()
            while(gpio.input(self._ENCC) == False):
                pass
            end = time.time()
            
            if float(end - start) >= 0.1 and float(end - start) < 0.6:
                time.sleep(0.01)
                return False
            elif float(end - start) >= 0.6:
                time.sleep(0.01)
                return True
            else:
                return None
        
        return None            

    """
        This gets the direction that the encoder was turned.
        Param: gpio, The Raspberry Pi gpio object.
    """
    def get_direction(self, gpio):
        switchA = False
        if(gpio.event_detected(self._ENCA) == True):
            while(gpio.input(self._ENCA) == True):
                pass
            if(gpio.input(self._ENCB) == False):
                print "RIGHT"
                time.sleep(0.015)
                return "RIGHT"
        elif(gpio.event_detected(self._ENCB) == True):
            while(gpio.input(self._ENCB) == True):
                pass
            if(gpio.input(self._ENCA) == False):
                print "LEFT"
                time.sleep(0.015)
                return "LEFT"
        return None
"""
# This is some test code.
gpio.setmode(gpio.BOARD)
ENC = Encoder2b(PINS)
ENC.init_encoder(gpio)
try:
    while(True):
        direction = ENC.get_direction(gpio)

        if direction != None:
            print direction
except KeyboardInterrupt:
    gpio.cleanup()
except Exception, e:
    print e
    gpio.remove_event_detect(PINS["ENCC"])
    gpio.cleanup()
"""
