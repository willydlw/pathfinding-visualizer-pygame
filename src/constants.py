from enum import IntEnum, unique, auto 
from functools import lru_cache 


# Path Costs 
class PATH_COST(IntEnum):
    CARDINAL = 10
    DIAGONAL = 14


# Notes: 
# Using auto() for values to let python handle the numbering 
# when specific integer values don't matter to program logic.
# Prevents manual numbering errors.

# @unique Decorator ensures no two members have the same value.


@unique
class Algorithm_Type(IntEnum):
    BFS = auto()
    DFS = auto()
    ASTAR = auto()

    @property 
    def label(self):
        # Converts "SINGLE_STEP" -> "Single Step"
        return self.name.replace("_", " ").title()
    
    def __str__(self):
        return self.label 
    
    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}>"

    @classmethod 
    def list_labels(cls):
        """Returns a list of all human-readable labels."""
        return [member.label for member in cls]
    
    @classmethod 
    def from_label(cls, label_text):
        """Finds an enum member by its label string (case-insensitive)."""
        for member in cls:
            if member.label.lower() == label_text.lower():
                return member 
        raise ValueError(f"Invalid label: {label_text}")
    
    # @lru_cache decorator avoids rebuilding the dictionary every time method
    # is called. The same dictionary object is returned on subsequent calls.
    @classmethod 
    @lru_cache(maxsize=None)
    def get_lookup(cls):
        """Creates a mapping: {"BFS" : Algorithm_Type.BFS, ...}"""
        return {m.label: m for m in cls}
    


@unique
class Animation_Mode(IntEnum):
    ANIMATED = auto()
    INSTANT = auto()
    SINGLE_STEP = auto()

    @property 
    def label(self):
        # Converts "SINGLE_STEP" -> "Single Step"
        return self.name.replace("_", " ").title()
    
    def __str__(self):
        return self.label 
    
    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}>"

    @classmethod 
    def list_labels(cls):
        """Returns a list of all human-readable labels."""
        return [member.label for member in cls]
    
    @classmethod 
    def from_label(cls, label_text):
        """Finds an enum member by its label string (case-insensitive)."""
        for member in cls:
            if member.label.lower() == label_text.lower():
                return member 
        raise ValueError(f"Invalid label: {label_text}")
    
    # @lru_cache decorator avoids rebuilding the dictionary every time method
    # is called. The same dictionary object is returned on subsequent calls.
    @classmethod 
    @lru_cache(maxsize=None)
    def get_lookup(cls):
        """Creates a mapping: {"Single Step" : Animation_Mode.SINGLE_STEP, ...}"""
        return {m.label: m for m in cls}
    


@unique
class Draw_State(IntEnum):
    START   = auto()
    END     = auto()
    VISITED = auto()
    CLOSED  = auto()
    PATH    = auto()
    GRID_LINE = auto()
    

    @property 
    def color(self):
        """Returns the (r, g, b) tuple associated wiht the state."""
        return{
            self.START:     ( 46, 204, 113),   # Emerald (Go) 
            self.END:       (231,  76,  60),   # Alizarin Red (Stop)
            self.VISITED:   (241, 196,  15),   # Sunflower Yellow (Scanning)
            self.CLOSED:    (149, 165, 166),   # Asbestos Gray (Done)
            self.PATH:      (155,  89, 182),   # Amethyst Purple (the result)
            self.GRID_LINE: ( 44,  62,  80),   # Dark Midnight Blue
        }.get(self, (255,255,255))             # Default white
  
    @property 
    def label(self):
        return self.name.replace("_", " ").title()
    
    def __str__(self):
        return self.label 
    
    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}>"

    @classmethod 
    def list_labels(cls):
        """Returns a list of all human-readable labels."""
        return [member.label for member in cls]
    
    @classmethod 
    def from_label(cls, label_text):
        """Finds an enum member by its label string (case-insensitive)."""
        for member in cls:
            if member.label.lower() == label_text.lower():
                return member 
        raise ValueError(f"Invalid label: {label_text}")
    
    # @lru_cache decorator avoids rebuilding the dictionary every time method
    # is called. The same dictionary object is returned on subsequent calls.
    @classmethod 
    @lru_cache(maxsize=None)
    def get_lookup(cls):
        """Creates a mapping: {"Start" : Draw_State.START, ...}"""
        return {m.label: m for m in cls}


@unique
class Map_Actions(IntEnum):
    CREATE_MAP = auto()
    LOAD_MAP = auto()
    SAVE_MAP = auto()

    @property 
    def label(self):
        return self.name.replace("_", " ").title()
    
    def __str__(self):
        return self.label 
    
    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}>"

    @classmethod 
    def list_labels(cls):
        """Returns a list of all human-readable labels."""
        return [member.label for member in cls]
    
    @classmethod 
    def from_label(cls, label_text):
        """Finds an enum member by its label string (case-insensitive)."""
        for member in cls:
            if member.label.lower() == label_text.lower():
                return member 
        raise ValueError(f"Invalid label: {label_text}")
    
    # @lru_cache decorator avoids rebuilding the dictionary every time method
    # is called. The same dictionary object is returned on subsequent calls.
    @classmethod 
    @lru_cache(maxsize=None)
    def get_lookup(cls):
        """Creates a mapping: {"Create Map" : Map_Actions.CREATE_MAP, ...}"""
        return {m.label: m for m in cls}



@unique 
class Speed_Options(IntEnum):
    ANIM_1x = 1
    ANIM_2X = 2
    ANIM_4X = 4 
    ANIM_8X = 8
    ANIM_16x = 16
    ANIM_32x = 32

    @property 
    def label(self):
        """Returns the human-readable strine like '1x', '2x', etc."""
        return f"(self.value)x"

    def __str__(self):
        return self.label 
    
    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}: {self.value}>"

    @classmethod 
    @lru_cache(maxsize=None)
    def get_lookup(cls):
        """Creates a mapping: {"1x" : Speed_Options.ANIM_1x, ...}"""
        return {m.label: m for m in cls}
     

@unique
class Terrain_Type(IntEnum): 
    GRASS = 0
    SAND = 1
    WATER = 2

    @property
    def color(self):
        """Returns the (r, g, b) tuple associated with the state."""
        return {
            self.GRASS:  (119, 158, 133),   # soft sage green 
            self.SAND:   (236, 217, 198),   # pale sand/Tan
            self.WATER:  (162, 192, 201),   # dusty blue  
        }.get(self, (255, 255, 255))        # Default white
    

    @property 
    def label(self):
        return self.name.replace("_", " ").title()
    
    def __str__(self):
        return self.label 
    
    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}>"

    @classmethod 
    def list_labels(cls):
        """Returns a list of all human-readable labels."""
        return [member.label for member in cls]
    
    @classmethod 
    def from_label(cls, label_text):
        """Finds an enum member by its label string (case-insensitive)."""
        for member in cls:
            if member.label.lower() == label_text.lower():
                return member 
        raise ValueError(f"Invalid label: {label_text}")
    
    # @lru_cache decorator avoids rebuilding the dictionary every time method
    # is called. The same dictionary object is returned on subsequent calls.
    @classmethod 
    @lru_cache(maxsize=None)
    def get_lookup(cls):
        """Creates a mapping: {"Grass" : Terrain_Type.GRASS, ...}"""
        return {m.label: m for m in cls}
    
    @classmethod 
    def list_labels(cls):
        """Returns ['1x', '2x', '4x', '8x', '16x', '32x']"""
        return [m.label for m in cls]  
