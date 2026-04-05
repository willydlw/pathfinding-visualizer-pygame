import pygame

from .constants import TERRAIN_COLORS, TERRAIN_TYPES, UI_COLORS

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
      
    

        # For A* later 
        self.g = float('inf')
        self.h = 0 
        self.f = 0 

    def __eq__(self, other):
        # Type check: Ensure the other object is the same class 
        if not isinstance(other, Node):
            return NotImplemented
        
        # two objects are equal if they have same row, col positions
        return self.row == other.row and self.col == other.col
    
    def __str__(self):
        return (
            f"[row, col]: ({self.row}, {self.col}), [x,y]: ({self.x}, {self.y}), "
            f"terrain: {self.terrain}, visited: {self.visited}"
        )

    def draw(self, surface, x_offset, y_offset):
        
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


    def reset_state(self):
        """Clears search data but keeps terrain."""
        self.visited = False 
        self.closed = False 
        self.path = False 
        self.parent = None 