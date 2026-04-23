# =========================================================
# CAPSTONE PROJECT: RESOURCE ALLOCATION IN CLOUD-EDGE CONTINUUM
# Group Project 8
#
# Weeks Covered:
#   Week 2 - System Modeling (nodes, tasks, data structures)
#   Week 4 - Graph Representation + BFS + Greedy Scheduler
#   Week 6 - Dynamic Programming + Policy Comparison
#   Week 7 - Complete Simulator + Metrics + Plots
#
# Policies Implemented:
#   1. Greedy   - Assign to fastest/least-loaded node
#   2. DP       - Optimal allocation over short time windows
#   3. Heuristic - Load balancing with deadline awareness
#
# Metrics Tracked:
#   - Missed deadlines per policy
#   - Total energy consumed per policy
#   - Average latency per policy
# =========================================================

import random
import copy
import time
from collections import deque

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


# ===========================================================
# WEEK 2: SYSTEM MODELING
# ===========================================================

# ---------------- NODE DEFINITIONS ----------------
# Each node has: cpu (tasks/sec), energy per task, latency (ms)

NODES = {
    "Edge1": {"cpu": 6,  "energy_per_task": 3, "latency": 4,  "load": 0},
    "Edge2": {"cpu": 4,  "energy_per_task": 2, "latency": 6,  "load": 0},
    "Cloud": {"cpu": 20, "energy_per_task": 1, "latency": 25, "load": 0},
}

# Network graph (adjacency list)
GRAPH = {
    "Edge1": ["Edge2", "Cloud"],
    "Edge2": ["Edge1", "Cloud"],
    "Cloud": ["Edge1", "Edge2"],
}

# ---------------- CONFIGURABLE PARAMETERS ----------------
NUM_TASKS        = 20     # Total tasks to simulate
TIME_WINDOW      = 5      # DP window size (tasks per window)
RANDOM_SEED      = 42     # For reproducibility


# ---------------- TASK GENERATOR ----------------
def generate_tasks(num_tasks, seed=RANDOM_SEED):
    """
    Week 2: Task model
    Each task has:
      - size     : computational load (1–10 units)
      - deadline : time limit in ms (10–50ms)
      - location : data origin node (edge locality)
    """
    random.seed(seed)
    tasks = []
    for i in range(1, num_tasks + 1):
        tasks.append({
            "id":       i,
            "size":     random.randint(1, 10),
            "deadline": random.randint(10, 50),
            "location": random.choice(["Edge1", "Edge2"]),
        })
    return tasks


# ===========================================================
# WEEK 4: GRAPH-BASED REPRESENTATION + BFS
# ===========================================================

def bfs(graph, start_node):
    """
    BFS traversal of the compute network.
    Complexity: O(V + E)
    """
    visited = set()
    queue   = deque([start_node])
    order   = []

    while queue:
        current = queue.popleft()
        if current not in visited:
            visited.add(current)
            order.append(current)
            for neighbor in graph[current]:
                if neighbor not in visited:
                    queue.append(neighbor)

    return order


def bfs_shortest_path(graph, start, target):
    """
    BFS to find shortest path between two nodes.
    Used to estimate routing latency.
    """
    visited = {start}
    queue   = deque([[start]])

    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == target:
            return path
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return []


# ===========================================================
# SHARED UTILITY: Compute task latency on a given node
# ===========================================================

def compute_latency(task, node_name, nodes):
    """
    Estimated processing time (ms):
      base latency + size / cpu + load penalty
    """
    node        = nodes[node_name]
    base        = node["latency"]
    processing  = (task["size"] / node["cpu"]) * 10   # scaled to ms
    load_penalty = node["load"] * 0.5
    return base + processing + load_penalty


# ===========================================================
# POLICY 1: GREEDY — Assign to least-loaded node
# Week 4 requirement
# ===========================================================

def greedy_allocate(tasks, nodes_init):
    """
    Greedy policy: always pick the node with the smallest current load.
    O(T * N) where T=tasks, N=nodes.
    """
    nodes   = copy.deepcopy(nodes_init)
    results = []

    for task in tasks:
        # Pick node with minimum load
        chosen = min(nodes, key=lambda n: nodes[n]["load"])

        latency  = compute_latency(task, chosen, nodes)
        energy   = nodes[chosen]["energy_per_task"] * task["size"]
        missed   = latency > task["deadline"]

        nodes[chosen]["load"] += task["size"]

        results.append({
            "task_id":  task["id"],
            "node":     chosen,
            "latency":  round(latency, 2),
            "energy":   energy,
            "missed":   missed,
            "deadline": task["deadline"],
        })

    return results, nodes


