import discord
from discord.ext import commands
import asyncio
from bot_utils.paginator import paginator

class utilities:

    def __init__(self, bot):
        self.bot = bot
        print("Utils loaded")

    @commands.command(aliases=['cp'])
    async def checkperm(self, ctx, *, perm: str):
        """list every user with a certain perm"""
        perm = perm.replace(" ", "_")
        perm = perm.lower()
        pager = paginator(self.bot)
        lines = []
        x = 1
        for m in ctx.guild.members:
            for item in m.guild_permissions:
                if item[0] == perm and item[1] is True:
                    lines.append(f"{x}. {m.name}")
                    x += 1
            if len(lines) == 20:
                dex = "\n".join(lines)
                e = discord.Embed(name=f"**Users with the {perm} perm**", description=dex)
                pager.add_page(data=e)
                lines = []
        if len(lines) != 0:
            dex = "\n".join(lines)
            e = discord.Embed(name=f"**Users with the {perm} perm**", description=dex)
            pager.add_page(data=e)
        if len(pager.pages) != 0:
            await pager.do_paginator(ctx)

def setup(bot):
    bot.add_cog(utilities(bot))