from models import db, bcrypt

def check_password(user, old_password):
    if bcrypt.check_password_hash(user.password, old_password):
        return True
    else:
        return False

def change_password(user, new_password):
    hashed = bcrypt.generate_password_hash(new_password)
    hashed_utf8 = hashed.decode("utf8") 
    user.password = hashed_utf8
    db.session.commit()