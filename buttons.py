from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def create_button(text: str, callback_data):
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data=callback_data)
    return builder.as_markup

summarize_news_btn = create_button('Ai Summary 🤖',callback_data='summarize_news')
summarize_event_btn = create_button('Ai Summary 🤖',callback_data='summarize_events')
