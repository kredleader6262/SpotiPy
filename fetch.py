import requests
import configparser
import os
from pathlib import Path
import re
import shutil

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Check if config.ini exists
if not os.path.exists('config.ini'):
    # Create config.ini with blank values
    config = configparser.ConfigParser()
    config['SPOTIFY'] = {'client_id': '', 'client_secret': '', 'user_id': ''}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    print("Please fill out the necessary details in config.ini")
    exit()

config = configparser.ConfigParser()
config.read('config.ini')
client_id = config['SPOTIFY']['client_id']
client_secret = config['SPOTIFY']['client_secret']
user_id = config['SPOTIFY']['user_id']

scope="playlist-read-private user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri="http://localhost:8888/callback", scope=scope))

def get_token(client_id, client_secret):
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    payload = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, headers=headers, data=payload, auth=(client_id, client_secret))
    token_json = response.json()
    return token_json['access_token']

def fetch_playlist(playlist_id, token):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    playlist = response.json()
    return playlist

def fetch_user_playlists(sp):
    playlists = []
    response = sp.current_user_playlists()
    while response:
        playlists.extend(response['items'])
        if response['next']:
            response = sp.next(response)
        else:
            response = None
    return playlists

def extract_playlist_info(playlist, token):
    playlist_name = playlist.get('name')
    playlist_description = playlist.get('description')

    # Extract track information
    tracks = playlist_info.get('tracks', {}).get('items', [])
    track_list = []
    for track in tracks:
        track_info = track.get('track', {})
        
        if track_info is None:
            print(f"Skipping track because its info is None.")
            continue

        track_name = track_info.get('name')
        track_artists = [artist.get('name') for artist in track_info.get('artists', [])]
        track_list.append((track_name, track_artists))

    # Print playlist information
    print(f"Playlist Name: {playlist_name}")
    print(f"Playlist Description: {playlist_description}")

    # Print track information
    for i, (track_name, track_artists) in enumerate(track_list, 1):
        print(f"Track {i}: {track_name} by {', '.join(track_artists)}")

# Fetch the user's playlists
token = get_token(client_id, client_secret)
playlists = fetch_user_playlists(sp)

downloads_dir = Path("downloads")

# If the directory exists, delete its contents
if downloads_dir.exists():
    for file in downloads_dir.iterdir():
        if file.is_file():
            file.unlink()
        elif file.is_dir():
            shutil.rmtree(file)
        print(f"Deleted {file}")
else:
    # Otherwise, create the directory
    downloads_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created {downloads_dir}")

# For each playlist, fetch and save its tracks
for i, playlist in enumerate(playlists):
    playlist_id = playlist.get('id')
    playlist_info = fetch_playlist(playlist_id, token)

    playlist_name = playlist_info.get('name')
    playlist_description = playlist_info.get('description')

    # Extract track information
    tracks = playlist_info.get('tracks', {}).get('items', [])
    track_list = []
    for track in tracks:
        try:
            if track is None:
                print(f"Skipping track because its info is None.")
                continue
            else:
                track_info = track.get('track', {})
                track_name = track_info.get('name')
                track_artists = [artist.get('name') for artist in track_info.get('artists', [])]
                track_list.append((track_name, track_artists))
        except:
            print(f"Skipping track because of an error. {track}")
            continue

    # Check if playlist_name is not None
    if playlist_name is None:
        print(f"Skipping playlist number {i+1} because its name is None.")
        continue

    # Clean and trim the playlist name for use as a filename
    filename = "".join(c for c in playlist_name if c.isalnum() or c in (' ',)).rstrip()
    filename = re.sub(r'[^\x00-\x7F]+', '', filename)  # Remove emojis and other non-ASCII characters
    filename = filename[:255]  # Trim to maximum filename length

    # Prepare the playlist information
    playlist_content = f"Playlist Name: {playlist_name}\n"
    playlist_content += f"Playlist Description: {playlist_description}\n"

    # Add track information
    for i, (track_name, track_artists) in enumerate(track_list, 1):
        playlist_content += f"Track {i}: {track_name} by {', '.join(track_artists)}\n"

    # Save the playlist info to a file
    with open(f'downloads/{filename}.txt', 'w', encoding='utf-8') as f:
        f.write(playlist_content)
    print(f"Downloaded playlist {i+1} of {len(playlists)}: {playlist_name}")