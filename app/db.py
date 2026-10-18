from flask import current_app, g
import sqlite3

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
        


def get_all_recipes_rows():
    rows = get_db().execute("SELECT * FROM recipes ORDER BY id").fetchall()
    return rows


