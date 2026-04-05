import networkx as nx

def minimum_cost_max_flow_assignment(agents, deliveries, distance_matrix, max_capacity):

    G = nx.DiGraph()

    source = "source"
    sink = "sink"

    total_deliveries = len(deliveries)

    # Add source and sink with demands
    G.add_node(source, demand=-total_deliveries)
    G.add_node(sink, demand=total_deliveries)

    # Add agent nodes
    for agent in agents:
        agent_node = f"agent_{agent['id']}"
        G.add_node(agent_node, demand=0)
        G.add_edge(source, agent_node, capacity=max_capacity, weight=0)

    # Add delivery nodes
    for delivery in deliveries:
        delivery_node = f"delivery_{delivery['id']}"
        G.add_node(delivery_node, demand=0)
        G.add_edge(delivery_node, sink, capacity=1, weight=0)

    # Connect agents to deliveries
    for agent in agents:
        agent_node = f"agent_{agent['id']}"
        for delivery in deliveries:
            delivery_node = f"delivery_{delivery['id']}"
            cost = int(distance_matrix[(agent["id"], delivery["id"])])
            G.add_edge(agent_node, delivery_node, capacity=1, weight=cost)

    # Solve using min_cost_flow (stable)
    flow_dict = nx.min_cost_flow(G)

    assignments = {agent["id"]: [] for agent in agents}

    for agent in agents:
        agent_node = f"agent_{agent['id']}"
        for delivery in deliveries:
            delivery_node = f"delivery_{delivery['id']}"
            if flow_dict[agent_node].get(delivery_node, 0) > 0:
                assignments[agent["id"]].append(delivery["id"])

    return assignments