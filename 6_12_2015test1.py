#!/usr/bin/env python
from seps525 import SEPS525_nhd as Oled
from template import Template_img as Temp
from text import Text_string as TS
from ad7998_1 import AD7998_1 as ADC  
from ad5696 import AD5696 as DAC
from encoder2b_int import Encoder2b as Encoder
from font import Font
import time
import datetime as dt
import smbus
import RPi.GPIO as gpio
import datetime as dt
from threading import Thread

font14h = Font("font14h")
font14h.init_bitmap("font14h.csv")
font14hL = Font("font14hL")
font14hL.init_bitmap("font14hL.csv")

gpio.cleanup()
gpio.setmode(gpio.BCM)

bus = smbus.SMBus(1)

display = Oled()

PINS = {
    "CONVST" : 17,
    "RESET" : 25,
    "ENCA" : 7,
    "ENCB" : 23,
    "ENCC" : 22,
    "HV1ONOFF" : 4,
    "HV2ONOFF" : 14,
    "HV3ONOFF" : 15,
    "HV4ONOFF" : 18,
    "HV1EN" : 30,
    "HV2EN" : 31,
    "HV3EN" : 29,
    "HV4EN" : 28,
}

# gpio for HVboard
gpio.setup(PINS["HV1ONOFF"], gpio.IN)
gpio.setup(PINS["HV2ONOFF"], gpio.IN)
gpio.setup(PINS["HV3ONOFF"], gpio.IN)
gpio.setup(PINS["HV4ONOFF"], gpio.IN)
gpio.setup(PINS["HV1EN"], gpio.OUT)
gpio.setup(PINS["HV2EN"], gpio.OUT)
gpio.setup(PINS["HV3EN"], gpio.OUT)
gpio.setup(PINS["HV4EN"], gpio.OUT)

gpio.output(PINS["HV1EN"], False)
gpio.output(PINS["HV2EN"], False)
gpio.output(PINS["HV3EN"], False)
gpio.output(PINS["HV4EN"], False)

gpio1 = False
gpio2 = False
gpio3 = False
gpio4 = False

# Calibration for DAC
Offset = -0.0116

# Default Set Parameters
VDefault = "0000.00"
IDefault = "0.00000"

# Max Voltages (These are used as limits for the output)
VoltageMax = 4000.00
DACVoltageMax = 2.5

# ADC and DAC initializers
CHV = ADC(PINS, 5, 12, 5, 0x23, "11111111")
VOUT = DAC(PINS, 5, 12, 0x0C, [0.0, 0.0, 0.0, 0.0])

CHV.init_adc_address(gpio)

CHV.init_adc_bus(bus)

# Encoder initializer
ENC = Encoder(PINS)
ENC.init_encoder(gpio)

# Voltage and Current to set to
CHVSet = [0.0, 0.0, 0.0, 0.0]
CHISet = [0.0, 0.0, 0.0, 0.0]

# Voltage and Current outputed from DAC
CHVCurrent = [0.0, 0.0, 0.0, 0.0]
CHICurrent = [0.0, 0.0, 0.0, 0.0]

