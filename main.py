from models.user import User
from models.ride import Ride
from models.scheduleEntry import ScheduleEntry
from models.ridePassegenrs import RidePassenger
from repositories.users_repository import save_user, get_all_users, get_user
from repositories.rides_repository import save_ride, get_all_rides, get_ride, add_ride_passenger
from repositories.schedule_entries_repository import save_schedule_entry, get_all_schedule_entries, get_schedule_entry
from repositories.base_repository import delete_all_collections
from core.firebase import db
from datetime import datetime, time

user_ids = []
ride_ids = []
schedule_entry_ids = []
ride_passenger_ids = []

print("--- Testing User ---")
# Step 1: Create and save all users
for i in range(2):
    user = User([1.1 + i, 1.1 + i], [1.2 + i, 1.2 + i])
    save_user(user)
    user_ids.append(user.id)
    print(f"Saved user with id: {user.id} to Firebase.")

# Step 2: Display the size of the users collection
all_users = get_all_users()
print(f"Number of users in Firebase: {len(all_users)}")

# Step 3: Retrieve and print each user
for user_id in user_ids:
    retrieved_user = get_user(user_id)
    print(
        f"Retrieved user from Firebase: {retrieved_user.to_dict() if retrieved_user else 'User not found'}\n")

print("--- Testing Ride ---")
# Create and save rides
for i in range(2):
    ride = Ride(user_id=user_ids[i], max_riders=4)
    save_ride(ride)
    ride_ids.append(ride.id)
    print(f"Saved ride with id: {ride.id} to Firebase.")

all_rides = get_all_rides()
print(f"Number of rides in Firebase: {len(all_rides)}")
for ride_id in ride_ids:
    retrieved_ride = get_ride(ride_id)
    print(
        f"Retrieved ride from Firebase: {retrieved_ride.to_dict() if retrieved_ride else 'Ride not found'}\n")

print("--- Testing ScheduleEntry ---")
# Create and save schedule entries
for i in range(2):
    entry = ScheduleEntry(
        user_id=user_ids[i],
        date=datetime.now(),
        start_time=time(8 + i, 0),
        arrival_time=time(9 + i, 0),
        max_delay=15,
        role="driver" if i % 2 == 0 else "rider"
    )
    save_schedule_entry(entry)
    schedule_entry_ids.append(entry.id)
    print(f"Saved schedule entry with id: {entry.id} to Firebase.")

all_entries = get_all_schedule_entries()
print(f"Number of schedule entries in Firebase: {len(all_entries)}")
for entry_id in schedule_entry_ids:
    retrieved_entry = get_schedule_entry(entry_id)
    print(
        f"Retrieved schedule entry from Firebase: {retrieved_entry.to_dict() if retrieved_entry else 'Entry not found'}\n")

print("--- Testing RidePassenger ---")
# Create and save ride passengers
for i in range(2):
    passenger = RidePassenger(
        id=None,
        ride_id=ride_ids[i],
        user_id=user_ids[i],
        status="confirmed",
        joined_at=datetime.now().isoformat()
    )
    add_ride_passenger(passenger.ride_id, passenger.user_id, passenger.status, passenger.joined_at)
    ride_passenger_ids.append(passenger.id)
    print(f"Saved ride passenger with id: {passenger.id} to Firebase.")

from repositories.rides_repository import get_passengers_for_ride, get_rides_for_user
all_passengers = get_passengers_for_ride(ride_ids[0])
print(f"Number of ride passengers in Firebase: {len(all_passengers)}")
for passenger_id in ride_passenger_ids:
    # Example retrievals using repository
    rides_for_user = get_rides_for_user(user_ids[0])
    retrieved_passenger = rides_for_user[0] if rides_for_user else None
    print(
        f"Retrieved ride passenger from Firebase: {retrieved_passenger.to_dict() if retrieved_passenger else 'Passenger not found'}\n")
