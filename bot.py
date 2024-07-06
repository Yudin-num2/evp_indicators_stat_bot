import configparser
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dataParse import *
import os


config = configparser.ConfigParser()
config.read('config.ini')
TOKEN = config.get('bot','token')
TPA = [
    "Lid 1", "Frame 1", "Cutter 1",
    "Lid 2", "Frame 2", "Cutter 2",
    "Lid 3", "Frame 3", "Cutter 3",
    "Lid 4", "Frame 4", "Cutter 4",
    "Lid 5", "Frame 5", "Cutter 5",
    "Lid 6", "Frame 6", "Cutter 6",
    "Lid 7", "Frame 7", "Cutter 7",
            ]
INDICATORS = [
    "Время цикла", "Давление GreenBox",
    "Гнёзда", "t°C масла",
    "t°C на входе формы", "t°C на выходе формы",
              ]

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_hello(message):
    bot.send_message(message.chat.id, """
Привет! 👋 
Я твой помощник в анализе отчётов 1С:ТОИР 🛠
Отправь мне отчёт из 1С:ТОИР в формате .xlsx
Выбери нужную машину и интересуемый показатель,
а я буду анализировать его и строить график 📈
""")
    
@bot.message_handler(content_types=['document'])
def save_document(message):
    file_info = bot.get_file(message.document.file_id)
    file_name = file_info.file_path
    if file_name.endswith('.xlsx'):
        print(file_info)
        downloaded_file = bot.download_file(file_name)
        with open('1.xlsx', 'wb') as f:
            f.write(downloaded_file)
        bot.send_message(message.chat.id, f'Файл успешно сохранён!')
    else:
        bot.send_message(message.chat.id, f"""Пока что я не умею работать с файлами {file_name.split('.')[-1]}
Только с файлами с расширением .xlsx""")


def check_xlsx_files_in_directory(message):
    files_and_dirs = os.listdir(".")
    xlsx_files = [f for f in files_and_dirs if f.endswith('.xlsx') and os.path.isfile(os.path.join(".", f))]

    if xlsx_files: return True
    else:
        bot.send_message(message.chat.id, f"""
В моём хранилище нет файла для формирования графиков.
Отправь мне его в формате Excel (.xlsx)""")
        return False

@bot.message_handler(commands=['stats'])
def send_stats(message):
    if check_xlsx_files_in_directory(message):
        markup = InlineKeyboardMarkup(row_width=3)
        buttons = [InlineKeyboardButton(f"{tpa}", callback_data=f"m_{tpa}") for tpa in TPA]
        markup.add(*buttons)
        bot.send_message(message.chat.id, "Выберите машину:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("m_"))
def first_group_callback(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    tpa = call.data.split("_")[1]
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(f"{ind}", 
        callback_data=f"i_{tpa}_{ind}") for ind in INDICATORS]
    markup.add(*buttons)
    bot.send_message(call.message.chat.id, "Выберите показатель:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("i_"))
def second_group_callback(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    _, tpa, ind = call.data.split("_")
    bot.send_message(call.message.chat.id,  f"📊 Анализирую, ожидайте")
    image_path = plot_metric_for_machine(tpa, ind)
    if image_path is not None:
        print(image_path)
        with open(image_path, 'rb') as photo:
            bot.send_photo(call.message.chat.id, photo)
    else:
        print(f"Не удалось создать изображение для {tpa} {ind}")
    bot.delete_message(call.message.chat.id, call.message.message_id)

    




if __name__ == '__main__':
    bot.infinity_polling()