#!/usr/bin/env python3

from spotiplex import SpotiPlex


#############################################################################################################################
#                                                       Configuration

# how to get these:
# https://developer.spotify.com/dashboard/
# log in and click Create A Client ID
spotifyInfo = {
    'clientId': '',         # insert your client ID
    'clientSecret': '',     # insert your client secret
    'user': ''              # insert your Spotify user name (or whoever owns the playlist)
}

# how to get the token:
# https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
plexInfo = {
    'url': '',              # insert your Plex server URL (has to look similar to this: http://192.168.1.100:32400)
    'token': ''             # insert your Plex token
}

pl = ''                     # insert your Spotify playlist ID you want to process (you can get this by right-clicking your playlist, go to Share and Copy Spotify URI, insert the number here)
plName = ''                 # insert the name of the Plex playlist

#############################################################################################################################

splex = SpotiPlex(spotifyInfo, plexInfo)

# get playlist info from Spotify
items = splex.getSpotifyPlaylist(pl)

# check if playlist already exists in Plex
plexPlaylist = splex.checkForPlexPlaylist(plName)

if plexPlaylist is not None:
    # playlist exists, check for differences
    itemsToAdd, itemsToKeepPlex = splex.comparePlaylists(items, plexPlaylist)
else:
    itemsToAdd = items
    itemsToKeepPlex = []

# Go and put those songs on your server at this step
#
# ...
# I wrote myself a script (not included) to do this, this would be the place to launch it, like:
# from magicalmodulename import Files
# Files.download()
# Files.toServer()
#
# Afterwards, continue with the workflow:

# check if the new items are found by Plex
present, missing = splex.checkPlexFiles(itemsToAdd)


if plexPlaylist is not None:
    splex.addToPlexPlaylist(plexPlaylist, present)
else:
    newPlaylistItems = present + itemsToKeepPlex
    splex.createPlexPlaylist(plName, newPlaylistItems)


print('Done.')