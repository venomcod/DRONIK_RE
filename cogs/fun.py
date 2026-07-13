from discord.ext import commands, tasks
import discord
from datetime import timedelta
from random import randint
class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        #self.ruletka_for_demyan.start() Отключил рулетку для демы
    

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
    
    @commands.hybrid_command("ruletka")
    async def ruletka(self, ctx: commands.Context, rolls: int = 1):
        member = ctx.author
        guild_id = 849591676066725898
        guild = self.bot.get_guild(guild_id)
        if rolls < 0 or rolls > 6:
            return await ctx.send("Можно вписывать только целые числа больше 0 и небольше 6")
        for i in range(rolls):
            if member.is_timed_out():
                break
            else:
                rndl = randint(1, 10)
                if rndl == 5:
                    try:
                        until = discord.utils.utcnow() + timedelta(minutes=5)
                        await member.timeout(until)
                        await ctx.send(f"к сожалению {member.mention} проиграл. Выдано 5 минут мута")
                        print(f"{member} ЛОХ")
                    except:
                        await ctx.send(f"{member.mention} ПОХОЖЕ ОН ХУЙ ВАЖНЫЙ, не могу выдать мут")
                        print(f"{member} ПИДР")
                else:
                    await ctx.send(f"{member.mention} выжил, молодец")

    @commands.hybrid_command(name="ruletka_user")
    async def ruletka_user(self, ctx: commands.Context, member: discord.Member, rolls: int = 1):
        """Рулетка для выбранного пользователя. Мут на 5 минут при проигрыше."""
        allowed_users = {499507046681673728, 566316034462711829, 695855560402403338}  # замените на ID тех, кому доступна команда
        if ctx.author.id not in allowed_users:
            if member.id in allowed_users:
                await ctx.send("ТЫ ШО НА БАРИНА СОБРАЛСЯ ЗАПУСКАТЬ, ПЛОХОЙ МАЛЬЧИК☝🏿☝🏿, Кручу на тебя 5 раз")
                for i in range(5):
                    if ctx.author.is_timed_out():
                        break
                    else:
                        rnd = randint(1, 10)
                        if rnd == 5:
                            try:
                                until = discord.utils.utcnow() + timedelta(minutes=5)
                                await ctx.author.timeout(until)
                                await ctx.send(f"к сожалению {ctx.author.mention} проиграл. Выдано 5 минут мута")
                                print(f"{ctx.author} ЛОХ")
                            except:
                                await ctx.send(f"{ctx.author.mention} ПОХОЖЕ ОН ХУЙ ВАЖНЫЙ, не могу выдать мут")
                                print(f"{ctx.author} ПИДР")
                        else:
                            await ctx.send(f"{ctx.author.mention} выжил, молодец")
            else:
                await ctx.send("Эта команда доступна ТОЛЬКО ДЛЯ ИЗБРАННЫХ, Кручу на тебя)")
                rnd = randint(1, 10)
                if rnd == 5:
                    try:
                        until = discord.utils.utcnow() + timedelta(minutes=5)
                        await ctx.author.timeout(until)
                        await ctx.send(f"к сожалению {ctx.author.mention} проиграл. Выдано 5 минут мута")
                        print(f"{ctx.author} ЛОХ")
                    except:
                        await ctx.send(f"{ctx.author.mention} ПОХОЖЕ ОН ХУЙ ВАЖНЫЙ, не могу выдать мут")
                        print(f"{ctx.author} ПИДР")
                else:
                    await ctx.send(f"{ctx.author.mention} выжил, молодец")
        else:
            if member == ctx.guild.owner or member.id in allowed_users:
                return await ctx.send("ТЫ ШО НА БАРИНА СОБРАЛСЯ ЗАПУСКАТЬ, ПЛОХОЙ МАЛЬЧИК☝🏿☝🏿")

            if member == ctx.author:
                return await ctx.send("Вы не можете выбрать себя для этой рулетки")
            
            if rolls < 0 or rolls > 6:
                return await ctx.send("Можно вписывать только целые числа больше 0 и небольше 6")
            
            for i in range(rolls):
                if member.is_timed_out():
                    break
                else:
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
    

    @ruletka_for_demyan.before_loop
    async def before_ruletka(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
