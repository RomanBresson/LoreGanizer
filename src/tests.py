from Classes import Event, Timeline, delete_event, delete_timeline
from Session import *
import unittest

class TestStringMethods(unittest.TestCase):

    def test_init_event(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event1 = Event()
        self.assertEqual(event1.get_date(),0)
        self.assertEqual(event1.get_id(),0)
        self.assertEqual(event1.timelines,[])

    def test_setting_id_event(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event1 = Event()
        self.assertEqual(event1.get_id(),0)
        event1.set_id(52)
        self.assertEqual(event1.get_id(),52)
    
    def test_setting_short_desc_event(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event1 = Event()
        event1.set_short_description("At this point in time, it just so happened that something extremely surprising occurred.")
        self.assertEqual(event1.get_short_description(),"At this point in time, it just so happened that so")

    def test_increment_id_events(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event1 = Event()
        self.assertEqual(event1.get_id(),0)
        event2 = Event()
        self.assertEqual(event2.get_id(),1)
        self.assertEqual(event2.get_date(),0)
        self.assertEqual(event2.timelines,[])

    def test_comparison_events(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event1 = Event(date=10)
        event2 = Event(date=8)
        self.assertGreater(event1, event2)
        self.assertGreaterEqual(event1, event2)
        self.assertLess(event2, event1)
        self.assertLessEqual(event2, event1)

    def test_init_timeline(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        timeline1 = Timeline()
        self.assertEqual(timeline1.get_id(), 0)
        self.assertEqual(timeline1.events, [])
    
    def test_setting_id_timeline(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        timeline1 = Timeline()
        timeline1.set_id(52)
        self.assertEqual(timeline1.get_id(),52)

    def test_increment_id_timeline(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        timeline1 = Timeline()
        timeline2 = Timeline()
        timeline3 = Timeline()
        self.assertEqual(timeline1.get_id(), 0)
        self.assertEqual(timeline2.get_id(), 1)
        self.assertEqual(timeline3.get_id(), 2)

    def test_init_items_by_timeline(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event1 = Event(date=10)
        event2 = Event(date=8)
        timeline1 = Timeline()
        timeline2 = Timeline(events=[event1.get_id(), event2.get_id()])
        self.assertEqual(len(Event.event_dict),2)
        self.assertEqual(timeline1.events, [])
        self.assertEqual(timeline2.events, [1,0])

    def test_insert_event_in_timelines(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event0 = Event(date=0)
        event1 = Event(date=5)
        event2 = Event(date=3)
        event3 = Event(date=-3)
        event4 = Event(date=8)
        timeline1 = Timeline(events=[event0.get_id(), event1.get_id()])
        self.assertEqual(timeline1.events, [0,1])
        timeline1.insert_event(event2.get_id())
        self.assertEqual(timeline1.events, [0,2,1])
        timeline1.insert_event(event4.get_id())
        self.assertEqual(timeline1.events, [0,2,1,4])
        timeline1.insert_event(event3.get_id())
        self.assertEqual(timeline1.events, [3,0,2,1,4])
        self.assertEqual(event0.timelines, [0])
        self.assertEqual(event1.timelines, [0])
        self.assertEqual(event2.timelines, [0])
        self.assertEqual(event3.timelines, [0])
        self.assertEqual(event4.timelines, [0])

    def test_delete_event_free_id(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event0 = Event(date=0)
        event1 = Event(date=5)
        event2 = Event(date=3)
        self.assertEqual(Event.free_ids,[])
        delete_event(event2)
        self.assertEqual(Event.free_ids,[2])
        delete_event(event1)
        self.assertEqual(Event.free_ids,[2,1])

    def test_delete_event_free_dict(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event0 = Event(date=0)
        event1 = Event(date=5)
        event2 = Event(date=3)
        event3 = Event(date=-3)
        event4 = Event(date=8)
        self.assertEqual(len(Event.event_dict), 5)
        delete_event(event2)
        self.assertEqual(len(Event.event_dict), 4)
        delete_event(event1)
        self.assertEqual(len(Event.event_dict), 3)
        self.assertEqual([e.get_id() for e in Event.event_dict.values()],[0,3,4])
        self.assertEqual([e.get_date() for e in Event.event_dict.values()],[0,-3,8])

    def test_timeline_dies_if_fewer_than_2_events(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event0 = Event(date=0)
        event1 = Event(date=5)
        event2 = Event(date=3)
        event3 = Event(date=10)
        timeline0 = Timeline(events=[event0.get_id(), event1.get_id()])
        timeline1 = Timeline(events=[event0.get_id(), event1.get_id()])
        timeline0.insert_event(event2.get_id())
        timeline0.insert_event(event3.get_id())
        timeline1.insert_event(event2.get_id())
        delete_event(event0)
        delete_event(event1)
        self.assertEqual(Timeline.free_ids,[1])
        self.assertEqual(list(Timeline.timeline_dict.keys()),[0])

    def test_new_events_take_free_ids(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event0 = Event(date=0)
        event1 = Event(date=5)
        event2 = Event(date=3)
        event3 = Event(date=10)
        delete_event(event3)
        delete_event(event1)
        event4 = Event(date=10)
        self.assertEqual(event4.get_id(),3)
        event5 = Event(date=11)
        self.assertEqual(event5.get_id(),1)
        event6 = Event(date=11)
        self.assertEqual(event6.get_id(),4)

    def test_delete_timeline(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event0 = Event(date=0)
        event1 = Event(date=5)
        event2 = Event(date=3)
        event3 = Event(date=10)
        timeline0 = Timeline(events = [event0.get_id(), event1.get_id()])
        timeline1 = Timeline(events = [event0.get_id(), event1.get_id()])
        timeline0.insert_event(event2.get_id())
        timeline0.insert_event(event3.get_id())
        timeline1.insert_event(event2.get_id())
        self.assertEqual(event0.timelines,[0,1])
        self.assertEqual(event1.timelines,[0,1])
        self.assertEqual(event2.timelines,[0,1])
        self.assertEqual(event3.timelines,[0])
        delete_timeline(timeline1)  
        self.assertEqual(event0.timelines,[0])
        self.assertEqual(event1.timelines,[0])
        self.assertEqual(event2.timelines,[0])
        self.assertEqual(event3.timelines,[0])
        delete_timeline(timeline0)
        self.assertEqual(Timeline.free_ids,[1,0])
        self.assertEqual(event0.timelines,[])
        self.assertEqual(event1.timelines,[])
        self.assertEqual(event2.timelines,[])
        self.assertEqual(event3.timelines,[])

    def test_load_save_event(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event0 = Event(date=0)
        event1 = Event(date=5)
        event2 = Event(date=3)
        event3 = Event(date=10)
        delete_event(event2)
        json_save("session_test")
        Event.event_dict = {}
        Event.free_ids = []
        json_load("session_test")
        self.assertEqual(list(Event.event_dict.keys()), [0,1,3])
        self.assertEqual([ev.get_date() for ev in Event.event_dict.values()], [0,5,10])
    
    def test_load_save_timeline(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event0 = Event(date=10)
        event1 = Event(date=5)
        event2 = Event(date=3)
        event3 = Event(date=0)
        delete_event(event2)
        timeline1 = Timeline()
        timeline2 = Timeline(id_nb=5)
        Timeline.free_ids = [1,2,3,4]
        timeline3 = Timeline(events=[0,3])
        json_save("session_test")
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        json_load("session_test")
        self.assertEqual(set(list(Timeline.timeline_dict.keys())), set([0,5,1]))
        self.assertEqual(Timeline.timeline_dict[0].events, [])
        self.assertEqual(Timeline.timeline_dict[5].events, [])
        self.assertEqual(Timeline.timeline_dict[1].events, [3,0])
    
    def test_update_tl(self):
        Event.event_dict = {}
        Event.free_ids = []
        Timeline.timeline_dict = {}
        Timeline.free_ids = []
        event0 = Event(date=10)
        event1 = Event(date=5)
        event2 = Event(date=3)
        event3 = Event(date=0)
        timeline1 = Timeline(events=[0,1,3])
        timeline2 = Timeline(events=[0,3,2])
        timeline3 = Timeline(events=[1,3,2])
        self.assertEqual(timeline1.events, [3,1,0])
        self.assertEqual(timeline2.events, [3,2,0])
        self.assertEqual(timeline3.events, [3,2,1])
        event0.set_date(4)
        self.assertEqual(timeline1.events, [3,0,1])
        self.assertEqual(timeline2.events, [3,2,0])
        self.assertEqual(timeline3.events, [3,2,1])

if __name__ == '__main__':
    unittest.main()