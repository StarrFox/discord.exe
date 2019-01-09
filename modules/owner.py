import discord
from discord.ext import commands
import asyncio
import traceback
import aiohttp
from os import system
from bot_utils import checks

class owner:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Logging out")
        await self.bot.shutdown()
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
        await ctx.send("Restarting Discord.exe....")
        system("start restart.bat")
        await self.bot.shutdown()
        await self.bot.logout()

    @commands.command()
    @checks.is_owner()
    async def dm(self, ctx, user: discord.User, *, msg: str):
        await user.send(msg)
        await ctx.send("message sent")

    @commands.group(invoke_without_command=True)
    @checks.is_owner()
    async def blacklist(self, ctx):
        """List of blacklisted users"""
        pager = commands.Paginator()
        for user_id in self.bot.blacklist:
            pager.add_line(str(user_id))
        for page in pager.pages:
            await ctx.send(page)

    @blacklist.command()
    async def add(self, ctx, user: discord.Member):
        """Add user to blacklist"""
        self.bot.blacklist.append(user.id)
        await ctx.send("Done.")

    @blacklist.command(aliases=['rem'])
    async def remove(self, ctx, user: discord.Member):
        """Remove user from blacklist"""
        self.bot.blacklist.remove(user.id)
        await ctx.send("Done.")

def setup(bot):
    bot.add_cog(owner(bot))