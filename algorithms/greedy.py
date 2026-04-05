def incremental_cost_greedy(agents, deliveries, distance_matrix):
    assignments = {a["id"]: [] for a in agents}
    agent_cost = {a["id"]: 0 for a in agents}

    # 🔥 Load balancing constraint
    max_deliveries = len(deliveries) // len(agents) + 5

    for d in deliveries:
        best_agent = None
        best_cost = float("inf")

        for a in agents:
            agent_id = a["id"]

            # Skip if agent overloaded
            if len(assignments[agent_id]) >= max_deliveries:
                continue

            cost = agent_cost[agent_id] + distance_matrix[(agent_id, d["id"])]

            if cost < best_cost:
                best_cost = cost
                best_agent = agent_id

        # Fallback if all full
        if best_agent is None:
            best_agent = min(agent_cost, key=agent_cost.get)

        assignments[best_agent].append(d["id"])
        agent_cost[best_agent] += distance_matrix[(best_agent, d["id"])]

    return assignments