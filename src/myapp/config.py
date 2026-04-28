import json
import os
from dataclasses import dataclass, field, replace, asdict

@dataclass(frozen=True)
class GridConfig:
    min_cells: int = 8
    max_cells: int = 256
    rows: int = 32
    cols: int = 32
    width: int = 768
    height: int = 768
    padding: int = 20
    
    @property 
    def start_x(self) -> int:
        return self.width + self.padding 
    
    @property 
    def start_y(self) -> int:
        return self.height + self.padding 
    

@dataclass(frozen=True)
class UIConfig:
    width: int = 400
    row_spacing: int = 50
    checkbox_size: int = 25
    label_width: int = 110
    widget_height: int = 35
    padding: int = 10
    # Calculated properties
    #panel_height: int = 763  # (Grid height + Padding - Start Y)

@dataclass(frozen=True)
class AppConfig:
    grid: GridConfig = field(default_factory=GridConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    fps: int = 60
    bg_color: tuple = (225, 225, 225)

    @property
    def window_width(self) -> int:
        return self.grid.width + (self.grid.padding * 3) + self.ui.width

    @property
    def window_height(self) -> int:
        return self.grid.height + (self.grid.padding * 2)
    

def load_config(filename: str = "config.json") -> AppConfig:
    """Loads JSON overrides and merges them with AppConfig defaults."""
    config = AppConfig()
    
    # Locate file relative to the project root (usually one level up from src)
    if not os.path.exists(filename):
        return config

    with open(filename, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return config

    # Merge nested dataclasses
    if "grid" in data:
        # Start with default dict, update with JSON values, unpack into constructor
        grid_merged = {**asdict(config.grid), **data["grid"]}
        config = replace(config, grid=GridConfig(**grid_merged))
    
    if "ui" in data:
        ui_merged = {**asdict(config.ui), **data["ui"]}
        config = replace(config, ui=UIConfig(**ui_merged))

    # Merge top-level AppConfig values
    if "fps" in data:
        config = replace(config, fps=data["fps"])
    if "bg_color" in data:
        config = replace(config, bg_color=tuple(data["bg_color"]))

    return config

