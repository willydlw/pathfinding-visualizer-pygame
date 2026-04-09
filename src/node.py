import pygame
import logging 

logger = logging.getLogger(__name__)

from .constants import TERRAIN_COLORS, Terrain_Type, UI_COLORS

class Node:
    def __init__(self, row, col, size, terrain):
        self.row = row 
        self.col = col 
        self.x = col * size 
        self.y = row * size 
        self.size = size 

        self.terrain = terrain 

        # State Flags
        self.visited = False        # "Open set" (in queue/stack)
        self.closed  = False        # "Closed set" (fully processed)
        self.path    = False        
        self.parent = None 
        self.is_start = False 
        self.is_end = False 
      

        # Costs for A* 
        self.g = float('inf')
        self.h = 0 
        self.f = 0 

    def __eq__(self, other):
        # Type check: Ensure the other object is the same class 
        if not isinstance(other, Node):
            return NotImplemented
        
        # two objects are equal if they have same row, col positions
        return self.row == other.row and self.col == other.col
    

    def __hash__(self):
        """
        Allows Node objects to be use as dictionary keys.
        Hashed based on coordinates to match equality logic.
        """
        return hash((self.row, self.col))
    
    def __str__(self):
        return (
            f"[row, col]: ({self.row}, {self.col}), [x,y]: ({self.x}, {self.y}), "
            f"terrain: {self.terrain}, visited: {self.visited}"
        )

    def draw(self, surface, font, x_offset, y_offset):
        
        if self.is_start:
            color = TERRAIN_COLORS[UI_COLORS.START]
        elif self.is_end:
            color = TERRAIN_COLORS[UI_COLORS.END]
        elif self.path:
            color = TERRAIN_COLORS[UI_COLORS.PATH]
        elif self.visited:
            color = TERRAIN_COLORS[UI_COLORS.VISITED]
        elif self.closed:
            color = TERRAIN_COLORS[UI_COLORS.CLOSED]
        else:
            color = TERRAIN_COLORS[self.terrain]

        rect = (self.x + x_offset, self.y + y_offset, self.size, self.size)
        pygame.draw.rect(surface, color, rect)

        #logger.info(f"row: {self.row}, col: {self.col}, f: {self.f}, g: {self.g}, h: {self.h}")

        text_color = (255, 255, 255)

        if self.g < float('inf'):
            # Convert to string FIRST to avoid OverflowError on float('inf')
            g_str = str(int(self.g)) if self.g != float('inf') else 'inf'
            f_str = str(int(self.f)) if self.f != float('inf') else 'inf'
            h_str = str(int(self.h)) if self.h != float('inf') else 'inf'

      
            # Render and Blit
            # f: top left, g: bottom left, h: bottom right
            f_text = font.render(f"f:{f_str}", True, text_color)
            g_text = font.render(f"g:{g_str}", True, text_color)
            h_text = font.render(f"h:{h_str}", True, text_color)

            # position relative to the cell 
            surface.blit(f_text, (rect[0] + 5, rect[1] + 5))
            surface.blit(g_text, (rect[0] + 5, rect[1] + self.size - 20))
            surface.blit(h_text, (rect[0] + self.size - 35, rect[1] + self.size - 20))

        """
        test_surface = font.render("TEST", True, (0,0,0))
        surface.blit(test_surface, (rect[0] + 5, rect[1] + 5))
        """
            

    
    def reset_all(self, default_terrain):
        """Clears search state data, start/end state and resets terrain."""
        self.reset_search_states()
        self.terrain = default_terrain 
        self.is_start = False 
        self.is_end = False   


    def reset_search_states(self):
        """Clears search data but keeps terrain."""
        self.visited = False 
        self.closed = False 
        self.path = False 
        self.parent = None 

        # Reset A* value if using them 
        self.g = float('inf')
        self.f = 0
        self.h = 0 