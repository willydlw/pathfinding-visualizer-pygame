import pygame 
import pygame_gui 
from pygame_gui.elements import UIDropDownMenu, UILabel, UIButton
from pygame_gui.windows import UIFileDialog 

import tkinter as tk 
from tkinter import filedialog 

import logging 

from .constants import TERRAIN_TYPES

logger = logging.getLogger(__name__)

class Sidebar:
    def __init__(self, manager, width, height, x_offset, grid, app):
        self.manager = manager 
        self.grid = grid
        self.app = app
        self.save_dialog = None 

        # UI Layout Constants 
        padding = 10 
        label_width = 140 
        dropdown_width = 140
        menu_width = width - label_width - (padding * 2)


        theme = manager.get_theme()

        # get font info for a standard label 
        label_font_info = theme.get_font_info(combined_element_ids=['label'])
        print(f"Default Label Font: {label_font_info['name']}")
        print(f"Default Label Size: {label_font_info['size']}")

        label_x = x_offset + padding 

        # Map Controls
        self.label = UILabel(
            relative_rect=pygame.Rect((label_x, 10), (-1, 40)),
            text="Environment Map",
            manager=self.manager,
        )

        # Add the map dropdown 
        self.map_dropdown = UIDropDownMenu(
            options_list=["Select Action...", "Create New", "Load Map", "Save Map"],
            starting_option="Select Action...",
            relative_rect=pygame.Rect((label_x + padding + label_width, 10),(dropdown_width, 40 )),
            manager=self.manager
        )

        

        # Terrain Controls 
        self.terrain_dropdown = UIDropDownMenu(
            options_list=["Default", "Green", "Blue", "Gray", "Navy", "Start", "End"],
            starting_option="Green",
            relative_rect=pygame.Rect((x_offset + padding, 200), (width - 20, 40)),
            manager=self.manager
        )

        # Algorithm Controls 
        self.algorithms = ["BFS", "DFS", "A*"]
        self.algo_dropdown = UIDropDownMenu(
            options_list=self.algorithms,
            starting_option=self.algorithms[0],
            relative_rect=pygame.Rect((x_offset + padding, 250), (menu_width, 30)),
            manager=self.manager
        )

        self.selected_algo = self.algorithms[0]

        # Add Run Search button 
        # Positioned at y = 100 to leave a small gap below the dropdown 
        self.search_button = UIButton(
            relative_rect=pygame.Rect((x_offset + padding, 300), (menu_width, 40)),
            text="Run Search",
            manager=self.manager
        )

        # Add Clear button 
        # Positioned at y = 100 to leave a small gap below the dropdown 
        self.clear_button = UIButton(
            relative_rect=pygame.Rect((x_offset + padding, 100), (menu_width, 40)),
            text="Clear Grid",
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


    def handle_events(self, event):
        # drop down menu event
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.map_dropdown:
                action = event.text 
                self.execute_map_action(action) 

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

                logging.info(f"event.text: {event.text}")
                new_brush = mapping.get(event.text)
                if new_brush is not None:
                    self.grid.current_brush = new_brush 
                    logging.info(f"Brush changed to : {event.text}")

            elif event.ui_element == self.algo_dropdown:
                self.selected_algo = event.text 
                logging.info(f"Selected algorithm: {self.selected_algo}")

        # Capture the file path when the user picks one 
        if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if event.ui_element == self.save.dialog:
                self.grid.save_to_file(event.text)

        # Hanlde Button Press 
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

        if action == "Save Map":
            # Hide the main tkinter window that pops up 
            root = tk.Tk() 
            root.withdraw() 

            file_path = filedialog.asksaveasfilename(
                initialdir="./maps",
                title="Save Map as...",
                defaultextension=".json",
                filetypes=(("JSON files", "*.json"), ("all files", "*.*"))
            )

            if file_path:
                self.grid.save_to_file(file_path)
            root.destroy()  # clean up tkinter 

        elif action == "Load Map":
            root = tk.Tk() 
            root.withdraw() 

            file_path = filedialog.askopenfilename(
                initialdir="./maps",
                title="Select map file",
                filetypes=(("JSON files", "*.json"), ("all_files", "*.*"))
            )

            if file_path:
                self.grid.load_from_file(file_path)

            root.destroy() 
            self.map_dropdown.selected_option = "Select Action..."

        elif action == "Create New":
            self.grid.clear()
            # Reset selection(optional)
            self.map_dropdown.selected_option = "Select Action..."
            print("Logic for clearing grid...")
        
        else:
            logging.error(f"unknown action: {action}")