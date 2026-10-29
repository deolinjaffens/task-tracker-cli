import json
from pathlib import Path


def _data_file(data_type: str) -> Path:
    return Path.cwd() / f"data/{data_type.lower()}.json"


def get_all_data(data_type: str) -> list:
    """Read records from a JSON file in the current working directory."""
    path = _data_file(data_type)
    if not path.exists():
        path.write_text("[]", encoding="utf-8")

    try:
        contents = path.read_text(encoding="utf-8")
        data = json.loads(contents) if contents.strip() else []
    except json.JSONDecodeError as error:
        raise ValueError(f"{path.name} contains invalid JSON: {error.msg}.") from error

    if not isinstance(data, list) or any(not isinstance(item, dict) for item in data):
        raise ValueError(f"{path.name} must contain a JSON array of task objects.")
    if data_type.lower() == "tasks":
        seen_ids = set()
        for index, task in enumerate(data, start=1):
            task_id = task.get("id")
            if not isinstance(task_id, int) or isinstance(task_id, bool) or task_id < 1:
                raise ValueError(f"Task record {index} in {path.name} has an invalid ID.")
            if task_id in seen_ids:
                raise ValueError(f"Task ID {task_id} appears more than once in {path.name}.")
            seen_ids.add(task_id)
            if not isinstance(task.get("description"), str) or not task["description"].strip():
                raise ValueError(f"Task record {index} in {path.name} has an invalid description.")
            if task.get("status") not in ("todo", "in-progress", "done"):
                raise ValueError(f"Task record {index} in {path.name} has an invalid status.")
            if not isinstance(task.get("createdAt"), str) or not isinstance(task.get("updatedAt"), str):
                raise ValueError(f"Task record {index} in {path.name} has invalid timestamps.")
    return data


def get_data(data_type: str, **kwargs) -> list:
    """Retrieve records matching all supplied field values."""
    return [
        item
        for item in get_all_data(data_type)
        if all(item.get(key) == value for key, value in kwargs.items())
    ]


def _write_data(data_type: str, records: list) -> None:
    _data_file(data_type).write_text(
        json.dumps(records, indent=4) + "\n",
        encoding="utf-8",
    )


def store_data(data_type: str, data: dict) -> int:
    """Append a record, assigning an ID not already present."""
    records = get_all_data(data_type)
    data["id"] = max(
        (item.get("id", 0) for item in records if isinstance(item.get("id"), int)),
        default=0,
    ) + 1
    records.append(data)
    _write_data(data_type, records)
    return data["id"]


def update_data(data_type: str, data: dict) -> dict:
    """Replace the record with the same ID."""
    records = get_all_data(data_type)
    for index, item in enumerate(records):
        if item.get("id") == data.get("id"):
            records[index] = data
            _write_data(data_type, records)
            return data
    raise ValueError(f"No task found with id {data.get('id')}.")


def delete_data(data_type: str, record_id: int) -> bool:
    """Delete a record and report whether it existed."""
    records = get_all_data(data_type)
    remaining = [item for item in records if item.get("id") != record_id]
    if len(remaining) == len(records):
        return False
    _write_data(data_type, remaining)
    return True
