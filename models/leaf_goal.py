from datetime import datetime
from goal import GoalNode

class LeafNode(GoalNode):
    def __init__(self, title: str, description: str = "", due_date: datetime = None):
        super().__init__(title, description)
        self.due_date = due_date
        self.isDone=False
