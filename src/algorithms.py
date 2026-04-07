from collections import deque 
import heapq 
import logging 

from .grid import Grid 

from .constants import (
    PATH_COST
)

logger = logging.getLogger(__name__)


def get_neighbors(node, grid):
    """
    Returns a list of valid, walkable Node neighbors (Up, Down, Left, Righ)
    """

    neighbors = []
    rows = grid.rows
    cols = grid.cols

    # Adjacent relative positions (row_offset, col_offset)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        r, c = node.row + dr, node.col + dc 

        # Boundary check 
        if 0 <= r < rows and 0 <= c < cols:
            neighbor = grid.map[r][c]
            neighbors.append(neighbor)

    return neighbors


def reconstruct_path(end_node):
    """Backtracks from the end node to the start node to mark the path."""
    curr = end_node.parent      # start with node before the end
    while curr and not curr.is_start:
        curr.path = True 
        curr = curr.parent 


def bfs(grid, start_node, end_node):
    """
    Performs a Breadth-First-Search on the grid.
    Returns the end node if path found, else None
    """

    # enqueue the starting node and mark as visited
    queue =deque([start_node]) 
    start_node.visited = True 

    allowed_terrain = start_node.terrain 
   
    while queue:
        current = queue.popleft()
        current.closed = True       # Mark as fully processed 

        if current == end_node:
            logging.info(f"BFS found path!")
            reconstruct_path(current)
            yield True   # Signal to PathFinder App that search is done
            return       # Stop the generator 

        for neighbor in get_neighbors(current, grid):
            if not neighbor.visited and neighbor.terrain == allowed_terrain:
                    neighbor.visited = True 
                    neighbor.parent = current   # Link for path reconstruction
                    queue.append(neighbor)

        # yield here to pause the algorithm and let pygame draw 
        # one full node processed per "frame"
        yield False 

    logging.info("BFS, No path exists")
    yield True 


def dfs(grid, start_node, end_node):
    """
    Performs a Depth-First Search on the grid.
    """

    # Use a list as a stack (LIFO)
    stack = [start_node]
    allowed_terrain = start_node.terrain       

    while stack:
        current = stack.pop() 
        current.closed = True       # Mark as fully processed

        if current == end_node:
            logging.info("Path found via DFS.")
            reconstruct_path(current)
            yield True 
            return 

        for neighbor in get_neighbors(current, grid):
            if not neighbor.visited and neighbor.terrain == allowed_terrain:
                neighbor.visited = True 
                neighbor.parent = current 
                stack.append(neighbor)

        # yield here to pause the algorithm and let pygame draw 
        # one full node processed per "frame"
        yield False 
                
    logging.info("DFS No path exists")
    yield True 

    def heuristic(p1, p2):
        """Manhattan distance: |x1 - x2| + |y1 - y2|"""
        (r1, c1) = p1 
        (r2, c2) = p2
        return abs(r1 - r2) + abs(c1 - c2)


    def astar(grid, start, end):
        allowed_terrain = start.terrain

        # The count variable ensures that if two nodes have the same f-score, 
        # the algorithm picks the one added first rather than trying to compare 
        # the Node objects
        count = 0       # tie-breaker for nodes with same f-score 
        open_set = [] 

        # priority queue stores (f_score, count, node) 
        # heapq is a min-heap. Always returns the item with the lowest value
        # compares index 0 values (f_score).
        # If two tuples have the same f_score, it moves to index 1 (count) 
        # and picks the one with the lower count (one added to queue first)
        # Count prevents comparing node objecst for node1 < node2
        h_start = heuristic((start.row, start.col), (end.row, end.col)) * PATH_COST.DIAGONAL
        heapq.heappush(open_set, (h_start, h_start, count, start))

        came_from = {} 
        g_score = {node: float("inf") for row in grid.map for node in row}
        g_score[start] = 0 

        f_score = {node: float("inf") for row in grid.map for node in row}
        f_score[start] = heuristic((start.row, start.col), (end.row, end.col))

        open_set_hash = {start}  # to check if node is already in priority queue

        while open_set:
            # pop tuple with the lowest f_score
            current = heapq.heappop(open_set)[3]        # gets node object stored in tuple
            if current in open_set_hash:
                open_set_hash.remove(current)
            logging.info(f"current: {current}")

            if current == end:
                logging.info(f"A* path found!")
                reconstruct_path(end)
                yield True 
                return 
            
            for neighbor in get_neighbors(current, grid):
                if neighbor.terrain != allowed_terrain or neighbor.closed:
                    continue

                tentative_g_score = g_score[current] + PATH_COST.CARDINAL

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current 
                    neighbor.parent = current 
                    g_score[neighbor]  = tentative_g_score 
                    h_score = heuristic((neighbor.row, neighbor.col), (end.row, end.col)) * PATH_COST.DIAGONAL
                    f_score[neighbor] = tentative_g_score + h_score 
                    count += 1 
                    # Store: (f_score, h_score, count, neighbor)
                    # 1st priority: lowest total cost (f)
                    # 2nd priority: lowest distance to goal (h)
                    # 3rd priority: oldest node (count)
                    heapq.heappush(open_set, (f_score[neighbor], h_score, count, neighbor))

                    if neighbor not in open_set_hash:
                        open_set_hash.add(neighbor) 
                        neighbor.visited = True  
            
            yield False # signal that we took one step
            if current != start:
                current.closed = True 
        
        logging.info(f"A* no path found")
        return False  # No path found


