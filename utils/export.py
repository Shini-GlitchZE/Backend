import csv
import os

def export_assignments_to_csv(assignments, deliveries, filename="outputs/assignment_output.csv"):

    # Create outputs folder if not exists
    os.makedirs("outputs", exist_ok=True)

    # Map delivery_id → coordinates
    delivery_lookup = {d["id"]: d for d in deliveries}

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)

        # Header
        writer.writerow(["agent_id", "delivery_id", "lat", "lng"])

        # Data
        for agent_id, delivery_ids in assignments.items():
            for d_id in delivery_ids:
                d = delivery_lookup[d_id]
                writer.writerow([agent_id, d_id, d["lat"], d["lng"]])

    print(f"\nCSV Exported Successfully -> {filename}")