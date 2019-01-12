import discord
from discord.ext import commands
import asyncio
from bot_utils import checks
from bot_utils import time as bt
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

    async def on_guild_remove(self, guild):
        #cleans up after leaving guild
        try:
            self.bot.mute_roles.pop(guild.id)
        except:
            pass

    @commands.group(invoke_without_command=True)
    async def prefix(self, ctx):
        """List and add/remove your prefixes"""
        guild = ctx.guild
        if guild.id in self.bot.prefixes:
            e = discord.Embed(description="\n".join(self.bot.prefixes[guild.id]), color=discord.Color.dark_purple())
            await ctx.send(embed=e)
        else:
            await ctx.send('exe!')

    @prefix.command()
    @checks.serverowner_or_permissions(administrator=True)
    async def add(self, ctx, prefix: str):
        """Add a prefix for this server"""
        guild = ctx.guild
        if len(prefix) > 20:
            return await ctx.send("Prefix too long (max is 20 chars)")
        if guild.id in self.bot.prefixes:
            if len(self.bot.prefixes[guild.id]) >= 10:
                return await ctx.send('Can only have 10 prefixes, remove one to add this one')
            else:
                self.bot.prefixes[guild.id].append(prefix)
                await ctx.send("Prefix added")
        else:
            self.bot.prefixes[guild.id] = []
            self.bot.prefixes[guild.id].append(prefix)
            await ctx.send("Prefix added")

    @prefix.command(aliases=['rem'])
    @checks.serverowner_or_permissions(administrator=True)
    async def remove(self, ctx, prefix: str):
        """Remove a prefix for this server"""
        guild = ctx.guild
        if guild.id in self.bot.prefixes:
            if len(self.bot.prefixes[guild.id]) == 1:
                return await ctx.send("Sorry I can't have no prefix")
            else:
                if prefix in self.bot.prefixes[guild.id]:
                    self.bot.prefixes[guild.id].remove(prefix)
                    return await ctx.send("Prefix removed")
                else:
                    return await ctx.send("Prefix not found")
        else:
            await ctx.send("Don't know how you got here lol")

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

    @commands.command(aliases=["nick", "rename"])
    @checks.serverowner_or_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, nick: str):
        """Change another members nickname"""
        old_nick = member.display_name
        if nick:
            if len(nick) > 32:
                clean = nick.replace('@', '@\u200b')
                return await ctx.send(f"{clean} is {len(nick)-32} over the character limit")
        if ctx.author.top_role.position > member.top_role.position or member.id == ctx.author.id:
            try:
                await member.edit(nick=nick)
                await ctx.send(f"Changed {old_nick}'s nickname to {nick}")
            except:
                await ctx.send("Missing perms or invalid characters")

    @commands.command()
    @checks.serverowner_or_permissions(manage_messages=True)
    async def mute(self, ctx, user: discord.Member, *, time: str = None):
        """Mute a server member"""
        guild = ctx.message.guild
        mod = ctx.message.author
        if guild.id not in self.bot.mute_roles:
            msg = await ctx.send("No mute role found one moment while I create one")
            role = await self.create_mute_role(guild)
            await msg.edit(content="Done")
        else:
            role = guild.get_role(self.bot.mute_roles[guild.id])
        if user != mod and mod.top_role.position > user.top_role.position:
            if time:
                await self.time_mute(ctx, role, user, time)
            else:
                try:
                    await user.add_roles(role)
                    await ctx.send('User muted')
                except:
                    await ctx.send('Muting failed')

    async def create_mute_role(self, guild):
        """Creates role named 'Discord.exe mute'
        Then makes overwrites for all channels"""
        try:
            role = await guild.create_role(name="Discord.exe mute", permissions=discord.Permissions())
        except:
            return None
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.add_reactions = False
        overwrite.connect = False
        for channel in guild.channels:
            try:
                await channel.set_permissions(target=role, overwrite=overwrite)
            except:
                pass
        return role
  
    async def time_mute(self, ctx, role, user, time):
        time = await bt.parse_time(time)
        if time == 0:
            return await ctx.send("Invalid time")
        await user.add_roles(role)
        await ctx.send(f"`{str(user)}` muted for about `{round(time)} seconds`")
        await asyncio.sleep(time)
        await user.remove_roles(role)
        await ctx.send(f"{str(user)} unmuted")

def setup(bot):
    bot.add_cog(mod(bot))