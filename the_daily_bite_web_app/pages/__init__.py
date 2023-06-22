from the_daily_bite_web_app.route import Route

from .index import index
from .news import *

routes = [r for r in locals().values() if isinstance(r, Route)]
