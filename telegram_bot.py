from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from aiogram.filters import Command
from config import settings
import asyncio
from forex_news import get_all_news, get_impact_events, get_dates
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ai_summary import get_event_prompt,get_news_prompt,call_groq_with_retry
from datetime import datetime
from aiogram.enums import ParseMode
from redis_db import save_summary, get_summary,red
from apscheduler.schedulers.background import BackgroundScheduler
from scraper import main as scraper_main
from utils import GroqRateLimiter
from pprint import pprint
from typing import List


TOKEN = settings.TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = BackgroundScheduler()
router = Router()
groq_limiter = GroqRateLimiter(redis_client=red)

scheduler.add_job(scraper_main, trigger="cron", day_of_week="mon-fri", hour=0, minute=0)


news_list = []
news_index = {"present_index": 0, "daily_event": [], "summary_event": []}
impacts = {}
impacts["high"] = get_impact_events("high")
impacts["medium"] = get_impact_events("medium")
impacts["low"] = get_impact_events("low")
date = datetime.now()
day = date.day
month = datetime.strftime(date, "%b")
dates = get_dates()


class Form(StatesGroup):
    waiting_for_pair = State()


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Welcome to Macrovex")


@router.message(Command("help"))
async def help_handler(message: Message):
    response = """To Get all the news for today
                  Click on the 'news' command
                  To check the news for a particular currency pair use this
                  CurrencyPair impact(high,medium,low)
                  To get AI summaries and potential advice on the currency pair use this format \n\t
                  AI CurrencyPair impact
                  """
    await message.answer(response)


def paginate_buttons(current_index, total):
    """Creates the buttons"""
    buttons = []
    if current_index > 0:
        prev_button = InlineKeyboardButton(
            text="Prev", callback_data=f"news:prev_{current_index}"
        )
        buttons.append(prev_button)
    if current_index < total - 1:
        next_button = InlineKeyboardButton(
            text="Next", callback_data=f"news:next_{current_index}"
        )
        buttons.append(next_button)
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def calendar_buttons(current_index: int, total: int, impact: str):
    buttons = []
    if current_index > 0:
        prev_button = InlineKeyboardButton(
            text="Prev", callback_data=f"event:prev_{current_index}_{impact}"
        )
        buttons.append(prev_button)
    if current_index < total - 1:
        next_button = InlineKeyboardButton(
            text="Next", callback_data=f"event:next_{current_index}_{impact}"
        )
        buttons.append(next_button)
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def event_buttons(current_index: int, total: int):
    buttons = []
    if current_index > 0:
        prev = InlineKeyboardButton(
            text="Prev", callback_data=f"summary:prev_{current_index}"
        )
        buttons.append(prev)
    if current_index < total - 1:
        next = InlineKeyboardButton(
            text="Next", callback_data=f"summary:next_{current_index}"
        )
        buttons.append(next)
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


@router.message(Command("news"))
async def help_handler(message: Message):
    index = 0
    await message.answer("Thinking......")
    news = get_all_news()
    news_list.extend(news)
    print(news,news_list,flush=True)
    print(news_list[0],flush=True)
    await message.answer(
        news_list[0], reply_markup=paginate_buttons(index, len(news_list))
    )


@router.callback_query(F.data.startswith("news:"))
async def handle_pagination(callback: CallbackQuery):
    print("handling_callback")
    data = callback.data
    print(f"Data: {data}")
    if data.startswith("news:prev_"):
        current_index = data.split("_")[1]
        new_index = int(current_index) - 1
    elif data.startswith("news:next_"):
        current_index = data.split("_")[1]
        new_index = int(current_index) + 1
    else:
        return
    await callback.message.edit_text(
        news_list[new_index], reply_markup=paginate_buttons(new_index, len(news_list))
    )
    print("edited message")
    present_index = news_index["present_index"]
    present_index = new_index
    news_index["present_index"] = new_index
    print(present_index)
    await callback.answer()
    print("done")


@router.callback_query(F.data.startswith("event:"))
async def handle_calendar_buttons(callback: CallbackQuery):
    """This function handkes the callback queries for the calendar events gotten based on the date"""
    data = callback.data
    if data.startswith("event:prev"):
        current_index = data.split("_")[1]
        impact = data.split("_")[2]
        # calendar_day = filter(
        #     lambda x: day in x,impacts[impact]
        # )
        new_index = (
            int(current_index) - 1
        )  # If user clicks on the prev button it reduces the day by 1 and gets the previous event
    elif data.startswith("event:next"):
        current_index = data.split("_")[1]
        impact = data.split("_")[2]
        # calendar_day = filter(
        #     lambda x: day in x,impacts[impact]
        # )
        new_index = int(current_index) + 1
    else:
        return
    # month = datetime.strftime(datetime.now(), "%b")
    new_event = list(
        filter(lambda x: dates[new_index] in x, impacts[impact])
    )  # filters the news based on the day
    news_index["daily_event"] = new_event
    await callback.message.edit_text(
        "\n\n".join(new_event),
        reply_markup=calendar_buttons(new_index, len(dates), impact),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("summary:"))
