from enum import IntEnum

FPS = 60

# Walkable Surfaces 
class TERRAIN_TYPES(IntEnum): 
    GRASS = 0
    SAND = 1
    WATER = 2


# UI/Status Indicators
class UI_COLORS(IntEnum):
    START = 100
    END = 101 
    VISITED = 102
    CLOSED = 103
    PATH = 104
    GRID_LINE = 105


# Use enum members as keys
TERRAIN_COLORS = {
    # Walkable Terrains (muted background tones)
    TERRAIN_TYPES.GRASS: (119, 158, 133),   # soft sage green 
    TERRAIN_TYPES.SAND:  (236, 217, 198),   # pale sand/Tan
    TERRAIN_TYPES.WATER: (162, 192, 201),   # dusty blue  
   

    # UI Overlays (High-Contrast "Action" Colors)
    UI_COLORS.START:     ( 46, 204, 113),   # Emerald (Go) 
    UI_COLORS.END:       (231,  76,  60),   # Alizarin Red (Stop)
    UI_COLORS.VISITED:   (241, 196,  15),   # Sunflower Yellow (Scanning)
    UI_COLORS.CLOSED:    (149, 165, 166),   # Asbestos Gray (Done)
    UI_COLORS.PATH:      (155,  89, 182),   # Amethyst Purple (the result)
    UI_COLORS.GRID_LINE: ( 44,  62,  80),   # Dark Midnight Blue
}

TERRAIN_NAMES = {
    TERRAIN_TYPES.GRASS: "Grass",
    TERRAIN_TYPES.SAND:  "Sand",
    TERRAIN_TYPES.WATER: "Water",
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