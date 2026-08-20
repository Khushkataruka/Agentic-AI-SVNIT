import collections
import heapq
import copy

# Directions: Up, Right, Down, Left
DIRS = [(-1, 0, 'U'), (0, 1, 'R'), (1, 0, 'D'), (0, -1, 'L')]

def print_grid(grid, agent_pos=None):
    """Utility function to print the grid with the agent's current position."""
    for r, row in enumerate(grid):
        line = ""
        for c, char in enumerate(row):
            if agent_pos == (r, c):
                line += "A "
            else:
                line += char + " "
        print(line)
    print()

def get_start_goal(grid):
    """Finds and returns the coordinates of Start (S) and Goal (G)."""
    start = goal = None
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 'S':
                start = (r, c)
            elif grid[r][c] == 'G':
                goal = (r, c)
    return start, goal

# --- Base Algorithm: BFS Planning ---
def bfs_plan(grid, start, goal):
    """Plans a path from start to goal using Breadth-First Search."""
    queue = collections.deque([(start, [])])
    visited = {start}
    
    while queue:
        (r, c), path = queue.popleft()
        
        if (r, c) == goal:
            return path
            
        for dr, dc, move in DIRS:
            nr, nc = r + dr, c + dc
            # Check boundaries
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                # Check for obstacles/pits and if visited
                if grid[nr][nc] not in ['#', 'P'] and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append(((nr, nc), path + [move]))
                    
    return None

def execute_plan(grid, start, path):
    """Executes the pre-calculated path step-by-step."""
    r, c = start
    print("Initial State:")
    print_grid(grid, (r, c))
    
    for move in path:
        print(f"Move: {move}")
        if move == 'U': r -= 1
        elif move == 'D': r += 1
        elif move == 'L': c -= 1
        elif move == 'R': c += 1
        
        print_grid(grid, (r, c))
        if grid[r][c] == '#':
            print("Failure: hit an obstacle!")
            return False
            
    if grid[r][c] == 'G':
        print("Success: Reached Goal!")
        return True
    return False

# --- Exercise 1: Uniform Cost Search ---
def ucs_plan(grid, costs, start, goal):
    """Plans a path using Uniform-Cost Search considering terrain costs."""
    pq = [(0, start, [])]
    visited = {}
    
    while pq:
        cost, (r, c), path = heapq.heappop(pq)
        
        if (r, c) in visited and visited[(r, c)] <= cost:
            continue
        visited[(r, c)] = cost
        
        if (r, c) == goal:
            return path, cost
            
        for dr, dc, move in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if grid[nr][nc] not in ['#', 'P']:
                    move_cost = costs[nr][nc]
                    new_cost = cost + move_cost
                    if (nr, nc) not in visited or visited.get((nr, nc), float('inf')) > new_cost:
                        heapq.heappush(pq, (new_cost, (nr, nc), path + [move]))
    return None, float('inf')

# --- Exercise 2: Re-planning on Failure ---
def execute_and_replan(grid, start, goal):
    """Executes a plan and replans if a dynamic obstacle blocks the path."""
    r, c = start
    path = bfs_plan(grid, (r, c), goal)
    
    if not path:
        print("No path found initially.")
        return
        
    print(f"Initial Plan: {path}")
    print("Starting execution:")
    print_grid(grid, (r, c))
    
    steps = 0
    while (r, c) != goal:
        if not path:
            print("Plan is empty but goal not reached. Re-planning...")
            path = bfs_plan(grid, (r, c), goal)
            if not path:
                print("Failed to re-plan. Goal unreachable.")
                return
            print(f"New Plan: {path}")
            
        move = path.pop(0)
        nr, nc = r, c
        if move == 'U': nr -= 1
        elif move == 'D': nr += 1
        elif move == 'L': nc -= 1
        elif move == 'R': nc += 1
        
        # Simulate a dynamic change: Block the path on step 1
        if steps == 1:
            print(f"\n--- DYNAMIC EVENT: Unknown obstacle appears at ({nr}, {nc})! ---")
            grid[nr][nc] = '#'
            
        # Check if the next intended step is now blocked
        if grid[nr][nc] == '#':
            print(f"Detected obstacle at intended cell ({nr}, {nc}). Stopping execution.")
            print("Re-planning from current position...")
            # Replan from current (r, c) without moving
            path = bfs_plan(grid, (r, c), goal)
            if not path:
                print("Failed to re-plan. Goal unreachable.")
                return
            print(f"New Plan: {path}")
        else:
            r, c = nr, nc
            print(f"Moved {move} to ({r}, {c})")
            print_grid(grid, (r, c))
            steps += 1
            
    print("Success: Reached Goal after re-planning!")