# ===========================================================
# POLICY 2: DYNAMIC PROGRAMMING — Optimal short-window allocation
# Week 6 requirement
# DP recurrence:
#   dp[i][j] = min cost to assign task i to node j
#   considering cumulative load at each node
# ===========================================================

def dp_allocate(tasks, nodes_init, window=TIME_WINDOW):
    """
    DP over sliding windows of `window` tasks.
    Minimises total latency within each window.
    Complexity: O(T * N^W) — exponential in window, pseudo-polynomial overall.
    """
    nodes   = copy.deepcopy(nodes_init)
    results = []

    # Process tasks in windows
    for w_start in range(0, len(tasks), window):
        window_tasks = tasks[w_start : w_start + window]
        n_nodes      = list(nodes.keys())
        n            = len(n_nodes)
        w            = len(window_tasks)

        # dp[task_idx][node_idx] = best cumulative latency up to this task
        INF = float("inf")
        dp      = [[INF] * n for _ in range(w)]
        assign  = [[None] * n for _ in range(w)]   # backtrack

        # Snapshot loads at window start
        load_snap = {nd: nodes[nd]["load"] for nd in n_nodes}

        # Fill DP table
        for t_idx, task in enumerate(window_tasks):
            for n_idx, node_name in enumerate(n_nodes):

                # Simulate load as if all previous tasks went to this node
                sim_nodes = copy.deepcopy(nodes)
                sim_nodes[node_name]["load"] = (
                    load_snap[node_name] + task["size"] * t_idx
                )

                lat  = compute_latency(task, node_name, sim_nodes)
                cost = lat  # minimise latency

                if t_idx == 0:
                    dp[t_idx][n_idx]     = cost
                    assign[t_idx][n_idx] = node_name
                else:
                    best_prev = min(dp[t_idx - 1])
                    total     = best_prev + cost
                    if total < dp[t_idx][n_idx]:
                        dp[t_idx][n_idx]     = total
                        assign[t_idx][n_idx] = node_name

        # Extract assignments from DP table
        for t_idx, task in enumerate(window_tasks):
            best_n_idx = dp[t_idx].index(min(dp[t_idx]))
            chosen     = assign[t_idx][best_n_idx]

            latency = compute_latency(task, chosen, nodes)
            energy  = nodes[chosen]["energy_per_task"] * task["size"]
            missed  = latency > task["deadline"]

            nodes[chosen]["load"] += task["size"]

            results.append({
                "task_id":  task["id"],
                "node":     chosen,
                "latency":  round(latency, 2),
                "energy":   energy,
                "missed":   missed,
                "deadline": task["deadline"],
            })

    return results, nodes


# ===========================================================
# POLICY 3: HEURISTIC — Deadline-aware load balancing
# Week 6 / Week 7 requirement
# ===========================================================

def heuristic_allocate(tasks, nodes_init):
    """
    Heuristic: score each node by combined latency + deadline urgency.
    Prefer edge nodes for tight deadlines (low latency).
    Prefer cloud for large tasks with relaxed deadlines.
    O(T * N).
    """
    nodes   = copy.deepcopy(nodes_init)
    results = []

    for task in tasks:
        best_node  = None
        best_score = float("inf")

        for node_name in nodes:
            latency = compute_latency(task, node_name, nodes)
            energy  = nodes[node_name]["energy_per_task"] * task["size"]

            # Urgency factor: penalise nodes likely to miss deadline
            urgency = max(0, latency - task["deadline"]) * 2

            # Prefer data-local nodes (same as task origin)
            locality_bonus = -3 if node_name == task["location"] else 0

            score = latency + urgency + energy * 0.5 + locality_bonus

            if score < best_score:
                best_score = score
                best_node  = node_name

        latency = compute_latency(task, best_node, nodes)
        energy  = nodes[best_node]["energy_per_task"] * task["size"]
        missed  = latency > task["deadline"]

        nodes[best_node]["load"] += task["size"]

        results.append({
            "task_id":  task["id"],
            "node":     best_node,
            "latency":  round(latency, 2),
            "energy":   energy,
            "missed":   missed,
            "deadline": task["deadline"],
        })

    return results, nodes


# ===========================================================
# METRICS COLLECTION
# ===========================================================

