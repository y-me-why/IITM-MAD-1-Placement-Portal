from flask import Flask
from application.database import db
from application.controller import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
db.init_app(app)


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)