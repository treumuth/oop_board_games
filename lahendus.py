class Player:
    def __init__(self, name):
        self.name = name
        self.num_games_played = 0
        self.num_games_won = 0
        self.num_games_lost = 0
        self.games_played = []

    def add_game_played(self):
        """Increments the number of games played by the player"""
        self.num_games_played += 1

    def add_game_won(self):
        """Increments the number of games won by the player"""
        self.num_games_won += 1

    def add_game_lost(self):
        """Increments the number of games lost by the player"""
        self.num_games_lost += 1

    def add_game(self, game):
        """Adds a game to the list of games played by the player"""
        self.games_played.append(game)

class Game:
    def __init__(self, name, result_type):
        self.name = name
        self.num_games_played = 0
        self.players_per_game = []
        self.players = []
        self.winners = []
        self.losers = []
        self.current_record = 0
        self.record_holder = ""
        self.result_type = result_type

    def add_player(self, player):
        """Adds a player to the game"""
        self.players.append(player)

    def add_winner_points(self, player, points):
        """Adds a winner to the game with their score"""
        self.winners.append(player)
        if points > self.current_record:
            self.current_record = points
            self.record_holder = player

    def add_winner(self, player):
        """Adds a winner to the game"""
        self.winners.append(player)

    def add_loser(self, player):
        """Adds a loser to the game"""
        self.losers.append(player)

    def add_game_played(self, num_players):
        """Increments the number of games played and records the number of players in the game"""
        self.num_games_played += 1
        self.players_per_game.append(num_players)

class Statistics:
    def __init__(self, filename):
        self.players = {}
        self.games = {}

        with open(filename, "r") as file:
            for line in file:
                # Parse the line into its component parts
                game_name, player_names, result_type, results = line.strip().split(";")

                player_names = player_names.split(",")
                results = results.split(",")

                # Add new players to the dictionary of players
                for player_name in player_names:
                    if player_name not in self.players:
                        self.players[player_name] = Player(player_name)

                # Add new games to the dictionary of games
                if game_name not in self.games:
                    self.games[game_name] = Game(game_name, result_type)
                game = self.games[game_name]
                game.add_game_played(len(player_names))

                # Add players to the game and update their stats
                for player_name in player_names:
                    player = self.players[player_name]
                    game.add_player(player)
                    player.add_game(game.name)
                    player.add_game_played()

                # Handle the different result types
                if result_type == "winner":
                    winner_name = results[0]
                    self.players[winner_name].add_game_won()
                    game.add_winner(winner_name)

                elif result_type == "points":
                    for i, player_name in enumerate(player_names):
                        points = int(results[i])
                        if points == max([int(x) for x in results]):
                            self.players[player_name].add_game_won()
                            game.add_winner_points(player_name, points)
                        if points == min([int(x) for x in results]):
                            self.players[player_name].add_game_lost()
                            game.add_loser(player_name)

                elif result_type == "places":
                    for i, player_name in enumerate(results):
                        if i == 0:
                            self.players[player_name].add_game_won()
                            game.add_winner(player_name)
                        if i == len(results)-1:
                            self.players[player_name].add_game_lost()
                            game.add_loser(player_name)

        # seda juppi kasutasin siis, kui tahtsin näha, mis sodi objektidesse on imetud
        # for player_name in self.players:
        #   print(vars(self.players[player_name]))
        # for game_name in self.games:
        #    print(vars(self.games[game_name]))

    def get(self, query):
        if query == "/players":
            # return a list of the names of all players
            return list(self.players.keys())

        elif query == "/games":
            # return a list of the names of all games
            return list(self.games.keys())

        elif query == "/total":
            # return the total number of games played
            return sum(game.num_games_played for game in self.games.values())

        elif query.startswith("/total/"):
            # get the type of result that the query is requesting
            parts = query.split("/")
            result_type = parts[2]

            # return the total number of games with the specified result type
            count_g = 0
            for game in self.games.values():
                if game.result_type == result_type:
                    count_g += game.num_games_played
            return count_g

        elif query.startswith("/player/"):
            # get the name of the player
            parts = query.split("/")
            player_name = parts[2]

            if parts[3] == "amount":
                # return the total number of games played by the player
                return self.players[player_name].num_games_played

            elif parts[3] == "won":
                # return the total number of games won by the player
                return self.players[player_name].num_games_won

            elif parts[3] == "favourite":
                # get a list of all the games played by the player
                games_played = self.players[player_name].games_played

                # find the game played most frequently by the player
                return max(set(games_played), key=games_played.count)

        elif query.startswith("/game/"):
            # get the name of the game
            parts = query.split("/")
            game_name = parts[2]

            if parts[3] == "amount":
                # return the total number of games played of the game
                return self.games[game_name].num_games_played

            elif parts[3] == "player-amount":
                # return the maximum number of players who played the game
                return max(self.games[game_name].players_per_game)

            elif parts[3] == "most-wins":
                # return the name of the player who has won the game the most
                winners = self.games[game_name].winners
                return max(set(winners), key=winners.count)

            elif parts[3] == "most-losses":
                # return the name of the player who has lost the game the most
                losers = self.games[game_name].losers
                return max(set(losers), key=losers.count)

            elif parts[3] == "most-frequent-winner":
                # create a dictionary to store the win rates of all players
                win_rates = {}

                # iterate over all players in the game
                for player in self.games[game_name].players:
                    # calculate the player's win rate
                    win_rate = player.num_games_won / player.num_games_played
                    # add the win rate to the dictionary
                    win_rates[player.name] = win_rate

                # get the name of the player with the highest win rate
                most_frequent_winner = max(win_rates, key=win_rates.get)

                # return the name of the player with the highest win rate
                return most_frequent_winner

            elif parts[3] == "most-frequent-loser":
                # create a dictionary to store the losing rates of all players in the game
                losing_rates = {}

                # iterate over all players in the game
                for player in self.games[game_name].players:
                    # calculate the player's losing rate
                    losing_rate = player.num_games_lost / player.num_games_played
                    # add the losing rate to the dictionary
                    losing_rates[player.name] = losing_rate

                # get the name of the player with the highest losing rate
                most_frequent_loser = max(losing_rates, key=losing_rates.get)

                # return the name of the player with the highest losing rate
                return most_frequent_loser

            elif parts[3] == "record-holder":
                # return the name of the player with the highest score in the game
                return self.games[game_name].record_holder

            else:
                # return an error message if the query is invalid
                return "Invalid query"
