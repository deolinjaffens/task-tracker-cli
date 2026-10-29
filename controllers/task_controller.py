from enums.task_enum import TaskStatus
from services.task_service import TaskService


class TaskController:
    def __init__(self):
        self.task_service = TaskService()

    def add_task(self, description):
        task = self.task_service.add_task({"description": description})
        print(f"Added task {task['id']}: {task['description']}")

    def update_task(self, task_id, description):
        task = self.task_service.update_task(task_id, {"description": description})
        if task is None:
            raise ValueError(f"No task found with id {task_id}.")
        print(f"Updated task {task_id}.")

    def delete_task(self, task_id):
        if not self.task_service.delete_task(task_id):
            raise ValueError(f"No task found with id {task_id}.")
        print(f"Deleted task {task_id}.")

    def mark_task_in_progress(self, task_id):
        self._mark_task(task_id, self.task_service.mark_task_in_progress)

    def mark_task_done(self, task_id):
        self._mark_task(task_id, self.task_service.mark_task_done)

    def list_tasks(self, status="all"):
        if status == "all":
            tasks = self.task_service.get_all_tasks()
        elif status == "not-done":
            tasks = [
                task
                for task in self.task_service.get_all_tasks()
                if task.get("status") != TaskStatus.DONE.value
            ]
        else:
            status_value = {
                "done": TaskStatus.DONE,
                "in-progress": TaskStatus.IN_PROGRESS,
            }[status]
            tasks = self.task_service.get_tasks_by_status(status_value)

        if not tasks:
            print("No tasks found.")
            return

        print("ID  STATUS       DESCRIPTION")
        for task in tasks:
            print(f"{task['id']:<3} {task['status']:<12} {task['description']}")

    def _mark_task(self, task_id, mark_method):
        task = mark_method(task_id)
        if task is None:
            raise ValueError(f"No task found with id {task_id}.")
        print(f"Marked task {task_id} as {task['status']}.")