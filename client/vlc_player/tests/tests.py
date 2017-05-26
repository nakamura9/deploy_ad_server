import unittest as ut
import time
import os
import sys
import requests
import json

sys.path.append(os.path.abspath(".."))

from myvlc import VLC, UnsupportedFileTypeException, FileNotFoundException

class PlayerTests(ut.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.v_list = ["video.mp4"]
        cls.v_string = "video.mp4"
        cls.v = VLC()


    def setUp(self):
        if not self.v.connection_open:
            self.v.create_player()
        self.v.clear()


    def test_initial_condition(self):
        self.assertEquals(self.v._playlist, self.v.playlist)


    def test_add_file_to_playlist(self):
        del self.v.playlist
        self.v.playlist = self.v_string
        self.assertEquals(self.v._playlist, ["video.mp4"])


    def test_add_file_list_to_playlist(self):
        del self.v.playlist
        self.v.playlist = self.v_list
        time.sleep(2)
        self.assertEquals(self.v._playlist, ["video.mp4"])


    def test_file_type_filter(self):
        self.assertRaises(UnsupportedFileTypeException,
                            self.v.check_path, "tests.py")


    def test_file_existance_filter(self):
        self.assertRaises(FileNotFoundException, self.v.check_path, "caleb.mp4")


    def test_make_connection(self):
        self.assertTrue(self.v.connection_open)


    def test_clear_playlist(self):
        self.v.clear()
        self.assertTrue(self.v._playlist == [])


    def test_enqueue_and_current_property(self):
        self.v._enqueue(self.v_string)
        self.assertEqual(self.v.playlist, ["video.mp4"])


    def test_play_pause_and_stop(self):
        self.v._enqueue(self.v_string)
        self.v.play()
        time.sleep(2)
        resp = requests.get(
            "http://%s:%s/requests/status.json" % (self.v.host, self.v.port), auth=("","1234"))
        js = json.loads(resp.content)
        self.assertEqual(js["fullscreen"], 1)
        self.assertEqual(js["loop"], 1)
        self.assertEqual(self.v.player_status, "playing")
        self.v.pause()
        time.sleep(2)
        self.assertEqual(self.v.player_status, "paused")
        self.v.play()
        self.v.stop()
        time.sleep(2)
        self.assertEqual(self.v.player_status, "stopped")

    def test_close_connection(self):
        if self.v.connection_open:
            self.v.shutdown()

        self.assertFalse(self.v.connection_open)


    @classmethod
    def tearDownClass(cls):
        cls.v.shutdown()


if __name__ == "__main__":
    ut.main()