from flask import Flask, request, redirect, session, url_for
import requests
import json
import os

# Set up a flask app that will run on port 5000 (check the end of the code)
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# LinkedIn API endpoint for retrieving LinkedIn profile information
profile_url = 'https://api.linkedin.com/v2/me'

# LinkedIn app credentials
client_id = 'client_id'
client_secret = 'client_secret'
redirect_uri = 'http://localhost:5000/callback'
scope = 'profile'  # for retrieving member's profile, including id, name, and profile picture
authorization_base_url = 'https://www.linkedin.com/oauth/v2/authorization'

# Token endpoint
token_url = 'https://www.linkedin.com/oauth/v2/accessToken'

@app.route('/')
def home():
    return 'Welcome to the LinkedIn OAuth Flask App! <a href="/login">Login with LinkedIn</a>'

# This function allows user to login to LinkedIn
@app.route('/login')
def login():
    # Authorization URL
    authorization_url = f'{authorization_base_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}'
    return redirect(authorization_url)

# This function allows the Flask server to retrieve the LinkedIn authorization code, access token, and profile information
@app.route('/callback')
def callback():

    # request the authorization code from the LinkedIn
    code = request.args.get('code')

    if not code:
        return "Authorization code not found in request", 400
    elif code:
        
        # Exchange authorization code for access token
        token_response = requests.post(token_url, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret,
        }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        
        if token_response.status_code != 200:
            return "Failed to obtain access token", 400

        # Save access tokenk
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        session['access_token'] = access_token

        # Headers with the access token for authentication
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Connection': 'Keep-Alive'
        }

        # request the LinkedIn profile information
        response = requests.get(profile_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return f'Error: {response.status_code} - {response.text}'

# The server's link is "localhost:5000"
if __name__ == '__main__':
    app.run(port=5000, debug=True)
