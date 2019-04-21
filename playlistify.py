import sys
import spotipy
import credentials

from spotipy import util


def get_playlists(sp, user):
    items = sp.user_playlists(user)['items']
    playlists = {pl['name']: pl['id'] for pl in items}
    return playlists


def get_n_last_liked_ids(sp, n):
    items = sp.current_user_saved_tracks(n)['items']
    return get_item_track_ids(items)


def get_item_track_ids(items):
    return {it['track']['id'] for it in items}


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
liked_songs = get_n_last_liked_ids(sp, playlist_length)
playlist_songs = get_item_track_ids(sp.user_playlist(username, playlist_id)['tracks']['items'])
new_songs = liked_songs - playlist_songs
old_songs = playlist_songs - liked_songs

if new_songs:
    sp.user_playlist_add_tracks(username, playlist_id, new_songs)
if old_songs:
    sp.user_playlist_remove_all_occurrences_of_tracks(username, playlist_id, old_songs)
