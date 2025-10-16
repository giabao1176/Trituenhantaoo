# main.py
import pygame, sys, random
from config import *
import algorithms as algo
from ui_components import DropdownMenu


# ----------------- Khởi tạo Pygame & Màn hình -----------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("📦 Robot Giao Hàng - Pathfinding Visualizer")
clock = pygame.time.Clock()

# ----------------- Tải ảnh -----------------
def load_and_scale_image(file_name, size):
    try:
        img = pygame.image.load(file_name).convert_alpha()
        return pygame.transform.scale(img, size)
    except pygame.error as e:
        print(f"Lỗi tải ảnh {file_name}: {e}. Sử dụng màu mặc định thay thế.")
        return None

WALL_IMAGE = load_and_scale_image("tuong.png", (CELL, CELL))
ROBOT_IMAGE = load_and_scale_image("robot.png", (CELL, CELL))
CUSTOMER_IMAGE = load_and_scale_image("khachhang.png", (CELL, CELL))
DUONGDI_IMAGE = load_and_scale_image("duongdi.png", (CELL, CELL))

# ----------------- Trạng thái game -----------------
start = None
goal = None
tile = [[0 for _ in range(COLS)] for _ in range(ROWS)]
weight = [[1 for _ in range(COLS)] for _ in range(ROWS)]
current_path = []
show_visited_set = set()
visited_animation_list = []
all_paths_results = {}
animating_path = False
moving_robot = False
animation_index = 0
robot_pos_pixel = None
path_index = 0
move_progress = 0.0
last_cost = 0.0
last_time = 0.0
visited_count = 0
results_table = {}
show_table = False
selected_algo = "A*"

SEARCHERS = {
    "BFS": algo.bfs_search, "DFS": algo.dfs_search, "UCS": algo.ucs_search,
    "A*": algo.astar_search, "Greedy": algo.greedy_search, "Beam": algo.beam_search,
    "IDS": algo.ids_search
}

# ----------------- Logic Game & Map -----------------
def get_pixel_coords(r, c):
    return BASE_X + c * CELL, r * CELL

def reset_map():
    global tile, weight, start, goal, current_path, show_visited_set, last_cost, last_time, visited_count, results_table, visited_animation_list, all_paths_results, animating_path, moving_robot, robot_pos_pixel, path_index, move_progress, show_table
    tile = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    weight = [[1 for _ in range(COLS)] for _ in range(ROWS)]
    start = None
    goal = None
    current_path = []
    show_visited_set.clear()
    visited_animation_list.clear()
    all_paths_results.clear()
    animating_path = False
    moving_robot = False
    robot_pos_pixel = None
    path_index = 0
    move_progress = 0.0
    last_cost = 0.0
    last_time = 0.0
    visited_count = 0
    results_table.clear()
    show_table = False

def generate_random_map(density_wall=0.2, density_storm=0.1):
    global start, goal, robot_pos_pixel
    reset_map()
    for r in range(ROWS):
        for c in range(COLS):
            if r==0 or c==0 or r==ROWS-1 or c==COLS-1:
                tile[r][c] = 1
                weight[r][c] = 999
                continue
    for r in range(1, ROWS-1):
        for c in range(1, COLS-1):
            rnd = random.random()
            if rnd < density_wall:
                tile[r][c] = 1; weight[r][c] = 999
            elif rnd < density_wall + density_storm:
                tile[r][c] = 3; weight[r][c] = random.choice([3,4,5])
    
    all_water_tiles = [(r, c) for r in range(ROWS) for c in range(COLS) if tile[r][c] == 0]
    if len(all_water_tiles) >= 2:
        start, goal = random.sample(all_water_tiles, 2)
    else:
        start, goal = (1, 1), (ROWS-2, COLS-2)
    
    tile[start[0]][start[1]] = 0; weight[start[0]][start[1]] = 1
    tile[goal[0]][goal[1]] = 0; weight[goal[0]][goal[1]] = 1
    robot_pos_pixel = get_pixel_coords(start[0], start[1])

