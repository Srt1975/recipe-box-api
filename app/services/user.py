
from app.users import get_user_by_id


def fetch_user(db, user_id):
    user = get_user_by_id(db, user_id)
    if user is None:
        return None
    return user