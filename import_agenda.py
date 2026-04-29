#!/usr/bin/env python3

from db_table import db_table 
import pandas as pd
import sys

def clean(val):
    return str(val).replace("'", "''")
try:
    bigTable = pd.read_excel(sys.argv[1], engine="xlrd", skiprows=14)
except IndexError:
    print("Input Structure: ./import_agenda.py agenda.xls <table.xls>")
    exit(1)
except: 
    print("Unrecognized Table.")
    exit(1)

# fun fact: I learned SQL in Paris, and had to google how some concepts translated to English!

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

colNames = list(bigTable.columns)

bigTable = bigTable[bigTable[str(colNames[0])] != str(colNames[0])]
bigTable = bigTable[bigTable[str(colNames[1])] != str(colNames[1])]
bigTable = bigTable[bigTable[str(colNames[2])] != str(colNames[2])]
bigTable = bigTable[bigTable[str(colNames[3])] != str(colNames[3])]
bigTable = bigTable[bigTable[str(colNames[4])] != str(colNames[4])]

speaker_list = []

# dictionary! avoid selecting while writing (SQLite doesn't like that)
speaker_cache = {}

for _, row in bigTable.iterrows():
    event_id = event_info.insert({
        "date": clean(row[str(colNames[0])]),
        "time_start": clean(row[str(colNames[1])]),
        "time_end": clean(row[str(colNames[2])]),
        "session_type": clean(row[str(colNames[3])]),
        "title": clean(row[str(colNames[4])]),
        "location": clean(row[str(colNames[5])]),
        "description": clean(row[str(colNames[6])])
    })

    # get raw speakers string
    speakerRepository = clean(row["Speakers"])

    # turn into "mini-array" w/ semicolon delimiters
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

#rows = speakersTable.select(columns=["id", "name"])

#print(speaker_list)

#for row in rows:
#    print(row)

#print(colNames)