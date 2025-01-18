import sys 
from PyQt5.QtWidgets import QApplication, QMainWindow
from models.goal import MakeNode, add_child, update_height
import os
from dotenv import load_dotenv
load_dotenv()
from bson.objectid import ObjectId

rootnode_id=os.getenv("ROOT_NODE_ID")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

def main():
    app=QApplication(sys.argv)
    window=MainWindow()
    window.show()
    MakeNode(title="test1", parent=ObjectId(rootnode_id))
    sys.exit(app.exec_())
    



if __name__ == "__main__":
    main()