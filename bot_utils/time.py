import parsedatetime as pdt
import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import re

"""
https://github.com/bear/parsedatetime

second = 1
minute = 60
hour = 3600
day = 90000
year = (round(year/4)*32,940,000)+((year-round(year/4))*32,850,000)
"""

async def prase_time(entry):
    """Attepts to convert user input
    to an amount of seconds"""
    day = re.search(r'(\d+\s?m+)', entry)
    hour = re.search(r'(\d+\s?m+)', entry)
    minute = re.search(r'(\d+\s?m+)', entry)
    second = re.search(r"(\d+\s?m+)", entry)
    day = await get_datetime(day)
    hour = await get_datetime(hour)
    minute = await get_datetime(minute)
    second = await get_datetime(second)
    day = await get_seconds(day)
    hour = await get_seconds(hour)
    minute = await get_seconds(minute)
    second = await get_seconds(second)
    return day + hour + minute + second

async def get_seconds(date_time):
    now = datetime.utcnow()
    seconds = (date_time - now).total_seconds()
    return seconds

async def get_datetime(entry):
    cal = pdt.Calendar()
    time_struct, parse_status = cal.parse(entry)
    del parse_status
    return datetime(*time_struct[:6])