"""
    This class holds the methods for the template for the subwindow of VISet.
    It has a Back, V and I position to choose. 
"""
class VISetN(Temp):
    def __init__(self, name = "VISetN", filename = "VISetN.csv", channel = 1):
        Temp.__init__(self, name, filename)
        # Based on channel name (1,..., channelN)
        self._channel = channel
        self._current_pos = 0
        self._VI_pos = 0
        self._selection = ("VISet", "V", "I")
        self._VI = 0
        self._title = TS(3, 30, 14, "CHANNEL " + str(channel + 1), font14hL)

        # Hold the Display strings
        self._V = []
        self._I = []

        # In terms of DAC voltages
        # The values we want to set to
        self._setV = CHVSet[self._channel - 1]
        self._setI = CHISet[self._channel - 1]
        
        voltage_string = self.__voltage_to_string(self._setV)
        current_string = self.__current_to_string(self._setI)
        count = 54
        for v in voltage_string:
            self._V.append(TS(count, 53, 14, v, font14hL))
            count += 10  

        count = 54
        for i in current_string:
            self._I.append(TS(count, 79, 14, i, font14hL))
            count += 10
       

        self._back = (255, 255)
        self._menu = (223, 60)
        self._line = [7, 18, 37]
   
    def __voltage_to_string(self, voltage):
        return str("{:.2f}".format(voltage / 4.64 * 4000.0)).zfill(7)
        

    def __current_to_string(self, voltage):
        return str("{:.2f}".format(voltage / 4.64 * 4000.0)).zfill(7)
    
    def update_channel(self, channel):
        self._channel = channel
        self._title.update_string("CHANNEL " + str(channel))
        self._setV = CHVSet[self._channel - 1]
        self._setI = CHISet[self._channel - 1]
 
        
    def init(self, display):
        voltage_string = "{:.2f}".format(self._setV).zfill(7)
        current_string = "{:.2f}".format(self._setI).zfill(7)
        
        # FIX Change color
        self._title.draw_string((0, 0), (255, 255), display)
        for i in range(4):
            self._V[i].update_string(voltage_string[i])
            self._I[i].update_string(current_string[i])

        for V in self._V:
            V.draw_string((0, 0), self._back, display)
        for I in self._I:
            I.draw_string((0, 0), self._back, display)
    
    def update_pos(self, direction, display):
        # Menu
        if self._VI == 0:
           if direction == "LEFT":
               if self._current_pos <= 2:
                   self._current_pos += 1
           else:
               if self._current_pos >= 1:
                   self._current_pos -= 1 
          
           if self._current_pos == 0:
               display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
               self._line = [7, 18, 30]
               display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
           elif self._current_pos == 1:
               display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
               self._line = [51, 70, 70]
               display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
           else:
               display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
               self._line = [51, 96, 70] 
               display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        # Voltage
        elif self._VI == 1:
            if direction == "LEFT":
               new_int = (int(str(self._V[self._VI_pos])) + 1)
               if new_int >= 10:
                   new_int = 0
               self._V[self._VI_pos].update_string(str(new_int))
            else:
                new_int = (int(str(self._V[self._VI_pos])) - 1)
                if new_int < 0:
                    new_int = 9
                self._V[self._VI_pos].update_string(str(new_int))
            self._V[self._VI_pos].draw_string((255, 255), (0, 0), display)
        # Current
        elif self._VI == 2:
            if direction == "LEFT":
               new_int = (int(str(self._I[self._VI_pos])) + 1)
               if new_int >= 10:
                   new_int = 0
               self._I[self._VI_pos].update_string(str(new_int))
            else:
                new_int = (int(str(self._I[self._VI_pos])) - 1)
                if new_int < 0:
                    new_int = 9
                self._I[self._VI_pos].update_string(str(new_int))
            self._I[self._VI_pos].draw_string((255, 255), (0, 0), display)
        
    def update_strings(self, adc, dac, bus, display, check_time):
       
       CHVSet[self._channel - 1] = self._setV
       CHISet[self._channel - 1] = self._setI

       if (dt.datetime.now() - check_time).total_seconds() >= 0.39:
           if(self._VI == 0):
               self.init(display)

        
    def voltage_to_DAC(self, voltage):
        DAC_voltage = None
        if voltage < VoltageMAX:
            DAC_voltage = (4.64 / 4000.0) * voltage
            if DAC_voltage >= DACVoltageMax:
                return None
        return DAC_voltage 

    def select_pos(self, display, check):
        global CURRENT
        self._setV = CHVSet[self._channel - 1]
        # Menu
        if self._VI == 0:
            if self._current_pos == 0:
                CURRENT = SCREEN[self._selection[0]]
                CURRENT.update_oled(display)
            elif self._current_pos == 1:
                self._VI = 1
            elif self._current_pos == 2:
                self._VI = 2
        # Voltage
        elif self._VI == 1:
            if check == False:
                self._VI_pos += 1
                if self._VI_pos == 4:
                    self._VI_pos += 1
                if self._VI_pos == 5:
                    self._VI_pos = 0
                
                for v in range(len(self._V)):
                    if v != 4:
                        if v == self._VI_pos:
                            self._V[v].draw_string((255, 255), (0, 0), display)
                        else:
                            self._V[v].draw_string((0, 0), self._back, display)
                self._V[4].draw_string((0, 0), self._back, display)
            else:
                self._VI = 0
                self._current_pos = 0
                self._VI_pos = 0
                self._V[self._current_pos].draw_string((0, 0), self._back, display)
                
                V_string = ""
                for V in self._V:
                    V_string += str(V)
       
                self._setV = float(V_string)
        # Current  
        elif self._VI == 2:
            if check == False:
                self._VI_pos += 1
                if self._VI_pos == 4:
                    self._VI_pos += 1
                if self._VI_pos == 5:
                    self._VI_pos = 0
                
                for i in range(len(self._I)):
                    if i != 4:
                        if i == self._VI_pos:
                            self._I[i].draw_string((255, 255), (0, 0), display)
                        else:
                            self._I[i].draw_string((0, 0), self._back, display)
                self._I[1].draw_string((0, 0), self._back, display)
            else:
                self._VI = 0
                self._I[self._current_pos].draw_string((0, 0), self._back, display)
                self._current_pos = 0
                self._VI_pos = 0
                I_string = ""
                for I in self._I:
                    I_string += str(I)
                self._setI = float(I_string)
                  
