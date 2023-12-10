# This file is a part of FileStreamBot

import pymongo
import time
import motor.motor_asyncio
from bson.objectid import ObjectId
from bson.errors import InvalidId
from WebStreamer.server.exceptions import FIleNotFound
from WebStreamer.vars import Var

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.black = self.db.blacklist
        self.file = self.db.file

# ----------[Add user]----------
    def new_user(self, id):
        return dict(
            id=id,
            join_date=time.time(),
            agreed_to_tos=False,
            Plan="Free"
        )

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

# ----------[User Info]----------
    async def get_user(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user

# ----------[User Count]----------
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

# ----------[User List]----------
    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

# ----------[Remove User]----------
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

# ----------[User Accept to TOS]----------
    async def agreed_tos(self, user_id):
        await self.col.update_one(
            {"id": int(user_id)},
            {"$set": {
                "agreed_to_tos": True,
                "when_agreed_to_tos": time.time()
                }
            }
        )

# ----------[Ban User]----------
    def black_user(self, id):
        return dict(
            id=id,
            ban_date=time.time()
        )

    async def ban_user(self, id):
        user = self.black_user(id)
        await self.black.insert_one(user)
        await self.delete_user(id)

# ----------[Unban User]----------
    async def unban_user(self, id):
        await self.black.delete_one({'id': int(id)})

# ----------[Check User is Banned]----------
    async def is_user_banned(self, id):
        user = await self.black.find_one({'id': int(id)})
        return True if user else False

# ----------[Banned User Count]----------
    async def total_banned_users_count(self):
        count = await self.black.count_documents({})
        return count
        
# ----------[Add File]----------
    async def add_file(self, file_info):
        file_info["time"]=time.time()
        fetch_old = await self.get_file_by_fileuniqueid(file_info["user_id"], file_info["file_unique_id"])
        if fetch_old:
            return fetch_old["_id"]
        return (await self.file.insert_one(file_info)).inserted_id

# ----------[User File List]----------
    async def find_files(self, user_id, range):
        user_files=self.file.find({"user_id": user_id})
        user_files.skip(range[0] - 1)
        user_files.limit(range[1] - range[0] + 1)
        user_files.sort('_id', pymongo.DESCENDING)
        total_files = await self.file.count_documents({"user_id": user_id})
        return user_files, total_files

# ----------[Get one File]----------
    async def get_file(self, _id):
        try:
            file_info=await self.file.find_one({"_id": ObjectId(_id)})
            if not file_info:
                raise FIleNotFound
            return file_info
        except InvalidId:
            raise FIleNotFound
    
# ----------[Get File Using File Unique ID]----------
    async def get_file_by_fileuniqueid(self, id, file_unique_id, many=False):
        if many:
            return self.file.find({"file_unique_id": file_unique_id})
        else:
            file_info=await self.file.find_one({"user_id": id, "file_unique_id": file_unique_id})
        if file_info:
            return file_info
        return False

# ----------[Total File Count]----------
    async def total_files(self, id=None):
        if id:
            return await self.file.count_documents({"user_id": id})
        return await self.file.count_documents({})

# ----------[Delete File]----------
    async def delete_one_file(self, _id):
        await self.file.delete_one({'_id': ObjectId(_id)})

# ----------[Update FileID List]----------
    async def update_file_ids(self, _id, file_ids: dict):
        await self.file.update_one({"_id": ObjectId(_id)}, {"$set": {"file_ids": file_ids}})

# ----------[Links Left]----------
    async def link_available(self, id):
        if not Var.LINK_LIMIT:
            return True
        user = await self.col.find_one({"id": id})
        if user.get("Plan") == "Plus":
            return "Plus"
        elif user.get("Plan") == "Free":
            files = await self.file.count_documents({"user_id": id})
            if files <= Var.LINK_LIMIT:
                return True
            return False