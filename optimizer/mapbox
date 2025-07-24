import requests
from geopy.distance import geodesic
from datetime import datetime

class MapboxOptimizer:
    def __init__(self, access_token):
        self.access_token = access_token

    def get_optimized_route(self, waypoints):
        coords = ';'.join([f'{lon},{lat}' for lat, lon in waypoints])
        url = f"https://api.mapbox.com/optimized-trips/v1/mapbox/driving/{coords}?geometries=geojson&access_token={self.access_token}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data['trips']:
                return [[coord[1], coord[0]] for coord in data['trips'][0]['geometry']['coordinates']], \
                       data['trips'][0]['distance'], data['trips'][0]['duration']
            return [waypoints[0], waypoints[-1]], 0, 0
        except requests.RequestException:
            return [waypoints[0], waypoints[-1]], 0, 0

    def haversine(self, coord1, coord2):
        lat1, lon1 = map(float, coord1.split(','))
        lat2, lon2 = map(float, coord2.split(','))
        return geodesic((lat1, lon1), (lat2, lon2)).km

    def calculate_matching_score(self, driver_entry, rider_entry, driver_user):
        if driver_user is None:
            return 0
        pickup_distance = self.haversine(driver_entry[6], rider_entry[6])
        dropoff_distance = self.haversine(driver_entry[7], rider_entry[7])
        max_distance = 10
        distance_score = max(0, 1 - (pickup_distance + dropoff_distance) / (2 * max_distance)) * 50

        driver_start = datetime.strptime(driver_entry[3], '%H:%M:%S').time()
        driver_end = datetime.strptime(driver_entry[4], '%H:%M:%S').time()
        rider_start = datetime.strptime(rider_entry[3], '%H:%M:%S').time()
        rider_end = datetime.strptime(rider_entry[4], '%H:%M:%S').time()
        latest_start = max(driver_start, rider_start)
        earliest_end = min(driver_end, rider_end)
        overlap_minutes = (earliest_end.hour * 60 + earliest_end.minute - latest_start.hour * 60 - latest_start.minute)
        total_minutes = 60
        time_score = max(0, overlap_minutes / total_minutes) * 30 if overlap_minutes > 0 else 0

        detour_time = (pickup_distance + dropoff_distance) * 5
        delay_score = (1 if detour_time <= driver_user[5] else 0) * 20

        return round(distance_score + time_score + delay_score, 2)