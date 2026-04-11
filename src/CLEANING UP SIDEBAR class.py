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
       
        self._init_ui_clear_grid_button()

        # Initial visibility: everything for 'Create Map' will be hidden
        self.update_visibility(Map_Actions.SELECT_NODES.label)


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


        """
        # Listen for the actual confirmation
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element == self.confirmation_dialog:
                selected_dim = Map_Dimension.from_label(self.pending_grid_size)
                print(f"Applying new grid size: {selected_dim.value}")
                # CALL YOUR ACTUAL RESIZE LOGIC HERE
                # self.app.resize_grid(selected_dim.value)
                logging.fatal(f"Missing logic to resize grid to {selected_dim} rows and columns")

 
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
