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
                    until = discord.utils.utcnow() + timedelta(hours=1)
                    await member.timeout(until)
                    await chnl.send(f"к сожалению {member.mention} проиграл. Выдан 1 час мута")
                    print(f"{member.mention} ЛОХ")
                except:
                    await chnl.send(f"{member.mention} ПОХОЖЕ ОН ХУЙ ВАЖНЫЙ, не могу выдать мут")
                    print(f"{member.mention} ПИДР")
            else:
                await chnl.send(f"{member.mention} выжил, молодец")
        elif member == dema:
            await chnl.send(f"А вот тебе нельзя пользоватся рулеткой, но но")

    @ruletka_for_demyan.before_loop
    async def before_ruletka(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
