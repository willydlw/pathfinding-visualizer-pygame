import pygame 
import pygame_gui 
import logging 
import random
import os 
import json
import time


import pygame_gui.ui_manager
from pygame_gui.windows import (
    UIConfirmationDialog,
    UIFileDialog,
    UIMessageWindow
)


from pygame_gui.elements import (
    UIDropDownMenu, 
    UILabel, 
    UIButton, 
    UICheckBox, 
    UISelectionList,
    UITextBox ,
    UITextEntryLine,
    UIPanel
)

from .appConfig import AppConfig

from .constants import (
    Algorithm_Type,
    Animation_Mode,
    Map_Actions,
    Map_Dimension,
    Neighbor_Connectivity,
    Neighbor_Direction,
    Speed_Options,
    Terrain_Type, 
    Speed_Options
)


from .algorithms import (
    bfs, dfs, astar
)


logger = logging.getLogger(__name__)

class UI_Layout:

    def __init__(self, width, padding, widget_height, label_width, x_offset, start_row):

        self.width = width 
        self.padding = padding 
        self.widget_height = widget_height 
        self.label_width = label_width 
        self.start_x = x_offset
        self.start_row = start_row
        self.draw_row = start_row


        # Interactive Widgets 
        self.full_width = width - (padding * 2)
        self.half_width = (width - padding * 3) // 2

        # Standard x positions
        self.col1x = padding
        self.col2x = padding + label_width + padding 
        self.col2_width = width - self.col2x - padding 

        
    def reset_flow(self):
        """Resets the vertical cursor to the initial starting position."""
        self.draw_row = self.start_row
    


