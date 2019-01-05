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
        e = discord.Embed(title="Guild add", color=discord.Color.dark_purple())
        e.set_thumbnail(url=guild.icon_url)
        e.add_field(name="Name:", value=guild.name)
        e.add_field(name="ID:", value=guild.id)
        e.add_field(name="Owner:", value=str(guild.owner))
        e.add_field(name="Member count", value=guild.member_count)
        await channel.send(embed=e)

    async def on_guild_remove(self, guild):
        channel = self.bot.get_channel(527440788934754314)
        e = discord.Embed(title="Guild remove", color=discord.Color.dark_purple())
        e.set_thumbnail(url=guild.icon_url)
        e.add_field(name="Name:", value=guild.name)
        e.add_field(name="ID:", value=guild.id)
        e.add_field(name="Owner:", value=str(guild.owner))
        e.add_field(name="Member count", value=guild.member_count)
        await channel.send(embed=e)

    async def on_message(self, message):
        if message.guild is None and not message.author.bot:
            channel = self.bot.get_channel(521116687437791233)
            e = discord.Embed(title=f"Dm from {str(message.author)}", color=discord.Color.dark_purple())
            e.set_thumbnail(url=message.author.avatar_url)
            e.add_field(name="Author ID:", value=message.author.id)
            e.add_field(name="Content:", value=message.content, inline=False)
            await channel.send(embed=e)

def setup(bot):
    bot.add_cog(logger(bot))