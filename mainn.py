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
import integer_programming

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
                print("warning")
                dist, times = Distance_Matrix_API.get_distance_time_matrix(locations)

            elif n <= 15:
                print("warning")
                dist, times = Distance_Matrix_API.get_distance_time_matrix_all(locations)

            elif n <= 25:
                print("warning")
                dist, times = Route_Matrix_Api.get_distance_time_matrix_routes(np.array(locations))

            else:
                print("warning")
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

    dataset_path = r"C:\Users\velch\Downloads\apitest.csv"

    # Load data
    agents, deliveries = load_csv_dataset(dataset_path)

    print(f"\n Agents: {len(agents)}")
    print(f" Deliveries: {len(deliveries)}")

    # Safety check
    if len(agents) == 0 or len(deliveries) == 0:
        raise ValueError("Dataset is empty or not loaded correctly.")

    # Build distance matrix
    agents_np = np.array([[a["lat"], a["lng"]] for a in agents])
    deliveries_np = np.array([[d["lat"], d["lng"]] for d in deliveries])
    
    # Caching logic for global agent-delivery matrix
    global_key = str(agents_np.tolist()) + str(deliveries_np.tolist())
    global_hash = hashlib.md5(global_key.encode()).hexdigest()
    global_dist_file = f"global_mat_{global_hash}_dist.csv"
    global_time_file = f"global_mat_{global_hash}_time.csv"
    
    if os.path.exists(global_dist_file) and os.path.exists(global_time_file):
        print("Loading global assignment matrix from CSV (cache hit)")
        distance_matrix_np = np.loadtxt(global_dist_file, delimiter=",")
        time_matrix = np.loadtxt(global_time_file, delimiter=",")
    else:
        print("Calling API for global assignment matrix (cache miss)")
        distance_matrix_np, time_matrix = agent_mat.get_agent_delivery_matrix(agents_np, deliveries_np)
        np.savetxt(global_dist_file, distance_matrix_np, delimiter=",", fmt="%d")
        np.savetxt(global_time_file, time_matrix, delimiter=",", fmt="%d")
        print("Saved global assignment matrices to CSV")
    
    distance_matrix = {}
    for i, a in enumerate(agents):
        for j, d in enumerate(deliveries):
            distance_matrix[(a["id"], d["id"])] = distance_matrix_np[i, j]

    # Capacity logic
    max_capacity = len(deliveries) // len(agents) + 2
    print(f" Max capacity per agent: {max_capacity}")

    #  Adaptive Algorithm Selection
    if len(deliveries) <= 150:
        print("\n[FAST] Small dataset -> Running MCMF + Greedy")

        greedy_result = incremental_cost_greedy(
            agents, deliveries, distance_matrix
        )
        greedy_metrics = calculate_metrics(greedy_result, distance_matrix)

        mcmf_result = minimum_cost_max_flow_assignment(
            agents, deliveries, distance_matrix, max_capacity
        )
        mcmf_metrics = calculate_metrics(mcmf_result, distance_matrix)

        greedy_score = greedy_metrics["total_distance"] + (greedy_metrics["load_std_dev"] * 10)
        mcmf_score = mcmf_metrics["total_distance"] + (mcmf_metrics["load_std_dev"] * 10)

        if mcmf_score < greedy_score:
            final_result = mcmf_result
            final_metrics = mcmf_metrics
            selected_algo = "MCMF"
        else:
            final_result = greedy_result
            final_metrics = greedy_metrics
            selected_algo = "Greedy"

    else:
        print("\n[FAST] Large dataset -> Using Greedy (optimized)")

        final_result = incremental_cost_greedy(
            agents, deliveries, distance_matrix
        )
        final_metrics = calculate_metrics(final_result, distance_matrix)
        selected_algo = "Greedy"

    #  RESULTS OUTPUT
    print(f"\n Selected Algorithm: {selected_algo}")

    print("\n DELIVERY DISTRIBUTION:\n")

    total_assigned = 0

    for agent_id in sorted(final_result.keys()):
        assigned = final_result[agent_id]
        count = len(assigned)
        total_assigned += count

        # Show preview only (clean output)
        preview = assigned[:5]

        print(f" AGENT {agent_id:<5} : {count:>3} DELIVERIES")
        print(f"  Sample: {preview} {'...' if count > 5 else ''}")

    print(f"\n TOTAL ASSIGNED DELIVERIES: {total_assigned}")

    # 📊 LOAD ANALYSIS
    loads = [len(v) for v in final_result.values()]

    print("\n LOAD ANALYSIS:")
    print(f"   Max Load : {max(loads)}")
    print(f"   Min Load : {min(loads)}")
    print(f"   Avg Load : {sum(loads)/len(loads):.2f}")

    #  PERFORMANCE METRICS
    print("\n PERFORMANCE METRICS:")
    print(f"   Total Distance : {final_metrics['total_distance']:.2f}")
    print(f"   Load Std Dev   : {final_metrics['load_std_dev']:.2f}")

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

       # print("Distance Matrix:\n", dist)
        #print("Time Matrix:\n", times)

        # ------------------------------------------------
        # RUN TSP ALGORITHMS
        # ------------------------------------------------
        def map_r(res):
            if res is None or res[0] is None: return res
            return ([assigned_delivery_ids[i] for i in res[0]],) + res[1:]

        if n <= 8:

            print("\nBrute Force")
            start = time.perf_counter()

            print("Min Distance:", map_r(brute_force.Brute_force_alg(dist, n)))
            print("Min Time:", map_r(brute_force.brute_force_min_time(times, n)))
            print("Max Speed:", map_r(brute_force.brute_force_max_speed(dist, times, n)))

            end = time.perf_counter()
            print("Execution Time:", end - start)

        if n <= 15:

            print("\nDynamic Programming Held-Karp")

            start = time.perf_counter()

            print("Min Distance:", map_r(Dynamic_Prog_held_karp.held_karp(dist, n)))
            print("Min Time:", map_r(Dynamic_Prog_held_karp.held_karp_min_time(times, n)))
            print("Max Speed:", map_r(Dynamic_Prog_held_karp.held_karp_max_speed(dist, times, n)))

            end = time.perf_counter()
            print("Execution Time:", end - start)

        print("\nNearest Neighbor")

        start = time.perf_counter()

        print(map_r(nearest_neighbor.nearest_neighbor_tsp(dist, n)))
        print(map_r(nearest_neighbor.nearest_neighbor_min_time(times, n)))
        print(map_r(nearest_neighbor.nearest_neighbor_tsp_max_speed(dist, times, n)))

        end = time.perf_counter()
        print("Execution Time:", end - start)

        print("\nAnt Colony Optimization")

        start = time.perf_counter()

        print(map_r(ant_colony_optimization.ant_colony_optimization(dist, n)))
        print(map_r(ant_colony_optimization.ant_colony_min_time(times, n)))
        print(map_r(ant_colony_optimization.ant_colony_max_avg_speed(dist, times, n)))

        end = time.perf_counter()
        print("Execution Time:", end - start)

        print("\nInsertion Algorithm")

        start = time.perf_counter()

        print(map_r(insertion_alg.nearest_insertion_tsp(dist, n)))
        print(map_r(insertion_alg.nearest_insertion_min_time(times, n)))
        print(map_r(insertion_alg.insertion_max_avg_speed(dist, times, n)))

        end = time.perf_counter()
        print("Execution Time:", end - start)

        print("\n2-OPT")

        start = time.perf_counter()

        print(map_r(Kopt.two_opt(dist, n)))
        print(map_r(Kopt.two_opt_min_time(times, n)))
        print(map_r(Kopt.two_opt_max_speed(dist, times, n)))

        end = time.perf_counter()
        print("Execution Time:", end - start)

        print("\nGenetic Algorithm")

        start = time.perf_counter()

        print(map_r(genetic_alg.genetic_algorithm_tsp(dist, n)))
        print(map_r(genetic_alg.genetic_algorithm_min_time(times, n)))
        print(map_r(genetic_alg.genetic_algorithm_max_speed(dist, times, n)))

        end = time.perf_counter()
        print("Execution Time:", end - start)

        '''print("\nInteger Linear Programming (MTZ Optimal)")

        start = time.perf_counter()

        # ILP – Minimum Distance
        ilp_dist = integer_programming.ilp_min_distance(dist, n)
        if ilp_dist[0] is None:
            # fallback to genetic algorithm (good heuristic)
            fallback = genetic_alg.genetic_algorithm_tsp(dist, n)
            print("ILP (Min Distance) timed out – using Genetic Algo:", map_r(fallback))
        else:
            print("Min Distance (ILP):", map_r(ilp_dist))

        # ILP – Minimum Time
        ilp_time = integer_programming.ilp_min_time(times, n)
        if ilp_time[0] is None:
            fallback = genetic_alg.genetic_algorithm_min_time(times, n)
            print("ILP (Min Time) timed out – using Genetic Algo:", map_r(fallback))
        else:
            print("Min Time (ILP):", map_r(ilp_time))

        # ILP – Max Speed (average speed)
        ilp_speed = integer_programming.ilp_max_speed(dist, times, n)
        if ilp_speed[0] is None:
            fallback = genetic_alg.genetic_algorithm_max_speed(dist, times, n)
            print("ILP (Max Speed) timed out – using Genetic Algo:", map_r(fallback))
        else:
            print("Max Speed (ILP):", map_r(ilp_speed))

        end = time.perf_counter()
        print("Execution Time:", end - start)'''