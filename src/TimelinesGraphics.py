from Classes import *
from LeftMenu import *
from EventNodes import *
from SurveyDialog import SurveyDialog
from TimelinesGraphics import *

from PyQt5.QtCore import Qt, QLineF, QPointF, QPoint
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import (
    QPushButton,
    QMessageBox,
    QListWidgetItem,
    QListWidget,
    QColorDialog,
    QMenu,
    QGraphicsLineItem,
    QAbstractItemView,
)

class TimelineAbstract:
    """
        No real graphical class, proxy for click events
    """
    def __init__(self, tl_id, window):
        self.timeline = tl_id
        self.window = window
        self.window.timelines_abstracts[self.timeline] = self
    
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.RightButton:
            self.contextMenuEvent(QMouseEvent)
    
    def contextMenuEvent(self, mouseEvent):
        contextMenu = QMenu()
        EditEv = contextMenu.addAction("Edit")
        DelEv = contextMenu.addAction("Delete")
        int_screen_pos = QPoint(int(mouseEvent.screenPos().x()), int(mouseEvent.screenPos().y()))
        action = contextMenu.exec_(int_screen_pos)
        if action==EditEv:
            self.mouseDoubleClickEvent(mouseEvent)
        elif action==DelEv:
            warning_box = QMessageBox()
            warning_box.setText("Delete this timeline ?")
            warning_box.setWindowTitle("Warning")
            warning_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            ret = warning_box.exec_()
            if ret:
                for conn in self.window.timeline_connections[self.timeline]:
                    conn.remove_from_scene(self.window.scene)
                delete_timeline(self.timeline)
                del self.window.timeline_connections[self.timeline]
                del self.window.timelines_abstracts[self.timeline]
                self.window.parent().sideMenu.tls_list.update_tls()

    def mouseDoubleClickEvent(self, QMouseEvent):
        timeline = Timeline.timeline_dict[self.timeline]
        edit_event_box = TimeLineInfoBox(timeline, self.window)
        which_button = edit_event_box.exec()
        new_values = edit_event_box.getInputs()
        sd_to_id = {f'{ev_id}: {ev.short_description}':ev_id for ev_id,ev in Event.event_dict.items()}
        if which_button:
            timeline.name = new_values["Name"]
            if new_values["Events"]:
                new_events = [sd_to_id[nv] for nv in new_values["Events"]]
                old_events = timeline.events
                for ev_id in old_events:
                    if ev_id not in new_events:
                        timeline.remove_event(ev_id)
                        self.window.events_nodes[ev_id].recompute_node_size()
                for ev_id in new_events:
                    if ev_id not in old_events:
                        timeline.insert_event(ev_id)
                        self.window.events_nodes[ev_id].recompute_node_size()
        self.window.recompute_lines()
        self.window.recompute_size()
        self.window.parent().sideMenu.tls_list.update_tls()

class AbstractConnection():
    """
        An interface for any graphics version of lines
    """
    def __init__(self, start, end, tl_id, window, color=Qt.black):
        self.window = window
        self.start = start
        self.end = end
        self.timeline = tl_id
        self.color = color
        self.lines = []
    
    def add_to_scene(self, scene):
        for line in self.lines:
            self.window.scene.addItem(line)
    
    def remove_from_scene(self, scene):
        for line in self.lines:
            self.window.scene.removeItem(line)
            self.lines = []
    
    def updateLines(self, source):
        for line in self.lines:
            line.updateLine(source)

    def paint(self):
        for lin in self.lines:
            lin.paint()

class AbstractConnectionSimpleLine(AbstractConnection):
    """
        Implements a simple line
    """
    def __init__(self, start, end, tl_id, window, color=Qt.black):
        super().__init__(start, end, tl_id, window, color)
        start.lines.append(self)
        end.lines.append(self)
        self.window.timeline_connections.setdefault(tl_id, [])
        self.window.timeline_connections[tl_id].append(self)
        self.lines = [LineConnection(self.start, self.end, self.timeline, self.window, color)]

class LineConnection(QGraphicsLineItem):
    def __init__(self, start, end, tl_id, window, color=Qt.black):
        super().__init__()
        self.window = window
        self.start = start
        self.end = end
        self.timeline = tl_id
        self.setZValue(0)
        self.compute_shifts()
        self.setLine(self._line)
        pen = QPen(QColor(color))
        pen.setWidth(window.parent().config.LINE_WIDTH)
        self.setPen(pen)

    def compute_shifts(self):
        shift_down_start = self.start.event.timelines.index(self.timeline)
        shift_down_end = self.end.event.timelines.index(self.timeline)
        self._line = QLineF(self.start.scenePos()+QPointF(self.window.parent().config.NODE_DIAMETER/2, self.window.parent().config.NODE_DIAMETER/2+shift_down_start*self.window.parent().config.LINE_WIDTH), self.end.scenePos()+QPointF(self.window.parent().config.NODE_DIAMETER/2, self.window.parent().config.NODE_DIAMETER/2 + shift_down_end*self.window.parent().config.LINE_WIDTH))

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
            self._line.setP1(source.scenePos()+QPointF(self.window.parent().config.NODE_DIAMETER/2, self.window.parent().config.NODE_DIAMETER/2 + self.window.parent().config.LINE_WIDTH*shift_down))
        else:
            self._line.setP2(source.scenePos()+QPointF(self.window.parent().config.NODE_DIAMETER/2, self.window.parent().config.NODE_DIAMETER/2 + self.window.parent().config.LINE_WIDTH*shift_down))
        self.setLine(self._line)

    def mousePressEvent(self, QMouseEvent):
        self.window.timelines_abstracts[self.timeline].mousePressEvent(QMouseEvent)
    
    def mouseDoubleClickEvent(self, QMouseEvent):
        self.window.timelines_abstracts[self.timeline].mouseDoubleClickEvent(QMouseEvent)

