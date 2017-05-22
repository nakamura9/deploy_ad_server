import socket
from subprocess import Popen, PIPE, STDOUT
import os
import time
import string
import requests
import json
import omxplayer


class UnsupportedFileTypeException(Exception):
    '''Raised if the file type is not among the list of supported types'''
    pass


class FileNotFoundException(Exception):
    '''raised if the file is not valid'''
    pass


class OmxCommsError(Exception):
    '''raised if a command failed to execute'''
    pass


class Omx(object):
    def __init__(self):
        # connection attrs
        # private playlist var, stores list of file paths
        # mirrors the list in the player at all times
        self._playlist = []
        self._player = None 
        # used to determine if a
        self.supported = ["mp4", "avi", "mkv",
                          "flv", ".aac", "3gp"]  # add more later

        # creating an instance of the vlc window
        # local socket connection to the vlc player

    @property
    def playlist(self):
        '''returns list of file paths'''
        return self._playlist

    @property
    def connection_open(self):
        return self._player.is_playing()

    @playlist.setter
    def playlist(self, arg):
        """Takes a string, tuple or a list as an argument and 
        updates the player's playlist and the local_playlist variable
        enqueues the vlc object with a playlist of all the files stored in it
        can only add files to the playlist"""

        if isinstance(arg, (list, tuple)):
            for path in arg:
                self.check_path(path)
                if not path in self._playlist:
                    data = self._enqueue(path)

        elif isinstance(arg, str):
            self.check_path(arg)
            if not arg in self._playlist:
                data = self._enqueue(arg)

    @playlist.deleter
    def playlist(self):
        '''clears the local playlist var and the remote one'''
        self._playlist = []
        self.clear()

    def create_player(self):
        if self.playlist == []:
            raise Exception("The video player has no files ot add")
        else:
            self._player = omxplayer.OMXPlayer(self._playlist[0])

    def check_path(self, path):
        '''Ensures all files added to the application are 
        valid paths.'''

        if not os.path.isfile(path):
            raise FileNotFoundException()
        path, file = os.path.split(path)
        name, ext = file.split(".")

        if ext not in self.supported:
            raise UnsupportedFileTypeException()

    
    def toggle_fullscreen(self):
        '''For compatibility'''
        return True
        
    def toggle_loop(self):
        '''for compatibility'''
        return True
        
    def pause(self):
        """Checks the current state to make sure the player is playing something"""
        if self._player:
            self._player.pause()
    def play(self):
        """First checks if a valid file is currently loaded."""
        if self._player:
            self._player.play()
        

    def stop(self):
        """checks first if there is something to stop"""
        if self._player:
            self._player.stop()

    def _enqueue(self, path):
        '''adds a file to the playlist'''
        self.playlist = path
    def clear(self):
        '''clears all files from the playlist'''
        del self.playlist
        
    def playlist_loop(self):
        """Get the currently playing video
        get its remaining time by subtracting its 
        current time from its duration and creating a new instance for each file"""
        if not self._player:
            self.create_player()
        while True:
            time.sleep(0.5)
            remaining = self._player.duration() - self._player.position()
            if remaining < 1:
                current = self._playlist.index(self._player.get_source())

                if current < len(self._playlist) - 2:
                    next = self._playlist[current + 1]
                else: next = self._playlist[0]
                self._player.load(next)



