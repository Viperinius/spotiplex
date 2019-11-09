#!/usr/bin/env python3

import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.playlist import Playlist
import plexapi


class SpotiPlex:
    def __init__(self, spotifyInfo, plexInfo):
        self.credManager = SpotifyClientCredentials(client_id=spotifyInfo['clientId'], client_secret=spotifyInfo['clientSecret'])
        self.user = spotifyInfo['user']
        self.sp = spotipy.Spotify(client_credentials_manager=self.credManager)
        self.plex = PlexServer(plexInfo['url'], plexInfo['token'])


    def getSpotifyPlaylist(self, plId):
        'Generate and return a list of tracks of the Spotify playlist'

        #playlist = self.sp.user_playlist(self.user, plId)
        playlist = self.sp.user_playlist_tracks(self.user, playlist_id=plId)

        tracks = playlist['items']
        while playlist['next']:
            playlist = self.sp.next(playlist)
            tracks.extend(playlist['items'])

        items = []
        for item in tracks:
            items.append({
                'title': item['track']['name'],
                'album': item['track']['album']['name'],
                'artist': item['track']['artists'][0]['name'],
                'isrc': item['track']['external_ids']['isrc']
                #'number': item['track']['track_number'],
                #'img': item['track']['album']['images'][0]['url']
            })
        
        return items

    def checkPlexFiles(self, playlist):
        'Check if the songs in the playlist are present on the Plex server. Returns list of found and missing items'

        tracks = []
        missing = []

        for item in playlist:
            results = self.plex.search(item['title'], mediatype='track')
            if not results:
                missing.append(item)
                continue
        
            for result in results:
                if type(result) != plexapi.audio.Track:
                    continue
                else:
                    if result.grandparentTitle.lower() == item['artist'].lower():# and result.parentTitle == item['album']:
                        tracks.append(result)
                        break
                    else:
                        if result == results[-1]:
                            missing.append(item)
                            break

        return tracks, missing
    
    def checkForPlexPlaylist(self, name):
        'Check if a playlist with this name exists in Plex. Returns the playlist if valid, else None'

        try:
            return self.plex.playlist(name)
        except plexapi.exceptions.NotFound:
            return None

    def comparePlaylists(self, sPlaylist, pPlaylist):
        'Compares the extracted Spotify playlist with the existing Plex playlist. Returns list of tracks to create the new playlist version from and missing songs in Plex'

        tracksToAdd = sPlaylist
        plexTracks = pPlaylist.items()
        plexOnlyItems = []
        temp = []
        for track in plexTracks:
            # remove any tracks from Spotify list that are already in Plex
            lastLen = len(temp)
            temp = list(filter(lambda item: not item['title'] == track.title, tracksToAdd))
            if not len(temp) == lastLen:
                tracksToAdd = temp
            else:
                plexOnlyItems.append(track)

        return tracksToAdd, plexOnlyItems

    def createPlexPlaylist(self, name, playlist=None):
        'Create the playlist on the Plex server from given name and a item list'
    
        newPlaylist = self.plex.createPlaylist(name, items=playlist)
        return

    def addToPlexPlaylist(self, plexPlaylist, newItems):
        'Add more items to a Plex playlist'

        return plexPlaylist.addItems(newItems)

    def removeFromPlexPlaylist(self, plexPlaylist, itemsToRemove):
        'Remove given items from a Plex playlist'

        ## Seems not to work properly yet

        for item in itemsToRemove:
            plexPlaylist.removeItem(item)