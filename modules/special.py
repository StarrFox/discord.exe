import discord
from discord.ext import commands
import asyncio
import json
from discord.ext.commands.cooldowns import BucketType

class special:

    def __init__(self, bot):
        self.bot = bot
        self.list = json.load(open("data/emote_list.json"))
        self.save_task = self.bot.loop.create_task(self.save())
        self.lastview = {}

    @commands.group(aliases=['we'], invoke_without_command=True)
    async def wallemotes(self, ctx):
        msg = ""
        for i in self.list:
            msg += f"{i}\n"
        await ctx.send(f"```Use exe!wallemotes view <name>\n{msg}```")

    @wallemotes.command()
    @commands.is_owner()
    async def add(self, ctx, name: str, invite: str, *, emotes: str):
        name = name.lower()
        self.list[name] = {}
        self.list[name]['invite'] = invite
        self.list[name]['emotes'] = emotes
        await ctx.send(f"Added {name} to wall emote lists")

    @wallemotes.command()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.guild)
    async def view(self, ctx, *, name: str):
        name = name.lower()
        if not name in self.list:
            await ctx.send("Not found")
            return
        if ctx.guild.id in self.lastview:
            for m in self.lastview[ctx.guild.id]:
                await m.delete()
            self.lastview.pop(ctx.guild.id)
        self.lastview[ctx.guild.id] = []
        msg = f"**{name}:**\n{self.list[name]['invite']}"
        m1 = await ctx.send(msg)
        m2 = await ctx.send(f"{self.list[name]['emotes']}")
        self.lastview[ctx.guild.id].append(m1)
        self.lastview[ctx.guild.id].append(m2)

    async def save(self):
        while True:
            with open('data/emote_list.json', 'w') as f:
                json.dump(self.list, f)
                f.close()
            await asyncio.sleep(1800)

def setup(bot):
    bot.add_cog(special(bot))