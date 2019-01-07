import discord
from discord.ext import commands
import asyncio
from fuzzywuzzy import process
from discord.ext.commands.cooldowns import BucketType

class tags:

    def __init__(self, bot):
        self.bot = bot
        self.tags = {}
        self.bot.loop.create_task(self.load_tags())

    def __unload(self):
        self.bot.loop.create_task(self.unload_tags())
        print('Tags cog unloaded')

    async def on_guild_remove(self, guild):
        #cleans up after leaving guild
        try:
            self.tags.pop(guild.id)
        except:
            pass

    async def load_tags(self):
        #Create quarry for reference
        #CREATE TABLE tags(guild_id BIGINT unique, tag_name text, content text, uses BIGINT, owner_id BIGINT);
        fetch = await self.bot.db.fetch("SELECT * FROM tags;")
        if fetch is None:
            print('No tags found')
            return
        temp_tags = {}
        for item in fetch:
            try:
                temp_tags[item[0]]
            except:
                temp_tags[item[0]] = {}
            temp_tags[item[0]][item[1]] = {}
            temp_tags[item[0]][item[1]]['content'] = item[2]
            temp_tags[item[0]][item[1]]['uses'] = item[3]
            temp_tags[item[0]][item[1]]['owner_id'] = item[4]
        self.tags = temp_tags
        print('Tags loaded')

    async def unload_tags(self):
        #(guild_id, tag_name, content, uses, owner_id)
        list_of_sets = []
        for guild_id in self.tags:
            for tag_name in self.tags[guild_id]:
                temp_set = (guild_id, tag_name, self.tags[guild_id][tag_name]['content'], self.tags[guild_id][tag_name]['uses'], self.tags[guild_id][tag_name]['owner_id'])
                list_of_sets.append(temp_set)
        await self.bot.db.execute("DELETE FROM tags;")
        await self.bot.db.executemany("INSERT INTO tags(guild_id, tag_name, content, uses, owner_id) VALUES ($1, $2, $3, $4, $5)", list_of_sets)
        print('Tags saved and unloaded')

    @commands.group(invoke_without_command=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def tag(self, ctx, *, tag_name: commands.clean_content()):
        """Create and recall info"""
        tag_name = tag_name.lower()
        guild = ctx.guild
        try:
            self.tags[guild.id]
        except:
            self.tags[guild.id] = {}
        if not tag_name in self.tags[guild.id]:
            try:
                matches = process.extract(tag_name, self.tags[guild.id].keys(), limit=2)
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
            self.tags[guild.id][tag_name]['uses'] += 1
            return await ctx.send(self.tags[guild.id][tag_name]['content'])

    @tag.command(aliases=['add'])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def create(self, ctx, tag_name: commands.clean_content(), *, content: commands.clean_content()):
        """Create a tag"""
        guild = ctx.guild
        try:
            self.tags[guild.id]
        except:
            self.tags[guild.id] = {}
        tag_name = tag_name.lower()
        if tag_name in self.tags[guild.id]:
            return await ctx.send("Tag already exist")
        else:
            self.tags[guild.id][tag_name] = {}
            self.tags[guild.id][tag_name]['content'] = content
            self.tags[guild.id][tag_name]['uses'] = 0
            self.tags[guild.id][tag_name]['owner_id'] = ctx.author.id
            await ctx.send(f"Tag created")

    @tag.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def edit(self, ctx, tag_name: commands.clean_content(), *, content: commands.clean_content()):
        """Edit a tag"""
        guild = ctx.guild
        try:
            self.tags[guild.id]
        except:
            self.tags[guild.id] = {}
        tag_name = tag_name.lower()
        if tag_name not in self.tags[guild.id]:
            return await ctx.send(f"Tag not found")
        if ctx.author.id != self.tags[guild.id][tag_name]['owner_id']:
            return await ctx.send(f"You do not own this tag")
        else:
            self.tags[guild.id][tag_name]['content'] = content
            await ctx.send(f"Edited tag")

    @tag.command()
    async def delete(self, ctx, tag_name: commands.clean_content()):
        """Deletes a tag

        Must be the tag owner or have the admin perm
        """
        guild = ctx.guild
        try:
            self.tags[guild.id]
        except:
            self.tags[guild.id] = {}
        tag_name = tag_name.lower()
        if tag_name not in self.tags[guild.id]:
            return await ctx.send(f"Tag not found")
        if ctx.author.id == self.tags[guild.id][tag_name] or ctx.author.guild_permissions.administrator:
            self.tags[guild.id].pop(tag_name)
            return await ctx.send("Tag deleted")
        else:
            await ctx.send("You are not the tag owner or an admin")

    @tag.command()
    async def info(self, ctx, tag_name: commands.clean_content()):
        """Get info on a tag"""
        guild = ctx.guild
        try:
            self.tags[guild.id]
        except:
            self.tags[guild.id] = {}
        tag_name = tag_name.lower()
        if tag_name not in self.tags[guild.id]:
            return await ctx.send(f"Tag not found")
        tag_owner = guild.get_member(self.tags[guild.id][tag_name]['owner_id'])
        e = discord.Embed(title=tag_name, color=discord.Color.dark_purple())
        e.set_thumbnail(url=tag_owner.avatar_url)
        e.add_field(name="Uses:", value=self.tags[guild.id][tag_name]['uses'])
        e.add_field(name="Owner:", value=f"{tag_owner.mention}\n{str(tag_owner)}")
        await ctx.send(embed=e)

    @tag.command(name='list')
    async def _list(self, ctx, member: discord.Member = None):
        """Look up tag list for yourself/another member"""
        guild = ctx.guild
        

def setup(bot):
    bot.add_cog(tags(bot))
