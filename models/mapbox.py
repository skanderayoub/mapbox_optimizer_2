import requests
from typing import List, Optional, Dict
import logging
import config

MAPBOX_OPTIMIZATION_API_URL = "https://api.mapbox.com/optimized-trips/v1/mapbox/driving-traffic/"
MAPBOX_DIRECTIONS_API_URL = "https://api.mapbox.com/directions/v5/mapbox/driving-traffic/"
MAPBOX_ACCESS_TOKEN = config.MAPBOX_ACCESS_TOKEN

class MapboxOptimizer:
    def __init__(self, access_token: str = MAPBOX_ACCESS_TOKEN) -> None:
        self.access_token = access_token

    def calculate_direct_route(self, start: List[float], end: List[float]) -> Optional[Dict]:
        # Ensure coordinates are [lon, lat]
        start_lonlat = [start[1], start[0]]
        end_lonlat = [end[1], end[0]]
        coords_str = f"{start[1]},{start[0]};{end[1]},{end[0]}"
        url = f"{MAPBOX_DIRECTIONS_API_URL}{coords_str}?geometries=geojson&overview=full&steps=true&access_token={self.access_token}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data.get("routes"):
                route = data["routes"][0]
                geometry_coords = route["geometry"]["coordinates"]
                # Convert [lon, lat] pairs to [{"lat": ..., "lng": ...}, ...]
                geometry = [{"lat": coord[1], "lng": coord[0]}
                            for coord in geometry_coords]
                result = {
                    "distance": route["distance"] / 1000,
                    "duration": route["duration"] / 60,
                    "type": route["geometry"]["type"],
                    "geometry": geometry
                }
                # print('Direct route result:', result)  # Debug print
            return result
        except requests.RequestException as e:
            return None

    def calculate_optimized_route(self, coordinates: List[List[float]]) -> Optional[Dict]:
        if len(coordinates) < 2 or len(coordinates) > 12:
            logging.warning(
                f"Invalid number of waypoints: {len(coordinates)}. Must be 2-12.")
            return None
        coords_str = ";".join(f"{lon},{lat}" for lat, lon in coordinates)
        url = f"{MAPBOX_OPTIMIZATION_API_URL}{coords_str}?geometries=geojson&overview=full&source=first&destination=last&roundtrip=false&steps=true&access_token={self.access_token}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data.get("trips"):
                trip = data["trips"][0]
                waypoint_indices = data.get("waypoints", [])
                if len(waypoint_indices) != len(coordinates):
                    return None
                legs = trip.get("legs", [])
                leg_durations = [leg["duration"] / 60 for leg in legs]
                steps = []
                for leg in legs:
                    steps.extend(leg.get("steps", []))
                # Convert geometry to list of dicts
                geometry_coords = trip["geometry"]["coordinates"]
                geometry = [{"lat": coord[1], "lng": coord[0]}
                            for coord in geometry_coords]
                result = {
                    "geometry": geometry,
                    "distance": trip["distance"] / 1000,
                    "duration": trip["duration"] / 60,
                    "waypoint_indices": [wp["waypoint_index"] for wp in waypoint_indices],
                    "leg_durations": leg_durations,
                    "steps": steps
                }
                return result
            return None
        except requests.RequestException as e:
            return None
