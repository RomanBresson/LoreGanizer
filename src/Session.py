from Classes import *
import json
import os

def json_save(session_name):
    events_str = {i:Event.event_dict[i].__dict__ for i in Event.event_dict}
    timelines_str = {i:Timeline.timeline_dict[i].__dict__ for i in Timeline.timeline_dict}
    dirpath = f'data/{session_name}'
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    with open(dirpath+'/events.json', 'w') as outfile:
        json.dump(events_str, outfile)
    with open(dirpath+'/timelines.json', 'w') as outfile:
        json.dump(timelines_str, outfile)

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
        Event(**ev)
    with open(dirpath+'/timelines.json', 'r') as infile:
        tl_json = json.load(infile)
    for tl in tl_json.values():
        tl["id_nb"] = tl["_Timeline__id_nb"]
        del tl["_Timeline__id_nb"]
        Timeline(**tl)
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