class Sidebar:
    # Declare instance attributes here for the IDE/Type Checker 
    manager:    pygame_gui.UIManager 
    config:     AppConfig 
    ui_layout:  UI_Layout
    btn_map_tab:    UIButton   # Hinting the attributes defined in _init_tabs 
    btn_algo_tab:   UIButton  
    btn_viz_tab: UIButton
    panel_map_config:  UIPanel 
    panel_algo_settings: UIPanel 
    panel_viz_settings:  UIPanel


    def __init__(self, manager, config: AppConfig):
        self.manager = manager
        self.config = config

        # UI Layout
        self.ui_layout = UI_Layout(
            width=config.SIDEBAR_WIDTH,
            padding = 10,
            widget_height=self.config.WIDGET_HEIGHT,
            label_width=110,
            x_offset = self.config.GRID_WIDTH + (self.config.GRID_PADDING * 2),
            start_row=config.UI_START_ROW
        )


        # Initialize these class attributes before the gui elements 
        self.active_file_dialog = None 
        
        # 1. Create Tab Buttons at the top of the Sidebar
        self.btn_map_tab  = None 
        self.btn_algo_tab = None 
        self.btn_viz_tab  = None
        self._init_tabs()

        # 2. Create the Panels (Containers)
        self.panel_map_config  = None
        self.panel_algo_settings = None
        self.panel_viz_settings  = None 
        self._init_panels()
         

        # 3. Initialize map panel ui elements
        self.label_map_action = None
        self.select_map_action = None 
        self.label_terrain_type = None 
        self.select_terrain = None 
        self.label_grid_dimensions = None 
        self.select_grid_dimensions = None 
        self.check_start = None
        self.check_end = None 
        self.btn_reset_grid = None 
        self._init_panel_map_config() 
       

        # 5. Initialze algorithm panel ui elements 
        self.label_algo = None 
        self.select_algo = None 

        self.label_neighbor_connectivity = None 
        self.select_neighbor_connectivity = None

        self.label_avail_dirs = None 
        self.list_avail_dirs = None 
        self.list_selected_order = None 

        self.btn_default_order = None 
        self.btn_random_order = None 

        self.btn_clear_order = None 

        self.select_preset = None 
        self.label_save_preset = None 
        self.input_preset_name = None 

        self.default_preset_name = "Type name & press Enter"

        self._init_panel_algo_settings()

        # 6. Initialize viz panel with ui elements
        self.btn_run_search = None 
       
        self._init_panel_viz_settings() 
       
        # Set Initial Active Panel State 
        self.active_panel = self.panel_algo_settings
        self.panel_map_config.hide()
        #self.panel_algo_settings.hide()
        self.panel_viz_settings.hide()

        self._init_event_maps()

        # Dictionary to map tabs to panels
        self.tab_map = {
            "map" : self.panel_map_config,
            "algo": self.panel_algo_settings,
            "viz" : self.panel_viz_settings
        }


    def _init_tabs(self):
        """Create the Tab Buttons."""
        tab_w = self.config.SIDEBAR_WIDTH // 3 
        tab_h = 40 

        self.btn_map_tab = UIButton(
            relative_rect=pygame.Rect((self.ui_layout.start_x,20), (tab_w, tab_h)),
            text="Map",
            manager=self.manager 
        )

        self.btn_algo_tab = UIButton(
            relative_rect=pygame.Rect((self.ui_layout.start_x + tab_w,20), (tab_w, tab_h)),
            text="Algorithm",
            manager=self.manager 
        )

        self.btn_viz_tab = UIButton(
            relative_rect=pygame.Rect((self.ui_layout.start_x + tab_w * 2,20), (tab_w, tab_h)),
            text="Visualize",
            manager=self.manager 
        )

    def _init_panels(self):
        """Create a panel for each Tab."""
        panel_y_start = 70 
        bottom_margin = 20 
        dynamic_height = self.config.GRID_WIDTH + (self.config.GRID_PADDING * 2) - panel_y_start - bottom_margin
        panel_rect = pygame.Rect(
            (self.ui_layout.start_x, panel_y_start), 
            (self.config.SIDEBAR_WIDTH, dynamic_height))

        self.panel_map_config = UIPanel(relative_rect=panel_rect, manager=self.manager, starting_height=1)
        self.panel_algo_settings = UIPanel(relative_rect=panel_rect, manager=self.manager, starting_height=1)
        self.panel_viz_settings = UIPanel(relative_rect=panel_rect, manager=self.manager, starting_height=1)

    def _init_panel_map_config(self):
        """
        Create UI elements for 
            1. Map actions: create map, load map, save map
            2. Terrain type, 
            3. Setting grid dimensions
            4. Setting start, end locations 
        """
        self.ui_layout.reset_flow()

        # 1. Map Actions 
        self.label_map_action = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.label_width, self.ui_layout.widget_height)),
            text="Map Actions:",
            manager=self.manager,
            container=self.panel_map_config 
        )

        self.select_map_action = UIDropDownMenu(
            options_list=Map_Actions.options_list(),
            starting_option=Map_Actions.get_default().label,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row),
                (self.ui_layout.col2_width, self.ui_layout.widget_height)),
            manager=self.manager,
            container=self.panel_map_config,
            object_id="#select_map_action"
        )
        
        self.ui_layout.draw_row += self.config.ROW_SPACING 

        # 2. Terrain        
        self.label_terrain_type = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.label_width, self.ui_layout.widget_height)),
            text="Terrain Type:",
            manager=self.manager,
            container=self.panel_map_config 
        )

        self.select_terrain = UIDropDownMenu(
            options_list=Terrain_Type.options_list(),
            starting_option=Terrain_Type.get_default().label,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row), 
                (self.ui_layout.col2_width, self.ui_layout.widget_height)),
            manager=self.manager,
            container=self.panel_map_config,
            object_id="#select_terrain"
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING 
    
        # Grid Settings
        self.label_grid_dimensions = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row),
                (self.ui_layout.label_width, self.ui_layout.widget_height)
            ),
            text="Set Grid Size:",
            manager=self.manager,
            container=self.panel_map_config 
        )

        self.select_grid_dimensions = UIDropDownMenu(
            options_list=Map_Dimension.options_list(),
            starting_option=Map_Dimension.get_default().label,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row),
                (self.ui_layout.col2_width, self.ui_layout.widget_height)
            ),
            manager=self.manager,
            container=self.panel_map_config,
            object_id="#select_grid_dimensions"
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING 

        # Start/End Markers     
        self.check_start = UICheckBox(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.config.CHECKBOX_SIZE, self.config.CHECKBOX_SIZE)),
            text="Set Start",
            manager=self.manager,
            container=self.panel_map_config,
            object_id="#check_start"
        )

        self.check_end = UICheckBox(
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row), 
                (self.config.CHECKBOX_SIZE, self.config.CHECKBOX_SIZE)),
            text="Set End",
            manager=self.manager,
            container=self.panel_map_config,
            object_id="#check_end"
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING 

        self.btn_reset_grid = UIButton(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_width, self.ui_layout.widget_height)
            ),
            text="CLEAR GRID",
            manager=self.manager,
            container=self.panel_map_config,
            object_id="#btn_reset_grid",
            tool_tip_text="Click here to reset the entire drawing area."
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING  

    def _init_panel_algo_settings(self):
        self.ui_layout.reset_flow()

        # 1. Algorithm Selection 
        self.label_algo = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.label_width, self.ui_layout.widget_height)),
            text="Algorithm:",
            manager=self.manager,
            container=self.panel_algo_settings 
        )

        self.select_algo = UIDropDownMenu(
            options_list=Algorithm_Type.options_list(),
            starting_option=Algorithm_Type.get_default().label,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row), 
                (self.ui_layout.col2_width, self.ui_layout.widget_height)),
            manager=self.manager,
            container=self.panel_algo_settings,
            object_id="#select_algo"
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING

        # Neighbor Connectivity
        self.label_neighbor_connectivity = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.label_width, self.ui_layout.widget_height)),
            text="Connectivity",
            manager=self.manager,
            container=self.panel_algo_settings 
        )

        self.select_neighbor_connectivity = UIDropDownMenu(
            options_list=Neighbor_Connectivity.options_list(),
            starting_option=Neighbor_Connectivity.get_default().label,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row), 
                (self.ui_layout.col2_width, self.ui_layout.widget_height)),
            manager=self.manager,
            container=self.panel_algo_settings,
            object_id="#select_neighbor_connectivity"
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING

        # --- Neighbor Direction Order ---
        #      UI Selections to control order in which search algorithms select neighbors
                 
        # Available neighbor directions label
        self.label_avail_dirs = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_width, self.ui_layout.widget_height)
            ),
            text="Neighbor Directions (click to select)",
            manager=self.manager,
            container=self.panel_algo_settings
        )
        self.ui_layout.draw_row += self.ui_layout.widget_height 

        # Available neighbor directions list
        self.list_avail_dirs = UISelectionList(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_width, self.config.LIST_HEIGHT)),
            item_list=Neighbor_Direction.get_labels(include_diagonals=False),
            manager=self.manager,
            container=self.panel_algo_settings,
            object_id="#available_direction_selector"
        )
        self.ui_layout.draw_row += self.config.LIST_HEIGHT + 10


        # Selected directions label
        self.label_selected_dirs = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_width, self.ui_layout.widget_height)
            ),
            text="Selected Order",
            manager=self.manager,
            container=self.panel_algo_settings
        )
        self.ui_layout.draw_row += self.ui_layout.widget_height 

        # Selected directions list
        self.list_selected_order = UISelectionList(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_width, self.config.LIST_HEIGHT)),
            item_list=[],
            manager=self.manager,
            container=self.panel_algo_settings,
            object_id="#list_selected_order"
        )
        self.ui_layout.draw_row += self.config.LIST_HEIGHT + 10

      
        # Random neighbor order checkbox
        self.check_random_neighbor_order = UICheckBox(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.config.CHECKBOX_SIZE, self.config.CHECKBOX_SIZE)),
            text="Random Order",
            manager=self.manager,
            container=self.panel_algo_settings,
            object_id="#check_start",
            tool_tip_text="Algorithm selects neighbors randomly"
        )


        # Default neighbor order button
        self.btn_default_order = UIButton(
            relative_rect=pygame.Rect((self.ui_layout.half_width + 20, self.ui_layout.draw_row), 
                                    (self.ui_layout.half_width, self.ui_layout.widget_height)),
            text="Default Order",
            manager=self.manager, container=self.panel_algo_settings
        )
        self.ui_layout.draw_row += self.config.ROW_SPACING
       

        # Clear neighbor order button
        self.btn_clear_order = UIButton(
             relative_rect=pygame.Rect((self.ui_layout.col1x, self.ui_layout.draw_row), 
                                    (self.ui_layout.half_width, self.ui_layout.widget_height)),
            text="Clear Search Order",
            manager=self.manager,
            container=self.panel_algo_settings, 
            object_id="#clear_order_btn",
            tool_tip_text="Resets Search Order"
        )
        
        # Select presets dropdown
        self.select_preset = UIDropDownMenu(
            options_list=["Select Preset"], # We will populate this dynamically
            starting_option="Select Preset",
            relative_rect=pygame.Rect((self.ui_layout.half_width + 20, self.ui_layout.draw_row), 
                                    (self.ui_layout.half_width, self.ui_layout.widget_height)),
            manager=self.manager, container=self.panel_algo_settings
        )
        self.ui_layout.draw_row += self.config.ROW_SPACING


        # Save preset label
        self.label_save_preset = UILabel(
            relative_rect=pygame.Rect((self.ui_layout.col1x, self.ui_layout.draw_row), 
                                    (self.ui_layout.label_width, self.ui_layout.widget_height)),
            text="Save Preset: ",
            manager=self.manager, 
            container=self.panel_algo_settings,
        )
        
        # Input preset name
        self.input_preset_name = UITextEntryLine(
            relative_rect=pygame.Rect((self.ui_layout.label_width + 20, self.ui_layout.draw_row), 
                                    (self.ui_layout.half_width + 30, self.ui_layout.widget_height)),
            manager=self.manager,
            container=self.panel_algo_settings,
            placeholder_text=self.default_preset_name, # Shows when empty
        )


        # Group widgets that are disabled when 'Random' is checked
        self.manual_order_widgets = [
            self.list_avail_dirs, 
            self.list_selected_order,
            self.btn_default_order, 
            self.btn_clear_order, 
            self.select_preset, 
            self.input_preset_name
        ]

        self._refresh_preset_dropdown()
        
    def _init_panel_viz_settings(self):
        self.ui_layout.reset_flow()

        # Save preset
        self.btn_run_search = UIButton(
            relative_rect=pygame.Rect((self.ui_layout.col1x, self.ui_layout.draw_row), 
                                    (self.ui_layout.half_width, self.ui_layout.widget_height)),
            text="Run Search",
            manager=self.manager, container=self.panel_viz_settings
        )
        

    def _init_event_maps(self):
        
        # Button -> Function Map 
        self.button_actions = {
            self.btn_map_tab: lambda: self._switch_tab(self.panel_map_config),
            self.btn_algo_tab: lambda: self._switch_tab(self.panel_algo_settings),
            self.btn_viz_tab: lambda: self._switch_tab(self.panel_viz_settings),
            self.btn_clear_order: self._handle_clear_order,
            self.btn_default_order: self._handle_set_default_order,
            self.btn_reset_grid: self.uncheck_start_end()
        }

        # Dropdown -> Function Map 
        self.dropdown_actions = {
            self.select_map_action: self._handle_map_action,
            self.select_neighbor_connectivity: self._handle_connectivity_selection,
            self.select_preset: self._handle_load_preset,
        }

        # The following dropdowns do not need additional logic for updating the UI
        # The PathFinderApp class handles their dropdown events 
        # self.select_algo
        # self.select_grid_dimensions
        # self.select_terrain 

        # Checkbox -> Function (receives a bool)
        self.checkbox_actions = {
            self.check_random_neighbor_order: self._toggle_neighbor_order_ui,
            self.check_start: self._toggle_start_end_ui,
            self.check_end: self._toggle_start_end_ui
        }


    def handle_events(self, event):
        # Immediate exit for irrelevant events 
        if not hasattr(event, "ui_element"):
            return 
        
        # Handle buttons 
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            action = self.button_actions.get(event.ui_element)
            if action:
                action()
                return 

        # Handle Dropdowns    
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            action = self.dropdown_actions.get(event.ui_element)
            if action:
                action(event.text)
                return 
        
        # Handle Text Entry (Enter key)
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.input_preset_name:
                self._handle_save_preset() 
                return 
            
        elif event.type in (pygame_gui.UI_CHECK_BOX_CHECKED, pygame_gui.UI_CHECK_BOX_UNCHECKED):
            action = self.checkbox_actions.get(event.ui_element)
            if action:
                is_checked = (event.type == pygame_gui.UI_CHECK_BOX_CHECKED)
                action(event.ui_element, is_checked)
                return 
            
        elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            self._handle_list_logic(event)
        
        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.active_file_dialog:
                self.active_file_dialog = None 


    # --------- Button Event Handlers -----------

    def _switch_tab(self, target_panel):
        for panel in self.tab_map.values():
            panel.hide()
        
        target_panel.show() 
        self.active_panel = target_panel



    def _handle_save_preset(self):
        preset_name = self.input_preset_name.text.strip() 
        if not preset_name:
            # Show status message via pygame_gui popup 
            UIMessageWindow(
                rect=pygame.Rect((400, 300), (300, 200)),
                html_message="<b>Error:</b> Preset name is required.",
                manager=self.manager,
                window_title="Save Error"
            )
            logging.warning("Save failed. No preset name provided.")
            return 
          
        # Get connectivity and selected directions
        raw_connectivity = self.select_neighbor_connectivity.selected_option
        connectivity_text = raw_connectivity[0] if isinstance(raw_connectivity, tuple) else raw_connectivity
        connectivity_enum = Neighbor_Connectivity.from_label(connectivity_text)
        current_order = self._get_clean_item_list(self.list_selected_order)

        # Validation checks 
        error_msg = None 
        if not current_order:
            error_msg = "Order list is empty."
        elif len(current_order) != connectivity_enum.value:
            error_msg = f"Please select all {connectivity_enum.value} directions."
        
        if error_msg:
            UIMessageWindow(
                rect=pygame.Rect((400, 300), (300, 200)),
                html_message=f"<b>Cannot Save:</b> {error_msg}",
                manager=self.manager
            )
            logging.warning(error_msg)
            self.input_preset_name.set_text("")
            return 

        # Save the file
        os.makedirs('presets', exist_ok=True)
        preset_data = {
            "order": current_order,
            "connectivity": connectivity_text
        }

        try:
            with open(f"presets/{preset_name}.json", "w") as f:
                json.dump(preset_data, f)
            self.input_preset_name.set_text("") 
            logging.info(f"{preset_name} saved.")

        except Exception as e:
            logging.error(f"Failed to write file: {e}")


    def _refresh_preset_dropdown(self):
        """Scan the presets folder and update the dropdown options."""

        # ensure directory exists, get files and strip extension, prepend "Select Preset" to list
        os.makedirs('presets', exist_ok=True)
        files = [f.replace('.json', '') for f in os.listdir('presets') if f.endswith('.json')]
        options = ["Select Preset"] + files 

        # Capture the current state and current selection 
        is_random = self.check_random_neighbor_order.is_checked 
        current_selection = self.select_preset.selected_option 

        rect = self.select_preset.relative_rect 
        manager = self.select_preset.ui_manager 
        container = self.select_preset.ui_container 

        self.select_preset.kill() 

        # Recreate with the previous selection
        if current_selection not in options:
            current_selection = "Select Preset"

        self.select_preset = UIDropDownMenu(
            options_list=options,
            starting_option=current_selection,
            relative_rect=rect,
            manager=manager,
            container=container
        )

        # restore disabled state and update the tracking list
        if random:
            self.select_preset.disable() 
 

    def _handle_clear_order(self):
        # Get strings from both lists 
        current_order = self._get_clean_item_list(self.list_selected_order)
        current_pool = self._get_clean_item_list(self.list_avail_dirs)

        # Combine them back into the pool
        current_pool.extend(current_order)

        # Clear the active order list 
        self.list_selected_order.set_item_list([])

        sorted_pool = Neighbor_Direction.sort_labels(current_pool)
        self.list_avail_dirs.set_item_list(sorted_pool)


    def _handle_set_default_order(self):
        """Sets order to the standard natural order based on connectivity selection."""
        # 1. Safely extract string (handles tuple issue)
        raw_selection = self.select_neighbor_connectivity.selected_option 
        if isinstance(raw_selection, (list, tuple)):
            selected_text = raw_selection[0]
        else:
            selected_text = raw_selection 

        # 2. Convert to enum 
        connectivity = Neighbor_Connectivity.from_label(selected_text)

        # 3. Determine if we need diagonals
        include_diagonals = (connectivity == Neighbor_Connectivity.CONNECT8)

        # 4. Get the labels 
        direction_labels = Neighbor_Direction.get_labels(include_diagonals=include_diagonals)

        # 5. Set lists: available empty, order full
        self.list_selected_order.set_item_list(direction_labels)
        self.list_avail_dirs.set_item_list([])

    
    def uncheck_start_end(self):
        #Unchecks both start and end boxes.
        self.check_start.is_checked = False 
        self.check_start.rebuild()
        self.check_end.is_checked = False 
        self.check_end.rebuild()


    # --------- CheckBox Event Handlers ------------
    def _toggle_neighbor_order_ui(self, is_random: bool):
        """Enable or disable all UI elements related to manual neighbor order."""
               
         # Group widgets that are disabled when 'Random' is checked
        self.manual_order_widgets = [
            self.list_avail_dirs, 
            self.list_selected_order,
            self.btn_default_order, 
            self.btn_clear_order, 
            self.select_preset, 
            self.input_preset_name,
        ]

        for el in self.manual_order_widgets:
            el.disable() if is_random else el.enable()

        if is_random:
            self.list_avail_dirs.set_item_list([])
            content = ["", "", "Randomly Selected at Runtime"] if is_random else []
            self.list_selected_order.set_item_list(content)
        else:
            # Convert selected connectivity to enum 
            selected_connectivity = self.select_neighbor_connectivity.selected_option
            if isinstance(selected_connectivity, (tuple, list)) and len(selected_connectivity) > 0:
                 connectivity_label = selected_connectivity[0]
            else: 
                 connectivity_label = selected_connectivity

            connectivity_enum = Neighbor_Connectivity.from_label(connectivity_label)
      
            # Fill available list based on connectivity
            if connectivity_enum == Neighbor_Connectivity.CONNECT4:
                available_dirs = Neighbor_Direction.get_labels(False)
            else:
                available_dirs = Neighbor_Direction.get_natural_order()
               
            self.list_avail_dirs.set_item_list(available_dirs)
            self.list_selected_order.set_item_list([])



    def _toggle_start_end_ui(self, element, is_checked):
        if not is_checked: return 

        if element == self.check_start:
                self.check_end.is_checked = False
                self.check_end.rebuild() 
        elif element == self.check_end:
                self.check_start.is_checked = False 
                self.check_start.rebuild()


    # --------- DropDown Event Handlers 
    
    def _handle_map_action(self, text):
        if text == Map_Actions.LOAD_MAP.label:
            self.open_file_dialog(Map_Actions.LOAD_MAP)
        elif text == Map_Actions.SAVE_MAP.label:
            self.open_file_dialog(Map_Actions.SAVE_MAP)


    def open_file_dialog(self, action_type):
        #Sidebar owns the dialog object, but the App uses the result
        if self.active_file_dialog is None:
           
            if action_type == Map_Actions.SAVE_MAP:
                path = "maps/new_map.json"
            else:
                path = "maps/"

            self.active_file_dialog = UIFileDialog(
                rect=pygame.Rect(160, 50, 440, 500),
                manager=self.manager,
                window_title=action_type.window_title,
                initial_file_path=path,
                object_id="#map_file_dialog",
                allowed_suffixes={".json"},
                allow_existing_files_only=(action_type == Map_Actions.LOAD_MAP)
            )



    def _handle_connectivity_selection(self, text):
        
        if self.check_random_neighbor_order.is_checked:
            return 
        
        # convert string to enum
        connectivity = Neighbor_Connectivity.from_label(text)
        
        # 1. Get the current version of both lists 
        current_order = self._get_clean_item_list(self.list_selected_order)
        current_avail = self._get_clean_item_list(self.list_avail_dirs)

        # 2. Get the list of diagonal labels 
        diagonals = Neighbor_Direction.get_diagonal_labels() 

        if connectivity == Neighbor_Connectivity.CONNECT4:
                # Checkbox unchecked - remove diagonals from both lists 
                new_order = [item for item in current_order if item not in diagonals]
                new_avail = [item for item in current_avail if item not in diagonals]

                # update the UI 
                self.list_selected_order.set_item_list(new_order)
                self.list_avail_dirs.set_item_list(new_avail)
        else:
            # add diagonals to available 
            for d in diagonals:
                if d not in current_avail and d not in current_order:
                    current_avail.append(d)

            sorted_avail = Neighbor_Direction.sort_labels(current_avail)
            self.list_avail_dirs.set_item_list(sorted_avail)


    def _handle_load_preset(self, preset_name):
        # load the data
        try:
            with open(f"presets/{preset_name}.json", "r") as f:
                data = json.load(f)

            connectivity_label = data.get('connectivity')
            if not connectivity_label:
                UIMessageWindow(
                    rect=pygame.Rect((400, 300), (300, 200)),
                    html_message="<b>Error:</b> Connectivity is required.",
                    manager=self.manager,
                    window_title="Load Error"
                )
                logging.warning("Load failed. No connectivity provided.")
                return 
                
          
            # 1. Update Connectivity Dropdown based on the 'diagonals' flag
            self.select_neighbor_connectivity.selected_option = connectivity_label 
            self.select_neighbor_connectivity.rebuild() 

            # 2. Update the lists
            self.list_selected_order.set_item_list(data['order'])
            self.list_avail_dirs.set_item_list([])

            self._refresh_preset_dropdown()

        except FileNotFoundError:
            logging.warning(f"File {preset_name} not found.")


