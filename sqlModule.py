import sqlite3

conn = sqlite3.connect('face_recog.db')

# initialize connection // jika table atau database belum ada maka akan dibuat
def init_connection():
    conn.execute("CREATE TABLE IF NOT EXISTS people(name VARCHAR , encoding TEXT)")

# get data face_recog
def get_people_encoding():
    cursor = conn.execute("SELECT name, encoding FROM people")
    return cursor

# menambahkan data
def insert_people_encoding(name, face_encode):
    encoding = ' '.join(str(e) for e in face_encode[0])
    conn.execute("INSERT INTO people (name, encoding) VALUES (?, ?)", (name, encoding))
    conn.commit()

# menghapus data
def delete_people_encoding(name):
    conn.execute("DELETE FROM people WHERE name = \"" + name + "\"")
    conn.commit()