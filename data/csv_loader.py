import csv

def load_csv_dataset(file_path):
    agents = []
    deliveries = []

    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)

        for i, row in enumerate(reader):

            # Clean keys + values (removes spaces / empty issues)
            row = {k.strip(): (v.strip() if v else "") for k, v in row.items()}

            # ✅ AGENTS (only rows where Agent_ID exists)
            if row["Agent_ID"]:
                try:
                    agents.append({
                        "id": row["Agent_ID"],
                        "lat": float(row["Start_Latitude"]),
                        "lng": float(row["Start_Longitude"])
                    })
                except ValueError:
                    print(f"⚠️ Skipping invalid agent row {i+1}")
                    continue

            # ✅ DELIVERIES (independent of agents)
            if row["Drop_Latitude"] and row["Drop_Longitude"]:
                try:
                    deliveries.append({
                        "id": f"D{i+1}",
                        "lat": float(row["Drop_Latitude"]),
                        "lng": float(row["Drop_Longitude"])
                    })
                except ValueError:
                    print(f"⚠️ Skipping invalid delivery row {i+1}")
                    continue

    return agents, deliveries