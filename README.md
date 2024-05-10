# Cmusic Crypto Airdrop Bot

## Introduction
Cmusic is an open-source Discord bot designed to facilitate cryptocurrency airdrops, specifically for music-related tokens within Discord communities. This bot helps artists and music communities distribute crypto assets effortlessly to fans and members, enhancing engagement and promoting new music projects.

## Setup

After downloading the files make sure to rename the example env to .env

Step 1) Setup a discord bot, I recommend to look up videos on this for more details if your confused.
  - Visit the discord developer page
  - Create a application
  - Create a bot in the application
  - Reset the token & copy the new one (DO NOT SHARE THIS EVER!!)
  - Scroll down and make sure to enable all indents.
  - Add the token to BOTTOKEN in the env

Step 2) Setting up the RPC (better details in readme soon or contact discord)
  - After you setup the coin RPC your going to need to modify these enviroment tables:
  rpc_user = your-rpc-username     <-- Username for the RPC 
  rpc_password = your-rpc-password <-- Password for the RPC 
  rpc_port = your-rpc-port         <-- Port for the RPC (Likely the default)
  rpc_ip = your-rpc-ip             <-- IP for the RPC  (Likely 127.0.0.1 for locally ran rpc's)
  from_address = wallet-address    <-- Wallet Address for the RPC  (Donation wallet address, make sure to give it funds!)


Step 3) Dev role
  - In your discord server create a 'developer' role or a 'admin role' (one with higher permissions, anyone with this role can use the bot)
  - Make sure in your account settings discord developer mode is on
  - After making the role add it to your profile, right click it and copy the role ID
  - Replace your-discord-admin-role-id in the .env file

Step 4) Explorer url
  - Get the URL for your explorer
  - replace the value for explorer_url in the .env, it should be in this format: https://example.com or http://example.com (replace example.com with your URL)

Step 5) Replace ticker value with your ticker (such as RVN, CMS, etc)

Step 6) Regex
 - This depends on your coin mostly but for most ravencoin based coins get the first character of your coin wallet address (Example: Raven wallets always start with R)
 - In the regex variable in .env find ^(R[a-zA-Z0-9]{33})$ and replace R with your first letter (After the ^( )
 - For more custom situations look up how to create a custom regex

Step 7)
  - airdropchannel, this is the channel ID for which the users will enter there wallet address into to enter the airdrop.

If you required help in any of these steps you may join our [discord](https://discord.gg/3zAprS9eBp)

