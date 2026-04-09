from enum import IntEnum, StrEnum

FPS = 60

# Walkable Surfaces 
class Terrain_Type(IntEnum): 
    GRASS = 0
    SAND = 1
    WATER = 2

    @property 
    def label(self):
        return self.name.replace("_", " ").capitalize()
    
    def __str__(self):
        return self.name.capitalize()
    


# UI/Status Indicators
class UI_COLORS(IntEnum):
    START = 100
    END = 101 
    VISITED = 102
    CLOSED = 103
    PATH = 104
    GRID_LINE = 105

    @property 
    def label(self):
        return self.name.replace("_", " ").capitalize()
    
    def __str__(self):
        return self.name.capitalize()
    


# Use enum members as keys
TERRAIN_COLORS = {
    # Walkable Terrains (muted background tones)
    Terrain_Type.GRASS: (119, 158, 133),   # soft sage green 
    Terrain_Type.SAND:  (236, 217, 198),   # pale sand/Tan
    Terrain_Type.WATER: (162, 192, 201),   # dusty blue  
   

    # UI Overlays (High-Contrast "Action" Colors)
    UI_COLORS.START:     ( 46, 204, 113),   # Emerald (Go) 
    UI_COLORS.END:       (231,  76,  60),   # Alizarin Red (Stop)
    UI_COLORS.VISITED:   (241, 196,  15),   # Sunflower Yellow (Scanning)
    UI_COLORS.CLOSED:    (149, 165, 166),   # Asbestos Gray (Done)
    UI_COLORS.PATH:      (155,  89, 182),   # Amethyst Purple (the result)
    UI_COLORS.GRID_LINE: ( 44,  62,  80),   # Dark Midnight Blue
}


# Algorithms 
class Algorithm_Type(IntEnum):
    BFS = 0
    DFS = 1
    ASTAR = 2 

    @property 
    def label(self):
        return self.name.replace("_", " ").capitalize()
    
    def __str__(self):
        return self.name.capitalize()
    
    # print(Algo.BFS.name) # "BFS"


# Animation 
class Animation_Mode(IntEnum):
    ANIMATED = 0
    INSTANT = 1
    SINGLE_STEP = 2

    @property 
    def label(self):
        # Converts "SINGLE_STEP" -> "Single Step"
        return self.name.replace("_", " ").capitalize()
    
    def __str__(self):
        return self.name.capitalize() 
    
    # Animation_Mode.SINGLE_STEP.name "SINGLE_STEP"
    # Animation_Mode.SINGLE_STEP.label "Single Step"
    # Animation_Mode.SINGLE_STEP.value is 3 




class SPEED_OPTIONS(IntEnum):
    ANIM_1x = 1
    ANIM_2X = 2
    ANIM_4X = 4 
    ANIM_8X = 8
    ANIM_16x = 16
    ANIM_32x = 32

SPEED_OPTION_NAMES = {
    SPEED_OPTIONS.ANIM_1x: "1x",
    SPEED_OPTIONS.ANIM_2X: "2x",
    SPEED_OPTIONS.ANIM_4X: "4x",
    SPEED_OPTIONS.ANIM_8X: "8x",
    SPEED_OPTIONS.ANIM_16x: "16x",
    SPEED_OPTIONS.ANIM_32x: "32x",
}


# Mapping 
class Map_Actions(IntEnum):
    CREATE_MAP = 1
    LOAD_MAP = 2
    SAVE_MAP = 3 

    @property 
    def label(self):
        # Converts "SINGLE_STEP" -> "Single Step"
        return self.name.replace("_", " ").capitalize()
    
    def __str__(self):
        return self.name.capitalize() 



# Path Costs 
class PATH_COST(IntEnum):
    CARDINAL = 10
    DIAGONAL = 14
