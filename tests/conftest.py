import types
import sys
import pytest


class FakeDoc:
    def __init__(self, data):
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return self._data


class FakeDocumentRef:
    def __init__(self, store: dict, collection_name: str, doc_id: str):
        self._store = store
        self._collection_name = collection_name
        self.id = doc_id

    def set(self, data: dict):
        self._store.setdefault(self._collection_name, {})[self.id] = dict(data)

    def get(self):
        data = self._store.get(self._collection_name, {}).get(self.id)
        return FakeDoc(data)

    def delete(self):
        if self._collection_name in self._store:
            self._store[self._collection_name].pop(self.id, None)


class FakeQuery:
    def __init__(self, docs: list):
        self._docs = docs

    def stream(self):
        for doc in self._docs:
            yield FakeDoc(doc)


class FakeCollectionRef:
    def __init__(self, store: dict, collection_name: str):
        self._store = store
        self._collection_name = collection_name

    def document(self, doc_id: str):
        return FakeDocumentRef(self._store, self._collection_name, doc_id)

    def stream(self):
        for _, data in self._store.get(self._collection_name, {}).items():
            yield FakeDoc(data)

    def where(self, field: str, op: str, value):
        if op != "==":
            raise NotImplementedError("Only == is supported in FakeCollectionRef.where")
        docs = []
        for _, data in self._store.get(self._collection_name, {}).items():
            if data.get(field) == value:
                docs.append(data)
        return FakeQuery(docs)


class FakeFirestore:
    def __init__(self):
        self._store = {}

    def collection(self, name: str):
        return FakeCollectionRef(self._store, name)


@pytest.fixture()
def fake_db():
    return FakeFirestore()


@pytest.fixture()
def patch_repositories_db(fake_db, monkeypatch):
    # Patch modules that directly import db
    monkeypatch.setattr("repositories.base_repository.db", fake_db, raising=False)
    monkeypatch.setattr("repositories.rides_repository.db", fake_db, raising=False)
    return fake_db


@pytest.fixture()
def app_with_fake_db(fake_db, monkeypatch, patch_repositories_db):
    # Provide a fake core.firebase before importing app and repositories
    fake_core_firebase = types.ModuleType("core.firebase")
    fake_core_firebase.db = fake_db
    sys.modules["core.firebase"] = fake_core_firebase

    from core.api import app
    return app


