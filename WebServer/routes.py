import pathlib

from aiohttp import web

from WebServer.main.views import index, FileHandler, status

PROJECT_PATH = pathlib.Path(__file__).parent


def init_routes(app: web.Application) -> None:
    add_route = app.router.add_route

    add_route('get', '/status', status)
    add_route('*', '/', index, name='index')
    add_route("get", "/dl/{ObjectID}", FileHandler)

