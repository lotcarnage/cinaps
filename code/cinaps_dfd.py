from flask_sqlalchemy import SQLAlchemy
from models import Member, Fiscal, Project, Task, Deliverable, Work, TaskInputDeliverable
import datetime


class DfdDeliverable:
    def __init__(self, deliverable: Deliverable) -> None:
        self.id = deliverable.id
        self.label = deliverable.label
        self.parent_project_id = deliverable.parent_project_id
        self.production_task_id = deliverable.production_task_id
        return None


class DfdTask:
    def __init__(self, task: Task, task_input_deliverables: list[TaskInputDeliverable]) -> None:
        self.id = task.id
        self.parent_project_id = task.parent_project_id
        self.asigned_member_id = task.asigned_member_id
        self.subject = task.subject
        self.depend_deliverable_ids = [deliverable for deliverable in task_input_deliverables if deliverable.task_id == task.id]
        return None


class DfdTaskToDeliverable:
    def __init__(self, task_id: int, delivarable_id: int) -> None:
        self.task_id = task_id
        self.delivarable_id = delivarable_id
        return None


class DfdDeliverableToTask:
    def __init__(self, delivarable_id: int, task_id: int) -> None:
        self.delivarable_id = delivarable_id
        self.task_id = task_id
        return None
