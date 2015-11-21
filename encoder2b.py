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
        self._state = None

    """
        This initializes the encoder.
        Param: gpio, The Raspberry Pi gpio object.
    """
    def init_encoder(self, gpio):
        gpio.setup(self._ENCA, gpio.IN)
        gpio.setup(self._ENCB, gpio.IN)
        gpio.setup(self._ENCC, gpio.IN, pull_up_down = gpio.PUD_UP)
        self._state = self.__get_state(gpio)
        gpio.add_event_detect(self._ENCC, gpio.FALLING, bouncetime = 0)


    """
        This determines the state of the encoder.
        Param: gpio, The Raspberry Pi gpio object.
    """
    def __get_state(self, gpio):
        if gpio.input(self._ENCA) == True and gpio.input(self._ENCB) == True:
            return 3
        elif gpio.input(self._ENCA) == True and gpio.input(self._ENCB) == False:
            return 2
        elif gpio.input(self._ENCA) == False and gpio.input(self._ENCB) == True:
            return 1
        else:
            return 0

    def state(self, gpio):
        print self.__get_state(gpio)

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
            
            if float(end - start) >= 0.1 and float(end - start) < 0.5:
                return False
            elif float(end - start) >= 0.5:
                return True
            else:
                return None
        
        return None            


    """
        This gets the direction that the encoder was turned.
        Param: gpio, The Raspberry Pi gpio object.
    """
    def get_direction(self, gpio):
        new_state = self.__get_state(gpio)
        direction = "SAME"
        if new_state == 3 and self._state == 1:
            direction = "LEFT"
        elif new_state == 3 and self._state == 2:
            direction = "RIGHT"
        
        self._state = new_state

        return direction

"""
# This is some test code.
gpio.setmode(gpio.BOARD)
PINS = {
    "ENCA" : 7, 
    "ENCB" : 21,
    "ENCC" : 16,
}
"""
