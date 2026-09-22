import sqlite3

connection = sqlite3.connect("data/aquarium.db")

connection.execute("DELETE FROM fishes")

connection.commit()

print("Все рыбки удалены из базы данных.")

connection.close()