#!/usr/bin/env python3

from db_table import db_table 
import pandas as pd
import sys

# The Irish can and will mess up your SQL databases
def clean(val):
    return str(val).replace("'", "''")

# try to read in the table.
try:
    bigTable = pd.read_excel(sys.argv[1], engine="xlrd", skiprows=14)
except IndexError:
    print("Input Structure: ./import_agenda.py agenda.xls <table.xls>")
    exit(1)
except: 
    print("Unrecognized Table.")
    exit(1)

# fun fact: I learned SQL in Paris, and had to google how some concepts translated to English!

# Main table: hold almost all info about events themselves.
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

# Speakers Table: Who are these speakers?
speakersTable = db_table("speakers", {
    "id": "integer PRIMARY KEY AUTOINCREMENT",
    "name": "text UNIQUE"
})

# Join table: Where have the speakers spoken?
eventSpeakersTable = db_table("event_speakers", {
    "event_id": "integer",
    "speaker_id": "integer",
    "PRIMARY KEY": "(event_id, speaker_id)"
})

# Join table: what sessions are subsessions associated with?
subsessionTable = db_table("sub_sessions", {
    "main_id": "integer",
    "subsession_id": "integer",
    "PRIMARY KEY": "(main_id, subsession_id)"
})

colNames = list(bigTable.columns)

# This is an aritfact of .xls I believe? Column names are present in the raw data,
# many times over. We don't want those rows!
bigTable = bigTable[bigTable[str(colNames[0])] != str(colNames[0])]
bigTable = bigTable[bigTable[str(colNames[1])] != str(colNames[1])]
bigTable = bigTable[bigTable[str(colNames[2])] != str(colNames[2])]
bigTable = bigTable[bigTable[str(colNames[3])] != str(colNames[3])]
bigTable = bigTable[bigTable[str(colNames[4])] != str(colNames[4])]

speaker_list = []
order = 1

# maintain so that subsessions are coherent (first session will never be subsession)
main_title = ""
supersession_id = -1

# dictionary! avoid selecting while writing
speaker_cache = {}

for _, row in bigTable.iterrows():

    # if this is a main session, prepare for possible subsessions
    if (clean(row[str(colNames[3])]) == "Session"):
        main_title = clean(row[str(colNames[4])])
        supersession_id = order
        event_id = event_info.insert({
            "date": clean(row[str(colNames[0])]),
            "time_start": clean(row[str(colNames[1])]),
            "time_end": clean(row[str(colNames[2])]),
            "session_type": clean(row[str(colNames[3])]),
            "title": clean(row[str(colNames[4])]),
            "location": clean(row[str(colNames[5])]),
            "description": clean(row[str(colNames[6])])
        })
    elif (clean(row[str(colNames[3])]) == "Sub"):
        subsessionTable.insert({"main_id" : supersession_id, "subsession_id" : order})
        event_id = event_info.insert({
            "date": clean(row[str(colNames[0])]),
            "time_start": clean(row[str(colNames[1])]),
            "time_end": clean(row[str(colNames[2])]),
            "session_type": ("Subsession of " + main_title),            #clean(row[str(colNames[3])]),
            "title": clean(row[str(colNames[4])]),
            "location": clean(row[str(colNames[5])]),
            "description": clean(row[str(colNames[6])])
        })
    else:
        print("Unrecognized Session Type.")
        exit(1)

    # get raw speakers string
    speakerRepository = clean(row["Speakers"])

    # turn into "mini-array" w/ semicolon delimiters (if it exists)
    if not (speakerRepository == 'nan'):
        speaker_list = ([s.strip() for s in speakerRepository.split(";") if s.strip()])
    else:
        speaker_list = []

    for speaker in speaker_list:

        # new and improved unicity enforcer
        if speaker not in speaker_cache:
            speakersTable.insert({"name": speaker})

            result = speakersTable.select(
                columns=["id"],
                where={"name": speaker}
            )

            if result:
                speaker_cache[speaker] = result[0]["id"]

        speaker_id = speaker_cache.get(speaker)

        if speaker_id:
            eventSpeakersTable.insert({
                "event_id": event_id,
                "speaker_id": speaker_id
            })
    # id isn't set before inserting, so track it with an accumulator.
    order += 1