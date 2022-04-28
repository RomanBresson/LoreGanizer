from sqlite3 import Time
from Classes import *
import json
import os

def json_save(session_name):
    for event in Event.event_dict.values():
        event.timelines.sort()
    events_str = {i:Event.event_dict[i].__dict__ for i in Event.event_dict}
    timelines_str = {i:Timeline.timeline_dict[i].name for i in Timeline.timeline_dict}
    dirpath = f'data/{session_name}'
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    with open(dirpath+'/events.json', 'w') as outfile:
        json.dump(events_str, outfile, indent=4)
    with open(dirpath+'/timelines.json', 'w') as outfile:
        json.dump(timelines_str, outfile, indent=4)

def json_load(session_name):
    Event.event_dict = {}
    Event.free_ids = []
    Timeline.timeline_dict = {}
    Timeline.free_ids = []
    dirpath = f'data/{session_name}'
    with open(dirpath+'/events.json', 'r') as infile:
        ev_json = json.load(infile)
    for ev in ev_json.values():
        ev["id_nb"] = ev["_Event__id_nb"]
        del ev["_Event__id_nb"]
        ev["date"] = ev["_Event__date"]
        del ev["_Event__date"]
        Event(**ev)
    make_timelines_from_events()
    with open(dirpath+'/timelines.json', 'r') as infile:
        tl_json = json.load(infile)
    for tl_id,tl_name in tl_json.items():
        Timeline.timeline_dict[int(tl_id)].name = tl_name
    autocomplete_free_ids_events()
    autocomplete_free_ids_timelines()

def autocomplete_free_ids_events():
    if len(Event.event_dict)==0:
        Event.free_ids = []
    else:
        Event.free_ids = [k for k in range(max(Event.event_dict)) if k not in (Event.event_dict)]

def autocomplete_free_ids_timelines():
    if len(Timeline.timeline_dict)==0:
        Timeline.free_ids = []
    else:
        Timeline.free_ids = [k for k in range(max(Timeline.timeline_dict)) if k not in (Timeline.timeline_dict)]