import asyncio
from aiogram.types import FSInputFile
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram import Bot, types, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.filters.command import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
import json
from states import User, Admin
import functions as func
from config import ADMINS, ADMIN_PASSWORD, TOKEN
from data.database_setup import Database




# Initialize bot and dispatcher
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=storage)
db = Database()
db.create_tables()


#-----------Open files---------------------#
with open("./data/language.json") as file:
    languages = json.load(file)


with open("./data/data.json") as file:
    admin_branch_data = json.load(file)

user_info = func.get_user_lan_data()





#--------------------Start message------------------------#
@dp.message(CommandStart())
async def send_welcome(message: types.Message, state: FSMContext):
    global user_info
    user_id = str(message.from_user.id)
    hello_msg = languages["uz"]["hello_msg"]
    await message.reply(text=hello_msg, reply_markup=ReplyKeyboardRemove())

    user_language = message.from_user.language_code
    if user_id in user_info:
        user_language = user_info[user_id]
        ask_name = languages[user_language]["ask_name"]
        await message.answer(text=ask_name)
        await state.set_state(User.name)
        return
    elif user_language in languages:
        func.add_user_language(user_id=user_id, language=user_language)
        user_info = func.get_user_lan_data()
        ask_name = languages[user_language]["ask_name"]
        await message.answer(text=ask_name)
        await state.set_state(User.name)
        return
    

    await ask_change_language(message)


