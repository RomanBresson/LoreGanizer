from Classes import Event, Timeline, delete_event, delete_timeline
from Session import *

tl_names = {"CharA":0, "CharB":1, "CharC":2}

CharA_life = [
    Event(date=0, short_description="CharA birth", long_description="CharA is born"),
    Event(date=2, short_description="CharA starts school", long_description="CharA starts going to school"),
    Event(date=19, short_description="Meets CharD", long_description="CharA meets CharD in her bar"),
    Event(date=19.75, short_description="Eats with CharD", long_description="CharA goes to the restaurant with CharD"),
    Event(date=20, short_description="CharA sick", long_description="CharA gets sick because of the restaurant"),
    Event(date=20.02, short_description="Goes to the doctor", long_description="CharA goes to receive a treetment, gets prescribed some medicine"),
    Event(date=20.2, short_description="CharA Meets CharB", long_description="CharA meets CharB for the first time", timelines=[1]),
    Event(date=21, short_description="Returns home", long_description="CharA returns to their home alone")
    ]

CharB_life = [
    Event(date=0, short_description="Gets a promotion", long_description="CharB gets a promotion at work, they are now a regional manager"),
    Event(date=22, short_description="Becomes CEO", long_description="CharB's boss retires, and they get the job because of theur performance"),
    Event(date=17, short_description="CharB Meets CharC", long_description="CharB meets CharC for the first time at the football field", timelines=[2]),
    ]

CharC_life = [
    Event(date=-20, short_description="CharC birth", long_description="CharC is born in a close city, at the top of a tower"),
    Event(date=18, short_description="Starts working on project", long_description="Agrees with CharB and starts working on ways to make the sales better"),
    Event(date=20.5, short_description="All meet", long_description="CharB makes CharC and CharA meet", timelines=[0,1])
    ]

for e in CharA_life:
    e.timelines.append(0)

for e in CharB_life:
    e.timelines.append(1)

for e in CharC_life:
    e.timelines.append(2)

make_timelines_from_events()
for name in tl_names:
    Timeline.timeline_dict[tl_names[name]].name = name

json_save("trial_session")
