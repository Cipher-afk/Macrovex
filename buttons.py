from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton


def create_button(text: str, callback_data):
    button = InlineKeyboardButton(text=text, callback_data=callback_data)
    return button

summarize_news_btn = create_button('Ai Summary 🤖',callback_data='summarize_news')
summarize_event_btn = create_button('Ai Summary 🤖',callback_data='summarize_events')
