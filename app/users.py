

def get_user_by_id(db, user_id):
    return db.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()