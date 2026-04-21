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
    