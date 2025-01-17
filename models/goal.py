class GoalNode:
    def __init__(self, title: str, description: str = "", parent=None, tag: str = ""):
        self.title = title
        self.description = description
        self.children = []
        self.parent = parent
        self.task = (0, 0, 0)
        self.tag=tag

    def add_child(self, child_node):
        self.children.append(child_node)
        child_node.parent = self

    def is_leaf(self):
        """Leaf 노드 여부 확인."""
        return len(self.children) == 0