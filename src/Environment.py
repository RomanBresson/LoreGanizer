import sys
import os
import Session
from Classes import *

from PyQt5.QtCore import Qt, QLineF, QPointF, QPoint
from PyQt5.QtGui import QBrush, QPainter, QPen, QDoubleValidator, QTransform, QCursor
from PyQt5.QtWidgets import (
    QPushButton,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QListWidgetItem,
    QListWidget,
    QDialog,
    QToolBar,
    QSizePolicy,
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

class EventNode(QGraphicsEllipseItem):
    def __init__(self, event, window):
        super().__init__(0, 0, NODE_DIAMETER, NODE_DIAMETER*(max(1,len(event.timelines))))
        self.event = event
        tls = event.timelines
        if event.height is None:
            if ((len(tls)>0)):
                self.event.height = sum(tls)/len(tls)
        self.setZValue(10)
        brush = QBrush(Qt.white)
        self.setBrush(brush)
        pen = QPen(Qt.black)
        pen.setWidth(1)
        self.setPen(pen)
        self.lines = []
        self.window = window
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setPos(self.event.get_date()*DILATION_FACTOR_DATE, self.event.height*DILATION_FACTOR_HEIGHT)
        self.nameLabel = QGraphicsTextItem(self)
        self.nameLabel.setPlainText(self.event.short_description)
        self.nameLabel.moveBy(-5, -10)
        self.nameLabel.setRotation(-45)
        self.nameLabel.setScale(1.2)
    
    def update_from_event(self):
        self.setPos(self.event.get_date()*DILATION_FACTOR_DATE, self.event.height*DILATION_FACTOR_HEIGHT)
        self.recompute_lines()
    
    def update_event_from_self(self):
        self.event.set_date(self.x()/DILATION_FACTOR_DATE) 
        self.event.height = self.y()/DILATION_FACTOR_HEIGHT
        self.recompute_lines()
    
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            pass
        elif QMouseEvent.button() == Qt.RightButton:
            pass
        
    def mouseDoubleClickEvent(self, QMouseEvent):
        edit_event_box = NodeInfoBox(self.event, self.parentWidget())
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
                    Timeline.timeline_dict[tl_id].remove_event(self.event)
            for tl_id in new_tl:
                if tl_id not in old_tl:
                    Timeline.timeline_dict[tl_id].insert_event(self.event)
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
        return super().mouseReleaseEvent(change)
    
    def recompute_lines(self):
        self.window.recompute_lines(self.event.timelines)
        self.setRect(0.,0.,NODE_DIAMETER, NODE_DIAMETER*(max(1,len(self.event.timelines))))
    
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.RightButton:
            self.contextMenuEvent(QMouseEvent)

    def contextMenuEvent(self, mouseEvent):
        contextMenu = QMenu(self.window)
        self.window.layout().addWidget(contextMenu)
        EditEv = contextMenu.addAction("Edit")
        DelEv = contextMenu.addAction("Delete")
        print((mouseEvent.scenePos()))
        action = contextMenu.exec_()
        
        if action==EditEv:
            self.mouseDoubleClickEvent(mouseEvent)
        elif action==DelEv:
            delete_event(self.event)
            self.window.scene.removeItem(self)

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
        self.timeline_connections = {}
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
        for timeline_id, timeline in timelines_dict.items():
            self.timeline_connections[timeline_id] = []
            for e1,e2 in zip(timeline.events[:-1], timeline.events[1:]):
                connection = Connection(self.events_nodes[e1], self.events_nodes[e2], tl_id = timeline.get_id(), color=self.colors[timeline.get_id()%len(self.colors)])
                self.scene.addItem(connection)
                self.timeline_connections[timeline_id].append(connection)
        
        for event_node in self.events_nodes.values():
            self.scene.addItem(event_node)

        # Set all items as moveable and selectable.
        """
        for item in self.scene.items():
            if isinstance(item, EventNode):
                item.setFlag(QGraphicsItem.ItemIsMovable)
                #item.setFlag(QGraphicsItem.ItemIsSelectable)
        """

        xmin, xmax, ymin, ymax = 0., 400, 0., 100
        if len(self.events_nodes):        
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
    
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.RightButton:
            self.contextMenuEvent(QMouseEvent)

    def contextMenuEvent(self, mouseEvent):
        contextMenu = QMenu(self)
        newEv = contextMenu.addAction("New event")
        action = contextMenu.exec_(self.mapToGlobal(mouseEvent.pos()))
        if action==newEv:
            new_event = Event(date=0., height=0)
            node = EventNode(new_event, self)
            node.setPos(node.mapToScene(mouseEvent.pos()))
            node.update_event_from_self()
            self.scene.addItem(node)
    
    def recompute_lines(self, list_of_timelines=None):
        if list_of_timelines is None:
            list_of_timelines = []
        for tl_id,timeline in Timeline.timeline_dict.items():
            for conn in self.timeline_connections[tl_id]:
                self.scene.removeItem(conn)
            self.timeline_connections[tl_id] = []
            if (len(timeline.events)>1):
                for e1,e2 in zip(timeline.events[:-1], timeline.events[1:]):
                    connection = Connection(self.events_nodes[e1], self.events_nodes[e2], tl_id = tl_id, color=self.colors[timeline.get_id()%len(self.colors)])
                    self.scene.addItem(connection)
                    self.timeline_connections[tl_id].append(connection)
                    self.events_nodes[e1].lines.append(connection)
                    self.events_nodes[e2].lines.append(connection)

class MyMainWindow(QMainWindow):
    def __init__(self, central_widget):
        super().__init__()
        self.setCentralWidget(central_widget)
        toolbar = QToolBar("Tools")
        self.addToolBar(toolbar)
        new_button = QAction("New", self)
        new_button.triggered.connect(self.new_session)
        toolbar.addAction(new_button)
        save_button = QAction("Save", self)
        save_button.triggered.connect(self.save_session)
        toolbar.addAction(save_button)
        save_as_button = QAction("Save as", self)
        save_as_button.triggered.connect(self.save_as_session)
        toolbar.addAction(save_as_button)
        load_button = QAction("Load", self)
        load_button.triggered.connect(self.load_session)
        toolbar.addAction(load_button)
        new_event = QAction("E+", self)
        new_event.triggered.connect(self.create_event)
        toolbar.addAction(new_event)
        new_tl = QAction("T+", self)
        new_tl.triggered.connect(self.create_timeline)
        toolbar.addAction(new_tl)

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

    def create_event(self):
        new_obj = EventCreator(self)
        new_obj.exec()
        fields = new_obj.getInputs()
        if fields is not None:
            new_event = Event(date=fields[0], height=fields[1], short_description=fields[2])
            new_node = EventNode(new_event, self.centralWidget())
            self.centralWidget().scene.addItem(new_node)
            self.centralWidget().events_nodes[new_event.get_id()] = new_node
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
        SESSION_NAME = new_session_name
        Session.json_save(SESSION_NAME)

    def save_as_session(self):
        self.save_session(save_as=True)

    def load_session(self):
        global SESSION_NAME
        session_loader = SessionLoader(parent=self)
        session_loader.exec()
        Session.json_load(SESSION_NAME)
        w = Window(Event.event_dict, Timeline.timeline_dict, parent=None)
        self.setCentralWidget(w)

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

class NodeInfoBox(SurveyDialog):
    def __init__(self, event, parent=None):
        self.event = event
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
        long_desc_editor.resize(500, 500)
        textBox.resize(490, 490)
        textBox.move(5, 5)
        textBox.verticalScrollBar()
        long_desc_editor.layout = QVBoxLayout()
        long_desc_editor.layout.addWidget(textBox)
        #buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=long_desc_editor)
        #buttonBox.accepted.connect(self.accept)
        #buttonBox.rejected.connect(self.reject)
        #long_desc_editor.layout.addWidget(buttonBox, alignment=(Qt.AlignRight | Qt.AlignBottom))
        long_desc_editor.exec()

class EventCreator(SurveyDialog):
    def __init__(self, parent=None):
        super().__init__(labels= ["Date", "Height", "Short Description"], parent=parent)
        self.setWindowTitle("New event")
        onlyDouble = QDoubleValidator()
        self.inputs["Date"].setValidator(onlyDouble)
        self.inputs["Height"].setValidator(onlyDouble)
        self.inputs["Short Description"].setMaxLength(Event.SHORT_DESC_MAX_LENGTH)
        self.layout.addWidget(self.buttonBox)
    
    def getInputs(self):
        try:
            return (float(self.inputs["Date"].text()), float(self.inputs["Height"].text()), self.inputs["Short Description"].text())
        except:
            return((0., 0., ""))

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

w = Window(Event.event_dict, Timeline.timeline_dict, parent=None)

MW = MyMainWindow(w)

MW.show()

app.exec()
