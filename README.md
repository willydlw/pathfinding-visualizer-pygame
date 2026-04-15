

For inspiration:

https://github.com/Tauseef-Hilal/Pathfinding-Visualizer/tree/main

https://github.com/atsushisakai/pythonrobotics

https://github.com/zhm-real/pathplanning



TODO:

SideBar class 

        # Mapping 
        # Label: Environment Map 
        # Default (64x64) with a default map loaded
        # Small (8x8)
        # L-shaped wall (16 x 16)
        # Sparse Canvas (128 x 128)
        # Dense Canvas (256 x 256)
        # Maze (128 x 128)

        # Legal Actions
        # Object must be within the map bounds 
        # Move in 4 directions Cardinal (4 neighbors)
        # Move in 8 directions Diagonal (8 neighbors)
        # Object can only move to a space if it is the same color as where it is currently
        # Object cannot move off the map
        # Action costs are all 100 for width, height and approx 141 for diagonal

        # Toggle Grid button that turns displaying grid on/off

        # Object Size
        # TODO: Select size of object finding its path
        # Examples: 1x1 Square, 2x2 square

        # Animation Visualization Control
        # TODO: Visualization Label
        # Choice: Instant Path, 
        #       Animated Search (select animation speed). When this option is selected
        #       show another button with default of 1x Speed (which shows every iteration of the search)
        #       and provides dropdown choices of 2x, 4x, 8x, 16x 32x speed
        #           Draw path between start and current node when showing animation 
        #           Show closed (visited) set in special color 
        #           Show open set in special color

        #       Single Step (click button for each iteration) (good for debugging)

        # TODO: Button for "Rerun Previous Path"
        # TODO: Button for Run Tests
        #           Show test result stats
        # TODO: Random Tests (maze generation with random start/stop?)

        # TODO: Show Stats 
        # Headings: Search(algo), Start (location), Goal(location), Cost, Closed (number in closed set?)
        # Time, Node/sec?

        # Show instructions
        # Search Visualization Instructions 
        # How to set start and goal tiles 
        # Object can only move through same color tiles in the grid 
        # Choose Animate Search visualization to see real-time search progress 
        # Re-Run Previous - Performs previous search again (useful when animating)


        # Visualization Legend 
        # Blue/Green/Gray tiles: terrain type, object can move within a color 
        # Red Tile - Node is in closed list (has been expanded)
        # Orange Tile - Node is in open list (generated, but not expanded)
        # White Tile - Node is on the generated path


## A* (A-star) Algorithm 

A* is an informed path finding and graph traversal algorithm used to find the shortest path between two nodes. It is considered an extension of Dijkstra's algorithm that uses **heuristics** to prioritize nodes, making it significantly faster and more efficient than non-informed pathfinding algorithms.

### Core Function: The Evaluation Function 

A* evaluates node using the following formula: **f(n) = g(n) + h(n)**

- **g(n)**: The actual cost of the path from the starting node to the current node n.
- **h(n)**: The estimated *heuristic* cost to get from node n to the goal.
- **f(n)**: The total estimated cost of the lowest-cost path through node n.

### How the Algorithm Works 

The algorithm maintains two sets: an **open List** (nodes to be explored) and a **closed list** (nodes that are already evaluated).

1. **Initialize**: Place the start node in the Open List.
2. **Selection**: Pick the node in hte Open list with the lowest f(n) value.
3. **Expansion**: Check all neighbors of that node. Calculate their f(n) values and add them to the open list if they haven't been visited or if a better path to them is found.
4. **Completion**: Repeat until the goal node is reached or the open list is empty (meaning no path exists).


### Common Heuristics

The choice of h(n) depends on the type of movement allowed:

- **Manhattan Distance**: Used when movement is restricted to four directions (up, downn, left, right).
- **Euclidean Distance**: Used for straight-line movement in any direction.
- **Chebyshev Distance**: Used when 8-way diagonal movement is allowed.

### Key Properties 

- **Optimality**: A* is guaranteed to find the shortest path if the heuristic is **admissible** (it nover overestimates the actual cost to the goal.)

- **Completeness**: It will always find a path if one exists.

