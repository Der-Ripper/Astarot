from aiogram.dispatcher.filters import Text
from config.configure import BOT_TOKEN, TESSERACT_PATH
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import shutil
import pyAesCrypt
import moviepy.editor
import pytesseract
from PIL import Image, ExifTags
from translatepy import Translator
from FSMbot import BotStates
from keyboards import *
from passCracker import PassCracker

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
greeting = "a bot that can encrypt and decrypt files, guess passwords for archives and documents in " \
           ".zip/.rar/.docx/.xlsx/.pdf format using a dictionary and password generation, extract audio tracks from " \
           "video files, photo metadata, text with a photo, and also knows how to translate text"


@dp.message_handler(commands=["start"])
async def start_func(message: types.Message) -> None:
    await message.reply("Hey! I'm Astaroth - " + greeting, reply_markup=get_base_keyboard())


@dp.callback_query_handler(Text(equals="Menu"), state=BotStates)
async def menu_func(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("Menu of " + greeting, reply_markup=get_base_keyboard())
    await state.finish()


@dp.callback_query_handler(Text(equals="Menu"))
async def call_menu(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text("Menu of " + greeting, reply_markup=get_base_keyboard())
    await state.finish()


@dp.callback_query_handler(Text(equals="Translation"))
async def choice_translation_func(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text("Send me a message and I will gladly translate it",
                                     reply_markup=get_translation_keyboard())
    await BotStates.translation_state.set()


@dp.message_handler(state=BotStates.translation_state)
async def choice_lang_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["text"] = message.text
    await message.answer("Please select or write the name of the language in which I should translate the message",
                         reply_markup=get_empty_keyboard())
    await BotStates.translation_lang_state.set()


@dp.callback_query_handler(Text(startswith="lang_"), state=BotStates.translation_lang_state)
async def translation_by_button_func(callback: types.CallbackQuery, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["lang"] = callback.data.split("_")[1]
    try:
        translator = Translator()
        await callback.message.answer(str(translator.translate(data["text"], data["lang"])),
                                      reply_markup=get_translation_keyboard())
        await BotStates.translation_state.set()
    except Exception as e:
        await callback.message.answer(f"Something went wrong, here is the error code:\n{e}",
                                      reply_markup=get_empty_keyboard())
        await state.finish()


@dp.message_handler(state=BotStates.translation_lang_state)
async def translation_with_text_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["lang"] = message.text
    try:
        translator = Translator()
        await message.answer(str(translator.translate(data["text"], data["lang"])), reply_markup=get_empty_keyboard())
        await BotStates.translation_state.set()
    except Exception as e:
        await message.answer(f"Something went wrong, here is the error code:\n{e}", reply_markup=get_empty_keyboard())
        await state.finish()


@dp.callback_query_handler(Text(equals="Crypto"))
async def choice_crypto_func(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text("It looks like you want to encrypt or decrypt a file using the AES protocol. "
                                     "Choose an action and good luck", reply_markup=get_crypto_keyboard())


@dp.callback_query_handler(Text(equals="Encrypt"))
async def choice_encrypt_func(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text("You want to encrypt the data. Well then send me the file",
                                     reply_markup=get_empty_keyboard())
    await BotStates.encrypt_state.set()


@dp.message_handler(content_types=["document"], state=BotStates.encrypt_state)
async def load_document_to_encrypt_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["path"] = f"temp/{message.document.file_id}/"
        data["name"] = f"{message.document.file_name}"
    await message.document.download(destination_file=data["path"]+data["name"])
    await message.reply("It's a matter of small. Now I need a key with which data will be encrypted",
                        reply_markup=get_empty_keyboard())
    await BotStates.encrypt_key_state.set()


@dp.message_handler(state=BotStates.encrypt_key_state)
async def encrypt_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["key"] = message.text
    pyAesCrypt.encryptFile(data["path"]+data["name"], data["path"]+"ENCRYPT_"+data["name"], data["key"])
    await message.reply_document(open(data["path"]+"ENCRYPT_"+data["name"], 'rb'))
    await message.answer("This is again the menu of " + greeting, reply_markup=get_base_keyboard())
    shutil.rmtree(data["path"])
    await state.finish()


@dp.callback_query_handler(Text(equals="Decrypt"))
async def choice_decrypt_func(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text("I need a file that I will decrypt. Send it to me",
                                     reply_markup=get_empty_keyboard())
    await BotStates.decrypt_state.set()


@dp.message_handler(content_types=["document"], state=BotStates.decrypt_state)
async def load_document_to_decrypt_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["path"] = f"temp/{message.document.file_id}/"
        data["name"] = f"{message.document.file_name}"
    await message.document.download(destination_file=data["path"]+data["name"])
    await message.reply("The file is in place, but something is missing to work with encrypted data. Possibly a key",
                        reply_markup=get_empty_keyboard())
    await BotStates.decrypt_key_state.set()


@dp.message_handler(state=BotStates.decrypt_key_state)
async def decrypt_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["key"] = message.text
    pyAesCrypt.decryptFile(data["path"]+data["name"], data["path"]+"DECRYPT_"+data["name"], data["key"])
    await message.reply_document(open(data["path"]+"DECRYPT_"+data["name"], 'rb'))
    await message.answer("This is again the menu of " + greeting, reply_markup=get_base_keyboard())
    shutil.rmtree(data["path"])
    await state.finish()


@dp.callback_query_handler(Text(equals="Extract"))
async def choice_extract_func(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text("Wow, you want to get into data mining. Hope I can help",
                                     reply_markup=get_extract_keyboard())


@dp.callback_query_handler(Text(equals="Extract audio"))
async def choice_extract_audio_func(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text("To extract the audio track from a video, I need...\nVideo file",
                                     reply_markup=get_empty_keyboard())
    await BotStates.extract_audio_state.set()


@dp.message_handler(content_types=["document"], state=BotStates.extract_audio_state)
async def extract_audio_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["path"] = f"temp/{message.document.file_id}/"
        data["name"] = f"{message.document.file_name}"
    await message.document.download(destination_file=data["path"]+data["name"])
    video = moviepy.editor.VideoFileClip(data["path"]+data["name"])
    audio = video.audio
    audio.write_audiofile(f"{data['path']}extract_audio.mp3")
    await message.reply_document(open(data["path"]+"extract_audio.mp3", "rb"))
    await message.answer("This is again the menu of " + greeting, reply_markup=get_base_keyboard())
    try:
        shutil.rmtree(data["path"])
    except OSError:
        pass
    await state.finish()


@dp.callback_query_handler(Text(equals="Extract meta"))
async def choice_extract_meta_func(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text("I need data about which I need to collect other data. Send me a photo "
                                     "(oh, and preferably via document submission)", reply_markup=get_empty_keyboard())
    await BotStates.extract_meta_state.set()


@dp.message_handler(content_types=["document"], state=BotStates.extract_meta_state)
async def extract_meta_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["path"] = f"temp/{message.document.file_id}/"
        data["name"] = f"photo.jpg"
    await message.document.download(destination_file=data["path"]+data["name"])
    img = Image.open(data["path"]+data["name"])
    exif_data = img.getexif()
    text = ""
    if exif_data:
        for key, val in exif_data.items():
            if key in ExifTags.TAGS:
                text += f"\n{ExifTags.TAGS[key]}:{val}"
    else:
        text = "I'm sorry, but I couldn't find the metadata"
    await message.answer(text, reply_markup=get_empty_keyboard())
    await message.answer("This is again the menu of " + greeting, reply_markup=get_base_keyboard())
    try:
        shutil.rmtree(data["path"])
    except OSError:
        pass
    await state.finish()


@dp.callback_query_handler(Text(equals="Extract text"))
async def choice_extract_text_func(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text("Hmm, recognize text in a picture. Not difficult, but for this I need a photo",
                                     reply_markup=get_empty_keyboard())
    await BotStates.extract_text_state.set()


@dp.message_handler(content_types=["photo"], state=BotStates.extract_text_state)
async def load_photo_to_extract_text_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["path"] = f"temp/{message.photo[-1].file_id}/"
        data["name"] = f"photo"
    await message.photo[-1].download(data["path"] + data["name"])
    await message.answer("And now the task is more difficult, decide on the language in the photo and "
                         "send it to me {eng, rus, fra...} or click on the button", 
                         reply_markup=get_translation_keyboard())
    await BotStates.extract_text_lang_state.set()


@dp.callback_query_handler(Text(startswith="lang_"), state=BotStates.extract_text_lang_state)
async def translation_by_button_func(callback: types.CallbackQuery, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["lang"] = callback.data.split("_")[1]
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    try:
        text = pytesseract.image_to_string(Image.open(data["path"] + data["name"]), lang=data["lang"])
        await callback.message.answer(text, reply_markup=get_empty_keyboard())
        await state.finish()
        try:
            shutil.rmtree(data["path"])
        except OSError:
            pass
    except Exception as exception:
        print(exception)
        await callback.message.answer(f"Something went wrong, here is the error code:\n{exception}",
                                      reply_markup=get_empty_keyboard())


@dp.message_handler(state=BotStates.extract_text_lang_state)
async def choice_lang_to_extract_text_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["lang"] = message.text
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    try:
        text = pytesseract.image_to_string(Image.open(data["path"] + data["name"]), lang=data["lang"])
        await message.answer(text, reply_markup=get_empty_keyboard())
        await state.finish()
        try:
            shutil.rmtree(data["path"])
        except OSError:
            pass
    except Exception as exception:
        print(exception)
        await message.answer(f"Something went wrong, here is the error code:\n{exception}",
                             reply_markup=get_empty_keyboard())


@dp.callback_query_handler(Text(equals="Password"))
async def choice_password_func(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text("And you are a little naughty, do you want to know the password from a document "
                                     "or archive? haha i'm ready to help", reply_markup=get_password_keyboard())


@dp.callback_query_handler(Text(equals="Crack password"))
async def choice_crack_password_func(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text("Let's not talk too much. Just send me the file",
                                     reply_markup=get_empty_keyboard())
    await BotStates.crack_password_state.set()


@dp.message_handler(content_types=["document"], state=BotStates.crack_password_state)
async def load_document_to_crack_password_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["path"] = f"temp/{message.document.file_id}/"
        data["name"] = f"{message.document.file_name}"
    await message.document.download(destination_file=data["path"]+data["name"])
    await message.answer("Password brute force is a tricky thing. You will make it easier for me "
                         "if you have a dictionary on hand.", reply_markup=get_auto_crack_keyboard())
    await BotStates.crack_password_dict_state.set()


@dp.message_handler(content_types=["document"], state=BotStates.crack_password_dict_state)
async def load_dictionary_to_crack_password_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["dict"] = f"{message.document.file_name}"
    await message.document.download(destination_file=data["path"]+data["dict"])
    cracker = PassCracker(data["path"]+data["name"], data["path"]+data["dict"], 0, 0)
    await message.answer(cracker.crack_password(), reply_markup=get_empty_keyboard())
    await message.answer("This is again the menu of " + greeting, reply_markup=get_base_keyboard())
    try:
        shutil.rmtree(data["path"])
    except OSError:
        pass
    await state.finish()


@dp.callback_query_handler(Text(equals="Pick up"), state=BotStates.crack_password_dict_state)
async def set_password_configuration_func(callback: types.CallbackQuery) -> None:
    await callback.message.answer("It's clear. You will have to do what you need to do. Thank you. Send me the "
                                  "minimum of password length.", reply_markup=get_empty_keyboard())
    await BotStates.crack_password_bottom_state.set()


@dp.message_handler(state=BotStates.crack_password_bottom_state)
async def get_bottom_of_password_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        try:
            data["bottom"] = int(message.text)
            await message.answer("Since you decided to shift all the work to me, then at least tell me in what "
                                 "interval the password length is located. Now send me the maximum length.",
                                 reply_markup=get_empty_keyboard())
            await BotStates.crack_password_up_state.set()
        except Exception as exception:
            print(exception)
            await message.answer("You entered something wrong, come on again.", reply_markup=get_empty_keyboard())


@dp.message_handler(state=BotStates.crack_password_up_state)
async def get_up_of_password_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        try:
            data["up"] = int(message.text)
            cracker = PassCracker(data["path"] + data["name"], None, data["bottom"], data["up"])
            await message.answer(cracker.crack_password(), reply_markup=get_empty_keyboard())
            await message.answer("Menu of " + greeting, reply_markup=get_base_keyboard())
            try:
                shutil.rmtree(data["path"])
            except OSError:
                pass
            await state.finish()
        except Exception as exception:
            print(exception)
            await message.answer("You entered something wrong, come on again.", reply_markup=get_base_keyboard())


@dp.message_handler()
async def pick_trash_func(message: types.Message) -> None:
    await message.answer("I don't quite understand what you want from me...", reply_markup=get_base_keyboard())


if __name__ == '__main__':
    try:
        shutil.rmtree("temp")
    except OSError:
        pass
    executor.start_polling(dp, skip_updates=True)
