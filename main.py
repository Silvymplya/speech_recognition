import os
import vosk
import telebot

import wave
import subprocess
from vosk import KaldiRecognizer
from vosk import Model

VOICE_MODEL = Model(r"C:/Diplom/model/vosk-model-ru-0.22-copy")

token = "211798674:GIQkyH-YDmh4hIQIqcqS7aP"
bot = telebot.TeleBot(token)

# Создание списка пользователей
list_of_users = dict([])

print('READY')
@bot.message_handler(content_types=['voice'])
def process_voice_message(message):
    id = message.chat.id
    global list_of_users
    if(list_of_users.get(str(id)) == "Off"):
        return
    id = message.from_user.id

    voice_model = VOICE_MODEL

    # Загрузка глосового сообщения
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open(os.path.join(str(id) + '_user_voice.ogg'), 'wb') as new_file:
        new_file.write(downloaded_file)

    # конвертирование oog в wav
    src_filename = str(id) + '_user_voice.ogg'
    dest_filename = str(id) + '_my_phrase_to_translite.wav'

    process = subprocess.run(['C:\\Diplom\\ASR\\Telegram_bot\\ffmpeg\\bin\\ffmpeg.exe', '-i', src_filename, dest_filename])
    if process.returncode != 0:
        raise Exception("Something went wrong")

    user_phrase = recognize_phrase(voice_model, str(id) + '_my_phrase_to_translite.wav')

    try:
        bot.reply_to(message, str(user_phrase).capitalize())
    except:
        bot.reply_to(message, "Не удалось распознать.")

    # Удаление всех ранее созданых файлов

    os.remove(str(id) + '_user_voice.ogg')
    os.remove(str(id) + '_my_phrase_to_translite.wav')


def recognize_phrase(model: vosk.Model, phrase_wav_path: str) -> str:

    wf = wave.open(phrase_wav_path, "rb")

    # Создание строки для результатов
    results = ""

    # Создание модели для управления анализа речи
    recognizer = KaldiRecognizer(model, wf.getframerate())
    recognizer.SetWords(True)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            recognizerResult = recognizer.Result()
            results = results + recognizerResult

    # обработка получившегося результата
    results = results + recognizer.FinalResult()
    res = results.split('"text" : ')

    print("Second Result: ", res[1])
    final = res[1].split('"')
    return final[1]

@bot.message_handler(commands=['start'])
def start_msg(message):
    if message.chat.type == "private":
        bot.send_message(message.from_user.id, 'Привет, я могу преобразовать голосовые сообщения в текстовые. Для помощи используй команду "/help"')

@bot.message_handler(commands=['on'])
def turn_on(message):
    global list_of_users
    list_of_users.update({str(message.chat.id): "On"})
    bot.send_message(message.chat.id, "Я включен")

@bot.message_handler(commands=['off'])
def turn_off(message):
    global list_of_users
    list_of_users.update({str(message.chat.id): "Off"})
    bot.send_message(message.chat.id, "Я выключен")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который переводит голосовые сообщение в текст. Меня можно добавить в групповой чат и при необходимости можно включить или выключить используя команды /on и /off.")

@bot.message_handler(content_types=['text'])
def text_msg(message):
    if message.chat.type == "private":
        bot.send_message(message.from_user.id, 'Для помощи используй команду "/help"')

bot.polling(none_stop=True, interval=0)