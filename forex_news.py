import feedparser
from datetime import datetime, timedelta
import pandas as pd
from utils import isholiday, read_json, BASE_DIR
from pathlib import Path
from typing import Dict, List
from pprint import pprint
import requests

HIGH_IMPACT_KEYWORD = []
JSON_FILE = Path(BASE_DIR, "calendar.json")

# urls = [
#     "https://www.forexlive.com/feed/news",
#     "https://www.investing.com/rss/news_1.rss",
#     "https://www.forexcrunch.com/feed/",
# ]

# for url in urls:
#     feed = feedparser.parse(url)
#     print(url,flush=True)
#     print("bozo:", feed.bozo, "| status:", feed.get('status'), "| entries:", len(feed.entries),flush=True)
#     print("---")

def get_all_news():
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    url = "https://www.forexlive.com/feed/news"
    feed = feedparser.parse(url)
    print(url,flush=True)
    print("bozo:", feed.bozo, "| status:", feed.get('status'), "| entries:", len(feed.entries),flush=True)
    news_list = []
    for entry in feed.entries:
        output = f"Title: {entry.title}\nSummary: {entry.summary}\nLink: {entry.link}\n"
        news_list.append(output)
    return news_list


# def get_high_impact_news():
#     pass


# def get_news_on_pair(pair: str):
#     pass


def get_calendar():
    data: Dict = read_json(json_file=JSON_FILE)
    if data:
        date = datetime.fromisoformat(data["refresh_date"])
        # if isholiday(date=date):
        #     return "No news for today enjoy your holiday".title()
        return data


def get_high_impact_events():
    calendar = get_calendar()
    if isinstance(calendar, str):
        return calendar
    high_impact = calendar["high_impact"]
    if not high_impact:
        return "No high impact news".title()
    else:
        return high_impact


def get_medium_impact_events():
    calendar = get_calendar()
    if isinstance(calendar, str):
        return calendar
    medium_impact = calendar["medium_impact"]
    if not medium_impact:
        return "No medium impact news".title()
    else:
        return medium_impact


def get_low_impact_events():
    calendar = get_calendar()
    if isinstance(calendar, str):
        return calendar
    low_impact = calendar["low_impact"]
    if not low_impact:
        return "No low impact news".title()
    else:
        return low_impact


def get_impact_events(impact_type: str):
    impact_type = impact_type.lower()
    if impact_type == "high":
        data = get_high_impact_events()
    elif impact_type == "medium":
        data = get_medium_impact_events()
    elif impact_type == "low":
        data = get_low_impact_events()
    else:
        raise Exception("Not a valid impact type")
    return data


def get_dates() -> List[str]:
    calendar = get_calendar()
    dates = calendar["dates"]
    return dates


if __name__ == "__main__":
    # pprint(get_high_impact_events())
    # date = datetime.now()
    # day, month = date.day, datetime.strftime(date, "%b")
    # day += 1
    # todays_events = filter(lambda x: f"{month} {day}" in x, get_high_impact_events())
    pprint(get_all_news())
    # # today = f"{month} {day}"
    # while True:
    #     todays_events = filter(
    #         lambda x: f"{month} {day}" in x, get_high_impact_events()
    #     )
    #     print(list(todays_events))
    #     user_input = input("Get tommorow's news[Y/N]: ").lower()
    #     if user_input == "y":
    #         day += 1
    #     elif todays_events[0] == None:
    #         print("Days done")
    #         break
    #     else:
    #         break
