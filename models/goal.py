class GoalNode:
    def __init__(self, title: str, description: str = "", parent=None, tag: str = "", location: str = ""):
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


    def add_child(self, child_node):
        """자식 노드 추가 및 부모 관계 설정."""
        self.children.append(child_node)
        child_node.parent = self
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