# ----------------- Animation logic -----------------
def animate_robot_movement():
    global moving_robot, path_index, move_progress, robot_pos_pixel
    if not current_path or len(current_path) < 2 or path_index >= len(current_path) - 1:
        moving_robot = False
        return
        
    start_r, start_c = current_path[path_index]
    end_r, end_c = current_path[path_index + 1]
    start_x, start_y = get_pixel_coords(start_r, start_c)
    end_x, end_y = get_pixel_coords(end_r, end_c)
    
    move_progress += MOVE_SPEED * 60 / FPS
    if move_progress >= 1.0:
        path_index += 1
        move_progress = 0.0
        robot_pos_pixel = (end_x, end_y)
        if path_index >= len(current_path) - 1:
            moving_robot = False
            return

    current_x = start_x + (end_x - start_x) * move_progress
    current_y = start_y + (end_y - start_y) * move_progress
    robot_pos_pixel = (current_x, current_y)

# ----------------- Drawing Functions -----------------
def draw_ui():
    pygame.draw.rect(screen, UI_BG, (0,0, PANEL_W, HEIGHT))
    screen.blit(bigfont.render("Robot Giao Hàng", True, TEXT), (12, -2))
    
    y_stats = HEIGHT - 150
    pygame.draw.line(screen, TABLE_BORDER, (10, y_stats - 10), (PANEL_W - 10, y_stats - 10), 1)

    screen.blit(font.render(f"Thuật toán: {selected_algo}", True, TEXT), (12, y_stats))
    screen.blit(font.render(f"Đã duyệt: {visited_count}", True, TEXT), (12, y_stats + 20))
    screen.blit(font.render(f"Thời gian: {last_time:.4f}s", True, TEXT), (12, y_stats + 40))
    screen.blit(font.render(f"Số bước: {len(current_path)}", True, TEXT), (12, y_stats + 60))
    screen.blit(font.render(f"Chi phí: {last_cost:.2f}", True, TEXT), (12, y_stats + 80))
    
    screen.blit(font.render("R-Click: Start/Goal | L-Click: Terrain", True, (150,150,150)), (12, HEIGHT - 20))

