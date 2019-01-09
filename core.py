import discord
import asyncio
from discord.ext import commands
import json
import glob
import datetime
import logging
import os
import typing
import importlib.util
import sys
import traceback
from bot_utils.danny_pager_temp import HelpPaginator, CannotPaginate
import asyncpg

#Logging setup
if os.path.exists('logs/discord.log'):
    os.remove('logs/discord.log')
with open('logs/discord.log', 'w+') as q:
    q.close()
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

with open("settings.json") as f:
    settings = json.load(f)
    f.close()

async def get_prefix(bot, message):
    if message.guild is None:
        return ""
    if message.guild.id in bot.prefixes:
        return commands.when_mentioned_or(*bot.prefixes[message.guild.id])(bot, message)
    else:
        return 'exe!'

bot = commands.Bot(command_prefix=get_prefix, description="Discord.exe", case_insensitive=True)
bot.remove_command('help')
bot.settings = settings
bot.start_time = datetime.datetime.utcnow()
bot.prefixes = {}
bot.tasks = []
bot.blacklist = []

#Copied from https://github.com/Rapptz/RoboDanny <3
@bot.command(name='help')
async def _help(ctx, *, command: str = None):
    """Shows help about a command or the bot"""
    try:
        if command is None:
            p = await HelpPaginator.from_bot(ctx)
        else:
            entity = bot.get_cog(command) or bot.get_command(command)
            if entity is None:
                clean = command.replace('@', '@\u200b')
                return await ctx.send(f'Command or category "{clean}" not found.')
            elif isinstance(entity, commands.Command):
                p = await HelpPaginator.from_command(ctx, entity)
            else:
                p = await HelpPaginator.from_cog(ctx, entity)
        await p.paginate()
    except Exception as e:
        await ctx.send(e)

@bot.event
async def on_ready():
    await connect_db()
    await load_mods()
    print("Connected as:")
    print(f"User: {bot.user}")
    print(f"ID: {bot.user.id}")
    print(f"With {len(bot.commands)} commands loaded")
    print("Connecting to Database")

@bot.event
async def on_message_edit(before, after):
    if not after.embeds:
        await bot.process_commands(after)

@bot.event
async def on_guild_join(guild):
    bot.prefixes[guild.id] = []
    bot.prefixes[guild.id].append('exe!')

@bot.event
async def on_guild_remove(guild):
    bot.prefixes.pop(guild.id)

async def load_mods():
    bot.load_extension('jishaku')
    found = glob.glob('modules/*.py')
    print('Begining cog loading')
    if not found:
        print('No cogs found')
        return
    loaded = []
    failed = []
    failedmsg = ""
    for cog in found:
        try:
            cog = cog.replace('.py', '')
            cog = cog.replace("\\", ".")
            bot.load_extension(cog)
            loaded.append(cog)
        except Exception as e:
            failed.append(cog)
            failedmsg += f"\n{cog}: {e}"
    print(f"Loaded: {loaded}")
    if failed:
        filename = str(datetime.datetime.now())
        filename = filename.replace(" ", "_")
        filename = filename.replace(":", "-")
        print(f"Failed: {failed}")
        print(f"Writing exception(s) to {filename}.log")
        with open(f"logs/{filename}.log", 'w+') as f:
            f.write(failedmsg)
            f.close()

async def connect_db():
    bot.db = await asyncpg.connect('postgresql://postgres@localhost/exe', password=bot.settings['db_pass'])
    print("Datebase loaded")
    for guild_id, prefix_list in await bot.db.fetch("SELECT * FROM prefixes;"):
        bot.prefixes[guild_id] = prefix_list
    print("Prefixes loaded")
    for user_id in await bot.db.fetch("SELECT * FROM blacklist;"):
        bot.blacklist.append(user_id)
    print("Blacklist loaded")

async def disconnect_db():
    await bot.db.execute("DELETE FROM prefixes;")
    await bot.db.executemany("INSERT INTO prefixes(guild_id, prefix_list) VALUES ($1, $2)", bot.prefixes.items())
    print("Prefixes unloaded")
    await bot.db.execute("DELETE FROM blacklist;")
    await bot.db.executemany("INSERT INTO blacklist VALUES($1)", bot.blacklist)
    print("Blacklist unloaded")
    await bot.db.close()
    print("Database unloaded")

async def presenceupdate():
    await bot.wait_until_ready()
    x = 0
    while True:
        servers = len(bot.guilds)
        members = len(bot.users)
        if x == 0:
            half = "{} servers".format(servers)
            x = 1
        elif x == 1:
            half = "{} users".format(members)
            x = 0
        await bot.change_presence(activity=discord.Game(f"exe!help | {half}"))
        await asyncio.sleep(300)

async def shutdown_bot():
    """Graceful shutdown"""
    await bot.change_presence(activity=discord.Game("Shutting down"))
    keys = list(bot.cogs.keys())
    for cog in keys:
        bot.unload_extension(cog)
        bot.remove_cog(cog)
    await asyncio.sleep(3)
    print("Extensions and cogs unloaded")
    await disconnect_db()
    print("Cleaned up. Now shutting down")
    await asyncio.sleep(10)

@bot.check
async def globally_block_dms(ctx):
    if ctx.guild is None:
        if ctx.message.author.id == bot.owner_id:
            return True
        else:
            return False
    else:
        return True

@bot.check
async def blacklist(ctx):
    if ctx.author.id in ctx.bot.blacklist:
        return False
    else:
        return True

bot.loop.create_task(presenceupdate())
bot.shutdown = shutdown_bot
bot.run(bot.settings['token'])
bot.close()