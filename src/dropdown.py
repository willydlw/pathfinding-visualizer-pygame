import pygame 

from .button import Button

class Dropdown:
    def __init__(self, x, y, width, height, options):
        self.is_open = False 
        self.options = options 
        self.buttons = [] 

        # Create a button for each option, stacked vertically 
        for i, text in enumerate(options):
            # y + h + (i * h) places buttons directly below the header button 
            self.buttons.append(Button(x, y + height + (i*height), width, height, text))

    
    def handle_event(self, event):
        if not self.is_open:
            return None 
        
        for btn in self.buttons:
            if btn.handle_event(event):
                self.is_open = False  # close after selection 
                return btn.text 
    
        return None 
    
    def draw(self, surface):
        if self.is_open:
            for btn in self.buttons:
                btn.draw(surface)