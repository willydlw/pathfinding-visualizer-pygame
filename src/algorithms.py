from collections import deque 
import logging 

from .grid import Grid 

logger = logging.getLogger(__name__)


def get_neighbors(node, grid):
    """
    Returns a list of valid, walkable Node neighbors (Up, Down, Left, Righ)
    """

    neighbors = []
    allowed_terrain = grid.start_node.terrain 

    rows = grid.rows
    cols = grid.cols

    # Adjacent relative positions (row_offset, col_offset)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        r, c = node.row + dr, node.col + dc 

        # Boundary check 
        if 0 <= r < rows and 0 <= c < cols:
            neighbor = grid.map[r][c]
            if neighbor.terrain == allowed_terrain:
                neighbors.append(neighbor)

    return neighbors


def reconstruct_path(end_node):
    """Backtracks from the end node to the start node to mark the path."""
    curr = end_node.parent      # start with node before the end
    while curr and not curr.is_start:
        curr.path = True 
        curr = curr.parent 


def bfs(grid):
    """
    Performs a Breadth-First-Search on the grid.
    Returns the end node if path found, else None
    """

    if not grid.start_node or not grid.end_node:
        logger.warning("Start or End node not set!")
        yield True  # Signal finished so the app doesn't hang
        return
    
    start_node = grid.start_node 
    end_node = grid.end_node


    # enqueue the starting node and mark as visited
    queue =deque([start_node]) 
    start_node.visited = True 
   
    while queue:
        current = queue.popleft()

        if current == end_node:
            logging.info("Path found!")
            reconstruct_path(current)
            yield True   # Signal to PathFinder App that search is done
            return       # Stop the generator 

        for neighbor in get_neighbors(current, grid):
            if not neighbor.visited:
                neighbor.visited = True 
                neighbor.parent = current   # Link for path reconstruction
                queue.append(neighbor)

                # yield here to pause the algorithm and let pygame draw 
                yield False 

    logging.info("No path exists")
    yield True 