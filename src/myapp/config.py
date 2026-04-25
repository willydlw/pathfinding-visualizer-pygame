from dataclasses import dataclass, field

@dataclass(frozen=True)
class GridConfig:
    MIN_CELLS: int = 8
    MAX_CELLS: int = 256
    GRID_SIZE: int = 768
    PADDING: int = 20

@dataclass(frozen=True)
class UIConfig:
    SIDEBAR_WIDTH: int = 400
    WIDGET_HEIGHT: int = 35
    ROW_SPACING: int = 50
    PADDING:     int = 10
    LABEL_WIDTH: int = 110
    # ... include your other UI constants here

@dataclass(frozen=True)
class Settings:
    grid: GridConfig = field(default_factory=GridConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    fps: int = 60
    bg_color: tuple = (225, 225, 225)
