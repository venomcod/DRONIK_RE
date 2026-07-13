import discord
from discord.ext import commands

class Function(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _send_reply(self, ctx: commands.Context, content: str):
        if ctx.interaction is not None:
            try:
                if not ctx.interaction.response.is_done():
                    await ctx.interaction.response.send_message(content)
                else:
                    await ctx.interaction.followup.send(content)
            except (discord.NotFound, discord.HTTPException):
                await ctx.channel.send(content)
        else:
            await ctx.send(content)

    @commands.hybrid_command(name="delete")
    async def delete(self, ctx: commands.Context, channel: discord.TextChannel, count: int):
        """Удаляет указанное количество сообщений из канала"""
        permissions = channel.permissions_for(ctx.author)
        if not permissions.manage_messages:
            return await self._send_reply(ctx, "У тебя нет права на удаление сообщений в этом канале")

        if count > 100:
            return await self._send_reply(ctx, "Нельзя удалять больше 100 сообщений за раз")
        if count <= 0:
            return await self._send_reply(ctx, "Впишите число больше 0")

        if ctx.interaction is not None and not ctx.interaction.response.is_done():
            await ctx.defer()

        try:
            deleted = await channel.purge(limit=count)
            await self._send_reply(ctx, f"Удалено {len(deleted)} сообщений в канале {channel.mention}")
        except discord.Forbidden:
            await self._send_reply(ctx, f"У бота нет прав на удаление сообщений в канале {channel.mention}")
        except Exception as exc:
            await self._send_reply(ctx, f"Не удалось удалить сообщения в канале {channel.mention}: {exc}")
    
    @commands.hybrid_command(name="avatar")
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        """Присылает сыллку на аватар пользователя"""
        target = member or ctx.author
        try:
            ava = target.avatar.url
            await ctx.send(ava)
        except Exception:
            await ctx.send(f"Не удалось получить аватар {target.mention}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Function(bot))