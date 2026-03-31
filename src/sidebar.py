import pygame 
import pygame_gui 
from pygame_gui.elements import UIDropDownMenu, UILabel, UIButton
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

        # Map Controls
        self.label = UILabel(
            relative_rect=pygame.Rect((x_offset + padding, 10), (menu_width, 30)),
            text="Map Controls",
            manager=self.manager 
        )

        # Add the map dropdown 
        self.map_dropdown = UIDropDownMenu(
            options_list=["Select Action...", "Create New", "Load Map", "Save Map"],
            starting_option="Select Action...",
            relative_rect=pygame.Rect((x_offset+padding, 50),(menu_width, 40 )),
            manager=self.manager
        )

        # Add Clear button 
        # Positioned at y = 100 to leave a small gap below the dropdown 
        self.clear_button = UIButton(
            relative_rect=pygame.Rect((x_offset + padding, 100), (menu_width, 40)),
            text="Clear Grid",
            manager=self.manager
        )

        # Terrain Controls 
        self.terrain_dropdown = UIDropDownMenu(
            options_list=["Green", "Blue", "Gray", "Wall", "Start", "End"],
            starting_option="Green",
            relative_rect=pygame.Rect((x_offset + 10, 200), (width - 20, 40)),
            manager=self.manager
        )


    def handle_events(self, event):
        # drop down menu event
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.map_dropdown:
                action = event.text 
                self.execute_map_action(action) 

            elif event.ui_element == self.terrain_dropdown:
                # update the brush on the grid 
                mapping = {
                    "Green": self.grid.GREEN,
                    "Blue" : self.grid.BLUE,
                    "Gray" : self.grid.GRAY,
                    "Wall" : self.grid.WALL,
                    "Start": self.grid.START,
                    "End"  : self.grid.END
                }

                new_brush = mapping.get(event.text)
                if new_brush is not None:
                    self.grid.current_brush = new_brush 
                    logging.info(f"Brush changed to : {event.text}")

        # Capture the file path when the user picks one 
        if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if event.ui_element == self.save.dialog:
                self.grid.save_to_file(event.text)

        # Hanlde Button Press 
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.clear_button:
                self.grid.clear()
    
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