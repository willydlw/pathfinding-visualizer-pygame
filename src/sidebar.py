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

        
        # 1. Create Tab Buttons ad the top of hte Sidebar
        self.map_btn  = None 
        self.algo_btn = None 
        self.viz_btn  = None
        self._init_tabs()

        # 2. Create the Panels (Containers)
        self.map_panel  = None
        self.algo_panel = None
        self.viz_panel  = None 
        self._init_panels()
        

        # 3. Initialize Content 
        self.ui_layout.reset_flow()
        self._init_map_tab() 
    
        self.ui_layout.reset_flow()
        self._init_algo_tab()

        self.ui_layout.reset_flow()
        self._init_viz_tab() 

        # 4. Set Initial State 
        self.active_panel = self.map_panel 
        self.algo_panel.hide()
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


    def _init_map_tab(self):

        # 1. Map Actions 
        self.label_map = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.label_width, self.ui_layout.widget_height)),
            text="Map Actions:",
            manager=self.manager,
            container=self.map_panel 
        )

        self.map_dropdown = UIDropDownMenu(
            options_list=Map_Actions.list_labels(),
            starting_option=Map_Actions.SELECT_NODES.label,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row),
                (self.ui_layout.col2_width, self.ui_layout.widget_height)),
            manager=self.manager,
            container=self.map_panel 
        )
        
        self.ui_layout.draw_row += self.config.ROW_SPACING 

        # 2. Terrain        
        self.terrain_label = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.label_width, self.ui_layout.widget_height)),
            text="Terrain Type:",
            manager=self.manager,
            container=self.map_panel 
        )

        self.terrain_dropdown = UIDropDownMenu(
            options_list=[terrain.name for terrain in Terrain_Type],
            starting_option=Terrain_Type.GRASS.name,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row), 
                (self.ui_layout.col2_width, self.ui_layout.widget_height)),
            manager=self.manager,
            container=self.map_panel 
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING 
    
        # Grid Settings
        self.grid_size_label = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row),
                (self.ui_layout.label_width, self.ui_layout.widget_height)
            ),
            text="Set Grid Size:",
            manager=self.manager,
            container=self.map_panel 
        )

        self.grid_size_dropdown = UIDropDownMenu(
            options_list=Map_Dimension.get_ui_labels(),
            starting_option=Map_Dimension.MD8.label,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row),
                (self.ui_layout.col2_width, self.ui_layout.widget_height)
            ),
            manager=self.manager,
            container=self.map_panel 
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING 

        # Start/End Markers     
        self.start_checkbox = UICheckBox(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row + 5), 
                (self.config.CHECKBOX_SIZE, self.config.CHECKBOX_SIZE)),
            text="",
            manager=self.manager,
            container=self.map_panel 
        )

        self.start_label = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x + self.config.CHECKBOX_SIZE + 5, self.ui_layout.draw_row), 
                (80, self.ui_layout.widget_height)),
            text="Set Start",
            manager=self.manager,
            container=self.map_panel 
        )

        self.end_checkbox = UICheckBox(
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row + 5), 
                (self.config.CHECKBOX_SIZE, self.config.CHECKBOX_SIZE)),
            text="",
            manager=self.manager,
            container=self.map_panel 
        )

        self.end_label = UILabel(
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
            container=self.map_panel 
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING  


    def _init_algo_tab(self):
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
            options_list=[algo.label for algo in Algorithm_Type],
            starting_option=Algorithm_Type.BFS.label,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2x, self.ui_layout.draw_row), 
                (self.ui_layout.col2_width, self.ui_layout.widget_height)),
            manager=self.manager,
            container=self.algo_panel 
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING

        # 2. Neighbor Direction Priority 
                 
        # Diagonal Toggle Checkbox 
        self.diagonal_checkbox = UICheckBox(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.config.CHECKBOX_SIZE, self.config.CHECKBOX_SIZE)),
            text="",
            manager=self.manager,
            container=self.algo_panel 
        )

        self.diagonal_label = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x + self.config.CHECKBOX_SIZE + 5, self.ui_layout.draw_row), 
                (self.ui_layout.width - self.ui_layout.label_width, self.ui_layout.widget_height)),
            text="Include Diagonals",
            manager=self.manager,
            container=self.algo_panel 
        )

        self.ui_layout.draw_row += self.config.ROW_SPACING


        # Search Order Instructions
       
        self.direction_label = UILabel(
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
        self.available_list = UISelectionList(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_widget_width, list_height)),
            item_list=Neighbor_Direction.get_labels(include_diagonals=False),
            manager=self.manager,
            container=self.algo_panel 
        )

        self.ui_layout.draw_row += list_height + 10
        self.neighbor_order_display = UISelectionList(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_widget_width, list_height)),
            item_list=[],
            manager=self.manager,
            container=self.algo_panel 
        )

        self.ui_layout.draw_row += list_height + 10

        self.clear_order_button = UIButton(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1x, self.ui_layout.draw_row), 
                (self.ui_layout.full_widget_width, self.ui_layout.widget_height)),
            text="Clear Order",
            manager=self.manager,
            container=self.algo_panel 
        )



    def _init_viz_tab(self):
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
            self._handle_dropdown_menu_events(event)

        elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            self._handle_file_dialog_path_picked_events(event)

        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            self._handle_window_close_events(event)

    
    def _handle_checkbox_unchecked(self, event):
        if event.ui_element == self.size_checkbox:
            self.size_dropdown.disable()

        elif event.ui_element == self.diagonal_checkbox:
            diagonals = Neighbor_Direction.get_diagonal_labels()

            # 1. Remove diagonals from the available list 
            current_available = [item['text'] for item in self.available_list.item_list]
            new_available = [d for d in current_available if d not in diagonals]
            self.available_list.set_item_list(new_available)

            # 2. Also remove them from the Order list if they were already selected 
            self.neighbor_order_list = [d for d in self.neighbor_order_list if d not in diagonals]
            self.neighbor_order_display.set_item_list(self.neighbor_order_list)


    def _handle_checkbox_checked(self, event):

        if event.type == self.start_checkbox:
            self.end_checkbox.is_checked = False 
            self.end_checkbox.rebuild()
        
        elif event.type == self.end_checkbox:
            self.start_checkbox.is_checked = False 
            self.start_checkbox.rebuild()

        elif event.ui_element == self.start_checkbox:
            if self.start_checkbox.is_checked:
                # Force uncheck the other 
                self.end_checkbox.is_checked = False 
                self.end_checkbox.rebuild()

        elif event.ui_element == self.end_checkbox:
            if self.end_checkbox.is_checked:
                # force uncheck the other 
                self.start_checkbox.is_checked = False 
                self.start_checkbox.rebuild() 

        elif event.ui_element == self.diagonal_checkbox:
            self.refresh_available_list()

    

    def _handle_dropdown_menu_events(self, event):

        if event.ui_element == self.map_dropdown:
            self.update_visibility(event.text)
      
        elif event.ui_element == self.grid_size_dropdown:

            # Store the intended size but don't apply it yet 
            self.pending_grid_size = event.text 

            # Create the confirmation dialog 
            # Create the confirmation dialog
            self.confirmation_dialog = UIConfirmationDialog(
                rect=pygame.Rect((400, 200), (300, 200)), # Center this as needed
                manager=self.manager,
                window_title="Confirm Resize",
                action_long_desc="Resizing the grid will <b>clear all current drawings</b>. Do you want to proceed?",
                action_short_name="Yes, Resize",
                blocking=True
            )

    
        elif event.ui_element == self.anim_dropdown:
            # Next Step button visibility
            logging.info(f"event.text: {event.text}, Animation_Mode.SINGLE_STEP.label: {Animation_Mode.SINGLE_STEP.label}")
            if event.text == Animation_Mode.SINGLE_STEP.name:
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

        elif event.ui_element == self.neighbor_order_dropdown:
            self._handle_neighbor_order(event.text)
        """
            

    def _handle_neighbor_order(self, event):
        self.neighbor_order = event
        logging.info(f"self.neighbor_order: {self.neighbor_order}")


    def _handle_file_dialog_path_picked_events(self, event):
        # Just close the dialog; let the App handle the grid logic.
        if event.ui_element == self.active_file_dialog:
            if self.current_action == Map_Actions.SAVE_MAP:
               self.active_file_dialog = None 

    def _handle_window_close_events(self, event):
        # Clean up dialog reference when closed
        if event.ui_element == self.active_file_dialog:
            self.active_file_dialog = None
            self.current_action = None
           

       
    def open_file_dialog(self, action_type):
        #Sidebar owns the dialog object, but the App uses the result
        if self.active_file_dialog is None:
            title = action_type.label

            self.active_file_dialog = UIFileDialog(
                rect=pygame.Rect(160, 50, 440, 500),
                manager=self.manager,
                window_title=title,
                initial_file_path="maps/"
            )

            self.current_action = action_type


    def refresh_available_list(self):
        # Base set of directions
        all_allowed = Neighbor_Direction.get_labels(
            include_diagonals=self.diagonal_checkbox.is_checked
        )

        # Available side gets filtered and sorted
        new_available = [d for d in all_allowed if d not in self.neighbor_order_list]
        sorted_available = Neighbor_Direction.sort_labels(new_available)
        self.available_list.set_item_list(sorted_available)

        # Order side gets updated but stays in the order items were clicked 
        self.neighbor_order_display.set_item_list(self.neighbor_order_list)


    def set_status(self, message):
        self.status_label.set_text(message)
    
    def uncheck_start_end(self):
        #Unchecks both start and end boxes.
        self.start_checkbox.is_checked = False 
        self.start_checkbox.rebuild()
        self.end_checkbox.is_checked = False 
        self.end_checkbox.rebuild()

    def update_visibility(self, label_text):
        current_action = Map_Actions.from_label(label_text)
        is_editing = (current_action == Map_Actions.CREATE_MAP)
        
        # Use the specific names you defined in _init_ui_grid_settings
        widgets = [
            self.grid_size_label, 
            self.grid_size_dropdown,
            self.terrain_label,
            self.terrain_dropdown,
            self.start_label,
            self.start_checkbox,
            self.end_label,
            self.end_checkbox,
            self.clear_grid_button
        ]

        for widget in widgets:
            widget.show() if is_editing else widget.hide()






    def _handle_map_action(self, text):
        #Trigger dialogs, but leave grid clearing to the App.

        logging.info("map action text: {text}")
        if text == Map_Actions.LOAD_MAP.name:
                self.open_file_dialog(Map_Actions.LOAD_MAP)
        elif text == Map_Actions.SAVE_MAP.name:
            self.open_file_dialog(Map_Actions.SAVE_MAP)
        
 """
        

    def _switch_tab(self, target_panel):
        self.map_panel.hide()
        self.algo_panel.hide()
        self.viz_panel.hide()
        target_panel.show() 
        self.active_panel = target_panel
 