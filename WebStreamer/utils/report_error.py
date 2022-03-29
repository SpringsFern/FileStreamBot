# (c) DeekshithSH

# import traceback
# from pyrogram import Client
# from pyrogram.types import Message
# from WebStreamer.vars import Var

# async def send_error(bot: Client, error, critical = False):
#     if Var.ERROR_CHANNEL:
#         if isinstance(error, Exception) and critical:
#             error=str(traceback.format_exc())
#         else:
#             error=str(error)
#         if len(error) > 4096:
#             for x in range(0, len(error), 4096):
#                 msg=await bot.send_message(Var.ERROR_CHANNEL, error[x:x+4096])
#         else:
#             msg=await bot.send_message(Var.ERROR_CHANNEL, error)
#     else:
#         if critical:
#             msg=await bot.send_message(Var.BIN_CHANNEL, error)
#     return msg