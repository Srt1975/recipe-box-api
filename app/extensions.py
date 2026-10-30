from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


migrate = Migrate()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)

def init_limiter(app):
    limiter.init_app(app)