import discord
from discord.ext import commands
import asyncio
import humanize

class info:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        """View bot info"""
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
        e.add_field(name="Uptime", value=f"Been up since {uptime}")
        e.add_field(name="Support server", value=f"[Join here]({support_server})")
        e.add_field(name="Invite me", value=f"[Invite here]({invite})")
        await ctx.send(embed=e)

    @commands.command(aliases=['ui'])
    async def userinfo(self, ctx, user: discord.Member = None):
        """Get info on a server member"""
        if not user:
            user = ctx.author
        joined = humanize.naturaldate(user.joined_at)
        joined_dis = humanize.naturaldate(user.create_at)
        top_role = user.top_role.name
        top_role_pos = (ctx.message.guild.roles[::-1].index(user.top_role))+1
        e = discord.Embed()
        e.add_field(name="Name|id", value=f"{user.name}|{user.id}")
        e.set_thumbnail(url=user.avatar_url)
        e.add_field(name="Joined guild:", value=joined)
        e.add_field(name="Joined discord:", value=joined_dis)
        e.add_field(name="Status:", value=f"Web: {user.web_stats}\nDesktop: {user.desktop_status}\nMobile: {user.mobile_status}")
        e.add_field(name="Top role:", value=f"{top_role} in pos #{top_role_pos}")
        e.add_field(name=f"{len(user.roles)} roles:", value=f"{[r.mention for r in user.roles]}")
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(info(bot))