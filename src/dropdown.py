import pygame 
import logging 

from .button import Button


logger = logging.getLogger(__name__)

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
        
        # check if an option was clicked
        button_hit = False 
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            if btn.rect.collidepoint(mouse_pos):
                button_hit = True 
            
            result = btn.handle_event(event)
            if result:
                logging.info(f"Button action triggered: {result}")
                self.is_open = False  # close after selection 
                return result 
    
        # Only close if a MOUSEBUTTONDOWN happened AND it wasn't on a button 
        if event.type == pygame.MOUSEBUTTONDOWN and not button_hit:
            self.is_open = False

        return None 
    
    def draw(self, surface):
        if self.is_open:
            for btn in self.buttons:
                btn.draw(surface)