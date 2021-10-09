from Classes import Event, Timeline
import unittest

class TestStringMethods(unittest.TestCase):

    def test_init_event(self):
        Event.event_count = 0
        Event.event_dict = {}
        event1 = Event()
        event2 = Event()
        self.assertEqual(event1.date,0)
        self.assertEqual(event1.get_id(),0)
        self.assertEqual(event2.date,0)
        self.assertEqual(event2.get_id(),1)
        self.assertIs(event1.timeline,None)
        self.assertIs(event2.timeline,None)
    
    def test_comp_event(self):
        Event.event_count = 0
        Event.event_dict = {}
        event1 = Event(date=10)
        event2 = Event(date=8)
        self.assertGreater(event1, event2)
        self.assertGreaterEqual(event1, event2)
        self.assertLess(event2, event1)
        self.assertLessEqual(event2, event1)

    def test_init_timeline(self):
        Event.event_count = 0
        Event.event_dict = {}
        Timeline.timeline_count = 0
        timeline1 = Timeline()
        self.assertEqual(timeline1.events, [0,1])

    def test_init_timelines(self):
        Event.event_count = 0
        Event.event_dict = {}
        Timeline.timeline_count = 0
        event1 = Event(date=10)
        event2 = Event(date=8)
        timeline1 = Timeline()
        timeline2 = Timeline(event1, event2)
        self.assertEqual(Event.event_count,4)
        self.assertEqual(timeline1.events, [2,3])
        self.assertEqual(timeline2.events, [1,0])

if __name__ == '__main__':
    unittest.main()