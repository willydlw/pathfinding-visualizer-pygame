import pygame 
import pygame_gui 
from pygame_gui.elements import UIDropDownMenu, UILabel, UIButton, UICheckBox
from pygame_gui.windows import UIFileDialog 


import logging 

from .constants import TERRAIN_TYPES, TERRAIN_NAMES, MAP_ACTION_TYPES, MAP_ACTION_DICT
from .algorithms import bfs, dfs

logger = logging.getLogger(__name__)

class Sidebar:
    def __init__(self, manager, width, height, x_offset, grid, app):
        self.manager = manager 
        self.grid = grid
        self.app = app

        # Track the active dialog to distinguish between Load and Save actions
        self.active_file_dialog = None 
        self.current_action = None 

        # UI Layout Constants 
        padding = 10 
        label_width = 110
        widget_height = 35 
        full_widget_width = width - (padding * 2)
        right_col_width = width - label_width - (padding * 3)

        col1_x = x_offset + padding 
        col2_x = col1_x + label_width + padding 

        # --- Row 1: Environment Map ---
        self.map_label = UILabel(
            relative_rect=pygame.Rect((col1_x, 20), (label_width, widget_height)),
            text="Map Actions:",
            manager=self.manager
        )

        self.map_dropdown = UIDropDownMenu(
            options_list=list(MAP_ACTION_DICT.values()),
            starting_option=MAP_ACTION_DICT[MAP_ACTION_TYPES.CREATE],
            relative_rect=pygame.Rect((col2_x, 20),(right_col_width, widget_height)),
            manager=self.manager
        )

        # --- Row 2: Terrain ---
        self.terrain_label = UILabel(
            relative_rect=pygame.Rect((col1_x, 70), (label_width, widget_height)),
            text="Terrain Type:",
            manager=self.manager
        )

        self.terrain_dropdown = UIDropDownMenu(
            options_list=list(TERRAIN_NAMES.values()),
            starting_option=TERRAIN_NAMES[TERRAIN_TYPES.GRASS],
            relative_rect=pygame.Rect((col2_x, 70), (right_col_width, widget_height)),
            manager=self.manager
        )

        # --- Row 3: Algorithm --- 
        self.algo_label = UILabel(
            relative_rect=pygame.Rect((col1_x, 120), (label_width, widget_height)),
            text="Algorithm:",
            manager=self.manager
        )

        self.algorithms = ["BFS", "DFS", "A*"]
        self.algo_dropdown = UIDropDownMenu(
            options_list=self.algorithms,
            starting_option=self.algorithms[0],
            relative_rect=pygame.Rect((col2_x, 120), (right_col_width, widget_height)),
            manager=self.manager
        )

        # --- Row 4: Action Buttons 
        self.search_button = UIButton(
            relative_rect=pygame.Rect((col1_x, 180), (full_widget_width, widget_height)),
            text="RUN SEARCH",  
            manager=self.manager
        )

        self.clear_button = UIButton(
            relative_rect=pygame.Rect((col1_x, 230), (full_widget_width, widget_height)),
            text="CLEAR GRID",
            manager=self.manager
        )

        # --- Row 5: Start/End Selection ---
        self.start_checkbox = UICheckBox(
            relative_rect=pygame.Rect((col1_x, 280), (100, widget_height)),
            text="Set Start",
            manager=self.manager
        )


        self.end_checkbox = UICheckBox(
            relative_rect=pygame.Rect((col2_x, 280), (100, widget_height)),
            text="Set End",
            manager=self.manager
        )

        # Mapping 
        # Label: Environment Map 
        # Default (64x64) with a default map loaded
        # Small (8x8)
        # L-shaped wall (16 x 16)
        # Sparse Canvas (128 x 128)
        # Dense Canvas (256 x 256)
        # Maze (128 x 128)
        # Wheel of War? (256 x 256)

        # Legal Actions
        # Object must be within the map bounds 
        # Move in 4 directions Cardinal (4 neighbors)
        # Move in 8 directions Diagonal (8 neighbors)
        # Object can only move to a space if it is the same color as where it is currently
        # Object cannot move off the map
        # Action costs are all 100 for width, height and approx 141 for diagonal

        # Toggle Grid button that turns displaying grid on/off

        # Object Size
        # TODO: Select size of object finding its path
        # Examples: 1x1 Square, 2x2 square

        # Visualization Control
        # TODO: Visualization Label
        # Choice: Instant Path, 
        #       Animated Search (select animation speed). When this option is selected
        #       show another button with default of 1x Speed (which shows every iteration of the search)
        #       and provides dropdown choices of 2x, 4x, 8x, 16x 32x speed
        #           Draw path between start and current node when showing animation 
        #           Show closed (visited) set in special color 
        #           Show open set in special color

        #       Single Step (click button for each iteration) (good for debugging)

        # TODO: Button for "Rerun Previous Path"
        # TODO: Button for Run Tests
        #           Show test result stats
        # TODO: Random Tests (maze generation with random start/stop?)

        # TODO: Show Stats 
        # Headings: Search(algo), Start (location), Goal(location), Cost, Closed (number in closed set?)
        # Time, Node/sec?

        # Show instructions
        # Search Visualization Instructions 
        # How to set start and goal tiles 
        # Object can only move through same color tiles in the grid 
        # Choose Animate Search visualization to see real-time search progress 
        # Re-Run Previous - Performs previous search again (useful when animating)


        # Visualization Legend 
        # Blue/Green/Gray tiles: terrain type, object can move within a color 
        # Red Tile - Node is in closed list (has been expanded)
        # Orange Tile - Node is in open list (generated, but not expanded)
        # White Tile - Node is on the generated path

        # Do we need this?
        self.selected_algo = self.algorithms[0]

    def execute_map_action(self, action):
        """Helper to trigger the file dialog based on dropdown selection."""
        if action == "Small (8x8)":
            logging.info("Loading Small (8x8) map...")
            self.grid.load_from_file("maps/small_8x8.json")
        
        elif action == "L-Wall":
            logging.info("Loading L-Wall map...")
            self.grid.load_from_file("maps/L-Wall.json")

        if action == "Save Map":
            self.current_action = "SAVE"
            self.active_file_dialog = UIFileDialog(
                rect=pygame.Rect(160, 50, 440, 500),
                manager=self.manager,
                window_title="Save Map As...",
                initial_file_path="maps/",
                allow_existing_files_only=False  # Crucial for 'Save As' behavior
            )
        elif action == "Load Map":
            self.current_action = "LOAD"
            self.active_file_dialog = UIFileDialog(
                rect=pygame.Rect(160, 50, 440, 500),
                manager=self.manager,
                window_title="Load Map...",
                initial_file_path="maps/",
                allow_existing_files_only=True   # Only pick files that exist
            )
        elif action == "Create New":
            self.grid.clear()
            # Reset selection(optional)
            self.map_dropdown.selected_option = "Select Action..."
            print("Logic for clearing grid...")
        
        else:
            logging.error(f"unknown action: {action}")

        # Reset dropdown to default text so user can click the same map again
        self.map_dropdown.selected_option = "Select Action..."


    def handle_events(self, event):
        # Dropdown Menu Events
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.map_dropdown:
                if event.text == MAP_ACTION_DICT[MAP_ACTION_TYPES.LOAD]:
                    self.open_file_dialog(MAP_ACTION_TYPES.LOAD)
                elif event.text == MAP_ACTION_DICT[MAP_ACTION_TYPES.SAVE]:
                    self.open_file_dialog(MAP_ACTION_TYPES.SAVE)
                elif event.text == MAP_ACTION_DICT[MAP_ACTION_TYPES.CREATE]:
                    self.grid.clear_grid()
                    self.reset_selection_modes()
                    logging.info("Grid cleared, start/end unchecked")

            elif event.ui_element == self.terrain_dropdown:
                # Dynamically map the Name back to the Enum Type ID
                reverse_lookup = {name: type_id for type_id, name in TERRAIN_NAMES.items()}
                new_brush = reverse_lookup.get(event.text)
                
                if new_brush is not None:
                    self.grid.current_brush = new_brush 
                    logging.info(f"Brush changed to: {event.text}")

            elif event.ui_element == self.algo_dropdown:
                self.selected_algo = event.text 
                logging.info(f"Selected algorithm: {self.selected_algo}")

        # 2. Handle File Selection
        if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if event.ui_element == self.active_file_dialog:
                if self.current_action == MAP_ACTION_TYPES.SAVE:
                    self.grid.save_to_file(event.text)
                    logging.info(f"Map saved to: {event.text}")
                elif self.current_action == MAP_ACTION_TYPES.LOAD:
                    self.grid.load_from_file(event.text)
                    logging.info(f"Map loaded from: {event.text}")

        # 3. Clean up dialog reference when closed
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.active_file_dialog:
                self.active_file_dialog = None
                self.current_action = None

        # 4. Handle Checkbox Mutual Exclusivity
        if event.type == pygame_gui.UI_CHECK_BOX_CHECKED:
            if event.ui_element == self.start_checkbox:
                self.end_checkbox.is_checked = False
                self.end_checkbox._update_visual_state()
                logging.info("Start placement mode active")
            elif event.ui_element == self.end_checkbox:
                self.start_checkbox.is_checked = False
                self.start_checkbox._update_visual_state()
                logging.info("End placement mode active")


        if event.type == pygame_gui.UI_CHECK_BOX_UNCHECKED: 
            # if user clicks already-checked box, turn it back on 
            # so one mode is always selected if they click it 
            if event.ui_element == self.start_checkbox or event.ui_element == self.end_checkbox:
                event.ui_element.is_checked = True 

        # Handle Button Press 
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.clear_button:
                self.grid.clear()
                self.reset_selection_modes()
            elif event.ui_element == self.search_button:
                self.run_search() 


    def open_file_dialog(self, action_type):
        if self.active_file_dialog is None:
            title = MAP_ACTION_DICT[action_type]

            self.active_file_dialog = UIFileDialog(
                rect=pygame.Rect(160, 50, 440, 500),
                manager=self.manager,
                window_title=title,
                initial_file_path="maps/"
            )

            self.current_action = action_type

   
    def reset_search_data(self):
        """Clears search visuals (visited, path, parents) but keeps terrain."""
        for row in self.map:
            for node in row:
                node.visited = False 
                node.path = False 
                node.parent = None

                # Reset A* value if using them 
                node.g = float('inf')
                node.f = 0
                node.h = 0 

    
    def reset_selection_modes(self):
        """Unchecks both start and end boxes."""
        self.start_checkbox.is_checked = False 
        self.start_checkbox._update_visual_state()
        self.end_checkbox.is_checked = False 
        self.end_checkbox._update_visual_state()
    
    
    def run_search(self):

        # 1. Validation:Ensure start and end are set 
        if not self.grid.start_node or not self.grid.end_node:
            logging.warning("Select both a Start and End node first!")
            return 
        
        # 2. Validation: ensure start and end are on the same terrain type 
        start_terrain = self.grid.start_node.terrain 
        end_terrain = self.grid.end_node.terrain 

        if start_terrain != end_terrain:
            logging.error(
                f"Terrain mismatch! Start is {TERRAIN_NAMES[start_terrain]}, "
                f"End is {TERRAIN_NAMES[end_terrain]}. They must match."
            )
            return 
        
        # 3. Success: Reset old search data and start the generator 
        self.grid.reset_search_data()

        # 4. Execution 
        if self.selected_algo == "BFS":
            logging.info(f"Starting BFS on {TERRAIN_NAMES[start_terrain]} terrain...")
            # Assign the generator to the app's tracker
            # Note: You may need to pass the app instance to Sidebar or 
            # use a callback to set self.active_generator in PathFinderApp
            self.app.active_generator = bfs(self.grid)
        elif self.selected_algo == "DFS":
            logging.info(f"Starting DFS on {TERRAIN_NAMES[start_terrain]} terrain...")
            self.app.active_generator = dfs(self.grid)
        else:
            logging.error(f"Algorithm {self.selected_algo} not implemented")
            return 
            