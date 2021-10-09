from Classes import *
import json
import os

def save(session_name):
    events_str = {i:Event.event_dict[i].__dict__ for i in Event.event_dict}
    dirpath = f'data/{session_name}'
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    with open(dirpath+'/events.json', 'w') as eventfile:
        json.dump(events_str, eventfile)

def load(session_name):
    dirpath = f'data/{session_name}'
    with open(dirpath+'/events.json', 'r') as eventfile:
        json_obj = json.load(eventfile)
    print(json_obj['1'])
