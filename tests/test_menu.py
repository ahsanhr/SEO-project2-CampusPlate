# test_menu.py — tests for menu fetch and caching logic

# things to test:
#   - fetch_menu returns a list of items with the expected fields
#   - a second call within the cache window does NOT hit the API again (uses cache)
#   - a call after the cache expires re-fetches from the API
#   - if the API is down, returns stale cached data instead of crashing
#   - _parse_items correctly flattens the nested dineoncampus JSON structure
#   - items with missing macro data come back with null fields (not fabricated values)
