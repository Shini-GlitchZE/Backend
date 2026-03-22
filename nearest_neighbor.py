import numpy as np

def nearest_neighbor_tsp(distance_matrix,n, start=0):
    """
    Nearest Neighbor heuristic for TSP
    distance_matrix: NxN numpy array
    start: starting node (agent depot)
    returns route and total cost
    """

    #n = len(distance_matrix)
    visited = np.zeros(n, dtype=bool)

    route = [start]
    visited[start] = True
    total_cost = 0

    current = start

    for _ in range(n - 1):
        # Find nearest unvisited node
        nearest = None
        min_dist = np.inf

        for j in range(n):
            if not visited[j] and distance_matrix[current, j] < min_dist:
                min_dist = distance_matrix[current, j]
                nearest = j

        route.append(nearest)
        visited[nearest] = True
        total_cost += min_dist
        current = nearest

    # Return to start
    total_cost += distance_matrix[current, start]
    route.append(start)

    return route, total_cost
'''n=21
arr=np.zeros((n,n))

for i in range(0,n):
    for j in range(0,n):
        if(i==j):
            continue
        c=np.random.randint(1,100)
        arr[i][j]=c'''

#       print(nearest_neighbor_tsp(arr))


def nearest_neighbor_tsp_max_speed(distance_matrix, time_matrix,n,start=0):
    """
    Nearest Neighbor heuristic maximizing speed (distance/time).
    
    Returns:
        route
        average_speed = total_distance / total_time
    """

    #n = len(distance_matrix)
    visited = np.zeros(n, dtype=bool)

    route = [start]
    visited[start] = True

    current = start

    total_distance = 0
    total_time = 0

    for _ in range(n - 1):
        best_city = None
        max_speed = -np.inf

        for j in range(n):
            if not visited[j] and time_matrix[current, j] > 0:

                speed = distance_matrix[current, j] / time_matrix[current, j]

                if speed > max_speed:
                    max_speed = speed
                    best_city = j

        # Update totals
        total_distance += distance_matrix[current, best_city]
        total_time += time_matrix[current, best_city]

        route.append(best_city)
        visited[best_city] = True
        current = best_city

    # Return to start
    if time_matrix[current, start] > 0:
        total_distance += distance_matrix[current, start]
        total_time += time_matrix[current, start]

    route.append(start)

    # Compute overall average speed
    average_speed = total_distance / total_time if total_time > 0 else 0

    return route, average_speed


def nearest_neighbor_min_time(time_matrix,n,start=0):
    """
    Nearest Neighbor heuristic minimizing total travel time.

    time_matrix : NxN numpy array (seconds)
    start       : starting node (agent depot)

    Returns:
        route (list)
        total_time (seconds)
    """

    #n = len(time_matrix)
    visited = np.zeros(n, dtype=bool)

    route = [start]
    visited[start] = True
    total_time = 0

    current = start

    for _ in range(n - 1):

        nearest = None
        min_time = np.inf

        for j in range(n):
            if not visited[j] and time_matrix[current, j] > 0:
                if time_matrix[current, j] < min_time:
                    min_time = time_matrix[current, j]
                    nearest = j

        if nearest is None:
            break  # safety check

        route.append(nearest)
        visited[nearest] = True
        total_time += min_time
        current = nearest

    # Return to depot
    total_time += time_matrix[current, start]
    route.append(start)

    return route, total_time