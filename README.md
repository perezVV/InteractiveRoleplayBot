## Introduction

This project is a Discord bot that provides the ability to create custom and immersive roleplay environments. 
All existing commands, as well as their descriptions, can be discovered by using `/help` and `/adminhelp`.

### Features
- Rooms: *Assign text channels as rooms with descriptions based on the channel topic.*
- Players: *Assign users as players with appearances, clothing, and inventories.*
- Movement: *Players may move between rooms and speak with fellow players who are present.*
- Items & Objects: *Add custom items, lockable containers, and decorative objects to rooms. Players may inspect them for further details.*
- Exits: *Create room connections with lockable doors using custom key items.*
- Rolls: *Roll dice to decide things randomly.*
- Chat History: *Retrieve chat logs from the previous five minutes if Discord clears them.*
- Admin Control: *Inspect, edit, and create all aspects of rooms, items, objects, and players. Pause player commands individually or globally.*

## Bot setup
This bot is not currently available via one singular invite link; unfortunately, we are still very small scale. This means you will have to create the bot and host it yourself. The process is easy, and detailed below.

- Go to the [Discord Developer Portal](https://discord.com/developers/applications).
- Log in to your Discord account.
- Click **New Application** and name your bot—feel free to give it whatever name and profile picture you like. Personally, I think it's fun to make it fit the theme of the roleplay.
- Navigate to the **Bot** tab in your application settings.
- Click **Reset Token** and confirm. Copy it and keep it somewhere safe—you'll need this to connect the source code to your bot later (more information about this in the **installation** section). Do not share your token with anyone you don't trust.
- Enable all Privileged Gateway Intents (Presence, Server Members, and Message Content).
- Go to the OAuth2 section.
  - Under the checkbox, select **bot**.
  - Check **Administrator** permissions.
  - Use the generated URL to invite the bot to your server.

## Installation
Download and extract (or `git clone`) this project. Downloading can be done by clicking on the "Code" button, then on "Download ZIP."

Create a text document in the project folder. Inside, paste the following:
```
guild_id=your_server_id
token=your_bot_token
```
Replace `your_server_id` with your server's ID (right-click on the server in Discord and select **Copy Server ID**. Note that you need to have Developer Mode enabled, which can be found in the 'Advanced' section of Discord's account settings.)
Replace `your_bot_token` with the token you gained from the **Discord Developer Portal**.

When saving the file, name it `.env` and select "All Files" as the file type rather than `.txt`. Do not include `.txt` at the end of the file name.

On Windows, you can simply double click on `run.bat`.

On Mac and Linux, you can run `run.sh` instead. This may require marking the script as executable.

## Server set up
By this point, you should have your own custom roleplay bot on your server. What you do from here is entirely your choice—still, we'd like to give you a few tips on getting started with creating new environments.

- When assigning rooms to text channels and players to Discord users, you will need to give the bot the ID of each respectively, which can be acquired by right clicking and selecting **Copy Channel/User ID**. For this, Developer Mode must be enabled. As mentioned previously, this can be enabled by navigating to the 'Advanced' section of Discord's account settings.
- To make it so each player may only see the room that they are currently in, they should be given a 'Player' role—though, feel free to call it something else. In each room's channel permissions, you must deny the Player role from seeing the channel and its chat history.
  - This is mostly for ease of access when swapping a player into a spectator. To do so, simply remove their Player role.
- When a player is assigned to a user, you must then use the `/drag` command to place them into a room.
