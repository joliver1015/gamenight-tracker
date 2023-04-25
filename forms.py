import os
from datetime import timedelta
from xml.dom import ValidationErr
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectMultipleField , DateField, widgets
from wtforms.validators import DataRequired, Length
from wtforms_sqlalchemy.fields import  QuerySelectMultipleField
from wtforms.csrf.session import SessionCSRF
from models import Player

class BaseForm(FlaskForm):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = os.environ["CSRF_SECRET"].encode('utf-8')
        csrf_time_limit = timedelta(minutes=30)

class RegisterForm(BaseForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired(), Length(min=9)])
    email = StringField("Email", validators=[DataRequired()])

class LoginForm(BaseForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired(), Length(min=9)])

class ChangePassword(BaseForm):
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=9)])

class PlayerForm(BaseForm):
    player_name = StringField('Player Name', validators=[DataRequired()])

class GameForm(BaseForm):
    game_name = StringField('Game Name', validators=[DataRequired()])

class SessionForm(BaseForm):
    date = DateField("Game Date", validators=[DataRequired()])
    players = QuerySelectMultipleField("Players", query_factory=lambda:
        Player.query.all(), widget=widgets.ListWidget(prefix_label=False),option_widget=widgets.CheckboxInput())

class WinnerForm(BaseForm):
    winner = SelectMultipleField("Winner(s)", widget=widgets.ListWidget(prefix_label=True), option_widget=widgets.CheckboxInput())