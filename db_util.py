import sqlite3


def create_tables(dbfile):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    c.execute((
        'CREATE TABLE IF NOT EXISTS devices ('
        'id INTEGER PRIMARY KEY,'
        'name TEXT,'
        'group_code TEXT,'
        'device_code TEXT)'
    ))

    c.close()
    conn.commit()
    conn.close()
