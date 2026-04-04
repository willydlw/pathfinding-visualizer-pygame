import pygame 
import pygame_gui 
from pygame_gui.elements import UIDropDownMenu, UILabel, UIButton
from pygame_gui.windows import UIFileDialog 


import logging 

from .constants import TERRAIN_TYPES, MAP_ACTION_TYPES, MAP_ACTION_DICT

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
            options_list=["Default", "Green", "Blue", "Gray", "Navy", "Start", "End"],
            starting_option="Green",
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
        #self.selected_algo = self.algorithms[0]


    def handle_events(self, event):
        # drop down menu event
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.map_dropdown:
                if event.text == MAP_ACTION_DICT[MAP_ACTION_TYPES.LOAD]:
                    self.open_file_dialog(MAP_ACTION_TYPES.LOAD)
                elif event.text == MAP_ACTION_DICT[MAP_ACTION_TYPES.SAVE]:
                    self.open_file_dialog(MAP_ACTION_TYPES.SAVE)
                elif event.text == MAP_ACTION_DICT[MAP_ACTION_TYPES.CREATE]:
                    self.grid.clear_grid()
                    logging.info("New map created (grid cleared)")

            elif event.ui_element == self.terrain_dropdown:
                # update the brush on the grid 
                mapping = {
                    "Default": TERRAIN_TYPES.DEFAULT,
                    "Green": TERRAIN_TYPES.GREEN,
                    "Blue" : TERRAIN_TYPES.BLUE,
                    "Gray" : TERRAIN_TYPES.GRAY,
                    "Navy" : TERRAIN_TYPES.NAVY,
                    "Start": TERRAIN_TYPES.START,
                    "End"  : TERRAIN_TYPES.END
                }

                new_brush = mapping.get(event.text)
                if new_brush is not None:
                    self.grid.current_brush = new_brush 
                    logging.info(f"Brush changed to : {event.text}")

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

        # Handle Button Press 
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.clear_button:
                self.grid.clear()
            elif event.ui_element == self.search_button:
                self.run_search() 
    
    def run_search(self):
        # resets search flags
        self.grid.reset_search_data()

        # ensure start and end are set before running 
        if not self.grid.start_node or not self.grid.end_node:
            logging.warning("Cannot run search without start and end positions.")
            return 
        
        if self.selected_algo == "BFS":
            from src.algorithms import bfs 
            # Assign the generator to the app's tracker
            # Note: You may need to pass the app instance to Sidebar or 
            # use a callback to set self.active_generator in PathFinderApp
            self.app.active_generator = bfs(self.grid)
        else:
            logging.error(f"Algorithm {self.selected_algo} not implemented")
            return 

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
