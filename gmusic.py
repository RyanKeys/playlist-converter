from gmusicapi import Mobileclient
import os

mc = Mobileclient()
if "credentials" not in os.listdir(os.getcwd()):
    mc.perform_oauth(
        storage_filepath=os.path.join(os.getcwd(), "credentials"), open_browser=True)
mc.oauth_login(device_id=Mobileclient.FROM_MAC_ADDRESS,
               oauth_credentials='./credentials')


def get_all_playlists():

    playlists = mc.get_all_playlists(
        incremental=False, include_deleted=None, updated_after=None)
    return playlists


def get_playlist_contents(playlist_id):
    for playlist in get_all_playlists():
        if playlist['id'] == playlist_id:
            return mc.get_shared_playlist_contents(share_token=playlist['shareToken'])


if __name__ == "__main__":
    get_playlist_contents(get_all_playlists()[0]['id'])
