import seps525
import RPi.GPIO as gpio
import csv
from font import Font
import spidev


display = seps525.SEPS525_nhd()
display.fill_screen((255,255))
display.show()

try:
    while(True):
        pass
except KeyboardInterrupt:
    gpio.cleanup()
