from Classes import Event, Timeline, delete_event, delete_timeline
from Session import *

tl_names = {"A":0, "B":1, "C":2}

A_life = [
    Event(date=0, short_description="A birth", long_description="A is born"),
    Event(date=2, short_description="A starts school", long_description="A starts going to school"),
    Event(date=19, short_description="A Meets D", long_description="A meets D at a bar"),
    Event(date=19.75, short_description="Eats with D", long_description="A goes to the restaurant with D"),
    Event(date=20, short_description="A goes to the shopping mall", long_description="A goes to buy some new clothes for a festival"),
    Event(date=20.02, short_description="Festival", long_description="A goes to a music festival. They see their favorite musicians there"),
    Event(date=20.2, short_description="A Meets B", long_description="A meets B for the first time", timelines=[1]),
    Event(date=21, short_description="A Buys CD", long_description="A buys a CD of the band they saw at the festival")
    ]

B_life = [
    Event(date=0, short_description="B gets a promotion", long_description="B gets a promotion at work, they are now a regional manager"),
    Event(date=22, short_description="B goes to buy coffee", long_description="B has run out of coffee. They go buy some at the supermarket, or they will be tired for the rest of the week."),
    Event(date=17, short_description="B Meets C", long_description="B meets C for the first time at the football field", timelines=[2]),
    ]

C_life = [
    Event(date=-20, short_description="C birth", long_description="C is born"),
    Event(date=18, short_description="C goes to the bar with B", long_description="C goes to watch another game with B at the local bar. They have orange juice and some toasts.", timelines=[1]),
    Event(date=20.5, short_description="All meet", long_description="B makes C and A meet", timelines=[0,1])
    ]

for e in A_life:
    e.timelines.append(0)

for e in B_life:
    e.timelines.append(1)

for e in C_life:
    e.timelines.append(2)

make_timelines_from_events()
for name in tl_names:
    Timeline.timeline_dict[tl_names[name]].name = name

json_save("trial_session")