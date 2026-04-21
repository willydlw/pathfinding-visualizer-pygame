"""
If you are using pytest, just navigate to the project_root in your terminal and run: pytest
"""


import pytest
from your_module import UIEnum, Neighbor_Connectivity

class MockEnum(UIEnum):
    FIRST_OPTION = 1
    SECOND_OPTION = 2

def test_uienum_default_behavior():
    # Test auto-label generation (underscore to Space Title Case)
    assert MockEnum.FIRST_OPTION.label == "First Option"
    
    # Test default member selection
    assert MockEnum.get_default() == MockEnum.FIRST_OPTION
    
    # Test options list generation
    assert MockEnum.options_list() == ["First Option", "Second Option"]


def test_uienum_from_label():
    # Test valid conversion
    assert MockEnum.from_label("Second Option") == MockEnum.SECOND_OPTION
    # Test case insensitivity
    assert MockEnum.from_label("first option") == MockEnum.FIRST_OPTION
    # Test fallback to default on invalid input
    assert MockEnum.from_label("Non-existent") == MockEnum.FIRST_OPTION


def test_neighbor_connectivity_overrides():
    # Test custom labels
    assert Neighbor_Connectivity.CONNECT4.label == '4 Cardinal (N, E, S, W)'
    
    # Test __str__ method (which uses the label)
    assert str(Neighbor_Connectivity.CONNECT8) == '8 (Cardinal + Diagonals)'
    
    # Test from_label with the specific custom strings
    member = Neighbor_Connectivity.from_label('4 Cardinal (n, e, s, w)')
    assert member == Neighbor_Connectivity.CONNECT4



