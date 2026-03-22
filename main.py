import Distance_Matrix_API
import route_matrix
import Route_Matrix_Api
import numpy as np
import brute_force
import Dynamic_Prog_held_karp
import nearest_neighbor
import ant_colony_optimization
import os
import hashlib
import pandas as pd
import insertion_alg
import Kopt
import time
import genetic_alg

#l = np.array([(lat, long), (lat1, long1)])
#l=np.array([(17.779241,83.224572),(17.729316,83.318806),(17.781668,83.385004),(17.728663,83.223558)])
k=50
df = pd.read_csv("delivery_dataset.csv")

# Convert to list of tuples
l = list(map(tuple, df[['Drop_Latitude', 'Drop_Longitude']].head(k).to_numpy()))

print(l)
# ---- Generate unique file name based on input ----
def get_filename(locations):
    #key = str(locations.tolist())
    key = str(locations)
    
    hash_key = hashlib.md5(key.encode()).hexdigest()
    return f"matrix_{hash_key}"

base_name = get_filename(l)

dist_file = base_name + "_dist.csv"
time_file = base_name + "_time.csv"

# ---- Check if already stored ----
if os.path.exists(dist_file) and os.path.exists(time_file):
    print("Loading from CSV (No API call)...")

    dist = np.loadtxt(dist_file, delimiter=",")
    times = np.loadtxt(time_file, delimiter=",")

else:
    print("Calling API...")

    n = len(l)

    if n <= 10:
        dist, times = Distance_Matrix_API.get_distance_time_matrix(l)
    elif n <= 15:
        dist, times= Distance_Matrix_API.get_distance_time_matrix_all(l)
    elif n <= 25:
        dist, times = Route_Matrix_Api.get_distance_time_matrix_routes(l)
    else:
        dist, times = route_matrix.get_distance_time_matrix_routes_batched(np.array(l))

    # Convert to NumPy arrays (important)
    dist = np.array(dist)
    times = np.array(times)

    # ---- Save to CSV ----
    np.savetxt(dist_file, dist, delimiter=",", fmt="%d")
    np.savetxt(time_file, time, delimiter=",", fmt="%d")

    print("Saved to CSV files!")

# ---- Now dist and time are ready as NumPy arrays ----
print("Distance Matrix:\n", dist)
print("Time Matrix:\n", times)


m=int(input("enter Number of location"))
n=m
#if(m==1):

#print(m)
if(n<=10):
    print("brute force algorithm")
    start = time.perf_counter()
    print("min distance",brute_force.Brute_force_alg(dist, n))
    print("min time",brute_force.brute_force_min_time(times, n))
    print("max avg speed",brute_force.brute_force_max_speed(dist,times,n))
    end = time.perf_counter()
    print("Execution time:", end - start, "seconds")
    
#elif(m==2):
#(m)
if(n<=20):
    print("dynamic programming held karp alg")
    start = time.perf_counter()
    print("min distance",Dynamic_Prog_held_karp.held_karp(dist,n))
    print("min time",Dynamic_Prog_held_karp.held_karp_min_time(times,n)) 
    print("max avg speed",Dynamic_Prog_held_karp.held_karp_max_speed(dist,times,n))
    end = time.perf_counter()
    print("Execution time:", end - start, "seconds")
        
#elif(m==3):
#print(m)

print("nearest neighbor")
start = time.perf_counter()
print(nearest_neighbor.nearest_neighbor_tsp(dist,n))
print(nearest_neighbor.nearest_neighbor_min_time(times,n))
print(nearest_neighbor.nearest_neighbor_tsp_max_speed(dist,times,n))
end = time.perf_counter()
print("Execution time:", end - start, "seconds")
#elif(m==4):
#print(m) 
dists = dist[:n, :n]
times=times[:n,:n]

print("ant colony optimization")
start = time.perf_counter()
print(ant_colony_optimization.ant_colony_optimization(dists,n))
print(ant_colony_optimization.ant_colony_min_time(times,n))
print(ant_colony_optimization.ant_colony_max_avg_speed(dists,times,n))
end = time.perf_counter()
print("Execution time:", end - start, "seconds")

print("insertion algorithm")
start = time.perf_counter()
print(insertion_alg.nearest_insertion_tsp(dist,n))
print(insertion_alg.nearest_insertion_min_time(times, n))
print(insertion_alg.insertion_max_avg_speed(dist,times, n))
end = time.perf_counter()
print("Execution time:", end - start, "seconds")

print("Kopt algorithm ")
start = time.perf_counter()
print(Kopt.two_opt(dist, n))
print(Kopt.two_opt_min_time(times, n))
print(Kopt.two_opt_max_speed(dist, times,n))
end = time.perf_counter()
print("Execution time:", end - start, "seconds")

print("genetic algorithm")
start = time.perf_counter()
print(genetic_alg.genetic_algorithm_tsp(dist, n))
print(genetic_alg.genetic_algorithm_min_time(times, n))
print(genetic_alg.genetic_algorithm_max_speed(dist, times, n))
end = time.perf_counter()
print("Execution time:", end - start, "seconds")
