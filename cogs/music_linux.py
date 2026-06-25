"""Music cog for Ubuntu Linux.

Assumes `ffmpeg` is installed system-wide (usually `/usr/bin/ffmpeg`).
Provide `FFMPEG_PATH` env var if ffmpeg is in a custom location.
"""
from __future__ import annotations

import os
import asyncio
import shutil
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands
from yt_dlp import YoutubeDL


def resolve_deno_path() -> Optional[str]:
    env_path = os.getenv('DENO_PATH')
    if env_path and Path(env_path).exists():
        return env_path

    candidate = Path.home() / '.deno' / 'bin' / 'deno'
    if candidate.exists():
        return str(candidate)

    candidate2 = Path.home() / '.deno' / 'bin' / 'deno.exe'
    if candidate2.exists():
        return str(candidate2)

    which = shutil.which('deno')
    return which

DENO_PATH = resolve_deno_path()

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'ignoreerrors': True,
    'default_search': 'auto',
    'jsruntimes': f'deno:{DENO_PATH}' if DENO_PATH else 'deno',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


class YTDLSource(discord.PCMVolumeTransformer):
    ytdl = YoutubeDL(YTDL_OPTIONS)

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.webpage_url = data.get('webpage_url')

    @classmethod
    async def from_url(cls, url: str, *, loop: Optional[asyncio.AbstractEventLoop] = None, ffmpeg_path: Optional[str] = None):
        loop = loop or asyncio.get_event_loop()
        search_source = url
        if not url.startswith(('http://', 'https://', 'www.')):
            search_source = f'ytsearch5:{url}'

        data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(search_source, download=False))

        if 'entries' in data:
            chosen = None
            for entry in data['entries']:
                if not entry:
                    continue
                if entry.get('is_live'):
                    continue
                if entry.get('url') is None and entry.get('webpage_url') is None:
                    continue
                chosen = entry
                break
            if chosen is None:
                raise ValueError('Не удалось найти доступный трек.')
            data = chosen

        filename = data.get('url') or data.get('webpage_url') or url

        executable = ffmpeg_path or os.getenv('FFMPEG_PATH') or 'ffmpeg'

        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS, executable=executable), data=data)


class MusicLinux(commands.Cog):
    """Basic music player cog tuned for Ubuntu Linux."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue = asyncio.Queue()

    @commands.command(name='join')
    async def join(self, ctx: commands.Context):
        if not ctx.author.voice:
            return await ctx.send('Вы должны быть в голосовом канале.')
        try:
            await ctx.author.voice.channel.connect()
            await ctx.send(f'Подключился к {ctx.author.voice.channel.name}')
        except RuntimeError as exc:
            if 'davey' in str(exc).lower() or 'voice' in str(exc).lower():
                return await ctx.send(
                    'Нужна голосовая библиотека для Discord. Установите davey: `python -m pip install davey`'
                )
            raise

    @commands.command(name='leave')
    async def leave(self, ctx: commands.Context):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send('Отключился от голосового канала')

    @commands.command(name='play')
    async def play(self, ctx: commands.Context, *, query: str):
        if not ctx.author.voice:
            return await ctx.send('Вы должны быть в голосовом канале.')

        if not ctx.voice_client:
            try:
                await ctx.author.voice.channel.connect()
            except RuntimeError as exc:
                if 'davey' in str(exc).lower() or 'voice' in str(exc).lower():
                    return await ctx.send(
                        'Нужна голосовая библиотека для Discord. Установите davey: `python -m pip install davey`'
                    )
                raise

        if not DENO_PATH and shutil.which('deno') is None:
            return await ctx.send(
                'Deno не найден. Установите Deno и добавьте его в PATH, или задайте переменную окружения DENO_PATH.'
            )

        ffmpeg_path = os.getenv('FFMPEG_PATH') or '/usr/bin/ffmpeg'
        try:
            source = await YTDLSource.from_url(query, loop=self.bot.loop, ffmpeg_path=ffmpeg_path)
        except Exception as exc:
            return await ctx.send(f'Не удалось получить трек: {exc}')

        def _play_next(err=None):
            coro = self._play_next_from_queue(ctx)
            fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
            try:
                fut.result()
            except Exception:
                pass

        if ctx.voice_client.is_playing():
            await self.queue.put(source)
            await ctx.send(f'Добавлено в очередь: {source.title}')
        else:
            ctx.voice_client.play(source, after=_play_next)
            await ctx.send(f'Играю: {source.title}')

    async def _play_next_from_queue(self, ctx: commands.Context):
        if self.queue.empty():
            return
        source = await self.queue.get()
        if not ctx.voice_client:
            return
        ctx.voice_client.play(source)

    @commands.command(name='pause')
    async def pause(self, ctx: commands.Context):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send('Пауза')

    @commands.command(name='resume')
    async def resume(self, ctx: commands.Context):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send('Возобновлено')

    @commands.command(name='queue')
    async def queue_list(self, ctx: commands.Context):
        if self.queue.empty():
            return await ctx.send('Очередь пуста.')

        items = list(self.queue._queue)
        lines = [f'{index + 1}. {item.title}' for index, item in enumerate(items)]
        await ctx.send('Очередь:\n' + '\n'.join(lines))

    @commands.command(name='skip')
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send('Сейчас ничего не играет.')

        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            ctx.voice_client.stop()
            await ctx.send('Трек пропущен. Играю следующий трек.')
            await self._play_next_from_queue(ctx)
        else:
            await ctx.send('Сейчас ничего не играет.')

    @commands.command(name='stop')
    async def stop(self, ctx: commands.Context):
        if ctx.voice_client:
            ctx.voice_client.stop()
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            await ctx.send('Остановлено и очередь очищена')


async def setup(bot: commands.Bot):
    await bot.add_cog(MusicLinux(bot))
