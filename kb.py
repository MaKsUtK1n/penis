from config import *
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def error_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Сделать ставку💎", payment_link))
    return keyboard

lose_kb = error_kb

def win_kb(code):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Сделать ставку💎", payment_link))
    keyboard.row(InlineKeyboardButton("Забрать выигрыш🏦", f'https://t.me/{bot_username}?start={code}'))
    return keyboard


def draw_kb(code):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Сделать ставку💎", payment_link))
    keyboard.row(InlineKeyboardButton("Вернуть ставку", f'https://t.me/{bot_username}?start={code}'))
    return keyboard


def start_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Профиль", callback_data="profile"), InlineKeyboardButton("Реферал панель", callback_data="ref"))
    keyboard.row(InlineKeyboardButton("Сделать ставку💎", payment_link), InlineKeyboardButton("Игровой канал", channel_link))
    return keyboard

def profile_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Сделать ставку💎", payment_link))
    keyboard.row(InlineKeyboardButton("Назад", callback_data="start"))
    return keyboard

def ref_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Вывести реферальный баланс", callback_data="ref_withdraw"))
    keyboard.row(InlineKeyboardButton("Назад", callback_data="start"))
    return keyboard