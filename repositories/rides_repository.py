from typing import List, Optional

from models.ride import Ride
from models.ridePassegenrs import RidePassenger
from repositories.base_repository import save_object, get_object, get_all_objects
from core.firebase import db

COLLECTION_NAME = "rides"


def save_ride(ride: Ride) -> None:
    save_object(ride, COLLECTION_NAME)


def get_ride(ride_id: str) -> Optional[Ride]:
    return get_object(Ride, ride_id, COLLECTION_NAME)


def get_all_rides() -> List[Ride]:
    return get_all_objects(Ride, COLLECTION_NAME)


def add_ride_passenger(ride_id: str, user_id: str, status: str = "Ready", joined_at=None) -> RidePassenger:
    from repositories.rides_repository import get_ride, save_ride
    ride = get_ride(ride_id)
    if ride is None:
        raise ValueError("Ride not found")
    if user_id == ride.user_id:
        raise ValueError("Driver cannot be a passenger in their own ride")
    if ride.current_riders >= ride.max_riders:
        raise ValueError("Ride is full")
    existing = db.collection("ridepassengers").document(f"{ride_id}_{user_id}").get()
    if existing.exists:
        raise ValueError("User is already a passenger in this ride")
    passenger = RidePassenger(ride_id, user_id, status, joined_at)
    save_object(passenger, "ridepassengers")
    ride.current_riders += 1
    save_ride(ride)
    return passenger


def remove_ride_passenger(ride_id: str, user_id: str) -> None:
    from repositories.rides_repository import get_ride, save_ride
    ride = get_ride(ride_id)
    if ride is None:
        raise ValueError("Ride not found")
    if user_id == ride.user_id:
        raise ValueError("Driver cannot be removed as a passenger (driver is not a passenger)")
    passenger_id = f"{ride_id}_{user_id}"
    doc = db.collection("ridepassengers").document(passenger_id).get()
    if not doc.exists:
        raise ValueError("Passenger not found in this ride")
    db.collection("ridepassengers").document(passenger_id).delete()
    ride.current_riders = max(0, ride.current_riders - 1)
    save_ride(ride)


def get_passengers_for_ride(ride_id: str) -> List[RidePassenger]:
    docs = db.collection("ridepassengers").where("ride_id", "==", ride_id).stream()
    return [RidePassenger.from_dict(doc.to_dict()) for doc in docs]


def get_rides_for_user(user_id: str) -> List[RidePassenger]:
    docs = db.collection("ridepassengers").where("user_id", "==", user_id).stream()
    return [RidePassenger.from_dict(doc.to_dict()) for doc in docs]


