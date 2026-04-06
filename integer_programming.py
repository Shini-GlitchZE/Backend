import pulp
import numpy as np

def _solve_ilp_tsp(cost_matrix, n, maximize=False):
    """
    Core function to solve TSP using MTZ Integer Linear Programming formulation.
    Returns: list representing the route, float representing optimal cost.
    """
    if n <= 1:
        return [0], 0

    # Create the PuLP model
    prob_type = pulp.LpMaximize if maximize else pulp.LpMinimize
    prob = pulp.LpProblem("TSP_MTZ", prob_type)

    # Decision variables
    # x[i][j] = 1 if route goes from i to j, else 0
    x = pulp.LpVariable.dicts("x", ((i, j) for i in range(n) for j in range(n)), cat="Binary")
    
    # u[i] = dummy variable for MTZ subtour elimination
    u = pulp.LpVariable.dicts("u", (i for i in range(1, n)), lowBound=0, upBound=n-1, cat="Integer")

    # Objective function
    prob += pulp.lpSum(cost_matrix[i][j] * x[i, j] for i in range(n) for j in range(n) if i != j)

    # Constraints
    # 1. Exactly one outgoing edge
    for i in range(n):
        prob += pulp.lpSum(x[i, j] for j in range(n) if i != j) == 1

    # 2. Exactly one incoming edge
    for j in range(n):
        prob += pulp.lpSum(x[i, j] for i in range(n) if i != j) == 1

    # 3. Subtour Elimination (MTZ)
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                prob += u[i] - u[j] + n * x[i, j] <= n - 1

    # Solve quietly with a time limit of 30 seconds
    # Uses GUROBI solver via gurobipy for enterprise-grade speed
    # Choose solver timeout based on problem size
    if n <= 15:
        # Small problems solve instantly – give solver unlimited time
        solver = pulp.GUROBI(msg=0)
    else:
        # Larger problems – keep 300‑second cap to avoid long hangs
        solver = pulp.GUROBI(msg=0, timeLimit=300)
    prob.solve(solver)

    # If infeasible or not optimal
    if pulp.LpStatus[prob.status] != "Optimal":
        return None, None

    # Reconstruct route starting from 0
    route = [0]
    current = 0
    
    total_cost = pulp.value(prob.objective)

    for _ in range(n - 1):
        for j in range(n):
            if current != j and pulp.value(x[current, j]) == 1.0:
                route.append(j)
                current = j
                break
    
    # Return to depot
    route.append(0)

    return route, total_cost

def ilp_min_distance(distance_matrix, n, start=0):
    route, cost_val = _solve_ilp_tsp(distance_matrix, n, maximize=False)
    if route is None: return None, 0
    return [int(x) for x in route], float(cost_val)

def ilp_min_time(time_matrix, n, start=0):
    route, cost_val = _solve_ilp_tsp(time_matrix, n, maximize=False)
    if route is None: return None, 0
    return [int(x) for x in route], float(cost_val)

def ilp_max_speed(distance_matrix, time_matrix, n, start=0):
    # To maximize speed Edge-by-Edge: speed_matrix = dist / time
    speed_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j and time_matrix[i][j] > 0:
                speed_matrix[i][j] = distance_matrix[i][j] / time_matrix[i][j]
    
    route, _ = _solve_ilp_tsp(speed_matrix, n, maximize=True)
    
    # Recalculate true speed (Total Dist / Total Time)
    if route is None:
        return None, 0
    
    tot_dist = 0
    tot_time = 0
    for idx in range(len(route) - 1):
        i = route[idx]
        j = route[idx+1]
        tot_dist += distance_matrix[i][j]
        tot_time += time_matrix[i][j]
    
    avg_spd = tot_dist / tot_time if tot_time > 0 else 0
    if route is None: return None, 0
    return [int(x) for x in route], float(avg_spd)
