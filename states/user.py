from aiogram.fsm.state import State, StatesGroup

class User(StatesGroup):
    name = State()
    worker_number = State()
    branch_name = State()
    complaint = State()
    is_complaint = State()
    another_complaint = State()