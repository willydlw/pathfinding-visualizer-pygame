import pygame 
import logging 

from .header import Header 
from .grid import Grid 
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS 


logger = logging.getLogger(__name__)


class PathFinderApp:
    def __init__(self):
        pygame.init() 
        self.screen_width = SCREEN_WIDTH 
        self.screen_height = SCREEN_HEIGHT 
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Algorithm Visualizer")

        self.clock = pygame.time.Clock() 
        self.running = True 

        # UI Components 
        self.header = Header(self.screen_width, 50)
        self.grid = Grid(0, 50, self.screen_width, self.screen_height - 50, 25, 40)

        self.mouse_captured_by_ui = False    # flag to track mouse press 

        self.status_text = "Ready"
        logging.info(f"PathFinderApp initialized")

    
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False 

            # Track if a new press starts on the header
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[1] <= self.header.rect.height:
                    self.mouse_captured_by_ui = True 
                else:
                    self.mouse_captured_by_ui = False 

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # escape key press should close any open menus 
                    self.header.algo_menu.is_open = False 
                    self.header.map_menu.is_open = False 
                    logging.info("Menus closed via Escape key")
            
            # pass events to UI 
            result = self.header.handle_events(event)
            if result:
                logging.info(f"result: {result}")
                self._process_ui_action(result)

    def _process_ui_action(self, action):
        """Dispatches actions based on UI returns."""
        logging.info(f"UI action: {action}")
        self.status_text = action

        if action == "Clear":
            self.grid.map = [[0 for _ in range(self.grid.cols)] for _ in range(self.grid.rows)]
            logging.info("Grid cleared via UI")
        else:
            logging.debug(f"TODO: process all UI actions in {self._process_ui_action.__name__}")

    def _update(self):

        # Check if any menu is currently open 
        menu_is_open = self.header.algo_menu.is_open or self.header.map_menu.is_open

        # Only allow grid interaction if
        #   - No menu is open 
        #   - The mouse button didn't start its press on the header/menu 
        #   - The mouse is physically over the grid 
        mouse_pos = pygame.mouse.get_pos()

        if not menu_is_open and not self.mouse_captured_by_ui:
            if mouse_pos[1] > self.header.rect.height:
                self.grid.handle_mouse()
    

    def _draw(self):
        self.screen.fill((30, 30, 30))
        self.grid.draw(self.screen)
        self.header.draw(self.screen)

        # Optional: draw status bar text at the very bottom 
        # TODO: add small footer here later 

        pygame.display.flip() 

    def run(self):
        """The main application loop."""
        while self.running:
            self._handle_events() 
            self._update()
            self._draw() 
            self.clock.tick(FPS)