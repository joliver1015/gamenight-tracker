from models import Player, db

def add_player(user, player_name):
    player = Player(player_name=player_name)
    user.players.append(player)
    db.session.commit()

def recent_games(player):
    games = player.sessions
    if len(games) > 0:
        recent = sorted(games, key=lambda x: x.date, reverse=True)
        last_ten = recent[:10]
        return last_ten
    else:
        return None




