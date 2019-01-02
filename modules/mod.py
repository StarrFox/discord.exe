import discord
from discord.ext import commands
import asyncio
from utils import checks
import typing

class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        ban_list = await ctx.guild.bans()
        try:
            member_id = int(argument, base=10)
            entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
        except ValueError:
            entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument("Not a valid previously-banned member.")
        return entity

class mod:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.serverowner_or_permissions(manage_messages=True)
    async def purge(self, ctx, number: int, user: typing.Optional[discord.Member] = None, *, text: str = None):
        """Purges messages from certain user or certain text"""
        channel = ctx.message.channel
        number += 1
        if not user and not text:
            try:
                deleted = await channel.purge(limit=number)
                msg = await channel.send(f"Deleted {len(deleted)} messages (deleted invoke message also)")
            except:
                msg = await channel.send("Unable to delete messages")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except:
                pass
            return
        def msgcheck(msg):
            if user and text:
                if text in msg.content.lower() and msg.author == user:
                    return True
                else:
                    return False
            if user:
                if msg.author == user:
                    return True
            if text:
                if text in msg.content.lower():
                    return True
        deleted = await channel.purge(limit=number, check=msgcheck)
        msg = await channel.send(f'Deleted {len(deleted)} message(s)')
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except:
            pass

    @commands.command()
    @checks.serverowner_or_permissions(ban_members=True)
    async def hackban(self, ctx, user: int):
        """Ban a user not in the server"""
        username = await self.bot.get_user_info(user)
        toban = discord.Object(id=user)
        if username in ctx.guild.members:
            await ctx.send("User is in server members")
            return
        try:
            await ctx.guild.ban(toban)
        except Exception as e:
            await ctx.send(e)
            return
        await ctx.send("{} has been banned".format(str(username)))

    @commands.command()
    @checks.serverowner_or_permissions(manage_messages=True)
    async def clean(self, ctx, num: int = 20):
        """Delete bot messages in the last 20(Default) messages"""
        channel = ctx.message.channel
        messages = []
        async for message in channel.history(limit=num):
            if message.author.bot:
                messages.append(message)
        if messages:
            await channel.delete_messages(messages)

    @commands.command()
    @checks.serverowner_or_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member):
        """Ban a member from the server"""
        guild = ctx.message.guild
        mod = ctx.message.author
        e = discord.Embed()
        guildid = str(guild.id)
        if guildid in self.userwhitelist:
            if user.id in self.userwhitelist[guildid]:
                await ctx.send("Cannot ban users in whitelist")
                return
        if user != mod and mod.top_role.position > user.top_role.position:
            try:
                await guild.ban(user)
                e.add_field(name='User banned', value="{} has been banned".format(user))
            except:
                e.add_field(name='No action', value="Unable to ban {}".format(user))
        else:
            await ctx.send("You cannot ban yourself or someone higher in role list")
        if e.fields:
            e.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=e)
    
    @commands.command()
    @checks.serverowner_or_permissions(administrator=True)
    async def unban(self, ctx, user: BannedMember):
        """Unban a user from the server"""
        guild = ctx.message.guild
        e = discord.Embed(title='')
        try:
            await guild.unban(user.user)
            e.add_field(name='Unban', value="{} has been unbanned".format(user.user))
        except:
            e.add_field(name='Unban', value="{} could not be unbanned".format(user))
        e.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(mod(bot))