def collect_metrics(results, policy_name):
    """
    Aggregate metrics from a policy run.
    """
    total_tasks    = len(results)
    missed         = sum(1 for r in results if r["missed"])
    total_energy   = sum(r["energy"] for r in results)
    avg_latency    = sum(r["latency"] for r in results) / total_tasks

    print(f"\n{'='*50}")
    print(f"  POLICY: {policy_name}")
    print(f"{'='*50}")
    print(f"  Tasks simulated  : {total_tasks}")
    print(f"  Missed deadlines : {missed}  ({100*missed/total_tasks:.1f}%)")
    print(f"  Total energy     : {total_energy} units")
    print(f"  Avg latency      : {avg_latency:.2f} ms")

    return {
        "policy":        policy_name,
        "missed":        missed,
        "total_energy":  total_energy,
        "avg_latency":   round(avg_latency, 2),
    }


# ===========================================================
# VISUALISATION — Week 7
# ===========================================================

def visualize_network(graph, nodes, title="Network State"):
    """
    Draw the compute network with node load info.
    """
    G = nx.Graph()
    for node in graph:
        for neighbor in graph[node]:
            G.add_edge(node, neighbor)

    labels = {
        n: f"{n}\nCPU:{nodes[n]['cpu']}\nLoad:{nodes[n]['load']}"
        for n in nodes
    }
    colors = ["#4fc3f7", "#81c784", "#ffb74d"]

    pos = nx.spring_layout(G, seed=1)
    plt.figure(figsize=(7, 5))
    nx.draw(G, pos, labels=labels, with_labels=True,
            node_size=3000, node_color=colors,
            font_size=9, font_weight="bold", edge_color="#888")
    plt.title(title, fontsize=13, fontweight="bold")
    plt.tight_layout()


def visualize_policy_comparison(metrics_list):
    """
    Side-by-side bar charts comparing all three policies.
    """
    policies = [m["policy"]       for m in metrics_list]
    missed   = [m["missed"]       for m in metrics_list]
    energy   = [m["total_energy"] for m in metrics_list]
    latency  = [m["avg_latency"]  for m in metrics_list]

    colors = ["#ef5350", "#42a5f5", "#66bb6a"]
    x = range(len(policies))

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle("Policy Comparison: Greedy vs DP vs Heuristic",
                 fontsize=14, fontweight="bold")

    # Missed deadlines
    axes[0].bar(x, missed, color=colors)
    axes[0].set_title("Missed Deadlines")
    axes[0].set_xticks(x); axes[0].set_xticklabels(policies)
    axes[0].set_ylabel("Count")
    for i, v in enumerate(missed):
        axes[0].text(i, v + 0.1, str(v), ha="center", fontweight="bold")

    # Total energy
    axes[1].bar(x, energy, color=colors)
    axes[1].set_title("Total Energy Consumed")
    axes[1].set_xticks(x); axes[1].set_xticklabels(policies)
    axes[1].set_ylabel("Energy Units")
    for i, v in enumerate(energy):
        axes[1].text(i, v + 0.5, str(v), ha="center", fontweight="bold")

    # Average latency
    axes[2].bar(x, latency, color=colors)
    axes[2].set_title("Average Latency (ms)")
    axes[2].set_xticks(x); axes[2].set_xticklabels(policies)
    axes[2].set_ylabel("ms")
    for i, v in enumerate(latency):
        axes[2].text(i, v + 0.2, str(v), ha="center", fontweight="bold")

    plt.tight_layout()


