import statistics

def calculate_metrics(assignments, distance_matrix):
    total_distance = 0
    load_counts = []

    for agent_id, delivery_ids in assignments.items():
        load_counts.append(len(delivery_ids))

        for delivery_id in delivery_ids:
            total_distance += distance_matrix[(agent_id, delivery_id)]

    avg_load = statistics.mean(load_counts)
    std_dev_load = statistics.stdev(load_counts) if len(load_counts) > 1 else 0
    max_load = max(load_counts)
    min_load = min(load_counts)

    return {
        "total_distance": round(total_distance, 2),
        "average_load": round(avg_load, 2),
        "load_std_dev": round(std_dev_load, 2),
        "max_load": max_load,
        "min_load": min_load
    }