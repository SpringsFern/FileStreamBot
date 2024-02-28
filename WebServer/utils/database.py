# This file is a part of FileStreamBot

import motor.motor_asyncio
import datetime
from bson.objectid import ObjectId
from bson.errors import InvalidId
from WebServer.utils.vars import Var

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.file = self.db.file
        self.dl = self.db.dl

    async def create_link(self, id):
        file_info = await self.dl.find_one({"id": id})
        if file_info:
            return Var.DL_URL+"dl/"+str(file_info["_id"])
        dl_id=ObjectId()
        await self.dl.insert_one({"_id":dl_id, "CreatedAt": datetime.datetime.utcnow(), "id" : id})
        await self.file.update_one({"_id": id}, {"$set": {"dl_id": dl_id}})
        return Var.DL_URL+"dl/"+str(dl_id)

        # await self.file.createIndex({"CreatedAt": datetime.datetime.now().isoformat()}, {"expireAfterSeconds":86400})
    
    async def get_file(self, _id):
        if isinstance(_id, str):
            _id=ObjectId(_id)
        try:
            file_info=await self.file.find_one({"_id": _id})
            if not file_info:
                return None
            return file_info
        except InvalidId:
            return None