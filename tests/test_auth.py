# test_auth.py — tests for signup, login, and JWT verification

# things to test:
#   - POST /api/auth/signup with valid data creates a user and returns a token
#   - POST /api/auth/signup with a duplicate email returns 409
#   - POST /api/auth/signup with missing fields returns 400
#   - POST /api/auth/login with correct credentials returns a token
#   - POST /api/auth/login with wrong password returns 401
#   - a protected route with no token returns 401
#   - a protected route with an expired token returns 401
#   - a protected route with a valid token returns 200
