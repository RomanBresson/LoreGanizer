import sys
import os

import Session
from Classes import *
from LeftMenu import SideMenu
from GlobalVariables import CONFIG
from EventNodes import EventNode, EventCreator
from SurveyDialog import SurveyDialog
from TimelinesGraphics import Connection, TimelineAbstract

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QKeySequence
from PyQt5.QtWidgets import (
    QPushButton,
    QShortcut,
    QMessageBox,
    QListWidget,
    QDialog,
    QColorDialog,
    QApplication,
    QMenu,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QAbstractItemView,
    QVBoxLayout,
    QWidget,
    QAction,
    QMainWindow,
)

class Window(QWidget):
    def __init__(self, events_dict = None, timelines_dict = None, parent=None, meta_data=None):
        super().__init__(parent=parent)
        if meta_data is not None:
            if "bg_color" in meta_data:
                parent.config.BG_COLOR = meta_data["bg_color"]
            else:
                parent.config.BG_COLOR = "lightgray"
        self.setStyleSheet(f'background-color: {parent.config.BG_COLOR};')
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
            date = pos.x()/self.parent().config.DILATION_FACTOR_DATE
            height = pos.y()/self.parent().config.DILATION_FACTOR_HEIGHT
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

class MyMainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.config = config
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
        close_button = QAction("Exit", self)
        close_button.triggered.connect(self.close_warning)
        fileMenu.addAction(close_button)

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
            self.config.BG_COLOR = color.name()
            self.centralWidget().setStyleSheet(f'background-color: {self.config.BG_COLOR};')

    def new_session(self):
        warning_box = QMessageBox()
        warning_box.setText("All unsaved progress will be lost. Proceed ?")
        warning_box.setWindowTitle("Warning")
        warning_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ret = warning_box.exec_()
        if ret==1024:
            #ok clicked
            self.config = CONFIG()
            Session.json_load(self.config.SESSION_NAME, self.config.DATA_PATH)
            w = Window(Event.event_dict, Timeline.timeline_dict, parent=self)
            self.setCentralWidget(w)
            self.sideMenu.events_list.update_events()
            self.sideMenu.tls_list.update_tls()

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
            TimelineAbstract(new_tl.get_id(), self.centralWidget())
            self.sideMenu.tls_list.update_tls()

    def save_session(self, save_as=False):
        new_session_name = self.config.SESSION_NAME
        if ((self.config.SESSION_NAME=="") | save_as):
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
        meta_data["bg_color"] = self.config.BG_COLOR
        self.config.SESSION_NAME = new_session_name
        Session.json_save(self.config.SESSION_NAME, self.config.DATA_PATH, meta_data)

    def save_as_session(self):
        self.save_session(save_as=True)

    def load_session(self):
        session_loader = SessionLoader(parent=self)
        session_loader.exec()
        meta_data = Session.json_load(self.config.SESSION_NAME, self.config.DATA_PATH)
        w = Window(Event.event_dict, Timeline.timeline_dict, parent=self, meta_data=meta_data)
        self.setCentralWidget(w)
        self.sideMenu.events_list.update_events()
        self.sideMenu.tls_list.update_tls()
    
    def close_warning(self):
        warning_box = QMessageBox()
        warning_box.setText("All unsaved progress will be lost. Proceed ?")
        warning_box.setWindowTitle("Warning")
        warning_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ret = warning_box.exec_()
        if ret==1024:
            self.close()

class SessionLoader(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setWindowTitle("Load existing session")
        #msg.setText("Select session to load")
        available_sessions = [session.name[:-5] for session in os.scandir(parent.config.DATA_PATH)]
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
            self.parent().config.SESSION_NAME = self.listwidget.currentItem().text()
        self.close()

colors_for_tl = ["white", "red", "blue", "grey", "green"]

app = QApplication(sys.argv)

config = CONFIG()
MainWindow = MyMainWindow(config)
AppWindow = Window(Event.event_dict, Timeline.timeline_dict, parent=MainWindow)

if not os.path.exists(MainWindow.config.DATA_PATH):
    os.makedirs(MainWindow.config.DATA_PATH)

MainWindow.saveSc = QShortcut(QKeySequence('Ctrl+S'), MainWindow)
MainWindow.closeSc = QShortcut(QKeySequence('Alt+F4'), MainWindow)
MainWindow.saveSc.activated.connect(MainWindow.save_session)
MainWindow.closeSc.activated.connect(MainWindow.close_warning)
MainWindow.setCentralWidget(AppWindow)

MainWindow.show()

app.exec()