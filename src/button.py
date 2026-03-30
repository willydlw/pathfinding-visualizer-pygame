import pygame 


class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text 
        self.pressed = False 
        self.color = color 
        self.font = pygame.font.SysFont('Arial', 20)

    def handle_event(self, event):
        """Returns the button text only once when the mouse button is released over the button."""
        mouse_pos = pygame.mouse.get_pos() 

        # check for mouse press 
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.pressed = True 

        # check for mouse release 
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed:
                self.pressed = False   # reset state
                # Only trigger action if mouse is still over the button on release 
                if self.rect.collidepoint(mouse_pos):
                    return self.text
            
        return None


    def draw(self, surface):
        # Visual feedback: change color if currently pressed 

        draw_color = (150, 150, 150) if self.pressed else self.color 
        pygame.draw.rect(surface, draw_color, self.rect, border_radius=5)

        # Create a surface sized to fit the text string, using preset font size
        # Apply anti-aliasing to smooth out the letter edges 
        # Text will be in the RGB color argument
        text_surf = self.font.render(self.text, True, (255,255,255))

        # Make a rectangle that fits this text perfectly, then move its
        # center to match the button's center
        text_rect = text_surf.get_rect(center=self.rect.center)

        # source to draw: text_surf 
        # destination (where) to draw: text_rect
        surface.blit(text_surf, text_rect)

