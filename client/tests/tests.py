import unittest as ut
import os
import sys
from django.test import Client as requests

sys.path.append(os.path.abspath(".."))


from http_client import Client



class Client_testing(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.requests = requests()
        cls.client = Client(id="test pi")
        cls.test_video = os.path.abspath("../vlc_player/tests/flash.mp4")
        cls.test_ad = {"name": "flash",
                    "link": "stuff",
                    "duration": "55",
                    "path": cls.test_video
                            }
        cls.push_ad_data = {"ad_name":"test ad",
                "description":"something",
                "customer":"someone",
                "duration":"10",
                "source": cls.test_video}
        
        cls.push_client = {"client_name": "test pi",
                    "password":"123",
                    "ip":"123123",
                    "location": "somewhere",
                    "test ad": "on"}
        

        
    def setUp(self):
        self.client.ads = {}


    def test_file_system_setup(self):
        print "file"
        self.assertTrue(os.path.exists(os.path.abspath("../Advertisments/")))

    def test_start_player_without_ads(self):
        print "raises"
        self.assertRaises(Exception, self.client.start_player)

    def test_sync_playlist(self):
        print "called"
        self.client.player.playlist = self.test_video
        self.client.sync_playlist()
        self.assertEquals(self.client.player.playlist, [])

    def test_start_player_with_ads(self):
        print "ads"
        self.client.ads = {"flash" : self.test_ad}

        self.client.start_player()
        self.assertIsNotNone(self.client.player)

if __name__ == "__main__":
    ut.main()