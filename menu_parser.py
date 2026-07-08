# menu_parser.py — Gemini API call to structure raw scraped menu text

# the raw data from dineoncampus.com is messy and inconsistently formatted
# this file sends it to Gemini once per day and asks for clean structured JSON
# matching the food_items schema: name, calories, protein_g, carbs_g, fat_g, station, time_of_day

# rules for the prompt:
#   - return ONLY valid JSON, no extra text
#   - if a macro can't be found in the source, return null — never guess or estimate
#     (wrong nutrition numbers are worse than missing ones for a health app)

# needs GEMINI_API_KEY from .env
