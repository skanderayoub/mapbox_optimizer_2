import uuid
from typing import List, Literal, Optional
from datetime import datetime, time
from models.user import User
from models.ride import Ride


class ScheduleEntry:
    def __init__(self, user_id: str, date: datetime, start_time: time, arrival_time: time, max_delay: int, role: Literal["driver", "rider"], id: str = None, save_object: bool = False, direction: Literal["work", "home"] = "work"):
        self.id: str = id if id is not None else str(uuid.uuid4())
        self.user_id: str = user_id
        self.date: datetime = date
        self.start_time: time = start_time
        self.arrival_time: time = arrival_time
        self.max_delay: int = max_delay  # in minutes
        self.role: Literal["driver", "rider"] = role
        self.direction = direction
        if self.direction == "work":
            import firebase
            user = firebase.get_user(user_id=self.user_id)
            self.pickup: List[float] = user.home[0]
            self.dropoff: List[float] = user.work[0]
        else:
            import firebase
            user = firebase.get_user(user_id=self.user_id)
            self.pickup: List[float] = user.work[0]
            self.dropoff: List[float] = user.home[0]
        if role == "driver":
            ride = Ride(user_id=user_id, max_riders=4, save_object=save_object)
            self.ride_id: Optional[str] = ride.id
            self.ride_obj = ride
        else:
            self.ride_id: Optional[str] = None
            self.ride_obj = None
        if save_object:
            import firebase
            firebase.save_object(self)

    def to_dict(self):
        """Serialize the ScheduleEntry object to a dictionary for Firestore."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'arrival_time': self.arrival_time.isoformat() if self.arrival_time else None,
            'max_delay': self.max_delay,
            'role': self.role,
            'direction': self.direction,
            'pickup': self.pickup,
            'dropoff': self.dropoff,
            'ride_id': self.ride_id
        }

    @staticmethod
    def from_dict(data):
        from datetime import datetime, time
        entry = ScheduleEntry(
            user_id=data.get('user_id'),
            date=datetime.fromisoformat(
                data.get('date')) if data.get('date') else None,
            start_time=time.fromisoformat(
                data.get('start_time')) if data.get('start_time') else None,
            arrival_time=time.fromisoformat(
                data.get('arrival_time')) if data.get('arrival_time') else None,
            max_delay=data.get('max_delay'),
            role=data.get('role'),
            id=data.get('id')
        )
        entry.direction = data.get('direction')
        entry.pickup = data.get('pickup')
        entry.dropoff = data.get('dropoff')
        entry.ride_id = data.get('ride_id')
        return entry
