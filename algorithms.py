# algorithms.py
import time
import heapq
from collections import deque

# --- Helpers ---
def in_bounds(r, c, rows, cols):
    return 0 <= r < rows and 0 <= c < cols

def neighbors(pos, tile, rows, cols):
    r, c = pos
    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc, rows, cols) and tile[nr][nc] != 1:
            yield (nr, nc)

def manhattan(a, b):
    if a is None or b is None: return 99999
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(parent, start, goal, weight):
    if goal not in parent: return [], 0
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent.get(cur)
    path.reverse()
    total_cost = 0
    if len(path) > 1:
        for p in path[1:]:
            total_cost += weight[p[0]][p[1]]
    return path, total_cost

# --- Search Algorithms ---
def bfs_search(start, goal, tile, weight, rows, cols):
    if not start or not goal: return [], [], 0, 0, 0
    t0 = time.perf_counter()
    q = deque([start])
    parent = {start: None}
    visited = {start}
    visited_list = [start]
    while q:
        node = q.popleft()
        if node == goal: break
        for nb in neighbors(node, tile, rows, cols):
            if nb not in parent:
                parent[nb] = node
                visited.add(nb)
                visited_list.append(nb)
                q.append(nb)
    path, cost = reconstruct_path(parent, start, goal, weight)
    t = time.perf_counter() - t0
    return path, visited_list, len(visited), t, cost

def dfs_search(start, goal, tile, weight, rows, cols):
    if not start or not goal: return [], [], 0, 0, 0
    t0 = time.perf_counter()
    stack = [start]
    parent = {start: None}
    visited = {start}
    visited_list = [start]
    while stack:
        node = stack.pop()
        if node == goal: break
        for nb in neighbors(node, tile, rows, cols):
            if nb not in parent:
                parent[nb] = node
                visited.add(nb)
                visited_list.append(nb)
                stack.append(nb)
    path, cost = reconstruct_path(parent, start, goal, weight)
    t = time.perf_counter() - t0
    return path, visited_list, len(visited), t, cost

def ucs_search(start, goal, tile, weight, rows, cols):
    if not start or not goal: return [], [], 0, 0, 0
    t0 = time.perf_counter()
    pq = [(0, start)]
    parent = {start: None}
    g = {start: 0}
    visited = set()
    visited_list = []
    while pq:
        cost_u, u = heapq.heappop(pq)
        if u in visited: continue
        visited.add(u)
        visited_list.append(u)
        if u == goal: break
        for v in neighbors(u, tile, rows, cols):
            w = weight[v[0]][v[1]]
            newg = g[u] + w
            if v not in g or newg < g[v]:
                g[v] = newg
                parent[v] = u
                heapq.heappush(pq, (newg, v))
    path, cost = reconstruct_path(parent, start, goal, weight)
    t = time.perf_counter() - t0
    return path, visited_list, len(visited), t, cost

def astar_search(start, goal, tile, weight, rows, cols):
    if not start or not goal: return [], [], 0, 0, 0
    t0 = time.perf_counter()
    pq = []
    g = {start: 0}
    f = {start: manhattan(start, goal)}
    parent = {start: None}
    heapq.heappush(pq, (f[start], start))
    visited = set()
    visited_list = []
    while pq:
        _, u = heapq.heappop(pq)
        if u in visited: continue
        visited.add(u)
        visited_list.append(u)
        if u == goal: break
        for v in neighbors(u, tile, rows, cols):
            w = weight[v[0]][v[1]]
            newg = g[u] + w
            if v not in g or newg < g[v]:
                g[v] = newg
                parent[v] = u
                f[v] = newg + manhattan(v, goal)
                heapq.heappush(pq, (f[v], v))
    path, cost = reconstruct_path(parent, start, goal, weight)
    t = time.perf_counter() - t0
    return path, visited_list, len(visited), t, cost

def greedy_search(start, goal, tile, weight, rows, cols):
    if not start or not goal: return [], [], 0, 0, 0
    t0 = time.perf_counter()
    pq = []
    parent = {start: None}
    visited = set()
    visited_list = []
    heapq.heappush(pq, (manhattan(start, goal), start))
    while pq:
        _, u = heapq.heappop(pq)
        if u in visited: continue
        visited.add(u)
        visited_list.append(u)
        if u == goal: break
        for v in neighbors(u, tile, rows, cols):
            if v not in visited and v not in parent:
                parent[v] = u
                heapq.heappush(pq, (manhattan(v, goal), v))
    path, cost = reconstruct_path(parent, start, goal, weight)
    t = time.perf_counter() - t0
    return path, visited_list, len(visited), t, cost

def beam_search(start, goal, tile, weight, rows, cols, beam_width=6):
    if not start or not goal: return [], [], 0, 0, 0
    t0 = time.perf_counter()
    frontier = [start]
    parent = {start: None}
    visited = {start}
    visited_list = [start]
    found = False
    depth = 0
    while frontier and not found and depth < rows*cols:
        candidates = []
        for u in frontier:
            if u == goal: found = True; break
            for v in neighbors(u, tile, rows, cols):
                if v not in parent:
                    parent[v] = u
                    visited.add(v)
                    visited_list.append(v)
                    candidates.append(v)
        if found: break
        candidates.sort(key=lambda x: manhattan(x, goal))
        frontier = candidates[:beam_width]
        depth += 1
    path, cost = reconstruct_path(parent, start, goal, weight)
    t = time.perf_counter() - t0
    return path, visited_list, len(visited), t, cost

def ids_search(start, goal, tile, weight, rows, cols, max_depth=None):
    if max_depth is None:
        max_depth = rows * cols
    if not start or not goal: return [], [], 0, 0, 0
    t0 = time.perf_counter()
    
    visited_for_animation = []
    
    for depth_limit in range(max_depth):
        stack = [(start, 0)]
        parent = {start: None}
        visited_in_this_dls = {start}

        while stack:
            node, current_depth = stack.pop()

            if node not in visited_for_animation:
                visited_for_animation.append(node)

            if node == goal:
                path, cost = reconstruct_path(parent, start, goal, weight)
                t = time.perf_counter() - t0
                visited_count = len(set(visited_for_animation))
                return path, visited_for_animation, visited_count, t, cost

            if current_depth < depth_limit:
                for nb in neighbors(node, tile, rows, cols):
                    if nb not in visited_in_this_dls:
                        visited_in_this_dls.add(nb)
                        parent[nb] = node
                        stack.append((nb, current_depth + 1))

    t = time.perf_counter() - t0
    visited_count = len(set(visited_for_animation))
    return [], visited_for_animation, visited_count, t, 0