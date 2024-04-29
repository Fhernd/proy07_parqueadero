from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import ConfigDevelopment

app = Flask(__name__)
app.config.from_object(ConfigDevelopment)

db = SQLAlchemy(app)

from app import models


from app import routes
