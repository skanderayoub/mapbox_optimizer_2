from typing import List
import uuid
from datetime import datetime


class Suggestion:
    def __init__(self, ride_id: str, user_id: str, score: float, id: str = str(uuid.uuid4())) -> None:
        self.id = id
        self.ride_id: str = ride_id
        self.user_id: str = user_id
        self.score: float = score
        self.detour_time: float = None
        self.pickup_location: List[float] = None
        self.dropoff: List[float] = None
        self.pickup_time: datetime = None
