import math
def held_karp(distance,n):
    """
    Solves TSP using Held-Karp DP algorithm.
    distance: 2D list (n x n) distance matrix
    Returns optimal tour and minimum cost
    """
   # n = len(distance)
    dp = {}
    parent = {}

    # Initialize base cases
    for i in range(1, n):
        dp[(1 << i, i)] = distance[0][i]
        parent[(1 << i, i)] = 0

    # Iterate through subsets of increasing size
    for mask in range(1 << n):
        for last in range(1, n):
            if not (mask & (1 << last)):
                continue
            prev_mask = mask ^ (1 << last)
            if prev_mask == 0:
                continue

            min_cost = math.inf
            best_prev = None

            for k in range(1, n):
                if prev_mask & (1 << k):
                    cost = dp.get((prev_mask, k), math.inf) + distance[k][last]
                    if cost < min_cost:
                        min_cost = cost
                        best_prev = k

            if min_cost < math.inf:
                dp[(mask, last)] = min_cost
                parent[(mask, last)] = best_prev

    # Close the tour (return to start)
    full_mask = (1 << n) - 2  # exclude start node (0)
    min_cost = math.inf
    last_city = None

    for i in range(1, n):
        cost = dp[(full_mask, i)] + distance[i][0]
        if cost < min_cost:
            min_cost = cost
            last_city = i

    # Reconstruct path
    route = [0]
    mask = full_mask
    curr = last_city

    while mask:
        route.append(curr)
        prev = parent[(mask, curr)]
        mask ^= (1 << curr)
        curr = prev

    route.append(0)
    route.reverse()

    return route, min_cost



def held_karp_min_time(time_matrix,n):
    """
    Solves TSP using Held-Karp DP algorithm
    minimizing total travel time.

    time_matrix: 2D list (n x n) travel time between cities
    Returns optimal route and minimum total time
    """

    #n = len(time_matrix)
    dp = {}
    parent = {}

    # Base case: travel from start city (0) to each other city
    for i in range(1, n):
        dp[(1 << i, i)] = time_matrix[0][i]
        parent[(1 << i, i)] = 0

    # Iterate through all subsets of cities
    for mask in range(1 << n):
        for last in range(1, n):

            # Skip if last city not in subset
            if not (mask & (1 << last)):
                continue

            prev_mask = mask ^ (1 << last)

            if prev_mask == 0:
                continue

            min_time = math.inf
            best_prev = None

            # Try all possible previous cities
            for k in range(1, n):
                if prev_mask & (1 << k):
                    cost = dp.get((prev_mask, k), math.inf) + time_matrix[k][last]

                    if cost < min_time:
                        min_time = cost
                        best_prev = k

            if min_time < math.inf:
                dp[(mask, last)] = min_time
                parent[(mask, last)] = best_prev

    # Close the tour (return to start city 0)
    full_mask = (1 << n) - 2   # exclude city 0
    min_time = math.inf
    last_city = None

    for i in range(1, n):
        cost = dp[(full_mask, i)] + time_matrix[i][0]

        if cost < min_time:
            min_time = cost
            last_city = i

    # Reconstruct optimal route
    route = [0]
    mask = full_mask
    curr = last_city

    while mask:
        route.append(curr)
        prev = parent[(mask, curr)]
        mask ^= (1 << curr)
        curr = prev

    route.append(0)
    route.reverse()

    return route, min_time



def held_karp_max_speed(distance_matrix, time_matrix,n):
    """
    Held-Karp DP for maximizing average speed.
    speed = total_distance / total_time

    distance_matrix: NxN matrix
    time_matrix: NxN matrix

    Returns:
        best_route,
        max_average_speed,
        total_distance,
        total_time
    """

    #n = len(distance_matrix)
    dp = {}
    parent = {}

    # Base case
    for i in range(1, n):
        mask = 1 << i
        dp[(mask, i)] = (
            distance_matrix[0][i],
            time_matrix[0][i]
        )
        parent[(mask, i)] = 0

    # Build DP
    for mask in range(1 << n):
        for last in range(1, n):

            if not (mask & (1 << last)):
                continue

            prev_mask = mask ^ (1 << last)

            if prev_mask == 0:
                continue

            best_state = None
            best_speed = -math.inf
            best_prev = None

            for k in range(1, n):
                if prev_mask & (1 << k):
                    if (prev_mask, k) in dp:

                        prev_dist, prev_time = dp[(prev_mask, k)]

                        new_dist = prev_dist + distance_matrix[k][last]
                        new_time = prev_time + time_matrix[k][last]

                        if new_time == 0:
                            continue

                        speed = new_dist / new_time

                        if speed > best_speed:
                            best_speed = speed
                            best_state = (new_dist, new_time)
                            best_prev = k

            if best_state:
                dp[(mask, last)] = best_state
                parent[(mask, last)] = best_prev

    # Close tour
    full_mask = (1 << n) - 2

    max_speed = -math.inf
    best_last = None
    best_total = None

    for i in range(1, n):
        if (full_mask, i) in dp:

            dist, time = dp[(full_mask, i)]

            total_dist = dist + distance_matrix[i][0]
            total_time = time + time_matrix[i][0]

            if total_time == 0:
                continue

            speed = total_dist / total_time

            if speed > max_speed:
                max_speed = speed
                best_last = i
                best_total = (total_dist, total_time)

    # Reconstruct route
    route = [0]
    mask = full_mask
    curr = best_last

    while mask:
        route.append(curr)
        prev = parent[(mask, curr)]
        mask ^= (1 << curr)
        curr = prev

    route.append(0)
    route.reverse()

    return route, max_speed, best_total[0], best_total[1]