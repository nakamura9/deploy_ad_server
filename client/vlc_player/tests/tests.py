import unittest as ut
import time
import os
import sys

sys.path.append(os.path.abspath(".."))

from myvlc import VLC, UnsupportedFileTypeException, FileNotFoundException

class PlayerTests(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v_list = ["video.mp4", "flash.mp4"]
        cls.v_string = "video.mp4"
        cls.v = VLC()

    def test_initial_condition(self):
        self.assertEquals(self.v._playlist, self.v.playlist)

    
    def test_add_file_to_playlist(self):
        del self.v.playlist
        self.v.playlist = self.v_string
        self.assertEquals(self.v._playlist, ["video.mp4"])
    
    def test_add_file_list_to_playlist(self):
        del self.v.playlist
        self.v.playlist = self.v_list
        self.assertEquals(self.v._playlist, ["video.mp4", "flash.mp4"])

    def test_file_type_filter(self):
        self.assertRaises(UnsupportedFileTypeException,
                            self.v.check_path, "tests.py")

    def test_file_existance_filter(self):
        self.assertRaises(FileNotFoundException, self.v.check_path, "caleb.mp4")

    def test_true_response(self):
        response = self.v.clear()
        self.assertEquals(response, True)
        
    @classmethod
    def tearDownClass(cls):
        cls.v.shutdown()


if __name__ == "__main__":
    ut.main()