# goals.py — goal input (direct + calculated), edit/update

# two ways a user can set their goals:
# 1. direct      — they enter calories + macros themselves
# 2. calculated  — they enter age, height, weight, and a fitness goal
#                  and we run the Mifflin-St Jeor equation to get their targets

# goals are saved to the db tied to the user, upserted if they already exist
# all routes require a valid JWT

# endpoints:
#   POST /api/goals/direct      → save targets directly
#   POST /api/goals/calculated  → calculate targets from body stats, then save
#   PUT  /api/goals             → update the active goal

from flask import Blueprint

goals_bp = Blueprint('goals', __name__, url_prefix='/api/goals')
