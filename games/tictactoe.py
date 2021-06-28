from asyncio import TimeoutError
from discord import ButtonStyle
from utils import Confirm, ResponseType
import discord
from discord.ext import commands

class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', group=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"Сейчас ходят нолики ({view.players[1].mention})"
        elif view.current_player == view.O:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = f"Сейчас ходят крестики {view.players[0].mention}"
        else:
            return

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = 'Крестики победили!'
            elif winner == view.O:
                content = 'Нолики победили!'
            else:
                content = "Ничья!"

            for child in view.children:
                assert isinstance(child, discord.ui.Button) # just to shut up the linter
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)

class TTTView(discord.ui.View):
    X = -1
    O = 1
    Tie = 2

    def __init__(self, p1: discord.Member, p2: discord.Member):
        super().__init__(timeout=60)
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0], ]
        self.players = [p1, p2]
        self.last_interaction = None

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))
    
    async def interaction_check(self, interaction: discord.Interaction):
        if self.last_interaction is None:
            self.last_interaction = interaction
        if interaction.user in self.players:
            if (self.current_player == self.X and interaction.user == self.players[0]) or \
               (self.current_player == self.O and interaction.user == self.players[1]):
                return True
        return False


    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None

class TicTacToe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'tictactoe', aliases = ['ttt'])
    async def tic(self, ctx: commands.Context, member: discord.Member = None):
        if not member:
            msg = await ctx.send(f'`{ctx.author.display_name}` хочет сыграть в крестики-нолики.\nЧтобы принять вызов, нажмите ✅')
            await msg.add_reaction('✅')
            def check(r: discord.Reaction, u):
                return u != ctx.author and \
                    r.message == msg and \
                    not u.bot
            try:
                _, user = await self.bot.wait_for('reaction_add', check=check, timeout=90)
                result = True
                member = user
            except TimeoutError:
                await msg.delete()
                return await ctx.reply('Никто не ответил')
        else:
            if member.bot:
                return await ctx.send('Нельзя игратьс ботом.')
            m = await ctx.send(f'{member.mention}, `{ctx.author.display_name}` хочет сыграть в крестики-нолики')
            result = await Confirm(m, [member.id], timeout=30).reconst(ctx)
        if result:
            view = TTTView(ctx.author, member)
            game_msg = await ctx.send(f'Крестики-нолики: X ({ctx.author.mention}) ходит', view=view)
            itr_result = await view.wait()
            if itr_result:
                await game_msg.delete()
                await ctx.reply('Игра окончана таймаутом.')
            else:
                await game_msg.edit('\n'.join([f'{player.mention} выбрал(а) {view.get_pressed(player).name}' for player in view.players]))
        elif result is None:
            await ctx.send(f'{ctx.author.mention}, `{member.display_name}` не успел(а) ответить.')
        else:
            await ctx.send(f'{ctx.author.mention}, приглашение отклонено')
        await m.delete()

def setup(bot):
    bot.add_cog(TicTacToe(bot))