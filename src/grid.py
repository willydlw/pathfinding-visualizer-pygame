import pygame 
import json 
import os

import logging 

from .constants import TERRAIN_TYPES, TERRAIN_COLORS, UI_COLORS
from .node import Node

logger = logging.getLogger(__name__)

class Grid:

    def __init__(self, x, y, grid_size, num_cells):

        self.rows = num_cells 
        self.cols = num_cells 
        
        self.grid_size = grid_size                  # units: pixels
        self.cell_size = grid_size // num_cells     # units: pixels

        self.rect = pygame.Rect(x, y, self.grid_size, self.grid_size)   # grid rectangle

        
        self.current_brush = TERRAIN_TYPES.GRASS             # default brush color

        self.start_node = None                       
        self.end_node = None 
        
        # init 2D list
        self.map = [[Node(r, c, self.cell_size, TERRAIN_TYPES.GRASS) for c in range(self.cols)] 
                    for r in range(self.rows)
        ]

        logging.info(f"grid_size: {self.grid_size}, rows: {self.rows}, cell_size: {self.cell_size}")
        logging.info(f"Grid init completed.")

    
    def clear(self):
        """Resets the grid map to all DEFAULT (0)."""
        self.map = [
            [Node(r, c, self.cell_size, TERRAIN_TYPES.GRASS) for c in range(self.cols)] 
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
    

    def handle_click_event(self, sidebar):
        """Called only once per mouse click (not held)"""
        pos = pygame.mouse.get_pos() 
        node = self.get_node_from_pos(pos)

        if not node:
            return 
        
        # Handle start placement 
        if sidebar.start_checkbox.is_checked:
            if self.start_node and self.start_node != node:
                self.start_node.is_start = False 
            node.is_start = True 
            node.is_end = False 
            self.start_node = node 
            logging.info(f"Start set to: {node.row}, {node.col}")

        # Handle End Placement 
        elif sidebar.end_checkbox.is_checked:
            if self.end_node and self.end_node != node:
                self.end_node.is_end = False 
            node.is_end = True 
            node.is_start = False 
            self.end_node = node 
            logging.info(f"End set to: {node.row}, {node.col}")
            
    
    def handle_continuous_mouse(self, sidebar):
        """Handles painting terrain/start/end whild mouse is held down."""
        # Left click held: paint terrain or start/end
        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos() 
            node = self.get_node_from_pos(pos)

            if node:
                # Handle start checkbox
                if sidebar.start_checkbox.is_checked:
                    # if we are click a new node, reset the old start node 
                    if self.start_node and self.start_node != node:
                        self.start_node.is_start = False 
                    node.is_start = True 
                    node.is_end = False 
                    self.start_node = node 
                    logging.info(f"Start moved to: {node.row}, {node.col}")

                # Handle end checkbox
                elif sidebar.end_checkbox.is_checked:
                    if self.end_node and self.end_node != node:
                        self.end_node.is_end = False 
                    node.is_start = False
                    node.is_end = True 
                    self.end_node = node 
                    logging.info(f"End moved to: {node.row}, {node.col}")

                # Handle regular painting
                else:
                    # Normal terrain painting (only if node isn't currently start/end)
                    if not node.is_start and not node.is_end:
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

    def draw(self, surface, font):
        # Draw the colored cell blocks
        for row in self.map:
             for node in row:
                node.draw(surface, font, self.rect.x, self.rect.y)

        # Draw grid lines (square grid: rows equal cols)
        for i in range(self.rows + 1):
                offset = i * self.cell_size

                #vertical lines
                pygame.draw.line(surface, TERRAIN_COLORS[UI_COLORS.GRID_LINE], 
                                 (self.rect.x + offset, self.rect.y), 
                                 (self.rect.x + offset, self.rect.y + self.grid_size)
                                )
                
                # horizontal lines
                pygame.draw.line(surface, TERRAIN_COLORS[UI_COLORS.GRID_LINE], 
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

            # Update the row, col counts 
            self.rows = data["rows"]
            self.cols = data["cols"]

            # recalculate cell size
            self.cell_size = self.grid_size // self.rows 

            # build a new 2d map with the stored terrain types
            new_map = []

            for r in range(self.rows):
                row = []
                for c in range(self.cols):
                    terrain_val = data["cells"][r][c]
                    #New nodes start with all UI flags (visited/path/start/end) as False
                    row.append(Node(r, c, self.cell_size, terrain_val))
                new_map.append(row)

            # replace the old map with the new map 
            self.map = new_map
            
            # restore Start Node with reference and flag
            self.start_node = None 
            if data.get("start_pos"):
                r, c = data["start_pos"]
                # Bounds check: only assign if coordinates exist in the new grid
                if r < self.rows and c < self.cols:
                    self.start_node = self.map[r][c]
                    self.start_node.is_start = True 

            # Restore the end node reference and flag 
            self.end_node = None 
            if data.get("end_pos"):
                r, c = data["end_pos"]
                if r < self.rows and c < self.cols:
                    self.end_node = self.map[r][c]
                    self.end_node.is_end = True 
                
            logging.info(f"Map loaded from {file_path}")

        except Exception as e:
            logger.error(f"Failed to load map: {e}")
    

    def save_to_file(self, file_path):
        # Ensure the file ends in .json
        if not file_path.lower().endswith('.json'):
            file_path += '.json'

        grid_data = {
            "rows": self.rows,
            "cols": self.cols,
            # Save start/end as coordinates
            "start_pos": (self.start_node.row, self.start_node.col) if self.start_node else None,
            "end_pos": (self.end_node.row, self.end_node.col) if self.end_node else None,
            # Save only the underlying terrain for each node 
            "cells": [[node.terrain for node in row] for row in self.map]
        }

        try:
            dir_name = os.path.dirname(file_path)
            if dir_name: # only create if there's actually a directory path
                # Create directory if it doesn't exist (e.g., /maps/)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(grid_data, f) 
            logger.info(f"Map successfully saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save map: {e}")


    def reset_search_data(self):
        """Clears search visuals (visited, path, closed, costs, parents) but keeps terrain."""
        for row in self.map:
            for node in row:
                node.reset_search_states()
        