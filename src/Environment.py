import time
import networkx as nx
import matplotlib.pyplot as plt
import Session
from Classes import *
import sys

from PyQt5.QtCore import Qt, QLineF, QPointF
from PyQt5.QtGui import QBrush, QPainter, QPen
from PyQt5.QtWidgets import (
    QPushButton,
    QToolBar,
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsLineItem,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QAction,
    QMainWindow
)

NODE_DIAMETER = 10
LINE_WIDTH = 8
DILATION_FACTOR_DATE = 500
DILATION_FACTOR_HEIGHT = 100
SESSION_NAME = "trial_session"

class EventNode(QGraphicsEllipseItem):
    def __init__(self, event, window):
        super().__init__(0, 0, NODE_DIAMETER, NODE_DIAMETER*(max(1,len(event.timelines))))
        tls = event.timelines
        if len(tls)>0:
            event.height = sum(tls)/len(tls)
        self.setPos(event.get_date()*DILATION_FACTOR_DATE, event.height*DILATION_FACTOR_HEIGHT)
        self.event = event
        self.setZValue(10)

        brush = QBrush(Qt.white)
        self.setBrush(brush)

        pen = QPen(Qt.black)
        pen.setWidth(1)
        self.setPen(pen)
        self.lines = []
        self.window = window
    
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            print("Left Button Clicked")
        elif QMouseEvent.button() == Qt.RightButton:
            print("Right Button Clicked")

    def delete_lines(self):
        for line in self.lines:
            self.window.scene.removeItem(line)
        self.lines = []

    def recompute_lines(self):
        self.lines = []
        for timeline in [Timeline.timeline_dict[tl_id] for tl_id in self.event.timelines]:
            for conn in self.window.timeline_connections[timeline.get_id()]:
                self.window.scene.removeItem(conn)
            self.window.timeline_connections[timeline.get_id()] = []
            for e1,e2 in zip(timeline.events[:-1], timeline.events[1:]):
                connection = Connection(self.window.events_nodes[e1], self.window.events_nodes[e2], tl_id = timeline.get_id(), color=self.window.colors[timeline.get_id()%len(self.window.colors)])
                self.window.scene.addItem(connection)
                self.window.timeline_connections[timeline.get_id()].append(connection)
                self.lines.append(connection)

    def mouseReleaseEvent(self, change):
        for line in self.lines:
            line.updateLine(self)
        new_date = self.scenePos().x()/DILATION_FACTOR_DATE
        self.event.set_date(new_date)
        self.recompute_lines()
        return super().mouseReleaseEvent(change)

class Connection(QGraphicsLineItem):
    def __init__(self, start, end, tl_id, color=Qt.black):
        super().__init__()
        self.start = start
        self.end = end
        self.timeline = tl_id
        self.setZValue(0)
        start.lines.append(self)
        end.lines.append(self)
        self.compute_shifts()
        self.setLine(self._line)
        pen = QPen(color)
        pen.setWidth(LINE_WIDTH)
        self.setPen(pen)

    def compute_shifts(self):
        shift_down_start = self.start.event.timelines.index(self.timeline)
        shift_down_end = self.end.event.timelines.index(self.timeline)
        self._line = QLineF(self.start.scenePos()+QPointF(NODE_DIAMETER/2, NODE_DIAMETER/2+shift_down_start*LINE_WIDTH), self.end.scenePos()+QPointF(NODE_DIAMETER/2, NODE_DIAMETER/2 + shift_down_end*LINE_WIDTH))

    def extremities(self):
        return self.start, self.end

    def setP2(self, p2):
        self._line.setP2(p2)
        self.setLine(self._line)

    def setStart(self, start):
        self.start = start
        self.updateLine()

    def setEnd(self, end):
        self.end = end
        self.updateLine(end)

    def updateLine(self, source):
        shift_down = source.event.timelines.index(self.timeline)
        if source == self.start:
            self._line.setP1(source.scenePos()+QPointF(NODE_DIAMETER/2, NODE_DIAMETER/2 + LINE_WIDTH*shift_down))
        else:
            self._line.setP2(source.scenePos()+QPointF(NODE_DIAMETER/2, NODE_DIAMETER/2 + LINE_WIDTH*shift_down))
        self.setLine(self._line)

class Window(QWidget):
    def __init__(self, events_dict = None, timelines_dict = None, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("background-color: gray;")

        # Defining a scene rect of 400x200, with it's origin at 0,0.
        # If we don't set this on creation, we can set it later with .setSceneRect
        self.scene = QGraphicsScene(0, 0, 400, 100)
        if events_dict is None:
            events_dict = {}
        if timelines_dict is None:
            timelines_dict = {}

        self.events_nodes = {}

        for event_id, event in events_dict.items():
            event_node = EventNode(event, self)
            
            # Add the items to the scene. Items are stacked in the order they are added.
            self.events_nodes[event_id] = event_node
        
        self.colors = [Qt.darkBlue, Qt.darkRed, Qt.darkGreen, Qt.magenta, Qt.blue, Qt.black]
        self.timeline_connections = {}
        for timeline_id, timeline in timelines_dict.items():
            self.timeline_connections[timeline_id] = []
            for e1,e2 in zip(timeline.events[:-1], timeline.events[1:]):
                connection = Connection(self.events_nodes[e1], self.events_nodes[e2], tl_id = timeline.get_id(), color=self.colors[timeline.get_id()%len(self.colors)])
                self.scene.addItem(connection)
                self.timeline_connections[timeline_id].append(connection)
        
        for event_node in self.events_nodes.values():
            self.scene.addItem(event_node)

        # Set all items as moveable and selectable.
        for item in self.scene.items():
            if isinstance(item, EventNode):
                item.setFlag(QGraphicsItem.ItemIsMovable)
                #item.setFlag(QGraphicsItem.ItemIsSelectable)
        
        xmin = min([e.scenePos().x() for e in self.events_nodes.values()])
        xmax = max([e.scenePos().x() for e in self.events_nodes.values()])
        ymin = min([e.scenePos().y() for e in self.events_nodes.values()])
        ymax = max([e.scenePos().y() for e in self.events_nodes.values()])
        self.scene.setSceneRect(xmin-100, ymin-100, xmax-xmin+100, ymax-ymin+100)

        # Define our layout.
        vbox = QVBoxLayout()

        view = QGraphicsView(self.scene)
        view.setRenderHint(QPainter.Antialiasing)

        hbox = QHBoxLayout(self)
        hbox.addLayout(vbox)
        hbox.addWidget(view)

        self.setLayout(hbox)
    
class MyMainWindow(QMainWindow):
    def __init__(self, central_widget):
        super().__init__()
        self.setCentralWidget(central_widget)
        toolbar = QToolBar("Tools")
        self.addToolBar(toolbar)
        save_button = QAction("Save", self)
        save_button.setStatusTip("This is your button")
        save_button.triggered.connect(self.save_session)
        toolbar.addAction(save_button)
    
    def save_session(self):
        Session.json_save(SESSION_NAME)

Session.json_load(SESSION_NAME)

colors_for_tl = ["white", "red", "blue", "grey", "green"]

app = QApplication(sys.argv)


w = Window(Event.event_dict, Timeline.timeline_dict, parent=None)
MW = MyMainWindow(w)

MW.show()

app.exec()
