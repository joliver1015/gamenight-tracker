import os
from flask import Flask, render_template, session, redirect, g, url_for
from flask_migrate import Migrate
from models import connect_db, db, User, Player, Game, Session
from forms import GameForm, RegisterForm, LoginForm, ChangePassword, SessionForm, PlayerForm, WinnerForm
from helpers.authhelpers import change_password, check_password
from helpers.playerhelper import add_player, recent_games
from helpers.gamehelpers import add_session, add_winner, remove_game, last_played, most_played

CURR_USER_KEY = 'curr_user'
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
connect_db(app)

@app.before_request
def add_user_to_g():
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    session[CURR_USER_KEY] = user.user_id

def do_logout():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/')
def home():
    if g.user:
        recent_games = last_played(g.user)
        top_games = most_played(g.user)
        return render_template('home.html', recent_games=recent_games, top_games=top_games)
    else:
        return render_template('home.html')

@app.route('/register',methods=["GET","POST"])
def register():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        user = User.register(username, password, email)

        db.session.add(user)
        db.session.commit()
        do_login(user)
        return redirect('/')
    return render_template('auth/register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            do_login(user)
            session['user_id'] = user.user_id
            return redirect('/')
        else:
            form.username.errors = ['Invalid username/password']
    return render_template('auth/login.html', form=form)

@app.route('/logout')
def logout():
    do_logout()
    return redirect('/')

@app.route('/unauthorized')
def unauthorized():
    return render_template("error/unauthorized.html")

@app.route('/settings', methods=["GET","POST"])
def settings():
    user = g.user
    password_form = ChangePassword()
    if password_form.validate_on_submit():
        old_password = password_form.old_password.data
        new_password = password_form.new_password.data
        if check_password(user,old_password):
            change_password(user, new_password)
            return redirect('/settings')
        else:
            password_form.old_password.errors = ['Incorrect Password']
    else:
        password_form.new_password.errors = ['Password must be at least 9 characters in length']
    return render_template("user/settings.html", user=user, password_form=password_form)

@app.route('/confirm-delete', methods=["GET","POST"])
def delete_account():
    db.session.delete(g.user)
    do_logout()
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/playerlist', methods=["GET","POST"])
def player_list():
    user = g.user
    if not user:
        return redirect('/unauthorized')
    players = user.players
    form = PlayerForm()
    if form.validate_on_submit():
        player_name = form.player_name.data
        add_player(user, player_name)
        return redirect("/playerlist")
    else:
        form.player_name.errors = ["Field cannot be empty"]
    return render_template("player/playerlist.html", user=user, players=players, form=form)

@app.route('/player/<player_id>')
def player_details(player_id):
    player = Player.query.get_or_404(player_id)
    if len(player.sessions) > 0:
        last_ten = recent_games(player)
        return render_template("player/playerdetail.html", player=player, last_ten=last_ten)
    else:
        no_games = True
        return render_template("player/playerdetail.html", player=player, no_games=no_games)

@app.route('/gamelist', methods = ["GET", "POST"])
def game_list():
    games = g.user.games
    form = GameForm()
    if form.validate_on_submit():
        game_name = form.game_name.data
        game = Game(game_name=game_name)
        g.user.games.append(game)
        db.session.commit()
    return render_template('game/gamelist.html', games=games, form=form)

@app.route('/game/<game_id>', methods=["GET", "POST"])
def game_details(game_id):
    user = g.user
    game = Game.query.get_or_404(game_id)
    form = SessionForm()
    if form.validate_on_submit():
        date = form.date.data
        players = form.players.data
        add_session(user, game, date, players)
        return redirect(url_for('game_details', game_id=game_id))
    if len(game.sessions) > 0:
        return render_template('game/gamedetails.html', user=user, game=game, form=form)
    else:
        no_games = True
        return render_template('game/gamedetails.html', user=user, game=game, form=form, no_games=no_games)


@app.route('/sessionlist', methods=["GET","POST"])
def session_list():
    user = g.user
    sessions = user.sessions
    sessions.sort(key=lambda x: x.date, reverse=True)
    return render_template("session/sessionlist.html", user=user, sessions=sessions)

@app.route('/session/<session_id>', methods=["GET","POST"])
def session_details(session_id):
    session = Session.query.get_or_404(session_id)
    form = WinnerForm()
    form.winner.choices = [(player.player_name, player.player_name) for player in session.players]
    if form.validate_on_submit():
        winners = form.winner.data
        add_winner(session, winners)
        return redirect(url_for("session_details", session_id=session_id))
    return render_template("session/sessiondetails.html", session=session, form=form)

@app.route('/session/<session_id>/deletesession', methods=["GET","POST"])
def delete_session(session_id):
    user = g.user
    session = Session.query.get_or_404(session_id)
    remove_game(user, session)
    return redirect("/sessionlist")