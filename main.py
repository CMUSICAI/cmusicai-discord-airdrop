import discord
from discord.ext import commands
import aiohttp
import json
import re
import os
import random
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

load_dotenv()
Token = os.environ.get("BOTTOKEN")

rpc_user = os.environ.get("rpc_user")
rpc_password = os.environ.get("rpc_password")
rpc_port = os.environ.get("rpc_port")
rpc_ip = os.environ.get("rpc_ip")
from_address = os.environ.get("from_address")
eurl = os.environ.get("explorer_url")
ticker = os.environ.get("ticker")
regexwallet = os.environ.get("regex")
airdropchannel = os.environ.get("airdropchannel")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$>', intents=intents)

pattern = re.compile(r""+regexwallet)
db_file = "airdop_db.json"
dev_role_id = int(os.environ.get("dev_role_id"))

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

def send_coins(rpc_user, rpc_password, rpc_port, rpc_ip, from_address, to_address, amount):
    rpc_url = f'http://{rpc_user}:{rpc_password}@{rpc_ip}:{rpc_port}'
    headers = {'content-type': 'application/json'}

    def send_coins(from_address, to_address, amount):
        payload = {
            "method": "sendtoaddress",
            "params": [to_address, amount],
            "jsonrpc": "2.0",
            "id": "1"
        }
        response = requests.post(rpc_url, data=json.dumps(payload), headers=headers).json()
        return response

    response = send_coins(from_address, to_address, amount)
    if response.get('error') is not None:
        print("Error:", response['error'])

    return response

def get_balance(username, password, host, port, address):
    url = f'http://{host}:{port}'
    auth = HTTPBasicAuth(username, password)
    data = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "getbalance",
        "params": []
    }
    response = requests.post(url, json=data, headers={'Content-Type': 'application/json'}, auth=auth)
    if response.status_code != 200:
        raise Exception(f"HTTP error: {response.json()}")
    result = response.json()
    if 'error' in result and result['error'] is not None:
        raise Exception(result['error'])
    return result['result']


@bot.command(name='verify')
async def verify_wallet(ctx, address: str):
    if pattern.match(address):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{eurl}/ext/getaddress/{address}") as response:
                if response.status == 200:
                    data = await response.json()
                    json_data = json.dumps(data, indent=2)
                    await ctx.send("```json\n" + json_data + "```")
                else:
                    await ctx.send("Failed to fetch address information, wallet may not be valid or no transactions [failed explorer check].")
    else:
        await ctx.send("Wallet address does not seem valid, [failed regex check].")

@bot.command(name='airdropbal')
@commands.check(has_required_role)
async def airdropbal(ctx):
    balance_response = get_balance(rpc_user, rpc_password, rpc_ip, rpc_port, from_address)
    await ctx.send(f"{ticker} Balance: " + str(balance_response))

@bot.event
async def on_message(message):
    if message.channel.id == airdropchannel and message.author != bot.user:
        if pattern.match(message.content):
            db = load_db()
            user_id = str(message.author.id)
            if any(entry["user_id"] == user_id and entry["wallet"] == message.content for entry in db):
                await message.author.send(f"Sorry, you have already entered the {ticker} Airdrop!")
            else:
                db.append({"user_id": user_id, "wallet": message.content})
                save_db(db)
                await message.author.send(f"Congrats! You have successfully entered into the {ticker} Airdrop!")
        else:
            await message.author.send(f"Oops, Are you sure that's a {ticker} wallet? Please verify that it is the correct wallet and try again.")
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
async def endairdrop(ctx, num_winners: int, coin_amount: int):
    if num_winners <= 0:
        await ctx.send("Please provide a valid number of winners.")
        return

    db = load_db()
    winners = random.sample(db, min(num_winners, len(db)))
    winners_list = "\n".join([f"{index + 1}) <@{winner['user_id']}> - {winner['wallet']}" for index, winner in enumerate(winners)])
    
    results = []
    transaction_explorer_links = []
    for winner in winners:
        sendresult = send_coins(rpc_user, rpc_password, rpc_port, rpc_ip, from_address, winner['wallet'], coin_amount)
        result = sendresult.get('result')
        results.append(result)
        transaction_explorer_links.append(f"[Transaction Explorer]({eurl}/tx/{result})")

    announcement = f"Behold the victorious! Below, you'll find the list of winners for the {coin_amount} `{ticker}` airdrop. Your funds should be automatically deposited into the wallets you provided. "

    winners_list_with_links = "\n".join([f"{index + 1}) <@{winner['user_id']}> - {winner['wallet']} {link}" for index, (winner, link) in enumerate(zip(winners, transaction_explorer_links))])

    announcement += f"\n\n {winners_list_with_links}\n\n `New airdrop has begun! Re-Enter your wallet address to participate` @everyone`!`"
    await ctx.send(announcement)
    os.remove(db_file)


bot.run(Token)
