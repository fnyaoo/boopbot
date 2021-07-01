import asyncio
from discord import ButtonStyle
from utils.menus import Confirm, ResponseType
import discord
from discord.ext import commands


class RPSType:
    none = -1
    rock = 0
    paper = 1
    scissors = 2

class RPSButton(discord.ui.Button['RockPaperScissors']): 
    def __init__(self, label: str, emoji: str, id: RPSType):
        super().__init__(style=ButtonStyle.blurple, label=label, emoji=emoji, custom_id=str(id))
        self.id = id
        self.name = ' '.join((emoji, label))
    
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: RockPaperScissors = self.view

        view.players[interaction.user.id] = self.id
        await interaction.response.send_message(f'Ты выбрал {self.name}', ephemeral=True)
        
        p = True
        for key in view.players:
            if view.players[key] == RPSType.none:
                p = False
                break
        
        if p:
            await interaction.response.defer()
            for child in view.children:
                assert isinstance(child, discord.ui.Button) # just to shut up the linter
                print('passed ', child)
                child.disabled = True
            view.stop()
            
        await interaction.response.edit_message(view=view)

class RockPaperScissors(discord.ui.View):
    def __init__(self, players: set[int]):
        super().__init__(timeout=30)
        self.players = {p: RPSType.none for p in players}
        

        self.mapping = {
            RPSType.rock:     RPSButton('Камень',  emoji='\U0001faa8', id=RPSType.rock),
            RPSType.paper:    RPSButton('Бумага',  emoji='\U0001f4f0', id=RPSType.paper),
            RPSType.scissors: RPSButton('Ножницы', emoji='\U00002702', id=RPSType.scissors)
        }
        for button in self.mapping.values():
            self.add_item(button)
    
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id in self.players:
            if self.players[interaction.user.id] == RPSType.none:
                return True
            else:
                button = self.get_pressed_name(interaction.user.id)
                await interaction.response.send_message(f'Вы уже выбрали {button}', ephemeral=True)
        await interaction.response.send_message(f'Извините, но вы не участниик игры', ephemeral=True)
        return False
    
    def get_pressed_name(self, user):
        try:
            return self.mapping[self.players[user]].name
        except KeyError:
            return '❌ Ничего'

class RockPaperScissors(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name = 'rockpaperscissors', aliases = ['rps'])
    async def rps(self, ctx: commands.Context, members: commands.Greedy[discord.Member]):
        """Камень-ножницы-бумага. Простая игра на удачу. Минимум 2 участника (включая отправителя команды)."""
        players = set([m.id for m in members if not m.bot])
        players.add(ctx.author.id)
        if len(players) < 2:
            return await ctx.send(f'Недостаточно игроков ({len(players)}, 2 минимум)')
        
        msg = await ctx.send(f'{", ".join([m.mention for m in members])}, нажмите ✅, чтобы принять вызов')
        result = await Confirm(msg, players, ResponseType.filter_of_given, timeout=30).reconst(ctx)

        if len(result) < 2:
            return await ctx.send(f'Недостаточно игроков ({len(result)}, 2 минимум)')
        
        pings = ", ".join([f"<@{m}>" for m in players])
        game = RockPaperScissors(players)
        game_msg = await ctx.send(f'Камень-ножницы-бумага! Игроки ({pings}), выберите ваш инструмент.', view = game)
        await game.wait()
        results = game.players

        ends = '\n'.join([f'<@{key}> выбрал(а) {game.get_pressed_name(key)}' for key in game.players])
        await game_msg.edit(content=ends)
        
    # @commands.command(name = 'test')
    # @commands.is_owner()
    # async def test_button(self, ctx):
    #     class Nottub(discord.ui.Button):
    #         def __init__(self, secret):
    #             super().__init__(style, label=label)
    #         @discord.ui.button(label='Click me!', style=ButtonStyle.grey)
    #         async def clickme(self, inter: discord.Interaction):
    #             await inter.response.edit_message()
    #     class Weiv(discord.ui.View):
    #         pass

def setup(bot):
    bot.add_cog(RockPaperScissors(bot))
