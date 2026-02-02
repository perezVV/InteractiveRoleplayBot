import asyncio
import os
import ssl
from pathlib import Path

import aiohttp
import certifi
import discord
from discord.ext import commands
from dotenv import load_dotenv

os.environ["BASE_PATH"] = Path(__file__).parent.resolve().as_posix()

def file_to_ext(str_path: str, base_path: str) -> str:
    # changes a file to an import-like string
    str_path = str_path.replace(base_path, "")
    str_path = str_path.replace("/", ".")
    return str_path.replace(".py", "")

def get_all_extensions(str_path: str, folder: str = "cogs") -> list[str]:
    # gets all extensions in a folder
    ext_files: list[str] = []
    loc_split = str_path.split(folder)
    base_path = loc_split[0]

    if base_path == str_path:
        base_path = base_path.replace("main.py", "")
    base_path = base_path.replace("\\", "/")

    if base_path[-1] != "/":
        base_path += "/"

    pathlist = Path(f"{base_path}/{folder}").glob("**/*.py")
    for path in pathlist:
        str_path = str(path.as_posix())
        str_path = file_to_ext(str_path, base_path)
        ext_files.append(str_path)

    return ext_files

load_dotenv()
GUILD = discord.Object(id=int(os.environ['guild_id']))

if not os.environ.get("CHATHISTORY_BASE_URL"):
    os.environ["CHATHISTORY_BASE_URL"] = "https://basic-discord-html-viewer.onrender.com/display?url="

class Client(commands.Bot):
    def __init__(self, *, intents:discord.Intents):
        super().__init__(intents=intents, command_prefix="/")

    async def setup_hook(self):
        self.remove_command("help")

        for ext_name in get_all_extensions(os.environ["BASE_PATH"]):
            await self.load_extension(ext_name)

        if not os.getenv("DONT_SYNC"):
            self.tree.copy_global_to(guild=GUILD)
            await self.tree.sync(guild=GUILD)

intents = discord.Intents.all()
client = Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged on as {client.user}!")

async def main():
    # fix for older systems with outdated ca certificates
    # note: discord.py does have a parameter in Client(...) for passing
    # connectors, but since connectors need to be made while the loop is
    # running, we have to set it after the Client is made, resulting
    # in this slight mess

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)

    client.http.connector = connector

    async with client:
        await client.start(os.environ["token"])

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
