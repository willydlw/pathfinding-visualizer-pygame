"""
If you are using pytest, just navigate to the project_root in your terminal and run: pytest
"""

import pytest
from myapp.ui.ui_types import (
    UIEnum, 
    Neighbor_Connectivity,
    Terrain_Type 
)

import pytest
from myapp.ui.ui_types import UIEnum, Neighbor_Connectivity

# --- Mock classes for testing base functionality ---

class MockEnum(UIEnum):
    FIRST_OPTION = 1
    SECOND_OPTION = 2

class CustomDefaultEnum(UIEnum):
    ALPHA = 1
    BETA = 2
    
    @classmethod
    def get_default(cls):
        return cls.BETA

# --- Tests ---

def test_uienum_auto_labels():
    """Verify underscores are converted to Title Case spaces."""
    assert MockEnum.FIRST_OPTION.label == "First Option"
    assert MockEnum.SECOND_OPTION.label == "Second Option"

def test_uienum_str_method():
    """Ensure str() returns the clean label for UI display."""
    assert str(MockEnum.FIRST_OPTION) == "First Option"

def test_uienum_options_list():
    """Ensure the list of strings is generated in the correct order."""
    assert MockEnum.options_list() == ["First Option", "Second Option"]

def test_uienum_from_label_success():
    """Test valid and case-insensitive label lookups."""
    assert MockEnum.from_label("Second Option") == MockEnum.SECOND_OPTION
    assert MockEnum.from_label("first option") == MockEnum.FIRST_OPTION

def test_uienum_from_label_fallback():
    """Test that invalid input returns the defined default."""
    # Standard default (first item)
    assert MockEnum.from_label("Non-existent") == MockEnum.FIRST_OPTION
    assert MockEnum.from_label("") == MockEnum.FIRST_OPTION
    
    # Custom overridden default
    assert CustomDefaultEnum.from_label("Invalid") == CustomDefaultEnum.BETA

def test_uienum_get_default():
    """Verify the default member selection logic."""
    assert MockEnum.get_default() == MockEnum.FIRST_OPTION
    assert CustomDefaultEnum.get_default() == CustomDefaultEnum.BETA


def test_uienum_no_side_effects():
    """Ensure get_labels returns a new dict and doesn't break on multiple calls."""
    labels1 = MockEnum.get_labels()
    labels2 = MockEnum.get_labels()
    assert labels1 == labels2
    assert labels1 is not labels2  # Different instances


# ----- Neighbor Connectivity -----

def test_neighbor_connectivity_custom_labels():
    """Verify the specific descriptive labels for Neighbor_Connectivity."""
    assert Neighbor_Connectivity.CONNECT4.label == '4 Cardinal (N, E, S, W)'
    assert Neighbor_Connectivity.CONNECT8.label == '8 (Cardinal + Diagonals)'
    
    # Test that from_label still works with these complex strings
    found = Neighbor_Connectivity.from_label('8 (Cardinal + Diagonals)')
    assert found == Neighbor_Connectivity.CONNECT8

def test_neighbor_connectivity_values():
    """Ensure the underlying integer values are preserved."""
    assert Neighbor_Connectivity.CONNECT4 == 4
    assert Neighbor_Connectivity.CONNECT8 == 8


# ------ Terrain Types ------
def test_terrain_type_values():
    """Verify that terrain costs and colors are correctly mapped."""
    # Test Cost (Crucial for pathfinding accuracy)
    assert Terrain_Type.GRASS.cost == 1.0
    assert Terrain_Type.WATER.cost == 5.0
    
    # Test Color (Crucial for rendering)
    assert Terrain_Type.SAND.color == (236, 217, 198)
    # Verify the fallback color for safety
    assert isinstance(Terrain_Type.GRASS.color, tuple)
    assert len(Terrain_Type.GRASS.color) == 3

def test_terrain_type_default_labels():
    """Verify that auto-labels still work for Terrain_Type."""
    # Should use the base UIEnum logic since get_labels isn't overridden
    assert Terrain_Type.GRASS.label == "Grass"
    assert Terrain_Type.WATER.label == "Water"
