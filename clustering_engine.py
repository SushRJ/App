import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

MIN_AVG_COMMUTE_MIN = 30

def get_direction(office, cluster_center):
    lat_diff = cluster_center[0] - office[0]
    lon_diff = cluster_center[1] - office[1]
    if abs(lat_diff) > abs(lon_diff):
        return "North Cluster" if lat_diff > 0 else "South Cluster"
    else:
        return "East Cluster" if lon_diff > 0 else "West Cluster"

def auto_cluster_radius_km(employees, min_sample_size=6):
    coords = np.radians([[e["latitude"], e["longitude"]] for e in employees])
    nbrs = NearestNeighbors(n_neighbors=min_sample_size, metric="haversine").fit(coords)
    distances, _ = nbrs.kneighbors(coords)
    kth_distances_km = distances[:, min_sample_size-1] * 6371
    radius_km = np.percentile(kth_distances_km, 90)
    radius_km = np.clip(radius_km, 0.5, 5.0)
    return round(radius_km, 2)

def cluster_driven_hub_opportunity(employees, office):
    coords = np.array([[e["latitude"], e["longitude"]] for e in employees])
    MIN_CLUSTER_SIZE = 6
    CLUSTER_RADIUS_KM = auto_cluster_radius_km(employees, MIN_CLUSTER_SIZE)
    epsilon = CLUSTER_RADIUS_KM / 6371
    db = DBSCAN(eps=epsilon, min_samples=MIN_CLUSTER_SIZE, metric="haversine").fit(np.radians(coords))
    for idx, e in enumerate(employees):
        e["cluster"] = int(db.labels_[idx])
    clusters = []
    for cluster_id in set(db.labels_):
        if cluster_id == -1:
            continue
        cluster_members = [e for e in employees if e["cluster"] == cluster_id]
        if len(cluster_members) <= MIN_CLUSTER_SIZE:
            continue
        avg_commute = round(np.mean([m["travel_time_min"] for m in cluster_members]), 1)
        hub_lat = np.mean([m["latitude"] for m in cluster_members])
        hub_lon = np.mean([m["longitude"] for m in cluster_members])
        direction = get_direction([office["latitude"], office["longitude"]], [hub_lat, hub_lon])
        clusters.append({
            "cluster": direction,
            "members": len(cluster_members),
            "avg_commute": avg_commute,
            "hub_latitude": round(hub_lat,5),
            "hub_longitude": round(hub_lon,5)
        })
    return clusters, CLUSTER_RADIUS_KM