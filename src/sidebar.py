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
    map_btn:    UIButton   # Hinting the attributes defined in _init_tabs 
    algo_btn:   UIButton  
    viz_button: UIButton
    map_panel:  UIPanel 
    algo_panel: UIPanel 
    viz_panel:  UIPanel


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
        self.map_btn  = None 
        self.algo_btn = None 
        self.viz_btn  = None
        self._init_tabs()

        # 2. Create the Panels (Containers)
        self.map_panel  = None
        self.algo_panel = None
        self.viz_panel  = None 
        self._init_panels()
         

        # 3. Initialize map panel with ui elements
        self.map_label = None
        self.map_dropdown = None 
        self.terrain_type_label = None 
        self.terrain_type_dropdown = None 
        self.grid_dimensions_label = None 
        self.grid_dimensions_dropdown = None 
        self.start_marker_checkbox = None
        self.start_marker_label = None 
        self.end_marker_checkbox = None
        self.end_marker_label = None 
        self.ui_layout.reset_flow()
        self._init_map_panel() 
       

        # 5. Initialze algorithm panel with ui elements 
        self.algo_label = None 
        self.algo_dropdown = None 
        self.diagonal_direction_checkbox = None 
        self.diagonal_direction_label = None 
        self.neighbor_direction_label = None 
        self.available_direction_list = None 
        self.neighbor_order_display = None 
        self.clear_order_button = None 

        self.ui_layout.reset_flow()
        self._init_algo_panel()

        # 6. Initialize viz panel with ui elements
        self.ui_layout.reset_flow()
        self._init_viz_panel() 
       
        # Set Initial Active Panel State 
        self.active_panel = self.algo_panel
        self.map_panel.hide()
        self.viz_panel.hide()


    def _init_tabs(self):
        """Create the Tab Buttons."""
        tab_w = self.config.SIDEBAR_WIDTH // 3 
        tab_h = 40 

        self.map_btn = UIButton(
            relative_rect=pygame.Rect((self.ui_layout.start_x,20), (tab_w, tab_h)),
            text="Map",
            manager=self.manager 
        )

        self.algo_btn = UIButton(
            relative_rect=pygame.Rect((self.ui_layout.start_x + tab_w,20), (tab_w, tab_h)),
            text="Algorithm",
            manager=self.manager 
        )

        self.viz_button = UIButton(
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

        self.map_panel = UIPanel(relative_rect=panel_rect, manager=self.manager, starting_height=1)
        self.algo_panel = UIPanel(relative_rect=panel_rect, manager=self.manager, starting_height=1)
        self.viz_panel = UIPanel(relative_rect=panel_rect, manager=self.manager, starting_height=1)


    def _init_map_panel(self):
        """
        Create UI elements for 
            1. Map actions: create map, load map, save map
            2. Terrain type, 
            3. Setting grid dimensions
            4. Setting start, end locations 
        """
        # 1. Map Actions 
        self.map_action_label = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.label_width, self.ui_layout.widget_height)),
            text="Map Actions:",
            manager=self.manager,
            container=self.map_panel 
        )

        self.map_action_dropdown = UIDropDownMenu(
            options_list=Map_Actions.list_labels(),
            starting_option=Map_Actions.EDIT_MAP.label,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row),
                (self.ui_layout.col2_width, self.ui_layout.widget_height)),
            manager=self.manager,
            container=self.map_panel,
            object_id="#map_action_selector"
        )
        
        self.ui_layout.draw_row += self.config.ROW_SPACING 

        # 2. Terrain        
        self.terrain_type_label = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.label_width, self.ui_layout.widget_height)),
            text="Terrain Type:",
            manager=self.manager,
            container=self.map_panel 
        )

        self.terrain_type_dropdown = UIDropDownMenu(
            options_list=[terrain.name for terrain in Terrain_Type],
            starting_option=Terrain_Type.GRASS.name,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row), 
                (self.ui_layout.col2_width, self.ui_layout.widget_height)),
            manager=self.manager,
            container=self.map_panel,
            object_id="#terrain_type_selector"
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING 
    
        # Grid Settings
        self.grid_dimensions_label = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row),
                (self.ui_layout.label_width, self.ui_layout.widget_height)
            ),
            text="Set Grid Size:",
            manager=self.manager,
            container=self.map_panel 
        )

        self.grid_dimensions_dropdown = UIDropDownMenu(
            options_list=Map_Dimension.get_ui_labels(),
            starting_option=Map_Dimension.MD8.label,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row),
                (self.ui_layout.col2_width, self.ui_layout.widget_height)
            ),
            manager=self.manager,
            container=self.map_panel,
            object_id="#grid_dimensions_selector"
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING 

        # Start/End Markers     
        self.start_marker_checkbox = UICheckBox(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row + 5), 
                (self.config.CHECKBOX_SIZE, self.config.CHECKBOX_SIZE)),
            text="",
            manager=self.manager,
            container=self.map_panel,
            object_id="#start_marker_checkbox"
        )

        self.start_marker_label = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x + self.config.CHECKBOX_SIZE + 5, self.ui_layout.draw_row), 
                (80, self.ui_layout.widget_height)),
            text="Set Start",
            manager=self.manager,
            container=self.map_panel 
        )

        self.end_marker_checkbox = UICheckBox(
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row + 5), 
                (self.config.CHECKBOX_SIZE, self.config.CHECKBOX_SIZE)),
            text="",
            manager=self.manager,
            container=self.map_panel,
            object_id="#end_marker_checkbox"
        )

        self.end_marker_label = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x + self.config.CHECKBOX_SIZE + 5, self.ui_layout.draw_row), 
                (80, self.ui_layout. widget_height)),
            text="Set End",
            manager=self.manager,
            container=self.map_panel 
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING 

        self.clear_grid_button = UIButton(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_widget_width, self.ui_layout.widget_height)
            ),
            text="CLEAR GRID",
            manager=self.manager,
            container=self.map_panel,
            object_id="#clear_grid_button",
            tool_tip_text="Click here to reset the entire drawing area."
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING  


    def _init_algo_panel(self):
        # 1. Algorithm Selection 
        self.algo_label = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.label_width, self.ui_layout.widget_height)),
            text="Algorithm:",
            manager=self.manager,
            container=self.algo_panel 
        )

        self.algo_dropdown = UIDropDownMenu(
            options_list=[algo.name for algo in Algorithm_Type],
            starting_option=Algorithm_Type.BFS.name,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row), 
                (self.ui_layout.col2_width, self.ui_layout.widget_height)),
            manager=self.manager,
            container=self.algo_panel,
            object_id="#algo_selector"
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING

        # 2. Neighbor Direction Priority 
                 
        # Diagonal Toggle Checkbox 
        self.diagonal_direction_checkbox = UICheckBox(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.config.CHECKBOX_SIZE, self.config.CHECKBOX_SIZE)),
            text="",
            manager=self.manager,
            container=self.algo_panel
        )

        self.diagonal_direction_label = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x + self.config.CHECKBOX_SIZE + 5, self.ui_layout.draw_row), 
                (self.ui_layout.width - self.ui_layout.label_width, self.ui_layout.widget_height)),
            text="Include Diagonals",
            manager=self.manager,
            container=self.algo_panel 
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING

        # Neighbor Search Order Settings
        self.neighbor_direction_label = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_widget_width, self.ui_layout.widget_height)
            ),
            text="Neighbor Search Order (Click to add):",
            manager=self.manager,
            container=self.algo_panel
        )

        self.ui_layout.draw_row += self.ui_layout.widget_height 

        # Selection Lists
        list_height = 100 
        self.available_direction_list = UISelectionList(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_widget_width, list_height)),
            item_list=Neighbor_Direction.get_labels(include_diagonals=False),
            manager=self.manager,
            container=self.algo_panel,
            object_id="#available_direction_selector"
        )

        self.ui_layout.draw_row += list_height + 10
        self.neighbor_order_display = UISelectionList(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_widget_width, list_height)),
            item_list=[],
            manager=self.manager,
            container=self.algo_panel,
            object_id="#neighbor_order_display"
        )

        self.ui_layout.draw_row += list_height + 10

        self.clear_order_button = UIButton(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_widget_width, self.ui_layout.widget_height)),
            text="Clear Order",
            manager=self.manager,
            container=self.algo_panel, 
            object_id="#clear_order_btn"
        )



    def _init_viz_panel(self):
        pass

    def handle_events(self, event):

        # Handles switching between map, panel, and viz tabs
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.map_btn:
                self._switch_tab(self.map_panel)
            elif event.ui_element == self.algo_btn:
                self._switch_tab(self.algo_panel)
            elif event.ui_element == self.viz_btn:
                self._switch_tab(self.viz_panel)

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


    def _handle_new_selection(self, event):

        # --- Moving from Available to Order ---
        if event.ui_object_id.endswith("#available_direction_selector"):
           
            selected = event.text 
            logging.info(f"Selected direction: {selected}")

            # Remove from Available 
            # Extract strings from the dictionary list
            current_avail = self._get_clean_item_list(self.available_direction_list)
            logging.info(f"current_avail: {current_avail}")

            if selected in current_avail:
                current_avail.remove(selected) 
                self.available_direction_list.set_item_list(current_avail)

                # Add to Neighbor Order 
                current_order = self._get_clean_item_list(self.neighbor_order_display)
                current_order.append(selected)
                self.neighbor_order_display.set_item_list(current_order)


        # --- Moving from Neighbor Order back to Available ---
        if event.ui_object_id.endswith("#neighbor_order_display"):
            selected = event.text 

            # Remove from Neighbor Order
            current_order = self._get_clean_item_list(self.neighbor_order_display)

            if selected in current_order:
                current_order.remove(selected)
                self.neighbor_order_display.set_item_list(current_order)

                # Add back to Available in sorted order
                current_avail = self._get_clean_item_list(self.available_direction_list)
                current_avail.append(selected)

                sorted_avail = Neighbor_Direction.sort_labels(current_avail)
                self.available_direction_list.set_item_list(sorted_avail)


    
    def _handle_checkbox_unchecked(self, event):
  
        if event.ui_element == self.diagonal_direction_checkbox:
            self._handle_diagonal_checkbox(is_checked=False)
            

    def _handle_checkbox_checked(self, event):

        if event.ui_element == self.start_marker_checkbox:
            if self.start_marker_checkbox.is_checked:
                # Force uncheck the other 
                self.end_marker_checkbox.is_checked = False 
                self.end_marker_checkbox.rebuild()

        elif event.ui_element == self.end_marker_checkbox:
            if self.end_marker_checkbox.is_checked:
                # force uncheck the other 
                self.start_marker_checkbox.is_checked = False 
                self.start_marker_checkbox.rebuild() 

        elif event.ui_element == self.diagonal_direction_checkbox:
           self._handle_diagonal_checkbox(is_checked=True)

    
    def _handle_diagonal_checkbox(self, is_checked):
        # 1. Get the current version of both lists 
        current_order = self._get_clean_item_list(self.neighbor_order_display)
        current_avail = self._get_clean_item_list(self.available_direction_list)

        # 2. Get the list of diagonal labels 
        diagonals = Neighbor_Direction.get_diagonal_labels() 

        if not is_checked:
                # Checkbox unchecked - remove diagonals from both lists 
                new_order = [item for item in current_order if item not in diagonals]
                new_avail = [item for item in current_avail if item not in diagonals]

                # update the UI 
                self.neighbor_order_display.set_item_list(new_order)
                self.available_direction_list.set_item_list(new_avail)
        else:
            # check box checked - add diagonals back to available 
            for d in diagonals:
                if d not in current_avail and d not in current_order:
                    current_avail.append(d)

            sorted_avail = Neighbor_Direction.sort_labels(current_avail)
            self.available_direction_list.set_item_list(sorted_avail)

    

    def _handle_dropdown_menu_events(self, event):

        if event.ui_object_id.endswith("#map_action_selector"):
            self._handle_map_action(event.text)
        elif event.ui_object_id.endswith("algo_dropdown"):
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
        self.start_marker_checkbox.is_checked = False 
        self.start_marker_checkbox.rebuild()
        self.end_marker_checkbox.is_checked = False 
        self.end_marker_checkbox.rebuild()




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
        self.map_panel.hide()
        self.algo_panel.hide()
        self.viz_panel.hide()
        target_panel.show() 
        self.active_panel = target_panel
 