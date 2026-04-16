import logging 

from .constants import (
    Algorithm_Type,
    Neighbor_Connectivity, 
    Neighbor_Direction
)


logger = logging.getLogger(__name__)


class Algo_Settings:
    def __init__(self):
        self._neighbor_connectivity : Neighbor_Connectivity = Neighbor_Connectivity.get_default()
        self._algorithm : Algorithm_Type = Algorithm_Type.get_default()
        self._randomize_neighbors = False 
        self._neighbor_directions = Neighbor_Direction.get_labels(include_diagonals=False)


    @property 
    def randomize_neighbors(self) -> bool:
        return self._randomize_neighbors 
                
    @randomize_neighbors.setter 
    def randomize_neighbors(self, enabled: bool):
        if not isinstance(enabled, bool):
            raise TypeError(f"randomize_neighbors: {value} (type: {type(value.__name__)}) must be a boolean.")
        self._randomize_neighbors = enabled 
    

    @property 
    def algorithm(self) -> Algorithm_Type:
        """Returns the stored enum member."""
        return self._algorithm
    
    @algorithm.setter 
    def algorithm(self, value):
        """Handles both Enum members and raw integers from the GUI"""
        if isinstance(value, Algorithm_Type):
            self._algorithm = value 
        elif isinstance(value, int):
            # Attempt to convert a raw int to the Enum member 
            try:
                self_algorithm = Algorithm_Type(value)
            except ValueError:
                raise ValueError(f"{value} is not a valid Algorithm_Type index")
        else:
            raise TypeError("algorithm: {value} must be a Algorithm_Type or int.")
    

    @property 
    def neighbor_connectivity(self) -> Neighbor_Connectivity:
        """Returns the stored enum member."""
        return self._neighbor_connectivity 
    
    @neighbor_connectivity.setter 
    def neighbor_connectivity(self, value):
        if isinstance(value, Neighbor_Connectivity):
            self._neighbor_connectivity = value 
        elif isinstance(value, int):
            # Attempt to convert a raw int (like 4 or 8) to the Enum member 
            try:
                self._neighbor_connectivity = Neighbor_Connectivity(value)
            except ValueError:
                raise ValueError(f"{value} is not a valid Neighbor_Connectivity index.")
        else:
            raise TypeError("neighbor_connectivity: {value} must be a Neighbor_Connectivity or int.")

    
    @property
    def neighbor_directions(self) -> list[str]:
        """Returns the current list of direction labels."""
        return self._neighbor_directions
    
    @neighbor_directions.setter 
    def neighbor_directions(self, values: list[str]):
        """Validates and set the direction order exactly as provided by the user."""
        if not isinstance(values, list):
            raise TypeError(f"neighbor_directions must be a list, not {type(values).__name__}")
        
        # Determine allowed labels base on the current connectivity (4 vs 8)
        is_8_way = (self._neighbor_connectivity == Neighbor_Connectivity.CONNECT8)
        allowed_labels = Neighbor_Direction.get_labels(include_diagonals=is_8_way)
        

        # Validate each label
        for label in values:
            if label not in allowed_labels:
                conn_desc = "8-way" if is_8_way else "4-way"
                raise ValueError(f"'{label}' is invalie for {conn_desc} connectivity.")
    
        self._neighbor_directions = list(values)

        
    