async def handle_event_buttons(callback: CallbackQuery):
    data = callback.data
    if data.startswith("summary:prev_"):
        current_index = data.split("_")[1]
        new_index = int(current_index) - 1
        print(f"Pevious clicked new_index:{new_index}")
    elif data.startswith("summary:next_"):
        current_index = data.split("_")[1]
        new_index = int(current_index) + 1
        print(f"Next clicked new_index:{new_index}")
    else:
        return
    summary_events = news_index["summary_event"]
    print(summary_events)
    await callback.message.edit_text(
        text=summary_events[new_index],
        reply_markup=event_buttons(current_index=new_index, total=len(summary_events)),
    )
    await callback.answer()


@router.message(Command("ai_summary"))
async def get_ai_summary(message: Message):
    """This function gives the ai summary of the present news displayed"""
    thinking_message = await message.answer('🧠 Connecting the dots...')
    present_index = news_index["present_index"]
    print(present_index)
    news: str = news_list[present_index]
    allowed, reason = await groq_limiter.acquire()
    if not allowed:
        if reason == 'minute':
            wait = await groq_limiter.seconds_until_minute()
            await message.answer(f'Macrovex is currently cooling down Try again in {wait}s Macro thanks you 🤖🥂')
        else:
            await message.answer('Daily Limit reached Macro waits for you tomorrow 🤖👋')
        return
    title = news.split("\n")[0].split(": ")[1]
    response = ''
    print(title)
    if await get_summary(title=title) == False:
        prompt = get_news_prompt(incoming_message=news)
        try:
            response = await call_groq_with_retry(prompt=prompt)
        except Exception as e:
            await message.answer("Something broke on my end, try again in a bit")
            print(f"Groq_Error: {e}", flush=True)
        await save_summary(title=title, summary=response)
        print(f"saved:{title}")
    else:
        summary = await get_summary(title=title)
        print("Gotten from redis")
        response = summary
    await thinking_message.edit_text(text=response,parse_mode='HTML')


@router.message(Command("ai_events"))
async def get_summary_for_events(message: Message):
    title = news_index["daily_event"][0].split(" ")[1:3]
    impact = news_index["daily_event"][0].split(" ")[0].lstrip(":")
    title = f"{"".join(title)}_{impact}_summary"
    print(title)
    text = "\n\n".join(news_index["daily_event"])
    current_index = 0
    summary = ''
    if await get_summary(title=title) == False:
        prompt = await get_event_prompt(incoming_message=text)
        try:
            summary = await call_groq_with_retry(prompt=prompt)
            await save_summary(title=title, summary=summary)
        except Exception as e:
            await message.answer("Something broke on my end, try again in a bit")
            print(f"Groq_Error: {e}", flush=True)
    else:
        summary = await get_summary(title=title)
    if "!" in summary:
        events = summary.split("!")
        print(events)
        news_index["summary_event"] = events
        await message.answer(
            events[current_index],
            reply_markup=event_buttons(current_index=current_index, total=len(events)),
        )
    else:
        print(summary)

async def get_impact_event(message:Message,event_type:List):
    current_index = 0
    if date.weekday() > 5:
        await message.answer("No events enjoy your holiday".title())
        return
    current_date = datetime.now().strftime('%b %d')
    data = list(filter(lambda x: current_date in x, event_type))
    news_index["daily_event"] = data
    if not data:
        await message.answer('No news for today champ guess we\'re going full technical 📈🤖')
    await message.answer(
        "\n\n".join(data),
        reply_markup=calendar_buttons(current_index, len(dates), "high"),
    )

@router.message(Command("high_impact_events"))
async def get_high_impact_events(message: Message):
    high_impact = get_impact_events("high")
    await get_impact_event(message=message,event_type=high_impact)
    # current_date = datetime.now().strftime('%b %d')
    # data = list(filter(lambda x: current_date in x, high_impact))
    # news_index["daily_event"] = data
    # if not data:
    #     await message.answer()
    # await message.answer(
    #     "\n\n".join(data),
    #     reply_markup=calendar_buttons(current_index, len(dates), "high"),
    # )
    


@router.message(Command("medium_impact_events"))
async def get_medium_impact_events(message: Message):
    medium_impact = get_impact_events("medium")
    await get_impact_event(message=message,event_type=medium_impact)
    # data = list(filter(lambda x: dates[current_index] in x, medium_impact))
    # news_index["daily_event"] = data
    # await message.answer(
    #     "\n\n".join(data),
    #     reply_markup=calendar_buttons(current_index, len(dates), "medium"),
    # )


@router.message(Command("low_impact_events"))
async def get_low_impact_events(message: Message):
    low_impact = get_impact_events("low")
    await get_impact_event(message=message,event_type=low_impact)
    # data = list(filter(lambda x: dates[current_index] in x, low_impact))
    # news_index["daily_event"] = data
    # await message.answer(
    #     "\n\n".join(data),
    #     reply_markup=calendar_buttons(current_index, len(dates), "low"),
    # )


async def main():
    scheduler.start()
    dp.include_router(router=router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("starting........")
    asyncio.run(main())
