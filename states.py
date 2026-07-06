from aiogram.fsm.state import State, StatesGroup

class RegisterStates(StatesGroup):
    full_name = State()
    xj_id = State()
    phone = State()
    gender = State()
    region = State()
    confirm = State()

class AdminStates(StatesGroup):
    set_limit = State()
    broadcast = State()
    search = State()
    delete = State()
    private_message = State()
    add_admin = State()
    remove_admin = State()

