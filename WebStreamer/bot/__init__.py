# This file is a part of FileStreamBot


from ..vars import Var
from .helper import TLClient

StreamBot = TLClient(
    session="WebStreamer",
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    flood_sleep_threshold=Var.SLEEP_THRESHOLD,
    receive_updates=not Var.NO_UPDATE
)

multi_clients = {}
work_loads = {}
