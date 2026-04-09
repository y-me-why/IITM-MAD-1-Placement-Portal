from flask import Flask
app = None
from application.database import db     

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.sqlite3'
    app.config['SECRET_KEY'] = '1234567890'
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()
from application.controller import *
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role = 'admin').first()
        if admin is None:
            print("Creating admin")
            admin = User(email = 'admin@thesu.in', password = '123', role = 'admin')
            db.session.add(admin)
            db.session.commit()
    app.run()
