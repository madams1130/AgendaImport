#!/usr/bin/env python3

from db_table import db_table 
import pandas as pd
import sys
import textwrap

printed = []

COL_WIDTHS = {
    "title": 15,
    "location": 15,
    "session_type": 20
}

# store keys to loop over later
EVENT_COLUMNS = [
    #"id",
    "date",
    "time_start",
    "time_end",
    "session_type",
    "title",
    "location"
]

# Printing "nan" over and over offends my aesthetic sensibilities
def clean(value):
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    if str(value).lower() == "nan":
        return ""
    return value

# "re-couple" speaker table with event table in output
def get_speakers(event_id):
    speaker_links = eventSpeakersTable.select(["speaker_id"], {"event_id": event_id})
    names = []

    # get all speakers associated with an event!
    # though this was originally in the agenda.xls file, my table structure 
    # handles them through a join table, so you can't grab the speaker list directly.
    # (plus, commas look better than semicolons!)
    for link in speaker_links:
        speaker = speakersTable.select(["name"], {"id": link["speaker_id"]})
        if speaker:
            names.append(speaker[0]["name"])

    return names

# because why write a bunch of nice code if your output is incomprehensible?
def format_row(session):
    for col in EVENT_COLUMNS:
        # remove nans
        val = clean(session.get(col, ""))
        print(f"{col:<12}: {val}")

    speakers = get_speakers(session["id"])
    speakers = [clean(s) for s in speakers if clean(s)]

    print(f"{'speakers':<12}: {', '.join(speakers) if speakers else ''}")

    print()

    desc = clean(session.get("description", ""))
    if desc:
        wrapped_desc = textwrap.fill(
            desc,
            width=80,
            initial_indent="    ",
            subsequent_indent="    "
        )
        print(wrapped_desc)

    print("\n" + "-" * 80 + "\n")

# what ties it all together
def pretty_print_session(session_id):

    # because subsessions can be printed independently, avoid dupes!
    if session_id in printed:
        return
    printed.append(session_id)

    rows = event_info.select(
        [],
        {"id": session_id}
    )

    if not rows:
        return

    session = rows[0]
    format_row(session)
    
    # find all related subsessions for given session
    subs = subsessionTable.select(["subsession_id"], {"main_id": session_id})

    for sub in subs:
        sub_id = sub["subsession_id"]
        #no risk of infinite recursion, subsessions can't have sub-subsessions
        pretty_print_session(sub_id)

if (len(sys.argv) < 3):
    print("Input format: ./lookup_agenda.py <column> <value>")
    exit(1)

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

subsessionTable = db_table("sub_sessions", {
    "main_id": "integer",
    "subsession_id": "integer",
    "PRIMARY KEY": "(main_id, subsession_id)"
})

if (sys.argv[1] == "speaker"):
    # if we're looking for a speaker, find all of their events!!

    # get the id of our speaker
    try:
        speakFind = (speakersTable.select(["id"], {"name" : sys.argv[2]}))[0]["id"]
    except IndexError:
        print("No matching events found.")
        exit()


    # pull out all matching events!
    searchResults = eventSpeakersTable.select(["event_id"], {"speaker_id" : speakFind})

    for result in searchResults:
        pretty_print_session(result["event_id"])

else:
    # normal search, less tricky
    searchResults = event_info.select(["id"], {sys.argv[1] : sys.argv[2]})

    if searchResults:
        for result in searchResults:
            pretty_print_session(result["id"])
    else:
        print("No matching events found.")
        exit()