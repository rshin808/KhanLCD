from template import Template_img as Temp
from text import Text_string as TS
from font import Font
import csv

VDefault = "0000.00"
IDefault = "0.00000"


class VIMeas(Temp):
    def __init__(self, font, name = "VIMeas", filename = "VIMeas.csv"):
        Temp.__init__(self, name, filename)
        self._current_pos = 0
        self._selection = ("Menu", "VISet", "1", "2", "3", "4")
        self._VD = []
        self._ID = []
        self._VD.append(TS(28, 50, 14, VDefault, font))
        self._VD.append(TS(28, 69, 14, VDefault, font))
        self._VD.append(TS(28, 88, 14, VDefault, font))
        self._VD.append(TS(28, 107, 14, VDefault, font))
        self._ID.append(TS(91, 50, 14, IDefault, font))
        self._ID.append(TS(91, 69, 14, IDefault, font))
        self._ID.append(TS(91, 88, 14, IDefault, font))
        self._ID.append(TS(91, 107, 14, IDefault, font))
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
    def update_strings(self, adc, bus, display):
        adc.get_data(bus)
        c = 0
        half = 4
        limit = 8
        for v in adc:
            if c >= limit:
                break
            if c != -1:
                if c >= half:
                    self._ID[c - half].update_string(str(v)[:6])
                else:
                    self._VD[c].update_string(str(v)[:6])
                c += 1
        for c in range(half):
            self._VD[c].draw_string((0, 0), self._back, display)
            self._ID[c].draw_string((0, 0), self._back, display)
    def select_pos(self, display, check):
        global CURRENT
        CURRENT = SCREEN[self._selection[self._current_pos]]
        CURRENT.update_oled(display)
