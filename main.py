from models.user import User
from models.ride import Ride
from models.scheduleEntry import ScheduleEntry
from models.ridePassegenrs import RidePassenger
import firebase
from datetime import datetime, time

user_ids = []
ride_ids = []
schedule_entry_ids = []
ride_passenger_ids = []

print("--- Testing User ---")
# Step 1: Create and save all users
for i in range(2):
    user = User([1.1 + i, 1.1 + i], [1.2 + i, 1.2 + i])
    firebase.save_user(user)
    user_ids.append(user.id)
    print(f"Saved user with id: {user.id} to Firebase.")

# Step 2: Display the size of the users collection
all_users = firebase.get_all_users()
print(f"Number of users in Firebase: {len(all_users)}")

# Step 3: Retrieve and print each user
for user_id in user_ids:
    retrieved_user = firebase.get_user(user_id)
    print(
        f"Retrieved user from Firebase: {retrieved_user.to_dict() if retrieved_user else 'User not found'}\n")

print("--- Testing Ride ---")
# Create and save rides
for i in range(2):
    ride = Ride(user_id=user_ids[i], max_riders=4)
    firebase.save_ride(ride)
    ride_ids.append(ride.id)
    print(f"Saved ride with id: {ride.id} to Firebase.")

all_rides = firebase.get_all_rides()
print(f"Number of rides in Firebase: {len(all_rides)}")
for ride_id in ride_ids:
    retrieved_ride = firebase.get_ride(ride_id)
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
    firebase.save_schedule_entry(entry)
    schedule_entry_ids.append(entry.id)
    print(f"Saved schedule entry with id: {entry.id} to Firebase.")

all_entries = firebase.get_all_schedule_entries()
print(f"Number of schedule entries in Firebase: {len(all_entries)}")
for entry_id in schedule_entry_ids:
    retrieved_entry = firebase.get_schedule_entry(entry_id)
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
    firebase.save_ride_passenger(passenger)
    ride_passenger_ids.append(passenger.id)
    print(f"Saved ride passenger with id: {passenger.id} to Firebase.")

all_passengers = firebase.get_all_ride_passengers()
print(f"Number of ride passengers in Firebase: {len(all_passengers)}")
for passenger_id in ride_passenger_ids:
    retrieved_passenger = firebase.get_ride_passenger(passenger_id)
    print(
        f"Retrieved ride passenger from Firebase: {retrieved_passenger.to_dict() if retrieved_passenger else 'Passenger not found'}\n")
