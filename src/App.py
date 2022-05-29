import sys
import os

import Session
from Classes import *

from PyQt5.QtCore import Qt, QLineF, QPointF, QPoint
from PyQt5.QtGui import QBrush, QPainter, QPen, QDoubleValidator, QKeySequence, QColor
from PyQt5.QtWidgets import (
    QPushButton,
    QToolBar,
    QShortcut,
    QLabel,
    QSizePolicy,
    QDialogButtonBox,
    QFormLayout,
    QSlider,
    QLineEdit,
    QMessageBox,
    QListWidgetItem,
    QListWidget,
    QDialog,
    QColorDialog,
    QApplication,
    QGraphicsEllipseItem,
    QMenu,
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsTextItem,
    QGraphicsLineItem,
    QHBoxLayout,
    QAbstractItemView,
    QVBoxLayout,
    QWidget,
    QAction,
    QMainWindow,
    QPlainTextEdit
)

NODE_DIAMETER = 10
LINE_WIDTH = 8
DILATION_FACTOR_DATE = 500
DILATION_FACTOR_HEIGHT = 100
SESSION_NAME = ""
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "saves")
BG_COLOR = 'lightgray'
NODE_DEFAULT_COLOR = 'white'
FONT_DEFAULT_COLOR = 'black'

class EventNode(QGraphicsEllipseItem):
    def __init__(self, event, window):
        super().__init__(0, 0, NODE_DIAMETER, NODE_DIAMETER*(max(1,len(event.timelines))))
        self.event = event
        tls = event.timelines
        if event.height is None:
            if ((len(tls)>0)):
                self.event.height = sum(tls)/len(tls)
        self.setZValue(10)
        color = NODE_DEFAULT_COLOR if (event.color=="default") else event.color
        font_color = FONT_DEFAULT_COLOR if (event.font_color=="default") else event.font_color
        brush = QBrush(QColor(color))
        self.setBrush(brush)
        pen = QPen(Qt.black)
        pen.setWidth(1)
        self.setPen(pen)
        self.lines = []
        self.window = window
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setPos(self.event.get_date()*DILATION_FACTOR_DATE, self.event.height*DILATION_FACTOR_HEIGHT)
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
        global LINE_WIDTH
        self.dateLabel.moveBy(0, LINE_WIDTH*max(1,len(self.event.timelines)))
        self.dateLabel.setPlainText(str(self.event.get_date()))

    def update_from_event(self):
        self.setPos(self.event.get_date()*DILATION_FACTOR_DATE, self.event.height*DILATION_FACTOR_HEIGHT)
        self.recompute_lines()
        self.window.recompute_size()
        self.set_name_label()
        self.set_date_label()
    
    def update_event_from_self(self):
        self.event.set_date(self.x()/DILATION_FACTOR_DATE) 
        self.event.height = self.y()/DILATION_FACTOR_HEIGHT
        self.set_date_label()
        self.recompute_lines()
           
    def mouseDoubleClickEvent(self, QMouseEvent):
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

    def delete_lines(self):
        for line in self.lines:
            self.window.scene.removeItem(line)
        self.lines = []

    def mouseReleaseEvent(self, change):
        additional_timelines = set()
        for line in self.lines:
            if line.timeline in self.event.timelines:
                line.updateLine(self)
            else:
                additional_timelines.add(line.timeline)
        self.update_event_from_self()
        self.recompute_lines()
        self.window.recompute_size()
        return super().mouseReleaseEvent(change)
    
    def recompute_lines(self):
        self.window.recompute_lines(self.event.timelines)
        self.recompute_node_size()

    def recompute_node_size(self):
        self.setRect(0.,0.,NODE_DIAMETER, NODE_DIAMETER*(max(1,len(self.event.timelines))))

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.RightButton:
            self.contextMenuEvent(QMouseEvent)

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
                global MainWindow
                MainWindow.centralWidget().recompute_lines(self.event.timelines)
                MainWindow.sideMenu.events_list.update_events()

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
                global MainWindow
                MainWindow.sideMenu.tls_list.update_tls()

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

