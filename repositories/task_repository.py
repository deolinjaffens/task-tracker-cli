from config.data_config import (
    delete_data,
    get_all_data,
    get_data,
    store_data,
    update_data,
)

class TaskRepository:
    """Repository for managing task data."""
    def __init__(self):
        self.type = "tasks"
    
    def get_all_tasks(self):
        """Retrieve all tasks."""
        return get_all_data(self.type)

    def get_task_by_id(self, task_id):
        """Retrieve a task by its ID."""
        tasks = get_data(self.type, id=task_id)
        return tasks[0] if tasks else None

    def add_task(self, task_data):
        """Add a new task."""
        task_id = store_data(self.type, task_data)
        return self.get_task_by_id(task_id)

    def update_task(self, task_id, updated_data):
        """Update an existing task."""
        task = self.get_task_by_id(task_id)
        if task is None:
            return None
        task.update(updated_data)
        task["id"] = task_id
        return update_data(self.type, task)

    def delete_task(self, task_id):
        """Delete a task by its ID."""
        return delete_data(self.type, task_id)

    def get_tasks_by_status(self, status):
        """Retrieve tasks filtered by their status."""
        data = get_data(self.type, status=status)
        return data