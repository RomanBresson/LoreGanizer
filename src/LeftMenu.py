from Classes import *

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QToolBar,
    QLabel,
    QSlider,
    QListWidgetItem,
    QListWidget,
    QAbstractItemView,
)

class TimelinePanel(QListWidget):
    def __init__(self, parent):
        super().__init__()
        self.setSelectionMode(0)
        self.setWordWrap(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.update_tls()
    
    def update_tls(self):
        self.clear()
        for tl_id, tl in Timeline.timeline_dict.items():
            next_item = TimelineListItem(f'{tl_id}: {tl.name}', tl_id, parent_list=self)
            next_item.setText(f"{tl_id}: {tl.name}")
            self.addItem(next_item)
    
    def mouseDoubleClickEvent(self, QMouseEvent):
        item_clicked = self.itemAt(QMouseEvent.pos())
        if item_clicked is not None:
            item_clicked.mouseDoubleClickEvent(QMouseEvent)
    
    def mousePressEvent(self, QMouseEvent):
        item_clicked = self.itemAt(QMouseEvent.pos())
        if item_clicked is not None:
            item_clicked.mousePressEvent(QMouseEvent)

class TimelineListItem(QListWidgetItem):
    def __init__(self, str_display, tl_id, parent_list):
        super().__init__(str_display)
        self.parent_list = parent_list
        self.tl_id = tl_id

    def mousePressEvent(self, QMouseEvent):
        self.parent_list.parent().parent().centralWidget().timelines_abstracts[self.tl_id].mousePressEvent(QMouseEvent)
        
    def mouseDoubleClickEvent(self, QMouseEvent):
        self.parent_list.parent().parent().centralWidget().timelines_abstracts[self.tl_id].mouseDoubleClickEvent(QMouseEvent)
    
class EventsPanel(QListWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setSelectionMode(0)
        self.setWordWrap(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.update_events()
    
    def update_events(self):
        self.clear()
        for ev_id, ev in Event.event_dict.items():
            next_item = EventListItem(f'{ev_id}: {ev.short_description}', ev_id, parent_list=self)
            next_item.setText(f"{ev_id}: {ev.short_description}")
            self.addItem(next_item)
    
    def mouseDoubleClickEvent(self, QMouseEvent):
        item_clicked = self.itemAt(QMouseEvent.pos())
        if item_clicked is not None:
            item_clicked.mouseDoubleClickEvent(QMouseEvent)
    
    def mousePressEvent(self, QMouseEvent):
        item_clicked = self.itemAt(QMouseEvent.pos())
        if item_clicked is not None:
            item_clicked.mousePressEvent(QMouseEvent)

class EventListItem(QListWidgetItem):
    def __init__(self, str_display, event_id, parent_list):
        super().__init__(str_display)
        self.event_id = event_id
        self.parent_list = parent_list

    def mousePressEvent(self, QMouseEvent):
        self.parent_list.parent().parent().centralWidget().events_nodes[self.event_id].mousePressEvent(QMouseEvent)
        
    def mouseDoubleClickEvent(self, QMouseEvent):
        self.parent_list.parent().parent().centralWidget().events_nodes[self.event_id].mouseDoubleClickEvent(QMouseEvent)

class SideMenu(QToolBar):
    def __init__(self, parent):
        super().__init__()
        self.horizontal_zoom = QSlider(Qt.Horizontal)
        self.horizontal_zoom.setMinimum(0)
        self.horizontal_zoom.setMaximum(2000)
        self.horizontal_zoom.setValue(500)
        label_h_zoom, label_v_zoom = QLabel(self), QLabel(self)
        label_h_zoom.setText("Horizontal zoom")
        label_v_zoom.setText("Vertical zoom")
        self.addWidget(label_h_zoom)
        self.addWidget(self.horizontal_zoom)
        self.horizontal_zoom.setTickPosition(QSlider.TicksBelow)
        self.horizontal_zoom.setTickInterval(parent.config.DILATION_FACTOR_DATE)
        self.vertical_zoom = QSlider(Qt.Horizontal)
        self.vertical_zoom.setMinimum(0)
        self.vertical_zoom.setMaximum(500)
        self.vertical_zoom.setValue(parent.config.DILATION_FACTOR_HEIGHT)
        self.vertical_zoom.setTickPosition(QSlider.TicksBelow)
        self.vertical_zoom.setTickInterval(125)
        self.addWidget(label_v_zoom)
        self.addWidget(self.vertical_zoom)
        self.vertical_zoom.valueChanged.connect(self.change_vertical_dilation_factor)
        self.horizontal_zoom.valueChanged.connect(self.change_horizontal_dilation_factor)
        self.events_list = EventsPanel(self)
        label_events_panel = QLabel(self)
        label_events_panel.setText("Events")
        self.addWidget(label_events_panel)
        self.addWidget(self.events_list)
        self.tls_list = TimelinePanel(self)
        label_tls_panel = QLabel(self)
        label_tls_panel.setText("Timelines")
        self.addWidget(label_tls_panel)
        self.addWidget(self.tls_list)

    def change_horizontal_dilation_factor(self):
        self.parent().config.DILATION_FACTOR_DATE = self.horizontal_zoom.value()
        for ev_id, ev in self.parent().centralWidget().events_nodes.items():
            ev.update_from_event()
    
    def change_vertical_dilation_factor(self):
        self.parent().config.DILATION_FACTOR_HEIGHT = self.vertical_zoom.value()
        for ev_id, ev in self.parent().centralWidget().events_nodes.items():
            ev.update_from_event()