from enum import IntEnum

FPS = 60

# Walkable Surfaces 
class TERRAIN_TYPES(IntEnum): 
    DEFAULT = 0
    NAVY = 1
    GREEN = 2
    BLUE = 3
    GRAY = 4 
  

# UI/Status Indicators
class UI_COLORS(IntEnum):
    START = 100
    END = 101 
    VISITED = 102 
    GRID_LINE = 103 
    PATH = 104 

# Use enum members as keys
TERRAIN_COLORS = {
    # Walkable Terrains 
    TERRAIN_TYPES.DEFAULT: (225, 225, 225), # light gray / off-white 
    TERRAIN_TYPES.NAVY:  (0, 0, 128),    # navy blue 
    TERRAIN_TYPES.GREEN: (46, 204, 113),  # emerald green 
    TERRAIN_TYPES.BLUE:  (52, 152, 219),  # Peter River Blue 
    TERRAIN_TYPES.GRAY:  (149, 165, 166), # Concrete gray

    # UI Overlays 
    UI_COLORS.START: (241, 196, 15),  # bright yellow 
    UI_COLORS.END:   (231, 75, 60),   # bright red
    UI_COLORS.VISITED: (173, 216, 230),  # light blue
    UI_COLORS.GRID_LINE: (50, 50, 50),      # Lighter gray lines
    UI_COLORS.PATH: (250, 149, 7)
}

TERRAIN_NAMES = {
    TERRAIN_TYPES.DEFAULT: "Default",
    TERRAIN_TYPES.NAVY: "Navy",
    TERRAIN_TYPES.GREEN: "Green",
    TERRAIN_TYPES.BLUE: "Blue",
    TERRAIN_TYPES.GRAY: "Gray",
}


class MAP_ACTION_TYPES(IntEnum):
    CREATE = 0
    LOAD = 1
    SAVE = 2 

MAP_ACTION_DICT = {
    MAP_ACTION_TYPES.CREATE: "Create New",
    MAP_ACTION_TYPES.LOAD:   "Load Map",
    MAP_ACTION_TYPES.SAVE:   "Save Map"
}