class VIMeas(Temp):
    def __init__(self, name = "VIMeas", filename = "VIMeas.csv"):
        Temp.__init__(self, name, filename)
        self._current_pos = 0
        self._selection = ("Menu", "VISet", "1", "2", "3", "4")
        self._VD = []
        self._ID = []
        self._VD.append(TS(28, 50, 14, VDefault, font14h))
        self._VD.append(TS(28, 69, 14, VDefault, font14h))
        self._VD.append(TS(28, 88, 14, VDefault, font14h))
        self._VD.append(TS(28, 107, 14, VDefault, font14h))
        self._ID.append(TS(91, 50, 14, IDefault, font14h))
        self._ID.append(TS(91, 69, 14, IDefault, font14h))
        self._ID.append(TS(91, 88, 14, IDefault, font14h))
        self._ID.append(TS(91, 107, 14, IDefault, font14h))
        self._back = (175, 223)
        self._menu = (223, 60)
        self._line = [7, 18, 37] 
    
    def init(self, display):
        for V in self._VD:
            V.draw_string((0, 0), self._back, display)
        for I in self._ID:
            I.draw_string((0, 0), self._back, display)
  
    def update_pos(self, direction, display):
        prev = self._current_pos
        if direction == "LEFT":
            if self._current_pos <= 4:
                self._current_pos += 1
        elif direction == "RIGHT":
            if self._current_pos >= 1:
                self._current_pos -= 1
        print self._selection[self._current_pos]

        if self._current_pos == 0:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [7, 18, 30]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 1:
            if prev == 0:
                display.draw_hline(self._line[0], self._line[1], self._line[2], self._menu)
            elif prev == 2:
                display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)

            self._line = [4, 40, 42]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 2:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 65, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 3:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 84, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 4:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 103, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        else:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 121, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
    
    def update_strings(self, adc, dac, bus, display, check_time):
        if (dt.datetime.now() - check_time).total_seconds() >= 0.39: 
            adc.get_data(bus)
            readings = adc.get_voltages()
            count = 1
            for reading in readings:
                if count == 5:
                    self._VD[0].update_string("{:.2f}".format(reading / 4.64 * 4000.0).rjust(7) + "V ")
                    self._VD[0].draw_string((0, 0), self._back, display)
                elif count == 3:
                    self._VD[1].update_string("{:.2f}".format(reading / 4.64 * 4000.0).rjust(7) + "V ")
                    self._VD[1].draw_string((0, 0), self._back, display)
                elif count == 4:
                    self._VD[2].update_string("{:.2f}".format(reading / 4.64 * 4000.0).rjust(7) + "V ")
                    self._VD[2].draw_string((0, 0), self._back, display)
                elif count == 8:
                    self._VD[3].update_string("{:.2f}".format(reading / 4.64 * 4000.0).rjust(7) + "V ")
                    self._VD[3].draw_string((0, 0), self._back, display)
                elif count == 7:
                    self._ID[0].update_string("{:.4f}".format(reading / 1000.0) + "A ")
                    self._ID[0].draw_string((0, 0), self._back, display)
                elif count == 1:
                    self._ID[1].update_string("{:.4f}".format(reading / 1000.0) + "A ")
                    self._ID[1].draw_string((0, 0), self._back, display)
                elif count == 2:
                    self._ID[2].update_string("{:.4f}".format(reading / 1000.0) + "A ")
                    self._ID[2].draw_string((0, 0), self._back, display)
                elif count == 6:
                    self._ID[3].update_string("{:.4f}".format(reading / 1000.0) + "A ")
                    self._ID[3].draw_string((0, 0), self._back, display)
                count += 1

    # FIX return the selection in the main instead
    def select_pos(self, display, check):
        global CURRENT
        CURRENT = SCREEN[self._selection[self._current_pos]]
        CURRENT.update_oled(display)


