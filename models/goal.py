from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
import configparser
import copy
from db.db import get_collection
collection = get_collection()


GOAL_SCHEMA_TEMPLATE = {
    "parent": None,
    "children": [],
    
    "title": "Untitled Node",
    "description": "",
    "due_date": [None, None],
    "location": "",
    "tag": [],
    "isLeaf": False,
    "repeat": [0, 0],

    "height": 0,
    "width": 1,
    "task": [0, 0, 0],
    "date": None,
    "start_time": None,
    "end_time": None,
    "color": None,
}

def MakeNode(title="Untitled Node", parent=None, description=""):
    goal_schema = copy.deepcopy(GOAL_SCHEMA_TEMPLATE)  # 원본 수정 방지
    goal_schema.update({
        "title": title,
        "description": description,
        "parent": parent,
        "tag": ["all"],  # 항상 'all' 태그를 포함
    })
    if not goal_schema["color"]:
        goal_schema["color"]="#FFFFFF"

    result = collection.insert_one(goal_schema)
    print(title, parent, description)
    if parent:
        collection.update_one({"_id": parent}, {"$push": {"children": result.inserted_id}})
        update_height(parent)
        parent_node=collection.find_one({"_id": parent})
        collection.update_one({"_id": result.inserted_id}, {"$set": {"color": parent_node["color"]}})
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
    data["title"] = f"{data.get('title', 'Untitled')}"

    # 새 노드 MongoDB에 삽입
    leaf = collection.insert_one(data)

    # 부모 노드에 새 노드 추가
    collection.update_one({"_id": node_id}, {"$push": {"children": leaf.inserted_id}})
    
    return leaf.inserted_id

def update_height(node_id):
    data = collection.find_one({"_id": node_id})
    #print(node_id, data)
    if data.get("date"):
        return
   
    height = 1
    width = 0
    
    tag_collection = get_collection("Tags")
    selected_tags = [tag["name"] for tag in tag_collection.find({"selected": True})]
    restricted_tags = ["deleted"]

    
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
        {"_id": node_id},
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


    print(f"Updated tags for node {node_id}: {list(updated_tags)}")
    return list(updated_tags)

def set_deleted_true(node_id):
    if not node_id: return
    """
    주어진 노드와 그 자식 노드들에 'deleted' 태그를 추가합니다.
    """
    # 해당 노드 찾기
    node = collection.find_one({"_id": node_id})
    if not node:
        raise ValueError(f"Node with ID {node_id} does not exist.")
    
    # 현재 태그에 'deleted' 추가
    updated_tags = set(node.get("tag", []))
    updated_tags.add("deleted")

    # 노드 업데이트
    collection.update_one(
        {"_id": node_id},
        {"$set": {"tag": list(updated_tags)}}
    )
    
    print(f"Added 'deleted' tag to node {node_id}.")
    
    # 자식 노드들에 대해서도 재귀적으로 'deleted' 태그 추가
    if "children" in node:
        for child_id in node["children"]:
            set_deleted_true(child_id)
    update_height(node_id)
    
def set_child_color(node_id, color):
    """
    주어진 노드와 그 자식 노드들에 색을 추가합니다.
    """
    # 해당 노드 찾기
    node = collection.find_one({"_id": node_id})
    if not node:
        raise ValueError(f"Node with ID {node_id} does not exist.")

    # 노드 업데이트
    collection.update_one(
        {"_id": node_id},
        {"$set": {"color": color}}
    )
    
    if "children" in node:
        for child_id in node["children"]:
            set_child_color(child_id, color)

def update_parent_task(node_id):
    node = collection.find_one({"_id": node_id})
    if not node or not node["children"]:
        return

    task_sum = [0, 0, 0]

    for child_id in node["children"]:
        child = collection.find_one({"_id": child_id})
        if not child:
            continue
        task_sum = [task_sum[i] + child["task"][i] for i in range(3)]

    # 부모 노드 업데이트
    collection.update_one({"_id": node_id}, {"$set": {"task": task_sum}})

    # 상위 부모 노드도 재귀적으로 업데이트
    if node["parent"]:
        update_parent_task(node["parent"])

def duplicate_node(parent_node_id, obj_node_id):
    tag_collection = get_collection("Tags")

    # 선택된 태그 가져오기
    selected_tags = [tag["name"] for tag in tag_collection.find({"selected": True})]

    def copy_subtree(src_node_id, new_parent_id):
        """재귀적으로 하위 트리를 복사하는 함수"""
        src_node = collection.find_one({"_id": src_node_id})
        if not src_node:
            return None

        # 태그 필터링: 선택된 태그에 포함되지 않으면 복사하지 않음
        if not any(tag in selected_tags for tag in src_node.get("tag", [])):
            return None

        # "deleted" 태그가 있는 경우 selected 태그에 포함되어 있어야 복사
        if "deleted" in src_node["tag"] and "deleted" not in selected_tags:
            return None

        # 새 노드 생성 (불필요한 필드 제거)
        new_node_data = copy.deepcopy(src_node)
        new_node_data.pop('_id')
        new_node_data["parent"] = new_parent_id  # 부모 ID 업데이트
        new_node_data["children"] = []  # 새 노드의 자식 목록 초기화

        new_node_id = collection.insert_one(new_node_data).inserted_id

        # 부모 노드의 children 리스트에 추가
        collection.update_one({"_id": new_parent_id}, {"$push": {"children": new_node_id}})

        # 자식 노드 복사
        for child_id in src_node.get("children", []):
            copy_subtree(child_id, new_node_id)

        return new_node_id

    # 최상위 노드(obj_node_id)를 parent_node_id 아래로 복사
    copied_root_id = copy_subtree(obj_node_id, parent_node_id)

    # 부모 노드의 높이 갱신
    if copied_root_id:
        update_height(parent_node_id)
    
    return copied_root_id