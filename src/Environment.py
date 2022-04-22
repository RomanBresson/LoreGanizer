from pyvis.network import Network
import networkx as nx

import Session
from Classes import *

Session.json_load("city_sesh")

colors_for_tl = ["white", "red", "blue", "grey", "green"]

net = Network("1080px", "1920px", bgcolor="000000", font_color="white")

for event_id,event in Event.event_dict.items():
    if event.height==0:
        tls = event.timelines
        event.height = sum(tls)/len(tls)
    net.add_node(event_id, label=event.short_description, title=event.long_description, x=event.date*500, y=event.height*200, physics=False, size=10)
for tl_id,tl in Timeline.timeline_dict.items():
    for ev1,ev2 in zip(tl.events[:-1],tl.events[1:]):
        net.add_edge(ev1, ev2, color=colors_for_tl[tl_id%len(colors_for_tl)])


net.show("test.html")