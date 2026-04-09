# =========================================================
# WEEK 4: CLOUD-EDGE TASK SCHEDULING SIMULATION
# Features:
# - BFS Traversal
# - Greedy Task Allocation
# - Load Tracking
# - Graph Visualization with Loads
# =========================================================

# ---------------- IMPORTS ----------------
from collections import deque
import networkx as nx
import matplotlib.pyplot as plt


# ---------------- GRAPH DEFINITION ----------------
graph = {
    "Edge1": ["Edge2", "Cloud"],
    "Edge2": ["Edge1", "Cloud"],
    "Cloud": ["Edge1", "Edge2"]
}

# Node properties (loads)
nodes = {
    "Edge1": {"load": 5},
    "Edge2": {"load": 2},
    "Cloud": {"load": 8}
}


# ---------------- BFS FUNCTION ----------------
def bfs(graph, start_node):
    """
    Performs Breadth-First Search traversal
    """
    visited = set()
    queue = deque([start_node])

    print("\n=== BFS TRAVERSAL ===")

    while queue:
        current = queue.popleft()

        if current not in visited:
            print(f"Visited: {current}")
            visited.add(current)

            for neighbor in graph[current]:
                queue.append(neighbor)


# ---------------- GREEDY ALGORITHM ----------------
def select_least_loaded_node(nodes):
    """
    Selects node with the smallest load
    """
    return min(nodes, key=lambda node: nodes[node]["load"])


def simulate_task_allocation(num_tasks):
    """
    Assigns tasks using Greedy approach
    """
    print("\n=== TASK ALLOCATION (GREEDY) ===")

    for task in range(1, num_tasks + 1):
        chosen_node = select_least_loaded_node(nodes)

        print(f"\nTask {task}")
        print(f"Assigned to: {chosen_node}")
        print(f"Previous Load: {nodes[chosen_node]['load']}")

        # Update load
        nodes[chosen_node]["load"] += 1

        print(f"New Load: {nodes[chosen_node]['load']}")


# ---------------- GRAPH VISUALIZATION ----------------
def visualize_graph(graph, nodes):
    """
    Displays the graph with node loads
    """
    G = nx.Graph()

    # Add edges
    for node in graph:
        for neighbor in graph[node]:
            G.add_edge(node, neighbor)

    # Create labels with load info
    labels = {
        node: f"{node}\nLoad: {nodes[node]['load']}"
        for node in nodes
    }

    plt.figure()
    nx.draw(G, with_labels=True, labels=labels, node_size=2000)
    plt.title("Cloud-Edge Network with Load Distribution")
    plt.show()


# ---------------- MAIN PROGRAM ----------------
def main():
    print("===== CLOUD-EDGE COMPUTING SIMULATION =====")

    # Step 1: BFS Traversal
    bfs(graph, "Edge1")

    # Step 2: Task Allocation
    simulate_task_allocation(5)

    # Step 3: Graph Visualization
    visualize_graph(graph, nodes)

    input("\nPress Enter to exit...")


# ---------------- PROGRAM ENTRY ----------------
if __name__ == "__main__":
    main()