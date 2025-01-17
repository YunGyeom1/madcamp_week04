from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItemGroup, QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QPen, QPainter
import sys
from models.goal import GoalNode

def get_nodes(root):
    res = {root.height: [root]}
    for child in root.children:
        child_nodes = get_nodes(child)
        for key, nodes in child_nodes.items():
            if key not in res:
                res[key] = []
            res[key].extend(nodes)
    return res

def vis_node(node):
    ellipse = QGraphicsEllipseItem(0, 0, 50, 50)
    ellipse.setBrush(QBrush(Qt.yellow))
    ellipse.setPen(QPen(Qt.black))

    node_label = f"{node.title}"
    text = QGraphicsTextItem(node_label)
    text.setDefaultTextColor(Qt.black)
    text.setPos(10, 10)  # 텍스트를 약간 안쪽으로 이동

    group = QGraphicsItemGroup()
    group.addToGroup(ellipse)
    group.addToGroup(text)
    return group

def add_edge(scene, parent_pos, child_pos):
    parent = QPointF(parent_pos.x() + 50, parent_pos.y() + 25)
    child = QPointF(child_pos.x(), child_pos.y() + 25)

    if parent.y() == child.y():
        line = QGraphicsLineItem(parent.x(), parent.y(), child.x(), child.y())
        line.setPen(QPen(Qt.black, 2))
        scene.addItem(line)
        return
    
    if parent.x() == child.x():
        line = QGraphicsLineItem(parent.x(), parent.y(), child.x(), child.y())
        line.setPen(QPen(Qt.black, 2))
        scene.addItem(line)
        return
    
    # 수평, 수직, 수평 선분의 중간 좌표 계산
    mid = QPointF(parent_pos.x()+75, parent_pos.y() + 25)
    # 첫 번째 수평 직선
    line1 = QGraphicsLineItem(mid.x(), mid.y(), mid.x(), child.y())
    line1.setPen(QPen(Qt.black, 2))
    scene.addItem(line1)

    # 수직 직선
    line2 = QGraphicsLineItem(mid.x(), child.y(), child.x(), child.y())
    line2.setPen(QPen(Qt.black, 2))
    scene.addItem(line2)
    return

def place_node(scene, node, x, y):
    vnode = vis_node(node)
    vnode.setPos(500-100*node.height, y)
    scene.addItem(vnode)
    dy = 0
    for ch in node.children:
        child_x = 500-100*ch.height
        child_y = y+dy
        place_node(scene, ch, 500-100*ch.height, child_y)
        add_edge(scene, vnode.pos(), QPointF(child_x, child_y))
        dy += ch.width * 100
    
def visualize_tree(root):
    # 루트 노드부터 배치 시작
    """PyQt로 트리 시각화."""
    app = QApplication(sys.argv)

    # 그래픽 장면 및 뷰 설정
    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.Antialiasing)

    place_node(scene, root, 100, 100)

    # 뷰 설정
    view.setScene(scene)
    view.setWindowTitle("GoalNode Tree Visualization")
    view.setGeometry(100, 100, 800, 600)
    view.show()

    sys.exit(app.exec_())

# GoalNode 생성 및 테스트
def create_sample_tree():
    root = GoalNode("Root")
    child1 = GoalNode("C1")
    child2 = GoalNode("C2")
    child3 = GoalNode("C3")
    child4 = GoalNode("C4")
    child5 = GoalNode("C5")
    child6 = GoalNode("C6")
    child7 = GoalNode("C7")

    root.add_child(child1)
    root.add_child(child2)
    child1.add_child(child3)
    child1.add_child(child4)
    child2.add_child(child5)
    child2.add_child(child6)
    child4.add_child(child7)

    return root
if __name__ == "__main__":
    root_node = create_sample_tree()
    visualize_tree(root_node)