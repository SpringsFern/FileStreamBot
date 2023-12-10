# eval and exec ..py

import logging
import io
import os
import sys
import traceback
from WebStreamer.bot import StreamBot
from pyrogram import filters
from pyrogram.types import Message

from WebStreamer.vars import Var


MAX_MESSAGE_LENGTH = 4096
FREE_USER_MAX_FILE_SIZE = 2097152000

@StreamBot.on_message(filters.private & filters.user(Var.OWNER_ID) & filters.command("eval"))
async def eval_handler(bot, message: Message):
    status_message = await message.reply_text("Processing ...")
    cmd = message.text.split(" ", maxsplit=1)[1]
    reply_to_id = message.id
    if message.reply_to_message:
      reply_to_id = message.reply_to_message.id
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
  
    try:
      await aexec(cmd, bot, message)
    except Exception:
      exc = traceback.format_exc()
        
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
  
    evaluation = ""
    if exc:
      evaluation = exc
    elif stderr:
      evaluation = stderr
    elif stdout:
      evaluation = stdout
    else:
      evaluation = "Success"
  
    final_output = (
      "<b>EVAL</b>: <code>{}</code>\n\n<b>OUTPUT</b>:\n<code>{}</code> \n".format(
        cmd, evaluation.strip()
      )
    )
      
          
  
    if len(final_output) > MAX_MESSAGE_LENGTH:
      with open("eval.text", "w+", encoding="utf8") as out_file:
        out_file.write(str(final_output))
        await message.reply_document(
          document="eval.text",
          caption=cmd,
          disable_notification=True,
          reply_to_message_id=reply_to_id,
        )
        os.remove("eval.text")
        await status_message.delete()
    else:
      await status_message.edit(final_output)
        
        
async def aexec(code, bot, message):
  exec(
    f"async def __aexec(bot, message): "
    + "".join(f"\n {l}" for l in code.split("\n"))
  )
  return await locals()["__aexec"](bot, message)