import sqlite3

connection = sqlite3.connect("data/aquarium.db")

rows = connection.execute(
    "SELECT id, filename, active FROM fishes"
).fetchall()

for row in rows:
    print(row)

connection.close()