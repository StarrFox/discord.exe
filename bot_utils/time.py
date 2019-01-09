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
class time:

    def __init__(self):
        self.timers = None

    async def prase_time(self, entry):
        """Attepts to convert user input
        to an amount of seconds"""
        day = re.search(r'(\d+\s?m+)', entry)
        hour = re.search(r'(\d+\s?m+)', entry)
        minute = re.search(r'(\d+\s?m+)', entry)
        second = re.search(r"(\d+\s?m+)", entry)
        day = await self.get_datetime(day)
        hour = await self.get_datetime(hour)
        minute = await self.get_datetime(minute)
        second = await self.get_datetime(second)
        day = await self.get_seconds(day)
        hour = await self.get_seconds(hour)
        minute = await self.get_seconds(minute)
        second = await self.get_seconds(second)
        return day + hour + minute + second

    async def get_seconds(self, date_time):
        now = datetime.utcnow()
        seconds = (date_time - now).total_seconds()
        return seconds

    async def get_datetime(self, entry):
        cal = pdt.Calendar()
        time_struct, parse_status = cal.parse(entry)
        del parse_status
        return datetime(*time_struct[:6])