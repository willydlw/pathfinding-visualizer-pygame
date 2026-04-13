import pygame 
import pygame_gui 
import logging 


import pygame_gui.ui_manager
from pygame_gui.windows import (
    UIConfirmationDialog,
    UIFileDialog 
)


from pygame_gui.elements import (
    UIDropDownMenu, 
    UILabel, 
    UIButton, 
    UICheckBox, 
    UISelectionList,
    UITextBox ,
    UIPanel
)

from .appConfig import AppConfig

from .constants import (
    Algorithm_Type,
    Animation_Mode,
    Map_Actions,
    Map_Dimension,
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
        self.full_widget_width = width - (padding * 2)

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
        self.current_action = None 
        self.selected_algo = Algorithm_Type.BFS
        self.neighbor_order_list = []

        
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
        self.check_place_start = None
        self.check_place_end = None
       
        self.ui_layout.reset_flow()
        self._init_panel_map_config() 
       

        # 5. Initialze algorithm panel ui elements 
        self.label_algo = None 
        self.select_algo = None 
        self.check_allow_diagonals = None 
        self.label_avail_dirs = None 
        self.list_avail_dirs = None 
        self.list_active_order = None 
        self.btn_clear_order = None 

        self.ui_layout.reset_flow()
        self._init_panel_algo_settings()

        # 6. Initialize viz panel with ui elements
        self.ui_layout.reset_flow()
        self._init_panel_viz_settings() 
       
        # Set Initial Active Panel State 
        self.active_panel = self.panel_algo_settings
        self.panel_map_config.hide()
        self.panel_viz_settings.hide()


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
            options_list=Map_Actions.list_labels(),
            starting_option=Map_Actions.EDIT_MAP.label,
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
            options_list=[terrain.name for terrain in Terrain_Type],
            starting_option=Terrain_Type.GRASS.name,
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
            options_list=Map_Dimension.get_ui_labels(),
            starting_option=Map_Dimension.MD8.label,
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
        self.check_place_start = UICheckBox(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.config.CHECKBOX_SIZE, self.config.CHECKBOX_SIZE)),
            text="Set Start",
            manager=self.manager,
            container=self.panel_map_config,
            object_id="#check_place_start"
        )

        self.check_place_end = UICheckBox(
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row), 
                (self.config.CHECKBOX_SIZE, self.config.CHECKBOX_SIZE)),
            text="Set End",
            manager=self.manager,
            container=self.panel_map_config,
            object_id="#check_place_end"
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING 

        self.btn_reset_grid = UIButton(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_widget_width, self.ui_layout.widget_height)
            ),
            text="CLEAR GRID",
            manager=self.manager,
            container=self.panel_map_config,
            object_id="#btn_reset_grid",
            tool_tip_text="Click here to reset the entire drawing area."
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING  


    def _init_panel_algo_settings(self):
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
            options_list=[algo.name for algo in Algorithm_Type],
            starting_option=Algorithm_Type.BFS.name,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row), 
                (self.ui_layout.col2_width, self.ui_layout.widget_height)),
            manager=self.manager,
            container=self.panel_algo_settings,
            object_id="#select_algo"
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING

        # 2. Neighbor Direction Priority 
                 
        # Diagonal Toggle Checkbox 
        self.check_allow_diagonals = UICheckBox(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.config.CHECKBOX_SIZE, self.ui_layout.widget_height)),
            text="Include Diagonal Neighbors",
            manager=self.manager,
            container=self.panel_algo_settings
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING

        # Neighbor Search Order Settings
        self.label_avail_dirs = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_widget_width, self.ui_layout.widget_height)
            ),
            text="Neighbor Search Order (Click to add):",
            manager=self.manager,
            container=self.panel_algo_settings
        )

        self.ui_layout.draw_row += self.ui_layout.widget_height 

        # Selection Lists
        list_height = 100 
        self.list_avail_dirs = UISelectionList(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_widget_width, list_height)),
            item_list=Neighbor_Direction.get_labels(include_diagonals=False),
            manager=self.manager,
            container=self.panel_algo_settings,
            object_id="#available_direction_selector"
        )

        self.ui_layout.draw_row += list_height + 10
        self.list_active_order = UISelectionList(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_widget_width, list_height)),
            item_list=[],
            manager=self.manager,
            container=self.panel_algo_settings,
            object_id="#list_active_order"
        )

        self.ui_layout.draw_row += list_height + 10

        self.btn_clear_order = UIButton(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_widget_width, self.ui_layout.widget_height)),
            text="Clear Search Order",
            manager=self.manager,
            container=self.panel_algo_settings, 
            object_id="#clear_order_btn",
            tool_tip_text="Resets Search Order"
        )



    def _init_panel_viz_settings(self):
        pass

    def handle_events(self, event):

        # Handles switching between map, panel, and viz tabs
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_map_tab:
                self._switch_tab(self.panel_map_config)
            elif event.ui_element == self.btn_algo_tab:
                self._switch_tab(self.panel_algo_settings)
            elif event.ui_element == self.btn_viz_tab:
                self._switch_tab(self.panel_viz_settings)
            elif event.ui_element == self.btn_clear_order:
                self._handle_clear_order()

        elif event.type == pygame_gui.UI_CHECK_BOX_CHECKED:
            self._handle_checkbox_checked(event)

        elif event.type == pygame_gui.UI_CHECK_BOX_UNCHECKED:
            self._handle_checkbox_unchecked(event)
        
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            logging.info(f"detected drop_down_menu_changed")
            self._handle_dropdown_menu_events(event)

        elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            logging.info(f"detected new selection")
            self._handle_new_selection(event)

        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            self._handle_window_close_events(event)

    
    def _get_clean_item_list(self, ui_list_element):
        """Extracts strings from a UISelectionList regardless of its internal format."""
        raw_list = ui_list_element.item_list 
        return [item['text'] if isinstance(item, dict) else item for item in raw_list]


    def _handle_clear_order(self):
        # Get strings from both lists 
        current_order = self._get_clean_item_list(self.list_active_order)
        current_pool = self._get_clean_item_list(self.list_avail_dirs)

        # Combine them back into the pool
        current_pool.extend(current_order)

        # Clear the active order list 
        self.list_active_order.set_item_list([])

        sorted_pool = Neighbor_Direction.sort_labels(current_pool)
        self.list_avail_dirs.set_item_list(sorted_pool)


    def _handle_new_selection(self, event):

        # --- Moving from Available to Order ---
        if event.ui_object_id.endswith("#available_direction_selector"):
           
            selected = event.text 
            logging.info(f"Selected direction: {selected}")

            # Remove from Available 
            # Extract strings from the dictionary list
            current_avail = self._get_clean_item_list(self.list_avail_dirs)
            logging.info(f"current_avail: {current_avail}")

            if selected in current_avail:
                current_avail.remove(selected) 
                self.list_avail_dirs.set_item_list(current_avail)

                # Add to Neighbor Order 
                current_order = self._get_clean_item_list(self.list_active_order)
                current_order.append(selected)
                self.list_active_order.set_item_list(current_order)


        # --- Moving from Neighbor Order back to Available ---
        if event.ui_object_id.endswith("#list_active_order"):
            selected = event.text 

            # Remove from Neighbor Order
            current_order = self._get_clean_item_list(self.list_active_order)

            if selected in current_order:
                current_order.remove(selected)
                self.list_active_order.set_item_list(current_order)

                # Add back to Available in sorted order
                current_avail = self._get_clean_item_list(self.list_avail_dirs)
                current_avail.append(selected)

                sorted_avail = Neighbor_Direction.sort_labels(current_avail)
                self.list_avail_dirs.set_item_list(sorted_avail)


    
    def _handle_checkbox_unchecked(self, event):
  
        if event.ui_element == self.check_allow_diagonals:
            self._handle_diagonal_checkbox(is_checked=False)
            

    def _handle_checkbox_checked(self, event):

        if event.ui_element == self.check_place_start:
            if self.check_place_start.is_checked:
                # Force uncheck the other 
                self.check_place_end.is_checked = False 
                self.check_place_end.rebuild()

        elif event.ui_element == self.check_place_end:
            if self.check_place_end.is_checked:
                # force uncheck the other 
                self.check_place_start.is_checked = False 
                self.check_place_start.rebuild() 

        elif event.ui_element == self.check_allow_diagonals:
           self._handle_diagonal_checkbox(is_checked=True)

    
    def _handle_diagonal_checkbox(self, is_checked):
        # 1. Get the current version of both lists 
        current_order = self._get_clean_item_list(self.list_active_order)
        current_avail = self._get_clean_item_list(self.list_avail_dirs)

        # 2. Get the list of diagonal labels 
        diagonals = Neighbor_Direction.get_diagonal_labels() 

        if not is_checked:
                # Checkbox unchecked - remove diagonals from both lists 
                new_order = [item for item in current_order if item not in diagonals]
                new_avail = [item for item in current_avail if item not in diagonals]

                # update the UI 
                self.list_active_order.set_item_list(new_order)
                self.list_avail_dirs.set_item_list(new_avail)
        else:
            # check box checked - add diagonals back to available 
            for d in diagonals:
                if d not in current_avail and d not in current_order:
                    current_avail.append(d)

            sorted_avail = Neighbor_Direction.sort_labels(current_avail)
            self.list_avail_dirs.set_item_list(sorted_avail)

    

    def _handle_dropdown_menu_events(self, event):

        if event.ui_object_id.endswith("#map_action_selector"):
            self._handle_map_action(event.text)
        elif event.ui_object_id.endswith("select_algo"):
                self.selected_algorithm = event.text 
                logging.info(f"Selected algorithm: {self.selected_algorithm}")

        """
        elif event.ui_element == self.anim_dropdown:
            # Next Step button visibility
            logging.info(f"event.text: {event.text}, Animation_Mode.SINGLE_STEP.label: {Animation_Mode.SINGLE_STEP.label}")
            if event.text == Animation_Mode.SINGLE_STEP.name:
                self.next_step_button.show() 
                self.speed_dropdown.hide() # hide speed as it's irrelevant 
            else:
                self.next_step_button.hide() 
                self.speed_dropdown.show()
        """
        
        

    def set_status(self, message):
        self.status_label.set_text(message)
    
    def uncheck_start_end(self):
        #Unchecks both start and end boxes.
        self.check_place_start.is_checked = False 
        self.check_place_start.rebuild()
        self.check_place_end.is_checked = False 
        self.check_place_end.rebuild()




    def _handle_map_action(self, text):
        if text == Map_Actions.LOAD_MAP.label:
            self.open_file_dialog(Map_Actions.LOAD_MAP)
        elif text == Map_Actions.SAVE_MAP.label:
            self.open_file_dialog(Map_Actions.SAVE_MAP)


    def _handle_window_close_events(self, event):
        # Clean up dialog reference when closed
        if event.ui_element == self.active_file_dialog:
            self.active_file_dialog = None


    def open_file_dialog(self, action_type):
        #Sidebar owns the dialog object, but the App uses the result
        if self.active_file_dialog is None:
            # Default name for saving
            
            if action_type == Map_Actions.SAVE_MAP:
                title = "Save Map (Type name in path bar above)"
                path = "maps/new_map.json"
            else:
                title = action_type.label
                path = "maps/"


            self.active_file_dialog = UIFileDialog(
                rect=pygame.Rect(160, 50, 440, 500),
                manager=self.manager,
                window_title=title,
                initial_file_path=path,
                object_id="#map_file_dialog",
                allowed_suffixes={".json"},
                allow_existing_files_only=(action_type == Map_Actions.LOAD_MAP)
            )


    def _switch_tab(self, target_panel):
        self.panel_map_config.hide()
        self.panel_algo_settings.hide()
        self.panel_viz_settings.hide()
        target_panel.show() 
        self.active_panel = target_panel
 