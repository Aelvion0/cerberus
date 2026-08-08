#  Cerberus - Discord Welcome & Verification Bot

Cerberus greets new members, verifies them with a button, and automatically
grants a configured role once they pass verification.

## Features
-  Sends a welcome embed when a new member joins
-  Persistent "Verify" button (survives bot restarts)
-  Automatically assigns a role after successful verification
-  `!setup_verify` admin command to (re)post the verification panel in any channel

## Setup

### 1. Create the Discord bot
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) -> New Application -> name it **Cerberus**.
2. Upload `cerberus_pfp.png` (included in this repo) as the application/bot icon.
3. Under **Bot**, click "Add Bot", then enable:
- `SERVER MEMBERS INTENT` (required to detect joins and manage roles)
4. Copy the **Bot Token** - you'll need it for `DISCORD_TOKEN`.
5. Under **OAuth2 -> URL Generator**, select scopes `bot`, and permissions:
- `Manage Roles`, `Send Messages`, `Embed Links`, `Read Message History`, `View Channels`
6. Use the generated URL to invite Cerberus to your server.

> ! Make sure the bot's role in Server Settings -> Roles is placed **above** the role it needs to assign (Cerberus can only grant roles below its own position).

### 2. Configure environment variables
Copy `.env.example` to `.env` and fill in:

```
DISCORD_TOKEN=your-bot-token-here
GUILD_ID=your-server-id
WELCOME_CHANNEL_ID=your-welcome-channel-id