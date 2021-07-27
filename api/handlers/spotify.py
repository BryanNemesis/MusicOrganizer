from os import environ
import json

import tekore as tk


client_id = environ.get('SPOTIFY_CLIENT_ID')
client_secret= environ.get('SPOTIFY_CLIENT_SECRET')
app_token = tk.request_client_token(client_id, client_secret)
spotify = tk.Spotify(app_token)


def get_album_list(query):
    full_albums = spotify.search(query, types=('album',), limit=10)
    # albums = [shrink_album(album) for album in full_albums]
    return full_albums


def get_album(album_id):
    album = spotify.album(album_id)
    return shrink_album(album)


def shrink_album(album):
    album_dict = json.loads(album.json())
    shrunk_album = {
        'images': album_dict['images'],
        'uri': album_dict['uri'],
        'name': album_dict['name'],
        'url': album_dict['external_urls']['spotify'],
        'artist': ', '.join([x['name'] for x in album_dict['artists']])
    }
    return shrunk_album