[README.md](https://github.com/user-attachments/files/24339501/README.md)
Telegram qBittorrent Magnet Bot
Telegram bot that accepts magnet links and sends them to a qBittorrent Web UI for downloading.
The bot lets you add torrents from Telegram, start/pause them with inline buttons, list active torrents, and pause everything with one command.

Features
Accepts magnet links directly in chat and forwards them to qBittorrent.

Inline Start / Pause / Info buttons for each added torrent.

/start and /help for basic usage instructions inside Telegram.

/list to see current torrents with progress and size.

/stopall to pause all torrents in qBittorrent.

Prerequisites
Python 3.8+ installed on your machine (Windows is supported).

A Telegram bot token from @BotFather.

qBittorrent installed with Web UI enabled and reachable from where the bot runs.

Installation:
https://github.com/mohanmaniac26-maker/Magnetic-Link-to-qbit

Create and activate virtual environment (optional but recommended)

bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
Install dependencies

bash
pip install python-telegram-bot qbittorrent-api
qBittorrent Web UI Setup
Open qBittorrent.

Go to Tools → Options → Web UI.

Enable “Web User Interface (Remote control)”.

Set:

Host: 0.0.0.0 (or leave default if only local).

Port: for example 8080.

Username: e.g. admin.

Password: e.g. Password.

Apply and restart qBittorrent.

Test in a browser: open http://127.0.0.1:8080 and confirm the Web UI loads.

Configuration
Open main.py and set these values near the top:

python
BOT_TOKEN   = "YOUR_TELEGRAM_BOT_TOKEN"
QB_HOST     = "127.0.0.1"      # or your LAN IP, e.g. "192.168.0.1"
QB_PORT     = 8080             # must match Web UI port
QB_USERNAME = "admin"
QB_PASSWORD = "password"
Make sure these match your qBittorrent Web UI settings.

Running the Bot
From the project folder:

bash
python main.py
You should see log messages that the bot started and connected to qBittorrent.
Open Telegram, find your bot, and press Start.

Usage
/start
Shows a welcome message and basic instructions.

/help
Lists available commands and how to use the bot.

/list
Shows up to 10 torrents with:

Name

Progress

Size

Short hash

/stopall
Pauses all torrents in qBittorrent.

Send a magnet link
Just paste a magnet link into chat.
The bot will:

Add it to qBittorrent.

Reply with torrent name, size, and hash.

Show three buttons:

▶️ Start – resume the torrent.

⏸️ Pause – pause the torrent.

ℹ️ Info – show current progress, speeds, and size.

Common Issues
1. Connection refused to qBittorrent
If you see something like:

Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it

Check:

qBittorrent is running.

Web UI is enabled and port matches QB_PORT.

You can open http://QB_HOST:QB_PORT in a browser on the bot machine.

Firewall is not blocking the port.

2. Authentication errors
If the bot says login failed:

Double-check QB_USERNAME and QB_PASSWORD in main.py.

Make sure they match the Web UI credentials in qBittorrent settings.

Project Structure
text
magnetiche/
├─ main.py          # Telegram bot + qBittorrent integration
├─ README.md        # This file
└─ .venv/           # Optional Python virtual environment (ignored in git)
Roadmap / Ideas
Add command to delete torrents from Telegram.

Support setting download category or save path.

Show per-torrent download/upload speeds in /list.

Docker file for easy deployment.

License
Add your preferred license here (e.g. MIT, Apache-2.0) and include the license file in the repo.

