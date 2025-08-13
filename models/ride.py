import uuid
from typing import List


class Ride:
    def __init__(self, user_id: str, max_riders: int, id: str = None, save_object=False):
        self.id: str = id if id is not None else str(uuid.uuid4())
        self.user_id: str = user_id  # driver's id
        self.max_riders = max_riders
        self.current_riders: int = 0
        self.actual_start_time = None
        self.actual_arrival_time = None
        self.max_detour = None
        self.actual_detour = None
        self.route: List[float] = None
        if save_object:
            from repositories.base_repository import save_object
            save_object(self)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'max_riders': self.max_riders,
            'current_riders': self.current_riders,
            'actual_start_time': self.actual_start_time,
            'actual_arrival_time': self.actual_arrival_time,
            'max_detour': self.max_detour,
            'actual_detour': self.actual_detour,
            'route': self.route
        }

    @staticmethod
    def from_dict(data):
        ride = Ride(
            user_id=data.get('user_id'),
            max_riders=data.get('max_riders'),
            id=data.get('id')
        )
        ride.current_riders = data.get('current_riders')
        ride.actual_start_time = data.get('actual_start_time')
        ride.actual_arrival_time = data.get('actual_arrival_time')
        ride.max_detour = data.get('max_detour')
        ride.actual_detour = data.get('actual_detour')
        ride.route = data.get('route')
        return ride
