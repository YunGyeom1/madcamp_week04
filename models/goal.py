from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()

connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)
db = client["W4_Calendar"]
collection = db["Test"]


class GoalNode:
    def __init__(self, title: str, description: str = "", parent=None, tag: str = "", location: str = ""):
        self.id = ""
        self.children = []
        self.height = 0
        self.parent = parent
        self.title = title
        self.location = location
        self.description = description
        self.task = (0, 0, 0)
        self.tag=tag
        self.isOpen=True
        self.width = 1
        goal_schema = {
            "title": self.title,
            "description": self.description,
            "children": [],  # 하위 목표의 ID 리스트
            "parent": None,
            "task": [0, 0, 0],
            "tag": self.tag,
            "height": self.height,
            "width": self.width,
            "isOpen": self.isOpen,
            "location": self.location,
            "due_date": "2025-01-30T10:00:00Z",  # Leaf Node만 해당
        }
        result = collection.insert_one(goal_schema)
        self.id = result.inserted_id


    def add_child(self, child_node):
        """자식 노드 추가 및 부모 관계 설정."""
        self.children.append(child_node)
        child_node.parent = self
        parent_id = self.id
        child_id = child_node.id

        collection.update_one({"_id": parent_id}, {"$push": {"children": child_id}})
        result = collection.update_one({"_id": child_id}, {"$set": {"parent": parent_id}})
        print(f"Update result for parent: {result.modified_count}")
        self.update_height()


    def update_height(self):
        """부모 및 조상 노드의 높이와 너비를 갱신."""
        self.height = max((child.height + 1 for child in self.children), default=1)
        self.width = sum(child.width for child in self.children) or 1
        if self.parent:
            self.parent.update_height()

    def is_leaf(self):
        """리프 노드 여부 확인."""
        return len(self.children) == 0