class Connection(QGraphicsLineItem):
    def __init__(self, start, end, tl_id, window, color=Qt.black):
        super().__init__()
        self.start = start
        self.end = end
        self.timeline = tl_id
        self.setZValue(0)
        start.lines.append(self)
        end.lines.append(self)
        self.compute_shifts()
        self.setLine(self._line)
        pen = QPen(QColor(color))
        pen.setWidth(LINE_WIDTH)
        self.setPen(pen)
        self.window = window
        self.window.timeline_connections.setdefault(tl_id, [])
        self.window.timeline_connections[tl_id].append(self)
        
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

    def mousePressEvent(self, QMouseEvent):
        self.window.timelines_abstracts[self.timeline].mousePressEvent(QMouseEvent)
    
    def mouseDoubleClickEvent(self, QMouseEvent):
        self.window.timelines_abstracts[self.timeline].mouseDoubleClickEvent(QMouseEvent)

class SurveyDialog(QDialog):
    def __init__(self, labels, parent=None, add_bottom_button=False):
        super().__init__(parent)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.layout = QFormLayout(self)
        
        self.inputs = {}
        for lab in labels:
            self.inputs[lab] = QLineEdit(self)
            self.layout.addRow(lab, self.inputs[lab])
        self.buttonBox = buttonBox
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        if add_bottom_button:
            self.layout.addWidget(buttonBox)
                
    def getInputs(self):
        return tuple(input.text() for input in self.inputs.values())

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
            global MainWindow
            MainWindow.centralWidget().recompute_lines([self.timeline.get_id()])

    def getInputs(self):
        dict_ret = {}
        dict_ret["Name"] = self.inputs["Name"].text()
        dict_ret["Events"] = [s.text() for s in self.inputs["Events"].selectedItems()]
        return(dict_ret)

class Window(QWidget):
    def __init__(self, events_dict = None, timelines_dict = None, parent=None, meta_data=None):
        super().__init__(parent=parent)
        global BG_COLOR
        if meta_data is not None:
            if "bg_color" in meta_data:
                BG_COLOR = meta_data["bg_color"]
            else:
                BG_COLOR = "lightgray"
        self.setStyleSheet(f'background-color: {BG_COLOR};')
        # Defining a scene rect of 400x200, with it's origin at 0,0.
        # If we don't set this on creation, we can set it later with .setSceneRect
        self.scene = QGraphicsScene(0, 0, 400, 100)
        if events_dict is None:
            events_dict = {}
        if timelines_dict is None:
            timelines_dict = {}

        self.events_nodes = {}
        self.timeline_connections = {}
        self.timelines_abstracts = {}

        for event_id, event in events_dict.items():
            event_node = EventNode(event, self)
            
            # Add the items to the scene. Items are stacked in the order they are added.
        
        self.colors = ["#bf0000", "#00bf00", "#0000bf", "#bfbf00", "#bf00bf", "#00bfbf"]
        
        for timeline_id, timeline in timelines_dict.items():
            timeline_abstract = TimelineAbstract(timeline_id, self)
            self.timeline_connections[timeline_id] = []
            if timeline.color is None:
                timeline.color = self.colors[timeline.get_id()%len(self.colors)]
        
        for event_node in self.events_nodes.values():
            self.scene.addItem(event_node)

        # Set all items as moveable and selectable.

        if len(self.events_nodes):
            self.recompute_size()
        else:
            self.scene.setSceneRect(-1000, -200, 1000, 200)
        self.recompute_lines()

        # Define our layout.
        vbox = QVBoxLayout()

        view = QGraphicsView(self.scene)
        view.setRenderHint(QPainter.Antialiasing)

        self.view = view
        hbox = QHBoxLayout(self)
        hbox.addLayout(vbox)
        hbox.addWidget(view)

        self.setLayout(hbox)

        self.recompute_size()
        
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.RightButton:
            self.contextMenuEvent(QMouseEvent)
            self.recompute_size()

    def contextMenuEvent(self, mouseEvent):
        contextMenu = QMenu(self)
        newEv = contextMenu.addAction("New event")
        action = contextMenu.exec_(self.mapToGlobal(mouseEvent.pos()))
        if action==newEv:
            pos = self.view.mapToScene(mouseEvent.pos())
            date = pos.x()/DILATION_FACTOR_DATE
            height = pos.y()/DILATION_FACTOR_HEIGHT
            self.parent().create_event(date, height)

    def recompute_lines(self, list_of_timelines=None):
        if list_of_timelines is None:
            list_of_timelines = Timeline.timeline_dict.keys()
        for tl_id,timeline in Timeline.timeline_dict.items():
            for conn in self.timeline_connections[tl_id]:
                self.scene.removeItem(conn)
            self.timeline_connections[tl_id] = []
            if (len(timeline.events)>1):
                for e1,e2 in zip(timeline.events[:-1], timeline.events[1:]):
                    connection = Connection(self.events_nodes[e1], self.events_nodes[e2], tl_id = tl_id, color=timeline.color, window=self)
                    self.scene.addItem(connection)
                    self.events_nodes[e1].lines.append(connection)
                    self.events_nodes[e2].lines.append(connection)

    def recompute_size(self):
        if  self.events_nodes.values():
            max_x = max([e.scenePos().x() for e in self.events_nodes.values()])
            min_x = min([e.scenePos().x() for e in self.events_nodes.values()])
            max_y = max([e.scenePos().y() for e in self.events_nodes.values()])
            min_y = min([e.scenePos().y() for e in self.events_nodes.values()])
            self.scene.setSceneRect(min_x-500, min_y-500, max_x-min_x+1000, max_y-min_y+1000)

