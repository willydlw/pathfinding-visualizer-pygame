import pygame 

class Node:
    def __init__(self, row, col, size, terrain):
        self.row = row 
        self.col = col 
        self.x = col * size 
        self.y = row * size 
        self.size = size 

        self.terrain = terrain 
        self.visited = False 
        self.parent = None 

        # For A* later 
        self.g = float('inf')
        self.h = 0 
        self.f = 0 

    def draw(self, surface, x_offset, y_offset, color):
        rect = (self.x + x_offset, self.y + y_offset, self.size, self.size)
        pygame.draw.rect(surface, color, rect)