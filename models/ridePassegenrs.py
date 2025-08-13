import uuid


class RidePassenger:
    def __init__(self, ride_id, user_id, status="Ready", joined_at=None, id=None, save_object=False):
        self.id = id if id is not None else f"{ride_id}_{user_id}"
        self.ride_id = ride_id
        self.user_id = user_id
        self.status = status
        self.joined_at = joined_at
        if save_object:
            from repositories.base_repository import save_object
            save_object(self)

    def to_dict(self):
        return {
            'id': self.id,
            'ride_id': self.ride_id,
            'user_id': self.user_id,
            'status': self.status,
            'joined_at': self.joined_at
        }

    @staticmethod
    def from_dict(data):
        return RidePassenger(
            ride_id=data.get('ride_id'),
            user_id=data.get('user_id'),
            status=data.get('status'),
            joined_at=data.get('joined_at'),
            id=data.get('id')
        )
