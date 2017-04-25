import socket
from subprocess import Popen, PIPE, STDOUT
import os, time, string

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
    def __init__(self, host="localhost", port=8888):
        #connection attrs
        self.host = host
        self.port = port
        self.fullscreen = False
        self.loop = False
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
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((self.host, self.port))
            sock.sendall("get_title\n".encode())
            data = sock.recv(4096)
        except:
            return False
        else:
            return True

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
        Popen(["vlc", "-I", "rc",
                             "--rc-quiet",
                            "--rc-host",
                            "%s:%s" % (self.host, self.port)],
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
        if not cmd.endswith('\n'):
            cmd = cmd + '\n'
        cmd = cmd.encode()
        if not self.connection_open:
            self.create_player()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((self.host, self.port))
            sock.sendall(cmd)
            data = sock.recv(4096)
            
            #need to implement a return value based on response
        except:
            print "command transmission error"
            data = None 
        finally:
            sock.close()
            return data


    def toggle_fullscreen(self):
        '''puts the windows in full screen'''
        self.fullscreen = not self.fullscreen
        self.execute('f')


    def toggle_loop(self):
        '''makes the vlc player loop the current playlist'''
        self.loop = not self.loop
        self.execute("loop")
#normal player controls 

    def pause(self):
        """Checks the current state to make sure the player is playing something"""
        self.execute('pause')

    def play(self):
        """First checks if a valid file is currently loaded."""
        self.execute('play')
        if not self.fullscreen:
            self.toggle_fullscreen()
        if not self.loop:
            self.toggle_loop()

    def stop(self):
        """checks first if there is something to stop"""
        self.execute('stop')

    def prev(self):
        """Makes sure the playlist is longer than 1"""
        self.execute('prev')

    def next(self):
        """Makes sure the playlist is longer than 1"""
        self.execute('next')

    def _enqueue(self, path):
        '''adds a file to the playlist'''
        self.check_path(path)
        data = self.execute('enqueue %s' % (path,))
        time.sleep(1)
        if data:
            self._playlist.append(path)

    def clear(self):
        '''clears all files from the playlist'''
        self.execute('clear')
        self._playlist = []

    def shutdown(self):
        '''closes the vlc window and closes the socket connection'''
        self.execute('quit')
        self.fullscreen = False
        self._playlist = []
        self.loop = False