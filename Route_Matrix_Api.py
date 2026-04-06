import requests
import numpy as np

GOOGLE_API_KEY = "AIzaSyBcAMogU9a6TN8VVF-N2Y8-Bv1S7hSGXCM"

def get_distance_time_matrix_routes(locations_np):
    """
    locations_np: NumPy array of shape (n, 2) -> [[lat, lng], ...]
    returns:
        distance_matrix (meters)  -> NumPy array
        time_matrix (seconds)     -> NumPy array
    """

    n = locations_np.shape[0]

    url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "originIndex,destinationIndex,distanceMeters,duration"
    }

    # Build origins & destinations from NumPy array
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
        for i in range(n)
    ]

    payload = {
        "origins": origins,
        "destinations": origins,   # full adjacency matrix
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE"
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    results = response.json()

    # Initialize NumPy matrices
    distance_matrix = np.zeros((n, n), dtype=np.int32)
    time_matrix = np.zeros((n, n), dtype=np.int32)

    # Fill matrices
    for item in results:
        i = item["originIndex"]
        j = item["destinationIndex"]

        distance_matrix[i, j] = item.get("distanceMeters", 0)
        time_matrix[i, j] = int(item["duration"].replace("s", ""))

    return distance_matrix, time_matrix
#l=np.array([(17.779241,83.224572),(17.729316,83.318806),(17.781668,83.385004),(17.728663,83.223558)])
#print(get_distance_time_matrix_routes(l))