def visualize_task_timeline(greedy_res, dp_res, heuristic_res):
    """
    Per-task latency vs deadline for each policy.
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    fig.suptitle("Per-Task Latency vs Deadline", fontsize=13, fontweight="bold")

    configs = [
        (greedy_res,    "Greedy",    "#ef5350"),
        (dp_res,        "DP",        "#42a5f5"),
        (heuristic_res, "Heuristic", "#66bb6a"),
    ]

    for ax, (results, label, color) in zip(axes, configs):
        ids       = [r["task_id"]  for r in results]
        latencies = [r["latency"]  for r in results]
        deadlines = [r["deadline"] for r in results]

        ax.plot(ids, latencies, marker="o", color=color,
                label="Latency", linewidth=2)
        ax.plot(ids, deadlines, marker="x", color="#555",
                linestyle="--", label="Deadline", linewidth=1.5)
        ax.fill_between(ids, latencies, deadlines,
                        where=[l > d for l, d in zip(latencies, deadlines)],
                        alpha=0.25, color="red", label="Missed")

        ax.set_title(f"{label} Policy", fontweight="bold")
        ax.set_ylabel("Time (ms)")
        ax.legend(loc="upper right", fontsize=8)
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("Task ID")
    plt.tight_layout()


def visualize_node_distribution(greedy_res, dp_res, heuristic_res, nodes):
    """
    Stacked bar showing how tasks were distributed across nodes per policy.
    """
    node_names = list(nodes.keys())
    policies   = ["Greedy", "DP", "Heuristic"]
    all_results = [greedy_res, dp_res, heuristic_res]

    data = {n: [] for n in node_names}
    for results in all_results:
        counts = {n: 0 for n in node_names}
        for r in results:
            counts[r["node"]] += 1
        for n in node_names:
            data[n].append(counts[n])

    x      = range(len(policies))
    bottom = [0] * len(policies)
    colors = ["#4fc3f7", "#81c784", "#ffb74d"]

    plt.figure(figsize=(8, 5))
    for i, node in enumerate(node_names):
        plt.bar(x, data[node], bottom=bottom,
                label=node, color=colors[i])
        bottom = [b + d for b, d in zip(bottom, data[node])]

    plt.xticks(x, policies)
    plt.title("Task Distribution Across Nodes", fontweight="bold")
    plt.ylabel("Number of Tasks")
    plt.legend()
    plt.tight_layout()


# ===========================================================
# BFS REPORT
# ===========================================================

def print_bfs_report(graph):
    print("\n" + "="*50)
    print("  WEEK 4: BFS NETWORK TRAVERSAL")
    print("="*50)
    for start in graph:
        order = bfs(graph, start)
        print(f"  BFS from {start}: {' -> '.join(order)}")

    print("\n  Shortest Paths:")
    node_list = list(graph.keys())
    for i in range(len(node_list)):
        for j in range(i+1, len(node_list)):
            path = bfs_shortest_path(graph, node_list[i], node_list[j])
            print(f"    {node_list[i]} -> {node_list[j]}: {' -> '.join(path)}")


# ===========================================================
# COMPLEXITY ANALYSIS REPORT
# ===========================================================

def print_complexity_report():
    print("\n" + "="*50)
    print("  COMPLEXITY ANALYSIS")
    print("="*50)
    print("""
  Greedy Allocation:
    Time:  O(T × N)  — T tasks, N nodes
    Space: O(N)
    Note:  Fast but suboptimal; may miss deadlines
           under heavy or bursty loads.

  Dynamic Programming (windowed):
    Time:  O(T × N^W) — W = window size
    Space: O(W × N)
    Note:  Optimal within each window. Exponential
           in W, so window kept small (W=5).
           Pseudo-polynomial overall.

  Heuristic (deadline-aware load balancing):
    Time:  O(T × N)
    Space: O(N)
    Note:  Balances speed and quality. Locality
           bonus and urgency penalty make it
           more deadline-aware than greedy.

  NP-Hardness Note:
    Global optimal scheduling is NP-hard
    (reduction from bin packing / job scheduling).
    That is why greedy and heuristic approximations
    are necessary in real embedded/cloud systems.
    DP is optimal only for small windows.
""")


# ===========================================================
# MAIN
# ===========================================================

def main():
    print("\n" + "="*50)
    print("  CAPSTONE: CLOUD-EDGE RESOURCE ALLOCATION")
    print("="*50)

    # --- Generate tasks ---
    tasks = generate_tasks(NUM_TASKS)
    print(f"\n  Generated {NUM_TASKS} tasks (seed={RANDOM_SEED})")
    print(f"  Configurable: NUM_TASKS={NUM_TASKS}, "
          f"TIME_WINDOW={TIME_WINDOW}")

    # --- BFS Report ---
    print_bfs_report(GRAPH)

    # --- Run all three policies ---
    greedy_res,    nodes_g = greedy_allocate(tasks, NODES)
    dp_res,        nodes_d = dp_allocate(tasks, NODES, window=TIME_WINDOW)
    heuristic_res, nodes_h = heuristic_allocate(tasks, NODES)

    # --- Collect and print metrics ---
    metrics = [
        collect_metrics(greedy_res,    "Greedy"),
        collect_metrics(dp_res,        "DP"),
        collect_metrics(heuristic_res, "Heuristic"),
    ]

    # --- Complexity report ---
    print_complexity_report()

    # --- Visualisations ---
    print("\n  Generating plots...")

    visualize_network(GRAPH, nodes_g,
                      title="Network After Greedy Allocation")
    visualize_policy_comparison(metrics)
    visualize_task_timeline(greedy_res, dp_res, heuristic_res)
    visualize_node_distribution(greedy_res, dp_res,
                                heuristic_res, NODES)

    plt.show()
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
