from django.test import TestCase
from unittest import skip
from django.test import Client
from .models import ads, clients, ad_schedule
from .observer import observer, convert_ad_to_json
import time, datetime
import json

class ClientsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.c = clients(client_name= "test pi",
                    password="123",
                    ip="123123",
                    location= "somewhere")
        cls.c.save()

        cls.a = ads(ad_name="test ad",
                description="something",
                customer="someone",
                duration=10,
                source="C:\Users\nakamura9a\Documents\code\git\States_project\server\DjangoApp\dashboard\clientManager\media\LocalAdStorage\flash.mp4",
                thumbnail="")

        cls.a.save()
    
    def test_client_page(self):
        page = self.client.get("/clients/")

        self.assertQuerysetEqual(page.context["clients"], clients.objects.all())

    def test_client_form(self):
        data = {"client_name": "test pi 2",
                    "password" :"123",
                    "ip":"123123",
                    "location": "somewhere"}
        self.client.post("/add_client/", data=data)
        page = self.client.get("/clients/")
        self.assertQuerysetEqual(page.context["clients"].all(), [repr(i) for i in clients.objects.all()])


    """
    def test_modify_client(self):
        data = {"client_name": "test pi",
                    "password" :"555",
                    "ip":"123123",
                    "location": "somewhere",
                    "client_ads": ads.objects.first()}

        page = self.client.post("/edit_client/test pi", data=data)

        c = clients.objects.get(client_name = "test pi")
        self.assertEquals(c.client_ads.first(), ads.objects.get(ad_name="test ad"))


    def test_remove_client_ads(self):
        data = {"client_name": "test pi",
                    "password" :"555",
                    "ip":"123123",
                    "location": "somewhere",
                    "client_ads": []}

        page = self.client.post("/edit_client/test pi", data=data)

        self.assertEquals(self.c.client_ads.all(), [] )
    """
    @classmethod
    def tearDownClass(cls):
        pass


class ObserverTests(TestCase):
    @classmethod
    def setUpTestData(self):
        a = ads.objects.create(ad_name="test ad",
                description="something",
                customer="someone",
                duration=10,
                source="C:\Users\nakamura9a\Documents\code\git\States_project\server\DjangoApp\dashboard\clientManager\media\LocalAdStorage\flash.mp4",
                thumbnail="")


        b = clients.objects.create(client_name= "test pi",
                    password="123",
                    ip="123123",
                    location= "somewhere")

    def setUp(self):
        self.client = clients.objects.get(client_name="test pi")
        self.old = []
        self.ad = ads.objects.get(ad_name="test ad")
    
    def test_convert_ad_to_json(self):
        ad_schedule.objects.create(ad_id="test ad",
                                start=datetime.datetime.now(),
                                end=datetime.datetime.now(),
                                days = "[tuesday]",
                                interval_one = "0000-1000",
                                interval_two = "1200-1400",
                                interval_three = "0000-1000",
                                    )
        data = convert_ad_to_json("test ad")
        print data
        duration = json.loads(data)["duration"]
        
        self.assertNotEqual(duration, {})


    def test_set_up_sucess(self):
        self.assertEquals(self.ad.ad_name, "test ad")

    def test_client_ads_changed(self):
        """tests add ad to client as well"""
        self.client.client_ads.add(self.ad)

        observer.client_ads_changed("test pi", self.old)
        self.assertNotEquals(observer.updated_clients, {})

    def test_ad_clients_changed(self):
        self.ad.ad_clients.add(self.client)

        ret_value = observer.ad_clients_changed("test ad", self.old)
        self.assertNotEquals(observer.updated_clients, {})
        self.assertTrue(ret_value)

    def test_no_changes(self):
        self.assertFalse(observer.ad_clients_changed("test ad", []))

    def test_delete_ad(self):
        """also tests remove ad from client"""
        self.client.client_ads.add(self.ad)
        observer.delete_ad("test ad")
        self.assertEquals(observer.updated_clients["test pi"]["DELETE"], ["test ad"])
        self.assertEquals(observer.updated_clients["test pi"]["CREATE"], {})

    def test_update_client(self):
        """not worth the test"""
        pass
        
class AdsTests(TestCase):
    pass

class UrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = Client()

        a = ads(ad_name="test ad",
                description="something",
                customer="someone",
                duration=10,
                source="C:\Users\nakamura9a\Documents\code\git\States_project\server\DjangoApp\dashboard\clientManager\media\LocalAdStorage\flash.mp4",
                thumbnail="")

        a.save()

        c = clients(client_name= "test pi",
                    password="123",
                    ip="123123",
                    location= "somewhere")

        c.save()

    def test_landing_page(self):
        page = self.client.get("/")

        self.assertEquals(page.status_code, 200)

    def test_sign_up_page(self):
        page = self.client.get("/signup/")

        self.assertEquals(page.status_code, 200)

    def test_summary_page(self):
        page = self.client.get("/summary/")

        self.assertEquals(page.status_code, 200)

    def test_clients_list(self):
        page = self.client.get("/clients/")

        self.assertEquals(page.status_code, 200)

    def test_ads_list(self):
        page = self.client.get("/ads/")

        self.assertEquals(page.status_code, 200)

    def test_add_ad(self):
        page = self.client.get("/add_advertisment/")

        self.assertEquals(page.status_code, 200)

    def test_ad_client(self):
        page = self.client.get("/add_client/")

        self.assertEquals(page.status_code, 200)

    def test_edit_ad(self):
        page = self.client.get("/edit_ad/test ad/")

        self.assertEquals(page.status_code, 200)

    def test_edit_client(self):
        page = self.client.get("/edit_client/test pi")

        self.assertEquals(page.status_code, 200)

    #Does not return a page more suitable for the other test cases
    

    @classmethod
    def tearDownClass(cls):
        clients.objects.get(client_name="test pi").delete()
        ads.objects.get(ad_name="test ad").delete()


class ClientServerCommsTests(TestCase):
    pass    
