'''Written by Cael Shoop.'''

import os
import json
import discord
import datetime
from typing import Literal
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv


load_dotenv()
GUESS_THE_LITERAL:Literal = Literal['GuessTheGame', 'GuessTheAudio', 'All']


def get_time():
    ct = str(datetime.datetime.now())
    hour = int(ct[11:13])
    minute = int(ct[14:16])
    return hour, minute


def get_log_time():
    time = datetime.datetime.now().astimezone()
    output = ''
    if time.hour < 10:
        output += '0'
    output += f'{time.hour}:'
    if time.minute < 10:
        output += '0'
    output += f'{time.minute}:'
    if time.second < 10:
        output += '0'
    output += f'{time.second}'
    return output


def get_gtg_guesses(player):
    return player.gtgame.guesses


def get_gta_guesses(player):
    return player.gtaudio.guesses


def main():
    '''Main function'''
    class GuessTheClient(discord.Client):
        '''Custom client class for GuessTheGame bot'''

        FILE_PATH = 'info.json'

        def __init__(self, intents):
            super(GuessTheClient, self).__init__(intents=intents)
            self.gtg_text_channel: discord.TextChannel
            self.gta_text_channel: discord.TextChannel
            self.server_id:int                 = 0
            self.players:list                  = []
            self.sent_warning:bool             = False
            self.midnight_called:bool          = False
            self.scored_gtg_today:bool         = False
            self.scored_gta_today:bool         = False
            self.tree:app_commands.CommandTree = app_commands.CommandTree(self)


        class GuessThe:
            '''GuessThe class for storing game info'''
            def __init__(self):
                self.winCount = 0
                self.guesses = 0
                self.skip = False
                self.registered = False
                self.completedToday = False
                self.succeededToday = False

        class Player:
            '''Player class for storing player info'''
            def __init__(self, name):
                self.name = name
                self.gtgame = client.GuessThe()
                self.gtaudio = client.GuessThe()


        async def setup_hook(self):
            await self.tree.sync()


        def read_json_file(self):
            '''Reads player information from the json file and puts it in the players list'''
            if not os.path.exists(self.FILE_PATH):
                print(f'{get_log_time()}> {self.FILE_PATH} does not exist')
                return
            with open(self.FILE_PATH, 'r', encoding='utf-8') as file:
                print(f'{get_log_time()}> Reading {self.FILE_PATH}')
                data = json.load(file)
                for firstField, secondField in data.items():
                    if firstField == 'text_channels':
                        self.gtg_text_channel = client.get_channel(int(secondField['gtg_text_channel']))
                        self.gta_text_channel = client.get_channel(int(secondField['gta_text_channel']))
                        print(f'{get_log_time()}> Got GTG text channel {self.gtg_text_channel.name} with id {self.gtg_text_channel.id}')
                        print(f'{get_log_time()}> Got GTA text channel {self.gta_text_channel.name} with id {self.gta_text_channel.id}')
                    elif firstField == 'scored_today':
                        self.scored_gtg_today = secondField['scored_gtg_today']
                        self.scored_gta_today = secondField['scored_gta_today']
                        print(f'{get_log_time()}> Got scored_gtg_today as {self.scored_gtg_today}')
                        print(f'{get_log_time()}> Got scored_gta_today as {self.scored_gta_today}')
                    else:
                        load_player = self.Player(firstField)
                        load_player.gtgame.winCount = secondField['gtgame']['winCount']
                        load_player.gtgame.guesses = secondField['gtgame']['guesses']
                        load_player.gtgame.registered = secondField['gtgame']['registered']
                        load_player.gtgame.completedToday = secondField['gtgame']['completedToday']
                        load_player.gtgame.succeededToday = secondField['gtgame']['succeededToday']
                        load_player.gtaudio.winCount = secondField['gtaudio']['winCount']
                        load_player.gtaudio.guesses = secondField['gtaudio']['guesses']
                        load_player.gtaudio.registered = secondField['gtaudio']['registered']
                        load_player.gtaudio.completedToday = secondField['gtaudio']['completedToday']
                        load_player.gtaudio.succeededToday = secondField['gtaudio']['succeededToday']
                        self.players.append(load_player)
                        print(f'{get_log_time()}> Loaded player {load_player.name}\n'
                              f'\t\t\tGTG/GTA wins:       {load_player.gtgame.winCount}/{load_player.gtaudio.winCount}\n'
                              f'\t\t\tGTG/GTA guesses:    {load_player.gtgame.guesses}/{load_player.gtaudio.guesses}\n'
                              f'\t\t\tGTG/GTA registered: {load_player.gtgame.registered}/{load_player.gtaudio.registered}\n'
                              f'\t\t\tGTG/GTA completed:  {load_player.gtgame.completedToday}/{load_player.gtaudio.completedToday}\n'
                              f'\t\t\tGTG/GTA succeeded:  {load_player.gtgame.succeededToday}/{load_player.gtaudio.succeededToday}')

                print(f'{get_log_time()}> Successfully loaded {self.FILE_PATH}')


        def write_json_file(self):
            '''Writes player information from the players list to the json file'''
            data = {}
            data['text_channels'] = {'gtg_text_channel': self.gtg_text_channel.id,
                                     'gta_text_channel': self.gta_text_channel.id}
            data['scored_today'] = {'scored_gtg_today': client.scored_gtg_today,
                                    'scored_gta_today': client.scored_gta_today}
            for player in self.players:
                data[player.name] = {
                    'gtgame': {'winCount': player.gtgame.winCount,
                               'guesses': player.gtgame.guesses,
                               'registered': player.gtgame.registered,
                               'completedToday': player.gtgame.completedToday,
                               'succeededToday': player.gtgame.succeededToday},
                    'gtaudio': {'winCount': player.gtaudio.winCount,
                               'guesses': player.gtaudio.guesses,
                               'registered': player.gtaudio.registered,
                               'completedToday': player.gtaudio.completedToday,
                               'succeededToday': player.gtaudio.succeededToday}
                }
            json_data = json.dumps(data)
            print(f'{get_log_time()}> Writing {self.FILE_PATH}')
            with open(self.FILE_PATH, 'w+', encoding='utf-8') as file:
                file.write(json_data)


        async def might_gtg_score(self):
            if self.scored_gtg_today:
                return
            for player in client.players:
                if player.gtgame.registered and not player.gtgame.skip and not player.gtgame.completedToday:
                    return
            scoreboard = ''
            scoreboardList = client.tally_gtg_scores()
            for line in scoreboardList:
                scoreboard += line
            await client.gtg_text_channel.send(scoreboard)


        async def might_gta_score(self):
            if self.scored_gta_today:
                return
            for player in client.players:
                if player.gtaudio.registered and not player.gtaudio.skip and not player.gtaudio.completedToday:
                    return
            scoreboard = ''
            scoreboardList = client.tally_gta_scores()
            for line in scoreboardList:
                scoreboard += line
            await client.gta_text_channel.send(scoreboard)


        async def process(self, name, message: discord.Message, channel: discord.TextChannel, guessThe: GuessThe):
            # player has already sent results
            if guessThe.completedToday:
                print(f'{get_log_time()}> {name} tried to resubmit results')
                await channel.send(f'{name}, you have already submitted your results today.')
                return

            try:
                result = message.content.splitlines()[2].replace(' ', '')[1:]
                guessThe.succeededToday = False
                guessThe.guesses = 0
                for char in result:
                    if char == '🟥' or char == '🟨':
                        guessThe.guesses += 1
                    elif char == '🟩':
                        guessThe.guesses += 1
                        guessThe.succeededToday = True
                        break
                guessThe.completedToday = True
                print(f'{get_log_time()}> Player {name} - guesses: {guessThe.guesses}, succeeded: {guessThe.succeededToday}')

                client.write_json_file()
                await self.might_gtg_score()
                await self.might_gta_score()
            except:
                print(f'{get_log_time()}> Player {name} submitted an invalid GuessThe results message')
                await channel.send(f'{name}, your results message had a formatting error and could not be processed.')


        def tally_gtg_scores(self):
            '''Sorts players and returns a list of strings to send as Discord messages'''
            if not self.players:
                print('No players to score')
                return

            print('GTG> Tallying scores')
            gtgPlayers = [] # list of players    - people who are registered and completed GTG today
            winners = []    # list of winners    - people with the lowest score
            completers = [] # list of completers - people who completed it but don't have the lowest score
            losers = []     # list of losers     - people who didn't guess the game
            results = []    # list of strings    - scoreboard to print out
            results.append('\nGUESSING COMPLETE!\n\n**SCOREBOARD:**\n')
            prevGuesses = 0
            placeCounter = 1

            # cull and sort the players
            for player in self.players:
                if player.gtgame.registered and player.gtgame.completedToday:
                    gtgPlayers.append(player)
            gtgPlayers.sort(key=get_gtg_guesses)

            # generate winners list
            if gtgPlayers[0].gtgame.succeededToday:
                winningGuessCount = gtgPlayers[0].gtgame.guesses
                for gtgPlayer in gtgPlayers.copy():
                    if gtgPlayer.gtgame.guesses == winningGuessCount and gtgPlayer.gtgame.succeededToday:
                        print(f'{get_log_time()}> GTG> {gtgPlayer.name} won with {winningGuessCount} guesses')
                        winners.append(gtgPlayer)
                        gtgPlayers.remove(gtgPlayer)

            # generate completers and losers lists
            for gtgPlayer in gtgPlayers.copy():
                if gtgPlayer.gtgame.succeededToday:
                    print(f'{get_log_time()}> GTG> {gtgPlayer.name} completed GTG with {gtgPlayer.gtgame.guesses} guesses')
                    completers.append(gtgPlayer)
                else:
                    print(f'{get_log_time()}> GTG> {gtgPlayer.name} did not succeed')
                    losers.append(gtgPlayer)
                gtgPlayers.remove(gtgPlayer)

            # generate results list
            for gtgPlayer in winners.copy():
                subResult = ''
                gtgPlayer.gtgame.winCount += 1
                if gtgPlayer.gtgame.winCount == 1:
                    subResult = f'1. {gtgPlayer.name} (1 win) wins by guessing the game '
                else:
                    subResult = f'1. {gtgPlayer.name} ({gtgPlayer.gtgame.winCount} wins) wins by guessing the game '
                if gtgPlayer.gtgame.guesses == 1:
                    subResult += f'in one guess! Nice!\n'
                else:
                    subResult += f'in {gtgPlayer.gtgame.guesses} guesses!\n'
                results.append(subResult)
                winners.remove(gtgPlayer)

            for gtgPlayer in completers.copy():
                print(f'{get_log_time()}> DEBUG: name: {gtgPlayer.name}, guesses: {gtgPlayer.gtgame.guesses}, prevGuesses: {prevGuesses}')
                if gtgPlayer.gtgame.guesses != prevGuesses:
                    placeCounter += 1
                prevGuesses = gtgPlayer.gtgame.guesses
                if gtgPlayer.gtgame.winCount == 1:
                    results.append(f'{placeCounter}. {gtgPlayer.name} (1 win) guessed the game in {gtgPlayer.gtgame.guesses} guesses.\n')
                else:
                    results.append(f'{placeCounter}. {gtgPlayer.name} ({gtgPlayer.gtgame.winCount} wins) guessed the game in {gtgPlayer.gtgame.guesses} guesses.\n')
                completers.remove(gtgPlayer)

            for gtgPlayer in losers.copy():
                if gtgPlayer.gtgame.winCount == 1:
                    results.append(f'{gtgPlayer.name} (1 win) did not successfully guess the game.\n')
                else:
                    results.append(f'{gtgPlayer.name} ({gtgPlayer.gtgame.winCount} wins) did not successfully guess the game.\n')
                losers.remove(gtgPlayer)

            self.scored_gtg_today = True
            self.write_json_file()
            return results


        def tally_gta_scores(self):
            '''Sorts players and returns a list of strings to send as Discord messages'''
            if not self.players:
                print('No players to score')
                return

            print('GTA> Tallying scores')
            gtaPlayers = [] # list of players    - people who are registered and completed GTA today
            winners = []    # list of winners    - people with the lowest score
            completers = [] # list of completers - people who completed it but don't have the lowest score
            losers = []     # list of losers     - people who didn't guess the audio
            results = []    # list of strings    - scoreboard to print out
            results.append('\nGUESSING COMPLETE!\n\n**SCOREBOARD:**\n')
            prevGuesses = 0
            placeCounter = 1

            # cull and sort the players
            for player in self.players:
                if player.gtaudio.registered and player.gtaudio.completedToday:
                    gtaPlayers.append(player)
            gtaPlayers.sort(key=get_gta_guesses)

            # generate winners list
            if gtaPlayers[0].gtaudio.succeededToday:
                winningGuessCount = gtaPlayers[0].gtaudio.guesses
                for gtaPlayer in gtaPlayers.copy():
                    if gtaPlayer.gtaudio.guesses == winningGuessCount and gtaPlayer.gtaudio.succeededToday:
                        print(f'{get_log_time()}> GTA> {gtaPlayer.name} won with {winningGuessCount} guesses')
                        winners.append(gtaPlayer)
                        gtaPlayers.remove(gtaPlayer)

            # generate completers and losers lists
            for gtaPlayer in gtaPlayers.copy():
                if gtaPlayer.gtaudio.succeededToday:
                    print(f'{get_log_time()}> GTA> {gtaPlayer.name} completed GTA with {gtaPlayer.gtaudio.guesses} guesses')
                    completers.append(gtaPlayer)
                else:
                    print(f'{get_log_time()}> GTA> {gtaPlayer.name} did not succeed')
                    losers.append(gtaPlayer)
                gtaPlayers.remove(gtaPlayer)

            # generate results list
            for gtaPlayer in winners.copy():
                subResult = ''
                gtaPlayer.gtaudio.winCount += 1
                if gtaPlayer.gtaudio.winCount == 1:
                    subResult = f'1. {gtaPlayer.name} (1 win) wins by guessing the audio '
                else:
                    subResult = f'1. {gtaPlayer.name} ({gtaPlayer.gtaudio.winCount} wins) wins by guessing the audio '
                if gtaPlayer.gtaudio.guesses == 1:
                    subResult += f'in one guess! Nice!\n'
                else:
                    subResult += f'in {gtaPlayer.gtaudio.guesses} guesses!\n'
                results.append(subResult)
                winners.remove(gtaPlayer)

            for gtaPlayer in completers.copy():
                if gtaPlayer.gtaudio.guesses != prevGuesses:
                    placeCounter += 1
                prevGuesses = gtaPlayer.gtaudio.guesses
                if gtaPlayer.gtaudio.winCount == 1:
                    results.append(f'{placeCounter}. {gtaPlayer.name} (1 win) guessed the audio in {gtaPlayer.gtaudio.guesses} guesses.\n')
                else:
                    results.append(f'{placeCounter}. {gtaPlayer.name} ({gtaPlayer.gtaudio.winCount} wins) guessed the audio in {gtaPlayer.gtaudio.guesses} guesses.\n')
                completers.remove(gtaPlayer)

            for gtaPlayer in losers.copy():
                if gtaPlayer.gtaudio.winCount == 1:
                    results.append(f'{gtaPlayer.name} (1 win) did not successfully guess the audio.\n')
                else:
                    results.append(f'{gtaPlayer.name} ({gtaPlayer.gtaudio.winCount} wins) did not successfully guess the audio.\n')
                losers.remove(gtaPlayer)

            self.scored_gta_today = True
            self.write_json_file()
            return results


    discord_token = os.getenv('DISCORD_TOKEN')

    intents = discord.Intents.all()

    client = GuessTheClient(intents=intents)

    @client.event
    async def on_ready():
        '''Client on_ready event'''
        client.read_json_file()
        if not midnight_call.is_running():
            midnight_call.start()
        print(f'{get_log_time()}> {client.user} has connected to Discord!')
        await client.might_gtg_score()
        await client.might_gta_score()


    @client.event
    async def on_message(message):
        '''Client on_message event'''
        # message is from this bot
        if message.author == client.user:
            return

        player = client.players[0]
        channel: discord.TextChannel
        if '#GuessTheGame' in message.content:
            print(f'{get_log_time()}> Received GuessTheGame message from {message.author}')
            channel = client.gtg_text_channel
        elif '#GuessTheAudio' in message.content:
            print(f'{get_log_time()}> Received GuessTheAudio message from {message.author}')
            channel = client.gta_text_channel

        # someone posts their GuessThe results
        if '#GuessTheGame' in message.content or '#GuessTheAudio' in message.content:
            user = discord.utils.get(client.users, name=message.author.name)
            # there are no registered players
            if not client.players:
                await channel.send(f'{user.mention}, there are no registered players! Please register and resend your results to be the first.')
                return

            # player is not registered
            found = False
            for player_it in client.players:
                if message.author.name == player_it.name:
                    found = True
            if not found:
                await channel.send(f'{message.author.name}, you are not registered! Please register and resend your results.')

            found = False
            for player_it in client.players:
                if message.author.name == player_it.name:
                    found = True
                    player = player_it
            if not found:
                print('Unregistered player posted a result')
                await channel.send(f'Unregistered user {user.mention} attempted to post a result. Please register with "/register" and try again.')
                return

            guessThe: GuessTheClient.GuessThe
            if '#GuessTheGame' in message.content:
                guessThe = player.gtgame
            elif '#GuessTheAudio' in message.content:
                guessThe = player.gtaudio

            await client.process(player.name, message, channel, guessThe)
            if guessThe.succeededToday:
                await message.add_reaction('👍')
            else:
                await message.add_reaction('👎')


    @client.tree.command(name='track', description='Track this text channel for GuessTheGame or GuessTheAudio.')
    @app_commands.describe(guess_the='Choose the GuessThe you want tracked to this channel')
    async def track_command(interaction: discord.Interaction, guess_the: GUESS_THE_LITERAL):
        '''Command to track a text channel'''
        response = ''
        client.server_id = interaction.guild.id
        if guess_the == 'GuessTheGame' or guess_the == 'All':
            if interaction.channel.id != client.gtg_text_channel.id:
                client.gtg_text_channel = interaction.channel
                print(f'{get_log_time()}> Now tracking channel {client.gtg_text_channel.id}')
                client.write_json_file()
                response += 'Now tracking this channel for GuessTheGame.\n'
            else:
                print('Tried to change channel tracking to current channel')
                response += 'Already tracking this channel for GuessTheGame.\n'
        if guess_the == 'GuessTheAudio' or guess_the == 'All':
            if interaction.channel.id != client.gta_text_channel.id:
                client.gta_text_channel = interaction.channel
                print(f'{get_log_time()}> Now tracking channel {client.gta_text_channel.id}')
                client.write_json_file()
                response += 'Now tracking this channel for GuessTheAudio.\n'
            else:
                print('Tried to change channel tracking to current channel')
                response += 'Already tracking this channel for GuessTheAudio.\n'
        await interaction.response.send_message(response)


    @client.tree.command(name='register', description='Register for GuessTheGame or GuessTheAudio tracking.')
    @app_commands.describe(guess_the='Choose the GuessThe you want to register for')
    async def register_command(interaction: discord.Interaction, guess_the: GUESS_THE_LITERAL):
        '''Command to register a player'''
        response = ''
        if guess_the == 'GuessTheGame' or guess_the == 'All':
            playerFound = False
            for player in client.players:
                if interaction.user.name.strip() == player.name.strip():
                    if player.gtgame.registered:
                        print(f'{get_log_time()}> User {interaction.user.name.strip()} attempted to re-register for tracking GTG')
                        response += 'You are already registered for GuessTheGame tracking!\n'
                    else:
                        print(f'{get_log_time()}> Registering user {interaction.user.name.strip()} for tracking GTG')
                        player.gtgame.registered = True
                        client.write_json_file()
                        response += 'You have been registered for GuessTheGame tracking.\n'
                    playerFound = True
            if not playerFound:
                print(f'{get_log_time()}> Registering user {interaction.user.name.strip()} for tracking GTG')
                player_obj = client.Player(interaction.user.name.strip())
                player_obj.gtgame.registered = True
                client.players.append(player_obj)
                client.write_json_file()
                response += 'You have been registered for GuessTheGame tracking.\n'
        if guess_the == 'GuessTheAudio' or guess_the == 'All':
            playerFound = False
            for player in client.players:
                if interaction.user.name.strip() == player.name.strip():
                    if player.gtaudio.registered:
                        print(f'{get_log_time()}> User {interaction.user.name.strip()} attempted to re-register for tracking GTA')
                        response += 'You are already registered for GuessTheAudio tracking!\n'
                    else:
                        print(f'{get_log_time()}> Registering user {interaction.user.name.strip()} for tracking GTA')
                        player.gtaudio.registered = True
                        client.write_json_file()
                        response += 'You have been registered for GuessTheAudio tracking.\n'
                    playerFound = True
            if not playerFound:
                print(f'{get_log_time()}> Creating player object and registering user {interaction.user.name.strip()} for tracking GTA')
                player_obj = client.Player(interaction.user.name.strip())
                player_obj.gtaudio.registered = True
                client.players.append(player_obj)
                client.write_json_file()
                response += 'You have been registered for GuessTheAudio tracking.\n'
        await interaction.response.send_message(response)


    @client.tree.command(name='deregister', description='Deregister for GuessThe tracking.')
    @app_commands.describe(guess_the='Choose the GuessThe you want to deregister from')
    async def deregister_command(interaction: discord.Interaction, guess_the: GUESS_THE_LITERAL):
        '''Command to deregister a player'''
        players_copy = client.players.copy()
        if guess_the == 'GuessTheGame':
            for player in players_copy:
                if player.name == interaction.user.name.strip():
                    if player.gtaudio.registered:
                        player.gtgame.registered = False
                    else:
                        client.players.remove(player)
                    client.write_json_file()
                    print(f'{get_log_time()}> Deregistered user {player.name} from GTG')
                    await interaction.response.send_message('You have been deregistered for GuessTheGame tracking.')
                    await client.might_gtg_score()
                    return
            print(f'{get_log_time()}> Unregistered user {interaction.user.name.strip()} attempted to deregister from GTG')
            await interaction.response.send_message('You were already unregistered for GuessTheGame tracking.')
        elif guess_the == 'GuessTheAudio':
            for player in players_copy:
                if player.name == interaction.user.name.strip():
                    if player.gtgame.registered:
                        player.gtaudio.registered = False
                    else:
                        client.players.remove(player)
                    client.write_json_file()
                    print(f'{get_log_time()}> Deregistered user {player.name} from GTA')
                    await interaction.response.send_message('You have been deregistered for GuessTheAudio tracking.')
                    await client.might_gta_score()
                    return
            print(f'{get_log_time()}> Unregistered user {interaction.user.name.strip()} attempted to deregister from GTA')
            await interaction.response.send_message('You were already unregistered for GuessTheAudio tracking.')
        elif guess_the == 'All':
            for player in players_copy:
                if player.name == interaction.user.name.strip():
                    client.players.remove(player)
                    client.write_json_file()
                    print(f'{get_log_time()}> Deregistered user {player.name} from GTG and GTA')
                    await interaction.response.send_message('You have been deregistered for GuessTheGame and GuessTheAudio tracking.')
                    await client.might_gtg_score()
                    await client.might_gta_score()
                    return
            print(f'{get_log_time()}> Unregistered user {interaction.user.name.strip()} attempted to deregister from GTG and GTA')
            await interaction.response.send_message('You were already unregistered for GuessThe tracking.')


    @client.tree.command(name='skip', description='Skip yourself for scoring today.')
    @app_commands.describe(guess_the='Choose the GuessThe you want to skip today')
    async def skip_command(interaction: discord.Interaction, guess_the: GUESS_THE_LITERAL):
        '''Command to skip scoring for today'''
        if guess_the == 'GuessTheGame':
            if client.scored_gtg_today:
                await interaction.response.send_message('GuessTheGame was already scored today.')
                return
            for player in client.players:
                if player.name == interaction.user.name:
                    if player.gtgame.registered:
                        player.gtgame.skip = True
                        await interaction.response.send_message('You will be skipped for today\'s GuessTheGame scoring.')
                        await client.might_gtg_score()
                    else:
                        await interaction.response.send_message('You are unregistered for GuessTheGame scoring; no need to skip.')
                    return
        elif guess_the == 'GuessTheAudio':
            if client.scored_gta_today:
                await interaction.response.send_message('GuessTheAudio was already scored today.')
                return
            for player in client.players:
                if player.name == interaction.user.name:
                    if player.gtaudio.registered:
                        player.gtaudio.skip = True
                        await interaction.response.send_message('You will be skipped for today\'s GuessTheAudio scoring.')
                        await client.might_gta_score()
                    else:
                        await interaction.response.send_message('You are unregistered for GuessTheAudio scoring; no need to skip.')
                    return
        elif guess_the == 'All':
            for player in client.players:
                if player.name == interaction.user.name:
                    response = ''
                    if client.scored_gtg_today:
                        response += 'GuessTheGame was already scored today.\n'
                    else:
                        if player.gtgame.registered:
                            player.gtaudio.skip = True
                            response += 'You will be skipped for today\'s GuessTheGame scoring.\n'
                        else:
                            response += 'You are unregistered for GuessTheGame scoring; no need to skip.\n'
                    if client.scored_gta_today:
                        response += 'GuessTheAudio was already scored today.\n'
                    else:
                        if player.gtaudio.registered:
                            player.gtaudio.skip = True
                            response += 'You will be skipped for today\'s GuessTheAudio scoring.\n'
                        else:
                            response += 'You are unregistered for GuessTheAudio scoring; no need to skip.\n'
                    await interaction.response.send_message(response)
                    await client.might_gtg_score()
                    await client.might_gta_score()
                    return


    @client.tree.command(name='unskip', description='Unskip yourself for scoring today.')
    @app_commands.describe(guess_the='Choose the GuessThe you want to unskip today')
    async def unskip_command(interaction: discord.Interaction, guess_the: GUESS_THE_LITERAL):
        '''Command to unskip scoring for today'''
        if guess_the == 'GuessTheGame':
            if client.scored_gtg_today:
                await interaction.response.send_message('GuessTheGame was already scored today.')
                return
            for player in client.players:
                if player.name == interaction.user.name:
                    if player.gtgame.registered:
                        player.gtgame.skip = False
                        await interaction.response.send_message('You will **not** be skipped for today\'s GuessTheGame scoring.')
                        await client.might_gtg_score()
                    else:
                        await interaction.response.send_message('You are unregistered for GuessTheGame scoring; you need to register to be tracked.')
                    return
        elif guess_the == 'GuessTheAudio':
            if client.scored_gta_today:
                await interaction.response.send_message('GuessTheAudio was already scored today.')
                return
            for player in client.players:
                if player.name == interaction.user.name:
                    if player.gtaudio.registered:
                        player.gtaudio.skip = False
                        await interaction.response.send_message('You will **not** be skipped for today\'s GuessTheAudio scoring.')
                        await client.might_gta_score()
                    else:
                        await interaction.response.send_message('You are unregistered for GuessTheAudio scoring; you need to register to be tracked.')
                    return
        elif guess_the == 'All':
            for player in client.players:
                if player.name == interaction.user.name:
                    response = ''
                    if client.scored_gtg_today:
                        response += 'GuessTheGame was already scored today.\n'
                    else:
                        if player.gtgame.registered:
                            player.gtaudio.skip = False
                            response += 'You will **not** be skipped for today\'s GuessTheGame scoring.\n'
                        else:
                            response += 'You are unregistered for GuessTheGame scoring; you need to register to be tracked.\n'
                    if client.scored_gta_today:
                        response += 'GuessTheAudio was already scored today.\n'
                    else:
                        if player.gtaudio.registered:
                            player.gtaudio.skip = False
                            response += 'You will **not** be skipped for today\'s GuessTheAudio scoring.\n'
                        else:
                            response += 'You are unregistered for GuessTheAudio scoring; you need to register to be tracked.\n'
                    await interaction.response.send_message(response)
                    await client.might_gtg_score()
                    await client.might_gta_score()
                    return


    @tasks.loop(seconds = 1)
    async def midnight_call():
        '''Midnight call loop task that is run every second with an almost midnight check.'''
        if not client.players:
            return

        hour, minute = get_time()
        if hour == 22 and minute == 31 and client.sent_warning:
            client.sent_warning = False
        if hour == 22 and minute == 30 and not client.sent_warning:
            if not client.scored_gtg_today:
                gtg_warning = ''
                for player in client.players:
                    if player.gtgame.registered and not player.gtgame.skip and not player.gtgame.completedToday:
                        user = discord.utils.get(client.users, name=player.name)
                        gtg_warning += f'{user.mention} '
                if gtg_warning != '':
                    await client.gtg_text_channel.send(f'{gtg_warning}, you have one hour left to Guess the Game!')
            if not client.scored_gta_today:
                gta_warning = ''
                for player in client.players:
                    if player.gtaudio.registered and not player.gtaudio.skip and not player.gtaudio.completedToday:
                        user = discord.utils.get(client.users, name=player.name)
                        gta_warning += f'{user.mention} '
                if gta_warning != '':
                    await client.gta_text_channel.send(f'{gta_warning}, you have one hour left to Guess the Audio!')
            client.sent_warning = True

        if client.midnight_called and hour == 23 and minute == 31:
            client.midnight_called = False
            client.write_json_file()
        if client.midnight_called or hour != 23 or minute != 30:
            return
        client.midnight_called = True

        print('It is almost midnight, sending daily scoreboard and then mentioning registered players')

        gtg_shamed = ''
        gta_shamed = ''
        for player in client.players:
            if player.gtgame.registered and not player.gtgame.skip and not player.gtgame.completedToday:
                user = discord.utils.get(client.users, name=player.name)
                if user:
                    gtg_shamed += f'{user.mention} '
            if player.gtaudio.registered and not player.gtaudio.skip and not player.gtaudio.completedToday:
                user = discord.utils.get(client.users, name=player.name)
                if user:
                    gta_shamed += f'{user.mention} '
        if gtg_shamed != '':
            await client.gtg_text_channel.send(f'SHAME ON {gtg_shamed} FOR NOT ATTEMPTING TO GUESS THE GAME!')
            scoreboard = ''
            scoreboardList = client.tally_gtg_scores()
            for line in scoreboardList:
                scoreboard += line
            await client.gtg_text_channel.send(scoreboard)
        if gta_shamed != '':
            await client.gta_text_channel.send(f'SHAME ON {gta_shamed} FOR NOT ATTEMPTING TO GUESS THE AUDIO!')
            scoreboard = ''
            scoreboardList = client.tally_gta_scores()
            for line in scoreboardList:
                scoreboard += line
            await client.gta_text_channel.send(scoreboard)

        gtg_everyone = ''
        gta_everyone = ''
        for player in client.players:
            player.gtgame.guesses = 0
            player.gtaudio.guesses = 0
            player.gtgame.skip = False
            player.gtaudio.skip = False
            player.gtgame.completedToday = False
            player.gtaudio.completedToday = False
            player.gtgame.succeededToday = False
            player.gtaudio.succeededToday = False
            user = discord.utils.get(client.users, name=player.name)
            if user:
                if player.gtgame.registered:
                    gtg_everyone += f'{user.mention} '
                if player.gtaudio.registered:
                    gta_everyone += f'{user.mention} '
        client.scored_gtg_today = False
        client.scored_gta_today = False
        await client.gtg_text_channel.send(f'{gtg_everyone}\nIt\'s time to Guess The Game!\nhttps://guessthe.game/')
        await client.gta_text_channel.send(f'{gta_everyone}\nIt\'s time to Guess The Audio!\nhttps://guesstheaudio.com/')


    client.run(discord_token)


if __name__ == '__main__':
    main()
