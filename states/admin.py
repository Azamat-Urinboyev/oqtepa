from aiogram.fsm.state import State, StatesGroup

class Admin(StatesGroup):
    new_admin_id = State()
    reply_worker_id = State()
    new_branch = State()
    get_database = State()