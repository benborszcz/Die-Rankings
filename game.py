from team import Team

class Game:
    def __init__(self, team1: Team, team2: Team, score: list, timestamp):
        self.team1 = team1
        self.team2 = team2
        self.score = score
        self.timestamp = timestamp
        self.etz_timestamp = None

    def point_difference(self):
        return self.score[0] - self.score[1]

    def save_data(self):
        with open("games.txt", 'a') as f:
            f.write(f"{self.team1.player1.name}-{self.team1.player2.name} ({self.score[0]}) vs ({self.score[1]}) {self.team2.player1.name}-{self.team2.player2.name}\n")
