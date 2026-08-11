import asyncio
import random
import discord
from discord.ext import commands


class Shuffle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.waiting_for_join = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            event = self.waiting_for_join.pop(member.id, None)
            if event is not None:
                event.set()

    async def _wait_for_member_to_join(self, ctx: commands.Context, member: discord.Member, timeout: int = 60*60):
        await ctx.send(f"{member.mention} вышел из голосового канала. Жду, пока он зайдёт снова...")
        event = asyncio.Event()
        self.waiting_for_join[member.id] = event
        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            self.waiting_for_join.pop(member.id, None)
            await ctx.send(f"{member.mention} так и не зашёл в голосовой канал за {timeout} секунд.")
            return False
        return True

    @commands.hybrid_command(name="shuffle")
    async def shuffle(self, ctx: commands.Context, member: discord.Member, count: int = 3):
        allowed_users = {499507046681673728, 695855560402403338, 1060658816540213268}

        if ctx.author.id not in allowed_users:
            await ctx.send("Даже не пробуй, жалкий смертный")
            return

        if member.voice is None or member.voice.channel is None:
            if not await self._wait_for_member_to_join(ctx, member):
                return

        first_channel = member.voice.channel
        first_channel_id = first_channel.id

        channels = [
            1048224741422542868,
            1479487550027468962,
            1205551019572854835,
            1279394019184476192,
            1436709459744264324,
            1316393262042320996,
        ]

        channels = [channel_id for channel_id in channels if channel_id != first_channel_id]

        if not channels:
            await ctx.send("Нет доступных каналов для перемещения")
            return

        attempted = 0
        while attempted < count:
            if member.voice is None or member.voice.channel is None:
                if not await self._wait_for_member_to_join(ctx, member):
                    return

            target_channel_id = random.choice(channels)
            target_channel = ctx.guild.get_channel(target_channel_id)

            if target_channel is None:
                print(f"Канал {target_channel_id} не найден")
                break

            try:
                await member.move_to(target_channel)
            except Exception as exc:
                print(f"Не удалось переместить {member.mention} в канал {target_channel.name}: {exc}")

            attempted += 1

        if member.voice is None or member.voice.channel is None:
            if not await self._wait_for_member_to_join(ctx, member):
                return

        try:
            await member.move_to(first_channel)
        except Exception as exc:
            print(f"Не удалось вернуть {member.mention} в канал {first_channel.name}: {exc}")
            return

        await ctx.send(f"{member.mention} был перемещён и возвращён в {first_channel.mention}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Shuffle(bot))
