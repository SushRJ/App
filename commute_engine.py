import openrouteservice
import time

CO2_PER_MIN = 0.14

# ORS client
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjVjM2FhOTkxZDU1NzQ1MDRiZGM1MDYyMTMwMGZkY2RiIiwiaCI6Im11cm11cjY0In0="
ors_client = openrouteservice.Client(key=ORS_API_KEY)

def get_travel_info(origin, destination):
    """Call ORS distance matrix to get distance (km) and duration (min)."""
    response = ors_client.distance_matrix(
        locations=[[origin["longitude"], origin["latitude"]],
                   [destination["longitude"], destination["latitude"]]],
        profile="driving-car",
        metrics=["distance", "duration"]
    )
    distance_km = response["distances"][0][1] / 1000
    duration_min = response["durations"][0][1] / 60
    return distance_km, duration_min

def compute_travel_times(employees, office):
    """Compute distance, travel time, weekly commute, and CO2 per employee."""
    for emp in employees:
        distance, travel_time = get_travel_info(office, emp)
        emp["distance_km"] = round(distance, 2)
        emp["travel_time_min"] = round(travel_time, 1)
        emp["weekly_commute_min"] = round(travel_time * 5, 1) # default 5 WFO days
        emp["co2_per_week"] = round(travel_time * CO2_PER_MIN * 5, 1)
    return employees
