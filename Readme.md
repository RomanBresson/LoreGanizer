# CrossRoadsTracker

Whether for story-writing, process-management or simply keeping tracks of interacting chains of events, CrossRoadsTracker is designed to be a tool for easy creation, edition and visualization of intertwined timelines. 

Visualization is akin to the way public transportation/metro lines are often represented, to ensure readability.

# General Description

## Events

It allows to represent events as nodes. An event has:
* a date, which defines its horizontal position
* a height, which defines its vertical position
* a short description (50 characters at most), which will be displayed on screen
* a long description, which can be accessed by double clicking the event, and has unlimited length

![Nodes](https://user-images.githubusercontent.com/22815154/169374500-99baf898-196b-4065-810e-126e0588cf9d.png)

## Timelines

Timelines are sets of connected events. The events are necessarily ordered (by date) in a timeline (time travel is not possible yet).

![GH](https://user-images.githubusercontent.com/22815154/169899950-e9533579-c684-428c-a316-1588e5d50ad0.png)

# How to use ?
## Install and run

This was tested and made using Python 3.9. Using a virtualenv is recommended.

    git clone https://github.com/RomanBresson/CrossRoadsTracker
    cd CrossRoadsTracker
    pip install -r requirements.txt
    python src/App.py

## Session handling

You can create, save, and load sessions using the toolbar. The files are saved in the "saves" directory and can be edited manually, as long as they remain coherent.

## Handling events

Events can be created in two ways:
* Using the E+ button in the toolbar allows to create an event and set its height, date and short description instantly
* Right-clicking anywhere and selecting "Create event" will create an event at the position of the click 

Events can be deleted by right-clicking the event and choosing the "Delete" option.

Events can be edited by:
* Right-clicking the event and choosing the "Delete" option
* Double-clicking the event
* Drag-and-dropping the event to a new date/height

This opens an editor which allows you to 
* edit the date, height, and short description of the event
* display and edit the long description by clicking on the associated button
* select the timelines to which the event belongs

## Handling timelines

Timelines can be created by clicking on the T+ button of the toolbar.

Once created, events can be added to the timeline by double-clicking those events and highlighting the desired timeline. They can be removed in the same way.

# Misc

See ToDo.txt for next steps
