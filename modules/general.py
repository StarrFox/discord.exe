import discord
from discord.ext import commands
import asyncio
import async_cse
import typing
from bot_utils import checks
import io
from datetime import datetime
import json

class general:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pyramid(self, ctx, *, msg: commands.clean_content()):
        final = ""
        length = len(msg)
        if length >= 35:
            await ctx.send('Message too long')
            return
        while length >- 0:
            final += f"{msg[:length]}\n"
            length -= 1
        length += 2
        while length <= len(msg):
            final += f"{msg[:length]}\n"
            length += 1
        await ctx.send(final)

    @commands.command()
    async def say(self, ctx, channel: typing.Optional[discord.TextChannel] = None, *, message: commands.clean_content()):
        if channel == None:
            channel = ctx.message.channel
        if ctx.author.id != self.bot.owner_id:
            userperms = ctx.message.author.guild_permissions
            for item in userperms:
                if str(item[0]) == "administrator" or str(item[0]) == "manage_channels":
                    if item[1] is True:
                        await channel.send(message)
                        return
                    else:
                        if channel.id != ctx.message.channel.id:
                            await ctx.send("Sorry bud you lack the perms to send to another channel")
                            return
                        else:
                            await channel.send(message)
                            return
        else:
            await channel.send(message)

    @commands.command()
    async def ping(self, ctx):
        """Check bot ping and latency"""
        process_time = round(((datetime.utcnow()-ctx.message.created_at).total_seconds())*1000)
        e = discord.Embed(
            color=discord.Color.dark_purple()
        )
        e.add_field(
            name="**Latency:**",
            value=f"{round(self.bot.latency*1000)}ms"
        )
        e.add_field(
            name="**Process time:**",
            value=f"{process_time}ms",
            inline=False
        )
        e.set_thumbnail(url=ctx.me.avatar_url)
        await ctx.send(embed=e)

    @commands.command()
    async def invite(self, ctx):
        """Invite the bot to your server"""
        invite0 = "https://discordapp.com/api/oauth2/authorize?client_id=529631910985596930&permissions=0&scope=bot"
        invite8 = "https://discordapp.com/api/oauth2/authorize?client_id=529631910985596930&permissions=8&scope=bot"
        message = f"**With perms:**\n<{invite8}>\n**Without perms (some things may not work):**\n<{invite0}>"
        await ctx.send(message)

    @commands.group(aliases=['g'], invoke_without_command=True)
    async def google(self, ctx, *, entry: str):
        """Google something"""
        apikey = self.bot.settings['google_key']
        search = async_cse.search.Search(apikey)
        results = await search.search(entry, safesearch=True)
        await search.session.close()
        googlelogo = "https://cdn.discordapp.com/emojis/515881186271166475.png?v=1"
        e = discord.Embed()
        e.add_field(name=results[0].title, value=f"[{results[0].description}]({results[0].url})")
        e.add_field(name=results[1].title, value=f"[{results[1].description}]({results[1].url})")
        e.add_field(name=results[2].title, value=f"[{results[2].description}]({results[2].url})")
        e.add_field(name=results[3].title, value=f"[{results[3].description}]({results[3].url})")
        e.add_field(name=results[4].title, value=f"[{results[4].description}]({results[4].url})")
        e.set_author(name="Results from Google", url="https://www.google.com", icon_url=googlelogo)
        await ctx.send(embed=e)

    @google.command(aliases=['i'])
    async def image(self, ctx, *, entry: str):
        """Google for images"""
        apikey = self.bot.settings['google_key']
        search = async_cse.search.Search(apikey)
        results = await search.search(entry, safesearch=True, image_search=True)
        await search.session.close()
        pages = []
        for i in results:
            pages.append(i.image_url)
        e = discord.Embed()
        e.set_image(url=pages[0])
        msg = await ctx.send(embed=e)
        await self.gimage(ctx, pages, msg, 0)

    async def gimage(self, ctx, pages, msg, page):
        arrow_left = "\u25c0"
        arrow_right = "\u25b6"
        await msg.add_reaction(arrow_left)
        await msg.add_reaction(arrow_right)
        def check(r, u):
            if r.message.id == msg.id and str(r.emoji) in [arrow_left, arrow_right] and u.id == ctx.message.author.id:
                return True
            else:
                return False
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=120)
        except:
            try:
                await msg.clear_reactions()
            except:
                pass
            return
        if reaction.emoji == arrow_left:
            page -= 1
            try:
                await msg.remove_reaction(arrow_left, user)
            except:
                pass
        else:
            page += 1
            try:
                await msg.remove_reaction(arrow_right, user)
            except:
                pass
        if page == 0:
            page += 1
        if page == 10:
            page -= 1
        e = discord.Embed()
        e.set_image(url=pages[page])
        await msg.edit(embed=e)
        await self.gimage(ctx, pages, msg, page)

    @commands.command(aliases=['msg'])
    @checks.serverowner_or_permissions(administrator=True)
    async def quote(self, ctx, user: discord.Member, *, message: str):
        """Send a message as someone else"""
        hook = await ctx.channel.create_webhook(name=user.display_name)
        await hook.send(message, avatar_url=user.avatar_url)
        await hook.delete()

    @commands.command(aliases=['tobin'])
    async def tobinary(self, ctx, *, entry: str):
        """Convert text to binary"""
        final = ""
        for c in entry:
            x = ord(c)
            x = bin(x)
            x = x.replace('b', '')
            final += x + " "
        if len(final) > 1000:
            fp = io.BytesIO(final.encode('utf-8'))
            await ctx.send("Output too long, dmed your file")
            await ctx.author.send(file=discord.File(fp, 'results.txt'))
        else:
            await ctx.send(final)

    @commands.command(aliases=['fbin'])
    async def frombinary(self, ctx, *entry: str):
        """Convery binary to text"""
        final = ""
        for c in entry:
            x = int(c, 2)
            x = chr(x)
            final += x
        if len(final) > 1000:
            fp = io.BytesIO(final.encode('utf-8'))
            await ctx.send("Output too long, dmed your file")
            await ctx.author.send(file=discord.File(fp, 'results.txt'))
        else:
            final = final.replace('@', '@\u200b')
            await ctx.send(final)

    @commands.command()
    async def msgraw(self, ctx, id: int):
        """Get the raw message data"""
        try:
            message = await self.bot.http.get_message(ctx.channel.id, id)
        except:
            return await ctx.send("Invalid message id")
        message['content'] = message['content'].replace('`', '')
        if len(message['content']) >= 100:
            message['content'] = message['content'][:97] + "..."
        message['embeds'] = len(message['embeds'])
        await ctx.send(f"```json\n{json.dumps(message, indent=4)}```")

def setup(bot):
    bot.add_cog(general(bot))