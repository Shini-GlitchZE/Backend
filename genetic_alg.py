
import numpy as np
import random

# -----------------------------
# Fitness (minimize distance)
# -----------------------------
def route_distance(route, dist_matrix):
    return sum(dist_matrix[route[i], route[i+1]] for i in range(len(route)-1))


def fitness(route, dist_matrix):
    return 1 / (route_distance(route, dist_matrix) + 1e-10)


# -----------------------------
# Create initial population (FIXED START/END = 0)
# -----------------------------
def create_population(pop_size, n):
    population = []
    base = list(range(1, n))  # exclude node 0

    for _ in range(pop_size):
        route = base[:]
        random.shuffle(route)
        route = [0] + route + [0]  # start and end at 0
        population.append(route)

    return population


# -----------------------------
# Selection (tournament)
# -----------------------------
def selection(population, dist_matrix, k=3):
    selected = random.sample(population, k)
    selected.sort(key=lambda r: route_distance(r, dist_matrix))
    return selected[0]


# -----------------------------
# Crossover (Order Crossover - OX) FIXED 0
# -----------------------------
def crossover(parent1, parent2):
    # Remove fixed start/end (0)
    p1 = parent1[1:-1]
    p2 = parent2[1:-1]

    n = len(p1)

    start, end = sorted(random.sample(range(n), 2))

    child = [-1] * n
    child[start:end] = p1[start:end]

    ptr = 0
    for gene in p2:
        if gene not in child:
            while child[ptr] != -1:
                ptr += 1
            child[ptr] = gene

    # Add fixed start/end
    child = [0] + child + [0]
    return child


# -----------------------------
# Mutation (swap) FIXED 0
# -----------------------------
def mutate(route, mutation_rate=0.1):
    middle = route[1:-1]  # exclude 0s

    if random.random() < mutation_rate:
        i, j = random.sample(range(len(middle)), 2)
        middle[i], middle[j] = middle[j], middle[i]

    route = [0] + middle + [0]
    return route


# -----------------------------
# Genetic Algorithm
# -----------------------------
def genetic_algorithm_tsp(distance_matrix, n,
                          pop_size=50,
                          generations=200,
                          mutation_rate=0.1):

    population = create_population(pop_size, n)

    best_route = None
    best_cost = float('inf')

    for gen in range(generations):

        new_population = []

        for _ in range(pop_size):
            parent1 = selection(population, distance_matrix)
            parent2 = selection(population, distance_matrix)

            child = crossover(parent1, parent2)
            child = mutate(child, mutation_rate)

            new_population.append(child)

        population = new_population

        # Track best
        for route in population:
            cost = route_distance(route, distance_matrix)
            if cost < best_cost:
                best_cost = cost
                best_route = route

        # print(f"Generation {gen+1} | Best Distance: {best_cost}")

    return best_route, best_cost


# -----------------------------
# Compute total travel time
# -----------------------------
def route_time_cost(route, time_matrix):
    return sum(time_matrix[route[i], route[i+1]] for i in range(len(route)-1))


# -----------------------------
# Fitness (minimize time)
# -----------------------------
def fitness_time(route, time_matrix):
    return 1 / (route_time_cost(route, time_matrix) + 1e-10)


# -----------------------------
# Create initial population (FIXED START/END = 0)
# -----------------------------
def create_population_time(pop_size, n):
    population = []
    base = list(range(1, n))  # exclude node 0

    for _ in range(pop_size):
        route = base[:]
        random.shuffle(route)
        route = [0] + route + [0]  # fixed start & end
        population.append(route)

    return population


# -----------------------------
# Selection (tournament)
# -----------------------------
def selection_time(population, time_matrix, k=3):
    selected = random.sample(population, k)
    selected.sort(key=lambda r: route_time_cost(r, time_matrix))
    return selected[0]


# -----------------------------
# Crossover (Order Crossover - OX) FIXED 0
# -----------------------------
def crossover_time(parent1, parent2):
    # Remove fixed nodes (0)
    p1 = parent1[1:-1]
    p2 = parent2[1:-1]

    n = len(p1)

    start, end = sorted(random.sample(range(n), 2))
    child = [-1] * n

    child[start:end] = p1[start:end]

    ptr = 0
    for gene in p2:
        if gene not in child:
            while child[ptr] != -1:
                ptr += 1
            child[ptr] = gene

    # Add fixed start/end
    child = [0] + child + [0]
    return child


