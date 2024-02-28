
import logging
import sys

from aiohttp import web

from WebServer.utils.vars import Var

from .app import init_app

logging.basicConfig(
    level=logging.DEBUG if Var.DEBUG else logging.INFO,
    datefmt="%d/%m/%Y %H:%M:%S",
    format="[%(asctime)s][%(name)s][%(levelname)s] ==> %(message)s",
    handlers=[logging.StreamHandler(stream=sys.stdout),
              logging.FileHandler("webui.log", mode="a", encoding="utf-8")],)

logging.getLogger("aiohttp").setLevel(logging.DEBUG if Var.DEBUG else logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.DEBUG if Var.DEBUG else logging.ERROR)

def create_app() -> web.Application:
    import aiohttp_debugtoolbar

    app = init_app()
    aiohttp_debugtoolbar.setup(app, check_host=False)

    return app


def main() -> None:
    app = init_app()
    app_settings = app['config']['app']
    web.run_app(
        app,
        host=app_settings['host'],
        port=int(Var.PORT) if Var.PORT else app_settings['port'],
    )


if __name__ == '__main__':
    main()
