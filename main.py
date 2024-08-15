import json
from flask import Flask, request, redirect, url_for, render_template, jsonify, send_file
import auth
from client import Spotify

URL = 'https://api.spotify.com/v1'

app = Flask(__name__)
authorization = auth.Authorization()
client = Spotify(authorization)


@app.route('/')
def index():
    auth_url = authorization.get_authorization_url()
    return render_template('index.html', auth_url=auth_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Authorization code not found', 400

    status, response = authorization.exchange_code_for_token(code)
    if status == 200:
        return redirect(url_for('dashboard'))
    else:
        return f'Failed to get tokens: {status}, {response}', 400


@app.route('/username')
def get_username():
    endpoint = '/me'
    response = client.get(URL + endpoint)
    username = response.get("display_name")
    return jsonify({'username': username})


@ app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@ app.route('/playlists')
def get_playlists():
    endpoint = '/me/playlists'
    response = client.get(URL + endpoint)
    data = client.parse_playlist_data(response)

    return jsonify(data)


@ app.route('/export-playlist/<playlist_id>')
def export_playlist(playlist_id):
    tracks_data = client.get_all_tracks(playlist_id)
    buffer = client.export_playlist({'items': tracks_data})

    return send_file(
        buffer,
        mimetype="text/plain",
        as_attachment=True,
        download_name=f'{playlist_id}.txt'
    )


@ app.route('/import-playlist', methods=['POST'])
def import_playlist():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        content = file.read().decode('utf-8')
        tracks = content.splitlines()

        id = client.create_playlist()
        client.add_to_playlist(id, tracks)

        return jsonify({'success': f'{len(tracks)} tracks uploaded to playlist'}), 200
    else:
        return jsonify({'error': 'Invalid file format, only .txt files are accepted.'}), 400


if __name__ == '__main__':
    app.run(port=5000)
