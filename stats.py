
class StatGenerator:
    def __init__(self, players, teams, games):
        self.teams = teams
        self.players = players
        self.games = games

    def generate_overall_stats(self):
        mean_score = self._mean_score()
        max_score = self._max_score()
        min_score = self._min_score()
        max_gap_score = self._max_gap_score()
        mean_score_gap = self._mean_score_gap()

        return {
            'mean_score': mean_score,
            'max_score': max_score.to_string(),
            'max_gap_score': max_gap_score.to_string(),
            'mean_score_gap': mean_score_gap
        }
    
    def get_player(self, name):
        ret = None
        for player in self.players:
            if player.name == name:
                ret = player
                return ret
        return None

    def generate_player_stats(self, player_name):
        player = self.get_player(player_name)
        mean_score = self._mean_score(player)
        max_score = self._max_score(player)
        min_score = self._min_score(player)
        max_gap_score = self._max_gap_score(player)
        mean_score_gap = self._mean_score_gap(player)

        return {
            'mean_score': mean_score,
            'max_score': max_score.to_string(),
            'max_gap_score': max_gap_score.to_string(),
            'mean_score_gap': mean_score_gap
        }
    

    def _mean_score(self, player=None):
        winning_scores = []
        losing_scores = []
        for game in self.games:
            if player not in [game.team1.player1, game.team1.player2, game.team2.player1, game.team2.player2] and player != None:
                continue
            if player in [game.team1.player1, game.team1.player2]:
                winning_scores.append(game.score[0])
                losing_scores.append(game.score[1])
                continue
            elif player in [game.team2.player1, game.team2.player2]:
                winning_scores.append(game.score[1])
                losing_scores.append(game.score[0])
                continue
            if game.score[0] > game.score[1]:
                winning_scores.append(game.score[0])
                losing_scores.append(game.score[1])
            else:
                winning_scores.append(game.score[1])
                losing_scores.append(game.score[0])
        mean_score = [sum(winning_scores)/len(winning_scores), sum(losing_scores)/len(losing_scores)]
        return mean_score
    
    def _mean_score_gap(self, player=None):
        winning_scores = []
        losing_scores = []
        for game in self.games:
            if player not in [game.team1.player1, game.team1.player2, game.team2.player1, game.team2.player2] and player != None:
                continue
            if player in [game.team1.player1, game.team1.player2]:
                winning_scores.append(game.score[0])
                losing_scores.append(game.score[1])
                continue
            elif player in [game.team2.player1, game.team2.player2]:
                winning_scores.append(game.score[1])
                losing_scores.append(game.score[0])
                continue
            if game.score[0] > game.score[1]:
                winning_scores.append(game.score[0])
                losing_scores.append(game.score[1])
            else:
                winning_scores.append(game.score[1])
                losing_scores.append(game.score[0])
        
        total = 0
        for i in range(len(winning_scores)):
            total += winning_scores[i] - losing_scores[i]

        mean_score = total/len(winning_scores)
        return mean_score
    
    def _max_score(self, player=None):
        max = None
        for game in self.games:
            if player not in [game.team1.player1, game.team1.player2, game.team2.player1, game.team2.player2] and player != None:
                continue
            if player in [game.team1.player1, game.team1.player2] and game.score[0] < game.score[1]:
                continue
            elif player in [game.team2.player1, game.team2.player2] and game.score[1] < game.score[0]:
                continue
            if max == None: 
                max = game
                continue
            if game.score[0]+game.score[1] > max.score[0]+max.score[1]:
                max = game
        return max

    def _min_score(self, player=None):
        min = None
        for game in self.games:
            if player not in [game.team1.player1, game.team1.player2, game.team2.player1, game.team2.player2] and player != None:
                continue
            if player in [game.team1.player1, game.team1.player2] and game.score[0] > game.score[1]:
                continue
            elif player in [game.team2.player1, game.team2.player2] and game.score[1] > game.score[0]:
                continue
            if min == None: 
                min = game
                continue
            if game.score[0]+game.score[1] < min.score[0]+min.score[1]:
                min = game
        return min

    def _max_gap_score(self, player=None):
        max = None
        for game in self.games:
            if player not in [game.team1.player1, game.team1.player2, game.team2.player1, game.team2.player2] and player != None:
                continue
            if player in [game.team1.player1, game.team1.player2] and game.score[0] < game.score[1]:
                continue
            elif player in [game.team2.player1, game.team2.player2] and game.score[1] < game.score[0]:
                continue
            if max == None: 
                max = game
                continue
            if abs(game.score[0]-game.score[1]) > abs(max.score[0]-max.score[1]):
                max = game
        return max