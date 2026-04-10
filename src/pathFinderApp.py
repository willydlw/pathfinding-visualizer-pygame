import pygame 
import pygame_gui 
from pygame_gui.elements import UIButton 

import json
import logging 

from .grid import Grid 
from .sidebar import Sidebar
from .algorithms import bfs, dfs, astar

from .constants import (
    Algorithm_Type,
    Animation_Mode,
    Map_Actions,
    Neighbor_Direction,
    Speed_Options,
    Terrain_Type,
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

        pygame.font.init() 
        self.font = pygame.font.SysFont('Arial', 14)

        if self.font is None:
            logger.fatal(f"Font failed to load")
        else:
            logger.info(f"Font loaded successfully: {pygame.font.get_default_font()}")

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
            sidebar_x
        )
        
        self.active_generator = None        # Holds the algorithms generator 
        self.step_requested = False 
        self.current_file_action = None 
        logging.info(f"PathFinderApp initialized")

    
    def _handle_events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False 

            # pygame_gui UIManager.process_events() handles input-based logic
            # Call it for every event retrieved from the Pygame event queue.
            self.ui_manager.process_events(event) 

            # Handles internal UI toggles
            self.sidebar.handle_events(event)

            # --- Handle Buttons ---
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                # App decides what to do when Sidebar buttons are pressed 
                if event.ui_element == self.sidebar.run_search_button:
                    selected = self.sidebar.algo_dropdown.selected_option 
                    algo_str = selected[0] if isinstance(selected, tuple) else selected 
                    self.start_search(algo_str)
                
                elif event.ui_element == self.sidebar.clear_button:
                     self.grid.clear() 
                     self.sidebar.uncheck_start_end() 

                elif event.ui_element == self.sidebar.next_step_button:
                     self.step_requested = True 

                elif event.ui_element == self.sidebar.clear_order_button:
                    # Clear the order
                    self.sidebar.neighbor_order_labels.clear()
                    self.sidebar.neighbor_order_display.set_item_list([])
                    
                    # Restore all cardinal options to Available
                    cardinals = ['North', 'East', 'South', 'West']
                    self.sidebar.available_list.set_item_list(cardinals)

                    

            # --- Handle File Dialog Logic --- 
            elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                if self.current_file_action == Map_Actions.LOAD_MAP:
                    self.grid.load_from_file(event.text)
                if self.current_file_action == Map_Actions.SAVE_MAP:
                    self.grid.save_to_file(event.text)

                self.current_file_action = None

            # --- Handle Dropdowns ---
            elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                logging.debug(f"event.text: {event.text}")
                # Terrain Brush
                if event.ui_element == self.sidebar.terrain_dropdown:
                      terrain = Terrain_Type[event.text].value
                      logging.debug(f"terrain: {terrain}")
                      self.grid.current_brush = terrain 
                # Map Actions
                elif event.ui_element == self.sidebar.map_dropdown:
                    logging.debug(f"Map_Actions.CREATE_MAP.name: {Map_Actions.CREATE_MAP.name}")
                    logging.debug(f"Map_Actions.LOAD_MAP.name:   {Map_Actions.LOAD_MAP.name}")
                    logging.debug(f"Map_Actions.SAVE_MAP.name:   {Map_Actions.SAVE_MAP.name}")

                    if event.text == Map_Actions.CREATE_MAP.name:
                        self.grid.clear() 
                        self.sidebar.uncheck_start_end() 
                    else:
                        # 1. Set the state so UI_FILE_DIALOG_PATH_PICKED knows what to do 
                        self.current_file_action = Map_Actions[event.text]
                        # 2. Opend the dialog via the sidebar
                        self.sidebar._handle_map_action(event.text)
                elif event.ui_element == self.sidebar.neighbor_order_dropdown:
                    self.search_bias = event.text
                    logging.debug(f"setting self.neighbor_order: {self.neighbor_order}")

            # Selection List 
            elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                # 1. User clicks an available direction
                if event.ui_element == self.sidebar.available_list:                   
                    selection = event.text
                    
                    # 1. Update Available list
                    # Extract only the string 'text' from the dictionaries in the list 
                    current_available_strings = [item['text'] for item in self.sidebar.available_list.item_list]

                    # Filter the strings
                    new_available = [text for text in current_available_strings if text != selection]

                    # Pass the list of strings to set_item_list
                    self.sidebar.available_list.set_item_list(new_available)

                    # 2. Update Order List
                    # Ensure you are using the correct variable name (you had a typo in neigbor)
                    if selection not in self.sidebar.neighbor_order_list:
                        self.sidebar.neighbor_order_list.append(selection)
                        self.sidebar.neighbor_order_display.set_item_list(self.sidebar.neighbor_order_list)

               
                # 2. (Optional) User clicks an item in the 'Order' list to move it BACK
                elif event.ui_element == self.sidebar.neighbor_order_display:
                    selection = event.text
                    
                    # Remove from Order list
                    if selection in self.sidebar.neighbor_order_list:
                        self.sidebar.neighbor_order_list.remove(selection)
                        self.sidebar.neighbor_order_display.set_item_list(self.sidebar.neighbor_order_list)
                    
                    # Add back to Available list
                    current_available_strings = [item['text'] for item in self.sidebar.available_list.item_list]
                    current_available_strings.append(selection)

                    # Sort it so the order stays 'North, East, South, West'

                    natural_order = ["North", "East", "South", "West"]
                    current_available_strings.sort(key=lambda x: natural_order.index(x)) 
                    self.sidebar.available_list.set_item_list(current_available_strings)
                                
                                    

            # TODO: Do we need this code for left clicks?
            # Pass the event to the grid to for "one-time" actions
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # left click
                    if not self.ui_manager.get_hovering_any_element():
                        # Only do single_click logic if a checkbox is active 
                        if self.sidebar.start_checkbox.is_checked or \
                            self.sidebar.end_checkbox.is_checked:
                            self.grid.handle_click_event(self.sidebar)


    def _update(self):

        time_delta = self.clock.tick(self.FPS) / 1000.0 

        # pygame_gui UIManager.update() handles time-based logic
        # must be called once every frame 
        self.ui_manager.update(time_delta)

        # Enable the next step button only if a search is actually in progress 
        if self.active_generator:
            self.sidebar.next_step_button.enable() 
        else:
            self.sidebar.next_step_button.disable()


        # Handle continuous painting only when NO search is running 
        if not self.active_generator:
            if not self.ui_manager.get_hovering_any_element():
                self.grid.handle_continuous_mouse(self.sidebar)
            return 
        
        # selected option is returning a list
        selected = self.sidebar.anim_dropdown.selected_option
        current_mode_str = selected[0] if isinstance(selected, (tuple, list)) else selected
        logging.debug(f"Type(selected): {type(selected)}, selected: {selected}")
        logging.debug(f"Current mode string: '{current_mode_str}'")

        current_mode = Animation_Mode[current_mode_str].value 
        logging.debug(f"Current mode enum: {current_mode}")

        if current_mode == Animation_Mode.INSTANT:
            try:
                self.sidebar.set_status("Searching...")

                # run until the generator signals True (finished)
                while True:
                    finished = next(self.active_generator)
                    if finished:
                        self.sidebar.set_status("<font color='#00FF00'>Path Found!</font>")
                        break 
                self.active_generator = None 
            except StopIteration:
                self.sidebar.set_status("<font color='#FF0000'>No Path Possible</font>")
                self.active_generator = None 
            
        elif current_mode == Animation_Mode.ANIMATED:
            speed_str = self.sidebar.speed_dropdown.selected_option 
            multiplier = Speed_Options.get_lookup().get(speed_str, Speed_Options.ANIM_1x).value

            if self.active_generator:
                self.sidebar.set_status("Searching...")

            for _ in range(multiplier):
                try:
                    if next(self.active_generator) is True:
                        self.sidebar.set_status("<font color='#00FF00'>Path Found!</font>")
                        self.active_generator = None 
                        break 
                except StopIteration:
                    self.sidebar.set_status("<font color='#FF0000'>No Path Possible</font>")
                    self.active_generator = None 
                    break 

        elif current_mode == Animation_Mode.SINGLE_STEP:
            logging.info("TRUE current_mode == Animation_Mode.SINGLE_STEP")

            if self.step_requested:
                try:
                    # Step the algorithm once
                    finished = next(self.active_generator)
                    if finished:
                        self.sidebar.set_status("Path Found!")
                        self.active_generator = None 
                        #self.searching = False
                    else:
                        self.sidebar.set_status("Stepping...")
                except StopIteration:
                    self.sidebar.set_status("No Path Possible")
                    self.active_generator = None
                    #self.searching = False  

            # Critical: Reset the flag so it waits for the next button press
            self.step_requested = False # reset the flag after one step


    def _draw(self):
        self.screen.fill(self.COLOR_BG)
        self.grid.draw(self.screen, self.font)

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
            self._handle_events()
            self._update()
            self._draw() 


    def start_search(self, algo_name):

        logging.info(f"algo_name: {algo_name}")

        # 1. Validation:Ensure start and end are set 
        if not self.grid.start_node or not self.grid.end_node:
            logging.warning("Select both a Start and End node first!")
            return 
        
        # 2. Validation: ensure start and end are on the same terrain type 
        start_terrain = self.grid.start_node.terrain 
        end_terrain = self.grid.end_node.terrain 

        if start_terrain != end_terrain:
            logging.error(
                f"Terrain mismatch! Start is {start_terrain}, "
                f"End is {end_terrain}. They must match."
            )
            return 
        
        # UI Cleanup: Uncheck start/end boxes before starting search to avoid 
        # accidentally changing during the search 
        self.sidebar.uncheck_start_end()

        # Reset any previous search state
        self.grid.reset_search_data()

        # In case there is any currently running search, set the generator to None
        # before staring the new search 
        self.active_generator = None 

        # Neighbor Search Directions 
        lookup = Neighbor_Direction.get_lookup() 

        # Fallback to a default order if the list is empty 
        if not self.sidebar.neigbor_order_list:
            search_order = [d.vector for d in [Neighbor_Direction.NORTH, Neighbor_Direction.SOUTH,
                                               Neighbor_Direction.EAST, Neighbor_Direction.WEST]]
        else:
            search_order = [lookup[label].vector for label in self.sidebar.neigbor_order_list]

        self.sidebar.set_status("Searching...")
 
        # Initialize the generator
        logging.debug(f"algo_name: {algo_name}, Algorithm_Type.BFS.name: {Algorithm_Type.BFS.name}")
        if algo_name == Algorithm_Type.BFS.name:
            logging.info(f"Calling bfs()")
            self.active_generator = bfs(self.grid, self.grid.start_node, self.grid.end_node, search_order)
        elif algo_name == Algorithm_Type.DFS.name:
            logging.info(f"Calling dfs()")
            self.active_generator = dfs(self.grid, self.grid.start_node, self.grid.end_node, search_order)
        elif algo_name == Algorithm_Type.ASTAR.name:
            logging.info("calling astar()")
            self.active_generator = astar(self.grid, self.grid.start_node, self.grid.end_node, search_order)
           
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
