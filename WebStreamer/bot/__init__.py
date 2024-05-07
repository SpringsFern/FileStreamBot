# This file is a part of FileStreamBot


from ..vars import Var
from telethon import Client

# if Var.SECONDARY:
#     plugins=None
#     no_updates=True
# else:    
#     plugins={"root": "WebStreamer/bot/plugins"}
#     no_updates=None

StreamBot = Client(
    session="WebStreamer",
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    flood_sleep_threshold=Var.SLEEP_THRESHOLD,
)

multi_clients = {}
work_loads = {}
