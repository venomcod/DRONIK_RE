from discord.ext import commands, tasks
import discord
from datetime import timedelta
from random import randint

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ruletka_for_demyan.start()
    

    @tasks.loop(hours=6)
    async def ruletka_for_demyan(self):
        guild_id = 849591676066725898
        user_id = 690242065157980180
        text_id = 1518211788846403675
        guild = self.bot.get_guild(guild_id)
        member = guild.get_member(user_id)
        text_chnl = guild.get_channel(text_id)
        rnd = randint(1, 100)
        if rnd <= 5:
            try:
                await member.ban(reason="Лох проиграл АХАХАХАХАХАХА")
                await text_chnl.send("АХАХАХАХА ЛОХ")
            except Exception as exc:
                print(f"Не удалось забанить {user_id}: {exc}")
                await text_chnl.send("АХХАХХАХ ПОХОЖЕ ЛОХ УЖЕ ЗАБАНЕН")   
        else:
            await text_chnl.send("к сожалению Демьян сегодня выжил")
        print("Была выполнена попытка")
    
    @commands.command("ruletka")
    async def ruletka(self, ctx: commands.Context):
        member = ctx.author
        guild_id = 849591676066725898
        demyan_id = 690242065157980180
        guild = self.bot.get_guild(guild_id)
        dema = guild.get_member(demyan_id)
        chnl = ctx.channel
        rndl = randint(1, 10)
        if member != dema:
            if rndl == 5:
                try:
                    until = discord.utils.utcnow() + timedelta(minutes=5)
                    await member.timeout(until)
                    await chnl.send(f"к сожалению {member.mention} проиграл. Выдано 5 минут мута")
                    print(f"{member.mention} ЛОХ")
                except:
                    await chnl.send(f"{member.mention} ПОХОЖЕ ОН ХУЙ ВАЖНЫЙ, не могу выдать мут")
                    print(f"{member.mention} ПИДР")
            else:
                await chnl.send(f"{member.mention} выжил, молодец")
        else:
            await chnl.send("А вот тебе нельзя пользоваться рулеткой")

    @commands.command(name="ruletka_user")
    async def ruletka_user(self, ctx: commands.Context, member: discord.Member):
        """Рулетка для выбранного пользователя. Мут на 1 час при проигрыше."""
        allowed_users = {499507046681673728, 566316034462711829, 695855560402403338}  # замените на ID тех, кому доступна команда
        if ctx.author.id not in allowed_users:
            return await ctx.send("Эта команда доступна ТОЛЬКО ДЛЯ ИЗБРАННЫХ")

        if member == ctx.guild.owner:
            return await ctx.send("ТЫ ШО НА БАРИНА СОБРАЛСЯ ЗАПУСКАТЬ, ПЛОХОЙ МАЛЬЧИК☝🏿☝🏿")

        if member == ctx.author:
            return await ctx.send("Вы не можете выбрать себя для этой рулетки")

        rnd = randint(1, 10)
        if rnd == 5:
            until = discord.utils.utcnow() + timedelta(minutes=5)
            try:
                await member.timeout(until)
                await ctx.send(f"к сожалению {member.mention} проиграл. Выдано 5 минут мута")
            except Exception as exc:
                await ctx.send(f"Не удалось выдать мут {member.mention}: {exc}")
        else:
            await ctx.send(f"{member.mention} повезло, мут не получил.")
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


    @ruletka_for_demyan.before_loop
    async def before_ruletka(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
