import pygame 

from .button import Button 
from .dropdown import Dropdown

class Header:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)

        # ---- Main Category Buttons ----
        self.algo_btn = Button(10, 10, 120, 30, "Algorithms")
        self.map_btn = Button(140, 10, 120, 30, "Map")

        # ---- Dropdown Menus ----
        self.algo_menu = Dropdown(10, 10, 120, 30, ["A*", "Dijkstra", "BFS", "DFS"])
        self.map_menu = Dropdown(140, 10, 120, 30, ["Load", "Create", "Save", "Clear"])


    def handle_events(self, event):
        # Check Algorithm dropdown
        algo_selection = self.algo_menu.handle_event(event)
        if algo_selection:
            return algo_selection 
        
        # Check Map dropdown 
        map_selection = self.map_menu.handle_event(event)
        if map_selection:
            return map_selection
        
        # Handle main button toggles
        if self.algo_btn.handle_event(event):
            self.algo_menu.is_open = not self.algo_menu.is_open 
            self.map_menu.is_open = False 

        if self.map_btn.handle_event(event):
            self.algo_menu.is_open = False
            self.map_menu.is_open = not self.map_menu.is_open 


        return None 
    
    def draw(self, surface):
        pygame.draw.rect(surface, (40, 40, 40), self.rect)
        self.algo_btn.draw(surface)
        self.algo_menu.draw(surface) # draws on top if open
        self.map_btn.draw(surface)
        self.map_menu.draw(surface)