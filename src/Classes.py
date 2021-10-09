import numpy as np
import bisect

class Event:
    event_dict = {}
    free_ids = []
    def __init__(self, date=0., height=0., timeline=None):
        self.__id = self.free_ids.pop() if (len(self.free_ids)>0) else len(self.event_dict)
        self.date = date
        self.height = height
        self.timelines = timeline if not (timeline is None) else []
        self.__class__.event_dict[self.__id] = self
        self.__short_description = ""
        self.long_description  = ""

    def __gt__(self, other):
        return(self.date>other.date)
    
    def __ge__(self, other):
        return(self.date>=other.date)
    
    def __lt__(self, other):
        return(self.date<other.date)

    def __le__(self, other):
        return(self.date<=other.date)
    
    def get_id(self):
        return(self.__id)
    
    def set_id(self, new_id):
        self.__id = new_id

    def set_sort_description(self, desc):
        self.short_description = desc[:100]

class Timeline:
    timeline_dict = {}
    free_ids = []
    def __init__(self, birth=None, death=None):
        self.__id = self.free_ids.pop() if (len(self.free_ids)>0) else len(self.timeline_dict)
        Timeline.timeline_dict[self.__id] = self
        birth_event = birth if not (birth is None) else Event(date=0, height=0, timeline=[])
        death_event = death if not (death is None) else Event(date=birth_event.date+1, height=0, timeline=[])
        birth_event.timelines.append(self.__id)
        death_event.timelines.append(self.__id)
        self.events = sorted([birth_event, death_event])
    
    def get_id(self):
        return(self.__id)
    
    def set_id(self, new_id):
        self.__id = new_id

    def insert_event(self, event_inserted):
        bisect.insort(self.events, event_inserted)