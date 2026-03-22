import numpy as np

# -----------------------------
# Compute route cost
# -----------------------------
def route_cost(route, dist_matrix):
    cost = 0
    for i in range(len(route) - 1):
        cost += dist_matrix[route[i], route[i+1]]
    return cost


# -----------------------------
# 2-opt swap (core of K-opt)
# -----------------------------
def two_opt_swap(route, i, k):
    new_route = route[:i] + route[i:k+1][::-1] + route[k+1:]
    return new_route


# -----------------------------
# 2-opt algorithm
# -----------------------------
def two_opt(distance_matrix,n, start=0):
    #n = len(distance_matrix)

    # Initial route (simple order)
    route = list(range(n))
    route.append(start)  # make it a cycle

    best_cost = route_cost(route, distance_matrix)
    improved = True

    while improved:
        improved = False

        for i in range(1, n - 1):
            for k in range(i + 1, n):

                new_route = two_opt_swap(route, i, k)
                new_cost = route_cost(new_route, distance_matrix)

                # If improvement found
                if new_cost < best_cost:
                    route = new_route
                    best_cost = new_cost
                    improved = True
                    break

            if improved:
                break

    return route, best_cost



# -----------------------------
# Compute total travel time
# -----------------------------
def route_time(route, time_matrix):
    total_time = 0
    for i in range(len(route) - 1):
        total_time += time_matrix[route[i], route[i+1]]
    return total_time


# -----------------------------
# 2-opt swap
# -----------------------------
def two_opt_swapp(route, i, k):
    return route[:i] + route[i:k+1][::-1] + route[k+1:]


# -----------------------------
# 2-opt algorithm (min time)
# -----------------------------
def two_opt_min_time(time_matrix,n, start=0):
   # n = len(time_matrix)

    # Initial route (simple order)
    route = list(range(n))
    route.append(start)  # complete cycle

    best_time = route_time(route, time_matrix)
    improved = True

    while improved:
        improved = False

        for i in range(1, n - 1):
            for k in range(i + 1, n):

                new_route = two_opt_swapp(route, i, k)
                new_time = route_time(new_route, time_matrix)

                # If improvement found
                if new_time < best_time:
                    route = new_route
                    best_time = new_time
                    improved = True
                    break

            if improved:
                break

    return route, best_time



# -----------------------------
# Compute total distance
# -----------------------------
def route_distance(route, dist_matrix):
    return sum(dist_matrix[route[i], route[i+1]] for i in range(len(route)-1))


# -----------------------------
# Compute total time
# -----------------------------
def route_times(route, time_matrix):
    return sum(time_matrix[route[i], route[i+1]] for i in range(len(route)-1))


# -----------------------------
# Compute average speed
# -----------------------------
def route_speed(route, dist_matrix, time_matrix):
    total_dist = route_distance(route, dist_matrix)
    total_time = route_times(route, time_matrix)
    return total_dist / (total_time + 1e-10)


# -----------------------------
# 2-opt swap
# -----------------------------
def two_opt_swaps(route, i, k):
    return route[:i] + route[i:k+1][::-1] + route[k+1:]


# -----------------------------
# 2-opt (maximize speed)
# -----------------------------
def two_opt_max_speed(distance_matrix, time_matrix,n, start=0):
    #n = len(distance_matrix)

    # Initial route
    route = list(range(n))
    route.append(start)

    best_speed = route_speed(route, distance_matrix, time_matrix)
    best_dist = route_distance(route, distance_matrix)
    best_time = route_times(route, time_matrix)

    improved = True

    while improved:
        improved = False

        for i in range(1, n - 1):
            for k in range(i + 1, n):

                new_route = two_opt_swaps(route, i, k)

                new_speed = route_speed(new_route, distance_matrix, time_matrix)

                # Accept if speed improves
                if new_speed > best_speed:
                    route = new_route
                    best_speed = new_speed
                    best_dist = route_distance(route, distance_matrix)
                    best_time = route_times(route, time_matrix)
                    improved = True
                    break

            if improved:
                break

    return route, best_speed, best_dist, best_time
