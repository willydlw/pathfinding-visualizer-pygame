from enum import Enum, IntEnum, unique

# Path Costs 
class PATH_COST(IntEnum):
    CARDINAL = 10
    DIAGONAL = 14



# UI Base Class 
class UIEnum(IntEnum):
    @classmethod 
    def get_labels(cls):
        """Default behavior: generate labels from member names."""
        return {member: member.name.replace("_", " ").title() for member in cls}
    
    @classmethod 
    def get_default(cls):
        """Returns the first member as default. can be overridden."""
        return list(cls)[0]

    @property  
    def label(self):
        """Gets the string label for the current enum instance."""
        return self.__class__.get_labels()[self]
    
    @classmethod 
    def options_list(cls):
        """Returns list of strings."""
        return list(cls.get_labels().values())
    
    @classmethod 
    def from_label(cls, label_text):
        """Converts string back to Enum number."""
        for member, label in cls.get_labels().items():
            if label.lower() == label_text.lower():
                return member 
        return cls.get_default() 
    
    def __str__(self):
        return self.label 



@unique
class Algorithm_Type(UIEnum):
    BFS = 0
    DFS = 1
    ASTAR = 2
    #WEIGHTED_ASTAR = 3
    #UCS = 4                 # uniform cost search 
    #GREEDY_BEST_FIRST = 5


    @classmethod 
    def get_labels(cls):
        return{
            cls.BFS: 'BFS',
            cls.DFS: 'DFS',
            cls.ASTAR: 'A*',
            #cls.WEIGHTED_ASTAR: 'WA*',
            #cls.UCS: 'UCS',
            #cls.GREEDY_BEST_FIRST: "GBFS"
        }


@unique
class Animation_Mode(UIEnum):
    ANIMATED = 0
    INSTANT =  1
    SINGLE_STEP = 2
    

@unique
class Draw_State(UIEnum):
    START   = 0
    END     = 1
    VISITED = 2
    CLOSED  = 3
    PATH    = 4
    GRID_LINE = 5
    

    @property 
    def color(self):
        """Returns the (r, g, b) tuple associated wiht the state."""
        return{
            self.__class__.START:     ( 46, 204, 113),   # Emerald (Go) 
            self.__class__.END:       (231,  76,  60),   # Alizarin Red (Stop)
            self.__class__.VISITED:   (241, 196,  15),   # Sunflower Yellow (Scanning)
            self.__class__.CLOSED:    (149, 165, 166),   # Asbestos Gray (Done)
            self.__class__.PATH:      (155,  89, 182),   # Amethyst Purple (the result)
            self.__class__.GRID_LINE: ( 44,  62,  80),   # Dark Midnight Blue
        }.get(self, (255,255,255))             # Default white
  

@unique
class Map_Actions(UIEnum):
    EDIT_MAP = 0
    LOAD_MAP = 1
    SAVE_MAP = 2

    
    @property 
    def window_title(self):
        """Returns a standardized window title for each action."""
        titles = {
            Map_Actions.SAVE_MAP: "Save Map (Type name in path bar above)",
            Map_Actions.LOAD_MAP: "Load Map",
            Map_Actions.EDIT_MAP: "Edit Map"
        }
        return titles.get(self, self.label)


@unique
class Map_Dimension(UIEnum):
    MD8 =  8
    MD16 = 16
    MD32 = 32
    MD64 = 64
    MD128 = 128 

    @classmethod
    def get_labels(cls):
        """Overrides base behavior to return '64 x 64' format."""
        return {member: f"{member.value} x {member.value}" for member in cls}
    
    @classmethod
    def get_default(cls):
        return cls.MD8
    


@unique 
class Neighbor_Connectivity(UIEnum):
    CONNECT4 = 4
    CONNECT8 = 8 

    @classmethod 
    def get_labels(cls):
        return{
            cls.CONNECT4: '4 Cardinal (N, E, S, W)',
            cls.CONNECT8: '8 (Cardinal + Diagonals)'
        }