class AbstractConnectionMetroLine(AbstractConnection):
    """
        Implements a horizontal, diagonal, then horizontal line
    """
    def __init__(self, start, end, tl_id, window, color=Qt.black):
        super().__init__(start, end, tl_id, window, color)
        self.points_limits = self.compute_points_limits()
        self.compute_shifts()
        self.pen = QPen(QColor(color))
        self.pen.setWidth(window.parent().config.LINE_WIDTH)
        self.compute_parts()

    def compute_parts(self):
        x1, y1 = self.points_limits[0].x(), self.points_limits[0].y()
        x2, y2 = self.points_limits[1].x(), self.points_limits[1].y()
        breakpoint1 = QPointF(x1+(x2-x1)/3, y1)
        breakpoint2 = QPointF(x2-(x2-x1)/3, y2)
        self.firstpart = QGraphicsLineItem()
        self.firstpart.setLine(QLineF(self.points_limits[0], breakpoint1))
        self.middlepart = QGraphicsLineItem()
        self.middlepart.setLine(QLineF(breakpoint1, breakpoint2))
        self.lastpart = QGraphicsLineItem()
        self.lastpart.setLine(QLineF(breakpoint2, self.points_limits[1]))
        self.lines = [self.firstpart, self.middlepart, self.lastpart]
        for lin in self.lines:
            lin.setZValue(0)
            lin.setPen(self.pen)

    def compute_shifts(self):
        shift_down_start = self.start.event.timelines.index(self.timeline)
        shift_down_end = self.end.event.timelines.index(self.timeline)
        return(shift_down_start, shift_down_end)

    def compute_points_limits(self):
        shift_down_start, shift_down_end = self.compute_shifts()
        return(self.start.scenePos()+QPointF(self.window.parent().config.NODE_DIAMETER/2, self.window.parent().config.NODE_DIAMETER/2+shift_down_start*self.window.parent().config.LINE_WIDTH), self.end.scenePos()+QPointF(self.window.parent().config.NODE_DIAMETER/2, self.window.parent().config.NODE_DIAMETER/2 + shift_down_end*self.window.parent().config.LINE_WIDTH))

    def extremities(self):
        return self.start, self.end

    def updateLines(self, source):
        self.compute_shifts()
        self.compute_points_limits()
        self.compute_parts()

    def mousePressEvent(self, QMouseEvent):
        self.window.timelines_abstracts[self.timeline].mousePressEvent(QMouseEvent)

    def mouseDoubleClickEvent(self, QMouseEvent):
        self.window.timelines_abstracts[self.timeline].mouseDoubleClickEvent(QMouseEvent)

class TimeLineInfoBox(SurveyDialog):
    def __init__(self, timeline, parent=None):
        items_list = ["Name"]
        super().__init__(labels=items_list, parent=parent)
        self.timeline = timeline
        self.setWindowTitle("Timeline editor")
        self.inputs["Name"].setText(timeline.name)
        self.inputs["Color"] = QPushButton(self)
        self.layout.addRow("Color", self.inputs["Color"])
        self.inputs["Color"].setText("Click to edit")
        self.inputs["Color"].clicked.connect(self.select_color)
        self.inputs["Events"] = QListWidget(self)
        self.inputs["Events"].setSelectionMode(2)
        self.inputs["Events"].setWordWrap(True)
        self.inputs["Events"].setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.inputs["Events"].setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        for ev_id, ev in Event.event_dict.items():
            next_item = QListWidgetItem(f'{ev_id}: {ev.short_description}', parent = self.inputs["Events"])
            next_item.setText(f"{ev_id}: {ev.short_description}")
            if ev_id in timeline.events:
                next_item.setSelected(True)
            self.inputs["Events"].addItem(next_item)
        self.layout.addRow(self.inputs["Events"])
        self.layout.addWidget(self.buttonBox)
    
    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.timeline.color = color.name()
            self.parent().recompute_lines([self.timeline.get_id()])

    def getInputs(self):
        dict_ret = {}
        dict_ret["Name"] = self.inputs["Name"].text()
        dict_ret["Events"] = [s.text() for s in self.inputs["Events"].selectedItems()]
        return(dict_ret)