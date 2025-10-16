# config.py
import pygame

# ----------------- Cấu hình -----------------
ROWS, COLS = 25, 35 # Kích thước lưới
CELL = 24           # Kích thước ô
PANEL_W = 280       # Chiều rộng Panel
WIDTH, HEIGHT = PANEL_W + COLS*CELL, ROWS*CELL

FPS = 60
MOVE_SPEED = 0.05   # Tốc độ di chuyển
BASE_X = PANEL_W    # Toạ độ X bắt đầu của lưới

# Màu
WHITE = (255,255,255)
BLACK = (10,10,10)
BG_OCEAN = (5,120,180)
WALL_COLOR = (40,40,40)
STORM = (140,60,160)
VISITED_COLOR = (180,255,200)
START_COLOR = (30,200,120)
GOAL_COLOR = (230,80,80)
UI_BG = (30,30,30)
BUTTON_BG = (60,60,70)
BUTTON_ACTIVE = (90,150,90)
TEXT = (230,230,230)
TABLE_BG = (50, 50, 50)
TABLE_BORDER = (100, 100, 100)

# Màu đường đi cho từng thuật toán
PATH_COLORS = {
    "BFS": (255, 230, 0), "DFS": (255, 100, 100), "UCS": (0, 255, 0),
    "A*": (255, 165, 0), "Greedy": (0, 255, 255), "Beam": (255, 0, 255),
    "IDS": (100, 100, 255)
}

# Thay đổi kích thước nút
BTN_H = 40 # Chiều cao nút
PADDING = 4

# Khởi tạo font chữ (cần pygame.init() trước)
pygame.init()
font = pygame.font.SysFont("Verdana", 14)
bigfont = pygame.font.SysFont("Arial", 20, bold=True)
headerfont = pygame.font.SysFont("Arial", 16, bold=True)