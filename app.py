from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

# register blueprints once each route file is implemented
# from auth  import auth_bp;  app.register_blueprint(auth_bp)
# from goals import goals_bp; app.register_blueprint(goals_bp)
# from menu  import menu_bp;  app.register_blueprint(menu_bp)
# from plate import plate_bp; app.register_blueprint(plate_bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
