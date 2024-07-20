# This file is a part of FileStreamBot

from __future__ import annotations
import sys
import glob
import importlib
from pathlib import Path
from aiohttp import web
from collections import defaultdict
from typing import Dict

from telethon.events import NewMessage, CallbackQuery
from WebStreamer.vars import Var

ongoing_requests: Dict[str, int] = defaultdict(lambda: 0)

ppath = "WebStreamer/bot/plugins/*.py"
files = glob.glob(ppath)

# https://github.com/EverythingSuckz/TG-FileStreamBot/blob/webui/WebStreamer/__main__.py

def load_plugins(path: str):
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"{path}/{plugin_name}.py")
            import_path = ".plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(
                import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["WebStreamer.bot.plugins." + plugin_name] = load
            print("Imported => " + plugin_name)

def get_requester_ip(req: web.Request) -> str:
    if Var.TRUST_HEADERS:
        try:
            return req.headers["X-Forwarded-For"].split(", ")[0]
        except KeyError:
            pass
    peername = req.transport.get_extra_info('peername')
    if peername is not None:
        return peername[0]

def allow_request(ip: str) -> None:
    return ongoing_requests[ip] < Var.REQUEST_LIMIT

def increment_counter(ip: str) -> None:
    ongoing_requests[ip] += 1

def decrement_counter(ip: str) -> None:
    ongoing_requests[ip] -= 1


# Moved from WebStreamer/utils/time_format.py
def get_readable_time(seconds: int) -> str:
    count = 0
    readable_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", " days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        readable_time += time_list.pop() + ", "
    time_list.reverse()
    readable_time += ": ".join(time_list)
    return readable_time

# moved from WebStreamer/utils/human_readable.py
def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

async def is_allowed(event: NewMessage.Event):
    if Var.ALLOWED_USERS and not (str(event.chat_id) in Var.ALLOWED_USERS):
        await event.message.reply(message="You are not in the allowed list of users who can use me.")
        return False
    return True

async def validate_user(event: NewMessage.Event | CallbackQuery.Event) -> bool:
    if isinstance(event, NewMessage.Event):
        if not event.is_private:
            return False
    if not await is_allowed(event):
        return False
    return True