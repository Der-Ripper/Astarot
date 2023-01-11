from aiogram.dispatcher.filters.state import StatesGroup, State


class BotStates(StatesGroup):
    encrypt_state = State()
    encrypt_key_state = State()
    decrypt_state = State()
    decrypt_key_state = State()
    extract_audio_state = State()
    extract_meta_state = State()
    extract_text_state = State()
    extract_text_lang_state = State()
    crack_password_state = State()
    crack_password_dict_state = State()
    crack_password_bottom_state = State()
    crack_password_up_state = State()
    translation_state = State()
    translation_lang_state = State()
