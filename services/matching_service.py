from typing import List, Optional, Dict, Any
from datetime import datetime, date
from math import radians, sin, cos, asin, sqrt
from models.scheduleEntry import ScheduleEntry
from models.user import User
from repositories.schedule_entries_repository import get_schedule_for_user, get_all_schedule_entries
from repositories.users_repository import get_user

def haversine_km(a: List[float], b: List[float]) -> float:
    lat1, lon1 = a
    lat2, lon2 = b
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    h = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 2 * R * asin(sqrt(h))

def overlap_minutes(s1, e1, s2, e2) -> int:
    s1m, e1m = s1.hour*60 + s1.minute, e1.hour*60 + e1.minute
    s2m, e2m = s2.hour*60 + s2.minute, e2.hour*60 + e2.minute
    return max(0, min(e1m, e2m) - max(s1m, s2m))

def score_match(driver: ScheduleEntry, rider: ScheduleEntry) -> float:
    pickup_distance = haversine_km(driver.pickup, rider.pickup)
    dropoff_distance = haversine_km(driver.dropoff, rider.dropoff)
    distance_score = max(0.0, 1.0 - (pickup_distance + dropoff_distance) / (2 * 10.0)) * 50.0
    overlap = overlap_minutes(driver.start_time, driver.arrival_time, rider.start_time, rider.arrival_time)
    time_score = (overlap / 60.0) * 30.0 if overlap > 0 else 0.0
    detour_time = (pickup_distance + dropoff_distance) * 5.0
    delay_score = (1.0 if (driver.max_delay or 0) >= detour_time else 0.0) * 20.0
    return round(distance_score + time_score + delay_score, 2)

def _same_day(d: date, e: ScheduleEntry) -> bool:
    ed = e.date.date() if isinstance(e.date, datetime) else e.date
    return ed == d

def _summary(entry: ScheduleEntry, user: User) -> Dict[str, Any]:
    return {
        "schedule_id": entry.id,
        "user_id": entry.user_id,
        "user_name": f"{user.firstName} {user.lastName}",
        "role": entry.role,
        "direction": entry.direction,
        "date": entry.date.isoformat() if isinstance(entry.date, datetime) else entry.date,
        "start_time": entry.start_time.isoformat() if entry.start_time else None,
        "arrival_time": entry.arrival_time.isoformat() if entry.arrival_time else None,
        "pickup": entry.pickup,
        "dropoff": entry.dropoff,
        "ride_id": entry.ride_id,
    }

class MatchingService:
    def drivers_for_rider(self, rider_id: str, on_date: Optional[date]):
        rider_entries = [e for e in get_schedule_for_user(rider_id) if e.role == "rider"]
        if on_date:
            rider_entries = [e for e in rider_entries if _same_day(on_date, e)]
        if not rider_entries:
            return {"rider_entry_id": None, "matches": []}
        rider_entry = rider_entries[0]

        all_entries = get_all_schedule_entries()
        drivers = [e for e in all_entries if e.role == "driver" and e.direction == rider_entry.direction]
        if on_date:
            drivers = [e for e in drivers if _same_day(on_date, e)]

        matches = []
        for d in drivers:
            driver_user = get_user(d.user_id)
            if not driver_user:
                continue
            matches.append({"score": score_match(d, rider_entry), "driver": _summary(d, driver_user)})
        matches.sort(key=lambda x: x["score"], reverse=True)
        return {"rider_entry_id": rider_entry.id, "matches": matches}

    def riders_for_driver(self, driver_id: str, on_date: Optional[date]):
        driver_entries = [e for e in get_schedule_for_user(driver_id) if e.role == "driver"]
        if on_date:
            driver_entries = [e for e in driver_entries if _same_day(on_date, e)]
        if not driver_entries:
            return {"driver_entry_id": None, "matches": []}
        driver_entry = driver_entries[0]

        all_entries = get_all_schedule_entries()
        riders = [e for e in all_entries if e.role == "rider" and e.direction == driver_entry.direction]
        if on_date:
            riders = [e for e in riders if _same_day(on_date, e)]

        matches = []
        for r in riders:
            rider_user = get_user(r.user_id)
            if not rider_user:
                continue
            matches.append({"score": score_match(driver_entry, r), "rider": _summary(r, rider_user)})
        matches.sort(key=lambda x: x["score"], reverse=True)
        return {"driver_entry_id": driver_entry.id, "matches": matches}

matching_service = MatchingService()