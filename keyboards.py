from aiogram import types


def get_base_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="Passwords", callback_data="Password"),
            types.InlineKeyboardButton(text="Extraction", callback_data="Extract")
        ],
        [
            types.InlineKeyboardButton(text="Translation", callback_data="Translation"),
            types.InlineKeyboardButton(text="Cryptography", callback_data="Crypto")
        ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def get_empty_keyboard():
    buttons = [[types.InlineKeyboardButton(text="Menu", callback_data="Menu")]]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def get_translation_keyboard():
    languages = ['Russian', 'German', 'Modern Greek (1453-)', 'Esperanto', 'Spanish', 'Estonian', 'Finnish', 'French',
                 'Irish', 'Scottish Gaelic', 'Hindi', 'Hmong', 'Croatian', 'Italian', 'Hebrew', 'Japanese', 'Korean',
                 'Latvian', 'Norwegian', 'Polish', 'Serbian', 'Swedish', 'Turkish', 'Chinese']
    buttons = [[], [], [], [], [], [], [types.InlineKeyboardButton(text="Menu", callback_data="Menu")]]
    for i in range(6):
        for j in range(4):
            buttons[i].append(types.InlineKeyboardButton(text=languages[4*i + j],
                                                         callback_data="lang_"+languages[4*i + j]))

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def get_auto_crack_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="Pick up password", callback_data="Pick up")
        ],
        [
            types.InlineKeyboardButton(text="Menu", callback_data="Menu")
         ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def get_crypto_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="Encrypt", callback_data="Encrypt"),
            types.InlineKeyboardButton(text="Decrypt", callback_data="Decrypt")
        ],
        [
            types.InlineKeyboardButton(text="Menu", callback_data="Menu")
         ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def get_extract_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="Extract audio", callback_data="Extract audio")
        ],
        [
            types.InlineKeyboardButton(text="Extract meta", callback_data="Extract meta")
        ],
        [
            types.InlineKeyboardButton(text="Extract text", callback_data="Extract text")
        ],
        [
            types.InlineKeyboardButton(text="Menu", callback_data="Menu")
         ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def get_password_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="Crack password", callback_data="Crack password")
        ],
        [
            types.InlineKeyboardButton(text="Menu", callback_data="Menu")
         ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
