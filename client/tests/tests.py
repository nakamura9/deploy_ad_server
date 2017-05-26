import unittest as ut
import os
import sys
import requests
import test_server
import datetime
import platform 

sys.path.append(os.path.abspath(".."))
from http_client import Client

class TestPlayer():
    def __init__(self):
        self.current = "video.mp4"

class Client_testing(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = Client(id="test pi")
        cls.test_video = os.path.abspath("video.mp4")
        

    def setUp(self):
        self.test_duration = {"start": datetime.date.today().strftime("%Y-%m-%d"),
        "end": datetime.date.today().strftime("%Y-%m-%d"),
        "days":["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
        "interval_one":"0000-2300",
        "interval_two":"0000-0000",
        "interval_three":"0000-0000",
                }
        self.test_ad = {"name": "ad",
                    "link": "stuff",
                    "duration": self.test_duration,
                    "path": self.test_video
                            }
        self.client.ads = {}


    def test_file_system_setup(self):
        self.assertTrue(os.path.exists(os.path.abspath("../Advertisments/")))
        self.assertTrue(os.path.exists("../config.json"))


    def test_start_player(self):
        self.assertEqual(self.client.start_player(), 0)


    def test_ad_expired(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        yesterday= yesterday.strftime("%Y-%m-%d")
        self.test_ad["duration"]["start"] = yesterday
        self.test_ad["duration"]["end"] = yesterday
        self.client.ads["ad"] = self.test_ad
        self.assertTrue(self.client.ad_expired("ad"))


    def  test_ad_not_expired(self):
        self.client.ads["ad"] = self.test_ad
        self.assertFalse(self.client.ad_expired("ad"))


    def test_ad_is_current(self):
        self.client.ads["ad"] = self.test_ad
        self.assertTrue(self.client.ad_is_current("ad"))


    def test_ad_is_not_current_by_day(self):
        self.test_ad["duration"]["days"] = []
        self.client.ads["ad"] = self.test_ad
        self.assertFalse(self.client.ad_is_current("ad"))


    def test_ad_is_not_current_by_time(self):
        self.test_ad["duration"]["interval_one"] = "0000-0100"
        self.client.ads["ad"] = self.test_ad
        self.assertFalse(self.client.ad_is_current("ad"))


    def test_cpu_temp(self):
        temp = self.client.get_cpu_temperature()
        print temp
        if platform.system().lower().startswith("windows"):
            self.assertEqual(temp, -1)
        else:
            self.assertTrue(isinstance(temp, float))


    def test_disk_space(self):
        disk = self.client.get_disk_space()
        if platform.platform().startswith("windows"):
            self.assertEqual(disk, -1)
        else:
            self.assertTrue(isinstance(disk, int))


    def test_disk_usage(self):
        self.assertTrue(isinstance(self.client.get_disk_usage(), float))


    def test_cpu_usage(self):
        self.assertTrue(isinstance(self.client.cpu_usage(), float))


    def test_ping(self):
        self.assertTrue(self.client.ping_server())


    def test_ram_usage(self):
        self.assertTrue(isinstance(self.client.get_ram_usage(), float))


    def test_health_query(self):
        self.client.player= TestPlayer()
        self.assertEqual(self.client.query_health(), 0)
        self.client.player = None

    def test_get_initial(self):
        self.assertEqual(self.client.get_initial_ads(), 0)


    def test_get_updates(self):
        self.assertEqual(self.client.get_updates(), 0)


    def test_upload_health(self):
        self.assertEqual(self.client.upload_health_status(), 0)



    def test_download_file(self):
        self.assertNotEqual(self.client.download_file("media"), -1)


    def test_sync_playlist(self):
        self.client.player.playlist = self.test_video
        self.client.sync_playlist()
        self.assertEquals(self.client.player.playlist, [])


    """def test_run(self):
        self.client.run(5)
        self.assertRaises(Exception, self.client.stop)
    """


    @classmethod
    def tearDownClass(cls):
        pass

if __name__ == "__main__":
    ut.main()