import requests
from pathlib import Path
from bs4 import BeautifulSoup, Tag, ResultSet
import re
from typing import List
import json
import os
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
link = "https://www.myfxbook.com/forex-economic-calendar"
html_filename = "forex_factory.html"


def get_calender(link, html_filename):
    response = requests.get(link)
    filename = Path(BASE_DIR, html_filename)
    temp_file = f"{filename}.tmp"
    temp_file = Path(BASE_DIR, temp_file)
    try:
        with open(temp_file, "w", encoding="utf-8") as file:
            file.write(response.text)
        os.replace(temp_file, filename)
        return True
    except Exception as e:
        print(e)
        if os.path.exists(Path(BASE_DIR, temp_file)):
            os.remove(temp_file)
            return False


def get_calendar_info(dates: List, calendarCell: ResultSet[Tag], impact: str):
    date: str = calendarCell[0].text.strip()
    country = calendarCell[2].find("i")["title"]
    currency = calendarCell[3].text.strip()
    info = calendarCell[4].text.strip()
    if date.split(", ")[0] not in dates:
        dates.append(date.split(", ")[0])
    return f"{impact.title()}: {date} {country} {currency} {info}"


def get_events(soup: BeautifulSoup):
    economic_calendar = soup.select("tr.economicCalendarRow")
    saved_calendar = {}
    low_impact = []
    medium_impact = []
    high_impact = []
    dates = []

    for calendar in economic_calendar:
        if calendar.find("div", class_="impact_low"):
            calendarCell = calendar.select("td.calendarToggleCell")
            response = get_calendar_info(
                dates=dates, calendarCell=calendarCell, impact="low-impact"
            )
            # print(response)
            low_impact.append(response)

        elif calendar.find("div", class_="impact_medium"):
            calendarCell = calendar.select("td.calendarToggleCell")
            response = get_calendar_info(
                dates=dates, calendarCell=calendarCell, impact="medium-impact"
            )
            # print(response)
            medium_impact.append(response)

        elif calendar.find("div", class_="impact_high"):
            calendarCell = calendar.select("td.calendarToggleCell")
            response = get_calendar_info(
                dates=dates, calendarCell=calendarCell, impact="high-impact"
            )
            # print(response)
            high_impact.append(response)
    saved_calendar["refresh_date"] = datetime.now().isoformat()
    saved_calendar["dates"] = dates
    saved_calendar["low_impact"] = low_impact
    saved_calendar["medium_impact"] = medium_impact
    saved_calendar["high_impact"] = high_impact
    return saved_calendar


def main():
    gotten_calendar = get_calender(link=link, html_filename=html_filename)
    if gotten_calendar:
        with open(Path(BASE_DIR, html_filename), "r", encoding="utf-8") as f:
            html = f.read()
        soup = BeautifulSoup(html, "lxml")
        temp_file = Path(BASE_DIR, "calendar.json.tmp")
        real_file = Path(BASE_DIR, "calendar.json")
        try:
            calendar = get_events(soup=soup)
            with open(temp_file, "w") as file:
                file.write(json.dumps(calendar, indent=3))
            os.replace(temp_file, real_file)
        except Exception as e:
            print(e)
            if temp_file.exists():
                os.remove(temp_file)

    else:
        print("Error occured couldn't save file")


main()
