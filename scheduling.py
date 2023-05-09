from itertools import combinations
import random
from player import Player

def generate_schedule_for_players(players, number_of_games):
    games_played = {}
    for player in players:
        games_played[player.name] = 0


	# Generate all possible pairings of players
    pairings = list(combinations(players, 2))

    # Generate all possible 2v2 games
    games = list(combinations(pairings, 2))

    # Filter out games where a player is playing twice (i.e., on both teams)
    valid_games = [game for game in games if len(set(game[0] + game[1])) == 4]

    # Initialize the schedule as an empty list
    schedule = []
    
    k=0
    # Loop for each game to be scheduled
    while k < number_of_games:
        
        # If the list of valid games is empty, regenerate the list from the players
        if not valid_games:
            valid_games = [game for game in games if len(set(game[0] + game[1])) == 4]

        # Choose a random game from the list and remove it
        game = random.choice(valid_games)
        valid_games.remove(game)

       
       # Add the chosen game to the schedule
        schedule.append(game)
        

        for i in range(2):
            for j in range(2):
                games_played[game[i][j].name] += 1


        k+=1

    # Find the maximum value and its key
    max_key = max(games_played, key=games_played.get)
    max_val = games_played[max_key]

    # Find the minimum value and its key
    min_key = min(games_played, key=games_played.get)
    min_val = games_played[min_key]

    # Calculate the average value
    avg_val = sum(games_played.values()) / len(games_played)

    print(min_val)
    print(max_val)
    print(games_played)

    if max_val - min_val > 1:
        schedule = generate_schedule_for_players(players, number_of_games)

    return schedule

def generate_tournament(players):
    # Sort players by Elo rating
    sorted_players = sorted(players, key=lambda x: x.elo, reverse=True)

    # Divide players into two groups: high-Elo and low-Elo
    high_elo_players = sorted_players[:len(sorted_players) // 2]
    low_elo_players = sorted_players[len(sorted_players) // 2:]

    # Create teams by pairing high-Elo players together and low-Elo players together
    high_elo_teams = list(combinations(high_elo_players, 2))
    low_elo_teams = list(combinations(low_elo_players, 2))

    # Generate a bracket by combining high-Elo and low-Elo teams
    bracket = []
    for high_elo_team in high_elo_teams:
        for low_elo_team in low_elo_teams:
            bracket.append((high_elo_team, low_elo_team))

    # Shuffle the bracket to randomize the match order
    random.shuffle(bracket)

    # Select a fixed number of games from the bracket
    schedule = bracket[:number_of_games]

    # Assign byes for high-Elo players
    byes = high_elo_players[:len(high_elo_players) // 2]

    return schedule, byes

if __name__ == '__main__':
    # Create a list of players
    players = [
    Player("Alice", elo=1300),
    Player("Bob", elo=1200),
    Player("Charlie", elo=1100),
    Player("David", elo=1000),
    Player("Eve", elo=900),
    Player("Frank", elo=800),
    Player("Garry", elo=800)
]
    
    # Set the number of games to be played
    number_of_games = 6

    # Generate the schedule
    schedule = generate_schedule_for_players(players, number_of_games)

    # Print the schedule
    for i, game in enumerate(schedule):
        print(f"Game {i + 1}: {game[0][0].name} & {game[0][1].name} vs {game[1][0].name} & {game[1][1].name}")
    
        
   