class VISet(Temp):
    def __init__(self, name = "VISet", filename = "VISet.csv"):
        Temp.__init__(self, name, filename)
        self._current_pos = 0
        self._selection = ("Menu", "VMS", "1", "2", "3", "4")
        self._VD = []
        self._ID = []
        self._VD.append(TS(28, 50, 14, VDefault, font14h))
        self._VD.append(TS(28, 69, 14, VDefault, font14h))
        self._VD.append(TS(28, 88, 14, VDefault, font14h))
        self._VD.append(TS(28, 107, 14, VDefault, font14h))
        self._ID.append(TS(91, 50, 14, IDefault, font14h))
        self._ID.append(TS(91, 69, 14, IDefault, font14h))
        self._ID.append(TS(91, 88, 14, IDefault, font14h))
        self._ID.append(TS(91, 107, 14, IDefault, font14h))
        self._back = (15, 233)
        self._menu = (223, 60)
        self._line = [7, 18, 37]
         
    def init(self, display):
        for V in self._VD:
            V.draw_string((0, 0), self._back, display)
        for I in self._ID:
            I.draw_string((0, 0), self._back, display)
  
    def update_pos(self, direction, display):
        prev = self._current_pos
        if direction == "LEFT":
            if self._current_pos <= 4:
                self._current_pos += 1
        else:
            if self._current_pos >= 1:
                self._current_pos -= 1

        if self._current_pos == 0:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [7, 18, 30]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 1:
            if prev == 0:
                display.draw_hline(self._line[0], self._line[1], self._line[2], self._menu)
            elif prev == 2:
                display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)

            self._line = [33, 40, 38]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 2:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 65, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 3:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 84, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 4:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 103, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        else:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 121, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
    
    def update_strings(self, adc, dac, bus, display, check_time):
        if (dt.datetime.now() - check_time).total_seconds() >= 0.39: 
            
            output_Vs = CHVSet
            output_Is = CHISet

            for count in range(len(output_Vs)):
                self._VD[count].update_string("{:.2f}".format(output_Vs[count]).rjust(7) + "V ")
                self._VD[count].draw_string((0, 0), self._back, display)
                self._ID[count].update_string("{:.4f}".format(output_Is[count] / 1000.0) + "A ")
                self._ID[count].draw_string((0, 0), self._back, display)
                

    def select_pos(self, display, check):
        global CURRENT
        if self._current_pos < 2:
            CURRENT = SCREEN[self._selection[self._current_pos]]
        else:
            CURRENT = SCREEN["VISetN"]
            CURRENT.update_channel(int(self._selection[self._current_pos]))
        CURRENT.init(display)
        CURRENT.update_oled(display)

