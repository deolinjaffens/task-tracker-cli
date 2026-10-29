from datetime import datetime, timezone

from repositories.task_repository import TaskRepository
from enums.task_enum import TaskStatus


class TaskService:
    def __init__(self):
        self.task_repository = TaskRepository()

    def get_all_tasks(self):
        return self.task_repository.get_all_tasks()

    def get_task_by_id(self, task_id):
        return self.task_repository.get_task_by_id(task_id)

    def add_task(self, task_data):
        description = self._validate_description(task_data.get("description"))
        now = self._timestamp()
        return self.task_repository.add_task({
            "description": description,
            "status": TaskStatus.TODO.value,
            "createdAt": now,
            "updatedAt": now,
        })

    def update_task(self, task_id, updated_data):
        description = self._validate_description(updated_data.get("description"))
        return self.task_repository.update_task(task_id, {
            "description": description,
            "updatedAt": self._timestamp(),
        })

    def delete_task(self, task_id):
        return self.task_repository.delete_task(task_id)

    def get_tasks_by_status(self, status):
        return self.task_repository.get_tasks_by_status(
            status.value if isinstance(status, TaskStatus) else status
        )

    def _change_task_status(self, task_id, new_status):
        task = self.get_task_by_id(task_id)
        if task:
            return self.task_repository.update_task(task_id, {
                "status": new_status.value,
                "updatedAt": self._timestamp(),
            })
        return None

    def mark_task_in_progress(self, task_id):
        return self._change_task_status(task_id, TaskStatus.IN_PROGRESS)

    def mark_task_done(self, task_id):
        return self._change_task_status(task_id, TaskStatus.DONE)

    @staticmethod
    def _validate_description(description):
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Task description must not be empty.")
        return description.strip()

    @staticmethod
    def _timestamp():
        return datetime.now(timezone.utc).isoformat()