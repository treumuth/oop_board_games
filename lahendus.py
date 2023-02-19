class Player:
    # ei hakka pikalt juurdlema, laon objektidesse kõik-võimalikud atribuudid, siis äkki hiljem lihtsam seda sodi uurida
    def __init__(self, name):
        self.name = name
        self.amount_played = 0
        self.games_won = 0
        self.games_lost = 0
        self.games_played = []

    def add_game_played(self):
        self.amount_played += 1

    def add_game_won(self):
        self.games_won += 1

    def add_game_lost(self):
        self.games_lost += 1

    def add_game(self, game):
        self.games_played.append(game)

class Game:
    # sry, sepad, ma isegi ei tea, kas ma hiljem kõiki neid atribuute kasutan
    # mõne atribuudi nimi sai veidi lohakas, aga ei viitsi teha läbivalt rename
    def __init__(self, name, result_type):
        self.name = name
        self.amount_played = 0
        self.players_per_game = []
        self.players = []
        self.winners = []
        self.losers = []
        self.current_record = 0
        self.record_holder = ""
        self.result_type = result_type

    def add_player(self, player):
        self.players.append(player)

    def add_winner_points(self, player, points):
        self.winners.append(player)
        # veider short-cut, aga las jääb
        if points > self.current_record:
            self.current_record = points
            self.record_holder = player

    def add_winner(self, player):
        self.winners.append(player)

    def add_loser(self, player):
        self.losers.append(player)

    def add_game_played(self, num_players):
        self.amount_played += 1
        self.players_per_game.append(num_players)

class Statistics:
    def __init__(self, filename):
        self.players = {}
        self.games = {}

        with open(filename, "r") as file:
            for line in file:
                parts = line.strip().split(";")

                game_name = parts[0]
                player_names = parts[1].split(",")
                result_type = parts[2]
                results = parts[3].split(",")

                for player_name in player_names:
                    if player_name not in self.players:
                        self.players[player_name] = Player(player_name)

                if game_name not in self.games:
                    self.games[game_name] = Game(game_name, result_type)
                game = self.games[game_name]
                game.add_game_played(len(player_names))

                for player_name in player_names:
                    player = self.players[player_name]
                    game.add_player(player)
                    self.players[player_name].add_game(game.name)
                    self.players[player_name].add_game_played()

                if result_type == "winner":
                    winner_name = results[0]
                    self.players[winner_name].add_game_won()
                    game.add_winner(winner_name)

                elif result_type == "points":
                    for i in range(len(player_names)):
                        player_name = player_names[i]
                        points = int(results[i])
                        if points == max([int(x) for x in results]):
                            self.players[player_name].add_game_won()
                            game.add_winner_points(player_name, points)
                        if points == min([int(x) for x in results]):
                            self.players[player_name].add_game_lost()
                            game.add_loser(player_name)

                elif result_type == "places":
                    for i in range(len(results)):
                        player_name = results[i]
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
            return list(self.players.keys())
        elif query == "/games":
            return list(self.games.keys())
        elif query == "/total":
            return sum(game.amount_played for game in self.games.values())
        elif query.startswith("/total/"):
            parts = query.split("/")
            result_t = parts[2]
            loendur = 0
            for game in self.games.values():
                if game.result_type == result_t:
                    loendur += game.amount_played
            return loendur

        elif query.startswith("/player/"):
            parts = query.split("/")
            player_name = parts[2]
            if parts[3] == "amount":
                return self.players[player_name].amount_played
            elif parts[3] == "won":
                return self.players[player_name].games_won
            elif parts[3] == "favourite":
                games_p = self.players[player_name].games_played
                return max(set(games_p), key=games_p.count)

        elif query.startswith("/game/"):
            parts = query.split("/")
            game_name = parts[2]
            if parts[3] == "amount":
                return self.games[game_name].amount_played
            elif parts[3] == "player-amount":
                return max(self.games[game_name].players_per_game)
            elif parts[3] == "most-wins":
                winners = self.games[game_name].winners
                return max(set(winners), key=winners.count)
            elif parts[3] == "most-losses":
                losers = self.games[game_name].losers
                return max(set(losers), key=losers.count)
            elif parts[3] == "most-frequent-winner":
                win_rates = {}
                for player in self.games[game_name].players:
                    # calculate the player's win rate
                    win_rate = player.games_won / player.amount_played
                    # add the win rate to the dictionary
                    win_rates[player.name] = win_rate

                # get the name of the player with the highest win rate
                most_frequent_winner = max(win_rates, key=win_rates.get)

                # return the name of the player with the highest win rate and their win rate
                return (most_frequent_winner)
            elif parts[3] == "most-frequent-loser":
                losing_rates = {}
                for player in self.games[game_name].players:
                    # calculate the player's win rate
                    losing_rate = player.games_lost / player.amount_played
                    # add the win rate to the dictionary
                    losing_rates[player.name] = losing_rate

                # get the name of the player with the highest win rate
                most_frequent_loser = max(losing_rates, key=losing_rates.get)

                # return the name of the player with the highest win rate and their win rate
                return (most_frequent_loser)
            elif parts[3] == "record-holder":
                return self.games[game_name].record_holder

