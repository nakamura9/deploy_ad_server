# -*- coding: utf-8 -*-
from django.test import TestCase, Client

from models import client_health, clients, ads, ad_schedule, user
from observer import *
import time
import json
import os
import datetime
from utilities import create_thumbnail

class ObserverTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        a = ads.objects.create(
            ad_name="test ad",
            description="something",
            customer="someone",
            duration=10,
            source=os.path.join("test_data", "video.mp4"),
            thumbnail="")

        b = clients.objects.create(
            client_name="test pi",
            password="123",
            ip="123123",
            location="somewhere")


    def setUp(self):
        self.client = clients.objects.get(client_name="test pi")
        self.old = []
        self.ad = ads.objects.get(ad_name="test ad")


    def test_set_up_sucess(self):
        self.assertEquals(self.ad.ad_name, "test ad")

    def test_convert_ad_to_json(self):
        data = {"ad_id":"test ad", 
        "start":datetime.datetime.today(), 
        "end":datetime.datetime.today(), "days":['tuesday'],
        "interval_one":"0000-1000", 
        "interval_two":"1200-1400", 
        "interval_three":"0000-1000"}
        ad_schedule.objects.create(**data)

        data = convert_ad_to_json("test ad")
        duration = json.loads(data)["duration"]
        self.assertNotEqual(duration, {})


    def test_remove_ad_from_client(self):
        observer.add_ad_to_client("test ad", "test pi")
        observer.remove_ad_from_client("test ad", "test pi")
        self.assertEqual(observer.updated_clients["test pi"], {"CREATE": {},
                     "DELETE": ["test ad"]})

    def test_add_ad_to_client(self):
        observer.add_ad_to_client("test ad", "test pi")
        self.assertNotEqual(observer.updated_clients["test pi"]["CREATE"], {})


    def test_client_ads_changed(self):
        """tests add ad to client as well"""
        self.client.client_ads.add(self.ad)
        ret_value = observer.client_ads_changed("test pi", self.old)
        self.assertNotEquals(observer.updated_clients, {})
        self.assertTrue(ret_value)


    def test_ad_clients_changed(self):
        self.ad.ad_clients.add(self.client)
        ret_value = observer.ad_clients_changed("test ad", self.old)
        self.assertNotEquals(observer.updated_clients, {})
        self.assertTrue(ret_value)


    def test_no_changes(self):
        self.assertFalse(observer.ad_clients_changed("test ad", []))
        self.assertFalse(observer.client_ads_changed("test pi", []))


    def test_delete_ad(self):
        """also tests remove ad from client"""
        self.client.client_ads.add(self.ad)
        observer.delete_ad("test ad")  # rename to destroy
        self.assertEquals(observer.updated_clients["test pi"]["DELETE"], ["test ad"])
        self.assertEquals(observer.updated_clients["test pi"]["CREATE"], {})


    def test_update_client(self):
        """checks the return value"""
        data = observer.add_ad_to_client("test ad", "test pi")
        self. assertNotEqual(data, -1)


class GetViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(GetViewsTests, cls).setUpClass()
        cls.client = Client()
        test_user = user.objects.create_user("test", password="test")
        test_user.save()
        a = ads(ad_name="test ad",
                description="something",
                customer="someone",
                duration=10,
                source=os.path.abspath(os.path.join(
                            "test_data", "video.mp4")),
                thumbnail="")
        a.save()
        c = clients(client_name="test pi",
                    password="123",
                    ip="123123",
                    location="somewhere")
        c.save()

    def setUp(self):
        resp = self.client.login(username="test", password="test")
        
    def test_landing_page(self):
        page = self.client.get("/")
        self.assertEquals(page.status_code, 200)


    def test_sign_up_page(self):
        page = self.client.get("/signup/")
        self.assertEquals(page.status_code, 200)


    def test_summary_page(self):
        page = self.client.get("/summary/", follow=True)
        self.assertEquals(page.status_code, 200)

    def test_client_list(self):
        page=self.client.get("/clients/")
        self.assertEquals(page.status_code, 200)
        self. assertEqual(page.context["clients"][0],
            clients.objects.all()[0])


    def test_ads_list(self):
        page=self.client.get("/ads/")
        self.assertEquals(page.status_code, 200)
        self.assertEqual(page.context["ads"][0],
        ads.objects.all()[0])


    def test_add_ad(self):
        page=self.client.get("/add_advertisment/")
        self.assertEquals(page.status_code, 200)


    def test_ad_client(self):
        page=self.client.get("/add_client/")
        self.assertEquals(page.status_code, 200)


    def test_edit_ad(self):
        page=self.client.get("/edit_ad/test ad/")
        self.assertEquals(page.status_code, 200)

    
    def test_get_health(self):
        client_health.objects.create(**{
                    "client": clients.objects.first(),
                    "disk_space": [1],
                    "temperature": [2],
                    "connectivity": [3],
                    "latency": [4],
                    "playing": [5],
                    "time": [6],
                    "ram_percentages": [7],
                    "cpu_percentages": [8]})
        page = self.client.get("/client_health/test pi/")
        self.assertEqual(page.status_code, 200)



    def test_edit_client(self):
        page=self.client.get("/edit_client/test pi")
        self.assertEquals(page.status_code, 200)


