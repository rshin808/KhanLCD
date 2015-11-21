from seps525 import SEPS525_nhd as Oled
from template import Template_img as Temp
from text import Text_string as TS
from ad7998_1 import AD7998_1 as ADC  
from ad5696 import AD5696 as DAC
import time
import smbus
import RPi.GPIO as gpio

gpio.cleanup()
gpio.setmode(gpio.BOARD)

PINS = {
    "AS" : 11,
    "CONVST" : 10,
    "A1" : 18,
    "A0" : 22,
    "RESET" : 15,
    "LDAC" : 13,
}

t1 = time.time()
VIMeas1 = Temp("VIMeas1", "VIMeas1.csv")
VISet1 = Temp("VISet1", "VISet1.csv")
VMS1 = Temp("VMS1", "VMS1.csv")
IMS1 = Temp("IMS1", "IMS1.csv")
t2 = time.time()
VDefault = "0000.00"
IDefault = "0.00000"
VD = []
ID = []
VD.append(TS(28, 50, 14, VDefault))
VD.append(TS(28, 69, 14, VDefault))
VD.append(TS(28, 88, 14, VDefault))
VD.append(TS(28, 107, 14, VDefault))
ID.append(TS(91, 50, 14, IDefault))
ID.append(TS(91, 69, 14, IDefault))
ID.append(TS(91, 88, 14, IDefault))
ID.append(TS(91, 107, 14, IDefault))
t3 = time.time()
bus = smbus.SMBus(1)
CHV = ADC(PINS, 5, 12, 5, 0x23, "11111111")
VOUT = DAC(PINS, 5, 12, 0x0C, [0, 0, 0, 0])
CHV.init_adc_address(gpio)
VOUT.init_dac_address(gpio)
CHV.init_adc_bus(bus)
t4 = time.time()
print "INITTemplate: " + str(t2 - t1)
print "INITTextDefault: " + str(t3 - t2)
print "INITADCDAC: " + str(t4 - t3)




TEMPS = {
    "VIMeas1" : VIMeas1.update_oled,
    "VISet1"  : VISet1.update_oled,
    "VMS1"    : VMS1.update_oled,
    "IMS1"    : IMS1.update_oled,
    }

display = Oled()
try:
    print "Initializing"
    display.show()
    display.fill_screen((255, 255))
    time.sleep(0.5)
    display.fill_screen((0,0))
    time.sleep(0.5)
    print "templates"
    TEMPS["VIMeas1"](display)
    for V in VD:
        V.draw_string((0, 0), (175, 223), display)
    for I in ID:
        I.draw_string((0, 0), (175, 223), display)
    time.sleep(0.05)
    TEMPS["VISet1"](display)
    for V in VD:
        V.draw_string((0, 0), (95, 233), display)
    for I in ID:
        I.draw_string((0, 0), (95, 233), display)
    TEMPS["VMS1"](display)
    for V in VD:
        V.draw_string((0, 0), (246, 0), display)
    for I in ID:
        I.draw_string((0, 0), (246, 0), display)
    time.sleep(0.05)
    TEMPS["IMS1"](display)
    for V in VD:
        V.draw_string((0, 0), (249, 192), display)
    for I in VD:
        I.draw_string((0, 0), (249, 192), display)
    time.sleep(0.05)
    print "Initialize Finished"
    print "Changing Text"
    VOUT.update_voltages([1, 3, 3, 1])
    VOUT.output_voltages(bus)
    while(True):
        t1 = time.time()
        CHV.get_data(bus)
        c = 0
        limit = 4
        for v in CHV:
            if c >= limit:
                break
            if c != -1:
                VD[c].update_string(str(v)[:6])
            c += 1
   
        for v in VD:
            v.draw_string((0, 0), (249, 192), display)
        
        t2 = time.time()
        time.sleep(0.01)
        print "Conversion: " + str(t2 - t1)
    time.sleep(1)
    display.hide()
    display.end_gpio()
except KeyboardInterrupt:
    display.hide()
    display.end_gpio()

except Exception, e:
    print e
    display.hide()
    display.end_gpio()
