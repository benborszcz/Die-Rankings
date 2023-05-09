from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
from tracking import Tracking
from game import Game
from datetime import datetime
from scheduling import generate_schedule_for_players

tracking = Tracking()

app = Flask(__name__)

cred = credentials.Certificate("die-rankings-firebase-admin.json") #you need to upload your own firebase file
firebase_admin.initialize_app(cred)
db = firestore.client()


def save_game_data_to_firebase(team1_player1, team1_player2, team2_player1, team2_player2, team1_score, team2_score):
    # Add game data to Firebase
    game_data = {
        'team1_player1': team1_player1,
        'team1_player2': team1_player2,
        'team2_player1': team2_player1,
        'team2_player2': team2_player2,
        'team1_score' : team1_score,
        'team2_score' : team2_score,
        'timestamp': datetime.now()
    }
    db.collection('games').add(game_data)


def fetch_individual_rankings_from_firebase():
    # Fetch individual rankings from Firebase
    player_docs = db.collection('players').order_by('elo', direction=firestore.Query.DESCENDING).stream()
    players = [doc.to_dict() for doc in player_docs]
    return players

def fetch_individual_rankings_from_tracking():
    # Fetch individual rankings from Tracking
    return tracking.players


def fetch_team_rankings_from_firebase():
    # Fetch team rankings from Firebase
    team_docs = db.collection('teams').order_by('wins', direction=firestore.Query.DESCENDING).stream()
    teams = [doc.to_dict() for doc in team_docs]
    return teams

def fetch_team_rankings_from_tracking():
    # Fetch team rankings from Tracking
    return tracking.teams


def fetch_game_history_from_firebase():
    # Fetch game history from Firebase
    game_docs = db.collection('games').stream()
    games = [{'id': doc.id, **doc.to_dict()} for doc in game_docs]
    return games


def fetch_game_from_firebase(game_id):
    # Fetch a single game from Firebase
    game_doc = db.collection('games').document(game_id).get()
    game = {'id': game_doc.id, **game_doc.to_dict()}
    return game


def update_game_data_in_firebase(game_id, team1_player1, team1_player2, team2_player1, team2_player2, team1_score, team2_score):
    # Update game data in Firebase
    game_data = {
        'team1_player1': team1_player1,
        'team1_player2': team1_player2,
        'team2_player1': team2_player1,
        'team2_player2': team2_player2,
        'team1_score' : team1_score,
        'team2_score' : team2_score
    }
    db.collection('games').document(game_id).update(game_data)


def delete_game_from_firebase(game_id):
    # Delete a game from Firebase
    db.collection('games').document(game_id).delete()

@app.route('/')
def home():
    if len(tracking.players) == 0:
        game_history = fetch_game_history_from_firebase()
        tracking.load_data(game_history)

    return render_template('home.html')

@app.route('/add_player', methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        # Handle form submission
        player_name = request.form['player_name']
        tracking.get_player(player_name)  # Replace with your function to add the new player
        return redirect(url_for('enter_game'))
    else:
        return render_template('add_player.html')

@app.route('/enter_game', methods=['GET', 'POST'])
def enter_game():
    if len(tracking.players) == 0:
        game_history = fetch_game_history_from_firebase()
        tracking.load_data(game_history)

    if request.method == 'POST':
        # Process submitted game data

        team1_player1 = request.form['team1_player1']
        team1_player2 = request.form['team1_player2']
        team2_player1 = request.form['team2_player1']
        team2_player2 = request.form['team2_player2']
        team1_score = request.form['team1_score']
        team2_score = request.form['team2_score']

        # Update data in Firebase
        # Example:
        save_game_data_to_firebase(team1_player1, team1_player2, team2_player1, team2_player2, team1_score, team2_score)

        team1 = tracking.get_team(tracking.get_player(team1_player1), tracking.get_player(team1_player2))
        team2 = tracking.get_team(tracking.get_player(team2_player1), tracking.get_player(team2_player2))

        game = Game(team1, team2, [int(team1_score), int(team2_score)])

        tracking.update_data(game)

        return redirect(url_for('home'))
    else:
        players = fetch_individual_rankings_from_tracking()  # Replace with your function to get the list of players
        return render_template('enter_game.html', players=players)


@app.route('/generate_schedule', methods=['GET', 'POST'])
def generate_schedule():
    if len(tracking.players) == 0:
        game_history = fetch_game_history_from_firebase()
        tracking.load_data(game_history)

    if request.method == 'POST':
        # Process submitted schedule data

        number_of_games = int(request.form['number_of_games'])
        selected_players = request.form.getlist('players[]')

        players = []
        for selected_player in selected_players:
            players.append(tracking.get_player(selected_player))


        # Generate the schedule using the selected players and number of games
        # Example:
        schedule = generate_schedule_for_players(players, number_of_games)

        # Save the generated schedule to Firebase (if needed)
        # Example:
        # save_schedule_to_firebase(schedule)

        # Redirect to a new page to display the generated schedule or pass it to the template
        # Example:
        return render_template('display_schedule.html', schedule=schedule)

    else:
        players = fetch_individual_rankings_from_tracking()  # Replace with your function to get the list of players
        return render_template('generate_schedule.html', players=players)
    



@app.route('/individual_rankings')
def individual_rankings():
    
    game_history = fetch_game_history_from_firebase()
    tracking.load_data(game_history)
   
    players = fetch_individual_rankings_from_tracking()

    players = sorted(players, key=lambda x: x.elo, reverse=True)

    return render_template('individual_rankings.html', players=players)


@app.route('/team_rankings')
def team_rankings():

    game_history = fetch_game_history_from_firebase()
    tracking.load_data(game_history)

    teams = fetch_team_rankings_from_tracking()

    teams = sorted(teams, key=lambda x: x.elo, reverse=True)

    return render_template('team_rankings.html', teams=teams)


@app.route('/game_history')
def game_history():
    games = fetch_game_history_from_firebase()
    print(games)
    return render_template('game_history.html', games=games)


@app.route('/edit_game/<game_id>', methods=['GET', 'POST'])
def edit_game(game_id):
    if request.method == 'POST':
        # Process submitted game data
        # Example:
        team1_player1 = request.form['team1_player1']
        team1_player2 = request.form['team1_player2']
        team2_player1 = request.form['team2_player1']
        team2_player2 = request.form['team2_player2']
        team1_score = request.form['team1_score']
        team2_score = request.form['team2_score']
        # Add more fields as needed

        # Update data in Firebase
        # Example:
        update_game_data_in_firebase(game_id, team1_player1, team1_player2, team2_player1, team2_player2, team1_score, team2_score)

        return redirect(url_for('game_history'))
    game = fetch_game_from_firebase(game_id)
    return render_template('edit_game.html', game=game)




@app.route('/delete_game/<game_id>', methods=['POST'])
def delete_game(game_id):
    password = request.form['password']
    correct_password = 'yhessno'  # Replace this with the correct password

    if password == correct_password:
        delete_game_from_firebase(game_id)
        return redirect(url_for('game_history'))
    else:
        return "Invalid password", 403




if __name__ == '__main__':
    app.run(debug=True)