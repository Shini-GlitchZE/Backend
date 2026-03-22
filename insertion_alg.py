import numpy as np

def nearest_insertion_tsp(distance_matrix,n, start=0):
    """
    Nearest Insertion algorithm for TSP

    distance_matrix : NxN numpy array
    start           : starting node

    Returns:
        route
        total_cost
    """

   # n = len(distance_matrix)
    unvisited = set(range(n))
    unvisited.remove(start)

    # Step 1: start with nearest node
    nearest = min(unvisited, key=lambda j: distance_matrix[start, j])
    route = [start, nearest, start]
    unvisited.remove(nearest)

    # Step 2: insert remaining nodes
    while unvisited:

        # Find node closest to any node in current route
        nearest_node = None
        min_dist = float('inf')

        for node in unvisited:
            for r in route:
                if distance_matrix[node, r] < min_dist:
                    min_dist = distance_matrix[node, r]
                    nearest_node = node

        # Find best position to insert this node
        best_pos = None
        min_increase = float('inf')

        for i in range(len(route) - 1):
            a = route[i]
            b = route[i + 1]

            increase = (
                distance_matrix[a, nearest_node]
                + distance_matrix[nearest_node, b]
                - distance_matrix[a, b]
            )

            if increase < min_increase:
                min_increase = increase
                best_pos = i + 1

        # Insert node
        route.insert(best_pos, nearest_node)
        unvisited.remove(nearest_node)

    # Compute total cost
    total_cost = 0
    for i in range(len(route) - 1):
        total_cost += distance_matrix[route[i], route[i+1]]

    return route, total_cost



def nearest_insertion_min_time(time_matrix,n, start=0):
    """
    Nearest Insertion algorithm minimizing total travel time

    time_matrix : NxN numpy array (seconds)
    start       : starting node

    Returns:
        route
        total_time (seconds)
    """

    #n = len(time_matrix)
    unvisited = set(range(n))
    unvisited.remove(start)

    # Step 1: start with nearest node (minimum time)
    nearest = min(unvisited, key=lambda j: time_matrix[start, j])
    route = [start, nearest, start]
    unvisited.remove(nearest)

    # Step 2: insert remaining nodes
    while unvisited:

        # Find node closest (in time) to any node in current route
        nearest_node = None
        min_time = float('inf')

        for node in unvisited:
            for r in route:
                if time_matrix[node, r] < min_time:
                    min_time = time_matrix[node, r]
                    nearest_node = node

        # Find best position to insert this node (minimum time increase)
        best_pos = None
        min_increase = float('inf')

        for i in range(len(route) - 1):
            a = route[i]
            b = route[i + 1]

            increase = (
                time_matrix[a, nearest_node]
                + time_matrix[nearest_node, b]
                - time_matrix[a, b]
            )

            if increase < min_increase:
                min_increase = increase
                best_pos = i + 1

        # Insert node
        route.insert(best_pos, nearest_node)
        unvisited.remove(nearest_node)

    # Compute total time
    total_time = 0
    for i in range(len(route) - 1):
        total_time += time_matrix[route[i], route[i+1]]

    return route, total_time



def insertion_max_avg_speed(distance_matrix, time_matrix,n, start=0):
    """
    Insertion algorithm to maximize average speed (distance/time)

    distance_matrix : NxN numpy array
    time_matrix     : NxN numpy array

    Returns:
        route
        avg_speed
        total_distance
        total_time
    """

    #n = len(distance_matrix)
    unvisited = set(range(n))
    unvisited.remove(start)

    # Step 1: start with nearest (based on best speed)
    nearest = max(
        unvisited,
        key=lambda j: distance_matrix[start, j] / (time_matrix[start, j] + 1e-10)
    )

    route = [start, nearest, start]
    unvisited.remove(nearest)

    total_distance = (
        distance_matrix[start, nearest] +
        distance_matrix[nearest, start]
    )

    total_time = (
        time_matrix[start, nearest] +
        time_matrix[nearest, start]
    )

    # Step 2: insert remaining nodes
    while unvisited:

        best_node = None
        best_pos = None
        best_score = -1  # maximize speed

        for node in unvisited:
            for i in range(len(route) - 1):
                a = route[i]
                b = route[i + 1]

                # Incremental distance & time
                delta_dist = (
                    distance_matrix[a, node] +
                    distance_matrix[node, b] -
                    distance_matrix[a, b]
                )

                delta_time = (
                    time_matrix[a, node] +
                    time_matrix[node, b] -
                    time_matrix[a, b]
                )

                if delta_time <= 0:
                    continue

                # Speed gain
                speed = delta_dist / (delta_time + 1e-10)

                if speed > best_score:
                    best_score = speed
                    best_node = node
                    best_pos = i + 1
                    best_delta_dist = delta_dist
                    best_delta_time = delta_time

        if best_node is None:
            break

        # Insert node
        route.insert(best_pos, best_node)
        unvisited.remove(best_node)

        total_distance += best_delta_dist
        total_time += best_delta_time

    avg_speed = total_distance / (total_time + 1e-10)

    return route, avg_speed, total_distance, total_time
