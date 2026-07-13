import discord
from discord.ext import commands

class Function(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.hybrid_command(name="delete", description="Удаляет определёное кол-во сообщений из чата")
    async def delete(self, ctx: commands.Context, channel: discord.TextChannel, *, count: int):
        premissions = channel.permissions_for(ctx.author)
        if not premissions.manage_messages:
            await ctx.send("У тебя нет права на удаление сообщений в этом канале")
        else:
            if count > 100:
                await ctx.send("Нельзя удалять больше 100 сообщений за раз")
            elif count <= 0:
                await ctx.send("Впишите число больше 0")
            else:
                try:
                    await channel.purge(limit=count)
                    await ctx.send(f"Удалено {count} сообщений в канале {channel.mention}")
                except:
                    await ctx.send(f"Не удалось удалить сообщения в канале {channel.mention}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Function(bot))