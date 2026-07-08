# menu.py — dineoncampus.com fetch + caching logic

# fetches today's dining hall menu from dineoncampus.com/uf
# runs once per day — only re-fetches if the stored date is stale

# after fetching, passes the raw data to menu_parser.py to clean and structure it
# then writes the results to the food_items table

# if a fetch fails, fall back to whatever is already in food_items for today
# if an item is still missing macros after parsing, try a nutrition API fallback

from flask import Blueprint

menu_bp = Blueprint('menu', __name__, url_prefix='/api/menu')
