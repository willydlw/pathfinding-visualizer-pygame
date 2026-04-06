import pygame 
import pygame_gui 
from pygame_gui.elements import UIButton 

import logging 

from .grid import Grid 
from .sidebar import Sidebar
from .algorithms import bfs, dfs 

from .constants import (
    ANIMATION_MODE,
    ANIMATION_MODE_NAMES,
    SPEED_OPTION_NAMES,
    SPEED_OPTIONS
)

logger = logging.getLogger(__name__)


class PathFinderApp:
    # Class constants
    FPS = 60

    NUM_GRID_CELLS = 8      # number of cells
    SIDEBAR_WIDTH = 400

    GRID_WIDTH = 768        # pixels

    PADDING = 20       # space around the grid 

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

        # Grid position top left x,y with padding on left and above
        self.grid = Grid(self.PADDING, self.PADDING, self.GRID_WIDTH, self.NUM_GRID_CELLS,)

        # UI Management 
        try:
            self.ui_manager = pygame_gui.UIManager(
                (self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
                'theme.json'
                )
        except json.JSONDecodeError as e:
            logging.error(f"problem with 'theme.json'")
            logging.error(f"Details: {e.msg} at line {e.lineno}, column {e.colno}")
            self.ui_manager = pygame_gui.UIManager((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        except FileNotFoundError:
            logging.error(f"File 'theme.json' not found")
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
        
        self.active_generator = None        # Holds the algorithms generator 
        self.step_requested = False 
        logging.info(f"PathFinderApp initialized")

    
    def _handle_events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False 

            # Process UI events 
            self.ui_manager.process_events(event) 
            self.sidebar.handle_events(event)

            # Pass the event to the grid to for "one-time" actions
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # left click
                    if not self.ui_manager.get_hovering_any_element():
                        # Only do single_click logic if a checkbox is active 
                        if self.sidebar.start_checkbox.is_checked or \
                            self.sidebar.end_checkbox.is_checked:
                            self.grid.handle_click_event(self.sidebar)


    def _update(self):

        # Handle continuous painting only when NO search is running 
        if not self.active_generator:
            if not self.ui_manager.get_hovering_any_element():
                self.grid.handle_continuous_mouse(self.sidebar)
            return 
        
        current_mode_str = self.sidebar.anim_dropdown.selected_option
        current_mode = next((k for k, v in ANIMATION_MODE_NAMES.items() if v == current_mode_str), ANIMATION_MODE.ANIMATED)

        if current_mode == ANIMATION_MODE.INSTANT:
            try:
                # run until the generator signals True (finished)
                while next(self.active_generator) is False:
                    pass     
                self.active_generator = None 
            except StopIteration:
                self.active_generator = None 
                logging.info("Active Generation is done.")

        elif current_mode == ANIMATION_MODE.ANIMATED:
            speed_str = self.sidebar.speed_dropdown.selected_option 
            multiplier = next((k.value for k, v in SPEED_OPTION_NAMES.items() if v == speed_str), 1)

            for _ in range(multiplier):
                try:
                    if next(self.active_generator) is True:
                        self.active_generator = None 
                        break 
                except StopIteration:
                    self.active_generator = None 
                    break 

        elif current_mode == ANIMATION_MODE.SINGLE_STEP:
            # Handle manual step logic
            if self.step_requested:
                try:
                    finished = next(self.active_generator)
                    if finished:
                        self.active_generator = None 
                except StopIteration:
                    self.active_generator = None 

                self.step_requested = False # reset the flag after one step


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


    def start_search(self, algo_name):
        
        # Uncheck start/end boxes before starting search to avoid 
        # accidentally changing during the search 
        self.sidebar.uncheck_start_end()

        # Reset any previous search state
        self.grid.reset_search_data()
        
        # Initialize the generator based on the dropdown choice
        if algo_name == "BFS":
            self.active_generator = bfs(self.grid, self.grid.start_node, self.grid.end_node)
        elif algo_name == "DFS":
            self.active_generator = dfs(self.grid, self.grid.start_node, self.grid.end_node)
        
        self.step_requested = False
        logging.info(f"Search started: {algo_name}")



    def step_search(self):
        if self.active_generator:
            try:
                # Get the next "frame" of the algorithm 
                next(self.active_generator)
            except StopIteration:
                self.active_generator = None 
                logging.info("Search finished.")
