import pygame 
import pygame_gui 
from pygame_gui.elements import UIButton 

import logging 

from .grid import Grid 
from .sidebar import Sidebar

logger = logging.getLogger(__name__)


class PathFinderApp:
    # Class constants
    FPS = 60

    CELL_SIZE_PIXELS = 12 
    NUM_GRID_CELLS = 64      # number of cells
    SIDEBAR_WIDTH = 300 

    GRID_WIDTH = NUM_GRID_CELLS * CELL_SIZE_PIXELS 

    PADDING = 20   # space around the grid 

    WINDOW_WIDTH = GRID_WIDTH + SIDEBAR_WIDTH + (PADDING * 3) # left, middle, right
    WINDOW_HEIGHT = GRID_WIDTH + (PADDING * 2)                # top, bottom

    # Colors (RGB)
    COLOR_BG = (225, 225, 225)
    
    COLOR_SIDEBAR = (240, 240, 240)     # Off-white for UI 
  

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

        # Position grid within padding
        self.grid = Grid(self.PADDING, self.PADDING, self.NUM_GRID_CELLS, self.CELL_SIZE_PIXELS)

        # UI Management 
        self.ui_manager = pygame_gui.UIManager((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))

        # Position sidebar after the grid + extra padding 
        sidebar_x = self.GRID_WIDTH + (self.PADDING * 2)
        self.sidebar = Sidebar(
            self.ui_manager,
            self.SIDEBAR_WIDTH,
            self.WINDOW_HEIGHT,
            sidebar_x, 
            self.grid,
            self
        )
        
        self.active_generator = None        # Holds the BFS generator 

        logging.info(f"PathFinderApp initialized")

    
    def _handle_events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False 

            # Process UI events 
            self.ui_manager.process_events(event) 
            self.sidebar.handle_events(event)



    def _update(self):

        # Check if a search is currently animating
        if self.active_generator:
            try:
                finished = next(self.active_generator)
                if finished:
                    self.active_generator = None 
                    logging.info("Search finished.")
            except StopIteration:
                self.active_generator = None 
        else:
            # Check if dialog is blocking the mouse
            is_blocking = self.ui_manager.get_hovering_any_element() 

            if not is_blocking:
                self.grid.handle_mouse() 

        

    

    def _draw(self):
        self.screen.fill(self.COLOR_BG)
        self.grid.draw(self.screen)

        # draw sidebar background with padding
        sidebar_x = self.GRID_WIDTH + (self.PADDING * 2)
        sidebar_rect = pygame.Rect(sidebar_x, self.PADDING, self.SIDEBAR_WIDTH, self.GRID_WIDTH)
        pygame.draw.rect(self.screen, self.COLOR_SIDEBAR, sidebar_rect, border_radius=8)

        # render UI elements 
        self.ui_manager.draw_ui(self.screen)

        # update display
        pygame.display.flip() 


    def run(self):
        while self.running:
            time_delta = self.clock.tick(self.FPS) / 1000.0 

            self._handle_events()
            self.ui_manager.update(time_delta)
            self._update()

            self._draw() 