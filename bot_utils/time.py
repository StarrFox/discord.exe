import parsedatetime as pdt
import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import re

async def parse_time(entry):
    """Attepts to convert user input
    to an amount of seconds"""
    day = re.search(r'(\d+)\s?d(?:ays?)?', entry)
    hour = re.search(r'(\d+)\s?h(?:ours?)?', entry)
    minute = re.search(r'(\d+)\s?m(?:inutes?)?', entry)
    second = re.search(r"(\d+)\s?s(?:econds?)?", entry)
    if day:
        day = await get_datetime(day[0])
    if hour:
        hour = await get_datetime(hour[0])
    if minute:
        minute = await get_datetime(minute[0])
    if second:
        second = await get_datetime(second[0])
    if day:
        day = await get_seconds(day)
    if hour:
        hour = await get_seconds(hour)
    if minute:
        minute = await get_seconds(minute)
    if second:
        second = await get_seconds(second)
    total = 0
    if day:
        total += day
    if hour:
        total += hour
    if minute:
        total += minute
    if second:
        total += second
    return total

async def get_seconds(date_time):
    now = datetime.utcnow()
    seconds = (date_time - now).total_seconds()
    return seconds

async def get_datetime(entry):
    cal = pdt.Calendar()
    time_struct, parse_status = cal.parse(entry)
    del parse_status
    return datetime(*time_struct[:6])