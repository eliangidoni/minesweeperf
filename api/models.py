import random
from flask import json
from api import db
import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(128), unique=True)

    def __init__(self, first_name, last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.email


class Game(db.Model):
    STATE_NEW = 0
    STATE_STARTED = 1
    STATE_PAUSED = 2
    STATE_TIMEOUT = 3
    STATE_WON = 4
    STATE_LOST = 5
    STATE_CHOICES = (
        (STATE_NEW, 'new'),
        (STATE_STARTED, 'started'),
        (STATE_PAUSED, 'paused'),
        (STATE_TIMEOUT, 'timeout'),
        (STATE_WON, 'won'),
        (STATE_LOST, 'lost'),
    )

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    title = db.Column(db.String(255), default='Game')

    board = db.Column(db.Text)  # Board as a JSON matrix. (0-9: adjacent mines, x: mine.
    player_board = db.Column(db.Text)  # Board as a JSON matrix. (v: visible, h: hidden, ?: question mark, !: exclamation mark.
    state = db.Column(db.Integer, default=STATE_NEW)
    duration_seconds = db.Column(db.Integer, default=0)
    elapsed_seconds = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)
    resumed_timestamp = db.Column(db.DateTime)
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    player = db.relationship('User', backref=db.backref('games', lazy='dynamic'))

    def __init__(self):
        None

    def __repr__(self):
        return '<Game %r>' % self.title

    def _get_state(self):
        return [s[1] for s in Game.STATE_CHOICES if self.state == s[0]][0]

    def _get_board_view(self):
        view = []
        board = json.loads(self.board)
        player_board = json.loads(self.player_board)
        for i in range(len(board)):
            view_row = []
            for j in range(len(board[i])):
                if player_board[i][j] == 'v':
                    view_row.append(board[i][j])
                elif player_board[i][j] == 'h':
                    view_row.append(' ')
                else:
                    view_row.append(player_board[i][j])
            view.append(view_row)
        return view

    @staticmethod
    def _inside_board(rows, cols, point):
        y, x = point
        return (x >= 0 and x < cols) and (y >= 0 and y < rows)

    @staticmethod
    def _adjacent_points(rows, cols, x, y):
        up = (y - 1, x)
        down = (y + 1, x)
        left = (y, x - 1)
        right = (y, x + 1)
        upper_right = (y - 1, x + 1)
        upper_left = (y - 1, x - 1)
        lower_right = (y + 1, x + 1)
        lower_left = (y + 1, x - 1)
        points = [up, down, left, right, upper_left, upper_right, lower_left, lower_right]
        return [p for p in points if Game._inside_board(rows, cols, p)]

    @staticmethod
    def _fill_adjacent(board, rows, cols, x, y):
        if board[y][x] != 'x':
            return
        for p in Game._adjacent_points(rows, cols, x, y):
            py, px = p
            if board[py][px] != 'x':
                board[py][px] = str(int(board[py][px]) + 1)

    @staticmethod
    def new_boards(rows, cols, mines):
        assert mines < (rows * cols)  # funny check!

        board = [['0' for j in range(cols)] for i in range(rows)]
        player_board = [['h' for j in range(cols)] for i in range(rows)]
        for i in range(mines):
            mine_set = False
            while not mine_set:
                x = random.randint(0, cols - 1)
                y = random.randint(0, rows - 1)
                if board[y][x] != 'x':
                    board[y][x] = 'x'
                    mine_set = True
        for i in range(rows):
            for j in range(cols):
                Game._fill_adjacent(board, rows, cols, j, i)
        return json.dumps(board), json.dumps(player_board)

    def reveal_at(self, x, y):
        pboard = json.loads(self.player_board)
        if pboard[y][x] == 'v':
            return
        pboard[y][x] = 'v'
        self.player_board = json.dumps(pboard)
        board = json.loads(self.board)
        rows, cols = len(board), len(board[0])
        if board[y][x] == '0':
            for p in Game._adjacent_points(rows, cols, x, y):
                py, px = p
                self.reveal_at(px, py)

    def is_mine_at(self, x, y):
        board = json.loads(self.board)
        return (board[y][x] == 'x')

    def is_all_revealed(self):
        board = json.loads(self.board)
        pboard = json.loads(self.player_board)
        rows, cols = len(board), len(board[0])
        for i in range(rows):
            for j in range(cols):
                if board[i][j] != 'x' and pboard[i][j] != 'v':
                    return False
        return True

    def mark_flag_at(self, x, y):
        board = json.loads(self.player_board)
        board[y][x] = '!'
        self.player_board = json.dumps(board)

    def mark_question_at(self, x, y):
        board = json.loads(self.player_board)
        board[y][x] = '?'
        self.player_board = json.dumps(board)

    def serialize(self):
        obj = {'id': self.id,
               'title': self.title,
               'state': self._get_state(),
               'board_view': self._get_board_view(),
               'duration_seconds': self.duration_seconds,
               'elapsed_seconds': self.elapsed_seconds,
               'score': self.score,
               'resumed_timestamp': self.resumed_timestamp}
        return obj
