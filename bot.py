import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# === KONFIGURATION ===
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
# =======================

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix=os.getenv("BOT_PREFIX"), intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Eingeloggt als {bot.user} ({bot.user.id})")

@bot.event
async def setup_hook():
    # Cog laden
    await bot.load_extension("cogs.quote")
    print("📚 Cog 'quote' geladen!")

    guild = discord.Object(id=GUILD_ID)
    await bot.sync_commands(guild_ids=[guild.id])
    print(f"🔁 Slash-Befehle synchronisiert (server-spezifisch: {GUILD_ID})")

bot.run(TOKEN)


