import io
import json
import requests

URL = 'https://api.spotify.com/v1'


class Spotify:
    def __init__(self, auth):
        self.auth = auth

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.auth.get_access_token()}'
        }

    def _refresh_access_token(self):
        status, response = self.auth.refresh_access_token()
        if status != 200:
            raise Exception(f"Failed to refresh token: {status}, {response}")

    def get(self, url):
        """ Makes a GET request to the Spotify API. """
        self._refresh_access_token()
        response = requests.get(url, headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def post(self, url, request_body):
        self._refresh_access_token()
        response = requests.post(
            url, headers=self._get_headers(), json=request_body)
        if response.status_code == 201:
            return response.json()
        else:
            response.raise_for_status()

    def parse_playlist_data(self, data):
        image_placeholder = 'https://cdn.discordapp.com/attachments/1072583184438546522/1273688722621333524/Screen_Shot_2024-08-15_at_19.03.51.png?ex=66bf868f&is=66be350f&hm=777deda40d3c3f0d2e0317a1978527960ba48917ad814c1c6f2dbf4251949a3c&'
        playlists = data.get('items', [])
        parsed = []

        for p in playlists:
            name = p.get('name', 'No Name')
            image_url = (
                p['images'][0].get('url', image_placeholder)
                if p.get('images') else image_placeholder
            )
            playlist_uri = p.get('uri', 'No URI')

            parsed.append({
                'name': name,
                'image_url': image_url,
                'playlist_uri': playlist_uri
            })

        return parsed

    def export_playlist(self, data):
        track_uris = [track['track']['uri'] for track in data.get('items', [])]

        file_content = "\n".join(track_uris)
        buffer = io.BytesIO(file_content.encode())
        buffer.seek(0)

        return buffer

    def get_all_tracks(self, playlist_id):
        """ Fetches all tracks from a playlist, handling pagination. """
        tracks = []
        endpoint = f'{URL}/playlists/{playlist_id}/tracks'

        while endpoint:
            data = self.get(endpoint)
            tracks.extend(data.get('items', []))
            endpoint = data.get('next')

        return tracks

    def create_playlist(self):
        endpoint = '/me/playlists'
        request_body = {
            "name": "Imported playlist",
            "public": False,
        }
        response = self.post(URL + endpoint, request_body)
        return response.get('id')

    def add_to_playlist(self, playlist_id, tracks):
        endpoint = f'/playlists/{playlist_id}/tracks'
        max_uri = 100

        for i in range(0, len(tracks), max_uri):
            chunk = tracks[i:i + max_uri]
            request_body = {
                "uris": chunk
            }
            response = self.post(URL + endpoint, request_body)
