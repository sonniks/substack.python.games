from typing import Iterable, Tuple, Set, List, Any


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
UI_OFFSET = 96
UI_HEIGHT = 96
TILE_SIZE = 32
SPRITESHEET_PATH = "assets/sprites/sheet.png"
FONT_PATH = "assets/fonts/Eight-Bit Madness.ttf"
SHOW_TILE_COORDS = False

PADDING = 12
ICON_SPACING = 8
TEXT_COLOR = (255, 255, 255)
BAR_BG = (0, 0, 0)

BEAM_DURATION_MS = 300  # ~0.3s
PROJ_SX, PROJ_SY = 0, 2
FIRE_SOUND = None

DEATH_ANIM_MS = 3000
DEATH_COOLDOWN_MS = 5000  # cannot die again for 5s after animation ends

# Tiles where combat/impact checks are not eligible
NON_ELIGIBLE = {'L', 'D', 'U', 'E', 'T'}

# Default candy set; adjust if your tiles.csv uses different symbols
DEFAULT_CANDY: Set[str] = {'@', '!', '#', '$'}

DISABLE_WINDOW_MS = 2000
DISABLE_DURATION_MS = 30000


