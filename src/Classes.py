class Event:
    """
        An event is uniquely defined by its id. 

        It has a date, a height, a short and a long description, and a set of timelines to which it belongs.
    """
    event_dict = {}
    free_ids = []
    SHORT_DESC_MAX_LENGTH = 50
    def __init__(self, id_nb=None, date=0., height=None, timelines=None, short_description=None, long_description=None, color="default"):
        if id_nb is None:
            self.__id_nb = Event.free_ids.pop(0) if (len(Event.free_ids)>0) else (max(Event.event_dict,default=-1)+1)
        else:
            self.__id_nb = id_nb
        self.__date = date
        self.timelines = timelines if not (timelines is None) else []
        self.height = height
        self.__class__.event_dict[self.__id_nb] = self
        self.set_short_description("" if short_description is None else short_description)
        self.long_description  = "" if long_description is None else long_description
        self.color = color

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
    
    def update(self):
        for timeline in self.timelines:
            Timeline.timeline_dict[timeline].update()

class Timeline:
    """
        A timeline is uniquely defined by its Id.

        It possesses a list of events, which should always be ordered by date if time travel is not allowed.
    """
    timeline_dict = {}
    free_ids = []
    def __init__(self, id_nb=None, events=None, name=None):
        self.events = []
        if id_nb is None:
            self.__id_nb = Timeline.free_ids.pop(0) if (len(Timeline.free_ids)>0) else (max(Timeline.timeline_dict,default=-1)+1)
        else:
            self.__id_nb = id_nb
        Timeline.timeline_dict[self.__id_nb] = self
        if events:
            for e in events:
                self.insert_event(e)
        if name is None:
            self.name = str(self.__id_nb)
        else:
            self.name = name
        self.color = None

    def get_id(self):
        return(self.__id_nb)
    
    def set_id(self, new_id):
        self.__id_nb = new_id

    def insert_event(self, event_id):
        event_inserted = Event.event_dict[event_id]
        if (len(self.events)==0):
            self.events.append(event_inserted.get_id())
        elif (event_inserted>(Event.event_dict[self.events[-1]])):
            self.events.append(event_inserted.get_id())
        else:
            for i,ev_id in enumerate(self.events):
                if (event_inserted<(Event.event_dict[ev_id])):
                    break
            self.events = self.events[:i] + [event_inserted.get_id()] + self.events[i:]
        if self.__id_nb not in event_inserted.timelines:
            event_inserted.timelines.append(self.__id_nb)
            event_inserted.timelines.sort()
    
    def remove_event(self, event_id):
        self.events.remove(event_id)
        Event.event_dict[event_id].timelines.remove(self.__id_nb)
    
    def update(self):
        self.events = [e.get_id() for e in sorted([Event.event_dict[i] for i in self.events])]
    
    def save_dict(self):
        dict_of_self = {
            "Name": self.name,
            "Color": self.color
        }
        return(dict_of_self)

def delete_timeline(tl):
    Timeline.free_ids.append(tl)
    for ev in Timeline.timeline_dict[tl].events:
        Event.event_dict[ev].timelines.remove(tl)
    del Timeline.timeline_dict[tl]
    del tl

def delete_event(ev):
    Event.free_ids.append(ev.get_id())
    marked_for_deletion = []
    for tl in ev.timelines:
        Timeline.timeline_dict[tl].events.remove(ev.get_id())
        if (len(Timeline.timeline_dict[tl].events)<=1):
            marked_for_deletion.append(tl)
    for tl in marked_for_deletion:
        delete_timeline(tl)
    del Event.event_dict[ev.get_id()]
    del ev

def make_timelines_from_events():
    all_ids = set()
    for ev_id, ev in Event.event_dict.items():
        all_ids = all_ids.union(ev.timelines)
    for tl_id in all_ids:
        tl = Timeline(id_nb=tl_id, events = [])
        for ev in Event.event_dict.values():
            if tl_id in ev.timelines:
                tl.insert_event(ev.get_id())