class Neighbor_Direction(Enum):
    # Cardinal Directions
    NORTH = (-1,  0)        # (row, col) -1 is row above, 0 is same column
    EAST =  ( 0,  1)
    SOUTH = ( 1,  0)
    WEST =  ( 0, -1)

    # Ordinal (Diagonal) Directions 
    NORTH_EAST = (-1,  1)
    NORTH_WEST = (-1, -1)
    SOUTH_EAST = ( 1,  1)
    SOUTH_WEST = ( 1, -1)
    

    @property 
    def label(self) -> str:
        """Returns a GUI-friendly string like 'North West'"""
        return self.name.replace("_", " ").title()
    
    @property
    def vector(self) -> tuple:
        """
        Alias for .value for clarity in pathfinding code.
        Returns the (dr, dc) tuple
        """
        return self.value 
    
    
    @classmethod
    def get_natural_order(cls):    
        """Standard clockwise rotation for UI or logic."""
        ordered = [
            cls.NORTH, cls.NORTH_EAST, 
            cls.EAST,  cls.SOUTH_EAST, 
            cls.SOUTH, cls.SOUTH_WEST, 
            cls.WEST,  cls.NORTH_WEST
        ]
        return [m.label for m in ordered]

    @classmethod
    def get_diagonal_labels(cls):
        """Returns the list of Diagonal order labels."""
        diagonals = [cls.NORTH_EAST, cls.SOUTH_EAST, cls.SOUTH_WEST, cls.NORTH_WEST]
        return [m.label for m in diagonals]
    
    @classmethod 
    def get_labels(cls, include_diagonals=False):
        """Returns labels. If include_diagonals is False, returns only Cardinals."""
        if include_diagonals:
            return Neighbor_Direction.get_natural_order()
        cardinals = [cls.NORTH, cls.EAST, cls.SOUTH, cls.WEST]
        return [m.label for m in cardinals]
       
    @classmethod 
    def from_label(cls, label_text: str):
        for member in cls:
            if member.label.lower() == label_text.lower():
                return member 
        return None 
   
    def __str__(self):
        return self.label 
    
    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}>, <{self.value}>"
    
    @classmethod 
    def sort_labels(cls, label_list):
        """Sorts a list of labels based on the natural order."""
        order = cls.get_natural_order() 
        label_list.sort(key=lambda x: order.index(x) if x in order else 999)
        return label_list
       
    


@unique
class Neighbor_Order(IntEnum):
    RANDOM = 0
    CLOCKWISE = 1
    COUNTER_CLOCKWISE = 2
    
    
    @property 
    def label(self):
        return self.name.replace("_", " ").title()
    
    def __str__(self):
        return self.label 
    
    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}>"

    @classmethod 
    def list_labels(cls):
        #Returns a list of all human-readable labels.
        return [member.label for member in cls]
    
    @classmethod 
    def from_label(cls, label_text):
        #Finds an enum member by its label string (case-insensitive).
        for member in cls:
            if member.label.lower() == label_text.lower():
                return member 
        raise ValueError(f"Invalid label: {label_text}")

 



@unique 
class Speed_Options(UIEnum):
    ANIM_1x = 1
    ANIM_2X = 2
    ANIM_4X = 4 
    ANIM_8X = 8
    ANIM_16x = 16
    ANIM_32x = 32

    @classmethod 
    def get_labels(cls):
        """Overrides the base to return '1x, '2x, etc. """
        return {member: f"{member.value}x" for member in cls}
    
    @classmethod
    def get_default(cls):
        return cls.ANIM_1x 

     

@unique
class Terrain_Type(UIEnum): 
    GRASS = 0
    SAND = 1
    WATER = 2

    @property
    def color(self):
        """Returns the (r, g, b) tuple associated with the state."""
        return {
            self.__class__.GRASS:  (119, 158, 133),   # soft sage green 
            self.__class__.SAND:   (236, 217, 198),   # pale sand/Tan
            self.__class__.WATER:  (162, 192, 201),   # dusty blue  
        }.get(self, (255, 255, 255))        # Default white
    
    @classmethod 
    def default(cls):
        return cls.GRASS 


    @property 
    def cost(self) -> float:
        """Returns the movement penalty for this terrain."""
        return {
            self.__class__.GRASS: 1.0,
            self.__class__.SAND:  2.5,
            self.__class__.WATER: 5.0,
        }.get(self, 1.0)