class VMS(Temp):
    def __init__(self, name = "VMS", filename = "VMS.csv"):
        Temp.__init__(self, name, filename)
        self._current_pos = 0
        self._selection = ("Menu", "IMS", "1", "2", "3", "4")
        self._VD = []
        self._ID = []
        self._VD.append(TS(28, 50, 14, VDefault, font14h))
        self._VD.append(TS(28, 69, 14, VDefault, font14h))
        self._VD.append(TS(28, 88, 14, VDefault, font14h))
        self._VD.append(TS(28, 107, 14, VDefault, font14h))
        self._ID.append(TS(91, 50, 14, IDefault, font14h))
        self._ID.append(TS(91, 69, 14, IDefault, font14h))
        self._ID.append(TS(91, 88, 14, IDefault, font14h))
        self._ID.append(TS(91, 107, 14, IDefault, font14h))
        self._back = (246, 0)
        self._menu = (223, 60)
        self._line = [7, 18, 40] 
    
    def init(self, display):
        for V in self._VD:
            V.draw_string((0, 0), self._back, display)
        for I in self._ID:
            I.draw_string((0, 0), self._back, display)
  
    def update_pos(self, direction, display):
        prev = self._current_pos
        if direction == "LEFT":
            if self._current_pos <= 4:
                self._current_pos += 1
        else:
            if self._current_pos >= 1:
                self._current_pos -= 1
        print self._selection[self._current_pos]

        if self._current_pos == 0:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [7, 18, 28]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 1:
            if prev == 0:
                display.draw_hline(self._line[0], self._line[1], self._line[2], self._menu)
            elif prev == 2:
                display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)

            self._line = [67, 40, 25]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 2:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 65, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 3:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 84, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 4:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 103, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        else:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 121, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
  
    def update_strings(self, adc, dac, bus, display, check_time):
        if (dt.datetime.now() - check_time).total_seconds() >= 0.39:
            adc.get_data(bus)
            readings = adc.get_voltages()
            count = 1
            for reading in readings:
                if count == 5:
                    self._VD[0].update_string("{:.2f}".format(reading / 4.64 * 4000.0).rjust(7) + "V ")
                    self._VD[0].draw_string((0, 0), self._back, display)
                elif count == 3:
                    self._VD[1].update_string("{:.2f}".format(reading / 4.64 * 4000.0).rjust(7) + "V ")
                    self._VD[1].draw_string((0, 0), self._back, display)
                elif count == 4:
                    self._VD[2].update_string("{:.2f}".format(reading / 4.64 * 4000.0).rjust(7) + "V ")
                    self._VD[2].draw_string((0, 0), self._back, display)
                elif count == 8:
                    self._VD[3].update_string("{:.2f}".format(reading / 4.64 * 4000.0).rjust(7) + "V ")
                    self._VD[3].draw_string((0, 0), self._back, display)
                count += 1
            
            for i in range(len(self._ID)):
                self._ID[i].update_string("{:.2f}".format(CHVSet[i]).rjust(7) + "V ")
                self._ID[i].draw_string((0, 0), self._back, display) 

    def select_pos(self, display, check):
        global CURRENT
        CURRENT = SCREEN[self._selection[self._current_pos]]
        CURRENT.update_oled(display)

