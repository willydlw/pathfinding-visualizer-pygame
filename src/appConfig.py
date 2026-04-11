from dataclasses import dataclass 

@dataclass (frozen=True)
class AppConfig:
    # Logic Constants 
    DEFAULT_GRID_SIZE: int = 8
    MAX_GRID_SIZE: int = 256 

    # Sidebar Sizes (used by UI_Layout)
    SIDEBAR_WIDTH: int = 400 
    WIDGET_HEIGHT: int = 35 
    CHECKBOX_SIZE: int = 25
    ROW_SPACING:   int = 50 
    UI_START_ROW:  int = 20


    # Grid 
    GRID_WIDTH: int = 768 
    GRID_PADDING: int = 20    # space around the grid 


    # Application Speed
    FPS: int = 60

    # Visual Constants (Colors)
    COLOR_BACKGROUND: tuple = (225, 225, 225)
    COLOR_SIDEBAR: tuple = (240, 240, 240)

 