# SpotiPy | A silly little thing

## fetch.py
This Python script is used to fetch and save information about a user's Spotify playlists. It uses the Spotify Web API and the Spotipy library to interact with Spotify's services.

## Features
- **Configuration File Management**: The script checks for the existence of a `config.ini` file which should contain the necessary Spotify API credentials. If it doesn't exist, it creates one with blank values.

- **Spotify Authentication**: It uses the Spotipy library to handle OAuth2 authentication with Spotify.

- **Fetching Playlists**: The script fetches all playlists of the authenticated user.

- **Fetching Playlist Information**: For each playlist, it fetches detailed information including the playlist name, description, and track details.

- **Cleaning Download Directory**: The script checks for a downloads directory and cleans it before saving new files.

- **Saving Playlist Information**: For each playlist, it saves the playlist information into a text file. The filename is derived from the playlist name, cleaned and trimmed to be valid as a filename. The file contains the playlist name, description, and a list of tracks with their artists.

## Usage
Before running the script, make sure to fill out the necessary details in `config.ini` file. You need to provide your Spotify `client_id`, `client_secret`, and `user_id`.

Run the script with Python:

```bash
python fetch.py