import pygame 
import logging 

logger = logging.getLogger(__name__)

class Grid:

    COLOR_GRID_LINE = (50, 50, 50)      # Lighter gray lines

    def __init__(self, x, y, num_cells, cell_size):

        self.rows = num_cells 
        self.cols = num_cells 
        self.cell_size = cell_size                  # units: pixels
        self.grid_size = num_cells * cell_size      # units: pixels

        self.rect = pygame.Rect(x, y, self.grid_size, self.grid_size)
        
        

        # init 2D list with 0 (Empty)
        self.map = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    
    def get_cell_from_pos(self, pos):
        """Translates screen pixel coordinates to (row, col)."""
        x, y = pos 
        if self.rect.collidepoint(pos):
            # subtract grid offset, then divide by cell size 
            col = (x - self.rect.x) // self.cell_size
            row = (y - self.rect.y) // self.cell_size
            return row, col 
        return None 
    
    def handle_mouse(self):
        pass 


    def draw(self, surface):

        # Draw grid lines (square grid: rows equal cols)
        for i in range(self.grid_size + 1):
                #vertical lines
                pygame.draw.line(surface, self.COLOR_GRID_LINE, (i * self.cell_size, 0), (i * self.cell_size, self.grid_size))
                
                # horizontal lines
                pygame.draw.line(surface, self.COLOR_GRID_LINE, (0, i * self.cell_size), (i * self.grid_size, i * self.cell_size))
            
                