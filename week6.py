"""
Week 6: Optimization Algorithms – DP and Heuristic

This module implements:
- Windowed Dynamic Programming (optimal for small windows).
- Deadline‑aware Heuristic with locality bonus and urgency penalty.
- Complexity analysis and comparison with greedy.
"""

import random
import copy
from collections import deque

# ============================================================
# Node and Task Models (reused from Week 2)
# ============================================================
NODES = {
    "Edge1": {"cpu": 6,  "energy_per_task": 3, "latency": 4,  "load": 0},
    "Edge2": {"cpu": 4,  "energy_per_task": 2, "latency": 6,  "load": 0},
    "Cloud": {"cpu": 20, "energy_per_task": 1, "latency": 25, "load": 0},
}

def generate_tasks(num_tasks, seed=42):
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

def compute_latency(task, node_name, nodes):
    node = nodes[node_name]
    base = node["latency"]
    processing = (task["size"] / node["cpu"]) * 10
    load_penalty = node["load"] * 0.5
    return base + processing + load_penalty

# ============================================================
# Dynamic Programming (Windowed Optimal)
# Complexity: O(T * N^W) where W = window size
# ============================================================
def dp_allocate(tasks, nodes_init, window=5):
    """DP over sliding windows. Minimises total latency per window."""
    nodes = copy.deepcopy(nodes_init)
    results = []
    for w_start in range(0, len(tasks), window):
        window_tasks = tasks[w_start:w_start + window]
        node_names = list(nodes.keys())
        n = len(node_names)
        w = len(window_tasks)

        # DP table: dp[task_idx][node_idx] = min cumulative latency
        dp = [[float('inf')] * n for _ in range(w)]
        assign = [[None] * n for _ in range(w)]  # for backtracking

        # Snapshot loads at start of window
        load_snap = {nd: nodes[nd]["load"] for nd in node_names}

        # Fill DP table
        for t_idx, task in enumerate(window_tasks):
            for n_idx, node_name in enumerate(node_names):
                # Simulate load as if all previous tasks in window went to this node
                sim_nodes = copy.deepcopy(nodes)
                sim_nodes[node_name]["load"] = load_snap[node_name] + task["size"] * t_idx
                lat = compute_latency(task, node_name, sim_nodes)
                cost = lat

                if t_idx == 0:
                    dp[t_idx][n_idx] = cost
                    assign[t_idx][n_idx] = node_name
                else:
                    best_prev = min(dp[t_idx - 1])
                    total = best_prev + cost
                    if total < dp[t_idx][n_idx]:
                        dp[t_idx][n_idx] = total
                        assign[t_idx][n_idx] = node_name

        # Extract assignments from DP table
        for t_idx, task in enumerate(window_tasks):
            best_n_idx = dp[t_idx].index(min(dp[t_idx]))
            chosen = assign[t_idx][best_n_idx]
            latency = compute_latency(task, chosen, nodes)
            energy = nodes[chosen]["energy_per_task"] * task["size"]
            missed = latency > task["deadline"]
            nodes[chosen]["load"] += task["size"]
            results.append({
                "task_id": task["id"],
                "node": chosen,
                "latency": round(latency, 2),
                "energy": energy,
                "missed": missed,
                "deadline": task["deadline"],
            })
    return results, nodes

# ============================================================
# Heuristic: Deadline-aware + Locality Bonus
# Complexity: O(T * N)
# ============================================================
def heuristic_allocate(tasks, nodes_init):
    """Score = latency + urgency*2 + 0.5*energy - locality_bonus."""
    nodes = copy.deepcopy(nodes_init)
    results = []
    for task in tasks:
        best_node = None
        best_score = float('inf')
        for node_name in nodes:
            latency = compute_latency(task, node_name, nodes)
            energy = nodes[node_name]["energy_per_task"] * task["size"]
            urgency = max(0, latency - task["deadline"]) * 2
            locality_bonus = -3 if node_name == task["location"] else 0
            score = latency + urgency + energy * 0.5 + locality_bonus
            if score < best_score:
                best_score = score
                best_node = node_name

        latency = compute_latency(task, best_node, nodes)
        energy = nodes[best_node]["energy_per_task"] * task["size"]
        missed = latency > task["deadline"]
        nodes[best_node]["load"] += task["size"]
        results.append({
            "task_id": task["id"],
            "node": best_node,
            "latency": round(latency, 2),
            "energy": energy,
            "missed": missed,
            "deadline": task["deadline"],
        })
    return results, nodes

# ============================================================
# Metrics and Complexity Report
# ============================================================
def print_metrics(results, policy_name):
    total = len(results)
    missed = sum(1 for r in results if r["missed"])
    total_energy = sum(r["energy"] for r in results)
    avg_lat = sum(r["latency"] for r in results) / total
    print(f"\n{policy_name}:")
    print(f"  Missed deadlines: {missed}/{total} ({100*missed/total:.1f}%)")
    print(f"  Total energy: {total_energy} units")
    print(f"  Avg latency: {avg_lat:.2f} ms")

def complexity_report():
    print("\n" + "="*50)
    print("Complexity Analysis")
    print("="*50)
    print("DP (windowed):   O(T × N^W) – exponential in window size")
    print("Heuristic:       O(T × N) – linear in tasks and nodes")
    print("Greedy (Week4):  O(T × N)")
    print("Note: Global optimal scheduling is NP-hard.")

# ============================================================
# Demonstration
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("Week 6: Optimization Algorithms Demo")
    print("=" * 50)

    # Generate tasks
    tasks = generate_tasks(20, seed=42)
    print(f"\nGenerated {len(tasks)} tasks.")

    # Run DP (window size = 5)
    dp_results, dp_nodes = dp_allocate(tasks, NODES, window=5)
    print_metrics(dp_results, "Dynamic Programming (window=5)")

    # Run Heuristic
    heur_results, heur_nodes = heuristic_allocate(tasks, NODES)
    print_metrics(heur_results, "Heuristic (deadline-aware)")

    # Complexity report
    complexity_report()