class IMS(Temp):
    def __init__(self, name = "IMS", filename = "IMS.csv"):
        Temp.__init__(self, name, filename)
        self._current_pos = 0
        self._selection = ("Menu", "VIMeas", "1", "2", "3", "4")
        self._VD = []
        self._ID = []
        self._VD.append(TS(28, 50, 14, IDefault, font14h))
        self._VD.append(TS(28, 69, 14, IDefault, font14h))
        self._VD.append(TS(28, 88, 14, IDefault, font14h))
        self._VD.append(TS(28, 107, 14, IDefault, font14h))
        self._ID.append(TS(91, 50, 14, IDefault, font14h))
        self._ID.append(TS(91, 69, 14, IDefault, font14h))
        self._ID.append(TS(91, 88, 14, IDefault, font14h))
        self._ID.append(TS(91, 107, 14, IDefault, font14h))
        self._back = (249, 192)
        self._menu = (223, 60)
        self._line = [7, 18, 37]
         
    def init(self, display):
        for V in self._VD:
            V.draw_string((0, 0), self._back, display)
        for I in self._ID:
            I.draw_string((0, 0), self._back, display)
  
    def update_pos(self, direction, display):
        prev = self._current_pos
        if direction == "LEFT":
            if self._current_pos <= 4:
                self._current_pos += 1
        else:
            if self._current_pos >= 1:
                self._current_pos -= 1
        print self._selection[self._current_pos]

        if self._current_pos == 0:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [7, 18, 30]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 1:
            if prev == 0:
                display.draw_hline(self._line[0], self._line[1], self._line[2], self._menu)
            elif prev == 2:
                display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
                
            self._line = [95, 40, 23]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 2:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 65, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 3:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 84, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        elif self._current_pos == 4:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 103, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
        else:
            display.draw_hline(self._line[0], self._line[1], self._line[2], self._back)
            self._line = [4, 121, 150]
            display.draw_hline(self._line[0], self._line[1], self._line[2], (0, 0))
    def update_strings(self, adc, dac, bus, display, check_time):
        if (dt.datetime.now() - check_time).total_seconds()  >= 0.39:
            adc.get_data(bus)
            readings = adc.get_voltages()
            
            count = 1
            for reading in readings:
                if count == 1:
                    self._VD[1].update_string("{:.4f}".format(reading / 1000.0) + "A ")
                    self._VD[1].draw_string((0, 0), self._back, display)
                elif count == 2:
                    self._VD[2].update_string("{:.4f}".format(reading / 1000.0) + "A ")
                    self._VD[2].draw_string((0, 0), self._back, display)
                elif count == 6:
                    self._VD[3].update_string("{:.4f}".format(reading / 1000.0) + "A ")
                    self._VD[3].draw_string((0, 0), self._back, display)
                elif count == 7:
                    self._VD[0].update_string("{:.4f}".format(reading / 1000.0) + "A ")
                    self._VD[0].draw_string((0, 0), self._back, display)
                count += 1
            
            for i in range(len(self._ID)):
                self._ID[i].update_string("{:.4f}".format(CHISet[i] / 1000.0) + "A ")
                self._ID[i].draw_string((0, 0), self._back, display)

    def select_pos(self, display, check):
        global CURRENT
        CURRENT = SCREEN[self._selection[self._current_pos]]
        CURRENT.update_oled(display)

VIMeas1 = VIMeas("VIMeas", "VIMeas1.csv")
VISet1 = VISet("VISet", "VISet1.csv")
VMS1 = VMS("VMS", "VMS1.csv")
IMS1 = IMS("IMS", "IMS1.csv")
VISetN1 = VISetN("VISetN", "VISetN.csv", 0)

SCREEN = {
    "VIMeas" : VIMeas1,
    "VISet" : VISet1,
    "VMS" : VMS1,
    "IMS" : IMS1,
    "Menu": VIMeas1,
    "VIMeasN": VIMeas1,
    "VISetN": VISetN1,
    "VMSN" : VMS1,
    "IMSN" : IMS1,
}

CURRENT = SCREEN["VIMeas"]

# Default ramp voltage
def ramp_default(channel, start, voltage):
    if (voltage / 4000.00 * 4.64 + Offset) > DACVoltageMax or voltage < 0.0:
        print "LIMIT EXCEEDED"
        
        return False

    check = (dt.datetime.now() - start).total_seconds()
     
    if check >= 0.02:
        if(CHVCurrent[channel] < voltage):
            CHVCurrent[channel] += 1
            if(CHVCurrent[channel] > voltage):
                CHVCurrent[channel] = voltage
        elif(CHVCurrent[channel] > voltage):
            CHVCurrent[channel] -= 1
            if(CHVCurrent[channel] < voltage):
                CHVCurrent[channel] = voltage
       
        return True
    
    return False

# Required for HV shutoff (prevents anything from interrupt slow ramp down)
def noInterrupt():
    print "Quiting"
    check_ramp = dt.datetime.now()

    CHVSet = [0.0, 0.0, 0.0, 0.0]
    
    while(CHVCurrent != CHVSet):
        if(dt.datetime.now() - check_ramp).total_seconds() > 0.03:
            check_ramp = dt.datetime.now()
        if CHVCurrent[0] != 0.0:
            ramp_default(0, check_ramp, 0.0)
        if CHVCurrent[1] != 0.0:
            ramp_default(1, check_ramp, 0.0)
        if CHVCurrent[2] != 0.0:
            ramp_default(2, check_ramp, 0.0)
        if CHVCurrent[3] != 0.0:
            ramp_default(3, check_ramp, 0.0)

        CHVOut = []
        for v in CHVCurrent:
            CHVOut.append(float(v) / 4000.0 * 4.64)
        VOUT.update_voltages(CHVOut)
        VOUT.output_voltages(bus)
    display.hide()
    display.end_gpio()
    