class EventListItem(QListWidgetItem):
    def __init__(self, str_display, tl_id, parent):
        super().__init__(str_display)
        self.tl_id = tl_id

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
            next_item = TimelineListItem(f'{tl_id}: {tl.name}', tl_id, parent = self)
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
    def __init__(self, str_display, tl_id, parent):
        super().__init__(str_display)
        self.tl_id = tl_id

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.RightButton:
            global MainWindow
            MainWindow.centralWidget().timelines_abstracts[self.tl_id].mousePressEvent(QMouseEvent)
        
    def mouseDoubleClickEvent(self, QMouseEvent):
        global MainWindow
        MainWindow.centralWidget().timelines_abstracts[self.tl_id].mouseDoubleClickEvent(QMouseEvent)

class EventListItem(QListWidgetItem):
    def __init__(self, str_display, event_id, parent):
        super().__init__(str_display)
        self.event_id = event_id

    def mousePressEvent(self, QMouseEvent):
        global MainWindow
        MainWindow.centralWidget().events_nodes[self.event_id].mousePressEvent(QMouseEvent)
        
    def mouseDoubleClickEvent(self, QMouseEvent):
        global MainWindow
        MainWindow.centralWidget().events_nodes[self.event_id].mouseDoubleClickEvent(QMouseEvent)
    
