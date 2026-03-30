import pygame 

from button import Button 
from dropdown import Dropdown

class Header:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.algo_btn = Button(10, 10, 120, 30, "Algorithms")

        self.algo_menu = Dropdown(10, 10, 120, 30, ["A*", "Dijkstra", "BFS", "DFS"])

    def handle_events(self, event):
        # Check dropdown first. It has priority if open.
        selection = self.algo_menu.handle_event(event)
        if selection:
            return selection 
        
        # Check main button to toggle the menu 
        if self.algo_btn.handle_event(event):
            self.algo_menu.is_open = not self.algo_menu.is_open 

        return None 
    
    def draw(self, surface):
        pygame.draw.rect(surface, (40, 40, 40), self.rect)
        self.algo_btn.draw(surface)
        self.algo_menu.draw(surface) # draws on top if open