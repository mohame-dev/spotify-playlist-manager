import base64
import hashlib
import os
import requests
import json
import urllib.parse
from dotenv import load_dotenv


class Authorization:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET_ID')
        self.redirect_uri = 'http://localhost:5000/callback'
        self.auth_url = 'https://accounts.spotify.com/authorize'
        self.token_url = 'https://accounts.spotify.com/api/token'

    def _post(self, url, headers, data):
        response = requests.post(url, headers=headers, data=data)
        response_json = json.loads(response.content)
        return response.status_code, response_json

    def _generate_code_verifier(self):
        return base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('ascii')

    def _generate_code_challenge(self, code_verifier):
        sha256 = hashlib.sha256(code_verifier.encode('ascii')).digest()
        return base64.urlsafe_b64encode(sha256).rstrip(b'=').decode('ascii')

    def get_authorization_url(self):
        code_verifier = self._generate_code_verifier()
        code_challenge = self._generate_code_challenge(code_verifier)
        os.environ["CODE_VERIFIER"] = code_verifier  # Save for later use

        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'user-read-private playlist-read-private playlist-modify-public playlist-modify-private',
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }

        query_string = urllib.parse.urlencode(params)
        return f'{self.auth_url}?{query_string}'

    def exchange_code_for_token(self, code):
        code_verifier = os.getenv('CODE_VERIFIER')
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'code_verifier': code_verifier
        }
        status, response = self._post(
            self.token_url, {'Content-Type': 'application/x-www-form-urlencoded'}, data)
        if status == 200:
            os.environ["SPOTIFY_ACCESS_TOKEN"] = response.get('access_token')
            os.environ["REFRESH_TOKEN"] = response.get('refresh_token')
        return status, response

    def refresh_access_token(self):
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': os.getenv("REFRESH_TOKEN"),
            'client_id': self.client_id
        }
        status, response = self._post(
            self.token_url, {'Content-Type': 'application/x-www-form-urlencoded'}, data)
        if status == 200:
            os.environ["SPOTIFY_ACCESS_TOKEN"] = response.get('access_token')
            os.environ["REFRESH_TOKEN"] = response.get('refresh_token')
        return status, response

    def get_access_token(self):
        return os.getenv("SPOTIFY_ACCESS_TOKEN")

    def get_refresh_token(self):
        return os.getenv("REFRESH_TOKEN")

    def set_access_token(self):
        os.environ["SPOTIFY_ACCESS_TOKEN"]
