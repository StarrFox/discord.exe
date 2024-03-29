import discord
from discord.ext import commands
import asyncio
from fuzzywuzzy import process
from discord.ext.commands.cooldowns import BucketType
from bot_utils.paginator import paginator

class tags:

    def __init__(self, bot):
        self.bot = bot
        self.reserved = [
            'add',
            'all',
            'create',
            'edit',
            'delete',
            'info',
            'list'
        ]

    async def on_guild_remove(self, guild):
        #cleans up after leaving guild
        try:
            self.bot.tags.pop(guild.id)
        except:
            pass

    async def on_guild_join(self, guild):
        self.bot.tags[guild.id] = {}
        print(f"Init tags for {guild.name}")

    @commands.group(invoke_without_command=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def tag(self, ctx, *, tag_name: commands.clean_content()):
        """Create and recall info"""
        tag_name = tag_name.lower()
        guild = ctx.guild
        if not tag_name in self.bot.tags[guild.id]:
            try:
                matches = process.extract(tag_name, self.bot.tags[guild.id].keys(), limit=2)
            except:
                matches = None
                pass
            if matches:
                if matches[0][1] > 60:
                    return await ctx.send("Tag not found did you mean:\n" + "\n".join([i[0] for i in matches]))
                else:
                    return await ctx.send("Tag not found")
            else:
                return await ctx.send("Tag not found")
        else:
            self.bot.tags[guild.id][tag_name]['uses'] += 1
            return await ctx.send(self.bot.tags[guild.id][tag_name]['content'])

    @tag.command(aliases=['add'])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def create(self, ctx, tag_name: commands.clean_content(), *, content: commands.clean_content()):
        """Create a tag"""
        guild = ctx.guild
        tag_name = tag_name.lower()
        if tag_name in self.reserved:
            return await ctx.send("This tag name is a reserved word")
        if len(tag_name) > 100:
            return await ctx.send("Tag names must be under 100 characters")
        if tag_name in self.bot.tags[guild.id]:
            return await ctx.send("Tag already exist")
        else:
            self.bot.tags[guild.id][tag_name] = {}
            self.bot.tags[guild.id][tag_name]['content'] = content
            self.bot.tags[guild.id][tag_name]['uses'] = 0
            self.bot.tags[guild.id][tag_name]['owner_id'] = ctx.author.id
            await ctx.send("Tag created")

    @tag.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def edit(self, ctx, tag_name: commands.clean_content(), *, content: commands.clean_content()):
        """Edit a tag"""
        guild = ctx.guild
        tag_name = tag_name.lower()
        if tag_name not in self.bot.tags[guild.id]:
            return await ctx.send(f"Tag not found")
        if ctx.author.id != self.bot.tags[guild.id][tag_name]['owner_id']:
            return await ctx.send(f"You do not own this tag")
        else:
            self.bot.tags[guild.id][tag_name]['content'] = content
            await ctx.send("Edited tag")

    @tag.command()
    async def delete(self, ctx, tag_name: commands.clean_content()):
        """Deletes a tag

        Must be the tag owner or have the admin perm
        """
        guild = ctx.guild
        tag_name = tag_name.lower()
        if tag_name not in self.bot.tags[guild.id]:
            return await ctx.send(f"Tag not found")
        if ctx.author.id == self.bot.tags[guild.id][tag_name]['owner_id'] or ctx.author.guild_permissions.administrator:
            self.bot.tags[guild.id].pop(tag_name)
            return await ctx.send("Tag deleted")
        else:
            await ctx.send("You are not the tag owner or an admin")

    @tag.command()
    async def info(self, ctx, tag_name: commands.clean_content()):
        """Get info on a tag"""
        guild = ctx.guild
        tag_name = tag_name.lower()
        if tag_name not in self.bot.tags[guild.id]:
            return await ctx.send(f"Tag not found")
        tag_owner = guild.get_member(self.bot.tags[guild.id][tag_name]['owner_id'])
        e = discord.Embed(title=tag_name, color=discord.Color.dark_purple())
        e.set_thumbnail(url=tag_owner.avatar_url)
        e.add_field(name="Uses:", value=self.bot.tags[guild.id][tag_name]['uses'])
        e.add_field(name="Owner:", value=f"{tag_owner.mention}\n{str(tag_owner)}")
        await ctx.send(embed=e)

    @tag.command()
    async def all(self, ctx):
        """List all the tags in this server"""
        guild = ctx.guild
        if len(self.bot.tags[guild.id]) == 0:
            return await ctx.send("This guild has no tags")
        pager = paginator(self.bot)
        temp_lines = []
        x = 1
        for key in self.bot.tags[guild.id].keys():
            temp_lines.append(f"{x}. {key}")
            if len(temp_lines) == 20:
                dex = "\n".join(temp_lines)
                e = discord.Embed(title="**All tags for this server**", description=dex, color=discord.Color.dark_purple())
                pager.add_page(data=e)
                temp_lines = []
            x += 1
        dex = "\n".join(temp_lines)
        e = discord.Embed(title="**All tags for this server**", description=dex, color=discord.Color.dark_purple())
        pager.add_page(data=e)
        await pager.do_paginator(ctx)

    @tag.command(name='list')
    async def _list(self, ctx, member: discord.Member = None):
        """List all tags for a user"""
        guild = ctx.guild
        if not member:
            member = ctx.author
        tag_list = [t for t in self.bot.tags[guild.id] if self.bot.tags[guild.id][t]['owner_id'] == member.id]
        if len(tag_list) == 0:
            return await ctx.send("This user has no tags")
        pager = paginator(self.bot)
        temp_lines = []
        x = 1
        for key in tag_list:
            temp_lines.append(f"{x}. {key}")
            if len(temp_lines) == 20:
                dex = "\n".join(temp_lines)
                e = discord.Embed(title="**All tags for this user**", description=dex, color=discord.Color.dark_purple())
                pager.add_page(data=e)
                temp_lines = []
            x += 1
        dex = "\n".join(temp_lines)
        e = discord.Embed(title="**All tags for this user**", description=dex, color=discord.Color.dark_purple())
        pager.add_page(data=e)
        await pager.do_paginator(ctx)

def setup(bot):
    bot.add_cog(tags(bot))