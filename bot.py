"""
Cerberus - Discord Welcome & Verification Bot
-----------------------------------------------
Welcomes new members, verifies them via a button, and automatically
assigns a configured role once they pass verification.
"""

import os
import logging

import discord
from discord.ext import commands

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("cerberus")

# ---------------------------------------------------------------------------
# Configuration (all via environment variables — never hardcode secrets)
# ---------------------------------------------------------------------------
TOKEN = os.environ.get("DISCORD_TOKEN")
GUILD_ID = int(os.environ.get("GUILD_ID", "0")) or None
WELCOME_CHANNEL_ID = int(os.environ.get("WELCOME_CHANNEL_ID", "0")) or None
VERIFIED_ROLE_ID = int(os.environ.get("VERIFIED_ROLE_ID", "0")) or None
VERIFY_CHANNEL_ID = int(os.environ.get("VERIFY_CHANNEL_ID", "0")) or None

if not TOKEN:
    raise SystemExit("Missing DISCORD_TOKEN environment variable. Set it before starting the bot.")

intents = discord.Intents.default()
intents.members = True  # required to detect joins and manage roles
intents.message_content = False

bot = commands.Bot(command_prefix="!", intents=intents)


# ---------------------------------------------------------------------------
# Verification View (persistent button)
# ---------------------------------------------------------------------------
class VerifyView(discord.ui.View):
    """A persistent view with a single 'Verify' button."""

    def __init__(self):
        super().__init__(timeout=None)  # persistent view, survives restarts

    @discord.ui.button(
        label="✅ Verify",
        style=discord.ButtonStyle.success,
        custom_id="cerberus_verify_button",
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user

        if guild is None or not isinstance(member, discord.Member):
            await interaction.response.send_message(
                "This button only works inside the server.", ephemeral=True
            )
            return

        role = guild.get_role(VERIFIED_ROLE_ID) if VERIFIED_ROLE_ID else None
        if role is None:
            await interaction.response.send_message(
                "⚠️ Verification role is not configured yet. Please contact an admin.",
                ephemeral=True,
            )
            log.warning("VERIFIED_ROLE_ID is not set or invalid.")
            return

        if role in member.roles:
            await interaction.response.send_message(
                "You're already verified! 🐺", ephemeral=True
            )
            return

        try:
            await member.add_roles(role, reason="Passed Cerberus verification")
            await interaction.response.send_message(
                f"✅ You've been verified, {member.mention}! Welcome aboard.", ephemeral=True
            )
            log.info("Verified member %s (%s)", member, member.id)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to assign that role. Please contact an admin.",
                ephemeral=True,
            )
            log.error("Missing permissions to assign role %s to %s", role, member)


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------
@bot.event
async def on_ready():
    bot.add_view(VerifyView())  # re-register persistent view after restarts
    log.info("Cerberus is online as %s (ID: %s)", bot.user, bot.user.id)


@bot.event
async def on_member_join(member: discord.Member):
    channel = None
    if WELCOME_CHANNEL_ID:
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if channel is None:
        channel = discord.utils.find(
            lambda c: isinstance(c, discord.TextChannel) and c.permissions_for(member.guild.me).send_messages,
            member.guild.text_channels,
        )
    if channel is None:
        return

    embed = discord.Embed(
        title="🐺 A new member has arrived!",
        description=(
            f"Welcome to **{member.guild.name}**, {member.mention}!\n\n"
            f"To gain access to the rest of the server, please verify yourself "
            f"by clicking the button below."
        ),
        color=discord.Color.dark_red(),
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="Cerberus Guardian Bot")

    verify_channel_mention = ""
    if VERIFY_CHANNEL_ID:
        verify_channel_mention = f"\nHead over to <#{VERIFY_CHANNEL_ID}> to verify."

    try:
        await channel.send(
            content=f"{member.mention} just joined!{verify_channel_mention}",
            embed=embed,
        )
    except discord.Forbidden:
        log.error("Missing permission to send welcome message in %s", channel)


# ---------------------------------------------------------------------------
# Slash / prefix command to (re)post the verification panel
# ---------------------------------------------------------------------------
@bot.command(name="setup_verify")
@commands.has_permissions(administrator=True)
async def setup_verify(ctx: commands.Context):
    """Posts the verification embed + button in the current channel. Admin only."""
    embed = discord.Embed(
        title="🔐 Server Verification",
        description=(
            "Click the button below to verify yourself and unlock access "
            "to the rest of the server."
        ),
        color=discord.Color.dark_red(),
    )
    embed.set_footer(text="Cerberus Guardian Bot")
    await ctx.send(embed=embed, view=VerifyView())


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need administrator permissions to run this command.")
    else:
        log.exception("Command error: %s", error)


if __name__ == "__main__":
    bot.run(TOKEN)
