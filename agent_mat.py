import numpy as np
import requests
import json
import math
import time


def get_agent_delivery_matrix(
    agents_np,
    deliveries_np,
    routing_preference="TRAFFIC_AWARE",
    max_elements_per_minute=3000
):
    api_key = "AIzaSyBcAMogU9a6TN8VVF-N2Y8-Bv1S7hSGXCM"   # 🔴 Put your key here
    if not api_key:
        raise ValueError("Google API key is missing.")

    agents_np = np.array(agents_np)
    deliveries_np = np.array(deliveries_np)
    A = agents_np.shape[0]
    D = deliveries_np.shape[0]

    url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"

    # API element limits
    if routing_preference == "TRAFFIC_AWARE_OPTIMAL":
        max_elements_per_request = 100
    else:
        max_elements_per_request = 625

    batch_size = int(math.floor(math.sqrt(max_elements_per_request)))

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "originIndex,destinationIndex,distanceMeters,duration"
    }
    print("API called")
    distance_matrix = np.zeros((A, D))
    time_matrix = np.zeros((A, D))

    elements_sent_this_minute = 0
    minute_window_start = time.time()

    for i_start in range(0, A, batch_size):
        for j_start in range(0, D, batch_size):

            i_end = min(i_start + batch_size, A)
            j_end = min(j_start + batch_size, D)

            elements_this_request = (i_end - i_start) * (j_end - j_start)

            # ---- Rate limiting ----
            now = time.time()

            if now - minute_window_start >= 60:
                elements_sent_this_minute = 0
                minute_window_start = now

            if elements_sent_this_minute + elements_this_request > max_elements_per_minute:
                sleep_time = 60 - (now - minute_window_start)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                elements_sent_this_minute = 0
                minute_window_start = time.time()

            # ---- Origins (Agents) ----
            origins = [
                {
                    "waypoint": {
                        "location": {
                            "latLng": {
                                "latitude": float(agents_np[i, 0]),
                                "longitude": float(agents_np[i, 1])
                            }
                        }
                    }
                }
                for i in range(i_start, i_end)
            ]

            # ---- Destinations (Deliveries) ----
            destinations = [
                {
                    "waypoint": {
                        "location": {
                            "latLng": {
                                "latitude": float(deliveries_np[j, 0]),
                                "longitude": float(deliveries_np[j, 1])
                            }
                        }
                    }
                }
                for j in range(j_start, j_end)
            ]

            payload = {
                "origins": origins,
                "destinations": destinations,
                "travelMode": "DRIVE",
                "routingPreference": routing_preference
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code != 200:
                raise Exception(f"HTTP Error {response.status_code}: {response.text}")

            raw_text = response.text.strip()

            # ---- Handle JSON / NDJSON ----
            if raw_text.startswith("["):
                items = response.json()
            else:
                items = [json.loads(line) for line in raw_text.split("\n") if line.strip()]

            # ---- Fill matrix ----
            for item in items:
                if "originIndex" not in item or "destinationIndex" not in item:
                    continue

                global_i = i_start + item["originIndex"]
                global_j = j_start + item["destinationIndex"]

                distance_matrix[global_i, global_j] = item.get("distanceMeters", 0)

                duration_str = item.get("duration", "0s").replace("s", "")
                time_matrix[global_i, global_j] = float(duration_str)

            elements_sent_this_minute += elements_this_request

    return distance_matrix, time_matrix