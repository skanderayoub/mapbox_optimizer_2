from typing import Any, Dict, List, Optional, Type, TypeVar

from core.firebase import db

T = TypeVar("T")


def save_object(obj: Any, collection_name: Optional[str] = None) -> None:
    if collection_name is None:
        collection_name = obj.__class__.__name__.lower() + "s"
    db.collection(collection_name).document(obj.id).set(obj.to_dict())


def get_object(model_class: Type[T], object_id: str, collection_name: Optional[str] = None) -> Optional[T]:
    if collection_name is None:
        collection_name = model_class.__name__.lower() + "s"
    doc = db.collection(collection_name).document(object_id).get()
    if doc.exists:
        return model_class.from_dict(doc.to_dict())
    return None


def get_all_objects(model_class: Type[T], collection_name: Optional[str] = None) -> List[T]:
    if collection_name is None:
        collection_name = model_class.__name__.lower() + "s"
    docs = db.collection(collection_name).stream()
    return [model_class.from_dict(doc.to_dict()) for doc in docs]

def delete_all_collections() -> None:
    collections = ["users", "rides", "scheduleentrys", "ridepassengers", "routes"]
    for collection_name in collections:
        docs = db.collection(collection_name).stream()
        for doc in docs:
            db.collection(collection_name).document(doc.id).delete()
