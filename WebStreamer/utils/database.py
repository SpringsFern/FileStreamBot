# This file is a part of FileStreamBot

import pymongo
import time
import motor.motor_asyncio
from bson.objectid import ObjectId
from bson.errors import InvalidId
from WebStreamer.server.exceptions import FIleNotFound

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.black = self.db.blacklist
        self.file = self.db.file

# ----------------------add ,check or remove user----------------------
    def new_user(self, id):
        return dict(
            id=id,
            join_date=time.time(),
            agreed_to_tos=False,
            Links=0,
            Plan="Free"
        )

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def get_user(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def agreed_tos(self, user_id):
        await self.col.update_one(
            {"id": int(user_id)},
            {"$set": {
                "agreed_to_tos": True,
                "when_agreed_to_tos": time.time()
                }
            }
        )

# ----------------------ban, check banned or unban user----------------------
    def black_user(self, id):
        return dict(
            id=id,
            ban_date=time.time()
        )

    async def ban_user(self, id):
        user = self.black_user(id)
        await self.black.insert_one(user)

    async def unban_user(self, id):
        await self.black.delete_one({'id': int(id)})

    async def is_user_banned(self, id):
        user = await self.black.find_one({'id': int(id)})
        return True if user else False

    async def total_banned_users_count(self):
        count = await self.black.count_documents({})
        return count
        
# --------------------------------------------------------
    async def add_file(self, file_info):
        file_info["time"]=time.time()
        fetch_old = await self.get_file_by_fileuniqueid(file_info["user_id"], file_info["file_unique_id"])
        if fetch_old:
            return fetch_old
        await self.count_links(file_info["user_id"], "+")
        return (await self.file.insert_one(file_info)).inserted_id

    async def find_files(self, user_id, range):
        user_files=self.file.find({"user_id": user_id})
        user_files.skip(range[0] - 1)
        user_files.limit(range[1] - range[0] + 1)
        user_files.sort('_id', pymongo.DESCENDING)
        total_files = await self.file.count_documents({"user_id": user_id})
        return user_files, total_files

    async def get_file(self, _id):
        try:
            file_info=await self.file.find_one({"_id": ObjectId(_id)})
            if not file_info:
                raise FIleNotFound
            return file_info
        except InvalidId:
            raise FIleNotFound
    
    async def get_file_by_fileuniqueid(self, id, file_unique_id):
        file_info=await self.file.find_one({"user_id": id, "file_unique_id": file_unique_id})
        if file_info:
            return file_info["_id"]
        return False

    async def total_files(self):
        return await self.file.count_documents({})

    async def delete_one_file(self, _id):
        await self.file.delete_one({'_id': ObjectId(_id)})

    async def update_file_ids(self, _id, file_ids: dict):
        await self.file.update_one({"_id": ObjectId(_id)}, {"$set": {"file_ids": file_ids}})

    async def link_available(self, id):
        user = await self.col.find_one({"id": id})
        if user.get("Plan") == "Free":
            if user.get("Links") < 16:
                return True
            return False
        
    async def count_links(self, id, operation: str):
        if operation == "-":
            await self.col.update_one({"id": id}, {"$inc": {"Links": -1}})
        elif operation == "+":
            await self.col.update_one({"id": id}, {"$inc": {"Links": 1}})