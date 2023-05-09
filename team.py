from player import Player

class Team:
    def __init__(self, player1: Player, player2: Player, wins=0, games=0):
        self.player1 = player1
        self.player2 = player2
        self.wins = wins
        self.games = games
        self.win_percentage = 0.0
        self.elo = 1000

    def add_win(self):
        self.wins += 1
        self.player1.add_win()
        self.player2.add_win()
        self.win_percentage = self.win_percentage_calc()

    def add_game(self):
        self.games += 1
        self.player1.add_game()
        self.player2.add_game()
        self.win_percentage = self.win_percentage_calc()

    def win_percentage_calc(self):
        return round((self.wins / self.games) * 100, 2) if self.games > 0 else 0

    def update_elo(self, delta):
        self.elo += delta

    def __str__(self):
        return f"{self.player1.name}-{self.player2.name}: {self.wins} wins, {self.games} games, {self.win_percentage()}% win rate"