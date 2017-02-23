from flask import abort, request, jsonify, render_template, current_app
from api import app, db
import models
import datetime


@app.route('/')
def index():
    """Generates a list of endpoints and their docstrings."""
    urls = dict([(r.rule, current_app.view_functions.get(r.endpoint).func_doc)
                 for r in current_app.url_map.iter_rules()
                 if not r.rule.startswith('/static')])
    return render_template('index.html', urls=urls)


@app.route('/test/', methods=['POST'])
def api_test():
    """
    Do nothing just testing *blabla*.
    """
    args = request.get_json()
    resp = {
        'hello': 'world',
        'number': 3,
        'args': args
    }
    return jsonify(resp)


@app.route('/api/v1/games/state/', methods=['GET'])
def api_state():
    """
    **Returns** the game object. (GET method)
    Arguments:
        - game_id

    The current `state` can be:

    - **new** : for a new game.
    - **started** : if the game is running.
    - **paused** : if the game is paused.
    - **timeout** : if the game finished by timeout.
    - **won** : if the player won the game.
    - **lost** : if the player lost the game.

    The `board_view` is a matrix where each cell can be:

    - an empty character if the user hasn't set a mark or revealed the cell.
    - **?** : if the user set a question mark
    - **!** : if the user set a red flag mark
    - **x** : to indicate the cell has a mine.
    - an integer (0-8) to indicate the number of adjacent mines to the cell.
    """
    args = request.get_json()
    game = models.Game.query.get(int(args['game_id']))
    return jsonify(game.serialize())


@app.route('/api/v1/games/new/', methods=['POST'])
def api_new():
    """
    Creates a new game. (POST method)
    **Returns** the game state.
    Arguments:
        - rows (number of rows)
        - columns (number of columns)
        - mines (number of mines, should be less than the board size)
    """
    args = request.get_json()
    rows = int(args['rows'])
    columns = int(args['columns'])
    mines = int(args['mines'])
    board, player_board = models.Game.new_boards(rows, columns, mines)

    user = models.User.query.limit(1).all()  # Hack to use a single user for now.
    if user is None:
        user = models.User("test", "test", "test@test.com")
        db.session.add(user)
        db.session.commit()
        user = models.User.query.limit(1).all()
    game = models.Game()
    game.title = 'Game for user %s' % (user[0].first_name)
    game.board = board
    game.player_board = player_board
    game.state = models.Game.STATE_NEW
    game.player_id = user[0].id
    game.resumed_timestamp = datetime.datetime.utcnow()
    db.session.add(game)
    db.session.commit()
    return jsonify(game.serialize())


@app.route('/api/v1/games/pause/', methods=['POST'])
def api_pause():
    """
    Pauses a given game (stops time tracking). (POST method)
    **Returns** the game state.
    Arguments:
        - game_id
    """
    args = request.get_json()
    game = models.Game.query.get(int(args['game_id']))
    return jsonify(game.serialize())


@app.route('/api/v1/games/resume/', methods=['POST'])
def api_resume():
    """
    Resumes a given game (starts time tracking). (POST method)
    **Returns** the game state.
    Arguments:
        - game_id
    """
    args = request.get_json()
    game = models.Game.query.get(int(args['game_id']))
    return jsonify(game.serialize())


@app.route('/api/v1/games/mark_as_flag/', methods=['POST'])
def api_mark_as_flag():
    """
    Set a flag mark in a given cell. (POST method)
    **Returns** the game state.
    Arguments:
        - game_id
        - x (cell index)
        - y (cell index)
    """
    args = request.get_json()
    gameid = int(args['game_id'])
    x = int(args['x'])
    y = int(args['y'])

    game = models.Game.query.get(gameid)
    game.mark_flag_at(x, y)
    db.session.commit()
    return jsonify(game.serialize())


@app.route('/api/v1/games/mark_as_question/', methods=['POST'])
def api_mark_as_question():
    """
    Set a question mark in a given cell. (POST method)
    **Returns** the game state.
    Arguments:
        - game_id
        - x (cell index)
        - y (cell index)
    """
    args = request.get_json()
    gameid = int(args['game_id'])
    x = int(args['x'])
    y = int(args['y'])

    game = models.Game.query.get(gameid)
    game.mark_question_at(x, y)
    db.session.commit()
    return jsonify(game.serialize())


@app.route('/api/v1/games/reveal/', methods=['POST'])
def api_reveal():
    """
    Reveals a given cell. (POST method)
    **Returns** the game state.
    Arguments:
        - game_id
        - x (cell index)
        - y (cell index)
    """
    args = request.get_json()
    gameid = int(args['game_id'])
    x = int(args['x'])
    y = int(args['y'])

    game = models.Game.query.get(gameid)
    game.reveal_at(x, y)
    if game.is_mine_at(x, y):
        game.state = models.Game.STATE_LOST
    elif game.is_all_revealed():
        game.state = models.Game.STATE_WON
    db.session.commit()
    return jsonify(game.serialize())
