# plate.py — generate-plate endpoint + knapsack matching algorithm

# the main feature — picks a combination of real dining hall items
# that fits the user's calorie and macro budget for the meal

# algorithm (knapsack-style):
#   score each item by how closely its macro ratios match the user's target
#   greedily pick the best items without going over the calorie cap
#   stop when max_items is hit or the budget runs out

# log the result to the recommendations table after generating

# endpoint:
#   POST /api/v1/generate-plate
#   body: { meal_type, max_items }
#   returns: { items: [...], totals: { calories, protein, carbs, fat } }
#   requires valid JWT

from flask import Blueprint

plate_bp = Blueprint('plate', __name__, url_prefix='/api/v1')
