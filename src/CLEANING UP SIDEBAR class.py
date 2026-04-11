CLEANING UP SIDEBAR class. Keep these old functions until we use or delete.

Initializing 

        """
        self.pending_grid_size = None 
        self.confirmation_dialog = None 
        
        # Track the active dialog to distinguish between Load and Save actions
        self.active_file_dialog = None 
        self.current_action = None 
        
        self.selected_algo = Algorithm_Type.BFS
        self.neighbor_order_list = []

    
        
        


         # --- Map Actions---
        self._init_ui_map_actions()
        self._init_ui_grid_settings()  # grid size toggle

        # --- Row 2: Terrain ---
        self._init_ui_terrain()

        # Start/End Selection 
        self._init_ui_start_end_markers()

        self._init_ui_clear_grid_button()

        # Initial visibility: everything for 'Create Map' will be hidden
        self.update_visibility(Map_Actions.SELECT_NODES.label)


        # --- Row 3: Algorithm --- 
        #self._init_algorithm_selection()

        # --- Row 4: Neighbor Direction --- 
        #self._init_ui_neighbor_direction()
       
        
    
        draw_row += 30

        # --- Row 5: Action Buttons 
        draw_row += list_height + 20
        self.run_search_button = UIButton(
            relative_rect=pygame.Rect((col1_x, draw_row), (full_widget_width, widget_height)),
            text="RUN SEARCH",  
            manager=self.manager
        )



        # --- Row 6: Start/End Selection ---
        

        # --- Row 7: Animation Mode ---
        draw_row += row_offset
        self.anim_label = UILabel(
            relative_rect=pygame.Rect((col1_x, draw_row), (label_width, widget_height)),
            text="Animation: ",
            manager=self.manager
        )

        self.anim_dropdown = UIDropDownMenu(
            options_list=[anim.name for anim in Animation_Mode],
            starting_option=Animation_Mode.ANIMATED.name,  
            relative_rect=pygame.Rect((col2_x, draw_row), (right_col_width, widget_height)),
            manager=self.manager
        )

        # --- Row 8: Shared position of Speed Multiplier (Hidden unless "Animated" is selected) 
        #     and Next Step Button ---

        draw_row += row_offset

        shared_rect = pygame.Rect((col1_x, draw_row), (full_widget_width, widget_height))

        self.speed_options = Speed_Options.list_labels()
        self.speed_dropdown = UIDropDownMenu(
            options_list=self.speed_options,
            starting_option=self.speed_options[0], # default to 1x
            relative_rect=shared_rect,
            manager=self.manager
        )

        # --- Row 8: Next Step Button (hidden by default) --- 
        self.next_step_button = UIButton(
            relative_rect=shared_rect,
            text="NEXT STEP",
            manager=self.manager,
            visible=0 # start hidden
        )

        # --- Row 9: Status Message --- 
        self.status_label = UITextBox(
            html_text="Ready",
            relative_rect=pygame.Rect((col1_x, draw_row), (full_widget_width, widget_height)),
            manager=self.manager,
            object_id="#status_label"
        )
        
        """ 



    def _init_ui_clear_grid_button(self):

        self.clear_grid_button = UIButton(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1_x, self.ui_layout.draw_row), 
                (self.ui_layout.full_widget_width, self.ui_layout.widget_height)
            ),
            text="CLEAR GRID",
            manager=self.manager
        )

        self.ui_layout.draw_row += self.ui_layout.y_offset 


    def _init_ui_algorithm_selection(self):
       
        self.algo_label = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1_x, self.ui_layout.draw_row), 
                (self.ui_layout.label_width, self.ui_layout.widget_height)),
            text="Algorithm:",
            manager=self.manager
        )

        self.algo_dropdown = UIDropDownMenu(
            options_list=[algo.name for algo in Algorithm_Type],
            starting_option=Algorithm_Type.BFS.name,
            relative_rect=pygame.Rect(
                (self.ui_layout.col2_x, self.ui_layout.draw_row), 
                (self.ui_layout.right_col_width, self.ui_layout.widget_height)),
            manager=self.manager
        )

        self.ui_layout.draw_row += self.ui_layout.y_offset


    def _init_ui_neighbor_direction(self):
         
        list_height = 100 

        # Diagonal Toggle Checkbox 
        self.diagonal_checkbox = UICheckBox(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1_x, self.ui_layout.draw_row), 
                (self.ui_layout.checkbox_size, self.ui_layout.checkbox_size)),
            text="",
            manager=self.manager 
        )

        self.diagonal_label = UILabel(
            relative_rect=pygame.Rect(
                (self.ui_layout.col1_x + self.ui_layout.checkbox_size + 5, self.ui_layout.draw_row), 
                (self.ui_layout.width - self.ui_layout.label_width, self.ui_layout.widget_height)),
            text="Include Diagonals",
            manager=self.manager
        )

        self.ui_layout.draw_row += self.ui_layout.y_offset

        draw_row += 30

        # Label to explain lists purpose 
        self.direction_label = UILabel(
            relative_rect=pygame.Rect((col1_x, draw_row), (full_widget_width, 25)),
            text="Neighbor Search Order (Click to add):",
            manager=self.manager
        )

        draw_row += 30  # smaller offset for label

        # Available Directions (Cardinal Only)
        self.available_list = UISelectionList(
            relative_rect=pygame.Rect((col1_x, draw_row), (full_widget_width, list_height)),
            item_list=['North', 'East', 'South', 'West'],
            manager=self.manager
        )

        draw_row += list_height + 10
        self.neighbor_order_display = UISelectionList(
            relative_rect=pygame.Rect((col1_x, draw_row), (full_widget_width, list_height)),
            item_list=[],
            manager=self.manager
        )

        draw_row += list_height + 5 
        self.clear_order_button = UIButton(
            relative_rect=pygame.Rect((col1_x, draw_row), (full_widget_width, 25)),
            text="Clear Order",
            manager=self.manager
        )


   
        """
        # Listen for the actual confirmation
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element == self.confirmation_dialog:
                selected_dim = Map_Dimension.from_label(self.pending_grid_size)
                print(f"Applying new grid size: {selected_dim.value}")
                # CALL YOUR ACTUAL RESIZE LOGIC HERE
                # self.app.resize_grid(selected_dim.value)
                logging.fatal(f"Missing logic to resize grid to {selected_dim} rows and columns")

    
        if event.type == pygame_gui.UI_CHECK_BOX_CHECKED:
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
        """ Just close the dialog; let the App handle the grid logic."""
        if event.ui_element == self.active_file_dialog:
            if self.current_action == Map_Actions.SAVE_MAP:
               self.active_file_dialog = None 

    def _handle_window_close_events(self, event):
        # Clean up dialog reference when closed
        if event.ui_element == self.active_file_dialog:
            self.active_file_dialog = None
            self.current_action = None
           

       
    def open_file_dialog(self, action_type):
        """Sidebar owns the dialog object, but the App uses the result"""
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
        """Unchecks both start and end boxes."""
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



Removed from theme.json

{
    "selection_list": {
        "colours": {
            "dark_bg": "#ffffff",
            "normal_border": "#999999"
        }
    },
    "selection_list.@selection_list_item": {
        "colours": {
            "normal_bg": "#ffffff",
            "normal_text": "#000000",
            "hovered_bg": "#e0e0e0",
            "selected_bg": "#d8e2f2",
            "selected_text": "#000000"
        }
    },
    
    "checkbox": {
        "colours": {
            "normal_bg": "#f0f0f0",
            "hovered_bg": "#e0e0e0",
            "clicked_bg": "#d0d0d0",
            "normal_text": "#000000",
            "selected_text": "#000000"
        },
        "misc": {
            "text_shadow_size": "0"
        }
    },
    
     "label": {
        "colours": {
            "normal_text": "#000000",
            "text_shadow": "#444444"
        }
    },

    "button": {
        "colours": {
            "normal_bg": "#d8e2f2",
            "hovered_bg": "#c8d2e2",
            "active_bg": "#b8c2d2",
            "normal_text": "#000000",
            "hovered_text": "#FFFFFF"
        }
    },
    "file_dialog": {
        "colours": {
            "dark_bg": "#d8e2f2",
            "title_bar_colour": "#b8c2d2"
        }
    },
    "file_dialog.#file_display_list": {
        "colours": {
            "dark_bg": "#ffffff" 
        }
    },
    "file_dialog.#file_display_list.@selection_list_item": {
        "colours": {
            "normal_bg": "#ffffff",
            "selected_bg": "#b8c2d2",
            "normal_text": "#000000",
            "selected_text": "#000000",
            "hovered_bg": "#c8d2e2"
        }
    }
}
