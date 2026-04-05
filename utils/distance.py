import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon/2)**2

    return 2 * R * math.asin(math.sqrt(a))


def build_distance_matrix(agents, deliveries):
    matrix = {}
    for a in agents:
        for d in deliveries:
            matrix[(a["id"], d["id"])] = haversine(
                a["lat"], a["lng"], d["lat"], d["lng"]
            )
    return matrix
