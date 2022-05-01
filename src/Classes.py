import numpy as np
import bisect

class Event:
    event_dict = {}
    free_ids = []
    SHORT_DESC_MAX_LENGTH = 50
    def __init__(self, id_nb=None, date=0., height=0., timelines=None, short_description=None, long_description=None):
        if id_nb is None:
            self.__id_nb = Event.free_ids.pop(0) if (len(Event.free_ids)>0) else (max(Event.event_dict,default=-1)+1)
        else:
            self.__id_nb = id_nb
        self.__date = date
        self.height = height
        self.timelines = timelines if not (timelines is None) else []
        self.__class__.event_dict[self.__id_nb] = self
        self.set_short_description("" if short_description is None else short_description)
        self.long_description  = "" if long_description is None else long_description

    def __gt__(self, other):
        return(self.__date>other.__date)
    
    def __ge__(self, other):
        return(self.__date>=other.__date)
    
    def __lt__(self, other):
        return(self.__date<other.__date)

    def __le__(self, other):
        return(self.__date<=other.__date)
    
    def get_id(self):
        return(self.__id_nb)
    
    def set_id(self, new_id):
        self.__id_nb = new_id
    
    def get_date(self):
        return(self.__date)

    def set_date(self, date):
        self.__date = date
        self.update()

    def set_short_description(self, desc):
        self.short_description = desc[:Event.SHORT_DESC_MAX_LENGTH]
    
    def get_short_description(self):
        return(self.short_description)
    
    def add_to_timeline(self, tl_id):
        if tl_id not in self.timelines:
            self.timelines.append(tl_id)
            self.timelines.sort()

    def update(self):
        for timeline in self.timelines:
            Timeline.timeline_dict[timeline].update()

class Timeline:
    timeline_dict = {}
    free_ids = []
    def __init__(self, birth=None, death=None, id_nb=None, events=None, name=None):
        if id_nb is None:
            self.__id_nb = Timeline.free_ids.pop(0) if (len(Timeline.free_ids)>0) else (max(Timeline.timeline_dict,default=-1)+1)
        else:
            self.__id_nb = id_nb
        Timeline.timeline_dict[self.__id_nb] = self
        if (events is None):
            birth_event = birth if not (birth is None) else Event(date=0, height=0, timelines=[])
            death_event = death if not (death is None) else Event(date=birth_event.get_date()+1, height=0, timelines=[])
            birth_event.add_to_timeline(self.__id_nb)
            death_event.add_to_timeline(self.__id_nb)
            self.events = [ev.get_id() for ev in sorted([birth_event, death_event])]
        else:
            assert(len(events)>=2)
            self.events = []
            for ev in events:
                self.insert_event(Event.event_dict[ev])
        if name is None:
            self.name = str(self.__id_nb)
        else:
            self.name = name

    def get_id(self):
        return(self.__id_nb)
    
    def set_id(self, new_id):
        self.__id_nb = new_id

    def insert_event(self, event_inserted):
        if (len(self.events)==0):
            self.events.append(event_inserted.get_id())
        elif (event_inserted>(Event.event_dict[self.events[-1]])):
            self.events.append(event_inserted.get_id())
        else:
            for i,ev_id in enumerate(self.events):
                if (event_inserted<(Event.event_dict[ev_id])):
                    break
            self.events = self.events[:i] + [event_inserted.get_id()] + self.events[i:]
        event_inserted.add_to_timeline(self.__id_nb)
    
    def remove_event(self, event_to_remove):
        self.events.remove(event_to_remove)
        Event.event_dict[event_to_remove].timelines.remove(self.__id_nb)
    
    def update(self):
        self.events = [e.get_id() for e in sorted([Event.event_dict[i] for i in self.events])]

def delete_timeline(tl):
    Timeline.free_ids.append(tl.get_id())
    for ev in tl.events:
        Event.event_dict[ev].timelines.remove(tl.get_id())
    del Timeline.timeline_dict[tl.get_id()]
    del tl

def delete_event(ev):
    Event.free_ids.append(ev.get_id())
    marked_for_deletion = []
    for tl in ev.timelines:
        Timeline.timeline_dict[tl].events.remove(ev.get_id())
        if (len(Timeline.timeline_dict[tl].events)<=1):
            marked_for_deletion.append(tl)
    for tl in marked_for_deletion:
        delete_timeline(Timeline.timeline_dict[tl])
    del Event.event_dict[ev.get_id()]
    del ev

def make_timelines_from_events():
    all_ids = set()
    for ev_id, ev in Event.event_dict.items():
        all_ids = all_ids.union(ev.timelines)
    for tl_id in all_ids:
        tl = Timeline(id_nb=tl_id, events=[ev.get_id() for ev in Event.event_dict.values() if tl_id in ev.timelines])