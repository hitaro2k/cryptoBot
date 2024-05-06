import telebot
from dotenv import load_dotenv
import os

load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'), parse_mode=None)


def start_bot():
    bot.polling()
