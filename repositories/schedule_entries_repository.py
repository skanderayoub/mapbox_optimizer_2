from typing import List, Optional

from models.scheduleEntry import ScheduleEntry
from repositories.base_repository import save_object, get_object, get_all_objects
from core.firebase import db

COLLECTION_NAME = "scheduleentrys"

def save_schedule_entry(entry: ScheduleEntry) -> None:
    save_object(entry, "COLLECTION_NAME")


def get_schedule_entry(entry_id: str) -> Optional[ScheduleEntry]:
    return get_object(ScheduleEntry, entry_id, "COLLECTION_NAME")


def get_all_schedule_entries() -> List[ScheduleEntry]:
    return get_all_objects(ScheduleEntry, "COLLECTION_NAME")


def get_schedule_for_user(user_id: str) -> List[ScheduleEntry]:
    docs = db.collection("COLLECTION_NAME").where("user_id", "==", user_id).stream()
    return [ScheduleEntry.from_dict(doc.to_dict()) for doc in docs]


