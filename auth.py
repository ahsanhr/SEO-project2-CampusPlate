# auth.py — signup, login, JWT issuance + verification

# this file handles everything related to users signing up and logging in
# when someone signs up we save their username, email, and password (hashed) to the db

# once they log in we give them a JWT so they stay logged in
# the token expires after 24 hours

# also need a login_required decorator that checks the token on protected routes
# reads Authorization header, verifies the token, returns 401 if bad or missing

# endpoints:
#   POST /api/auth/signup  → create account, return JWT
#   POST /api/auth/login   → verify credentials, return JWT

from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
