import pygame 
import pygame_gui 
from pygame_gui.elements import UIDropDownMenu, UILabel 

import logging 

logger = logging.getLogger(__name__)

class Sidebar:
    def __init__(self, manager, width, height, x_offset, grid_ref):
        self.manager = manager 
        self.grid = grid_ref 

        # UI Layout Constants 
        padding = 10 
        menu_width = width - (padding * 2)

        # Add a label 
        self.label = UILabel(
            relative_rect=pygame.Rect((x_offset + padding, 10), (menu_width, 30)),
            text="Map Controls",
            manager=self.manager 
        )

        # Add the dropdown 
        self.map_dropdown = UIDropDownMenu(
            options_list=["Select Action...", "Create New", "Load Map", "Save Map"],
            starting_option="Select Action...",
            relative_rect=pygame.Rect((x_offset+padding, 50),(menu_width, 40 )),
            manager=self.manager
        )

    def handle_events(self, event):
        """Processes sidebar-specific UI events."""
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.map_dropdown:
                action = event.text 
                self.execute_map_action(action)
                
    
    def execute_map_action(self, action):
        if action == "Create New":
            self.grid.clear()
            # Reset selection(optional)
            self.map_dropdown.selected_option = "Select Action..."
            print("Logic for clearing grid...")
        elif action == "Load Map":
            print("Logic for opening file browser...")
        elif action == "Save Map":
            print("Logic for saving current grid...")
        else:
            logging.error(f"unknown action: {action}")