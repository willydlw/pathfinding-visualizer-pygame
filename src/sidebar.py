import pygame 
import pygame_gui 
from pygame_gui.elements import UIDropDownMenu, UILabel, UIButton, UICheckBox
from pygame_gui.windows import UIFileDialog 


import logging 

from .constants import (
    Algorithm_Type,
    Animation_Mode,
    Map_Actions,
    Terrain_Type, 
    Speed_Options
)

from .algorithms import bfs, dfs, astar

logger = logging.getLogger(__name__)

class Sidebar:
    def __init__(self, manager, width, height, x_offset):
        self.manager = manager 
        
        # Track the active dialog to distinguish between Load and Save actions
        self.active_file_dialog = None 
        self.current_action = None 
        self.selected_algo = Algorithm_Type.BFS

        # UI Layout Constants 
        padding = 10 
        label_width = 110
        checkbox_size = 25
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
            options_list=[action.name for action in Map_Actions],
            starting_option=Map_Actions.CREATE_MAP.name,
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
            options_list=[terrain.name for terrain in Terrain_Type],
            starting_option=Terrain_Type.GRASS.name,
            relative_rect=pygame.Rect((col2_x, 70), (right_col_width, widget_height)),
            manager=self.manager
        )

        # --- Row 3: Algorithm --- 
        self.algo_label = UILabel(
            relative_rect=pygame.Rect((col1_x, 120), (label_width, widget_height)),
            text="Algorithm:",
            manager=self.manager
        )

       
        self.algo_dropdown = UIDropDownMenu(
            options_list=[algo.name for algo in Algorithm_Type],
            starting_option=Algorithm_Type.BFS.name,
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
            relative_rect=pygame.Rect((col1_x, 285), (checkbox_size, checkbox_size)),
            text="",
            manager=self.manager
        )

        self.start_lablel = UILabel(
            relative_rect=pygame.Rect((col1_x + checkbox_size + 5, 280), (80, widget_height)),
            text="Set Start",
            manager=self.manager
        )

        self.end_checkbox = UICheckBox(
            relative_rect=pygame.Rect((col2_x, 285), (checkbox_size, checkbox_size)),
            text="",
            manager=self.manager
        )

        self.end_lablel = UILabel(
            relative_rect=pygame.Rect((col2_x + checkbox_size + 5, 280), (80, widget_height)),
            text="Set End",
            manager=self.manager
        )

        # --- Row 6: Animation Mode ---
        self.anim_label = UILabel(
            relative_rect=pygame.Rect((col1_x, 380), (label_width, widget_height)),
            text="Animation: ",
            manager=self.manager
        )

        self.anim_dropdown = UIDropDownMenu(
            options_list=[anim.name for anim in Animation_Mode],
            starting_option=Animation_Mode.ANIMATED.name,  
            relative_rect=pygame.Rect((col2_x, 380), (right_col_width, widget_height)),
            manager=self.manager
        )

        # --- Row 7: Speed Multiplier (Hidden unless "Animated" is selected) ---
        self.speed_options = Speed_Options.list_labels()
        self.speed_dropdown = UIDropDownMenu(
            options_list=self.speed_options,
            starting_option=self.speed_options[0], # default to 1x
            relative_rect=pygame.Rect((col2_x, 430), (right_col_width, widget_height)),
            manager=self.manager
        )

        # --- Row 8: Next Step Button (hidden by default) --- 
        self.next_step_button = UIButton(
            relative_rect=pygame.Rect((col1_x, 480), (full_widget_width, widget_height)),
            text="NEXT STEP",
            manager=self.manager,
            visible=0 # start hidden
        )


    def handle_events(self, event):
        
        if event.type == pygame_gui.UI_CHECK_BOX_CHECKED:
            self._handle_checkbox_toggle(event)
        
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            self._handle_dropdown_menu_events(event)

        elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            self._handle_file_dialog_path_picked_events(event)

        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            self._handle_window_close_events(event)


    def _handle_checkbox_toggle(self, event):
        """Handles mutual exclusivity in Pygame Gui 0.6.14"""
        if event.ui_element == self.start_checkbox:
            if self.start_checkbox.is_checked:
                # Force uncheck the other 
                self.end_checkbox.is_checked = False 
                self.end_checkbox.rebuild()

        elif event.ui_element == self.end_checkbox:
            if self.end_checkbox.is_checked:
                # force uncheck the other 
                self.start_checkbox.is_checked = False 
                self.start_checkbox.rebuild()


    def _handle_dropdown_menu_events(self, event):
        if event.ui_element == self.anim_dropdown:
            # Next Step button visibility
            if event.text == ANIMATION_MODE_NAMES[ANIMATION_MODE.SINGLE_STEP]:
                self.next_step_button.show() 
                self.speed_dropdown.hide() # hide speed as it's irrelevant 
            else:
                self.next_step_button.hide() 
                self.speed_dropdown.show()

        elif event.ui_element == self.algo_dropdown:
                self.selected_algo = event.text 
                logging.info(f"Selected algorithm: {self.selected_algo}")
        
        elif event.ui_element == self.map_dropdown:
            self._handle_map_action(event.text)
            

    def _handle_file_dialog_path_picked_events(self, event):
        """ Just close the dialog; let the App handle the grid logic."""
        if event.ui_element == self.active_file_dialog:
            if self.current_action == MAP_ACTION_TYPES.SAVE:
               self.active_file_dialog = None 

    def _handle_window_close_events(self, event):
        # Clean up dialog reference when closed
        if event.ui_element == self.active_file_dialog:
            self.active_file_dialog = None
            self.current_action = None
           

    def _handle_map_action(self, text):
        """Trigger dialogs, but leave grid clearing to the App."""
        if text == MAP_ACTION_DICT[MAP_ACTION_TYPES.LOAD]:
                self.open_file_dialog(MAP_ACTION_TYPES.LOAD)
        elif text == MAP_ACTION_DICT[MAP_ACTION_TYPES.SAVE]:
            self.open_file_dialog(MAP_ACTION_TYPES.SAVE)
        
        
    def open_file_dialog(self, action_type):
        """Sidebar owns the dialog object, but the App uses the result"""
        if self.active_file_dialog is None:
            title = MAP_ACTION_DICT[action_type]

            self.active_file_dialog = UIFileDialog(
                rect=pygame.Rect(160, 50, 440, 500),
                manager=self.manager,
                window_title=title,
                initial_file_path="maps/"
            )

            self.current_action = action_type

    
    def uncheck_start_end(self):
        """Unchecks both start and end boxes."""
        self.start_checkbox.is_checked = False 
        self.start_checkbox.rebuild()
        self.end_checkbox.is_checked = False 
        self.end_checkbox.rebuild()
            