class PostFormsTests(TestCase):
    def test_post_schedule(self):
        ads(**{"ad_name": "test ad",
                "description": "test ip",
                "customer": "test",
                "duration": "5",
                "source": os.path.abspath(
                	            os.path.join(
                                    "test_files", "video.mp4"))
                }).save()
        data={"ad": "test ad",
                "days": "['tuesday']",
                "interval_one": "0000-1800",
                "interval_two": "0000-0000",
                "interval_three": "0000-0000",
                "start": datetime.datetime.today().strftime("%Y-%m-%d"),
                "end": datetime.datetime.today().strftime("%Y-%m-%d")}

        resp = self.client.post("/add_schedule_to_ad/", data)
        self.assertTrue(resp.status_code == 302)


    def test_post_ad(self):
        data={"ad_name": "test ad",
                "description": "test ip",
                "location": "test location",
                "customer": "test",
                "duration": "5",
                "source": os.path.abspath(
                	            os.path.join("test_files", "video.mp4"))
                }

        resp =self.client.post("/add_advertisment/", data)
        self.assertTrue(resp.status_code == 302)

    def test_post_signup_and_login(self):
        user={"first_name": "test",
                "last_name": "test",
                "email": "test@gmail.com",
                "username": "test",
                "password": "test",
                "role": "admin"}
        self.client.post("/signup/", data=user)

        resp = self.client.post("/", {"username": "test",
        	                        "password": "test"}, follow=True)
        self.assertTrue(resp.redirect_chain[-1][0] == "/summary")


    def test_post_client(self):
        data={"client_name": "test pi",
                "ip": "test ip",
                "location": "test location",
                "password": "test"}

        resp = self.client.post("/add_client/", data)
        self.assertTrue(resp.status_code == 302)

    def test_post_confirm_ad(self):
        ads(**{"ad_name": "test ad",
                "description": "test ip",
                "customer": "test",
                "duration": "5",
                "source": os.path.abspath(
                	            os.path.join("test_files", "video.mp4"))
                }).save()
        self.client.post("/delete_ad/test ad/", {"confirm": "confirm"})


    def test_post_confirm_client(self):
        clients(**{"client_name": "test pi",
                "ip": "test ip",
                "location": "test location",
                "password": "test"}).save()
        self.client.post("/delete_client/test pi/", {"confirm": "confirm"})



class ClientCommsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ClientCommsTests, cls).setUpClass()
        cls.client=Client()
        a=ads(ad_name="test ad",
            description="something",
            customer="someone",
            duration=10,
            source=os.path.join(
                            "test_data", "video.mp4"),
            thumbnail="")
        a.save()
        c=clients(client_name="test pi",
                password="123",
                ip="123123",
                location="somewhere")
        c.save()
    
    def setUp(self):
        self.c=clients.objects.get(client_name="test pi")
        self.ad=ads.objects.get(ad_name="test ad")


    def test_push_initial(self):
        self.c.client_ads.add(self.ad)
        self.c.save()

        resp=self.client.get("/push_initial/test pi/")
        self.assertTrue("test ad" in json.loads(resp.content),
        		    )


    def test_push_updates(self):
        self.c.client_ads.add(self.ad)
        self.c.save()
        observer.add_ad_to_client("test ad", "test pi")

        resp=self.client.get("/push_updates/test pi/")
        print resp.content
        self.assertTrue("test ad" in json.loads(resp.content)["CREATE"])

    def test_pull_data(self):
        health_data={"disk_space": [1],
                    "temperature": [2],
                    "connectivity": [3],
                    "latency": [4],
                    "playing": [5],
                    "time": [6],
                    "ram_percentages": [7],
                    "cpu_percentages": [8]}

        self.client.post("/pull_data/test pi/",
        	                 json.dumps(json.dumps(health_data)),
        	                 content_type="application/json")

        health_obj=client_health.objects.get(
            client="test pi")
        self.assertTrue(isinstance(health_obj, client_health))

class UtilityTests(TestCase):
    def test_create_thumbnail(self):
        create_thumbnail(os.path.join("clientManager","test_data","video.mp4"))
        dest = os.path.join("clientManager","static",
                                        "clientManager", "thumbs", "video.png")
        self.assertTrue(os.path.isfile(dest))
        os.remove(dest)