thread = Thread(target = noInterrupt)

try:
    display.show()
    display.fill_screen((0,0))
    time.sleep(0.5)
    CURRENT.update_oled(display)
    CURRENT.init(display)
    check_ramp = dt.datetime.now()
    check_time = check_ramp
    
    while(True):
        now = dt.datetime.now()
        
        if(now - check_ramp).total_seconds() > 0.03:
            check_ramp = now
        
        if(now - check_time).total_seconds() > 0.4:
            check_time = now
        
        check = ENC.wait_hold(gpio)
        direction = ENC.get_direction(gpio)
        
        # Check for button press
        if check != None:
            CURRENT.select_pos(display, check)
        
        # Check for direction change
        if direction != None:
            CURRENT.update_pos(direction, display)

        CURRENT.update_strings(CHV, VOUT, bus, display, check_time)
        if gpio.input(PINS["HV1ONOFF"]):
            if gpio1 == False and CHVCurrent[0] == 0.0:
                gpio.output(PINS["HV1EN"], True)
                gpio1 = True
            elif gpio1 == True:
                ramp_default(0, check_ramp, CHVSet[0])
        else:
            if CHVCurrent[0] != 0.0:
                if gpio1 == True:
                    ramp_default(0, check_ramp, 0.0)
                    if CHVCurrent[0] == 0.0:
                        gpio.output(PINS["HV1EN"], False)
                        gpio1 = False
        
        if gpio.input(PINS["HV2ONOFF"]):
            if gpio2 == False and CHVCurrent[1] == 0.0:
                gpio.output(PINS["HV2EN"], True)
                gpio2 = True
            elif gpio2 == True:
                ramp_default(1, check_ramp, CHVSet[1])
        else:
            if CHVCurrent[1] != 0.0:
                if gpio2 == True:
                    ramp_default(1, check_ramp, 0.0)
                    if CHVCurrent[1] == 0.0:
                        gpio.output(PINS["HV2EN"], False)
                        gpio2 = False
        
        if gpio.input(PINS["HV3ONOFF"]):
            if gpio3 == False and CHVCurrent[2] == 0.0:
                gpio.output(PINS["HV3EN"], True)
                gpio3 = True
            elif gpio3 == True:
                ramp_default(2, check_ramp, CHVSet[2])
        else:
            if CHVCurrent[2] != 0.0:
                if gpio3 == True:
                    ramp_default(2, check_ramp, 0.0)
                    if CHVCurrent[2] == 0.0:
                        gpio.output(PINS["HV3EN"], False)
                        gpio3 = False
        
        if gpio.input(PINS["HV4ONOFF"]):
            if gpio4 == False and CHVCurrent[3] == 0.0:
                gpio.output(PINS["HV4EN"], True)
                gpio4 = True
            elif gpio4 == True:
                ramp_default(3, check_ramp, CHVSet[3])
        else:
            if CHVCurrent[3] != 0.0:
                if gpio4 == True:
                    ramp_default(3, check_ramp, 0.0)
                    if CHVCurrent[3] == 0.0:
                        gpio.output(PINS["HV4EN"], False)
                        gpio4 = False
        CHVOut = [0.0, 0.0, 0.0, 0.0]
        count = 0
        for v in CHVCurrent:
            if count == 0:
                CHVOut[0] = float(v) / 4000.0 * 4.64
            elif count == 1:
                CHVOut[1] = float(v) / 4000.0 * 4.64
            elif count == 2:
                CHVOut[3] = float(v) / 4000.0 * 4.64
            elif count == 3:
                CHVOut[2] = float(v) / 4000.0 * 4.64
            count += 1
        VOUT.update_voltages(CHVOut)
        VOUT.output_voltages(bus)
except:
    thread.start()
    thread.join()
