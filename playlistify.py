import sys
import spotipy
import credentials

from spotipy import util
from datetime import datetime


def get_playlists(sp, user):
    items = sp.user_playlists(user)['items']
    playlists = {pl['name']: pl['id'] for pl in items}
    return playlists


def get_n_last_liked(sp, n):
    items = sp.current_user_saved_tracks(n)['items']
    return items


def sorted_id(items):
    items = list((it['track']['id'], it['added_at']) for it in items)
    items = sorted(items, key=lambda x: to_timestamp(x[1]), reverse=True)
    return [it[0] for it in items]


def item_track_ids(items):
    return {it['track']['id'] for it in items}


def to_timestamp(date):
    ts = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ').timestamp()
    return ts


scope = 'playlist-modify-public user-library-read'
username = sys.argv[1]
playlist_length = sys.argv[2]

token = util.prompt_for_user_token(username, scope, client_id=credentials.client_id,
                                   client_secret=credentials.client_secret, redirect_uri=credentials.redirect_uri)
sp = spotipy.Spotify(auth=token)

# Create playlist if it does not exist.
pl_name = 'Recently liked'
playlists = get_playlists(sp, username)
if pl_name not in playlists:
    sp.user_playlist_create(username, pl_name)
    playlists = get_playlists(sp, username)

playlist_id = playlists[pl_name]

# Get new/old songs and add/remove them.
liked_songs = sorted_id(get_n_last_liked(sp, playlist_length))
playlist_songs = item_track_ids(sp.user_playlist(username, playlist_id)['tracks']['items'])

if not set(liked_songs) == playlist_songs:
    print('Updating!')
    sp.user_playlist_replace_tracks(username, playlist_id, liked_songs)
