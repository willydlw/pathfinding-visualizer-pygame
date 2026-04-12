import pygame 
import pygame_gui 
from pygame_gui.elements import UIButton
from pygame_gui.windows import UIConfirmationDialog 

import json
import logging 
import os 

from .appConfig import AppConfig
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
   
    def __init__(self, config: AppConfig):

        # window attributes
        self.config = config 
        self.screen_width = config.GRID_WIDTH + config.SIDEBAR_WIDTH + (config.GRID_PADDING * 3) 
        self.screen_height = config.GRID_WIDTH + (config.GRID_PADDING * 2)

        # pygame initialization
        pygame.init() 
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
        self.grid = Grid(self.config.GRID_PADDING, self.config.GRID_PADDING, 
                         self.config.GRID_WIDTH, self.config.DEFAULT_GRID_SIZE)

        # UI Management 
        try:
            self.ui_manager = pygame_gui.UIManager(
                (self.screen_width, self.screen_height),
                'theme.json'
                )
        except json.JSONDecodeError as e:
            logging.error(f"problem with 'theme.json'")
            logging.error(f"Details: {e.msg} at line {e.lineno}, column {e.colno}")
            self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height))
        except FileNotFoundError:
            logging.error(f"File 'theme.json' not found")
            self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height))

        # Position sidebar after the grid + extra padding 
        sidebar_x = self.config.GRID_WIDTH + (self.config.GRID_PADDING * 2)
        self.sidebar = Sidebar(
            self.ui_manager,
            self.config
        )
        
        self.active_generator = None        # Holds the algorithms generator 
        self.step_requested = False 
        self.pending_save_path = None
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
                #logging.fatal(f"Uncomment run_search_button")
                #logging.fatal(f"Uncomment next_step_button")
                #logging.fatal(f"Uncomment clear_order_button")
                #logging.fatal(f"Uncomment clear_grid_button")

                """
                if event.ui_element == self.sidebar.clear_grid_button:
                     self.grid.clear() 
                     self.sidebar.uncheck_start_end() 
                
                if event.ui_element == self.sidebar.run_search_button:
                    selected = self.sidebar.algo_dropdown.selected_option 
                    algo_str = selected[0] if isinstance(selected, tuple) else selected 
                    self.start_search(algo_str)
                
                elif event.ui_element == self.sidebar.next_step_button:
                     self.step_requested = True 

                elif event.ui_element == self.sidebar.clear_order_button:
                    # Clear the order
                    self.sidebar.neighbor_order_list.clear()
                    self.sidebar.neighbor_order_display.set_item_list([])
                    self.sidebar.refresh_available_list()
                """
                    

            # --- Handle File Dialog Logic --- 
            elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                # Use the window title to decide what to do 
                dialog_title = event.ui_element.window_display_title 

                if dialog_title == Map_Actions.LOAD_MAP.label:
                    logging.info(f"Loading map from {event.text}")
                    self.grid.load_from_file(event.text)
                elif dialog_title == Map_Actions.SAVE_MAP.label:
                    logging.info(f"Saving map to {event.text}")
                    if os.path.exists(event.text):
                        self.pending_save_path = event.text 
                        UIConfirmationDialog(
                            rect=pygame.Rect(250, 200, 300, 200),
                            manager=self.ui_manager,
                            action_long_desc=f"The file '{os.path.basename(event.text)}' already exists. Overwrite?",
                            window_title="Confirm Overwrite",
                            action_short_name="Overwrite",
                            blocking=True
                        )
                    else:
                        self.grid.save_to_file(event.text)

            elif event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                if self.pending_save_path:
                    logging.info(f"Overwriting file {self.pending_save_path}")
                    self.grid.save_to_file(self.pending_save_path)
                    self.pending_save_path = None 


            # --- Handle Dropdowns ---
            elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                logging.debug(f"event.text: {event.text}")

                # Terrain Brush
                if event.ui_element == self.sidebar.terrain_type_dropdown:
                    terrain = Terrain_Type[event.text].value
                    self.grid.current_brush = terrain 

                elif event.ui_element == self.sidebar.grid_dimensions_dropdown:
                    logging.fatal(f"need logic for changing grid dimensions")

                # Map Actions
                elif event.ui_element == self.sidebar.map_dropdown:
                    logging.debug(f"map_dropdown event: {event.text}")
                    #logging.debug(f"Map_Actions.CREATE_MAP.name: {Map_Actions.CREATE_MAP.name}")
                    #logging.debug(f"Map_Actions.LOAD_MAP.name:   {Map_Actions.LOAD_MAP.name}")
                    #logging.debug(f"Map_Actions.SAVE_MAP.name:   {Map_Actions.SAVE_MAP.name}")

                    if event.text == Map_Actions.CREATE_MAP.name:
                        self.grid.clear() 
                        self.sidebar.uncheck_start_end() 
              

            # Selection List 
            #logging.fatal(f"Uncomments UI_SELECTION_LIST_NEW_SELECTION")
            """
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
                    current_available = [item['text'] for item in self.sidebar.available_list.item_list]
                    current_available.append(selection)

                    # Sort it so the order stays 'North, East, South, West'
                    sorted_available = Neighbor_Direction.sort_labels(current_available)
                    self.sidebar.available_list.set_item_list(sorted_available)
                                
                """

            #logging.fatal("uncomment start_checkbox logic")
            # TODO: Do we need this code for left clicks?
            # Pass the event to the grid to for "one-time" actions
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # left click
                    if not self.ui_manager.get_hovering_any_element():
                        # Only do single_click logic if a checkbox is active 
                        logging.fatal("uncomment start_checkbox logic")
                        """
                        if self.sidebar.start_checkbox.is_checked or \
                            self.sidebar.end_checkbox.is_checked:
                            self.grid.handle_click_event(self.sidebar)
                        """


    def _update(self):

        time_delta = self.clock.tick(self.config.FPS) / 1000.0 

        # pygame_gui UIManager.update() handles time-based logic
        # must be called once every frame 
        self.ui_manager.update(time_delta)

        # Enable the next step button only if a search is actually in progress 
        #if self.active_generator:
            #self.sidebar.next_step_button.enable() 
            #logging.fatal(f"Uncomment next_step_button.enable")
        #else:
            #self.sidebar.next_step_button.disable()
            #logging.fatal(f"Uncomment next_step_button.disable")


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
        self.screen.fill(self.config.COLOR_BACKGROUND)
        self.grid.draw(self.screen, self.font)

        # draw sidebar background with padding
        sidebar_x = self.config.GRID_WIDTH + (self.config.GRID_PADDING * 2)
        sidebar_rect = pygame.Rect(sidebar_x, self.config.GRID_PADDING, self.config.SIDEBAR_WIDTH, self.config.GRID_WIDTH)
        pygame.draw.rect(self.screen, self.config.COLOR_SIDEBAR, sidebar_rect, border_radius=8)

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
