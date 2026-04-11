import pygame 
import pygame_gui 
import logging 


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

    def __init__(self, width, padding, widget_height, label_width, start_row):

        self.width = width 
        self.padding = padding 
        self.widget_height = widget_height 
        self.label_width = label_width 
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
    def __init__(self, manager, config: AppConfig):
        self.manager = manager
        self.config = config

        self.ui_layout = UI_Layout(
            width=config.SIDEBAR_WIDTH,
            padding = 10,
            widget_height=self.config.WIDGET_HEIGHT,
            label_width=110,
            start_row=config.UI_START_ROW
        )

        self.ui_layout.draw_row = 20
        self.x_offset = self.config.GRID_WIDTH + (self.config.GRID_PADDING * 2)

        # 1. Create Tab Buttons ad the top of hte Sidebar
        self._init_tabs()


        # 2. Create the Panels (Containers)
        panel_y_start = 70 
        bottom_margin = 20 
        dynamic_height = config.GRID_WIDTH + (config.GRID_PADDING * 2) - panel_y_start - bottom_margin
        panel_rect = pygame.Rect(
            (self.x_offset, panel_y_start), 
            (config.SIDEBAR_WIDTH, dynamic_height))

        self.map_panel = UIPanel(relative_rect=panel_rect, manager=self.manager, starting_height=1)
        self.algo_panel = UIPanel(relative_rect=panel_rect, manager=self.manager, starting_height=1)
        self.viz_panel = UIPanel(relative_rect=panel_rect, manager=self.manager, starting_height=1)

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
        tab_w = self.config.SIDEBAR_WIDTH // 3 
        tab_h = 40 

        self.btn_map = UIButton(
            relative_rect=pygame.Rect((self.x_offset,20), (tab_w, tab_h)),
            text="Map",
            manager=self.manager 
        )

        self.btn_algo = UIButton(
            relative_rect=pygame.Rect((self.x_offset + tab_w,20), (tab_w, tab_h)),
            text="Algorithm",
            manager=self.manager 
        )

        self.btn_viz = UIButton(
            relative_rect=pygame.Rect((self.x_offset + tab_w * 2,20), (tab_w, tab_h)),
            text="Visualize",
            manager=self.manager 
        )


    def _init_map_tab(self):

        # 1. Map Actions 
        self.map_label = UILabel(
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


    def _init_algo_tab(self):
        pass 

    def _init_viz_tab(self):
        pass

    def handle_events(self, event):

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_map:
                self._switch_tab(self.map_panel)
            elif event.ui_element == self.btn_algo:
                self._switch_tab(self.algo_panel)
            elif event.ui_element == self.btn_viz:
                self._switch_tab(self.viz_panel)

    def _switch_tab(self, target_panel):
        self.map_panel.hide()
        self.algo_panel.hide()
        self.viz_panel.hide()
        target_panel.show() 
        self.active_panel = target_panel
 

    def _handle_map_action(self, text):
        """Trigger dialogs, but leave grid clearing to the App."""

        logging.info("map action text: {text}")
        if text == Map_Actions.LOAD_MAP.name:
                self.open_file_dialog(Map_Actions.LOAD_MAP)
        elif text == Map_Actions.SAVE_MAP.name:
            self.open_file_dialog(Map_Actions.SAVE_MAP)
        
 