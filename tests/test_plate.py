# test_plate.py — tests for the plate generation + knapsack algorithm

# things to test:
#   - generate-plate returns items that don't exceed the user's calorie target
#   - the number of returned items never exceeds max_items
#   - if there are no menu items for today, returns a clear error
#   - if the user hasn't set goals yet, returns a clear error before running the algorithm
#   - the knapsack result is logged to the recommendations table
#   - calling generate-plate without a JWT returns 401
