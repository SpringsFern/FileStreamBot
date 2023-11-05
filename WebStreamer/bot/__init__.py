# This file is a part of FileStreamBot


from ..vars import Var
from pyrogram import Client

if Var.SECONDARY:
    plugins=None
    no_updates=True
else:    
    plugins={"root": "WebStreamer/bot/plugins"}
    no_updates=None

StreamBot = Client(
    name="WebStreamer",
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    workdir="WebStreamer",
    plugins=plugins,
    bot_token=Var.BOT_TOKEN,
    sleep_threshold=Var.SLEEP_THRESHOLD,
    workers=Var.WORKERS,
    no_updates=no_updates
)

multi_clients = {}
work_loads = {}
