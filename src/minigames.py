from discord.ext import tasks, commands
import random

class Minigames(commands.Cog):
    '''Fun minigames because why not'''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "rock", aliases = ["paper", "scissors"])
    async def RPS(self, ctx):
        '''Rock, Paper, Scissors vs. Bean'''
        choices = { "rock": 0, "paper": 1, "scissors": 2}
        matrix = [
            [0, -1, 1],
            [1, 0, -1],
            [-1, 1, 0]
        ]
        choice = choices[ctx.message.content[3:]]
        bean_choice = random.randint(0,2)
        m = matrix[bean_choice][choice]
        bean = list(choices.keys())[bean_choice]
        if m > 0:
            await ctx.send(f"Bean chose {bean}. Bean wins!")
        elif m < 0:
            await ctx.send(f"Bean chose {bean}. You win!")
        else:
            await ctx.send(f"Bean chose {bean}. Tie!")