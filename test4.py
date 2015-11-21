#! /usr/bin/python
import spidev
import time
import RPi.GPIO as gpio
import math
import Image
import math
import os
import csv
import font5x8

path = os.getcwd()

COLOR_16 = {
    "WHITE" : 0xFFFF,
    "BLACK" : 0x0000,
    "BLUE" : 0x001F,
    "GREEN" : 0x07E0,
    "RED" : 0xF800,
    "CYAN" : 0x07FF,
    "MAGENTA" : 0xF81F,
    "YELLOW" : 0xFFE0,
}

RES = 8
RS = 12
gpio.setmode(gpio.BOARD)
gpio.setup(RES, gpio.OUT)
gpio.output(RES, True)
gpio.setup(RS, gpio.OUT)
gpio.output(RS, False)
time.sleep(1)

spi = spidev.SpiDev()
spi.open(0, 0)
#spi.max_speed_hz = 5000
spi.max_speed_hz = 100000000
spi.mode = 3

WIDTH = 160
HEIGHT = 128 


def seps525_reg(address, value):
    # CS low
    # RS low
    # send address
    # RS high
    # CS high
    # CS low
    # send value
    # CS high
    gpio.output(RS, False)
    spi.xfer2([address])
    gpio.output(RS, True)
    spi.xfer2([value])

def data(value):
    gpio.output(RS, True)
    spi.xfer2(list(value))
    gpio.output(RS, False)

def seps525_init():
    # startup RS
    gpio.output(RS, False)
    time.sleep(0.5)
    gpio.output(RS, True)
    time.sleep(0.5)

    # set normal driving current
    # disable oscillator power down
    seps525_reg(0x04, 0x01)
    time.sleep(0.002)

    # enable power save mode
    # set normal driving current
    # disable oscillator power down
    seps525_reg(0x04, 0x00)
    time.sleep(0.002)

    seps525_reg(0x3B, 0x00)

    # set EXPORT1 at internal clock
    seps525_reg(0x02, 0x01)

    # set framerate as 120 Hz
    seps525_reg(0x03, 0x30)

    # set reference voltage controlled by external resistor
    seps525_reg(0x80, 0x01)

    # set pre-charge time
    # red
    seps525_reg(0x08, 0x04)
    # green
    seps525_reg(0x09, 0x05)
    # blue  
    seps525_reg(0x0A, 0x05)

    # set pre-charge current
    # red
    seps525_reg(0x0B, 0x9D)
    # green
    seps525_reg(0x0C, 0x8C)
    # blue
    seps525_reg(0x0D, 0x57)

    # set driving current
    # red
    seps525_reg(0x10, 0x56)
    # green
    seps525_reg(0x11, 0x4D)
    # blue 
    seps525_reg(0x12, 0x46)

    # set color sequence
    seps525_reg(0x13, 0x00)
        
    # set MCU interface mode
    seps525_reg(0x14, 0x01)
    seps525_reg(0x16, 0x66)
    
    # shift mapping RAM counter
    seps525_reg(0x20, 0x00)
    seps525_reg(0x21, 0x00)

    # 1/128 duty
    seps525_reg(0x28, 0x7F)

    # set mapping
    seps525_reg(0x29, 0x00)

    # display on
    seps525_reg(0x06, 0x01)

    # disable power save mode
    seps525_reg(0x05, 0x00)

    # set RGB polarity
    seps525_reg(0x15, 0x00)

class template_img:
    """
        This is the template for creating bitmaps.
        The template class only allows updte to the SEPS525.
        The bitmap is automatically updated using the oled commands.
    """
    def __init__(self, name, img):
        """
            This will create and initialize the template.
        """
        self._name = str(name)
        self._bitmap = []
        self.__create_bitmap(img)

    def __str__(self):
        return self._name

    def __create_bitmap(self, img):
        """
            This creates the bitmap for the template given an image.
            The bitmap values match the values for the SEPS525.
        """
        with open(img, "rb") as img_csv:
            reader = csv.reader(img_csv)
            for row in reader:
                self._bitmap.append(int(row[0]))

    def update_oled(self):
        seps525_set_region(0, 0, 160, 128)
        data_start()
        value = []
        for pixel in self._bitmap:
            color = parse_color(int(pixel))
            value.append(color[0])
            value.append(color[1])

        for i in range(10):
            data(value[(4096 * i): (4096 * i + 4096)])
        
    def update_oled_region(self, x, y, w, h, img):
        rgb = Image.open(img).convert("RGB")
        seps525_set_region(x, y, w, h)
        
    def name(self):
        return self._name

    def bitmap(self):
        return self._bitamp
def init_oled_display():
    seps525_init()
    bg1 = template_img("background", "earth.csv")
    print bg1.name()
    t1 = time.time()
    bg1.update_oled()
    #fill_screen_16([COLOR_16["WHITE"]])
    t2 = time.time()
    print "DELAY: " + str(t2 - t1)
    # for pixel in range((160 * 128)):
    #     data(COLOR_16["WHITE"])

def parse_color(value):
    return (int("{0:b}".format(value)[:-8].zfill(8), 2), int("{0:b}".format(value)[-8:], 2))
 
def data_start():
    gpio.output(RS, False)
    spi.xfer([0x22])
    gpio.output(RS, True)

def seps525_set_region(width1 = 0, height1 = 0, width2 = 160, height2 = 128):
    seps525_reg(0x17, width1)
    seps525_reg(0x18, width1 + width2 - 1)
    seps525_reg(0x19, height1)
    seps525_reg(0x1A, height1 + height2 - 1)
    seps525_reg(0x20, width1)
    seps525_reg(0x21, height1)

