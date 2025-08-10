import firebase_admin
from firebase_admin import credentials, firestore
from models.user import User
from models.ride import Ride
from models.scheduleEntry import ScheduleEntry
from models.ridePassegenrs import RidePassenger
import config

# Initialize Firebase app and Firestore client
_creds = config.get_firebase_credentials()
if isinstance(_creds, dict):
    cred = credentials.Certificate(_creds)
else:
    cred = credentials.Certificate(_creds)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_object(obj, collection_name=None):
    """Save any model object to Firestore."""
    if collection_name is None:
        collection_name = obj.__class__.__name__.lower() + 's'
    db.collection(collection_name).document(obj.id).set(obj.to_dict())


def get_object(model_class, object_id, collection_name=None):
    """Retrieve any model object from Firestore by ID."""
    if collection_name is None:
        collection_name = model_class.__name__.lower() + 's'
    doc = db.collection(collection_name).document(object_id).get()
    if doc.exists:
        return model_class.from_dict(doc.to_dict())
    else:
        return None


def get_all_objects(model_class, collection_name=None):
    """Retrieve all objects of a model from Firestore."""
    if collection_name is None:
        collection_name = model_class.__name__.lower() + 's'
    docs = db.collection(collection_name).stream()
    return [model_class.from_dict(doc.to_dict()) for doc in docs]

# Specific helpers for each model (optional, for convenience)


def save_user(user: User):
    save_object(user, 'users')


def get_user(user_id: str) -> User:
    return get_object(User, user_id, 'users')


def get_all_users():
    return get_all_objects(User, 'users')


def save_ride(ride: Ride):
    save_object(ride, 'rides')


def get_ride(ride_id: str) -> Ride:
    return get_object(Ride, ride_id, 'rides')


def get_all_rides():
    return get_all_objects(Ride, 'rides')


def save_schedule_entry(entry: ScheduleEntry):
    save_object(entry, 'scheduleentrys')


def get_schedule_entry(entry_id: str) -> ScheduleEntry:
    return get_object(ScheduleEntry, entry_id, 'scheduleentrys')


def get_all_schedule_entries():
    return get_all_objects(ScheduleEntry, 'scheduleentrys')


def add_ride_passenger(ride_id, user_id, status="Ready", joined_at=None):
    ride = get_ride(ride_id)
    if ride is None:
        raise ValueError("Ride not found")
    if user_id == ride.user_id:
        raise ValueError("Driver cannot be a passenger in their own ride")
    if ride.current_riders >= ride.max_riders:
        raise ValueError("Ride is full")
    # Check if user is already a passenger
    existing = db.collection('ridepassengers').document(
        f"{ride_id}_{user_id}").get()
    if existing.exists:
        raise ValueError("User is already a passenger in this ride")
    passenger = RidePassenger(ride_id, user_id, status, joined_at)
    save_object(passenger, 'ridepassengers')
    ride.current_riders += 1
    save_ride(ride)
    return passenger


def remove_ride_passenger(ride_id, user_id):
    ride = get_ride(ride_id)
    if ride is None:
        raise ValueError("Ride not found")
    if user_id == ride.user_id:
        raise ValueError(
            "Driver cannot be removed as a passenger (driver is not a passenger)")
    passenger_id = f"{ride_id}_{user_id}"
    doc = db.collection('ridepassengers').document(passenger_id).get()
    if not doc.exists:
        raise ValueError("Passenger not found in this ride")
    db.collection('ridepassengers').document(passenger_id).delete()
    ride.current_riders = max(0, ride.current_riders - 1)
    save_ride(ride)


def get_passengers_for_ride(ride_id):
    docs = db.collection('ridepassengers').where(
        'ride_id', '==', ride_id).stream()
    return [RidePassenger.from_dict(doc.to_dict()) for doc in docs]


def get_rides_for_user(user_id):
    docs = db.collection('ridepassengers').where(
        'user_id', '==', user_id).stream()
    return [RidePassenger.from_dict(doc.to_dict()) for doc in docs]


def get_schedule_for_user(user_id):
    docs = db.collection('scheduleentrys').where(
        'user_id', '==', user_id).stream()
    return [ScheduleEntry.from_dict(doc.to_dict()) for doc in docs]


def delete_all_collections():
    """Delete all documents in all main collections for cleanup/testing."""
    collections = ['users', 'rides',
                   'scheduleentrys', 'ridepassengers', "routes"]
    for collection_name in collections:
        docs = db.collection(collection_name).stream()
        for doc in docs:
            db.collection(collection_name).document(doc.id).delete()
