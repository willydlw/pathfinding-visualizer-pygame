import pygame 
import pygame_gui 
from pygame_gui.elements import UIDropDownMenu, UILabel
from pygame_gui.windows import UIFileDialog 

import tkinter as tk 
from tkinter import filedialog 

import logging 

logger = logging.getLogger(__name__)

class Sidebar:
    def __init__(self, manager, width, height, x_offset, grid_ref):
        self.manager = manager 
        self.grid = grid_ref 
        self.save_dialog = None 

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
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.map_dropdown:
                action = event.text 
                self.execute_map_action(action)

        # Capture the file path when the user picks one 
        if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if event.ui_element == self.save.dialog:
                self.grid.save_to_file(event.text)

                
    
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