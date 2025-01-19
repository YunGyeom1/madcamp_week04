from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
import configparser
import copy
from db.db import get_collection
from models.tags import sync_tags_with_goals
collection = get_collection()


GOAL_SCHEMA_TEMPLATE = {
    "parent": None,
    "children": [],
    
    "title": "Untitled Node",
    "description": "",
    "isOpen": True,
    "due_date": None,
    "location": "",
    "tag": [],

    "height": 0,
    "width": 1,
    "task": [0, 0, 0],
    "date": None,
    "start_time": None,
    "end_time": None,
}


def MakeNode(title="Untitled Node", parent=None, description=""):
    goal_schema = copy.deepcopy(GOAL_SCHEMA_TEMPLATE)  # 원본 수정 방지
    goal_schema.update({
        "title": title,
        "description": description,
        "parent": parent,
        "tag": ["all"],  # 항상 'all' 태그를 포함
    })

    result = collection.insert_one(goal_schema)

    if parent:
        collection.update_one({"_id": parent}, {"$push": {"children": result.inserted_id}})
        update_height(parent)
    sync_tags_with_goals()
    return result.inserted_id

def set_time(node_id, start_time=None, end_time=None):
    update_data = {"width":1, "height":0}
    if start_time:
        update_data["start_time"] = start_time
    if end_time:
        update_data["end_time"] = end_time

    collection.update_one({"_id": node_id}, {"$set": update_data})
    return node_id


def add_leaf(node_id, date=None):
    """새로운 leaf 노드를 생성하고 MongoDB에 저장"""
    data = collection.find_one({"_id": node_id})
    # 기존 노드 데이터 복사 및 불필요한 필드 제거
    data.pop('_id')
    data.pop('children', None)
    data["parent"] = node_id
    data["date"] = date  # 전달받은 날짜 추가
    data["title"] = f"Leaf of {data.get('title', 'Untitled')}"

    # 새 노드 MongoDB에 삽입
    leaf = collection.insert_one(data)

    # 부모 노드에 새 노드 추가
    collection.update_one({"_id": node_id}, {"$push": {"children": leaf.inserted_id}})
    
    return leaf.inserted_id


def update_height(node):
    data = collection.find_one({"_id": node})
    if data.get("start_time") or data.get("end_time"):
        return
   
    height = 1
    width = 0
    
    tag_collection = get_collection("Tags")
    selected_tags = [tag["name"] for tag in tag_collection.find({"selected": True})]
    restricted_tags = [tag["name"] for tag in tag_collection.find({"restricted": True})]

    
    for childid in data["children"]:
        child = collection.find_one({"_id": childid})

        if not child:
            continue

        # 1. 선택된 태그 중 하나라도 포함되지 않으면 제외
        if not any(tag in selected_tags for tag in child["tag"]):
            continue

        # 2. 금지된 태그가 포함된 경우 모든 태그가 선택되었는지 확인
        restricted_in_child = [tag for tag in child["tag"] if tag in restricted_tags]
        if restricted_in_child and not all(tag in selected_tags for tag in restricted_in_child):
            continue

        height = max(height, child["height"] + 1)
        width += child["width"]

    # 데이터베이스에 업데이트
    collection.update_one(
        {"_id": node},
        {"$set": {"height": height, "width": max(width, 1)}}
    )

    # 부모 노드 갱신 (재귀적으로 호출)
    if data["parent"] is not None:
        update_height(data["parent"])

    

def is_leaf(node):
    """리프 노드 여부 확인."""
    data = collection.find_one({"_id": node})
    return len(data["children"]) == 0

def update_tags(node_id, add_tags=[], remove_tags=[]):

    # 노드 가져오기
    node = collection.find_one({"_id": node_id})
    if not node:
        raise ValueError(f"Node with ID {node_id} does not exist.")

    # 기존 태그 가져오기
    current_tags = set(node.get("tag", []))

    # 태그 업데이트
    updated_tags = current_tags.union(set(add_tags)).difference(set(remove_tags))

    # 데이터베이스 업데이트
    collection.update_one(
        {"_id": node_id},
        {"$set": {"tag": list(updated_tags)}}
    )

    # 태그 컬렉션 동기화
    sync_tags_with_goals()

    print(f"Updated tags for node {node_id}: {list(updated_tags)}")
    return list(updated_tags)