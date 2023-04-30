# This file is a part of FileStreamBot

import datetime
import math
from WebStreamer import __version__
from WebStreamer.bot import StreamBot
from WebStreamer.vars import Var
from WebStreamer.utils.Translation import Language, BUTTON
from WebStreamer.utils.database import Database
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.server.exceptions import FIleNotFound
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.file_id import FileId, FileType, PHOTO_TYPES
db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


deldbtnmsg=["Your Already Deleted the Link", "You can't undo the Action", "You can Resend the File to Regenerate New Link", "Why Clicking me Your Link is Dead", "This is Just a Button Showing that Your Link is Deleted"]

@StreamBot.on_callback_query()
async def cb_data(bot, update: CallbackQuery):
    lang = Language(update)
    usr_cmd = update.data.split("_")
    if usr_cmd[0] == "home":
        await update.message.edit_text(
            text=lang.START_TEXT.format(update.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=BUTTON.START_BUTTONS
        )
    elif usr_cmd[0] == "help":
        await update.message.edit_text(
            text=lang.HELP_TEXT.format(Var.UPDATES_CHANNEL),
            disable_web_page_preview=True,
            reply_markup=BUTTON.HELP_BUTTONS
        )
    elif usr_cmd[0] == "about":
        await update.message.edit_text(
            text=lang.ABOUT_TEXT.format(__version__),
            disable_web_page_preview=True,
            reply_markup=BUTTON.ABOUT_BUTTONS
        )
    elif usr_cmd[0] == "N/A":
        await update.answer("N/A", True)
    elif usr_cmd[0] == "close":
        await update.message.delete()
    # elif usr_cmd[0] == "msgdeleted":
    #     await update.answer(random.choice(deldbtnmsg), show_alert=True)
    elif usr_cmd[0] == "msgdelconf2":
        await update.message.edit_caption(
        caption= "<b>Do You Want to Delete the file<b>\n" + update.message.caption,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Yes", callback_data=f"msgdelyes_{usr_cmd[1]}_{usr_cmd[2]}"), InlineKeyboardButton("No", callback_data=f"myfile_{usr_cmd[1]}_{usr_cmd[2]}")]])
    )
    elif usr_cmd[0] == "msgdelyes":
        await delete_user_file(usr_cmd[1], int(usr_cmd[2]), update)
        return
    elif usr_cmd[0] == "userfiles":
        file_list, total_files = await gen_file_list_button(int(usr_cmd[1]), update.from_user.id)
        await update.message.edit_caption(
            caption="Total files: {}".format(total_files),
            reply_markup=InlineKeyboardMarkup(file_list)
            )
    elif usr_cmd[0] == "myfile":
        await gen_file_menu(usr_cmd[1], usr_cmd[2], update)
        return
    elif usr_cmd[0] == "accepttos":
        await db.agreed_tos(int(usr_cmd[1]))
        await update.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ I accepted the TOS", callback_data="N/A")]]))
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
                InlineKeyboardButton(f"{file_list_no}/{math.ceil(total_files/10)}", callback_data="N/A"),
                InlineKeyboardButton(">>", callback_data="{}".format("userfiles_"+str(file_list_no+1) if total_files > file_list_no*10 else 'N/A'))
            ]
    )
    if not file_list:
        file_list.append([InlineKeyboardButton("Empty", callback_data="N/A")])
    return file_list, total_files

async def gen_file_menu(_id, file_list_no, update: CallbackQuery):
    try:
        myfile_info=await db.get_file(_id)
    except FIleNotFound:
        await update.answer("File Not Found")
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

    page_link = f"{Var.URL}watch/{myfile_info['_id']}"
    stream_link = f"{Var.URL}dl/{myfile_info['_id']}"
    TiMe=myfile_info['time']
    if type(TiMe) == float:
        date = datetime.datetime.fromtimestamp(TiMe)
    await update.edit_message_caption(
        caption="Name: {}\nFile Size: {}\nType: {}\nCreated at: {}\nTime: {}".format(myfile_info['file_name'], humanbytes(int(myfile_info['file_size'])), file_type, TiMe if isinstance(TiMe, str) else date.date(), "N/A" if isinstance(TiMe, str) else date.time().strftime("%I:%M:%S %p %Z")),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Back", callback_data="userfiles_{}".format(file_list_no)), InlineKeyboardButton("Delete Link", callback_data=f"msgdelconf2_{myfile_info['_id']}_{file_list_no}")],
                [InlineKeyboardButton("🖥STREAM", url=page_link), InlineKeyboardButton("Dᴏᴡɴʟᴏᴀᴅ 📥", url=stream_link)]
            ]
            )
        )

async def delete_user_file(_id, file_list_no: int, update:CallbackQuery):

    try:
        myfile_info=await db.get_file(_id)
    except FIleNotFound:
        await update.answer("File Not Found")
        return

    await db.delete_one_file(myfile_info['_id'])
    await update.message.edit_caption(
            caption= "<b>Deleted Link Successfully<b>\n" + update.message.caption.replace("Do You Want to Delete the file", ""),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data=f"userfiles_1")]])
        )