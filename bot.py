import telebot
from telebot import types
import sqlite3

TOKEN = '1762092765:AAHZT8ijxALtbO7JNWiOghKvsDu4cAlP_A4'
bot = telebot.TeleBot(TOKEN)


def message(message):
    bot.send_message('1458879576', message)


def send_photo(pic, mem=0, meme=0):
    photo = open(pic, 'rb')
    bot.send_photo('1458879576', photo)
