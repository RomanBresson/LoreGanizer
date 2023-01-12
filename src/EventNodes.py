from Classes import *
from LeftMenu import *
from SurveyDialog import SurveyDialog

from PyQt5.QtCore import Qt, QPoint, QRegularExpression
from PyQt5.QtGui import QBrush, QPen, QColor, QRegularExpressionValidator
from PyQt5.QtWidgets import (
    QPushButton,
    QMessageBox,
    QListWidgetItem,
    QListWidget,
    QDialog,
    QColorDialog,
    QGraphicsEllipseItem,
    QMenu,
    QGraphicsItem,
    QGraphicsTextItem,
    QAbstractItemView,
    QVBoxLayout,
    QPlainTextEdit
)

class EventNode(QGraphicsEllipseItem):
    def __init__(self, event, window):
        super().__init__(0, 0, window.parent().config.NODE_DIAMETER, window.parent().config.NODE_DIAMETER*(max(1,len(event.timelines))))
        self.event = event
        tls = event.timelines
        if event.height is None:
            if ((len(tls)>0)):
                self.event.height = sum(tls)/len(tls)
            else:
                self.event.height = 0.
        self.setZValue(10)
        color = window.parent().config.NODE_DEFAULT_COLOR if (event.color=="default") else event.color
        font_color = window.parent().config.FONT_DEFAULT_COLOR if (event.font_color=="default") else event.font_color
        brush = QBrush(QColor(color))
        self.setBrush(brush)
        pen = QPen(Qt.black)
        pen.setWidth(1)
        self.setPen(pen)
        self.lines = []
        self.window = window
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setPos(self.event.get_date()*self.window.parent().config.DILATION_FACTOR_DATE, self.event.height*self.window.parent().config.DILATION_FACTOR_HEIGHT)
        self.nameLabel = QGraphicsTextItem(self)
        self.nameLabel.setRotation(-45)
        self.nameLabel.moveBy(-5, -15)
        self.nameLabel.setScale(1.25)
        self.set_name_label()
        self.dateLabel = QGraphicsTextItem(self)
        self.dateLabel.setScale(1.25)
        self.set_date_label()
        self.window.events_nodes[self.event.get_id()] = self

    def set_name_label(self):
        self.nameLabel.setDefaultTextColor(QColor(self.event.font_color))
        self.nameLabel.setPlainText(self.event.short_description)
    
    def set_date_label(self):
        self.dateLabel.setDefaultTextColor(QColor(self.event.font_color))
        self.dateLabel.setPos(-5, 0)
        self.dateLabel.moveBy(0, self.window.parent().config.LINE_WIDTH*max(1,len(self.event.timelines)))
        self.dateLabel.setPlainText(str(round(self.event.get_date(),3)))

    def update_from_event(self):
        self.setPos(self.event.get_date()*self.window.parent().config.DILATION_FACTOR_DATE, self.event.height*self.window.parent().config.DILATION_FACTOR_HEIGHT)
        self.recompute_lines()
        self.window.recompute_size()
        self.set_name_label()
        self.set_date_label()
    
    def update_event_from_self(self):
        self.event.set_date(self.x()/self.window.parent().config.DILATION_FACTOR_DATE) 
        self.event.height = self.y()/self.window.parent().config.DILATION_FACTOR_HEIGHT
        self.set_date_label()
        self.recompute_lines()
           
    def mouseDoubleClickEvent(self, QMouseEvent):
        self.setSelected()
        edit_event_box = NodeInfoBox(self.event, self, self.parentWidget())
        which_button = edit_event_box.exec()
        new_values = edit_event_box.getInputs()
        if which_button:
            self.event.short_description = new_values["Short Description"]
            self.event.long_description = new_values["Long Description"]
            self.event.set_date(new_values["Date"])
            self.event.height = new_values["Height"]
            tl_name_to_id = {tl.name:tl.get_id() for tl in Timeline.timeline_dict.values()}
            old_tl = [tl_id for tl_id in self.event.timelines]
            new_tl = [tl_name_to_id[nv] for nv in new_values["Timelines"]]
            for tl_id in old_tl:
                if tl_id not in new_tl:
                    Timeline.timeline_dict[tl_id].remove_event(self.event.get_id())
            for tl_id in new_tl:
                if tl_id not in old_tl:
                    Timeline.timeline_dict[tl_id].insert_event(self.event.get_id())
        self.update_from_event()
        self.unsetSelected()
        self.window.parent().sideMenu.events_list.update_events()

    def setSelected(self):
        pen = QPen(Qt.black)
        pen.setWidth(3)
        self.setPen(pen)

    def unsetSelected(self):
        pen = QPen(Qt.black)
        pen.setWidth(1)
        self.setPen(pen)

    def delete_lines(self):
        for line in self.lines:
            self.window.scene.removeItem(line)
        self.lines = []

    def mouseReleaseEvent(self, change):
        additional_timelines = set()
        for line in self.lines:
            if line.timeline in self.event.timelines:
                line.updateLines(self)
            else:
                additional_timelines.add(line.timeline)
        self.update_event_from_self()
        self.recompute_lines()
        self.window.recompute_size()
        self.unsetSelected()
        return super().mouseReleaseEvent(change)
    
    def recompute_lines(self):
        self.window.recompute_lines(self.event.timelines)
        self.recompute_node_size()

    def recompute_node_size(self):
        self.setRect(0.,0., self.window.parent().config.NODE_DIAMETER, self.window.parent().config.NODE_DIAMETER*(max(1,len(self.event.timelines))))

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.RightButton:
            self.setSelected()
            self.update_event_from_self()
            self.contextMenuEvent(QMouseEvent)
            self.unsetSelected()

    def contextMenuEvent(self, mouseEvent):
        contextMenu = QMenu(self.window)
        EditEv = contextMenu.addAction("Edit")
        DelEv = contextMenu.addAction("Delete")
        int_screen_pos = QPoint(int(mouseEvent.screenPos().x()), int(mouseEvent.screenPos().y()))
        action = contextMenu.exec_(int_screen_pos)
        
        if action==EditEv:
            self.mouseDoubleClickEvent(mouseEvent)
        elif action==DelEv:
            warning_box = QMessageBox()
            warning_box.setText("Delete this event ?")
            warning_box.setWindowTitle("Warning")
            warning_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            ret = warning_box.exec_()
            if ret:
                delete_event(self.event)
                self.window.scene.removeItem(self)
                self.window.recompute_lines(self.event.timelines)
                self.window.parent().sideMenu.events_list.update_events()