@dp.message(Command("cancel"))
@dp.message(func.CancelFilter(languages))
async def cancel(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_lan = user_info[user_id]

    await state.clear()
    # And remove keyboard (just in case)
    canceled_msg = languages[user_lan]["canceled"]
    await message.reply(text=canceled_msg, reply_markup=ReplyKeyboardRemove())




@dp.message(Command("language"))
async def ask_change_language(message: types.Message):
    ask_language = languages["ru"]["change_language"]
    language_btns = func.get_inline(languages["languages"], row=2)

    await message.answer(text=ask_language, reply_markup=language_btns)




#----------------------------check the admin----------------------------
@dp.message(lambda message: message.text == ADMIN_PASSWORD and message.chat.id in ADMINS)
async def checking_the_admin(message: types.Message):
    user_id = str(message.from_user.id)
    user_lan = user_info[user_id]

    admin_verified = languages[user_lan]["admin_verified"]

    add_admin_btn_data = languages[user_lan]["add_admin_btn"]
    add_admin_btn = func.get_inline(add_admin_btn_data, 2)

    await message.answer(text=admin_verified, reply_markup=add_admin_btn)



#-------------------------callback-queries---------------------------------#
#-------------------------------admin side----------------------------#
@dp.callback_query(F.data == "add_admin")
async def add_admin(call: types.CallbackQuery, state: FSMContext):
    user_id = str(call.message.chat.id)
    user_lan = user_info[user_id]
    ask_admin_id = languages[user_lan]["ask_admin_id"]


    await call.message.answer(text=ask_admin_id)
    await state.set_state(Admin.new_admin_id)


@dp.callback_query(F.data == "add_branch")
async def add_new_branch(call: types.CallbackQuery, state: FSMContext):
    user_id = str(call.message.chat.id)
    user_lan = user_info[user_id]
    
    ask_new_branch_msg = languages[user_lan]["ask_new_branch_name"]
    await call.message.answer(text=ask_new_branch_msg)
    await state.set_state(Admin.new_branch)



@dp.callback_query(F.data.startswith("change_lan_"))
async def change_language(call: types.CallbackQuery, state: FSMContext):
    global user_info
    user_lan_code = call.data.split("_")[-1]
    user_id = call.message.chat.id

    func.add_user_language(user_id=user_id, language=user_lan_code)

    user_info = func.get_user_lan_data()
    changed_success = languages[user_lan_code]["lan_changed_success"]
    await call.message.edit_text(changed_success)

    ask_start = languages[user_lan_code]["ask_to_start"]
    await call.message.answer(ask_start)



@dp.callback_query(F.data.startswith("reply_"))
async def reply_to_worker(call: types.CallbackQuery, state: FSMContext):
    user_id = str(call.message.chat.id)
    user_lan = user_info[user_id]
    worker_id = int(call.data.split("_")[-1])
    await call.message.reply(text=languages[user_lan]["ask_reply_text"])

    await state.update_data(reply_worker_id=worker_id)
    await state.set_state(Admin.reply_worker_id)



@dp.callback_query(F.data == "get_database")
async def get_database(call: types.CallbackQuery, state: FSMContext):
    user_id = str(call.message.chat.id)
    user_lan = user_info[user_id]

    ask_time_period = languages[user_lan]["ask_time_period"]
    time_period_btns = [1, 3, 6, 12]
    time_period_btns = func.reply_key(time_period_btns, 2)

    await call.message.answer(text=ask_time_period, reply_markup=time_period_btns)

    await state.set_state(Admin.get_database)



#----------------------------reply_keyboards----------------------------#
@dp.message(Admin.new_admin_id)
async def get_admin_id(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_lan = user_info[user_id]
    try:
        new_admin_id = int(message.text)
    except:
        error_message = languages[user_lan]["admin_id_wrong"]
        await message.reply(text=error_message)
        return

    ADMINS.append(new_admin_id)
    func.add_admin(new_admin_id)
    await message.reply(text=languages[user_lan]["admin_added"], reply_markup=ReplyKeyboardRemove())
    await state.clear()
    



@dp.message(F.text, User.name)
async def get_worker_name(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_lan = user_info[user_id]
    worker_name = message.text
    await state.update_data(name=worker_name)
    await state.set_state(User.worker_number)

    await message.answer(text=languages[user_lan]["ask_phone_number"])


@dp.message(F.text, User.worker_number)
async def get_worker_phone(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_lan = user_info[user_id]
    phone_number = message.text
    phone_number = func.validate_phone_number(phone_number)
    if not phone_number:
        await message.answer(text=languages[user_lan]["wrong_phone_number"])
        return

    await state.update_data(worker_number=phone_number)
    await state.set_state(User.branch_name)
    
    branches = admin_branch_data["branches"]
    branch_btns = func.reply_key(branches, row=2)
    await message.answer(text=languages[user_lan]["ask_branch"], reply_markup=branch_btns)


@dp.message(User.branch_name)
async def get_work_place(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_lan = user_info[user_id]
    branch_name = message.text
    await state.update_data(branch_name=branch_name)
    data = await state.get_data()
    user_name = data.get("name")
    worker_number = data.get("worker_number")

    ## if user not in database, add it
    if not db.check_user_exist(user_id=user_id):
        db.insert_user(user_id=user_id, username=user_name, phone_number=worker_number, branch=branch_name)
    await state.set_state(User.complaint)
    await message.answer(text=languages[user_lan]["ask_complaint"], reply_markup=ReplyKeyboardRemove())


@dp.message(User.complaint)
async def get_worker_complaint(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_lan = user_info[user_id]
    content_type = message.content_type
    worker_chat_id = message.chat.id
    

    data = await state.get_data()
    name = data.get("name")
    branch = data.get("branch_name")
    worker_number = data.get("worker_number")

    complaint_text = languages[user_lan]["complaint_text"]
    complaint_id = f"Id:  {func.get_id_number()}"  ##Complaint id
    complaint_data = {
        "id123": complaint_id,
        "worker123": name,
        "tel_num123": worker_number,
        "branch123": branch,
        "complaint123": ""
    }
    complaint_text = func.text_update(complaint_text, complaint_data)

    #sent complaint to admins
    if content_type == "text":
        complaint_text += message.text
        db.insert_complaint(user_id=user_id, complaint=message.text)   ##adding complaint into the database
        for admin in ADMINS:
            admin_lan = user_info[str(admin)]
            reply_worker_data = {
                languages[admin_lan]["reply_worker"]: f"reply_{worker_chat_id}"
            }
            reply_worker_btn = func.get_inline(reply_worker_data)
            await bot.send_message(chat_id=admin, text=complaint_text, reply_markup=reply_worker_btn)

    elif content_type == "audio":
        db.insert_complaint(user_id=user_id, complaint=complaint_id)
        file_id = message.audio.file_id
        for admin in ADMINS:
            admin_lan = user_info[str(admin)]
            reply_worker_data = {
                languages[admin_lan]["reply_worker"]: f"reply_{worker_chat_id}"
            }
            reply_worker_btn = func.get_inline(reply_worker_data)
            await bot.send_audio(chat_id=admin, audio=file_id, caption=complaint_text, reply_markup=reply_worker_btn)

    elif content_type == "video":
        db.insert_complaint(user_id=user_id, complaint=complaint_id)
        file_id = message.video.file_id
        for admin in ADMINS:
            admin_lan = user_info[str(admin)]
            reply_worker_data = {
                languages[admin_lan]["reply_worker"]: f"reply_{worker_chat_id}"
            }
            reply_worker_btn = func.get_inline(reply_worker_data)
            await bot.send_video(chat_id=admin, video=file_id, caption=complaint_text, reply_markup=reply_worker_btn)
    
    elif content_type == "photo":
        db.insert_complaint(user_id=user_id, complaint=complaint_id)
        file_id = message.photo[-1].file_id
        for admin in ADMINS:
            admin_lan = user_info[str(admin)]
            reply_worker_data = {
                languages[admin_lan]["reply_worker"]: f"reply_{worker_chat_id}"
            }
            reply_worker_btn = func.get_inline(reply_worker_data)
            await bot.send_photo(chat_id=admin, photo=file_id, caption=complaint_text, reply_markup=reply_worker_btn)

    elif content_type == "document":
        db.insert_complaint(user_id=user_id, complaint=complaint_id)
        file_id = message.document.file_id
        for admin in ADMINS:
            admin_lan = user_info[str(admin)]
            reply_worker_data = {
                languages[admin_lan]["reply_worker"]: f"reply_{worker_chat_id}"
            }
            reply_worker_btn = func.get_inline(reply_worker_data)
            await bot.send_document(chat_id=admin, document=file_id, caption=complaint_text, reply_markup=reply_worker_btn)

    elif content_type == "voice":
        db.insert_complaint(user_id=user_id, complaint=complaint_id)
        file_id = message.voice.file_id
        for admin in ADMINS:
            admin_lan = user_info[str(admin)]
            reply_worker_data = {
                languages[admin_lan]["reply_worker"]: f"reply_{worker_chat_id}"
            }
            reply_worker_btn = func.get_inline(reply_worker_data)
            await bot.send_voice(chat_id=admin, voice=file_id, caption=complaint_text, reply_markup=reply_worker_btn)

    elif content_type == "video_note":
        db.insert_complaint(user_id=user_id, complaint=complaint_id)
        file_id = message.video_note.file_id
        for admin in ADMINS:
            admin_lan = user_info[str(admin)]
            reply_worker_data = {
                languages[admin_lan]["reply_worker"]: f"reply_{worker_chat_id}"
            }
            reply_worker_btn = func.get_inline(reply_worker_data)
            video_note_message = await bot.send_video_note(chat_id=admin, video_note=file_id)
            await video_note_message.reply(text=complaint_text, reply_markup=reply_worker_btn)
    
    

    
    ask_another_complaint_btn = func.reply_key([languages[user_lan]["ask_another_complaint"]])
    await message.answer(text=languages[user_lan]["complaint_received"], reply_markup=ask_another_complaint_btn)
    await state.set_state(User.is_complaint)


another_complaint_btns = [languages[lan]["ask_another_complaint"] for lan in languages if lan != "languages"]
@dp.message(lambda message: message.text in another_complaint_btns, User.is_complaint)
async def is_there_another_complaint(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_lan = user_info[user_id]

    ask_complaint = languages[user_lan]["ask_complaint"]
    await message.answer(text=ask_complaint)
    await state.set_state(User.another_complaint)


@dp.message(User.another_complaint)
async def get_worker_complaint_again(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_lan = user_info[user_id]
    content_type = message.content_type
    worker_chat_id = message.chat.id
    

    data = await state.get_data()
    name = data.get("name")
    branch = data.get("branch_name")
    worker_number = data.get("worker_number")

    complaint_text = languages[user_lan]["complaint_text"]
    complaint_id = f"Id:  {func.get_id_number()}"  ##Complaint id
    complaint_data = {
        "id123": complaint_id,
        "worker123": name,
        "tel_num123": worker_number,
        "branch123": branch,
        "complaint123": ""
    }
    complaint_text = func.text_update(complaint_text, complaint_data)

    #sent complaint to admins
    if content_type == "text":
        complaint_text += message.text
        db.insert_complaint(user_id=user_id, complaint=message.text)   ##adding complaint into the database
        for admin in ADMINS:
            admin_lan = user_info[str(admin)]
            reply_worker_data = {
                languages[admin_lan]["reply_worker"]: f"reply_{worker_chat_id}"
            }
            reply_worker_btn = func.get_inline(reply_worker_data)
            await bot.send_message(chat_id=admin, text=complaint_text, reply_markup=reply_worker_btn)

    elif content_type == "audio":
        db.insert_complaint(user_id=user_id, complaint=complaint_id)
        file_id = message.audio.file_id
        for admin in ADMINS:
            admin_lan = user_info[str(admin)]
            reply_worker_data = {
                languages[admin_lan]["reply_worker"]: f"reply_{worker_chat_id}"
            }
            reply_worker_btn = func.get_inline(reply_worker_data)
            await bot.send_audio(chat_id=admin, audio=file_id, caption=complaint_text, reply_markup=reply_worker_btn)

    elif content_type == "video":
        db.insert_complaint(user_id=user_id, complaint=complaint_id)
        file_id = message.video.file_id
        for admin in ADMINS:
            admin_lan = user_info[str(admin)]
            reply_worker_data = {
                languages[admin_lan]["reply_worker"]: f"reply_{worker_chat_id}"
            }
            reply_worker_btn = func.get_inline(reply_worker_data)
            await bot.send_video(chat_id=admin, video=file_id, caption=complaint_text, reply_markup=reply_worker_btn)
    
    elif content_type == "photo":
        db.insert_complaint(user_id=user_id, complaint=complaint_id)
        file_id = message.photo[-1].file_id
        for admin in ADMINS:
            admin_lan = user_info[str(admin)]
            reply_worker_data = {
                languages[admin_lan]["reply_worker"]: f"reply_{worker_chat_id}"
            }
            reply_worker_btn = func.get_inline(reply_worker_data)
            await bot.send_photo(chat_id=admin, photo=file_id, caption=complaint_text, reply_markup=reply_worker_btn)

    elif content_type == "document":
        db.insert_complaint(user_id=user_id, complaint=complaint_id)
        file_id = message.document.file_id
        for admin in ADMINS:
            admin_lan = user_info[str(admin)]
            reply_worker_data = {
                languages[admin_lan]["reply_worker"]: f"reply_{worker_chat_id}"
            }
            reply_worker_btn = func.get_inline(reply_worker_data)
            await bot.send_document(chat_id=admin, document=file_id, caption=complaint_text, reply_markup=reply_worker_btn)

    elif content_type == "voice":
        db.insert_complaint(user_id=user_id, complaint=complaint_id)
        file_id = message.voice.file_id
        for admin in ADMINS:
            admin_lan = user_info[str(admin)]
            reply_worker_data = {
                languages[admin_lan]["reply_worker"]: f"reply_{worker_chat_id}"
            }
            reply_worker_btn = func.get_inline(reply_worker_data)
            await bot.send_voice(chat_id=admin, voice=file_id, caption=complaint_text, reply_markup=reply_worker_btn)

    elif content_type == "video_note":
        db.insert_complaint(user_id=user_id, complaint=complaint_id)
        file_id = message.video_note.file_id
        for admin in ADMINS:
            admin_lan = user_info[str(admin)]
            reply_worker_data = {
                languages[admin_lan]["reply_worker"]: f"reply_{worker_chat_id}"
            }
            reply_worker_btn = func.get_inline(reply_worker_data)
            video_note_message = await bot.send_video_note(chat_id=admin, video_note=file_id)
            await video_note_message.reply(text=complaint_text, reply_markup=reply_worker_btn)
    
    await message.answer(text=languages[user_lan]["complaint_received"])
    await state.set_state(User.is_complaint)


@dp.message(Admin.reply_worker_id)
async def reply_worker(message: types.Message, state: FSMContext):
    reply_text = message.text
    data = await state.get_data()
    worker_chat_id = data.get("reply_worker_id")

    await bot.send_message(chat_id=worker_chat_id, text=reply_text)
    await message.reply("\u2705\u2705")
    await state.clear()



@dp.message(Admin.new_branch)
async def get_new_branch_name(message: types.Message, state: FSMContext):
    global admin_branch_data
    new_branch_name = message.text

    func.add_new_branch(new_branch_name)
    admin_branch_data = func.get_admin_branch_data()  ## update the branches


    await message.reply(text="\u2705\u2705")
    await state.clear()


@dp.message(Admin.get_database)
async def send_complaint_data(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    months = message.text
    if months.isdigit():
        months = int(months)
        data = db.select_complaints(months=months)
    elif func.validate_date(time_data=months):
        custom_date = func.validate_date(time_data=months)
        data = db.select_complaints(custom_time=custom_date)
    else:
        return

    data.to_csv("./data/complaints.csv")
    complaints = FSInputFile("./data/complaints.csv")
    await bot.send_document(chat_id=user_id, document=complaints)

async def main() -> None:
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())