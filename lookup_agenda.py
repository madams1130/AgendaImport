#!/usr/bin/env python3

from db_table import db_table 
import pandas as pd
import sys

if (len(sys.argv) < 3):
    print("Input format: ./lookup_agenda.py <column> <value>")
    exit(1)
# input: ./lookup_agenda.py <column> <value>

event_info = db_table("agenda", {
    "id": "integer PRIMARY KEY AUTOINCREMENT",
    "date": "text",
    "time_start": "text",
    "time_end": "text",
    "session_type": "text",
    "title": "text",
    "location": "text",
    "description": "text"
})

speakersTable = db_table("speakers", {
    "id": "integer PRIMARY KEY AUTOINCREMENT",
    "name": "text UNIQUE"
})

eventSpeakersTable = db_table("event_speakers", {
    "event_id": "integer",
    "speaker_id": "integer",
    "PRIMARY KEY": "(event_id, speaker_id)"
})

if (sys.argv[1] == "speaker"):
    # if we're looking for a speaker, find all of their events!!

    # get the id of our speaker
    speakFind = (speakersTable.select(["id"], {"name" : sys.argv[2]}))[0]["id"]

    # pull out all matching events!
    searchResults = eventSpeakersTable.select(["event_id"], {"speaker_id" : speakFind})

    for result in searchResults:
        findnar = event_info.select([], {"id" : result["event_id"]})
        print(findnar)

else:
    searchResults = event_info.select(["id"], {sys.argv[1] : sys.argv[2]})

    for result in searchResults:
        findnar = event_info.select([], {"id" : result["id"]})
        print(findnar)

#print(ids)

#rows = event_info.select(columns=["id", "date", "time_start", "time_end", "session_type"])

#for row in rows:
#    print(row)