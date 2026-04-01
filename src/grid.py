import pygame 
import json 

import logging 

from .node import Node

logger = logging.getLogger(__name__)

class Grid:

    # Terrain Types
    DEFAULT = 0
    NAVY = 1
    GREEN = 2
    BLUE = 3
    GRAY = 4 
    START = 5 
    END = 6

    # Terrain Colors
    COLORS = {
        DEFAULT: (225, 225, 225), # light gray / off-white 
        NAVY:  (0, 0, 128),    # navy blue 
        GREEN: (46, 204, 113),  # emerald green 
        BLUE:  (52, 152, 219),  # Peter River Blue 
        GRAY:  (149, 165, 166), # Concrete gray
        START: (241, 196, 15),  # bright yellow 
        END:   (231, 75, 60),   # bright red
    }

    # Visited Color
    VISITED_COLOR = (173, 216, 230)  # light blue


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
        
        # init 2D list
        self.map = [[Node(r, c, cell_size, self.DEFAULT) for c in range(self.cols)] 
                    for r in range(self.rows)
        ]

    
    def clear(self):
        """Resets the grid map to all DEFAULT (0)."""
        self.map = [
            [Node(r, c, self.cell_size, self.DEFAULT) for c in range(self.cols)] 
            for r in range(self.rows)
        ]
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
        node = self.map[row][col]

        if mouse_buttons[0]:    # left click held down 
            # if we are painting Start or End, clear the old one first 
            if self.current_brush == self.START:
                if self.start_pos:
                    old_r, old_c = self.start_pos 
                    self.map[old_r][old_c].terrain = self.DEFAULT
                self.start_pos = (row, col)
            elif self.current_brush == self.END:
                if self.end_pos:
                    old_r, old_c = self.end_pos 
                    self.map[old_r][old_c].terrain = self.DEFAULT 
                self.end_pos = (row, col)

            # if painting over and existing START/END with terrain, clear the reference 
            elif (row, col) == self.start_pos: self.start_pos = None 
            elif (row, col) == self.end_pos: self.end_pos = None 

            node.terrain = self.current_brush



        elif mouse_buttons[2]:      # right click held down (eraser)
            if (row, col)  == self.start_pos: self.start_pos = None 
            elif (row, col) == self.end_pos: self.end_pos = None 
            node.terrain = self.DEFAULT


    def draw(self, surface):
        # Draw the colored cell blocks
        for row in self.map:
             for node in row:
                # Determine color based on node.terrain or node.visited 
                color = self.COLORS.get(node.terrain, self.COLORS[self.DEFAULT])

                # Special color for search visualization 
                if node.visited and node.terrain not in [self.START, self.END]:
                     color = self.VISITED_COLOR 
                
                node.draw(surface, self.rect.x, self.rect.y, color)
             

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
                if self.map[r][c].terrain == node_type:
                    return (r, c)
        return None 


    def load_from_file(self, file_path):
        """Loads a map from a JSON file into the grid."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            for r in range(self.rows):
                for c in range(self.cols):
                    self.map[r][c].terrain = data[r][c]
                    if data[r][c] == self.START: self.start_pos = (r, c)
                    if data[r][c] == self.END: self.end_pos = (r, c)
        except Exception as e:
            logger.error(f"Failed to load map: {e}")
    

    def save_to_file(self, file_path):
        """Saves the current map 2D list to a JSON file."""

        # Create a 2D list of integers from the Nodes to save as JSON 
        raw_map = [[node.terrain for node in row] for row in self.map]

        try:
            with open(file_path, 'w') as f:
                json.dump(raw_map, f) 
            logger.info(f"Map successfully saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save map: {e}")