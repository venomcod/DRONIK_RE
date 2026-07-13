from discord.ext import commands
import discord
class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="hello")
    async def hello(self, ctx: commands.Context):
        """Простая команда: отправляет ответ в канал."""
        await ctx.send(f"Привет, {ctx.author.mention}! Я работаю.")

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """Проверка отклика бота."""
        await ctx.send("Pong! 🏓")

    @commands.command(name="say")
    async def say(self, ctx: commands.Context, channel: discord.TextChannel, *, text: str):
        """Команда повторяет за пользователем."""
        try:
            await ctx.send(f"Сообщение отправлено:{text}")
            await channel.send(text)
        except:
            await ctx.send(f"Используйте только текстовые каналы!")
    
    @commands.command(name="pong")
    async def pong(self, ctx: commands.Context):
        await ctx.send("Ping! 🎾")

    @commands.command(name="sleep")
    async def sleep(self, ctx: commands.Context):
        try:
            is_owner = await self.bot.is_owner(ctx.author)
        except Exception:
            is_owner = False

        if not is_owner:
            await ctx.send('Только владелец бота может использовать эту команду.')
            return

        await ctx.send('Выключаюсь. Пока!')
        await self.bot.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
