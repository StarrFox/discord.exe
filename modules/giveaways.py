import discord
from discord.ext import commands
import asyncio
from random import choice
import humanize
from datetime import datetime

class giveaways:
    """Giveaway process and related comamnds"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def start(self, ctx, channel: discord.TextChannel, time: int, winners: int, *, prize: str):
        await ctx.send("Starting")
        await self.giveaway_process(channel, time, winners, prize)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def giveaway(self, ctx):
        def chancheck(msg):
            channel = msg.channel_mentions
            if not channel:
                return False
            elif msg.author.id == ctx.author.id:
                return True
        def authorcheck(msg):
            if msg.author.id == ctx.message.author.id:
                return True
            else:
                return False
        await ctx.send("What channel would you like to host the giveaway in?")
        try:
            chanmsg = await self.bot.wait_for('message', check=chancheck, timeout=120)
        except:
            await ctx.send("Timmed out, aborting setup")
            return
        await ctx.send("How long should the giveaway be?\nEX: 10 days 4 minutes 7 seconds")
        try:
            timemsg = await self.bot.wait_for('message', check=authorcheck, timeout=120)
        except:
            await ctx.send("Timmed out, aborting setup")
            return
        try:
            time = await self.dmhsconvert(timemsg.content)
        except:
            await ctx.send("Invalid time detected aborting setup")
            return
        await ctx.send("How many winners?")
        try:
            winnermsg = await self.bot.wait_for('message', check=authorcheck, timeout=120)
        except:
            await ctx.send("Timmed out, aborting setup")
            return
        await ctx.send("What would you like to giveaway?")
        try:
            prizemsg = await self.bot.wait_for('message', check=authorcheck, timeout=120)
        except:
            await ctx.send("Timmed out, aborting setup")
            return
        await ctx.send("Starting")
        winnermsg = int(winnermsg.content)
        prizemsg = prizemsg.content
        chanmsg = chanmsg.channel_mentions[0]
        await self.giveaway_process(chanmsg, time, winnermsg, prizemsg)

    async def giveaway_process(self, channel, time, winners, prize):
        humantime = humanize.naturaltime(datetime.utcfromtimestamp(datetime.utcnow().timestamp()+time))
        e = discord.Embed(title=prize, description=f"React with <a:giveaway:526404437799862292> to enter\nEnding {humantime}")
        msg = await channel.send(embed=e)
        await msg.add_reaction('a:giveaway:526404437799862292')
        await asyncio.sleep(int(time))
        msg = await channel.get_message(msg.id)
        entries = []
        for reaction in msg.reactions:
            if reaction.emoji.id == 526404437799862292:
                async for user in reaction.users():
                    if not user.bot:
                        entries.append(user)
        finalwinners = []
        if len(entries) < winners:
            finalwinners = entries
        else:
            for x in range(winners):
                pick = choice(entries)
                finalwinners.append(pick)
                entries.remove(pick)
            del x
        winning_msg = ""
        for y in finalwinners:
            winning_msg += y.mention
        if winners == 1:
            dex = f"{winning_msg} is the winner"
        else:
            dex = f"{winning_msg} are the winnders"
        q = discord.Embed(title=prize, description=dex)
        await msg.edit(embed=q)
        await channel.send(f"Giveaway over, congratz {winning_msg}")

    async def dmhsconvert(self, entry):
        entry = entry.replace(" ", "")
        entry = entry.lower()
        if 'days' in entry:
            entry = entry.replace("days", "d")
        if 'day' in entry:
            entry = entry.replace("day", "d")
        if 'hours' in entry:
            entry = entry.replace("hours", "h")
        if 'hour' in entry:
            entry = entry.replace("hour", "h")
        if 'minutes' in entry:
            entry = entry.replace("minutes", "m")
        if 'minute' in entry:
            entry = entry.replace("minute", "m")
        if 'seconds' in entry:
            entry = entry.replace("seconds", "s")
        if 'second' in entry:
            entry = entry.replace("second", "s")
        x = 0
        if 'd' in entry:
            days, entry = entry.split('d')
            x += (int(days)*86400)
        if 'h' in entry:
            hours, entry = entry.split('h')
            x += (int(hours)*3600)
        if 'm' in entry:
            minutes, entry = entry.split('m')
            x += (int(minutes)*60)
        if 's' in entry:
            seconds = entry.replace("s", "")
            seconds = int(seconds)
            x += seconds
        return x

def setup(bot):
    n = giveaways(bot)
    bot.add_cog(n)