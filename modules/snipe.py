import discord
from discord.ext import commands
import asyncio
import typing

class snipe:

    def __init__(self, bot):
        self.bot = bot
        self.snipe_dict = {}

    async def on_message_delete(self, msg):
        """Saves message to snipe dict"""
        if not msg.content:
            return
        if not msg.channel.id in self.snipe_dict:
            self.snipe_dict[msg.channel.id] = []
        self.snipe_dict[msg.channel.id].insert(0, msg)

    @commands.group(name='snipe', invoke_without_command=True)
    async def _snipe(self, ctx, channel: typing.Optional[discord.TextChannel] = None, index: int = 0):
        """Snipe a command deleted in a channel"""
        if index < 0:
            return await ctx.send("Positive numbers only")
        if not channel:
            channel = ctx.channel
        if not channel.id in self.snipe_dict:
            return await ctx.send("This channel has no recorded messages")
        if len(self.snipe_dict[channel.id])-1 < index:
            return await ctx.send("I don't have that many messages recorded")
        msg = self.snipe_dict[channel.id][index]
        e = discord.Embed(
            color=discord.Color.dark_purple(),
            description=msg.content
        )
        e.set_author(
            name=msg.author.name,
            icon_url=msg.author.avatar_url
        )
        e.set_footer(
            text=f"{index}/{len(self.snipe_dict[channel.id])-1}"
        )
        await ctx.send(embed=e)

    @_snipe.command(name='list')
    async def _list(self, ctx, channel: discord.TextChannel = None):
        """List last 5 deleted messages in a channel"""
        if not channel:
            channel = ctx.channel
        if not channel.id in self.snipe_dict:
            return await ctx.send("This channel has no recorded messages")
        e = discord.Embed(
            color=discord.Color.dark_purple()
        )
        for num in range(5):
            try:
                msg = self.snipe_dict[channel.id][num]
                e.add_field(
                    name=f"**{msg.author.display_name}** said in **#{msg.channel.name}**",
                    value=msg.content[:100],
                    inline=False
                )
            except:
                pass
        await ctx.send(embed=e)



def setup(bot):
    bot.add_cog(snipe(bot))