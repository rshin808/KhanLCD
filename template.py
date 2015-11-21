"""
    File: template.py
    By  : Reed Shinsato
    Desc: This implements the class for template images from bitmaps.
"""

# Libraries
import os
import csv
import datetime as dt


class Template_img:
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
        self._btest = []
        s = dt.datetime.now()
        self.__create_bitmap(img)
        e = dt.datetime.now()

    def __str__(self):
        return self._name

    def __create_bitmap(self, img):
        """
            This creates the bitmap for the template given an image.
            The bitmap values match the values for the SEPS525.
            Note: To reduce delay change .csv to have more than 2 values per row
        """
        script_path = os.path.dirname(os.path.realpath(__file__))
        img_path = os.path.join(script_path, img)
        with open(img_path, "rb") as img_csv:
            reader = csv.reader(img_csv)
            for row in reader:
                self._bitmap.append(tuple([int(row[0]), int(row[1])]))

    """
        This updates the oled based on the current template.
        Param: oled, The oled driver object.
    """    
    def update_oled(self, oled):
        oled.seps525_set_region(0, 0, 160, 128)
        oled.data_start()
        value = []
        for pixel in self._bitmap:
            value.append(pixel[0])
            value.append(pixel[1])
        for i in range(10):
            oled.data(value[(4096 * i): (4096 * i + 4096)])
        

    """
        This returns the name of the template.
        Return: The name of the template.
    """
    def name(self):
        return self._name


    """
        This returns the bitmap of the template.
        Return: The bitmap currently saved.
    """
    def bitmap(self):
        return self._bitamp


"""
# This is test code.
test = template_img("test", "VIMeas1.csv")
test.update_oled()
"""
