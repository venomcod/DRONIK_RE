import os
import sys
from pathlib import Path

import discord
from discord.ext import commands

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
TOKEN_FILE = BASE_DIR / "token.txt"

# Простой бот на discord.py
# 1. Установите библиотеку: python -m pip install -U discord.py
# 2. Создайте приложение в Discord Developer Portal
# 3. Скопируйте токен бота и сохраните в token.txt или в переменной окружения DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True  # важно для чтения текста сообщений
intents.members = True

# Здесь прямо перечисляются cogs, которые бот должен загрузить.
# Укажите имена файлов без расширения .py из папки cogs.
COGS = [
    'general',
    'fun',
    #'music_windows',
    'music_linux',
    'moderate',
]

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:
        await self.load_cogs()

    async def load_cogs(self) -> None:
        for cog_name in COGS:
            try:
                await self.load_extension(f"cogs.{cog_name}")
                print(f"Loaded cog: {cog_name}")
            except Exception as exc:
                print(f"Failed to load cog {cog_name}: {exc}")


bot = MyBot()


@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user} (ID: {bot.user.id})")
    print("Ready to receive commands.")


def get_token() -> str | None:
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if token:
            return token
    return os.getenv("DISCORD_TOKEN")


if __name__ == "__main__":
    token = get_token()
    if not token:
        raise SystemExit(
            "ERROR: token not found. Добавьте token.txt в проект или задайте переменную DISCORD_TOKEN"
        )
    bot.run(token)
