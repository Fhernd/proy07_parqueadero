import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

base_dir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(base_dir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


with app.app_context():
    db.create_all()

    new_user = User(username='johno', email='johno@mail.co')
    db.session.add(new_user)
    db.session.commit()

    users = User.query.all()
    print(users)

from app import routes
