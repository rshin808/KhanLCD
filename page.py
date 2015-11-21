from template import Template_img as Temp
from text import Text_string as TS
from font import Font


class Page(Temp):
    def __init__(self, name, filename, selection):
        Temp.__init__(self, name, filename)
        self._current_pos = 0
        self._selection = tuple(selection)
        
    def init(self, display):
       pass
    
    
    def update_pos(self, direction, display):
        pass 
        
    def select_pos(self, display, check):
        pass 
