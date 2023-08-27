import os
from pickletools import read_uint2
from player import Player
from team import Team
from game import Game

LOOP_NUMBER = 50

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

        games = []
        for game in game_history:
            team1 = self.get_team(self.get_player(game['team1_player1']), self.get_player(game['team1_player2']))
            team2 = self.get_team(self.get_player(game['team2_player1']), self.get_player(game['team2_player2']))
            game = Game(game['id'], team1, team2, [int(game['team1_score']), int(game['team2_score'])], game['timestamp'])
            games.append(game)
            self.update_data(game)

        orders = []

        # Forward order
        orders.append(games)

        # Alternated order
        alternated_games = []
        for i in range(0, len(games), 2):
            alternated_games.append(games[i])
        for i in range(1, len(games), 2):
            alternated_games.append(games[i])
        orders.append(alternated_games)

        # Backwards order
        orders.append(games[::-1])

        # From the middle order
        middle_games = []
        middle = len(games) // 2
        for i in range(len(games)):
            middle_games.append(games[(middle + i) % len(games)])
        orders.append(middle_games)

        # Reverse Alternated order
        reversed_alternated_games = []
        for i in range(len(games)-1, -1, -2):
            reversed_alternated_games.append(games[i])
        for i in range(len(games)-2, -1, -2):
            reversed_alternated_games.append(games[i])
        orders.append(reversed_alternated_games)

        # Circular Order
        circular_games = []
        for i in range(len(games)):
            circular_games.append(games[(i+1) % len(games)])
        orders.append(circular_games)

        # Reverse Circular Order
        reverse_circular_games = []
        for i in range(len(games)):
            reverse_circular_games.append(games[(i-1) % len(games)])
        orders.append(reverse_circular_games)

        # Random Order 1
        import random
        random.seed(123123123)
        random_games = games.copy()
        random.shuffle(random_games)
        orders.append(random_games)

        # Random Order 2
        random.seed(233233233)
        random_games = games.copy()
        random.shuffle(random_games)
        orders.append(random_games)

        # Random Order 3
        random.seed(696969696)
        random_games = games.copy()
        random.shuffle(random_games)
        orders.append(random_games)


        for i in range(int(LOOP_NUMBER/10)):
            for game_order in orders:
                for game in game_order:
                    self.update_data_elo_strict(game)

        




    def save_data(self):
        with open(self.filename, 'w') as f:
            for player in self.players:
                f.write(f"{player.name} {player.elo}\n")
            for team in self.teams:
                f.write(f"{team.player1.name},{team.player2.name},{team.wins},{team.games}\n")


    def bottom_quartile_games_played_teams(self):
        games_played = sorted([team.games for team in self.teams])
        quartile_index = int(len(games_played) / 4)
        return games_played[quartile_index]

    def bottom_quartile_games_played_players(self):
        games_played = sorted([player.games for player in self.players])
        quartile_index = int(len(games_played) / 4)
        return games_played[quartile_index]

    def update_data(self, game):
        # Get the playing teams
        team1 = game.team1
        team2 = game.team2

        # Determine the winner and loser based on the game score
        winner = team1
        loser = team2
        if game.score[0] < game.score[1]:
            winner = team2
            loser = team1
        
        winner.add_game()
        loser.add_game()
        winner.add_win()
        

        # Update the games played and wins for the winner and loser
        self.update_elo(winner, loser, game)

    def update_data_elo_strict(self, game):
        # Get the playing teams
        team1 = game.team1
        team2 = game.team2

        # Determine the winner and loser based on the game score
        winner = team1
        loser = team2
        if game.score[0] < game.score[1]:
            winner = team2
            loser = team1

        # Update the games played and wins for the winner and loser
        self.update_elo(winner, loser, game)
        

    def update_elo(self, winner, loser, game):
        

        # Calculate the Elo rating difference for the teams
        team_elo_difference = loser.elo - winner.elo

        # Calculate the Elo rating difference for the players
        winner_elo = (winner.player1.elo + winner.player2.elo) / 2
        loser_elo = (loser.player1.elo + loser.player2.elo) / 2
        player_elo_difference = loser_elo - winner_elo

        # Set the base rewards
        win_reward = 10/LOOP_NUMBER
        play_reward = (win_reward/5)

        # Set multipliers
        rating_diff_multiplier = (win_reward/500)
        point_diff_multiplier = (win_reward/100)

        # Calculate the point difference between the winner and the loser
        point_diff = game.point_difference()

        # Calculate the compensated win reward based on the rating difference
        team_compensated_win_reward = win_reward + (team_elo_difference * rating_diff_multiplier)
        player_compensated_win_reward = win_reward + (player_elo_difference * rating_diff_multiplier)
        
        # Calculate the rating change based on the compensated win reward and point difference
        team_rating_change = (team_compensated_win_reward + (point_diff * point_diff_multiplier))
        player_rating_change = (player_compensated_win_reward + (point_diff * point_diff_multiplier))

        # Update the Elo ratings for the teams and the players
        self.update_team_elo(winner, loser, team_rating_change, play_reward)
        self.update_player_elo(winner, loser, player_rating_change, play_reward)

        return winner, loser

    def update_team_elo(self, winner, loser, rating_change, play_reward):
        
        Q1 = self.bottom_quartile_games_played_teams()

        # Update the team Elo ratings for the winner and the loser
        winner.update_elo(rating_change + play_reward)
        winner.penalty = 0.0
        if winner.games < Q1: winner.penalty = winner.elo
        

        loser.update_elo(-rating_change + play_reward)
        loser.penalty = 0.0
        if loser.games < Q1: loser.penalty = loser.elo
      

    def update_player_elo(self, winner, loser, rating_change, play_reward):

        Q1 = self.bottom_quartile_games_played_players()

        # Update the individual Elo ratings for the winner and loser players
        for winning_player in [winner.player1, winner.player2]:
            winning_player.update_elo(rating_change + play_reward)
            winning_player.penalty = 0.0
            if winning_player.games < Q1: winning_player.penalty = winning_player.elo

        for losing_player in [loser.player1, loser.player2]:
            losing_player.update_elo(-rating_change + play_reward)
            losing_player.penalty = 0.0
            if losing_player.games < Q1: losing_player.penalty = losing_player.elo
        

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