class NodeInfoBox(SurveyDialog):
    def __init__(self, event, eventNode, parent=None):
        self.event = event
        self.eventNode = eventNode
        self.pending_long_description = self.event.long_description
        items_list = ["Short Description", "Date", "Height"]
        super().__init__(labels=items_list, parent=parent)
        self.setWindowTitle("Event editor")
        self.inputs["Short Description"].setText(event.short_description)
        self.inputs["Date"].setText(str(event.get_date()))
        self.inputs["Height"].setText(str(event.height))
        regexp_double = QRegularExpression("[0-9]*(\.[0-9]*)?")
        onlyDouble = QRegularExpressionValidator(regexp_double)
        self.inputs["Date"].setValidator(onlyDouble)
        self.inputs["Height"].setValidator(onlyDouble)
        self.inputs["Short Description"].setMaxLength(Event.SHORT_DESC_MAX_LENGTH)
        self.LongDescZone = QPlainTextEdit(self)
        self.LongDescZone.setPlainText(self.pending_long_description)
        self.layout.addRow("Long Description", self.LongDescZone)
        self.inputs["Long Description"] = self.LongDescZone
        self.inputs["Color"] = QPushButton(self)
        self.layout.addRow("Color", self.inputs["Color"])
        self.inputs["Color"].setText("Click to edit")
        self.inputs["Color"].clicked.connect(self.select_color)
        self.inputs["Font color"] = QPushButton(self)
        self.layout.addRow("Font color", self.inputs["Font color"])
        self.inputs["Font color"].setText("Click to edit")
        self.inputs["Font color"].clicked.connect(self.select_font_color)
        self.inputs["Timelines"] = QListWidget(self)
        self.inputs["Timelines"].setSelectionMode(2)
        self.inputs["Timelines"].setWordWrap(True)
        self.inputs["Timelines"].setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.inputs["Timelines"].setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        for tl_id, tl in Timeline.timeline_dict.items():
            next_item = QListWidgetItem(tl.name, parent = self.inputs["Timelines"])
            next_item.setText(tl.name)
            if tl_id in event.timelines:
                next_item.setSelected(True)
            self.inputs["Timelines"].addItem(next_item)
        self.layout.addRow(self.inputs["Timelines"])
        self.layout.addWidget(self.buttonBox)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.event.color = color.name()
            brush = QBrush(QColor(color))
            self.eventNode.setBrush(brush)
    
    def select_font_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.event.font_color = color.name()
            self.eventNode.set_name_label()
            self.eventNode.set_date_label()
    
    def getInputs(self):
        dict_ret = {}
        dict_ret["Short Description"] = self.inputs["Short Description"].text()
        dict_ret["Long Description"] = self.inputs["Long Description"].toPlainText()
        dict_ret["Date"] = float(self.inputs["Date"].text())
        dict_ret["Height"] = float(self.inputs["Height"].text())
        dict_ret["Timelines"] = [s.text() for s in self.inputs["Timelines"].selectedItems()]
        return(dict_ret)

class EventCreator(SurveyDialog):
    def __init__(self, parent=None, date=None, height=None):
        super().__init__(labels= ["Date", "Height", "Short Description"], parent=parent)
        self.setWindowTitle("New event")
        regexp_double = QRegularExpression("[0-9]*(\.[0-9]*)?")
        onlyDouble = QRegularExpressionValidator(regexp_double)
        self.inputs["Date"].setValidator(onlyDouble)
        self.inputs["Height"].setValidator(onlyDouble)
        self.inputs["Short Description"].setMaxLength(Event.SHORT_DESC_MAX_LENGTH)
        if date is not None:
            self.inputs["Date"].setText(str(date))
        if height is not None:
            self.inputs["Height"].setText(str(height))
        self.layout.addWidget(self.buttonBox)
    
    def getInputs(self):
        try:
            date = float(self.inputs["Date"].text())
        except:
            date = 0.
        try:
            height =  float(self.inputs["Height"].text())
        except:
            height = 0.
        short_description = self.inputs["Short Description"].text()
        return(date, height, short_description)