def draw_grid():
    for r in range(ROWS):
        for c in range(COLS):
            x, y = get_pixel_coords(r, c)
            rect = pygame.Rect(x,y,CELL,CELL)
            t = tile[r][c]
            
            if t == 1:
                if WALL_IMAGE: screen.blit(WALL_IMAGE, rect)
                else: pygame.draw.rect(screen, WALL_COLOR, rect)
            elif t == 3:
                pygame.draw.rect(screen, STORM, rect)
            else:
                if DUONGDI_IMAGE: screen.blit(DUONGDI_IMAGE, rect)
                else: pygame.draw.rect(screen, BG_OCEAN, rect)
            
            pygame.draw.rect(screen, BLACK, rect, 1)
            if weight[r][c] > 1 and t != 1:
                txt = font.render(str(weight[r][c]), True, WHITE)
                screen.blit(txt, (x+4, y+4))

    if show_visited_set:
        for v in show_visited_set:
            if v == start or v == goal: continue
            x, y = get_pixel_coords(v[0], v[1])
            s = pygame.Surface((CELL,CELL), pygame.SRCALPHA)
            s.fill((*VISITED_COLOR, 90))
            screen.blit(s, (x,y))

    if current_path and len(current_path) >= 2:
        path_color = PATH_COLORS.get(selected_algo, WHITE)
        points = [(BASE_X + c*CELL + CELL//2, r*CELL + CELL//2) for r,c in current_path]
        pygame.draw.lines(screen, path_color, False, points, 4)

    if all_paths_results:
        for algo_name, res in all_paths_results.items():
            path = res.get('path', [])
            if path and len(path) > 1:
                path_color = PATH_COLORS.get(algo_name, WHITE)
                points = [(BASE_X + c*CELL + CELL//2, r*CELL + CELL//2) for r,c in path]
                pygame.draw.lines(screen, path_color, False, points, 2)
    
    if goal:
        x, y = get_pixel_coords(goal[0], goal[1])
        if CUSTOMER_IMAGE: screen.blit(CUSTOMER_IMAGE, (x,y))
        else: pygame.draw.rect(screen, GOAL_COLOR, (x+3,y+3,CELL-6,CELL-6), border_radius=6)
    
    if start and robot_pos_pixel:
        if ROBOT_IMAGE: screen.blit(ROBOT_IMAGE, (robot_pos_pixel))
        else: pygame.draw.rect(screen, START_COLOR, (*robot_pos_pixel, CELL, CELL), border_radius=6)

def draw_results_table():
    if not show_table: return
    
    table_rect = pygame.Rect(PANEL_W + 50, 50, WIDTH - PANEL_W - 100, HEIGHT - 100)
    pygame.draw.rect(screen, TABLE_BG, table_rect, border_radius=10)
    pygame.draw.rect(screen, TABLE_BORDER, table_rect, 2, border_radius=10)

    headers = ["Thuật toán", "Đã duyệt", "Thời gian (s)", "Số bước", "Chi phí"]
    col_widths = [table_rect.width * 0.25, table_rect.width * 0.15, table_rect.width * 0.2, table_rect.width * 0.15, table_rect.width * 0.15]
    
    y = table_rect.y + 10
    x_start = table_rect.x + 10
    
    x = x_start
    for i, header in enumerate(headers):
        screen.blit(headerfont.render(header, True, TEXT), (x, y))
        x += col_widths[i]

    y += 30
    pygame.draw.line(screen, TABLE_BORDER, (table_rect.x + 10, y - 5), (table_rect.right - 10, y - 5), 1)
    
    for algo_name, res in results_table.items():
        data = [
            algo_name,
            str(res.get("visited", 0)),
            f'{res.get("time", 0.0):.4f}',
            str(len(res.get("path", []))),
            f'{res.get("cost", 0.0):.2f}'
        ]
        x = x_start
        for i, item in enumerate(data):
            screen.blit(font.render(item, True, TEXT), (x, y))
            x += col_widths[i]
        y += 25

# ----------------- Khởi tạo UI -----------------
ALGO_MENU = DropdownMenu(
    (PADDING, 20, PANEL_W - 2 * PADDING, BTN_H + 4), 
    f"Chọn Thuật Toán ({selected_algo})", 
    list(SEARCHERS.keys()), 
    "algo"
)

FUNC_MENU = DropdownMenu(
    (PADDING, 20 + BTN_H + 4 + PADDING, PANEL_W - 2 * PADDING, BTN_H + 4), 
    "Chọn Chức Năng", 
    ["1. Duyệt ô (Run)", "2. Di chuyển Robot", "3. Chạy tất cả & So sánh", "4. Xem bảng so sánh",
     "---", "Random Map", "Reset Map", "Xóa kết quả"], 
    "func"
)

# ----------------- Main loop -----------------
def main():
    global selected_algo, current_path, show_visited_set, visited_animation_list, all_paths_results, last_cost, last_time, visited_count, show_table, animating_path, moving_robot, animation_index, start, goal, robot_pos_pixel, results_table

    reset_map()
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    show_table = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                if mx < PANEL_W:
                    menu_clicked, item_text = ALGO_MENU.handle_click((mx, my))
                    if menu_clicked:
                        FUNC_MENU.is_open = False
                        if menu_clicked == "algo":
                            selected_algo = item_text
                            current_path, show_visited_set, last_cost, last_time, visited_count = [], set(), 0.0, 0.0, 0

                    menu_clicked, item_text = FUNC_MENU.handle_click((mx, my))
                    if menu_clicked:
                        ALGO_MENU.is_open = False
                        if menu_clicked == "func":
                            show_table = animating_path = moving_robot = False
                            all_paths_results.clear()

                            if item_text in ["1. Duyệt ô (Run)", "2. Di chuyển Robot"]:
                                if start and goal:
                                    search_func = SEARCHERS[selected_algo]
                                    if selected_algo == "Beam":
                                        path, visited_list, visited_c, time_t, cost_t = search_func(start, goal, tile, weight, ROWS, COLS, beam_width=8)
                                    else:
                                        path, visited_list, visited_c, time_t, cost_t = search_func(start, goal, tile, weight, ROWS, COLS)
                                    
                                    current_path, visited_animation_list, visited_count, last_time, last_cost = path, visited_list, visited_c, time_t, cost_t
                                    show_visited_set.clear()
                                    if start: robot_pos_pixel = get_pixel_coords(start[0], start[1])

                                    if item_text == "2. Di chuyển Robot" and current_path:
                                        moving_robot = True
                                        show_visited_set.update(visited_list)
                                    elif item_text == "1. Duyệt ô (Run)":
                                        animating_path = True
                                        animation_index = 0

                            elif item_text == "3. Chạy tất cả & So sánh" or item_text == "4. Xem bảng so sánh":
                                if start and goal:
                                    results_table = {}
                                    for name, func in SEARCHERS.items():
                                        if name == "Beam":
                                            p, vl, vc, tt, ct = func(start, goal, tile, weight, ROWS, COLS, beam_width=8)
                                        else:
                                            p, vl, vc, tt, ct = func(start, goal, tile, weight, ROWS, COLS)
                                        results_table[name] = {"path": p, "visited": vc, "time": tt, "cost": ct}
                                    
                                    if item_text == "3. Chạy tất cả & So sánh":
                                        all_paths_results = results_table
                                        current_path = []
                                        show_visited_set.clear()
                                    else: # Xem bảng
                                        show_table = True

                            elif item_text == "Random Map": generate_random_map()
                            elif item_text == "Reset Map": reset_map()
                            elif item_text == "Xóa kết quả":
                                current_path, show_visited_set, visited_animation_list, all_paths_results = [], set(), [], {}
                                last_cost, last_time, visited_count = 0.0, 0.0, 0

                elif not show_table and not animating_path and not moving_robot:
                    ALGO_MENU.is_open = FUNC_MENU.is_open = False
                    col, row = (mx - BASE_X) // CELL, my // CELL
                    
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        current_path, show_visited_set, visited_animation_list, all_paths_results, last_cost, last_time, visited_count = [], set(), [], {}, 0.0, 0.0, 0
                        
                        pos = (row, col)
                        if event.button == 1:
                            if pos != start and pos != goal:
                                current_tile = tile[row][col]
                                if current_tile == 1: tile[row][col], weight[row][col] = 0, 1
                                elif current_tile == 0: tile[row][col], weight[row][col] = 3, 3
                                else: tile[row][col], weight[row][col] = 1, 999
                        elif event.button == 3:
                            if not start:
                                start = pos
                                tile[row][col], weight[row][col] = 0, 1
                                robot_pos_pixel = get_pixel_coords(row, col)
                            elif not goal and pos != start:
                                goal = pos
                                tile[row][col], weight[row][col] = 0, 1
                            elif pos == start: start, robot_pos_pixel = None, None
                            elif pos == goal: goal = None

        if moving_robot: animate_robot_movement()
        
        if animating_path and visited_animation_list:
            if animation_index < len(visited_animation_list):
                # Tăng tốc độ animation
                for _ in range(5):
                    if animation_index < len(visited_animation_list):
                        show_visited_set.add(visited_animation_list[animation_index])
                        animation_index += 1
            else:
                animating_path = False

        screen.fill(BLACK)
        draw_grid()
        draw_ui()
        
        ALGO_MENU.top_button.text = f"Thuật Toán ({selected_algo})"
        if ALGO_MENU.is_open:
            FUNC_MENU.draw(screen, None)
            ALGO_MENU.draw(screen, selected_algo)
        else:
            ALGO_MENU.draw(screen, selected_algo)
            FUNC_MENU.draw(screen, None)

        draw_results_table()
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()