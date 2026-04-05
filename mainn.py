from utils.export import export_assignments_to_csv
from algorithms.graph import minimum_cost_max_flow_assignment
from algorithms.greedy import incremental_cost_greedy
from utils.distance import build_distance_matrix, haversine
from utils.metrics import calculate_metrics
from data.csv_loader import load_csv_dataset

import Distance_Matrix_API
import route_matrix
import Route_Matrix_Api
import numpy as np
import brute_force
import Dynamic_Prog_held_karp
import nearest_neighbor
import ant_colony_optimization
import insertion_alg
import Kopt
import genetic_alg

import os
import hashlib
import time
import agent_mat

# ------------------------------------------------
# MATRIX CACHE FUNCTION
# ------------------------------------------------
def get_filename(locations):
    key = str(locations)
    hash_key = hashlib.md5(key.encode()).hexdigest()
    return f"matrix_{hash_key}"


def get_distance_time_matrix(locations):

    base_name = get_filename(locations)

    dist_file = base_name + "_dist.csv"
    time_file = base_name + "_time.csv"

    valid_cache = False
    if os.path.exists(dist_file) and os.path.exists(time_file):
        print("Loading from CSV (cache hit)")
        dist = np.loadtxt(dist_file, delimiter=",")
        times = np.loadtxt(time_file, delimiter=",")
        if np.sum(dist) > 0 or len(locations) <= 1:
            valid_cache = True
        else:
            print("Cached matrix is all zeros, ignoring cache...")

    if not valid_cache:
        print("Calling API (cache miss)")
        n = len(locations)

        try:
            if n <= 10:
                dist, times = Distance_Matrix_API.get_distance_time_matrix(locations)

            elif n <= 15:
                dist, times = Distance_Matrix_API.get_distance_time_matrix_all(locations)

            elif n <= 25:
                dist, times = Route_Matrix_Api.get_distance_time_matrix_routes(np.array(locations))

            else:
                dist, times = route_matrix.get_distance_time_matrix_routes_batched(np.array(locations))

            dist = np.array(dist)
            times = np.array(times)
            
            if np.sum(dist) == 0 and n > 1:
                raise Exception("API returned an invalid (all zeros) matrix")
                
        except Exception as e:
            print(f"API call failed with error: {e}. Using heuristic fallback instead.")
            dist = np.zeros((n, n))
            times = np.zeros((n, n))
            avg_speed_kmh = 40.0
            
            for i in range(n):
                for j in range(n):
                    if i != j:
                        d_km = haversine(locations[i][0], locations[i][1], locations[j][0], locations[j][1])
                        dist[i][j] = int(d_km * 1000)
                        times[i][j] = int(dist[i][j] / (avg_speed_kmh * 1000 / 3600))
            dist = np.array(dist, dtype=int)
            times = np.array(times, dtype=int)

        np.savetxt(dist_file, dist, delimiter=",", fmt="%d")
        np.savetxt(time_file, times, delimiter=",", fmt="%d")

        print("Saved matrices to CSV")

    return dist, times


