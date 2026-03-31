import pygame 
import pygame_gui 
from pygame_gui.elements import UIButton 

import logging 

from .grid import Grid 

logger = logging.getLogger(__name__)


class PathFinderApp:
    # Class constants
    FPS = 60

    CELL_SIZE_PIXELS = 12 
    NUM_GRID_CELLS = 64      # number of cells
    SIDEBAR_WIDTH = 300 

    GRID_WIDTH = NUM_GRID_CELLS * CELL_SIZE_PIXELS 
    
    WINDOW_WIDTH = GRID_WIDTH + SIDEBAR_WIDTH
    WINDOW_HEIGHT = GRID_WIDTH 

    # Colors (RGB)
    COLOR_BG = (30, 30, 30)             # Dark gray 
    
    COLOR_SIDEBAR = (240, 240, 240)     # Off-white for UI 
    COLOR_WALKABLE = (46, 204, 113)     # Green walkable area 

    def __init__(self):

        # window attributes
        pygame.init() 
        self.screen_width = self.WINDOW_WIDTH 
        self.screen_height = self.WINDOW_HEIGHT 

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Pathfinding Visualizer")

        # application state 
        self.clock = pygame.time.Clock() 
        self.running = True 

        # Grid 
        self.grid = Grid(0, 0, self.NUM_GRID_CELLS, self.CELL_SIZE_PIXELS)

        # UI Management 
        self.ui_manager = pygame_gui.UIManager((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))

        # Create a button 
        self.load_button = UIButton(relative_rect=pygame.Rect((self.GRID_WIDTH + 50, 100), (200, 50)),
                                    text='Load Map',
                                    manager=self.ui_manager)
        
        logging.info(f"PathFinderApp initialized")

    
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False 

            # Process UI events 
            self.ui_manager.process_events(event) 

            # Handle specific UI actions 
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.load_button:
                    print("Load Map clicked!")



    def _update(self):
        pass 
    

    def _draw(self):
        self.screen.fill(self.COLOR_BG)
        self.grid.draw(self.screen)

        # draw sidebar 
        sidebar_rect = pygame.Rect(self.GRID_WIDTH, 0, self.SIDEBAR_WIDTH, self.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, self.COLOR_SIDEBAR, sidebar_rect)

        # render UI elements 
        self.ui_manager.draw_ui(self.screen)

        # update display
        pygame.display.flip() 


    def run(self):
        """The main application loop."""
        while self.running:
            # update based on delta time 
            time_delta = self.clock.tick(self.FPS) / 1000.0 
            self._handle_events()
            self.ui_manager.update(time_delta)

            self._draw() 
            self.clock.tick(self.FPS)