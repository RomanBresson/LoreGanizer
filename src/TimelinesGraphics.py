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
                    self.window.scene.removeItem(conn)
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

class Connection(QGraphicsLineItem):
    def __init__(self, start, end, tl_id, window, color=Qt.black):
        super().__init__()
        self.window = window
        self.start = start
        self.end = end
        self.timeline = tl_id
        self.setZValue(0)
        start.lines.append(self)
        end.lines.append(self)
        self.compute_shifts()
        self.setLine(self._line)
        pen = QPen(QColor(color))
        pen.setWidth(window.parent().config.LINE_WIDTH)
        self.setPen(pen)
        self.window.timeline_connections.setdefault(tl_id, [])
        self.window.timeline_connections[tl_id].append(self)

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