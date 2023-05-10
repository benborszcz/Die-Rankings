class Player:
    def __init__(self, name, elo=1000):
        self.name = name
        self.elo = elo
        self.games = 0
        self.wins = 0
        self.win_percentage = 0.0
        self.penalty = 0.0

    def add_game(self):
        self.games += 1
        self.win_percentage = self.win_percentage_calc()

    def add_win(self):
        self.wins += 1
        self.win_percentage = self.win_percentage_calc()

    def win_percentage_calc(self):
        return round((self.wins / self.games) * 100, 2) if self.games > 0 else 0

    def update_elo(self, delta):
        self.elo += delta

    def get_elo(self):
        return self.elo - self.penalty

    def __str__(self):
        return f"{self.name}: {self.elo}"