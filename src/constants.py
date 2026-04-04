from enum import IntEnum

FPS = 60


class TERRAIN_TYPES(IntEnum): 
    DEFAULT = 0
    NAVY = 1
    GREEN = 2
    BLUE = 3
    GRAY = 4 
    START = 5 
    END = 6
    VISITED = 7
    GRID_LINE = 8
    PATH = 9

# Use enum members as keys
TERRAIN_COLORS = {
    TERRAIN_TYPES.DEFAULT: (225, 225, 225), # light gray / off-white 
    TERRAIN_TYPES.NAVY:  (0, 0, 128),    # navy blue 
    TERRAIN_TYPES.GREEN: (46, 204, 113),  # emerald green 
    TERRAIN_TYPES.BLUE:  (52, 152, 219),  # Peter River Blue 
    TERRAIN_TYPES.GRAY:  (149, 165, 166), # Concrete gray
    TERRAIN_TYPES.START: (241, 196, 15),  # bright yellow 
    TERRAIN_TYPES.END:   (231, 75, 60),   # bright red
    TERRAIN_TYPES.VISITED: (173, 216, 230),  # light blue
    TERRAIN_TYPES.GRID_LINE: (50, 50, 50),      # Lighter gray lines
    TERRAIN_TYPES.PATH: (250, 149, 7)
}