# --- Exercise 3: Hybrid Agent (Reactive Filter) ---
def get_adjacent_cells(grid, r, c):
    """Returns valid adjacent cells for a given position."""
    adj = []
    for dr, dc, _ in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
            adj.append((nr, nc))
    return adj

def hybrid_plan_and_execute(grid, start, goal):
    """Deliberative planning filtered by a reactive rule (avoid cells adjacent to pits)."""
    path = bfs_plan(grid, start, goal)
    if not path:
        print("No valid path found.")
        return False
        
    print(f"Deliberative Plan: {path}")
    print("Starting execution with Reactive Filter:")
    
    r, c = start
    print_grid(grid, (r, c))
    for move in path:
        nr, nc = r, c
        if move == 'U': nr -= 1
        elif move == 'D': nr += 1
        elif move == 'L': nc -= 1
        elif move == 'R': nc += 1
        
        # Reactive filter: never step into a cell adjacent to a pit
        adj = get_adjacent_cells(grid, nr, nc)
        adjacent_to_pit = any(grid[ar][ac] == 'P' for ar, ac in adj)
        
        if adjacent_to_pit:
            print(f"REACTING: Danger detected! Cell ({nr}, {nc}) is adjacent to a pit 'P'!")
            print("Reactive rule overriding deliberative plan. Stopping execution.")
            return False
            
        if grid[nr][nc] == '#':
            print("Hit an obstacle!")
            return False
            
        r, c = nr, nc
        print(f"Moved {move}")
        print_grid(grid, (r, c))
        
    if (r, c) == goal:
        print("Success: Reached Goal safely!")
        return True
    return False

def main():
    world = [
        ['S', '.', '.', '.', '#'],
        ['.', '#', '.', '.', '.'],
        ['.', '.', '.', '#', 'G'],
        ['#', '.', '.', '.', '.']
    ]
    
    start, goal = get_start_goal(world)
    
    print("="*50)
    print("Base Algorithm: BFS Plan & Execute")
    print("="*50)
    path = bfs_plan(world, start, goal)
    print(f"Calculated Plan: {path}\n")
    execute_plan(world, start, path)
    
    print("\n" + "="*50)
    print("Exercise 1: Uniform Cost Search")
    print("="*50)
    # Define a terrain cost grid (same size as world)
    costs = [
        [1, 1, 1, 1, 1],
        [1, 5, 2, 1, 1],
        [1, 1, 9, 5, 1],
        [5, 1, 1, 1, 1]
    ]
    ucs_path, ucs_cost = ucs_plan(world, costs, start, goal)
    print(f"UCS Plan: {ucs_path}")
    print(f"Total Cost: {ucs_cost}")
    
    print("\n" + "="*50)
    print("Exercise 2: Re-planning on Failure")
    print("="*50)
    world_copy = copy.deepcopy(world)
    execute_and_replan(world_copy, start, goal)
    
    print("\n" + "="*50)
    print("Exercise 3: Hybrid Agent")
    print("="*50)
    # Introduce a pit 'P' that the deliberative plan might not consider dangerous
    # (BFS just avoids stepping ON 'P', but our reactive rule avoids adjacency)
    world_with_pit = [
        ['S', '.', '.', '.', '#'],
        ['.', '#', '.', 'P', '.'],
        ['.', '.', '.', '#', 'G'],
        ['#', '.', '.', '.', '.']
    ]
    start_p, goal_p = get_start_goal(world_with_pit)
    hybrid_plan_and_execute(world_with_pit, start_p, goal_p)

if __name__ == "__main__":
    main()
