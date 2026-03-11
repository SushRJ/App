CO2_PER_MIN = 0.14

def office_fit_score(employees, acceptable_commute_min=45):
    """Compute percentage of employees within acceptable commute."""
    if not employees:
        return 0, "N/A"
    fit_count = sum(1 for e in employees if e["travel_time_min"] <= acceptable_commute_min)
    fit_pct = round(fit_count / len(employees) * 100, 1)
    if fit_pct < 50:
        label = "Poor"
    elif fit_pct < 70:
        label = "Fair"
    else:
        label = "Good"
    return fit_pct, label

def commute_distribution(employees, low=30, medium=45):
    """Return count of Low, Moderate, High commute."""
    dist = {"low": 0, "medium": 0, "high": 0}
    for e in employees:
        if e["travel_time_min"] < low:
            dist["low"] += 1
        elif e["travel_time_min"] <= medium:
            dist["medium"] += 1
        else:
            dist["high"] += 1
    total = len(employees)
    return {k: round(v/total*100,1) for k,v in dist.items()}

def wfo_impact(employees, wfo_days):
    """Compute average commute per week and CO2."""
    if not employees:
        return 0, 0, 0, 0
    total_time = sum(e["travel_time_min"] for e in employees)
    total_distance = sum(e["distance_km"] for e in employees)
    avg_commute_per_week = round(total_time * wfo_days / len(employees) / 60, 1) # hours per week
    co2_per_week = round(sum(e["travel_time_min"]*CO2_PER_MIN*wfo_days for e in employees)/len(employees), 1)
    marginal_commute_per_day = round(total_time / len(employees) / 60, 1) # hours/day
    marginal_co2_per_day = round(total_distance / len(employees) * CO2_PER_MIN, 1)
    return avg_commute_per_week, co2_per_week, marginal_commute_per_day, marginal_co2_per_day


