import discord
from discord.ext import commands
import aiohttp
import json
import re
import os
import random

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$>', intents=intents)

pattern = re.compile(r"^(C[a-zA-Z0-9]{33})$")
db_file = "airdop_db.json"
dev_role_id = 1220802801924444371

def load_db():
    try:
        with open(db_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_db(db):
    with open(db_file, "w") as file:
        json.dump(db, file)

def has_required_role(ctx):
    role = discord.utils.get(ctx.guild.roles, id=dev_role_id)
    return role in ctx.author.roles

@bot.command(name='verify')
async def verify_wallet(ctx, address: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://explorer.cmusic.ai/ext/getaddress/{address}") as response:
            if response.status == 200:
                data = await response.json()
                json_data = json.dumps(data, indent=2)
                await ctx.send("```json\n" + json_data + "```")
            else:
                await ctx.send("Failed to fetch address information.")

@bot.event
async def on_message(message):
    if message.channel.id == 1220821915586007090 and message.author != bot.user:
        if pattern.match(message.content):
            db = load_db()
            user_id = str(message.author.id)
            if any(entry["user_id"] == user_id and entry["wallet"] == message.content for entry in db):
                await message.author.send("Sorry, you have already entered the Cmusic Airdrop!")
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://explorer.cmusic.ai/ext/getaddress/{message.content}") as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("error") == "address not found.":
                                await message.author.send("Oops, Are you sure that's a Cmusic wallet? Please verify that it is the correct wallet and try again.")
                            else:
                                db.append({"user_id": user_id, "wallet": message.content})
                                save_db(db)
                                await message.author.send("Congrats! You have successfully entered into the Cmusic Airdrop!")
                        else:
                            await message.author.send("Failed to fetch address information.")
        else:
            await message.author.send("Oops, Are you sure that's a Cmusic wallet? Please verify that it is the correct wallet and try again.")
    await bot.process_commands(message)

@bot.command()
@commands.check(has_required_role)
async def entries(ctx):
    db = load_db()
    await ctx.send(f"Total number of entries: {len(db)}")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command()
@commands.check(has_required_role)
async def cleardb(ctx):
    os.remove(db_file)
    await ctx.send("Database cleared successfully.")

@bot.command()
@commands.check(has_required_role)
async def endairdrop(ctx, num_winners: int):
    db = load_db()
    winners = random.sample(db, min(num_winners, len(db)))
    winners_list = "\n".join([f"{index + 1}) <@{winner['user_id']}> - {winner['wallet']}" for index, winner in enumerate(winners)])
    announcement = f"Congrats! You have won the Cmusic airdrop! Your funds should be automatically deposited into the wallets you provided. Here are the winners:\n{winners_list} \n\n New airdrop has started, re-enter your wallets!"
    await ctx.send(announcement)
    os.remove(db_file)

bot.run('TOKEN')
