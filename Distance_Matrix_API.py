import requests
import numpy as np

# Hard-coded Google API key (for testing only)
GOOGLE_API_KEY = ""

def get_distance_time_matrix(locations):
    """
    locations: list of (lat, lng)
    returns:
        distance_matrix (meters)
        time_matrix (seconds, traffic-aware)
    """
    origins = "|".join([f"{lat},{lng}" for lat, lng in locations])
    destinations = origins

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origins,
        "destinations": destinations,
        "key": GOOGLE_API_KEY,
        "departure_time": "now",      # enables traffic
        "traffic_model": "best_guess"
    }

    response = requests.get(url, params=params)
    data = response.json()
    

    # Initialize NumPy arrays
    n = len(data["rows"])
    distance_matrix = np.zeros((n, n), dtype=int)
    time_matrix = np.zeros((n, n), dtype=int)
    
    for i, row in enumerate(data["rows"]):
        for j, elem in enumerate(row["elements"]):
            distance_matrix[i, j] = elem["distance"]["value"]             # meters
            time_matrix[i, j] = elem["duration_in_traffic"]["value"]     # seconds
    
       

    return distance_matrix, time_matrix

#input format
'''l=[(17.779241,83.224572),(17.729316,83.318806),(17.781668,83.385004),(17.728663,83.223558)]
dist,time=get_distance_time_matrix(l)
print(dist)
print(time)'''


import time

#GOOGLE_API_KEY = "YOUR_API_KEY"

def chunk_list(lst, chunk_size):
    """Yield successive chunk_size chunks from list."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def get_distance_time_matrix_all(locations):
    """
    locations: list of (lat, lng)
    returns:
        distance_matrix (meters)
        time_matrix (seconds, traffic-aware)
    """

    n = len(locations)

    # Initialize full matrices
    distance_matrix = np.zeros((n, n), dtype=int)
    time_matrix = np.zeros((n, n), dtype=int)

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    # Because max elements = 100,
    # we use 10x10 blocks (10*10 = 100)
    max_block_size = 10

    origin_blocks = list(chunk_list(locations, max_block_size))
    dest_blocks = list(chunk_list(locations, max_block_size))

    origin_start = 0

    for origin_block in origin_blocks:

        destination_start = 0

        origins_str = "|".join([f"{lat},{lng}" for lat, lng in origin_block])

        for dest_block in dest_blocks:

            destinations_str = "|".join([f"{lat},{lng}" for lat, lng in dest_block])

            params = {
                "origins": origins_str,
                "destinations": destinations_str,
                "key": GOOGLE_API_KEY,
                "departure_time": "now",
                "traffic_model": "best_guess"
            }

            response = requests.get(url, params=params)
            data = response.json()

            # Fill matrices
            for i, row in enumerate(data["rows"]):
                for j, elem in enumerate(row["elements"]):

                    global_i = origin_start + i
                    global_j = destination_start + j

                    if elem["status"] == "OK":
                        distance_matrix[global_i, global_j] = elem["distance"]["value"]
                        time_matrix[global_i, global_j] = elem["duration_in_traffic"]["value"]
                    else:
                        distance_matrix[global_i, global_j] = 0
                        time_matrix[global_i, global_j] = 0

            destination_start += len(dest_block)

            time.sleep(0.1)  # small delay to avoid rate spikes

        origin_start += len(origin_block)

    return distance_matrix, time_matrix


