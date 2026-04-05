import numpy as np
from sklearn.cluster import KMeans

def kmeans_assignment(agents, deliveries):
    coords = np.array([[d["lat"], d["lng"]] for d in deliveries])
    kmeans = KMeans(n_clusters=len(agents), random_state=0).fit(coords)

    assignments = {a["id"]: [] for a in agents}

    for i, label in enumerate(kmeans.labels_):
        assignments[agents[label]["id"]].append(deliveries[i]["id"])

    return assignments
