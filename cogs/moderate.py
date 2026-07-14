from discord.ext import commands, tasks
import discord
from datetime import timedelta

class Moderate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.hybrid_command(name="dvesti")
    async def dvesti(self, ctx: commands.Context, member: discord.Member):
        """Выдаёт мут на 5 минут и сообщает об этом в общем чате"""
        channel = ctx.guild.get_channel(1293249841501306933)
        tm = discord.utils.utcnow() + timedelta(minutes=5)
        alowed_users = {499507046681673728, 695855560402403338, 566316034462711829}
        if ctx.author.id in alowed_users:
            if member.is_timed_out():
                await ctx.send(f"{member.mention} Уже 200")
            else:
                try:
                    await member.timeout(tm)
                    await channel.send(f"{member.mention} 200")
                    await ctx.send(f"{member.mention} выдано 200(5 минут)")
                except:
                    await ctx.send("У него иммунитет к 200")
        else:
            await ctx.author.timeout(tm)
            await ctx.send(f"{ctx.author.mention} зачем то стреляет в себя")
    @commands.hybrid_command(name="trista")
    async def trista(self, ctx: commands.Context, member: discord.Member):
        """Выдаёт мут на 1 минуту и сообщает об этом в общем чате"""
        channel = ctx.guild.get_channel(1293249841501306933)
        tm = discord.utils.utcnow() + timedelta(minutes=1)
        alowed_users = {499507046681673728, 695855560402403338, 566316034462711829}
        if ctx.author.id in alowed_users:
            if member.is_timed_out():
                await ctx.send(f"{member.mention} Уже 300")
            else:
                try:
                    await member.timeout(tm)
                    await channel.send(f"{member.mention} 300")
                    await ctx.send(f"{member.mention} выдано 300(1 минута)")
                except:
                    await ctx.send("У него иммунитет к 300")
        else:
            await ctx.author.timeout(tm)
            await ctx.send(f"{ctx.author.mention} зачем то стреляет в себя")

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderate(bot))