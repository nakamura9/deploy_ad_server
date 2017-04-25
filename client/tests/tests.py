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


    """"def test_get_updates(self):
        try:
            self.requests.get("localhost:8000/summary")
        except:
            raise Exception("This test cannot run without a corresponding development server")

        
        self.requests.post()
        self.client.get_updates()
        self.assertNotEqual(self.client.ads, {})

    def test_get_initial_ads(self):
        test = self.requests.get("http://localhost:8000/summary")
        
        if test.status_code != 200:
            raise Exception("This test cannot run without a corresponding development server")

        ad = self.requests.post("http://localhost:8000/add_advertisment/", data=self.push_ad_data)
        print ad.text

        c = self.requests.post("http://localhost:8000/add_client", data =self.push_client)
        print c.text


        self.client.get_initial_ads()
        self.assertNotEquals(self.ads, {})"""


if __name__ == "__main__":
    ut.main()