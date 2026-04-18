import pygame 
import pygame_gui 
from pygame_gui.elements import UIButton
from pygame_gui.windows import UIConfirmationDialog 

import json
import logging 
import os 

from .appConfig import AppConfig
from .algo_settings import Algo_Settings
from .grid import Grid 
from .sidebar import Sidebar
from .algorithms import bfs, dfs, astar

from .constants import (
    Algorithm_Type,
    Animation_Mode,
    Map_Actions,
    Map_Dimension,
    Neighbor_Connectivity,
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

        # Preloading this font to avoid a warning when UI later has to load it.
        self.ui_manager.preload_fonts([
                {'name': 'noto_sans', 'point_size': 14, 'style': 'bold'},
            ])

        # Position sidebar after the grid + extra padding 
        sidebar_x = self.config.GRID_WIDTH + (self.config.GRID_PADDING * 2)
        self.sidebar = Sidebar(
            self.ui_manager,
            self.config
        )

        self.algo_settings = Algo_Settings()
        
        self.active_generator = None        # Holds the algorithms generator 
        self.step_requested = False 
        self.pending_save_path = None
        self.pending_grid_size = None 
        self.confirmation_dialog = None
        
        self.left_button_held = False 
        self.right_button_held = False 

        self.current_brush = Terrain_Type.get_default().label
        

        logging.info(f"PathFinderApp initialized")

    
    def _handle_events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False 

            # pygame_gui UIManager.process_events() handles input-based logic
            # Call it for every event retrieved from the Pygame event queue.
            self.ui_manager.process_events(event) 

            # Handles internal UI changes
            self.sidebar.handle_events(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    self.left_button_held = True 
                elif event.button == 3:  
                    self.right_button_held = True 

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: 
                    self.left_button_held = False 
                elif event.button == 3:
                    self.right_button_held = False 

            # --- Handle UI Buttons ---
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                # reset grid 
                if event.ui_element == self.sidebar.btn_reset_grid:
                    self.grid.clear(self.current_brush)
                    self.sidebar.uncheck_start_end()

                # run search
                elif event.ui_element == self.sidebar.btn_run_search:
                    selected = self.sidebar.select_algo.selected_option 
                    algo_str = selected[0] if isinstance(selected, tuple) else selected 
                    logging.info(f"run search button pressed, selected: {selected}")
                    logging.info(f"algo_str: {algo_str}")
                    self.start_search(algo_str)

                
                """
                elif event.ui_element == self.sidebar.next_step_button:
                     self.step_requested = True 

                elif event.ui_element == self.sidebar.clear_order_button:
                    # Clear the order
                    self.sidebar.neighbor_order_list.clear()
                    self.sidebar.neighbor_order_display.set_item_list([])
                    self.sidebar.refresh_available_list()
                """
            

            # --- Handle UI Checkboxes ---
            elif event.type == pygame_gui.UI_CHECK_BOX_CHECKED:
                if event.ui_element == self.sidebar.btn_random_order:
                    self.algo_settings.randomize_neighbors = True 

            elif event.type == pygame_gui.UI_CHECK_BOX_UNCHECKED:
                if event.ui_element == self.sidebar.btn_random_order:
                    self.algo_settings.randomize_neighbors = False


            # --- Handle Dropdowns ---
            elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                
                # Terrain Brush
                if event.ui_element == self.sidebar.select_terrain:
                    terrain = Terrain_Type.from_label(event.text)
                    self.current_brush = terrain 
                    logging.info(f"detected select_terrain: {terrain}")

                elif event.ui_element == self.sidebar.select_grid_dimensions:
                    logging.info(f"Detected grid size change")
                    # Store the intended size but don't apply it yet 
                    self.pending_grid_size = Map_Dimension.from_label(event.text).value

                    # Define the dialog dimensions 
                    dialog_w, dialog_h = 300, 200 

                    # Calculate center position 
                    center_x = (self.screen_width - dialog_w) // 2 
                    center_y = (self.screen_height - dialog_h) // 2
                
                    # Create the confirmation dialog
                    self.confirmation_dialog = UIConfirmationDialog(
                        rect=pygame.Rect((center_x, center_y), (dialog_w, dialog_h)), # Center this as needed
                        manager=self.ui_manager,
                        window_title="Confirm Grid Resize",
                        action_long_desc="Resizing the grid will <b>clear all current drawings</b>. Do you want to proceed?",
                        action_short_name="Yes, Resize",
                        blocking=True
                    )
                
                elif event.ui_element == self.sidebar.select_algo:
                    logging.info(f"select_algo dropdown, event.text: {event.text}")
                    # convert string to enum 
                    algo = Algorithm_Type.from_label(event.text)
                    self.algo_settings.algorithm = algo 

                elif event.ui_element == self.sidebar.select_neighbor_connectivity:
                    logging.info(f"select_neighbor_connectivity dropdown, event.text: {event.text}")
                    
                    # convert string to enum 
                    connectivity = Neighbor_Connectivity.from_label(event.text)

                    # apply to pathfinding logic 
                    self.algo_settings.neighbor_connectivity = connectivity

            elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION: 
                # Check if the event came from either of the two direction lists 
                if "#available_direction_selector" in event.ui_object_id or \
                   "#list_selected_order" in event.ui_object_id:
                    
                    # read the current visual state from the sidebar 
                    new_order = self.sidebar.get_selected_directions()

                    logging.info(f"event selection_list_new_selection, new_order: {new_order}")

                    # update the algorithm settings
                    self.algo_settings.neighbor_directions = new_order


            # --- Handle File Dialog Logic --- 
            elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                if event.ui_element.most_specific_combined_id == "#map_file_dialog":
                    dialog_title = event.ui_element.window_display_title
                   
                    if dialog_title == Map_Actions.LOAD_MAP.window_title:
                        self.grid.load_from_file(event.text)

                    elif dialog_title == Map_Actions.SAVE_MAP.window_title:
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
                    self.grid.save_to_file(self.pending_save_path)
                    self.pending_save_path = None 
                
                if self.pending_grid_size is not None:
                    self.grid.resize_grid(self.pending_grid_size)

                    # reset the pending variable soe it doesn't trigger again accidentally
                    self.pending_grid_size = None 
                    
            elif event.type == pygame_gui.UI_WINDOW_CLOSE:
                if event.ui_element ==  self.confirmation_dialog:
                    # User cancelled! Revert dropdown to the actual current grid size
                    # Find the label corresponding to the current grid rows 
                    current_dim_label = Map_Dimension(self.grid.rows).label 


                    # Kill and recreate is the standard for "pygame-gui>=0.6.14",
                    # Grab existing rect
                    old_rect = self.sidebar.select_grid_dimensions.relative_rect
                    
                    self.sidebar.select_grid_dimensions.kill()
                    self.sidebar.select_grid_dimensions = pygame_gui.elements.UIDropDownMenu(
                        options_list=Map_Dimension.options_list(),
                        starting_option=current_dim_label,
                        relative_rect=old_rect,
                        manager=self.sidebar.manager,
                        container=self.sidebar.panel_map_config,
                        object_id="#grid_dimensions_selector"
                    )

                    # clear the pending state
                    self.pending_grid_size = None 



    def _handle_continuous_mouse(self):
        """Handles painting terrain/start/end while mouse is pressed."""
        if self.ui_manager.get_hovering_any_element():
            return 
        
    
        pos = pygame.mouse.get_pos() 
        node = self.grid.get_node_from_pos(pos)
        if not node:
            return
        
        #logging.info(f"self.left_button_held: {self.left_button_held}")
        #logging.info(f"self.right_button_held: {self.right_button_held}")
       
        # Handle painting (start/end/terrain)
        if self.left_button_held:
            # Handle start node placement
            if self.sidebar.check_start.is_checked:
                self.grid.set_start(node)

            elif self.sidebar.check_end.is_checked:
                self.grid.set_end(node)

            # Handle regular painting
            else:
                node.set_terrain(self.current_brush)
            

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
            self._handle_continuous_mouse()
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

        # Reset any previous search state information
        self.grid.reset_search_data()

        # In case there is any currently running search, set the generator to None
        # before staring the new search 
        self.active_generator = None 

        # Neighbor Search Directions 
        lookup = Neighbor_Direction.get_lookup() 

        item_list = self.sidebar.list_active_order.item_list 
        neighbor_search_order = [item['text'] for item in item_list]
        logging.info(f"neighbor_search_order: {neighbor_search_order}")


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
