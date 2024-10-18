import json
import re
from aiogram.filters import Filter



def text_update(text, variables):
	#replace variables in the text with it value
	for var, new_val in variables.items():
		text = text.replace(var, new_val)
	return text



def reply_key(names: list,  row=1):
	from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
	from aiogram.types.keyboard_button import KeyboardButton
	keyboards = []
	for name in names:
		name = str(name)
		keyboards.append(KeyboardButton(text=name))
	keyboards = [keyboards[i:i+row] for i in range(0, len(keyboards), row)]
	markup = ReplyKeyboardMarkup(keyboard=keyboards, resize_keyboard=True)
	return markup


def get_inline(data, row=1):
	from aiogram.utils.keyboard import InlineKeyboardBuilder    ## Because when imported it runs module it takes less time if we import it here.

	builder = InlineKeyboardBuilder()
	for lan, call_data in data.items():
		builder.button(text=lan, callback_data=call_data)
	builder.adjust(row)
	return builder.as_markup()


def get_admins():
	with open("./data/data.json") as file:
		admins = json.load(file)["admins"]
	return admins

def add_admin(admin_id):
	with open("./data/data.json") as file:
		admin_data = json.load(file)

	admin_data["admins"].append(admin_id)
	
	with open("./data/data.json", "w") as file:
		json.dump(admin_data, file)

def get_user_lan_data():
	with open("./data/user_language.json") as file:
		user_language = json.load(file)
	return user_language

def add_user_language(user_id, language):
	user_language = get_user_lan_data()
	user_language[str(user_id)] = language

	with open("./data/user_language.json", "w") as file:
		json.dump(user_language, file)

def validate_phone_number(number):
	number = re.sub(pattern=r"\+|\-|\s", repl="", string=number)

	regex = r"^998([378]{2}|(9[013-57-9]))\d{7}$"  ##phone number regex pattern

	match_number = re.match(pattern=regex, string=number)
	if match_number:
		phone_number = match_number.group()
		return f"+{phone_number[0:5]} {phone_number[5:8]} {phone_number[8:10]} {phone_number[10:]}"  ##formating phone number
	return


def add_new_branch(branch_name):
	with open("./data/data.json") as file:
		data = json.load(file)

	data["branches"].append(branch_name)
	
	with open("./data/data.json", "w") as file:
		json.dump(data, file)


def get_admin_branch_data():
	with open("./data/data.json") as file:
		data = json.load(file)
	return data



def get_id_number():
	with open("./data/data.json") as file:
		data = json.load(file)
	
	last_id = data["id_count"]
	next_id = last_id + 1
	data["id_count"] = next_id

	with open("./data/data.json", "w") as file:
		json.dump(data, file)
	return next_id


def validate_date(time_data):
	regex = r"^\d{4}-\d{2}-\d{2}$"
	match_time = re.match(pattern=regex, string=time_data)
	if match_time:
		month = int(time_data.split("-")[1])
		day = int(time_data.split("-")[2])
		if month < 13 and day < 32:
			return match_time.group()
	return False


class CancelFilter(Filter):
	def __init__(self, languages) -> None:
		self.cancel_btns = [languages[lan]["cancel"] for lan in languages if lan != "languages"]

	async def __call__(self, message) -> bool:
		return message.text in self.cancel_btns