class EventsPanel(QListWidget):
    def __init__(self, parent):
        super().__init__()
        self.setSelectionMode(0)
        self.setWordWrap(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.update_events()
    
    def update_events(self):
        self.clear()
        for ev_id, ev in Event.event_dict.items():
            next_item = EventListItem(f'{ev_id}: {ev.short_description}', ev_id, parent = self)
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
        self.horizontal_zoom.setTickInterval(500)
        self.vertical_zoom = QSlider(Qt.Horizontal)
        self.vertical_zoom.setMinimum(0)
        self.vertical_zoom.setMaximum(500)
        self.vertical_zoom.setValue(10)
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
        global DILATION_FACTOR_DATE
        DILATION_FACTOR_DATE = self.horizontal_zoom.value()
        for ev_id, ev in self.parent().centralWidget().events_nodes.items():
            ev.update_from_event()
    
    def change_vertical_dilation_factor(self):
        global DILATION_FACTOR_HEIGHT
        DILATION_FACTOR_HEIGHT = self.vertical_zoom.value()
        for ev_id, ev in self.parent().centralWidget().events_nodes.items():
            ev.update_from_event()
    
    def mousePressEvent(self, QMouseEvent):
        ...

class MyMainWindow(QMainWindow):
    def __init__(self, central_widget):
        super().__init__()
        self.setCentralWidget(central_widget)
        self.sideMenu = SideMenu(self)
        self.addToolBar(Qt.LeftToolBarArea, self.sideMenu)
        menuBar = self.menuBar()#QMenu("Tools")
        fileMenu = menuBar.addMenu("File")
        new_button = QAction("New", self)
        new_button.triggered.connect(self.new_session)
        fileMenu.addAction(new_button)
        save_button = QAction("Save", self)
        save_button.triggered.connect(self.save_session)
        fileMenu.addAction(save_button)
        save_as_button = QAction("Save as", self)
        save_as_button.triggered.connect(self.save_as_session)
        fileMenu.addAction(save_as_button)
        load_button = QAction("Load", self)
        load_button.triggered.connect(self.load_session)
        fileMenu.addAction(load_button)

        createMenu = menuBar.addMenu("Create")
        new_event = QAction("Event", self)
        new_event.triggered.connect(self.create_event_button)
        createMenu.addAction(new_event)
        new_tl = QAction("Timeline", self)
        new_tl.triggered.connect(self.create_timeline)
        createMenu.addAction(new_tl)
        
        prefMenu = menuBar.addMenu("Preferences")
        color_bg = QAction("Theme", self)
        color_bg.triggered.connect(self.select_color)
        prefMenu.addAction(color_bg)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            global BG_COLOR
            BG_COLOR = color.name()
            self.centralWidget().setStyleSheet(f'background-color: {BG_COLOR};')

    def new_session(self):
        global SESSION_NAME
        warning_box = QMessageBox()
        warning_box.setText("All unsaved progress will be lost. Proceed ?")
        warning_box.setWindowTitle("Warning")
        warning_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ret = warning_box.exec_()
        if ret==1024:
            #ok clicked
            SESSION_NAME = ""
            Session.json_load(SESSION_NAME)
            w = Window(Event.event_dict, Timeline.timeline_dict, parent=None)
            self.setCentralWidget(w)

    def create_event_button(self):
        self.create_event()

    def create_event(self, date=None, height=None):
        new_obj = EventCreator(self, date, height)
        is_created = new_obj.exec()
        if is_created:
            fields = new_obj.getInputs()
            if fields is not None:
                new_event = Event(date=fields[0], height=fields[1], short_description=fields[2])
                new_node = EventNode(new_event, self.centralWidget())
                self.centralWidget().scene.addItem(new_node)
                self.centralWidget().recompute_size()
                self.sideMenu.events_list.update_events()
                new_node.show()
    
    def create_timeline(self):
        editor = SurveyDialog(["Name"], parent=self, add_bottom_button=True)
        editor.exec()
        name = editor.getInputs()[0]
        if name is not None:
            new_tl = Timeline(name=name)
            if name=="":
                new_tl.name = f'Timeline {new_tl.get_id()}'
            self.centralWidget().timeline_connections[new_tl.get_id()] = []
            global MainWindow
            MainWindow.sideMenu.tls_list.update_tls()

    def save_session(self, save_as=False):
        global SESSION_NAME
        new_session_name = SESSION_NAME
        if ((SESSION_NAME=="") | save_as):
            new_session_name = ""
            save_as_window = SurveyDialog(labels=["Project name"], add_bottom_button=True)
            button_clicked = 0
            while (len(new_session_name)<1):
                button_clicked = save_as_window.exec()
                if button_clicked:
                    new_session_name = save_as_window.getInputs()[0]
                else:
                    return
        meta_data = {}
        meta_data["bg_color"] = BG_COLOR
        SESSION_NAME = new_session_name
        Session.json_save(SESSION_NAME, meta_data)

    def save_as_session(self):
        self.save_session(save_as=True)

    def load_session(self):
        global SESSION_NAME
        session_loader = SessionLoader(parent=self)
        session_loader.exec()
        meta_data = Session.json_load(SESSION_NAME)
        w = Window(Event.event_dict, Timeline.timeline_dict, parent=None, meta_data=meta_data)
        self.setCentralWidget(w)
        self.sideMenu.events_list.update_events()
        self.sideMenu.tls_list.update_tls()

class NodeInfoBox(SurveyDialog):
    def __init__(self, event, eventNode, parent=None):
        self.event = event
        self.eventNode = eventNode
        items_list = ["Short Description", "Date", "Height"]
        super().__init__(labels=items_list, parent=parent)
        self.setWindowTitle("Event editor")
        self.inputs["Short Description"].setText(event.short_description)
        self.inputs["Date"].setText(str(event.get_date()))
        self.inputs["Height"].setText(str(event.height))
        self.inputs["Long Description"] = QPushButton(self)
        self.layout.addRow("Long Description", self.inputs["Long Description"])
        self.inputs["Long Description"].setText("Click to edit")
        self.inputs["Long Description"].clicked.connect(self.edit_long_description)
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
        dict_ret["Long Description"] = self.inputs["Long Description"].text()
        dict_ret["Date"] = float(self.inputs["Date"].text())
        dict_ret["Height"] = float(self.inputs["Height"].text())
        dict_ret["Timelines"] = [s.text() for s in self.inputs["Timelines"].selectedItems()]
        return(dict_ret)
    
    def edit_long_description(self):
        long_desc_editor = QDialog(parent=self.parent())
        textBox = QPlainTextEdit(long_desc_editor)
        textBox.setPlainText(self.event.long_description)
        #textBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        long_desc_editor.resize(500, 500)
        textBox.resize(490, 490)
        textBox.move(5, 5)
        textBox.verticalScrollBar()
        long_desc_editor.layout = QVBoxLayout()
        long_desc_editor.layout.addWidget(textBox)
        long_desc = long_desc_editor.exec()
        self.event.long_description = textBox.toPlainText()

class EventCreator(SurveyDialog):
    def __init__(self, parent=None, date=None, height=None):
        super().__init__(labels= ["Date", "Height", "Short Description"], parent=parent)
        self.setWindowTitle("New event")
        onlyDouble = QDoubleValidator()
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

class SessionLoader(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setWindowTitle("Load existing session")
        #msg.setText("Select session to load")
        available_sessions = [session.name[:-5] for session in os.scandir(DATA_PATH)]
        self.resize(200, 300)
        self.listwidget = QListWidget(parent=self)
        self.listwidget.setWordWrap(True)
        self.listwidget.setSelectionMode(1)
        self.listwidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.listwidget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.listwidget.addItems(available_sessions)
        self.listwidget.resize(200, 250)

        self.ok_button = QPushButton(self)
        self.ok_button.setText("Ok")
        self.ok_button.clicked.connect(self.clicked)
        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(self.ok_button, alignment=(Qt.AlignRight | Qt.AlignBottom))
        #self.verticalLayout.addWidget(self.ok_button, alignment=Qt.AlignBottom)

    def clicked(self):
        warning_box = QMessageBox()
        warning_box.setText("All unsaved progress will be lost. Proceed ?")
        warning_box.setWindowTitle("Warning")
        warning_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ret = warning_box.exec_()
        if ret==1024:
            #ok clicked
            global SESSION_NAME
            SESSION_NAME = self.listwidget.currentItem().text()
        self.close()

#Session.json_load(SESSION_NAME)

colors_for_tl = ["white", "red", "blue", "grey", "green"]

app = QApplication(sys.argv)

AppWindow = Window(Event.event_dict, Timeline.timeline_dict, parent=None)

MainWindow = MyMainWindow(AppWindow)

MainWindow.saveSc = QShortcut(QKeySequence('Ctrl+S'), MainWindow)
MainWindow.saveSc.activated.connect(MainWindow.save_session)

MainWindow.show()

app.exec()
