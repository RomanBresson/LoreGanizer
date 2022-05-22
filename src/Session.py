from Classes import *
import json

def json_save(session_name, meta_data=None):
    if meta_data is None:
        meta_data = {}
    for event in Event.event_dict.values():
        event.timelines.sort()
    events_str = {i:Event.event_dict[i].__dict__ for i in Event.event_dict}
    timelines_str = {i:Timeline.timeline_dict[i].name for i in Timeline.timeline_dict}
    complete_str = {"events": events_str, "timelines": timelines_str}
    complete_str["meta_data"] = {}
    for k,v in meta_data.items():
        complete_str["meta_data"][k] = v
    filepath = f'saves/{session_name}.json'
    with open(filepath, 'w') as outfile:
        json.dump(complete_str, outfile, indent=4)

def json_load(session_name):
    Event.event_dict = {}
    Event.free_ids = []
    Timeline.timeline_dict = {}
    Timeline.free_ids = []
    if session_name:
        filepath = f'saves/{session_name}.json'
        with open(filepath, 'r') as infile:
            json_str = json.load(infile)
            ev_json = json_str["events"]
            tl_json = json_str["timelines"]
            meta_data = {}
            if "meta_data" in json_str:
                meta_data = json_str["meta_data"]
        for ev in ev_json.values():
            ev["id_nb"] = ev["_Event__id_nb"]
            del ev["_Event__id_nb"]
            ev["date"] = ev["_Event__date"]
            del ev["_Event__date"]
            Event(**ev)
        make_timelines_from_events()
        for tl_id_str,tl_name in tl_json.items():
            tl_id = int(tl_id_str)
            if tl_id not in Timeline.timeline_dict: #timelines that are in the saves but have no event
                Timeline.timeline_dict[tl_id] = Timeline(tl_id)
            Timeline.timeline_dict[tl_id].name = tl_name
        autocomplete_free_ids_events()
        autocomplete_free_ids_timelines()
        return(meta_data)

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