import pygame 


class Grid:
    def __init__(self, x, y, width, height, rows, cols):
        self.rect = pygame.Rect(x, y, width, height)
        self.rows = rows 
        self.cols = cols 
        self.cell_w = width // cols 
        self.cell_h = width // rows 

        # init 2D list with 0 (Empty)
        self.map = [[0 for _ in range(cols)] for _ in range(rows)]

        self.wall_color = (50, 50, 50)
        self.line_color = (200, 200, 200)

    
    def get_cell_from_pos(self, pos):
        """Translates screen pixel coordinates to (row, col)."""
        x, y = pos 
        if self.rect.collidepoint(pos):
            # subtract grid offset, then divide by cell size 
            col = (x - self.rect.x) // self.cell_w 
            row = (y - self.rect.y) // self.cell_h 
            return row, col 
        return None 
    
    def handle_mouse(self):
        """Allows 'painting' walls by holding the mouse button."""
        if pygame.mouse.get_pressed()[0]:       # left click
            pos = pygame.mouse.get_pos()
            cell = self.get_cell_from_pos(pos)

            if cell:
                row, col = cell 
                self.map[row][col] = 1  # set to wall 
        
        elif pygame.mouse.get_pressed()[2]:     # right click held
            pos = pygame.mouse.get_pos() 
            cell = self.get_cell_from_pos(pos)
            if cell:
                row, col = cell 
                self.map[row][col]

    def draw(self, surface):
        for r in range(self.rows):
            for c in range(self.cols):
                color = (255, 255, 255) # empty 
                if self.map[r][c] == 1:
                    color = self.wall_color 

                # draw the cell 
                cell_rect = pygame.Rect(
                    self.rect.x + c * self.cell_w,
                    self.rect.y + r * self.cell_h,
                    self.cell_w,
                    self.cell_h
                )

                pygame.draw.rect(surface, color, cell_rect)

                # draw grid lines
                pygame.draw.rect(surface, self.line_color, cell_rect, 1)