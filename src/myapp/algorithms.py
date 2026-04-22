from collections import deque 
import heapq 
import logging 
import random 

from .grid import Grid 
from .constants import Neighbor_Order


logger = logging.getLogger(__name__)


def get_ordered_neighbors(current, grid, strategy=Neighbor_Order.RANDOM):
    neighbors = get_neighbors(current, grid)

    if strategy == Neighbor_Order.RANDOM:
        random.shuffle(neighbors)
    
    return neighbors


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


def bfs(grid, start_node, end_node, neighbor_order):
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


def dfs(grid, start_node, end_node, neighbor_order):
    """
    Performs a Depth-First Search on the grid.
    """

    # Use a list as a stack (LIFO)
    stack = [start_node]
    start_node.visite = True 
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



def manhattan_distance(p1, p2):
    """Manhattan distance: |x1 - x2| + |y1 - y2|"""
    return abs(p1.row - p2.row) + abs(p1.col - p2.col)


def astar(grid, start, end, neighbor_order):

    # Path can only traverse the same terrain as the start and end nodes.
    allowed_terrain = start.terrain 

    # Reset grid states 
    for row in grid.map:
        for node in row:
            node.g = float("inf")
            node.f = float("inf")
            node.visited = False 
            node.closed = False 
            node.parent = None 
    

    # Start node setup
    start.g = 0     # g is cost from start to current node 
    start.h = manhattan_distance(start, end) * 10  # estimate of cost from current node to the goal
    start.f = start.g + start.h 

    # Used as priority queue tie-breaker when f and h costs are equal
    count = 0       

    # Initialize empty list
    open_list = [] 

    # To optimize checking for node in open_list, use open_set in tandem 
    # Searching a python list is 0(n) and checking a set is 0(1) constant time
    # Note: __eq__ and __hash__ implemented in Node class
    open_set = {start}      # hash set for fast lookups 

    
    # Place start node into the priority queue 
    # heapq manages a standard python list as a binary heap.
    # heappush(open_list, item) adds the item and rearranges the list 
    # to ensure the lowest cost is at open_list[0]

    # tuple ordering: The open_list usually stores tuples such as (total_cost, position).
    # heapq compares tuples lexicographically

    # heapq is a min-heap. 
    # Always returns the item with the lowest value by comparing tuple values
    # Our tuple: (f_cost, h_cost, count, neighbor_node)
    # 1st priority: lowest total cost (f)
    # 2nd priority: lowest distance to goal (h)
    # 3rd priority: oldest node (count)   

    # To determine lowest value, f_costs (tuple index 0) are compared
    # If there is a tie with more than one item in the list having the same 
    # lowest f_cost, then the 2nd priority comparison of h_cost is used 
    # to find the item with the lowest value.
    
    # If two tuples have the same f_cost and h_cost, it then compares
    # and picks the one with the lower count (one added to queue first)
    # Count prevents comparing node objecst for node1 < node2

    # Places start node in the open list
    heapq.heappush(open_list, (start.f, start.h, count, start))


    while open_list:

        # Find the node in open list with the lowest f(n) value
        # pop off lowest cost node
        current = heapq.heappop(open_list)[3]        # Tuple index 3 location of stored node

        if current in open_set:
            open_set.remove(current)

        # Optimization: Skip if we have already closed this node 
        # Handles duplicates from the lazy neighbor removal strategy 
        if current.closed:
            continue 

        # Get current's sucessor neighbor nodes
        for neighbor in get_neighbors(current, grid):
            if neighbor.terrain != allowed_terrain or neighbor.closed:
                continue

            # Calculate tentative g score (cost from start to this neighbor)
            tentative_g = current.g + 10

            # Update costs if this new path is better
            if tentative_g < neighbor.g:
                neighbor.parent = current 
                neighbor.g = tentative_g 
                neighbor.h = manhattan_distance(neighbor, end) * 10
                neighbor.f = neighbor.g + neighbor.h 

                logging.info(f"STEP LOG: Node({neighbor.row},{neighbor.col}) G={neighbor.g}, F={neighbor.f}")

                # Check if this neighbor is the end node
                if neighbor == end:
                    logging.info(f"A* path found")
                    reconstruct_path(end)
                    yield True 
                    return
            
                # Push the new, better path into the heap.
                # Even if the neighbor is already in the open list, this new 
                # entry will have a lower f cost and be processed first. (Lazy removal)
                # Later when the higher f cost of this same neighbor is remove from 
                # the open list, it will be marked as closed and not processed again.
                count += 1 
                heapq.heappush(open_list, (neighbor.f, neighbor.h, count, neighbor))
                neighbor.visited = True  # for visualizing the open set
        
        # Mark closed only after all neighbors are processed
        if current != start:
            current.closed = True 

        yield False # Signal visualization one step taken 
    
    logging.info(f"A* no path found")
    return False  # No path found


