import math
import itertools 

def Brute_force_alg(Adjacency_matrix,n):
    delivery_list=list(range(1,n))
    minimum=math.inf
    best_route=None
    for permutation in itertools.permutations(delivery_list):
        cost=0
        current_loc=0
        for loc in permutation:
            cost+=Adjacency_matrix[current_loc][loc]
            current_loc=loc
            
        cost += Adjacency_matrix[current_loc][0]

        if cost < minimum:
            minimum = cost
            best_route = (0,) + permutation + (0,)

    return [int(x) for x in best_route], float(minimum)


def brute_force_min_time(time_matrix, n):
    """
    Solves TSP using brute force
    minimizing total travel time.

    time_matrix: n x n matrix (travel time between cities)
    n: number of cities

    Returns:
        best_route,
        minimum_time
    """

    delivery_list = list(range(1, n))  # exclude start city 0
    minimum_time = math.inf
    best_route = None

    # Generate all permutations of cities
    for permutation in itertools.permutations(delivery_list):

        total_time = 0
        current_loc = 0

        # Travel through permutation
        for loc in permutation:
            total_time += time_matrix[current_loc][loc]
            current_loc = loc

        # Return to start city
        total_time += time_matrix[current_loc][0]

        # Update minimum time
        if total_time < minimum_time:
            minimum_time = total_time
            best_route = (0,) + permutation + (0,)

    return [int(x) for x in best_route], float(minimum_time)



def brute_force_max_speed(distance_matrix, time_matrix, n):
    """
    Brute force TSP maximizing average speed.

    distance_matrix: n x n matrix
    time_matrix: n x n matrix
    n: number of cities

    Returns:
        best_route,
        max_speed,
        total_distance,
        total_time
    """

    delivery_list = list(range(1, n))
    max_speed = -math.inf
    best_route = None
    best_distance = 0
    best_time = 0

    # Generate all permutations
    for permutation in itertools.permutations(delivery_list):

        total_distance = 0
        total_time = 0
        current_loc = 0

        # Travel through permutation
        for loc in permutation:
            total_distance += distance_matrix[current_loc][loc]
            total_time += time_matrix[current_loc][loc]
            current_loc = loc

        # Return to start city
        total_distance += distance_matrix[current_loc][0]
        total_time += time_matrix[current_loc][0]

        # Avoid division by zero
        if total_time == 0:
            continue

        speed = total_distance / total_time

        # Update maximum speed
        if speed > max_speed:
            max_speed = speed
            best_route = (0,) + permutation + (0,)
            best_distance = total_distance
            best_time = total_time

    return [int(x) for x in best_route], float(max_speed), float(best_distance), float(best_time)

