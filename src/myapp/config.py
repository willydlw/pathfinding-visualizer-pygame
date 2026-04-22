from dataclasses import dataclass, field

@dataclass(frozen=True)
class GridConfig:
    DEFAULT_SIZE: int = 8
    MAX_SIZE: int = 256
    WIDTH: int = 768
    PADDING: int = 20

@dataclass(frozen=True)
class UIConfig:
    SIDEBAR_WIDTH: int = 400
    WIDGET_HEIGHT: int = 35
    ROW_SPACING: int = 50
    # ... include your other UI constants here

@dataclass(frozen=True)
class Settings:
    grid: GridConfig = field(default_factory=GridConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    fps: int = 60
    bg_color: tuple = (225, 225, 225)
