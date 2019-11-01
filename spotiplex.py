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
        playlist = self.sp.user_playlist(self.user, plId)
        totalTracks = playlist['tracks']['total']

        items = []
        if totalTracks > 100:
            # implement dealing with next url
            pass
        else:
            for item in playlist['tracks']['items']:
                items.append({
                    'title': item['track']['name'],
                    'album': item['track']['album']['name'],
                    'artist': item['track']['artists'][0]['name'],
                    #'number': item['track']['track_number'],
                    #'img': item['track']['album']['images'][0]['url']
                })
        
        return items

    def checkPlexFiles(self, playlist):
        'Check if the songs in the playlist are present on the Plex server. Returns list of items to include in the playlist'

        tracks = []
        missing = []

        for item in playlist:
            results = self.plex.search(item['name'], mediatype='track')
            if not results:
                continue
        
            for result in results:
                if type(result) != plexapi.audio.Track:
                    continue
                else:
                    if result.grandparentTitle == item['artist'] and result.parentTitle == item['album']:
                        tracks.append(result)
                        break
                    else:
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
        'Compares the extracted Spotify playlist with the existing Plex playlist. Returns list of tracks to create the new playlist version from'

        plexTracks = pPlaylist.items()
        plexItems = []
        for track in plexTracks:
            plexItems.append({
                'artist': track.grandparentTitle.lower(),
                'album': track.parentTitle.lower(),
                'title': track.title.lower()
            })

        spotifyItems = []
        for item in sPlaylist:
            spotifyItems.append({
                'artist': item['artist'].lower(),
                'album': item['album'].lower(),
                'title': item['title'].lower()
            })

        notInPlex = [item for item in spotifyItems if item not in plexItems]
        notInSpotify = [item for item in plexItems if item not in spotifyItems]

        result = []
        for item in notInPlex:
            for sItem in sPlaylist:
                if item['title'] == sItem['title'].lower():
                    result.append(sItem)
        for item in notInSpotify:
            for track in plexTracks:
                if item['title'] == track.title.lower():
                    result.append({
                        'artist': track.grandparentTitle,
                        'album': track.parentTitle,
                        'title': track.title
                    })
        return result

    def createPlexItems(self, newItems):
        'Creates and returns list of Plex Media items'

        #test = plexapi.media.Media(self.plex, )
        pass

    def createPlexPlaylist(self, name, items):
        'Create the playlist on the Plex server with the given items'
    
        #test = plex.createPlaylist(name, items=items)
        pass
