SCREEN_W, SCREEN_H = 800, 600
CELL_SIZE = 20
GRID_W = SCREEN_W // CELL_SIZE
GRID_H = SCREEN_H // CELL_SIZE
FPS = 60
SNAKE_SPEED = 8
FINGER_THRESHOLD = 25
CAM_W, CAM_H = 200, 150

SCORE_FILENAME = "scores.json"
POWERUP_DURATION = 8.0
POWERUP_SPAWN_SEC = 7.0

# Feature flags untuk mengatur progress demo tanpa menghapus kode.
# Fitur utama presentasi tetap aktif.
ENABLE_GESTURE_CONTROL = True
ENABLE_KEYBOARD_CONTROL = True
ENABLE_SCORE = True
ENABLE_HIGH_SCORE = True
ENABLE_MENU = True
ENABLE_PAUSE = True
ENABLE_RESET = True
ENABLE_DIFFICULTY_SELECT = True
ENABLE_WEBCAM_PREVIEW = True
ENABLE_HAND_SKELETON = True

# Fitur tambahan bisa dinyalakan lagi saat milestone berikutnya.
ENABLE_LEVEL_PROGRESS = False
ENABLE_LEVEL_SPEEDUP = False
ENABLE_OBSTACLES = False
ENABLE_POWERUPS = False
ENABLE_ADVANCED_POWERUPS = False
ENABLE_PARTICLES = True
ENABLE_GESTURE_POWER_SKILL = False

MODEL_FILENAME = "hand_landmarker.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)

RIGHT = (1, 0)
LEFT = (-1, 0)
UP = (0, -1)
DOWN = (0, 1)

COLOR_BG = (10, 10, 20)
COLOR_GRID = (20, 20, 35)
COLOR_SNAKE_HEAD = (0, 230, 120)
COLOR_SNAKE_BODY = (0, 170, 90)
COLOR_SNAKE_SHINE = (100, 255, 180)
COLOR_FOOD = (255, 70, 70)
COLOR_FOOD_SHINE = (255, 180, 150)
COLOR_TEXT = (220, 220, 220)
COLOR_SCORE = (0, 230, 120)
COLOR_CAM_BORDER = (0, 200, 100)
COLOR_WARNING = (255, 180, 0)
COLOR_OBSTACLE = (90, 90, 120)
COLOR_POWERUP = (80, 180, 255)
COLOR_SHIELD = (90, 210, 255)

INDEX_FINGER_TIP = 8

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"

POWER_SLOW = "slow"
POWER_DOUBLE = "double"
POWER_SHIELD = "shield"
POWER_GHOST = "ghost"

DIFFICULTIES = {
    "Easy": {"speed": 10, "obstacles": False},
    "Normal": {"speed": 8, "obstacles": True},
    "Hard": {"speed": 6, "obstacles": True},
}

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9), (9, 13), (13, 17),
]
