import pygame 
import json 

import logging 

logger = logging.getLogger(__name__)

class Grid:

    # Terrain Types
    EMPTY = 0
    WALL = 1
    GREEN = 2
    BLUE = 3
    GRAY = 4 
    START = 5 
    END = 6

    # Terrain Colors
    COLORS = {
        EMPTY: (225, 225, 225), # light gray / off-white 
        WALL:  (50, 50, 50),    # very dark gray 
        GREEN: (46, 204, 113),  # emerald green 
        BLUE:  (52, 152, 219),  # Peter River Blue 
        GRAY:  (149, 165, 166), # Concrete gray
        START: (241, 196, 15),  # bright yellow 
        END:   (231, 75, 60),   # bright red
    }


    COLOR_GRID_LINE = (50, 50, 50)      # Lighter gray lines

    def __init__(self, x, y, num_cells, cell_size):

        self.rows = num_cells 
        self.cols = num_cells 
        self.cell_size = cell_size                  # units: pixels
        self.grid_size = num_cells * cell_size      # units: pixels

        self.rect = pygame.Rect(x, y, self.grid_size, self.grid_size)

        self.current_brush = self.GREEN

        self.start_pos = None 
        self.end_pos = None 
        
        

        # init 2D list with 0 (Empty)
        self.map = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    
    def clear(self):
         """Resets the grid map to all empty (0)."""
         self.map = [[self.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
         self.start_pos = None 
         self.end_pos = None 
         logger.info("Grid cleared!")

    
    def get_pos(self, pos):
        """Translates screen pixel coordinates to (row, col)."""
        x, y = pos 
        if self.rect.collidepoint(pos):
            # subtract grid offset, then divide by cell size 
            col = (x - self.rect.x) // self.cell_size
            row = (y - self.rect.y) // self.cell_size
            return row, col 
        return None 
    
    def handle_mouse(self):
        """Check mouse state every frame for continuous drawing/erasing."""
        mouse_buttons = pygame.mouse.get_pressed() 
        mpos = pygame.mouse.get_pos()

        # Get the cell location under the mouse 
        cell = self.get_pos(mpos)
        if not cell:
             return 
        
        row, col = cell 

        if mouse_buttons[0]:    # left click held down 
            # if we are painting Start or End, clear the old one first 
            if self.current_brush == self.START:
                if self.start_pos:
                    old_r, old_c = self.start_pos 
                    self.map[old_r][old_c] = self.EMPTY 
                self.start_pos = (row, col)
            elif self.current_brush == self.END:
                if self.end_pos:
                    old_r, old_c = self.end_pos 
                    self.map[old_r][old_c] = self.EMPTY 
                self.end_pos = (row, col)

            # if painting over and existing START/END with terrain, clear the reference 
            elif (row, col) == self.start_pos: self.start_pos = None 
            elif (row, col) == self.end_pos: self.end_pos = None 

            self.map[row][col] = self.current_brush



        elif mouse_buttons[2]:      # right click held down (eraser)
            if (row, col)  == self.start_pos: self.start_pos = None 
            elif (row, col) == self.end_pos: self.end_pos = None 
            self.map[row][col] = self.EMPTY


    def draw(self, surface):
        # Draw the colored cell blocks
        for row in range(self.rows):
             for col in range(self.cols):
                  terrain_type = self.map[row][col]
                  if terrain_type != self.EMPTY:
                    rect = pygame.Rect( self.rect.x + (col * self.cell_size), 
                                        self.rect.y + (row * self.cell_size),
                                        self.cell_size,
                                        self.cell_size
                                        )
                    pygame.draw.rect(surface, self.COLORS[terrain_type], rect)

        # Draw grid lines (square grid: rows equal cols)
        for i in range(self.rows + 1):
                offset = i * self.cell_size

                #vertical lines
                pygame.draw.line(surface, self.COLOR_GRID_LINE, 
                                 (self.rect.x + offset, self.rect.y), 
                                 (self.rect.x + offset, self.rect.y + self.grid_size)
                                )
                
                # horizontal lines
                pygame.draw.line(surface, self.COLOR_GRID_LINE, 
                                 (self.rect.x, self.rect.y + offset), 
                                 (self.rect.x + self.grid_size, self.rect.y + offset)
                                )
    
    def find_node(self, node_type):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.map[r][c] == node_type:
                    return (r, c)
        return None 


    def load_from_file(self, file_path):
        """Loads a map from a JSON file into the grid."""
        try:
            with open(file_path, 'r') as f:
                loaded_data = json.load(f)
            
            if len(loaded_data) == self.rows and len(loaded_data[0]) == self.cols:
                self.map = loaded_data 
                self.start_pos = self.find_node(self.START)
                self.end_pos = self.find_node(self.END)
                logger.info(f"Map loaded successfully from {file_path}")
            else:
                logger.error("Loaded map dimensions do not match current grid.")
        except Exception as e:
            logger.error(f"Failed to load map: {e}")
    

    def save_to_file(self, file_path):
        """Saves the current map 2D list to a JSON file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.map, f) 
            logger.info(f"Map successfully saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save map: {e}")