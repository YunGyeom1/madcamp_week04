from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter

class TreeRenderer:
    def __init__(self, root):
        self.root = root
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setWindowTitle("Interactive Tree Visualization")
        self.view.setGeometry(100, 100, 800, 600)

    def render_tree(self):
        self.scene.clear()
        self._place_node(self.root, 100, 100)

    def _place_node(self, node, x, y):
        vnode = InteractiveNode(node, self.render_tree)
        vnode.setPos(x, y)
        self.scene.addItem(vnode)

        dy = 0
        for ch in node.children:
            child_x = x + 100
            child_y = y + dy
            self._place_node(ch, child_x, child_y)
            self._add_edge((x + 25, y + 25), (child_x, child_y + 25))
            dy += 100

    def _add_edge(self, start, end):
        from PyQt5.QtWidgets import QGraphicsLineItem
        from PyQt5.QtGui import QPen

        line = QGraphicsLineItem(start[0], start[1], end[0], end[1])
        line.setPen(QPen(Qt.black, 2))
        self.scene.addItem(line)

    def show(self):
        self.render_tree()
        self.view.show()