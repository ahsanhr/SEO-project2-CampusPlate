from flask import Flask, render_template, url_for, flash, redirect, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_behind_proxy import FlaskBehindProxy
from dotenv import load_dotenv
import os

from forms import RegistrationForm


load_dotenv()
# next 3 lines might be needed for when we actually deploy
# base_dir = Path(__file__).resolve().parent
# env_path = base_dir / '.env'
# load_dotenv(dotenv_path=env_path)
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY") 

app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


# register blueprints once each route file is implemented
# from auth  import auth_bp;  app.register_blueprint(auth_bp)
# from goals import goals_bp; app.register_blueprint(goals_bp)
# from menu  import menu_bp;  app.register_blueprint(menu_bp)
# from plate import plate_bp; app.register_blueprint(plate_bp)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', subtitle='Home Page', text='This is the home page')



with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
