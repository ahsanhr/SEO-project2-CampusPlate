# from flask_debugtoolbar import DebugToolbarExtension              # this doesnt work 
from flask import Flask, render_template, url_for, flash, redirect, request, abort
import os
from dotenv import load_dotenv
import git
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
import subprocess
import hmac
import hashlib
from pathlib import Path


base_dir = Path(__file__).resolve().parent
env_path = base_dir / '.env'
load_dotenv(dotenv_path=env_path)
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY") 

app = Flask(__name__)                    # this gets the name of the file so Flask knows it's name
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.debug = True
# toolbar = DebugToolbarExtension(app)              #yeah this doesnt work 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(60), nullable=False)

  def __repr__(self):
    return f"User('{self.username}', '{self.email}')"

with app.app_context():
  db.create_all()

# this is from gemini, to set up the webhook and to validate the token. 
# its not working though so i just kept the parts from the codio and from gemini that matched up 
# GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

# def is_valid_signature(x_hub_signature, data, private_key):
#     """Verify that the payload matches the GitHub signature"""
#     hash_algorithm, github_signature = x_hub_signature.split('=', 1)
#     if hash_algorithm != 'sha256':
#         return False
    
#     algorithm = hashlib.sha256
#     mac = hmac.new(private_key.encode('utf-8'), msg=data, digestmod=algorithm)
#     return hmac.compare_digest(mac.hexdigest(), github_signature)

@app.route('/update_server', methods=['POST'])
def webhook():
    # # 1. Validate the signature from GitHub
    # x_hub_signature = request.headers.get('X-Hub-Signature-256')
    # if not x_hub_signature:
    #     abort(400, "Missing signature")
        
    # if not is_valid_signature(x_hub_signature, request.data, GITHUB_WEBHOOK_SECRET):
    #     abort(403, "Invalid signature")

    # 2. If valid, execute the deployment script
    if request.method == 'POST':
        payload = request.json
        # Optional: Only deploy if the push is to the main branch
        if payload.get('ref') == 'refs/heads/master':
            # Run the bash script we created in Step 1
            script_path = '/home/SEOweek3practice/SEO-week3-practice/post-merge.sh'
            subprocess.Popen([script_path])
            return 'Update initialized successfully', 200
        else:
            return 'Push event ignored (not main branch)', 200
    else:
        abort(400)

# gemini help end


@app.route("/")                          # this tells you the URL the method below is related to
@app.route("/home")
def home():
    return render_template('home.html', subtitle='Home Page', text='This is the home page')

# def hello_world():
#     return "<p>Hello, World But this time with a webhook again again</p>"        # this prints HTML to the webpage, the "hello world"

@app.route("/second_page")
def second_page():
    return render_template('second_page.html', subtitle='Second Page', text='This is the second page')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit(): # checks if entries are valid
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home')) # if so - send to home page
    return render_template('register.html', title='Register', form=form)
  
if __name__ == '__main__':               # this should always be at the end
    app.run(debug=True, host="0.0.0.0")

