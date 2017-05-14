import socket
from subprocess import Popen, PIPE, STDOUT
import os
import time
import string
import requests
import json

class UnsupportedFileTypeException(Exception):
    '''Raised if the file type is not among the list of supported types'''
    pass

class FileNotFoundException(Exception):
    '''raised if the file is not valid'''
    pass

class VLCCommsError(Exception):
    '''raised if a command failed to execute'''
    pass


class VLC(object):
    def __init__(self, host="127.0.0.1", port=8080):
        #connection attrs
        self.host = host
        self.port = port
        #private playlist var, stores list of file paths
        #mirrors the list in the player at all times
        self._playlist = []

        #used to determine if a 
        self.supported = ["mp4", "avi", "mkv", "flv", ".aac", "3gp"] # add more later
        
        #creating an instance of the vlc window
        #local socket connection to the vlc player
        

    @property
    def playlist(self):
        '''returns list of file paths'''
        return self._playlist

    @property
    def connection_open(self):
        try:
            resp = requests.get("http://%s:%s/requests/status.json" % \
            (self.host, self.port),
             auth=("", "1234"))
            if resp.status_code == 200:
                return True
            else: return False
        except Exception as e:
            return False

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
        if self.connection_open:
            return
        Popen(["vlc", "-I", "http"],
                            stdout=PIPE, stdin=PIPE,
                            stderr=PIPE)


    def check_path(self, path):
        '''Ensures all files added to the application are 
        valid paths.'''
     
        if not os.path.isfile(path):
            raise FileNotFoundException()
        path, file = os.path.split(path)
        name, ext = file.split(".")

        if ext not in self.supported:
            raise UnsupportedFileTypeException()


    def execute(self, cmd):
        '''Prepare a command and send it to VLC'''
        request_string = \
        "http://%s:%s/requests/status.xml?command=%s" % (
            self.host, self.port, cmd)
        resp =requests.get(request_string, auth=("","1234"))
        
    def toggle_fullscreen(self):
        '''puts the windows in full screen'''
        resp = requests.get(
            "http://%s:%s/requests/status.json" % (self.host, self.port), auth=("", "1234"))
        js = json.loads(resp.content)
        print js["fullscreen"]
        if js["fullscreen"] == 0:
            print "toggled"
            self.execute('fullscreen')
            resp = requests.get(
            "http://%s:%s/requests/status.json" % (self.host, self.port), auth=("", "1234"))
            js = json.loads(resp.content)
            print js["fullscreen"]

    def toggle_loop(self):
        '''makes the vlc player loop the current playlist'''
        resp = requests.get(
            "http://%s:%s/requests/status.json" % (self.host, self.port), auth=("", "1234"))
        js = json.loads(resp.content)
        if not js["loop"]:
            self.execute("pl_loop")


    def pause(self):
        """Checks the current state to make sure the player is playing something"""
        self.execute('pl_pause')

    def play(self):
        """First checks if a valid file is currently loaded."""
        self.execute('pl_play')
        time.sleep(5)
        self.toggle_fullscreen()
        self.toggle_loop()

    def stop(self):
        """checks first if there is something to stop"""
        self.execute('pl_stop')


    def _enqueue(self, path):
        '''adds a file to the playlist'''
        self.check_path(path)
        data = self.execute(
            'in_enqueue&input=%s' % (
                os.path.abspath(path),))
        

    def clear(self):
        '''clears all files from the playlist'''
        self.execute('clear')
        self._playlist = []
