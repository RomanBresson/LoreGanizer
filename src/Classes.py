import numpy as np

class Event:
    event_count = 0
    event_dict = {}
    def __init__(self, date=0., height=0., timeline=None):
        self.__id = self.__class__.event_count
        self.__class__.event_count += 1
        self.date = date
        self.height = height
        self.timeline = timeline
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
    timeline_count = 0
    def __init__(self, birth=None, death=None):
        self.__class__.timeline_count += 1
        self.__id = self.__class__.timeline_count
        birth_event = birth if not (birth is None) else Event(date=0, height=0, timeline=self.__id)
        death_event = death if not (death is None) else Event(date=birth_event.date+1, height=0, timeline=self.__id)
        birth_event.timeline = death_event.timeline = self.__id
        self.events = [b.get_id() for b in sorted([birth_event, death_event])]
    
    def get_id(self):
        return(self.__id)
    
    def set_id(self, new_id):
        self.__id = new_id