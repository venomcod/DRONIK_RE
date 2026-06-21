from discord.ext import commands

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
    async def say(self, ctx: commands.Context, *, text: str):
        """Команда повторяет за пользователем."""
        await ctx.send(text)
    
    @commands.command(name="pong")
    async def pong(self, ctx: commands.Context):
        await ctx.send("Ping! 🎾")


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
