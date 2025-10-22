import discord
from discord.ext import commands
from discord import option

class QuoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Standardwerte (kann man später über Slash Commands ändern)
        self.quote_channel_id = None
        self.quote_emoji = "⭐"
        self.min_reactions = 1

    # === REAKTIONEN BEOBACHTEN ===
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if not self.quote_channel_id:
            return  # Kein Quote-Channel gesetzt

        if str(payload.emoji) != self.quote_emoji:
            return

        if payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # Prüfen, ob genügend Reaktionen vorhanden sind
        reaction = discord.utils.get(message.reactions, emoji=self.quote_emoji)
        if not reaction or reaction.count < self.min_reactions:
            return

        quote_channel = guild.get_channel(self.quote_channel_id)
        if not quote_channel:
            print("⚠️ Quote-Channel nicht gefunden!")
            return

        quote_link = f"https://discord.com/channels/{guild.id}/{channel.id}/{message.id}"

        # Doppelte Quotes vermeiden
        async for msg in quote_channel.history(limit=100):
            if quote_link in msg.content:
                return

        embed = discord.Embed(
            description=message.content or "*[Keine Nachricht]*",
            color=discord.Color.gold()
        )
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.add_field(name="Link", value=f"[Zur Nachricht]({quote_link})", inline=False)
        embed.timestamp = message.created_at

        if message.attachments:
            embed.set_image(url=message.attachments[0].url)

        await quote_channel.send(embed=embed)
        print(f"⭐ Nachricht von {message.author} wurde gequotet!")

    # === SLASH BEFEHLE ===
    @commands.slash_command(description="Setze den Kanal, in den Quotes gepostet werden.")
    @option("channel", discord.TextChannel, description="Der Kanal, in den gequotete Nachrichten gepostet werden sollen.")
    async def setquotechannel(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        self.quote_channel_id = channel.id
        await ctx.respond(f"✅ Quote-Channel wurde auf {channel.mention} gesetzt.", ephemeral=True)

    @commands.slash_command(description="Setze das Emoji, das für Quotes verwendet wird.")
    @option("emoji", str, description="Das Emoji, das Quotes auslösen soll (z. B. ⭐)")
    async def setquoteemoji(self, ctx: discord.ApplicationContext, emoji: str):
        self.quote_emoji = emoji
        await ctx.respond(f"✅ Quote-Emoji wurde auf `{emoji}` gesetzt.", ephemeral=True)

    @commands.slash_command(description="Setze, wie viele Reaktionen benötigt werden, bevor gequotet wird.")
    @option("count", int, description="Anzahl benötigter Reaktionen", min_value=1, max_value=10)
    async def setquotethreshold(self, ctx: discord.ApplicationContext, count: int):
        self.min_reactions = count
        await ctx.respond(f"✅ Mindestanzahl der Reaktionen auf `{count}`` gesetzt.", ephemeral=True)

    @commands.slash_command(description="Zeigt die aktuelle Quote-Konfiguration.")
    async def quoteinfo(self, ctx: discord.ApplicationContext):
        channel = f"<#{self.quote_channel_id}>" if self.quote_channel_id else "❌ Nicht gesetzt"
        await ctx.respond(
            f"📋 **Quote-Einstellungen:**\n"
            f"**Channel:** {channel}\n"
            f"**Emoji:** {self.quote_emoji}\n"
            f"**Mindestreaktionen:** {self.min_reactions}",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(QuoteCog(bot))


    