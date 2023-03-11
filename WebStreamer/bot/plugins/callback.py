# This file is a part of FileStreamBot

import random
from WebStreamer.bot import StreamBot
from WebStreamer.utils.file_properties import gen_link, get_media_file_unique_id
from WebStreamer.vars import Var
from WebStreamer.utils.Translation import Language, BUTTON
from WebStreamer.utils.database import Database
from WebStreamer.utils.human_readable import humanbytes
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMedia, InputMediaPhoto
from pyrogram.errors import MessageDeleteForbidden
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.file_id import FileId, FileType, PHOTO_TYPES
db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


deldbtnmsg=["Your Already Deleted the Link", "You can't undo the Action", "You can Resend the File to Regenerate New Link", "Why Clicking me Your Link is Dead", "This is Just a Button Showing that Your Link is Deleted"]

@StreamBot.on_callback_query()
async def cb_data(bot, update: CallbackQuery):
    lang = Language(update)
    if update.data == "home":
        await update.message.edit_text(
            text=lang.START_TEXT.format(update.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=BUTTON.START_BUTTONS
        )
    elif update.data == "help":
        await update.message.edit_text(
            text=lang.HELP_TEXT.format(Var.UPDATES_CHANNEL),
            disable_web_page_preview=True,
            reply_markup=BUTTON.HELP_BUTTONS
        )
    elif update.data == "about":
        await update.message.edit_text(
            text=lang.ABOUT_TEXT,
            disable_web_page_preview=True,
            reply_markup=BUTTON.ABOUT_BUTTONS
        )
    elif update.data == "N/A":
        await update.answer("N/A", True)
    elif update.data == "close":
        await update.message.delete()
    elif update.data == "msgdeleted":
        await update.answer(random.choice(deldbtnmsg), show_alert=True)
    else:
        usr_cmd = update.data.split("_")
        if usr_cmd[0] == "msgdelconf2":
            await update.message.edit_caption(
            caption= "<b>Do You Want to Delete the file<b>\n" + update.message.caption,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Yes", callback_data=f"msgdelyes_{usr_cmd[1]}"), InlineKeyboardButton("No", callback_data=f"myfile_{usr_cmd[1]}_{usr_cmd[2]}")]])
        )
        elif usr_cmd[0] == "msgdelyes":
            await update.answer("Comming Soon", show_alert=True)
            return
            try:
                resp = await bot.get_messages(Var.BIN_CHANNEL, int(usr_cmd[1]))
                if get_media_file_unique_id(resp) == usr_cmd[2]:
                    await bot.delete_messages(
                        chat_id=Var.BIN_CHANNEL,
                        message_ids=int(usr_cmd[1])
                    )
                    await update.message.edit_text(
                    text=update.message.text,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Link Deleted", callback_data="msgdeleted")]])
                    )
                elif resp.empty:
                    await update.answer("Sorry Your File is Missing from the Server", show_alert=True)
                else:
                    await update.answer("Message id and file_unique_id miss match", show_alert=True)
            except MessageDeleteForbidden as e:
                print(e)
                await bot.send_message(
                    chat_id=Var.BIN_CHANNEL,
                    text=f"**#ᴇʀʀᴏʀ_ᴛʀᴀᴄᴇʙᴀᴄᴋ:** `{e}`\n#Delete_Link", disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN,
                )
                await update.answer(text='message too old', show_alert=True)
            except Exception as e:
                print(e)
                error_id=await bot.send_message(
                    chat_id=Var.BIN_CHANNEL,
                    text=f"**#ᴇʀʀᴏʀ_ᴛʀᴀᴄᴇʙᴀᴄᴋ:** `{e}`\n#Delete_Link", disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN,
                )
                await update.message.reply_text(
                    text=f"**#ᴇʀʀᴏʀ_ᴛʀᴀᴄᴇʙᴀᴄᴋ:** `message-id={error_id.message_id}`\nYou can get Help from [Public Link Generator (Support)](https://t.me/{Var.UPDATES_CHANNEL})", disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN,
                )
        elif usr_cmd[0] == "userfiles":
            file_list = await gen_file_list_button(int(usr_cmd[1]), update.from_user.id)
            await update.message.edit_caption(
                caption=update.message.caption,
                reply_markup=InlineKeyboardMarkup(file_list)
                )
        elif usr_cmd[0] == "myfile":
            await gen_file_menu(usr_cmd[1], usr_cmd[2], update)
            return

        else:
            await update.message.delete()

async def gen_file_list_button(file_list_no: int, user_id: int):

    file_range=[file_list_no*10-10+1, file_list_no*10]
    user_files, total_files=await db.find_files(user_id, file_range)

    file_list=[]
    async for x in user_files:
        file_list.append([InlineKeyboardButton(x["file_name"], callback_data=f"myfile_{x['_id']}_{file_list_no}")])
    if total_files > 10:
        file_list.append(
            [
                InlineKeyboardButton("<<", callback_data="{}".format("userfiles_"+str(file_list_no-1) if file_list_no > 1 else 'N/A')),
                InlineKeyboardButton(file_list_no, callback_data="N/A"),
                InlineKeyboardButton(">>", callback_data="{}".format("userfiles_"+str(file_list_no+1) if total_files > file_list_no*10 else 'N/A'))
            ]
    )
    return file_list

async def gen_file_menu(_id, file_list_no, update: CallbackQuery):
    myfile_info=await db.get_file(_id)
    get_msg = await update._client.get_messages(chat_id=Var.BIN_CHANNEL, message_ids=int(myfile_info['msg_id']))
    
    if not get_media_file_unique_id(get_msg) == myfile_info['file_unique_id']:
        await update.answer("Sorry Your File is Missing from the Server", show_alert=True)
        return

    file_id=FileId.decode(myfile_info['file_id'])

    if file_id.file_type in PHOTO_TYPES:
        file_type="Photo"
    elif file_id.file_type == FileType.VOICE:
        file_type="Voice"
    elif file_id.file_type in (FileType.VIDEO, FileType.ANIMATION, FileType.VIDEO_NOTE):
        file_type="Video"
    elif file_id.file_type == FileType.DOCUMENT:
        file_type="Document"
    elif file_id.file_type == FileType.STICKER:
        file_type="Sticker"
    elif file_id.file_type == FileType.AUDIO:
        file_type="Audio"
    else:
        file_type = "Unknown"

    page_link = f"{Var.URL}watch/{(myfile_info['file_unique_id'])[:6]}{myfile_info['msg_id']}"
    stream_link = f"{Var.URL}{(myfile_info['file_unique_id'])[:6]}{myfile_info['msg_id']}"
    await update.edit_message_caption(
        caption="Name: {}\nFile Size: {}\nType: {}\nCreated at: {}".format(myfile_info['file_name'], humanbytes(int(myfile_info['file_size'])), file_type, myfile_info['time']),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Back", callback_data="userfiles_{}".format(file_list_no)), InlineKeyboardButton("Delete Link", callback_data=f"msgdelconf2_{myfile_info['_id']}_{file_list_no}")],
                [InlineKeyboardButton("🖥STREAM", url=page_link), InlineKeyboardButton("Dᴏᴡɴʟᴏᴀᴅ 📥", url=stream_link)]
            ]
            )
        )
    