# ------------------------------------------------
# MAIN
# ------------------------------------------------
if __name__ == "__main__":

    dataset_path = r"C:\Users\velch\Desktop\delivery_dataset.csv"

    agents, deliveries = load_csv_dataset(dataset_path)

    print("Agents:", len(agents))
    print("Deliveries:", len(deliveries))

    distance_matrix = build_distance_matrix(agents, deliveries)
    # distance_matrix = agent_mat.get_agent_delivery_matrix(agents, deliveries)

    max_capacity = len(deliveries) // len(agents) + 2
    print("Max capacity per agent:", max_capacity)

    # ------------------------------------------------
    # ASSIGNMENT STEP
    # ------------------------------------------------
    if len(deliveries) <= 150:

        print("Small dataset -> running Greedy + MCMF")

        greedy_result = incremental_cost_greedy(
            agents, deliveries, distance_matrix
        )

        greedy_metrics = calculate_metrics(greedy_result, distance_matrix)

        mcmf_result = minimum_cost_max_flow_assignment(
            agents,
            deliveries,
            distance_matrix,
            max_capacity
        )

        mcmf_metrics = calculate_metrics(mcmf_result, distance_matrix)

        greedy_score = greedy_metrics["total_distance"] + (
            greedy_metrics["load_std_dev"] * 10
        )

        mcmf_score = mcmf_metrics["total_distance"] + (
            mcmf_metrics["load_std_dev"] * 10
        )

        if mcmf_score < greedy_score:
            final_result = mcmf_result
            selected_algo = "MCMF"
        else:
            final_result = greedy_result
            selected_algo = "Greedy"

    else:

        print("Large dataset -> using Greedy only")

        final_result = incremental_cost_greedy(
            agents,
            deliveries,
            distance_matrix
        )

        selected_algo = "Greedy"

    print("\nSelected Algorithm:", selected_algo)

    # ------------------------------------------------
    # PRINT ASSIGNMENT
    # ------------------------------------------------
    for agent_id in sorted(final_result.keys()):
        print("Agent", agent_id, "->", len(final_result[agent_id]), "deliveries")

    total_assigned = sum(len(v) for v in final_result.values())
    print("Total Assigned Deliveries:", total_assigned)

    export_assignments_to_csv(final_result, deliveries)

    delivery_lookup = {d["id"]: d for d in deliveries}

    # ------------------------------------------------
    # ROUTE OPTIMIZATION PER AGENT
    # ------------------------------------------------
    for agent_id, assigned_delivery_ids in final_result.items():

        if len(assigned_delivery_ids) == 0:
            continue

        print("\n====================================")
        print("Route Optimization for Agent", agent_id)

        locations = [
            (delivery_lookup[d_id]["lat"], delivery_lookup[d_id]["lng"])
            for d_id in assigned_delivery_ids
        ]

        dist, times = get_distance_time_matrix(locations)

        n = len(locations)

        print("Distance Matrix:\n", dist)
        print("Time Matrix:\n", times)

        # ------------------------------------------------
        # RUN TSP ALGORITHMS
        # ------------------------------------------------

        if n <= 10:

            print("\nBrute Force")
            start = time.perf_counter()

            print("Min Distance:", brute_force.Brute_force_alg(dist, n))
            print("Min Time:", brute_force.brute_force_min_time(times, n))
            print("Max Speed:", brute_force.brute_force_max_speed(dist, times, n))

            end = time.perf_counter()
            print("Execution Time:", end - start)

        if n <= 20:

            print("\nDynamic Programming Held-Karp")

            start = time.perf_counter()

            print("Min Distance:", Dynamic_Prog_held_karp.held_karp(dist, n))
            print("Min Time:", Dynamic_Prog_held_karp.held_karp_min_time(times, n))
            print("Max Speed:", Dynamic_Prog_held_karp.held_karp_max_speed(dist, times, n))

            end = time.perf_counter()
            print("Execution Time:", end - start)

        print("\nNearest Neighbor")

        start = time.perf_counter()

        print(nearest_neighbor.nearest_neighbor_tsp(dist, n))
        print(nearest_neighbor.nearest_neighbor_min_time(times, n))
        print(nearest_neighbor.nearest_neighbor_tsp_max_speed(dist, times, n))

        end = time.perf_counter()
        print("Execution Time:", end - start)

        print("\nAnt Colony Optimization")

        start = time.perf_counter()

        print(ant_colony_optimization.ant_colony_optimization(dist, n))
        print(ant_colony_optimization.ant_colony_min_time(times, n))
        print(ant_colony_optimization.ant_colony_max_avg_speed(dist, times, n))

        end = time.perf_counter()
        print("Execution Time:", end - start)

        print("\nInsertion Algorithm")

        start = time.perf_counter()

        print(insertion_alg.nearest_insertion_tsp(dist, n))
        print(insertion_alg.nearest_insertion_min_time(times, n))
        print(insertion_alg.insertion_max_avg_speed(dist, times, n))

        end = time.perf_counter()
        print("Execution Time:", end - start)

        print("\n2-OPT")

        start = time.perf_counter()

        print(Kopt.two_opt(dist, n))
        print(Kopt.two_opt_min_time(times, n))
        print(Kopt.two_opt_max_speed(dist, times, n))

        end = time.perf_counter()
        print("Execution Time:", end - start)

        print("\nGenetic Algorithm")

        start = time.perf_counter()

        print(genetic_alg.genetic_algorithm_tsp(dist, n))
        print(genetic_alg.genetic_algorithm_min_time(times, n))
        print(genetic_alg.genetic_algorithm_max_speed(dist, times, n))

        end = time.perf_counter()
        print("Execution Time:", end - start)