# ===============================================================

# Helper functions for PathFinderApp's event handling to access UI data


    def set_status(self, message):
        self.status_label.set_text(message)


 

    # --- List Logic ---
    def _handle_list_logic(self, event):
        
        # Define the relationships: clicking an item in 'src' moves it to 'dest'
        list_map = {
            self.list_avail_dirs: (self.list_selected_order, False), # To Selected (no sort)
            self.list_selected_order: (self.list_avail_dirs, True),  # To Availalbe (sort)
        }

        if event.ui_element in list_map:
            dest_list, should_sort = list_map[event.ui_element]
            self._transfer_item(event.text, src=event.ui_element, dest=dest_list, sort=should_sort)

    def _transfer_item(self, text, src, dest, sort=False):
        s_list = self._get_clean_item_list(src)
        d_list = self._get_clean_item_list(dest) 

        if text in s_list:
            s_list.remove(text)
            d_list.append(text)
            if sort: d_list = Neighbor_Direction.sort_labels(d_list)

        src.set_item_list(s_list)
        dest.set_item_list(d_list)



    def _get_clean_item_list(self, ui_list_element):
        """Extracts strings from a UISelectionList regardless of its internal format."""
        raw_list = ui_list_element.item_list 
        return [item['text'] if isinstance(item, dict) else item for item in raw_list]
    

    def get_selected_directions(self):
        return self._get_clean_item_list(self.list_selected_order)
    
    
    def get_selected_direction_vectors(self):
        """
        Converts the strings in list_selected_order into (dr, dc) vectors.
        Ensures all required directions are included, appending missing ones to the end.
        """
        # Get the user's custom order and current settings
        selected_labels = self._get_clean_item_list(self.list_selected_order)
        include_diagonals = (self.select_neighbor_connectivity == Neighbor_Connectivity.CONNECT8)

        # Define what complete looks like for the current mode 
        required_labels = Neighbor_Direction.get_labels(include_diagonals)

        # Create the final sequence: Start with user choices, then add missing 
        final_labels = list(selected_labels)
        for label in required_labels:
            if label not in final_labels:
                final_labels.append(label)

        # Map the labels back to vectors 
        # Get the lookup map : {"North": <Neighbor_Direction.NORTH>, ...}
        lookup = Neighbor_Direction.get_lookup()

        # Return a list of vectors [(dr, dc), ...]
        return [lookup[label].vector for label in final_labels if label in lookup]
    

    def _sync_neighbor_order(self):
        """Fills missing directions in the UI so the user sees the final search order."""
        # Get the current user oder and the required defaults 
        user_order = self._get_clean_item_list(self.list_selected_order)
        include_diagonals = self.check_allow_diagonals.is_checked 
        required_labels = Neighbor_Direction.get_labels(include_diagonals)

        # Add missing directions to the user order list 
        updated_order = list(user_order)
        for label in required_labels:
            if label not in updated_order:
                updated_order.append(label)

        # Update the UI lists 
        self.list_selected_order.set_item_list(updated_order)
        self.list_avail_dirs.set_item_list([])  # everything is now in the active list
