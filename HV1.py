from seps525 import SEPS525_nhd as Oled
from template import Template_img as Temp
from text import Text_string as TS
import time


t1 = time.time()
VIMeas1 = Temp("VIMeas1", "VIMeas1.csv")
VISet1 = Temp("VISet1", "VISet1.csv")
VMS1 = Temp("VMS1", "VMS1.csv")
IMS1 = Temp("IMS1", "IMS1.csv")
t2 = time.time()
VDefault = "0000.00"
IDefault = "0.00000"
VD1 = TS(28, 50, 14, VDefault)
VD2 = TS(28, 69, 14, VDefault)
VD3 = TS(28, 88, 14, VDefault)
VD4 = TS(28, 107, 14, VDefault)
ID1 = TS(91, 50, 14, IDefault)
ID2 = TS(91, 69, 14, IDefault)
ID3 = TS(91, 88, 14, IDefault)
ID4 = TS(91, 107, 14, IDefault)
t3 = time.time()
print "INITTemplate: " + str(t2 - t1)
print "INITTextDefault: " + str(t3 - t2)



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
    VD1.draw_string((0, 0), (175, 223), display)
    VD2.draw_string((0, 0), (175, 223), display)
    VD3.draw_string((0, 0), (175, 223), display)
    VD4.draw_string((0, 0), (175, 223), display)
    ID1.draw_string((0, 0), (175, 223), display)
    ID2.draw_string((0, 0), (175, 223), display)
    ID3.draw_string((0, 0), (175, 223), display)
    ID4.draw_string((0, 0), (175, 223), display)
    time.sleep(0.5)
    TEMPS["VISet1"](display)
    VD1.draw_string((0, 0), (95, 233), display)
    VD2.draw_string((0, 0), (95, 233), display)
    VD3.draw_string((0, 0), (95, 233), display)
    VD4.draw_string((0, 0), (95, 233), display)
    ID1.draw_string((0, 0), (95, 233), display)
    ID2.draw_string((0, 0), (95, 233), display)
    ID3.draw_string((0, 0), (95, 233), display)
    ID4.draw_string((0, 0), (95, 233), display)
    time.sleep(0.5)
    TEMPS["VMS1"](display)
    VD1.draw_string((0, 0), (246, 0), display)
    VD2.draw_string((0, 0), (246, 0), display)
    VD3.draw_string((0, 0), (246, 0), display)
    VD4.draw_string((0, 0), (246, 0), display)
    ID1.draw_string((0, 0), (246, 0), display)
    ID2.draw_string((0, 0), (246, 0), display)
    ID3.draw_string((0, 0), (246, 0), display)
    ID4.draw_string((0, 0), (246, 0), display)
    time.sleep(0.5)
    TEMPS["IMS1"](display)
    VD1.draw_string((0, 0), (249, 192), display)
    VD2.draw_string((0, 0), (249, 192), display)
    VD3.draw_string((0, 0), (249, 192), display)
    VD4.draw_string((0, 0), (249, 192), display)
    ID1.draw_string((0, 0), (249, 192), display)
    ID2.draw_string((0, 0), (249, 192), display)
    ID3.draw_string((0, 0), (249, 192), display)
    ID4.draw_string((0, 0), (249, 192), display)
    time.sleep(0.5)
    print "Initialize Finished"
    print "Changing Text"
    t1 = time.time()
    VD1.update_string("test me")
    VD2.update_string("test me")
    VD3.update_string("test me")
    VD4.update_string("test me")
    ID1.update_string("test me")
    ID2.update_string("test me")
    ID3.update_string("test me")
    ID4.update_string("test me")
    VD1.draw_string((0, 0), (249, 192), display)
    VD2.draw_string((0, 0), (249, 192), display)
    VD3.draw_string((0, 0), (249, 192), display)
    VD4.draw_string((0, 0), (249, 192), display)
    ID1.draw_string((0, 0), (249, 192), display)
    ID2.draw_string((0, 0), (249, 192), display)
    ID3.draw_string((0, 0), (249, 192), display)
    ID4.draw_string((0, 0), (249, 192), display)
    
    t2 = time.time()
    print "Changing Text: " + str(t2 - t1)
    time.sleep(1)
    display.hide()
    display.end_gpio()
except Exception, e:
    print e
    display.hide()
    display.end_gpio()
