import os
from player import Player
from team import Team
from game import Game


class Tracking:
    def __init__(self, filename = None):
        self.filename = filename
        self.players = []
        self.teams = []

    def load_data(self, game_history):

        # Sort the game_history by timestamp from earliest to latest
        game_history = sorted(game_history, key=lambda x: x['timestamp'])

        self.players = []
        self.teams = []

        for game in game_history:
            team1 = self.get_team(self.get_player(game['team1_player1']), self.get_player(game['team1_player2']))
            team2 = self.get_team(self.get_player(game['team2_player1']), self.get_player(game['team2_player2']))
            game = Game(team1, team2, [int(game['team1_score']), int(game['team2_score'])])
            print(game)
            self.update_data(game)

    def save_data(self):
        with open(self.filename, 'w') as f:
            for player in self.players:
                f.write(f"{player.name} {player.elo}\n")
            for team in self.teams:
                f.write(f"{team.player1.name},{team.player2.name},{team.wins},{team.games}\n")


    def update_data(self, game):
        team1 = game.team1
        team2 = game.team2

        winner = team1
        loser = team2

        if game.score[0] < game.score[1]:
            winner = team2
            loser = team1
          
        winner.add_game()
        winner.add_win()
        loser.add_game()

        winner_elo = (winner.player1.elo + winner.player2.elo) / 2
        loser_elo = (loser.player1.elo + loser.player2.elo) / 2
        rating_diff = loser_elo - winner_elo

        win_reward = 8

        rating_diff_multiplier = 0.05

        compensated_win_reward = win_reward + (rating_diff * rating_diff_multiplier)

        point_diff = game.point_difference()

        point_diff_multiplier = 0.125

        rating_change = round((compensated_win_reward + (point_diff * point_diff_multiplier)), 2)

        for winning_player in [winner.player1, winner.player2]:
            winning_player.update_elo(round(rating_change+0.5, 2))
            
        for losing_player in [loser.player1, loser.player2]:
            losing_player.update_elo(round(-rating_change+0.5, 2))

        # Team Elo
        
        team_elo_difference = loser.elo - winner.elo
        team_compensated_win_reward = win_reward + (team_elo_difference * rating_diff_multiplier)
        team_rating_change = round((team_compensated_win_reward + (point_diff * point_diff_multiplier)), 2)
        winner.update_elo(round(team_rating_change+0.5, 2))
        loser.update_elo(round(-team_rating_change+0.5, 2))
        

    def get_player(self, name):
        ret = None
        for player in self.players:
            if player.name == name:
                ret = player
                return ret
        self.players.append(Player(name))
        return self.players[-1]

    def get_team(self, player1, player2):
        ret = None
        for team in self.teams:
            if (team.player1.name == player1.name and team.player2.name == player2.name) or (team.player1.name == player2.name and team.player2.name == player1.name):
                ret = team
                return ret
        self.teams.append(Team(player1, player2))
        return self.teams[-1]

    def display_data(self):
        print("\n\nIndividual Rankings:")
        for player in sorted(self.players, key=lambda x: x.elo, reverse=True):
            print(player)

        print("\n\nTeam Rankings:")
        for team in sorted(self.teams, key=lambda x: x.wins, reverse=True):
            print(team)

