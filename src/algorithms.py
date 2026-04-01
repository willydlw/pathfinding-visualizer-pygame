from collections import deque 
import logging 

from .grid import Grid 

logger = logging.getLogger(__name__)


def get_neighbors(node, grid_map):
    """
    Returns a list of valid, walkable Node neighbors (Up, Down, Left, Righ)
    """

    neighbors = []
    rows = len(grid_map)
    cols = len(grid_map[0])

    # Adjacent relative positions (row_offset, col_offset)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in indices:
        r, c = node.row + dr, node.col + dc 

        # Boundary check 
        if 0 <= r < rows and 0 <= c < cols:
            neighbor = grid_map[r][c]
        if neighbor.terrain == node.terrain:
            neighbors.append(neighbor)

    return neighbors


def bfs(grid):
    """
    Performs a Breadth-First-Search on the grid.
    Returns the end node if path found, else None
    """

    if not grid.start_pos or not grid.end_pos:
        logger.warning("Start or End position not set!")
        return None 

    # Get node objects from coordinates 
    start_node = grid.map[grid.start_pos[0]][grid.start_pos[1]]
    end_node = grid.map[grid.end_pos[0]][grid.end_pos[1]]


    # enqueue the starting node
    queue =deque([start_node]) 

    # mark the starting node as visited 
    start_node.visited = True 
   

    while queue:
        # dequeue the front node
        current = queue.popleft()

        if current == end_node:
            logging.info("Path found!")
            return end_node 

        # for every unvisited neighbor of the current node,
        # mark it as
        for neighbor in get_neighbors(current, grid.map):
            if not neighbor.visited:
                neighbor.visited = True 
                neighbor.parent = current   # Link for path reconstruction
                queue.append(neighbor)

    logging.info("No path exists")
    return None 