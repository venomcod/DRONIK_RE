#В Разработке

import discord
from discord.ext import commands

class Epedemic(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #@commands.hybrid_command(name="epedemia")
    #async def epedemia(self, ctx: commands.Context, member: discord.Member):
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(member)

async def setup(bot: commands.Bot):
    await bot.add_cog(Epedemic(bot))