# -----------------------------
# Mutation (swap) FIXED 0
# -----------------------------
def mutate_time(route, mutation_rate=0.1):
    middle = route[1:-1]  # exclude 0s

    if random.random() < mutation_rate:
        i, j = random.sample(range(len(middle)), 2)
        middle[i], middle[j] = middle[j], middle[i]

    route = [0] + middle + [0]
    return route


# -----------------------------
# Genetic Algorithm (Min Time)
# -----------------------------
def genetic_algorithm_min_time(time_matrix, n,
                              pop_size=50,
                              generations=200,
                              mutation_rate=0.1):

    population = create_population_time(pop_size, n)

    best_route = None
    best_time = float('inf')

    for gen in range(generations):

        new_population = []

        for _ in range(pop_size):
            parent1 = selection_time(population, time_matrix)
            parent2 = selection_time(population, time_matrix)

            child = crossover_time(parent1, parent2)
            child = mutate_time(child, mutation_rate)

            new_population.append(child)

        population = new_population

        # Track best solution
        for route in population:
            t = route_time_cost(route, time_matrix)
            if t < best_time:
                best_time = t
                best_route = route

        # print(f"Generation {gen+1} | Best Time: {best_time}")

    return best_route, best_time






# -----------------------------
# Compute total distance
# -----------------------------
def route_distance_speed(route, dist_matrix):
    return sum(dist_matrix[route[i], route[i+1]] for i in range(len(route)-1))


# -----------------------------
# Compute total time
# -----------------------------
def route_time_speed(route, time_matrix):
    return sum(time_matrix[route[i], route[i+1]] for i in range(len(route)-1))


# -----------------------------
# Fitness (maximize speed)
# -----------------------------
def fitness_speed(route, dist_matrix, time_matrix):
    total_dist = route_distance_speed(route, dist_matrix)
    total_time = route_time_speed(route, time_matrix)
    return total_dist / (total_time + 1e-10)


# -----------------------------
# Create initial population (FIXED START/END = 0)
# -----------------------------
def create_population_speed(pop_size, n):
    population = []
    base = list(range(1, n))  # exclude node 0

    for _ in range(pop_size):
        route = base[:]
        random.shuffle(route)
        route = [0] + route + [0]  # fixed start and end
        population.append(route)

    return population


# -----------------------------
# Selection (tournament)
# -----------------------------
def selection_speed(population, dist_matrix, time_matrix, k=3):
    selected = random.sample(population, k)
    selected.sort(
        key=lambda r: fitness_speed(r, dist_matrix, time_matrix),
        reverse=True
    )
    return selected[0]


# -----------------------------
# Crossover (Order Crossover) FIXED 0
# -----------------------------
def crossover_speed(parent1, parent2):
    # Remove fixed nodes (0)
    p1 = parent1[1:-1]
    p2 = parent2[1:-1]

    n = len(p1)

    start, end = sorted(random.sample(range(n), 2))
    child = [-1] * n

    child[start:end] = p1[start:end]

    ptr = 0
    for gene in p2:
        if gene not in child:
            while child[ptr] != -1:
                ptr += 1
            child[ptr] = gene

    # Add fixed start and end
    child = [0] + child + [0]
    return child


# -----------------------------
# Mutation FIXED 0
# -----------------------------
def mutate_speed(route, mutation_rate=0.1):
    middle = route[1:-1]  # exclude 0s

    if random.random() < mutation_rate:
        i, j = random.sample(range(len(middle)), 2)
        middle[i], middle[j] = middle[j], middle[i]

    route = [0] + middle + [0]
    return route


# -----------------------------
# Genetic Algorithm (Max Speed)
# -----------------------------
def genetic_algorithm_max_speed(distance_matrix,
                               time_matrix, n,
                               pop_size=50,
                               generations=200,
                               mutation_rate=0.1):

    population = create_population_speed(pop_size, n)

    best_route = None
    best_speed = -1
    best_dist = 0
    best_time = 0

    for gen in range(generations):

        new_population = []

        for _ in range(pop_size):
            parent1 = selection_speed(population, distance_matrix, time_matrix)
            parent2 = selection_speed(population, distance_matrix, time_matrix)

            child = crossover_speed(parent1, parent2)
            child = mutate_speed(child, mutation_rate)

            new_population.append(child)

        population = new_population

        # Track best solution
        for route in population:
            speed = fitness_speed(route, distance_matrix, time_matrix)

            if speed > best_speed:
                best_speed = speed
                best_route = route
                best_dist = route_distance_speed(route, distance_matrix)
                best_time = route_time_speed(route, time_matrix)

        # print(f"Generation {gen+1} | Best Speed: {best_speed:.4f}")

    return best_route, best_speed, best_dist, best_time