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

bot = commands.Bot(command_prefix=r'exe!', description="Discord.exe", case_insensitive=True)
bot.settings = settings

@bot.event
async def on_ready():
    await load_mods()
    print("Connected as:")
    print(f"User: {bot.user}")
    print(f"ID: {bot.user.id}")
    print(f"With {len(bot.commands)} commands loaded")

@bot.event
async def on_command_error(ctx, error):
    error = getattr(error, 'original', error)
    ignored = (commands.CommandNotFound, commands.UserInputError, commands.CheckFailure)
    if isinstance(error, ignored):
        return
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    await ctx.send(error)

@bot.event
async def on_message_edit(before, after):
    if not after.embeds:
        await bot.process_commands(after)

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

@bot.check
async def globally_block_dms(ctx):
    if ctx.guild is None:
        if ctx.message.author.id == bot.owner_id:
            return True
        else:
            return False
    else:
        return True

bot.loop.create_task(presenceupdate())
bot.run(bot.settings['token'])
bot.close()