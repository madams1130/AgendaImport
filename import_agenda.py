from db_table import db_table 
import pandas as pd
import sys

def clean(val):
    return str(val).replace("'", "''")

bigTable = pd.read_excel(sys.argv[1], engine="xlrd", skiprows=14)

parsedAgenda = db_table("Agenda", {
    "id": "integer PRIMARY KEY AUTOINCREMENT",
    "date": "text",
    "time_start": "text",
    "time_end": "text",
    "session_type": "text",
    "title": "text",
    "location": "text",
    "description": "text",
    "speaker": "text"
})

colNames = list(bigTable.columns)
trickyCols = colNames[0:4]

bigTable = bigTable[bigTable[str(colNames[0])] != str(colNames[0])]
bigTable = bigTable[bigTable[str(colNames[1])] != str(colNames[1])]
bigTable = bigTable[bigTable[str(colNames[2])] != str(colNames[2])]
bigTable = bigTable[bigTable[str(colNames[3])] != str(colNames[3])]
bigTable = bigTable[bigTable[str(colNames[4])] != str(colNames[4])]

for _, row in bigTable.iterrows():
    parsedAgenda.insert({
        "date": clean(row[str(colNames[0])]),
        "time_start": clean(row[str(colNames[1])]),
        "time_end": clean(row[str(colNames[2])]),
        "session_type": clean(row[str(colNames[3])]),
        "title": clean(row[str(colNames[4])]),
        "location": clean(row[str(colNames[5])]),
        "description": clean(row[str(colNames[6])]),
        "speaker": clean(row[str(colNames[7])])
    })

rows = parsedAgenda.select(columns=["id", "date", "time_start", "time_end", "type"])

for row in rows:
    print(row)

#print(colNames)