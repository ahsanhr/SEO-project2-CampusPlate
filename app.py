from flask import Flask, render_template, url_for, flash, redirect, request, abort
from flask_behind_proxy import FlaskBehindProxy
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

from forms import RegistrationForm
from extensions import db


load_dotenv()
# next 3 lines might be needed for when we actually deploy
# base_dir = Path(__file__).resolve().parent
# env_path = base_dir / '.env'
# load_dotenv(dotenv_path=env_path)
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

from models import User

from auth import auth_bp
app.register_blueprint(auth_bp)

from plate import plate_bp
app.register_blueprint(plate_bp)
print(app.url_map)

from goals import goals_bp
app.register_blueprint(goals_bp)

from menu import menu_bp
app.register_blueprint(menu_bp)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/account")
def account():
    return render_template('account.html')

@app.route("/sign_up")
def sign_in():
    return render_template('sign_up.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/build_a_plate")
def build_a_plate():

    # prompt = f"""
    # """

    # response = client.models.generate_content(
    #     model='gemini-2.5-flash',
    #     contents=prompt,
    #     config=types.GenerateContentConfig(
    #         response_mime_type="application/json",
    #         response_schema=DailyPlan,
    #     ),
    # )

    # meal_plan = response.parsed
    return render_template('build_a_plate.html')

@app.route("/previous_meals")
def previous_meals():
    return render_template('previous_meals.html')

def _daily_menu_fetch():
    with app.app_context():
        from menu import fetch_and_store_menu
        fetch_and_store_menu()


with app.app_context():
    db.create_all()
    # populate today's menu on startup if not already loaded
    from menu import fetch_and_store_menu
    fetch_and_store_menu()

# schedule a daily re-fetch at midnight so tomorrow's menu is ready on day change
scheduler = BackgroundScheduler()
scheduler.add_job(_daily_menu_fetch, 'cron', hour=0, minute=0)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
