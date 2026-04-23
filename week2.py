"""
Week 2: System Modeling for Cloud-Edge Resource Allocation

This module defines:
- Computing nodes with CPU, energy per task, latency, and load.
- Task generation with size, deadline, and data location.
- Data structures for task queues and node states.
- Memory analysis (printed at the end).
"""

import random
from collections import deque

# ============================================================
# Node Definitions
# ============================================================
NODES = {
    "Edge1": {"cpu": 6,  "energy_per_task": 3, "latency": 4,  "load": 0},
    "Edge2": {"cpu": 4,  "energy_per_task": 2, "latency": 6,  "load": 0},
    "Cloud": {"cpu": 20, "energy_per_task": 1, "latency": 25, "load": 0},
}

# ============================================================
# Task Model
# ============================================================
def generate_tasks(num_tasks, seed=42):
    """
    Generate a list of tasks.
    Each task: id, size (1-10), deadline (10-50 ms), location (Edge1/Edge2)
    """
    random.seed(seed)
    tasks = []
    for i in range(1, num_tasks + 1):
        tasks.append({
            "id": i,
            "size": random.randint(1, 10),
            "deadline": random.randint(10, 50),
            "location": random.choice(["Edge1", "Edge2"]),
        })
    return tasks

# ============================================================
# Data Structures & Memory Analysis
# ============================================================
def memory_analysis(num_tasks):
    """
    Estimate memory usage of the simulation data structures.
    """
    # Approximate sizes (in bytes) for Python objects
    task_overhead = 72  # dict overhead + keys
    per_task_attrs = 4 * 28  # each attribute (int/str) ~28 bytes
    total_per_task = task_overhead + per_task_attrs  # ~184 bytes
    tasks_memory = num_tasks * total_per_task

    node_overhead = 64
    per_node_attrs = 4 * 28
    total_per_node = node_overhead + per_node_attrs
    nodes_memory = len(NODES) * total_per_node

    print("\n=== Memory Analysis ===")
    print(f"Tasks ({num_tasks}): ~{tasks_memory / 1024:.2f} KB")
    print(f"Nodes ({len(NODES)}): ~{nodes_memory / 1024:.2f} KB")
    print(f"Total (approx): {(tasks_memory + nodes_memory) / 1024:.2f} KB")
    print("Note: Memory scales linearly with number of tasks.")

# ============================================================
# Demonstration
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("Week 2: System Modeling Demo")
    print("=" * 50)

    # Show node characteristics
    print("\n--- Node Characteristics ---")
    for name, attrs in NODES.items():
        print(f"{name}: CPU={attrs['cpu']} tasks/s, "
              f"Energy/task={attrs['energy_per_task']}, "
              f"Base latency={attrs['latency']} ms, Load={attrs['load']}")

    # Generate tasks
    tasks = generate_tasks(10, seed=42)
    print(f"\n--- Generated {len(tasks)} Tasks (first 3 shown) ---")
    for t in tasks[:3]:
        print(f"Task {t['id']}: size={t['size']}, deadline={t['deadline']} ms, location={t['location']}")

    # Memory analysis
    memory_analysis(20)  # typical simulation size