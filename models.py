import math
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False, unique=True)
    players = db.relationship('Player',backref='users', cascade="all, delete")
    games = db.relationship('Game', backref='users', cascade="all, delete")
    sessions = db.relationship('Session', backref='users', cascade='all, delete')

    def __repr__(self) -> str:
        return f"<User {self.username} Email {self.email}"
    
    @classmethod
    def register(cls, username, password, email):
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        return cls(username=username, password=hashed_utf8, email=email)
    
    @classmethod
    def authenticate(cls, username, password):
        u = User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False

session_players = db.Table('session_players',
                db.Column('player_id', db.Integer, db.ForeignKey('players.player_id', ondelete='CASCADE')),
                db.Column('session_id', db.Integer, db.ForeignKey('sessions.session_id')))

class Player(db.Model):
    __tablename__ = "players"

    player_id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    sessions = db.relationship("Session", secondary=session_players, back_populates='players')

    def win_count(self):
        wins = 0
        for session in self.sessions:
            for winner in session.winners:
                if winner.winner_name == self.player_name:
                    wins += 1
        return wins
    
    def winrate(self):
        wins = self.win_count()
        if len(self.sessions) > 0:
            rate = wins / len(self.sessions)
            return math.floor(rate * 100)
        else:
            return 0
    
    def best_game(self):
        if len(self.sessions) > 0:
            game_list = {}
            for session in self.sessions:
                for winner in session.winners:
                    if winner.winner_name == self.player_name:
                        if session.game_name() not in game_list:
                            game_list[session.game_name()] = 1
                        else:
                            game_list[session.game_name()] += 1
            return max(game_list, key=game_list.get)
        else:
            return "No games played"
    
    def top_games(self):
        if len(self.sessions) > 0:
            game_list = {}
            for session in self.sessions:
                for winner in session.winners:
                    if winner.winner_name == self.player_name:
                        if session.game_name() not in game_list:
                            game_list[session.game_name()] = 1
                        else:
                            game_list[session.game_name()] += 1
            return sorted(game_list.items(), key=lambda x:x[1], reverse=True)
        else:
            return "No games played"
    
    def won_game(self, session):
        winners = session.winners
        for winner in winners:
            if winner.winner_name == self.player_name:
                return True
        return False

    def __repr__(self):
        return f"<Player {self.player_name} Wins {self.win_count()}>"


class Game(db.Model):
    __tablename__ = "games"

    game_id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(), nullable=False, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    sessions = db.relationship('Session', backref='games', cascade='all, delete')

    def best_player(self):
        if len(self.sessions) > 0:
            player_list = {}
            for session in self.sessions:
                for winner in session.winners:
                    if winner.winner_name not in player_list:
                        player_list[winner.winner_name] = 1
                    else:
                        player_list[winner.winner_name] += 1
            return max(player_list, key=player_list.get)
        else:
            return "No games played yet"
    
    def leaderboard(self):
        if len(self.sessions) > 0:
            player_list = {}
            for session in self.sessions:
                for winner in session.winners:
                    if winner.winner_name not in player_list:
                        player_list[winner.winner_name] = 1
                    else:
                        player_list[winner.winner_name] += 1
            return sorted(player_list.items(), key=lambda x:x[1], reverse=True)
        else:
            return "No games played yet"
            
class Session(db.Model):
    __tablename__ = 'sessions'

    session_id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'))
    date = db.Column(db.Date, nullable=False)
    players = players = db.relationship('Player', secondary=session_players, back_populates='sessions')
    winners = db.relationship('Winner', backref='game_winners', cascade='all, delete')
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def game_name(self):
        game = Game.query.get(self.game_id)
        return game.game_name

class Winner(db.Model):
    __tablename__= 'winners'

    winner_id = db.Column(db.Integer, primary_key=True)
    winner_name = db.Column(db.String())
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.session_id'))

def connect_db(app):
    db.app = app
    db.init_app(app)

