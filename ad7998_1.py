"""
    File: ad7998_1.py
    By  : Reed Shinsato
    Desc: This implements the class for the basic ADC functions.
"""

# Libraries
import smbus
import time
import RPi.GPIO as gpio

# Pins
CONV = 0x00
ALERT = 0x01
CONFIG = 0x02
CYCLE = 0x03
DATA_L1 = 0x04
DATA_H1 = 0x05
HYS1 = 0x06
DATA_L2 = 0x07
DATA_H2 = 0x08
HYS2 = 0x09
DATA_L3 = 0x0A
DATA_H3 = 0x0B
HYS3 = 0x0C
DATA_L4 = 0x0D
DATA_H4 = 0x0E
HYS4 = 0x0F

"""
    AD7998_1 ADC class.
    Note: The main difference between the AD7998_x is the ADDRESS.
"""
class AD7998_1:
    """
        Constructor
        Param: PINS, A list of pins that the ADC will use. 
               VREF, The external voltage reference value.
               RES, The resolution of the ADC.
               VMAX, The maximum voltage that the ADC can output.
               ADDRESS, The address of the ADC on the I2C line.
               CHANNELS, The enabled channels of the ADC. 
    """
    def __init__(self, PINS, VREF = 5, RES = 12, VMAX = 5, ADDRESS = 0x20, CHANNELS = "11111111"):
        # PINS is a dictionary
        self._CONVST = int(PINS["CONVST"])
        self._ADDRESS = ADDRESS
        self._RES = RES
        self._VREF = VREF
        self._VMAX = VMAX
        self._CHANNELS = CHANNELS
        self._channels_EN = 0
        self._lowest = 9
        self._voltage = [-1, -1, -1, -1, -1, -1, -1, -1]       


    def __str__(self):
        return str(self._voltage)

    def __iter__(self):
        for v in self._voltage:
            yield v


    def __len__(self):
        return len(self._voltage)

    def get_voltages(self):
        return self._voltage

    """
        This initializes the ADC address on the I2C line.
    """
    def init_adc_address(self, gpio):
        gpio.setup(self._CONVST, gpio.OUT)

        gpio.output(self._CONVST, True)
        time.sleep(0.1)


    """
        This initializes the ADC on the settings on the I2C line.
    """
    def init_adc_bus(self, bus):
        ch_EN1 = "0000"
        ch_EN2 = "1000"

        ch_EN1 += self._CHANNELS[:4]
        ch_EN2 = self._CHANNELS[4:] + ch_EN2

        for c in self._CHANNELS:
            if c == "1":
                self._channels_EN += 1

        self.__startup(bus, int(ch_EN1, 2), int(ch_EN2, 2))
        self.__write_addr(bus, CONV)

        for dummy_index in range(2 * self._channels_EN):
            data = self.get_readings(bus)[:2]
            data1 = self.__int_to_bin8(data[0])
            if(self.get_channel(data1[:4]) < self._lowest):
                self._lowest = self.get_channel(data1[:4])
 

    """
        This sets the cmd address of the ADC.
    """
    def __write_addr(self, bus, cmd):
        bus.write_byte(self._ADDRESS, cmd)


    """
        This writes a single byte of data to a cmd address.
        Param: 
    """
    def __write_single_byte(self, bus, cmd, data):
        bus.write_i2c_block_data(self._ADDRESS, cmd, [data])

    def __write_two_byte(self, bus, cmd, data1, data2):
        bus.write_i2c_block_data(self._ADDRESS, cmd, [data1, data2])

    def __startup(self, bus, cmd1, cmd2):
        self.__write_two_byte(bus, CONFIG, cmd1, cmd2)
        self.__write_addr(bus, CONV)   
 
    def __int_to_bin8(self, in_int):
        return ("{0:b}".format(in_int).zfill(8))

    def __int_to_volt(self, in_int):
        return ((float(in_int) / float(2 ** self._RES)) * float(self._VMAX))

    def get_channel(self, bin_string):
        return int(bin_string[-3:], 2) + 1

    def get_readings(self, bus):
        gpio.output(self._CONVST, False)
        time.sleep(0.000001)
        gpio.output(self._CONVST, True)
        time.sleep(0.000001)
        return bus.read_i2c_block_data(self._ADDRESS, CONV)

    def get_data(self, bus):
        while(True):
            data = self.get_readings(bus)[:2]
            data1 = self.__int_to_bin8(data[0])
            data2 = self.__int_to_bin8(data[1])

            if(self.get_channel(data1[:4]) == self._lowest):
                voltage_bin = data1[4:] + data2
                self._voltage[self.get_channel(data1[:4]) - 1] = self.__int_to_volt(int(voltage_bin, 2))
                break

        for dummy_index in range(1, self._channels_EN):
            data = self.get_readings(bus)[:2]
            data1 = self.__int_to_bin8(data[0])
            data2 = self.__int_to_bin8(data[1])
            voltage_bin = data1[4:] + data2
            self._voltage[self.get_channel(data1[:4]) - 1] = self.__int_to_volt(int(voltage_bin, 2))