- **Efficiency**: By using a heuristic, it avoids exploring unnecessary directions, unlike Breadh-First Search (BFS) or Dijkstra.


### Search Bias
UI Implementation (Pygame GUI)
Since you are already using a dropdown for "Algorithm," you can add a second dropdown for "Search Bias":
Dropdown Options: ["Random", "Clockwise", "Counter-Clockwise", "Prefer Vertical", "Prefer Horizontal"]
The "Pop" Logic: Remind users (via a tooltip or label) that in a Stack (DFS), the last neighbor added is the first one visited. So, if they want to go "Right," they should ensure "Right" is at the end of the neighbor list.
Why this is helpful for the user:
Random: Shows a "drunkard's walk" path.
Clockwise: Shows the algorithm perfectly hugging the "outside" of every obstacle it encounters.
Horizontal/Vertical Bias: Shows how DFS can be "tricked" into exploring the entire map inefficiently if the goal is in the opposite direction.


## Breadth-First Search

In a Breadth-First Search (BFS) on a 2D grid, search "bias" refers to the non-random order in which the algorithm explores cells that are at the same distance from the starting point. While BFS is mathematically guaranteed to find the shortest path in an unweighted grid, the specific sequence it uses to visit equidistant neighbors introduces subtle directional biases. 

Directional Bias (Adjacency Ordering)
The most common bias in a 2D grid search is determined by the order in which a cell's neighbors are added to the queue data structure. 
Fixed Sequence: Developers typically define a direction vector like [Up, Right, Down, Left].
Exploration Pattern: If multiple paths to a target have the same length, BFS will consistently return the one that follows this predefined order. For example, if "Right" is enqueued before "Down," the algorithm will systematically favor horizontal expansion over vertical when both are equally viable.

Lack of Heuristic Bias (Uninformed Search) 
Unlike A* Search, BFS is an uninformed search. 

Radial Expansion: It expands in all directions equally (forming a diamond or circle shape) because it has no "bias" toward the goal.

Inefficiency: This lack of goal-oriented bias means it must visit every node at distance before it can even consider a node at distance, making it slower for simple point-to-point pathfinding on large grids. 

Implementation-Specific Biases
Tie-Breaking: If two different paths reach the same cell at the same time, the one added to the queue first (based on the neighbor-processing loop) becomes the "official" shortest path in the parent-tracking map.


### Neighbor Connectivity 

Neighbors are defined by the connectivity of the grid, which are the cells an agent can move to from its current position.

1. Connectivity Types (Types of Neighbors)

The number of neighbors defines the movement restrictions:

- **4-Connectivity (Von Neumann Neighborhood):** Neighbors are adjacent orthonally - up, down, left, right. This represents the "Manhattan" movement pattern.

- **8-Connectivity (Moore Neighborhood):** Neighbors include the 4 orthonal cells plus the 4 diagonal cells (up-left, up-right, down-left, down-right). This is used when diagonal movement is allowed.

2. Technical Definition Methods 

Neighbors are defined by the change ins coordinates (dx, dy) from the current cell(x, y).

**Cardinal Movement (4-Neighbors)** 

- Neighbors: (x, y+1), (x, y-1), (x+1, y), (x-1, y)

- Implementation: A loop using relative coordinates: [(0, 1), (0, -1), (1, 0), (-1, 0)]

**Cardinal + Diagonal Movement (8-Neighbors)** 

- Neigbors: 4-neighbors plus (x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1)

- Implementation: A loop using relative coordinates, including diagonals: [(0, 1), (0, -1), (1, 0), (-1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

3. Key Considerations When Defining Neighbors 

- **Boundary Checking:** Ensure neighbor coordinates do not go outside the grid array bounds.
- **Obstacle Checking:** Ensure the neighbor is not a non-walkable tile.
- **Diagonal Cut-corner Check:** In 8-connectivity, you may want to prevent the agent from moving diagonally through the corner of two obstacles. This requires checking if both adjacent orthogonal cells are walkable.
- **Traversal Cost:** Orthogonal neighbors usually have a cost of 1, which diagonal neighbors have a cost of square root(2), approx 1.41.