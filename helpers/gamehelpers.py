from models import db, Game, Session, Winner

def add_session(user, game ,date, players):
    session = Session(date=date)
    for player in players:
        session.players.append(player)
    user.sessions.append(session)
    game.sessions.append(session)
    db.session.commit()

def add_winner(session, winners):
    for winner in winners:
        w = Winner(winner_name=winner)
        session.winners.append(w)
    db.session.commit()

def remove_game(user, session):
    session.winners.clear()
    user.sessions.remove(session)
    db.session.delete(session)
    db.session.commit()

def last_played(user):
    sessions = user.sessions
    recent = sorted(sessions, key=lambda x: x.date, reverse=True)
    last_five = recent[:5]
    return last_five

def most_played(user):
    games = user.games
    top_games = []
    for game in games:
        top_games.append({'game_name':game.game_name, 'games_played': len(game.sessions)})
    top_games.sort(key=lambda x: x['games_played'], reverse=True)
    top_five = top_games[:5]
    return top_five


    
