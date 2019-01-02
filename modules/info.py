import discord
from discord.ext import commands
import asyncio
import humanize

class info:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        owner = "StarrFox#6312"
        guilds = len(self.bot.guilds)
        users = len(self.bot.users)
        channels = len([c for c in self.bot.get_all_channels()])
        support_server = "https://discord.gg/WsgQfxC"
        top_role = ctx.message.guild.me.top_role.name
        top_role_pos = (ctx.message.guild.roles[::-1].index(ctx.message.guild.me.top_role))+1
        invite = "https://discordapp.com/api/oauth2/authorize?client_id=529631910985596930&permissions=8&scope=bot"
        uptime = humanize.naturaltime(self.bot.start_time)
        e = discord.Embed(title="Discord.exe")
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.add_field(name="Owner:", value=owner)
        e.add_field(name="Connected to:", value=f"Guilds: {guilds}\nChannels: {channels}\nUsers: {users}")
        e.add_field(name="Top role", value=f"{top_role} in pos #{top_role_pos}")
        e.add_field(name="Uptime", value=f"been up since {uptime}")
        e.add_field(name="Support server", value=f"[Join here]({support_server})")
        e.add_field(name="Invite me", value=f"[Invite here]({invite})")
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(info(bot))