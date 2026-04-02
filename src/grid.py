import pygame 
import json 

import logging 

from .constants import TERRAIN_TYPES, TERRAIN_COLORS
from .node import Node

logger = logging.getLogger(__name__)

class Grid:

   


    def __init__(self, x, y, grid_size, num_cells):

        self.rows = num_cells 
        self.cols = num_cells 
        
        self.grid_size = grid_size                  # units: pixels
        self.cell_size = grid_size // num_cells     # units: pixels

        self.rect = pygame.Rect(x, y, self.grid_size, self.grid_size)   # grid rectangle

        
        self.current_brush = TERRAIN_TYPES.GREEN             # default brush color

        self.start_node = None                       
        self.end_node = None 
        
        # init 2D list
        self.map = [[Node(r, c, self.cell_size, TERRAIN_TYPES.DEFAULT) for c in range(self.cols)] 
                    for r in range(self.rows)
        ]

        logging.info(f"grid_size: {self.grid_size}, rows: {self.rows}, cell_size: {self.cell_size}")
        logging.info(f"Grid init completed.")

    
    def clear(self):
        """Resets the grid map to all DEFAULT (0)."""
        self.map = [
            [Node(r, c, self.cell_size, TERRAIN_TYPES.DEFAULT) for c in range(self.cols)] 
            for r in range(self.rows)
        ]
        self.start_node = None 
        self.end_node = None 
        logger.info("Grid cleared!")

    
    def get_node_from_pos(self, pos):
        """Returns the Node object at the give pixel coordinates, or None."""
        coords = self.get_pos(pos) 
        if coords:
            row, col = coords 
            return self.map[row][col]
        return None 
    

    def get_pos(self, pos):
        """Translates screen pixel coordinates to (row, col)."""
        x, y = pos 
        if self.rect.collidepoint(pos):
            # subtract grid offset, then divide by cell size 
            col = (x - self.rect.x) // self.cell_size
            row = (y - self.rect.y) // self.cell_size
            return row, col 
        return None 
    
    def handle_continuous_mouse(self):
        """Handles painting terrain/start/end whild mouse is held down."""
        mouse_pressed = pygame.mouse.get_pressed() 

        # Left click held: paint terrain or start/end
        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos() 
            node = self.get_node_from_pos(pos)

            if node:
                if self.current_brush == TERRAIN_TYPES.START:
                    if self.start_node: self.start_node.is_start = False 
                    node.is_start = True 
                    self.start_node = node 
                elif self.current_brush == TERRAIN_TYPES.END:
                    if self.end_node: self.end_node.is_end = False 
                    node.is_end = True 
                    self.end_node = node 
                else:
                    node.terrain = self.current_brush
        
    
    def handle_mouse_event(self, event):
        """Handles one-time clicks, specifically for right-click release"""
        # Right click: Erase (Wait for button UP)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            pos = pygame.mouse.get_pos() 
            node = self.get_node_from_pos(pos)
            if node:
                if node.is_start:
                    node.is_start = False 
                    self.start_node = None 
                elif node.is_end:
                    node.is_end = False 
                    self.end_node = None 
                else:
                    node.terrain = TERRAIN_TYPES.DEFAULT 

    def draw(self, surface):
        # Draw the colored cell blocks
        for row in self.map:
             for node in row:
                node.draw(surface, self.rect.x, self.rect.y)

        # Draw grid lines (square grid: rows equal cols)
        for i in range(self.rows + 1):
                offset = i * self.cell_size

                #vertical lines
                pygame.draw.line(surface, TERRAIN_COLORS[TERRAIN_TYPES.GRID_LINE], 
                                 (self.rect.x + offset, self.rect.y), 
                                 (self.rect.x + offset, self.rect.y + self.grid_size)
                                )
                
                # horizontal lines
                pygame.draw.line(surface, TERRAIN_COLORS[TERRAIN_TYPES.GRID_LINE], 
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
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            self.rows = data["rows"]
            self.cols = data["cols"]
            self.cell_size = self.grid_size // self.rows 

            # rebuild the 2d map with the stored terrain types
            self.map = []
            for r in range(self.rows):
                row = []
                for c in range(self.cols):
                    terrain_val = data["cells"][r][c]
                    row.append(Node(r, c, self.cell_size, terrain_val))
                self.map.append(row)
            
            # Restore the start node reference and flag
            if data["start_pos"]:
                r, c = data["start_pos"]
                self.start_node = self.map[r][c]
                self.start_node.is_start = True 
            else:
                self.start_node = None 

            # Restore the end node reference and flag 
            if data["end_pos"]:
                r, c = data["end_pos"]
                self.end_node = self.map[r][c]
                self.end_node.is_end = True 
            else:
                self.end_node = None 

            logging.info(f"Map loaded from {file_path}")

        except Exception as e:
            logger.error(f"Failed to load map: {e}")
    

    def save_to_file(self, file_path):
        grid_data = {
            "rows": self.rows,
            "cols": self.cols,
            # Save start/end as coordinates
            "start_pos": (self.start_node.r, self.start_node.c) if self.start_node else None,
            "end_pos": (self.end_node.r, self.end_node.c) if self.end_node else None,
            # Save only the underlying terrain for each node 
            "cells": [[node.terrain for node in row] for row in self.map]
        }

        try:
            with open(file_path, 'w') as f:
                json.dump(grid_data, f) 
            logger.info(f"Map successfully saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save map: {e}")