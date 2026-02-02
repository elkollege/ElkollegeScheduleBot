import aiogram.fsm.state


class States(aiogram.fsm.state.StatesGroup):
    upload_schedule = aiogram.fsm.state.State()
    upload_substitutions = aiogram.fsm.state.State()
