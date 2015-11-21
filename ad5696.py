"""
    File: ad5696.py
    By  : Reed Shinsato
    Desc: This implements the class for the basic DAC functions.
"""

# Libraries
import smbus
import time
import RPi.GPIO as gpio


"""
    AD5696 DAC class.
"""
class AD5696:
    """
        Constructor
        Param:  PINS, A list of pins that the DAC will use.
                VREF, The DAC reference voltage.
                ADDRESS, The DAC address on the I2C line.
                voltages, A list of channels to enable the DAC channels.
    """
    def __init__(self, PINS, VREF = 5, RES = 12, ADDRESS = 0x0C, voltages = [0, 0, 0, 0]):
        self._VREF = VREF
        self._RES = RES
        self._ADDRESS = ADDRESS
        self._voltages = voltages


    def __str__(self):
        return str(self._voltages)

    def __iter__(self):
        for v in self._voltages:
            yield v 


    
    """
        This updates the voltages on the channels.
        Param: voltages, A list of voltages for the DAC to output.
    """
    def update_voltages(self, voltages = [0.0, 0.0, 0.0, 0.0]):
        
        self._voltages = voltages


    """
        This converts a voltage into an integer.
        Param: voltage, A voltage to convert.
        Return: The integer value of the voltage.
    """    
    def __voltage_to_int(self, voltage):
        conversion = 2 ** self._RES - 1
        scalar = float(conversion) / float(self._VREF)
        return int(voltage * scalar)


    """
        This turns the voltages for enabled channels on.
        Param: bus, The Raspberry Pi bus object.
    """
    def output_voltages(self, bus):
        cmd = 0x30
        temp_cmd1 = "{0:b}".format(cmd).zfill(8)[:4]
        for channel in range(len(self._voltages)):
            temp_cmd2 = "{0:b}".format(cmd).zfill(8)[4:]
            temp_cmd2_list = list(temp_cmd2)
            temp_cmd2_list[channel] = "1"
            temp_cmd2 = "".join(temp_cmd2_list)
            cmd_bits = temp_cmd1 + temp_cmd2
            cmd_int = int(cmd_bits, 2)
            ch_voltages = self.__voltage_to_int(self._voltages[channel])
            ch_voltages_bits = "{0:b}".format(ch_voltages).zfill(self._RES)

            voltages_bits_list = [ch_voltages_bits[i: i + 8] for i in range(0, len(ch_voltages_bits), 8)]
            while(len(voltages_bits_list[-1]) != 8):
                voltages_bits_list[-1] += "1"

            ch_voltages_int = []

            try:
                for voltage_bits in voltages_bits_list:
                    ch_voltages_int.append(int(voltage_bits, 2))
                bus.write_i2c_block_data(self._ADDRESS, cmd_int, ch_voltages_int)
            except:
                pass
