import numpy as np
import random

def ant_colony_optimization(distance_matrix,n,
                            n_ants=20,
                            n_iterations=100,
                            alpha=1,
                            beta=5,
                            evaporation_rate=0.5,
                            Q=100):
    """
    Ant Colony Optimization for TSP (minimum distance)

    distance_matrix : NxN numpy array (meters or km)
    n_ants          : number of ants
    n_iterations    : number of iterations
    alpha           : pheromone importance
    beta            : heuristic importance
    evaporation_rate: pheromone evaporation
    Q               : pheromone deposit factor

    Returns:
        best_route
        best_distance
    """

    #n = len(distance_matrix)

    # Initialize pheromone matrix
    pheromone = np.ones((n, n))

    # Heuristic information (1/distance)
    heuristic = 1 / (distance_matrix + np.eye(n))

    best_route = None
    best_distance = float('inf')

    for iteration in range(n_iterations):

        all_routes = []
        all_distances = []

        for ant in range(n_ants):

            visited = [False] * n
            route = [0]        # start from node 0
            current = 0
            visited[0] = True
            total_distance = 0

            for _ in range(n - 1):

                probabilities = []
                for j in range(n):
                    if not visited[j]:
                        prob = (pheromone[current][j] ** alpha) * \
                               (heuristic[current][j] ** beta)
                    else:
                        prob = 0
                    probabilities.append(prob)

                probabilities = np.array(probabilities)
                probabilities /= probabilities.sum()

                next_city = np.random.choice(range(n), p=probabilities)

                total_distance += distance_matrix[current][next_city]
                route.append(next_city)
                visited[next_city] = True
                current = next_city

            # Return to start
            total_distance += distance_matrix[current][route[0]]
            route.append(route[0])

            all_routes.append(route)
            all_distances.append(total_distance)

            if total_distance < best_distance:
                best_distance = total_distance
                best_route = route

        # Evaporation
        pheromone *= (1 - evaporation_rate)

        # Pheromone update
        for route, distance in zip(all_routes, all_distances):
            for i in range(n):
                pheromone[route[i]][route[i+1]] += Q / distance

    return best_route, best_distance



def ant_colony_min_time(time_matrix,n,
                        n_ants=25,
                        n_iterations=150,
                        alpha=1,
                        beta=5,
                        evaporation_rate=0.5,
                        Q=100):
    """
    Ant Colony Optimization minimizing total travel time.

    time_matrix      : NxN numpy array (seconds)
    n_ants           : number of ants
    n_iterations     : number of iterations
    alpha            : pheromone importance
    beta             : heuristic importance (1/time)
    evaporation_rate : pheromone evaporation rate
    Q                : pheromone deposit factor

    Returns:
        best_route
        best_time (seconds)
    """

    #n = len(time_matrix)

    # Initialize pheromone levels
    pheromone = np.ones((n, n))

    # Heuristic information (inverse of time)
    heuristic = 1 / (time_matrix + np.eye(n))  # avoid division by zero

    best_route = None
    best_time = float('inf')

    for iteration in range(n_iterations):

        all_routes = []
        all_times = []

        for ant in range(n_ants):

            visited = [False] * n
            route = [0]        # fixed start
            current = 0
            visited[0] = True
            total_time = 0

            for _ in range(n - 1):

                probabilities = []

                for j in range(n):
                    if not visited[j]:
                        prob = (pheromone[current][j] ** alpha) * \
                               (heuristic[current][j] ** beta)
                    else:
                        prob = 0
                    probabilities.append(prob)

                probabilities = np.array(probabilities)

                if probabilities.sum() == 0:
                    break

                probabilities /= probabilities.sum()

                next_city = np.random.choice(range(n), p=probabilities)

                total_time += time_matrix[current][next_city]
                route.append(next_city)
                visited[next_city] = True
                current = next_city

            # Return to starting node
            total_time += time_matrix[current][route[0]]
            route.append(route[0])

            all_routes.append(route)
            all_times.append(total_time)

            if total_time < best_time:
                best_time = total_time
                best_route = route

        # Pheromone evaporation
        pheromone *= (1 - evaporation_rate)

        # Pheromone update
        for route, time in zip(all_routes, all_times):
            for i in range(n):
                pheromone[route[i]][route[i+1]] += Q / time

    return best_route, best_time





def ant_colony_max_avg_speed(distance_matrix, time_matrix,n,
                             n_ants=20,
                             n_iterations=100,
                             alpha=1,
                             beta=3,
                             evaporation_rate=0.5,
                             Q=100):

   # n = len(distance_matrix)

    distance_matrix = np.array(distance_matrix, dtype=float)
    time_matrix = np.array(time_matrix, dtype=float)

    epsilon = 1e-10
    speed_matrix = distance_matrix / (time_matrix + epsilon)

    pheromone = np.ones((n, n))

    best_route = None
    best_avg_speed = -1

    for iteration in range(n_iterations):

        all_routes = []
        all_avg_speeds = []

        for ant in range(n_ants):

            visited = [False] * n
            route = [0]
            visited[0] = True

            current = 0
            total_distance = 0
            total_time = 0

            for _ in range(n - 1):

                probabilities = []
                candidates = []

                for j in range(n):
                    if not visited[j] and time_matrix[current, j] > 0:

                        tau = pheromone[current, j] ** alpha
                        eta = speed_matrix[current, j] ** beta

                        probabilities.append(tau * eta)
                        candidates.append(j)

                if not candidates:
                    break

                probabilities = np.array(probabilities)
                probabilities = probabilities / probabilities.sum()

                next_node = np.random.choice(candidates, p=probabilities)

                total_distance += distance_matrix[current, next_node]
                total_time += time_matrix[current, next_node]

                route.append(next_node)
                visited[next_node] = True
                current = next_node

            # return to start
            total_distance += distance_matrix[current, 0]
            total_time += time_matrix[current, 0]
            route.append(0)

            avg_speed = total_distance / (total_time + epsilon)

            all_routes.append(route)
            all_avg_speeds.append(avg_speed)

            # Update global best
            if avg_speed > best_avg_speed:
                best_avg_speed = avg_speed
                best_route = route

        # Evaporation
        pheromone *= (1 - evaporation_rate)

        # Pheromone update
        for route, avg_speed in zip(all_routes, all_avg_speeds):
            for i in range(len(route) - 1):
                pheromone[route[i], route[i+1]] += Q * avg_speed

    return best_route, best_avg_speed