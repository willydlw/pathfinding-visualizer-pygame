from .constants import Neighbor_Connectivity

class Algo_Settings:
    def __init__(self):
        # Use ': TypeName' to hint the atrribute
        self._neighbor_connectivity : Neighbor_Connectivity = Neighbor_Connectivity.get_default()

    @property 
    def neighbor_connectivity(self) -> Neighbor_Connectivity:
        """The getter: returns the stored enum member."""
        return self._neighbor_connectivity 
    
    @neighbor_connectivity.setter 
    def neighbor_connectivity(self, value):
        """The setter: ensures only valid connectivity values are assigned."""
        if isinstance(value, Neighbor_Connectivity):
            self._neighbor_connectivity = value 
        elif isinstance(value, int):
            # Attempt to convert a raw int (like 4 or 8) to the Enum member 
            try:
                self._neighbor_connectivity = Neighbor_Connectivity(value)
            except ValueError:
                raise ValueError(f"{value} is not a valid Neighbor_Connectivity value.")
        else:
            raise TypeError("neighbor_connectivity: {value} must be a Neighbor_Connectivity enum or int.")