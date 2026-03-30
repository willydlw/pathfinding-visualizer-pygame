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

        self.status_text = "Ready"
        logging.info(f"PathFinderApp initialized")

    
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False 
            
            # pass events to UI 
            result = self.header.handle_events(event)
            if result:
                self._process_ui_action(result)

    def _process_ui_action(self, action):
        """Dispatches actions based on UI returns."""
        logging.info("UI action: {action}")
        self.status_text = action 
        if action == "Map: Clear":
            self.grid.map = [[0 for _ in range(self.grid.cols)] for _ in range(self.grid.rows)]
        else:
            logging.debug(f"TODO: process all UI actions in {_process_ui_action.__name__}")

    def _update(self):
        # Handle continuous mouse painting for walls 
        if not self.header.algo_menu.is_open and not self.header.map_menu.is_open:
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