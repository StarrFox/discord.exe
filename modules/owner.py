import discord
from discord.ext import commands
import asyncio
import traceback
import aiohttp
from os import system

class owner:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Logging out")
        await self.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def avatar(self, ctx, url: str):
        botuser = self.bot.user
        session = aiohttp.ClientSession(loop=self.bot.loop)
        try:
            async with session.get(url) as r:
                data = await r.read()
                r.close()
            await botuser.edit(avatar=data)
            await ctx.send("Done.")
        except Exception as e:
            await ctx.send(e)
            traceback.print_exc()

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.send("Restarting discord.exe....")
        system("start restart.bat")
        await self.bot.logout()

def setup(bot):
    bot.add_cog(owner(bot))