import numpy as np
import requests
import json
import math
import time


def get_distance_time_matrix_routes_batched(
    locations_np,
    routing_preference="TRAFFIC_AWARE_OPTIMAL",
    max_elements_per_minute=3000
):
    api_key = ""   # 🔴 Put your key here
    if not api_key:
        raise ValueError("Google API key is missing.")

    n = locations_np.shape[0]
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

    distance_matrix = np.zeros((n, n))
    time_matrix = np.zeros((n, n))

    elements_sent_this_minute = 0
    minute_window_start = time.time()

    for i_start in range(0, n, batch_size):
        for j_start in range(0, n, batch_size):

            i_end = min(i_start + batch_size, n)
            j_end = min(j_start + batch_size, n)

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

            # ---- Build origins ----
            origins = [
                {
                    "waypoint": {
                        "location": {
                            "latLng": {
                                "latitude": float(locations_np[i, 0]),
                                "longitude": float(locations_np[i, 1])
                            }
                        }
                    }
                }
                for i in range(i_start, i_end)
            ]

            # ---- Build destinations ----
            destinations = [
                {
                    "waypoint": {
                        "location": {
                            "latLng": {
                                "latitude": float(locations_np[j, 0]),
                                "longitude": float(locations_np[j, 1])
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

            # ---- HTTP error handling ----
            if response.status_code != 200:
                raise Exception(f"HTTP Error {response.status_code}: {response.text}")

            raw_text = response.text.strip()

            # -------------------------------------------------
            # HANDLE BOTH POSSIBLE RESPONSE FORMATS
            # -------------------------------------------------

            # Case 1: JSON Array
            if raw_text.startswith("["):
                data = response.json()
                items = data

            # Case 2: NDJSON
            else:
                items = []
                for line in raw_text.split("\n"):
                    line = line.strip()
                    if line:
                        items.append(json.loads(line))

            # -------------------------------------------------
            # Fill matrices
            # -------------------------------------------------
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