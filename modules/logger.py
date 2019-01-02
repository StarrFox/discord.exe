import discord
from discord.ext import commands
import asyncio
import traceback
import aiohttp
from os import system

class logger:

    def __init__(self, bot):
        self.bot = bot

    async def on_guild_join(self, guild):
        channel = self.bot.get_channel(527440788934754314)
        await channel.send(f"name:{guild.name} id:{guild.id} members:{guild.member_count} owner:{str(guild.owner)}")


def setup(bot):
    bot.add_cog(logger(bot))