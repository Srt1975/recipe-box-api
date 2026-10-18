"""Create and seed recipes.db. Run once after cloning: python init_db.py"""
from app.db import get_db
import sqlite3
from app import create_app # or import get_db via app

SCHEMA = """
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL DEFAULT '',
    is_public INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);
"""

SEED = [
    (
        "Shakshuka",
        "eggs, tomatoes, peppers, onion, cumin, paprika",
        "Simmer the sauce, crack in the eggs, cover until just set.",
        1,
    ),
    (
        "Overnight oats",
        "rolled oats, milk, yogurt, chia seeds, honey",
        "Stir everything together and refrigerate overnight.",
        1,
    ),
    (
        "Secret family hot sauce",
        "habaneros, garlic, vinegar, a secret ingredient",
        "If we wrote it down here, it wouldn't be a secret.",
        0,
    ),
]

def init_db(app):
    with app.app_context():
        db = get_db()
        db.executescript(SCHEMA)
        existing = db.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
        if existing == 0:
            db.executemany(
                "INSERT INTO recipes (title, ingredients, instructions, is_public)"
                " VALUES (?, ?, ?, ?)",
                SEED,
            )
            db.commit()
            print(f"Created {app.config['DATABASE']} and seeded {len(SEED)} recipes.")
        else:
            print(f"{app.config['DATABASE']} already has {existing} recipes - nothing to do.")

def main():
    app = create_app("development")
    init_db(app)

if __name__ == "__main__":
    main()
    