def fill_screen_16(parameters):
    color = int(parameters[0])
    seps525_set_region(0, 0, 160, 128)
    data_start()
    color = parse_color(color)
    value = []
    
    for pixel in range(2048):
        value.append(color[0])
        value.append(color[1])

    for pixel in range(10):
        data(value)


def draw_pixel(parameters):
    # (x, y, color)
    x = int(parameters[0])
    y = int(parameters[1])
    color = int(parameters[2])
    color = parse_color(color)
    seps525_set_region(x, y, 1, 1)
    data_start()
    data(color)

def draw_vline(parameters):
    # (x, y, h, color)
    x = int(parameters[0])
    y = int(parameters[1])
    h = int(parameters[2])
    color = int(parameters[3])
    color = parse_color(color)
    seps525_set_region(x, y, 1, h)
    data_start()
 
    value = []
    for pixel in range(2048):
        value.append(color[0])
        value.append(color[1])

    data(value)

def draw_hline(parameters):
    # (x, y, w, color)
    x = int(parameters[0])
    y = int(parameters[1])
    w = int(parameters[2])
    color = int(parameters[3])
    color = parse_color(color)
    seps525_set_region(x, y, w, 1)
    data_start()

    value = [] 
    for pixel in range(2048):
        value.append(color[0])
        value.append(color[1])

    data(value)

def draw_rect(parameters):
    # (x, y, w, h, color, filled)
    x = int(parameters[0])
    y = int(parameters[1])
    w = int(parameters[2])
    h = int(parameters[3])
    color = int(parameters[4])
    color = parse_color(color)
    filled = str(parameters[5])
    if(filled == "True"):
        seps525_set_region(x, y, w, h)
        data_start()
        value = []
        for pixel in range(2048):
            value.append(color[0])
            value.append(color[1])

        if((w * h) <= 2048):
            data(value)
        else:
            for pixel in range(((x + w) * (y + h) / 2048 + 1)):
                data(value)
    else:
        draw_vline([x, y, h, int(parameters[4])])
        draw_hline([x, y, w, int(parameters[4])])
        draw_hline([x, y + h, w, int(parameters[4])])
        draw_vline([x + w, y, h, int(parameters[4])])       

def draw_circ(parameters):
    # (x, y, r, color, filled)
    if(parameters[4] != "True"):

        draw_pixel([parameters[0], int(parameters[1]) - int(parameters[2]), parameters[3]])
        draw_pixel([parameters[0], 2 * int(parameters[2]) + 1, parameters[3]])
        f = 1 - int(parameters[2])
        ddf_x = 1
        ddf_y = -2 * int(parameters[2])
        x = 0;
        y = int(parameters[2])
        while(x < y):
            if(f >= 0):
                y -= 1
                ddf_y += 2
                f += ddf_y
            x += 1
            ddf_x += 2
            f += ddf_x
           

            draw_pixel([(int(parameters[0]) + x), (int(parameters[1]) - y), parameters[3]])
            draw_pixel([x + int(parameters[0]), (int(parameters[1]) + y), parameters[3]])
            
            
            draw_pixel([int(parameters[0]) + y, int(parameters[1]) - x, parameters[3]])
            draw_pixel([int(parameters[0]) + y, int(parameters[1]) + x, parameters[3]])
            

            draw_pixel([int(parameters[0]) - x, int(parameters[1]) - y, parameters[3]])
            draw_pixel([int(parameters[0]) - x, int(parameters[1]) + y, parameters[3]])
            
            draw_pixel([int(parameters[0]) - y, int(parameters[1]) - x, parameters[3]])
            draw_pixel([int(parameters[0]) - y, int(parameters[1]) + x, parameters[3]])

       
def write_text(parameters):
    # (x, y, color, text)
    x = int(parameters[0])
    y = int(parameters[1])
    text = str(parameters[3])
    font = font5x8.Font5x8
    font_bytes = font.bytes
    font_rows = font.rows
    font_cols = font.cols
    
    for c in text:
        p = ord(c) * font_col
        for col in range(0, font_cols):
            mask = font_bytes[p]
            p += 1
            for row in range(0, 8):
                draw_pixel(x, y + row, parameters[2])
            x += 1

COMMANDS = {
    "TEXT" : write_text,
    "PIXEL" : draw_pixel,
    "HLINE" : draw_hline,
    "VLINE" : draw_vline,
    "RECT" : draw_rect,
    "CIRC" : draw_circ,
    "FILL" : fill_screen_16
}

init_oled_display()

try:
    command = None
    while(True):
        try:
            print "Enter command and parameters. ('command parameter1,...,parametern'): "
            command = raw_input()
            new_command = command.split(" ")[0]
            new_parameters = command.split(" ")[-1]
            new_parameters = new_parameters.split(",")
            print new_command, new_parameters
            t1 = time.time()
            COMMANDS[new_command](new_parameters)
            t2 = time.time()
            print "Delay: " + str(t2 - t1)
            command = None
        except KeyboardInterrupt:
            seps525_reg(0x06, 0x00)
            gpio.output(RES, True)
            gpio.cleanup()
            exit()
        except: 
            print "Input Error"

except KeyboardInterrupt:
    seps525_reg(0x06, 0x00)
    gpio.output(RES, True)
    gpio.cleanup()
    exit()    
