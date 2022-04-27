import time
import networkx as nx
import matplotlib.pyplot as plt
import Session
from Classes import *
import sys

from PyQt5.QtCore import Qt, QLineF, QPointF
from PyQt5.QtGui import QBrush, QPainter, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsLineItem,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

NODE_DIAMETER = 10

class EventNode(QGraphicsEllipseItem):
    def __init__(self, event):
        super().__init__(0, 0, NODE_DIAMETER, NODE_DIAMETER)
        tls = event.timelines
        if len(tls)>0:
            event.height = sum(tls)/len(tls)
        self.setPos(event.date*500, event.height*100)
        self.event = event

        brush = QBrush(Qt.blue)
        self.setBrush(brush)

        pen = QPen(Qt.cyan)
        pen.setWidth(1)
        self.setPen(pen)
        self.lines = []
    
    def itemChange(self, change, value):
        for line in self.lines:
            line.updateLine(self)
        return super().itemChange(change, value)

class Connection(QGraphicsLineItem):
    def __init__(self, start, end):
        super().__init__()
        self.start = start
        self.end = end
        start.lines.append(self)
        end.lines.append(self)
        self._line = QLineF(start.scenePos()+QPointF(NODE_DIAMETER/2, NODE_DIAMETER/2), end.scenePos()+QPointF(NODE_DIAMETER/2, NODE_DIAMETER/2))
        self.setLine(self._line)

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
        if source == self.start:
            self._line.setP1(source.scenePos()+QPointF(NODE_DIAMETER/2, NODE_DIAMETER/2))
        else:
            self._line.setP2(source.scenePos()+QPointF(NODE_DIAMETER/2, NODE_DIAMETER/2))
        self.setLine(self._line)

class Window(QWidget):
    def __init__(self, events_dict = None, timelines_dict = None):
        super().__init__()

        # Defining a scene rect of 400x200, with it's origin at 0,0.
        # If we don't set this on creation, we can set it later with .setSceneRect
        self.scene = QGraphicsScene(0, 0, 400, 100)
        if events_dict is None:
            events_dict = {}
        if timelines_dict is None:
            timelines_dict = {}

        events_nodes = {}

        for event_id, event in events_dict.items():
            event_node = EventNode(event)
            
            # Add the items to the scene. Items are stacked in the order they are added.
            self.scene.addItem(event_node)
            events_nodes[event_id] = event_node
        
        for timeline_id, timeline in timelines_dict.items():
            for e1,e2 in zip(timeline.events[:-1], timeline.events[1:]):
                connection = Connection(events_nodes[e1], events_nodes[e2])
                self.scene.addItem(connection)

        # Set all items as moveable and selectable.
        for item in self.scene.items():
            if isinstance(item, EventNode):
                item.setFlag(QGraphicsItem.ItemIsMovable)
                item.setFlag(QGraphicsItem.ItemIsSelectable)
        
        xmin = min([e.scenePos().x() for e in events_nodes.values()])
        xmax = max([e.scenePos().x() for e in events_nodes.values()])
        ymin = min([e.scenePos().y() for e in events_nodes.values()])
        ymax = max([e.scenePos().y() for e in events_nodes.values()])
        self.scene.setSceneRect(xmin, ymin, xmax, ymax)
        
        # Define our layout.
        vbox = QVBoxLayout()

        view = QGraphicsView(self.scene)
        view.setRenderHint(QPainter.Antialiasing)

        hbox = QHBoxLayout(self)
        hbox.addLayout(vbox)
        hbox.addWidget(view)

        self.setLayout(hbox)

Session.json_load("session_test")

colors_for_tl = ["white", "red", "blue", "grey", "green"]

app = QApplication(sys.argv)

w = Window(Event.event_dict, Timeline.timeline_dict)
w.show()

app.exec()
