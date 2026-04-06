import csv

def load_csv_dataset(file_path):
    agents = []
    deliveries = []

    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)

        for i, row in enumerate(reader):

            # Clean keys + values (removes spaces / empty issues / BOMs)
            clean_row = {}
            for k, v in row.items():
                if k:
                    clean_k = str(k).replace('\ufeff', '').replace('\xef\xbb\xbf', '').strip()
                    clean_row[clean_k] = str(v).strip() if v else ""
            row = clean_row

            # ✅ AGENTS (only rows where Agent_ID exists)
            if row.get("Agent_ID"):
                try:
                    agents.append({
                        "id": row["Agent_ID"],
                        "lat": float(row.get("Start_Latitude", 0)),
                        "lng": float(row.get("Start_Longitude", 0))
                    })
                except (ValueError, KeyError):
                    print(f"⚠️ Skipping invalid agent row {i+1}")
                    continue

            # ✅ DELIVERIES (independent of agents)
            drop_lat = row.get("Drop_Latitude") or row.get("Delivery_Latitude")
            drop_lng = row.get("Drop_Longitude") or row.get("Delivery_Longitude")
            
            if drop_lat and drop_lng:
                try:
                    deliveries.append({
                        "id": f"D{i+1}",
                        "lat": float(drop_lat),
                        "lng": float(drop_lng)
                    })
                except (ValueError, KeyError):
                    print(f"⚠️ Skipping invalid delivery row {i+1}")
                    continue

    return agents, deliveries