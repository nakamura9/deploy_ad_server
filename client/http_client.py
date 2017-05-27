# -*- coding: utf-8 -*-

from vlc_player.myvlc import VLC, FileNotFoundException
import requests
import time
import datetime
import sched
import json
import os
import platform
import shutil
import subprocess
import psutil
import logging

"""The client is responsible for playing the ads as a video loop 
continuously. It will request updates from the server every hour for new ads.
It will provide the server with information about its health every 10 minutes 
The method of communication will be http. The client requests an authentication page
where the verification with the  server occurs. After the handshake it is redirected
to the update center which checks if updates are needed. If so, the updates will be 
sent to the client by the server as json. The json structure will be as follows:
    {"delete": ["list of ads to be deleted by name"];
        "download": {"name" :{"name": "",
                    "link": "",
                    "duration": "{"start" : date, }"
                    },
                    } #nested data structure 
        }
if the data has been properly processed the client posts a response that indicates 
the sucess of the process.

With regards to vlc, once ads are downloaded, they are copied to a folder where the vlc instance
is deriving its playlist and adds the ad to the queue. finer controls will be added later.
"""

logging.basicConfig(filename="log.log", level=logging.INFO)


def log_event(msg, level="i"):
    timestamp = "%s " % datetime.datetime.now()
    if level.lower() == "w":
        logging.warn(timestamp + msg)
    elif level.lower() == "e":
        logging.error(timestamp + msg)
    else:
        logging.info(timestamp + msg)
    print msg


class Client(object):
    def __init__(self, host="localhost", port="8000", id=""):
        self.ads = {}
        self.player = None
        self.retries = 0
        self.server_host = host
        self.server_port = port
        self.id = id
        if not os.path.exists("Advertisments"):
            os.mkdir("Advertisments")

        self.ad_folder = os.path.join(os.getcwd(), "Advertisments")
        self.weekdays = {6: "sunday", 0: "monday", 1: "tuesday",
                         2: "wednesday", 3: "thursday", 4: "friday", 5: "saturday"}

        self.health = {
            "disk_space": [],
            "temperature": [],
            "connectivity": [],
            "latency": [],
            "playing": [],
            "time": [],
            "ram_percentages": [],
            "cpu_percentages": []
        }

    @property
    def now(self):
        return datetime.datetime.now().strftime("%H:%M")

    @property
    def is_connected(self):
        return self.ping_server()

    def start_player(self):
        """Starts an instance of the video player"""
        if not self.player:
            self.player = VLC()
            while not self.player.connection_open:
                self.player.create_player()
                time.sleep(2)
            log_event("Instance of vlc_player started")
            if self.player.connection_open:
                return 0
            else: return -1

    def ad_expired(self, ad):
        """Returns true if an ad has expired and must be removed"""
        today = datetime.date.today()

        ad = self.ads[ad]
        end_date = datetime.datetime.strptime(
            ad["duration"]["end"], "%Y-%m-%d").date()

        if today > end_date:
            return True
        return False

    def ad_is_current(self, ad):
        """Checks if an advertisment is meant to be 
        in the current playlist"""
        today = datetime.date.today()
        ad = self.ads[ad]
        start_date = datetime.datetime.strptime(
            ad["duration"]["start"], "%Y-%m-%d").date()

        if self.weekdays[today.weekday()] not in ad["duration"]["days"]:
            return False

        def in_interval(interval):
            """checks if a time is between certain intervals"""
            start, end = tuple(interval.split("-"))
            start_time = datetime.datetime.strptime(start, "%H%M").time()
            end_time = datetime.datetime.strptime(end, "%H%M").time()
            now = datetime.datetime.now().time()
            if now >= start_time and now < end_time:
                return True
            else:
                return False

        if today >= start_date:
            if in_interval(ad["duration"]["interval_one"]) or \
             in_interval(ad["duration"]["interval_two"]) or \
             in_interval(ad["duration"]["interval_three"]):
                return True
            else:
                return False
        else:
            return False

    def sync_playlist(self):
        """matches the local playlist variable with the list of 
        paths stored in the vlc player"""
        new_list = []
        bad_list = []
        for ad in self.ads:
            if self.ad_expired(ad):
                self.ads.pop(ad)
            else:
                if self.ad_is_current(ad):
                    try:
                        self.player.check_path(self.ads[ad]["path"])
                    except FileNotFoundException:
                        bad_list.append(ad)
                    else:
                        new_list.append(self.ads[ad]["path"])

        for ad in bad_list:
            self.ads.pop(ad)

        if self.player.connection_open:
            if self.player.playlist != new_list:
                del self.player.playlist
                self.player.playlist = new_list
        return 0

    def get_cpu_temperature(self):
        if platform.system().lower().startswith("windows"):
            return -1
        process = subprocess.Popen(['vcgencmd','measure_temp'], stdout=subprocess.PIPE)
        output, _error = process.communicate()
        return float(output[output.index('=') +
                            1:output.rindex("'")])

    def get_disk_space(self):
        if platform.system().lower().startswith("windows"):
            return -1
        stats = os.statvfs(__file__)
        return stats.f_bavail * stats.f_frsize

    def get_disk_usage(self):
        return psutil.disk_usage(os.getcwd())[3]

    def get_latency(self):
        # Not implemented, yet
        return 0.035

    def cpu_usage(self):
        return psutil.cpu_percent()

    def get_ram_usage(self):
        return psutil.virtual_memory()[2]

    def ping_server(self):
        parameters = ["-n", "1"]\
                     if platform.system().lower() == "windows" \
                     else ["-c", "1"]

        if self.server_host == "localhost":
            output = subprocess.call(["ping",
                                      "localhost", "-n", "1"], stdout=subprocess.PIPE)
            return output == 0
        else:
            output = subprocess.call(
                        ["ping", "http://%s:%s/ads" %
                    (self.server_host,self.server_port)] +
                    parameters,
                                     stdout=subprocess.PIPE)
            return output == 0

    def query_health(self):
        """Functionality that interrogates the device hardware
        for the current state of the pi
        checks if the player is running"""
        log_event("querying health...")
        try:
            self.health["time"].append(self.now)
            self.health["connectivity"].append(
                self.ping_server())
            self.health["temperature"].append(
                self.get_cpu_temperature())
            self.health["cpu_percentages"].append(
                self.cpu_usage())
            self.health["ram_percentages"].append(
                self.get_ram_usage())
            self.health["latency"].append(
                self.get_latency())
            self.health["playing"].append(
                self.player.current)
            self.health["disk_space"].append(
                self.get_disk_usage())
        except Exception as e:
            print e
            return -1
        else:
            return 0


    def upload_health_status(self):
        """Creates a json file regarding status of the client
        in the last 10 minutes """
        log_event("uploading health data...")
        code = None
        try:
            response = requests.post("http://{}:{}/pull_data/{}".format(
                                self.server_host, self.server_port,self.id),
                                json=json.dumps(self.health))
            if response.status_code == 200:
                log_event("Upload successful")
                code = 200
        except Exception as e :
            log_event("the data upload failed because of %s " % e)
        finally:
            self.health = {
                "disk_space": [],
                "temperature": [],
                "connectivity": [],
                "latency": [],
                "playing": [],
                "time": [],
                "ram_percentages": [],
                "cpu_percentages": []
            }
            if code is not None:
                return 0
            else:
                return -1

    def delete_currently_playing_ad(self, path):
        log_event("ad %s is currently playing")
        self.player.stop()
        time.sleep(2)
        try:
            os.remove(path)
        except Exception as e:
            log_event("failed to delete %s because of %s" %
                      (path, e))

        finally:
            self.start_player()
            self.player.play()

    def delete_ads(self, ad_list):
        """takes a list of ads and removes them from the playlist
         and the file system"""

        for ad in ad_list:
            if ad in self.ads:
                path = self.ads[ad]["path"]
                try:
                    os.remove(path)
                    del self.ads[ad]
                    self.sync_playlist()
                except:
                    self.delete_currently_playing_ad(path)

    def get_initial_ads(self):
        log_event("getting initial data...")
        try:
            response = requests.get("http://{}:{}/push_initial/{}".format(
                                self.server_host,self.server_port,self.id))
            if response.status_code != 200:
                log_event("the request failed with status code %d" %
                          response.status_code, "e")

            server_data = response.json()

        except ValueError:
            log_event("no json data sent from server, going to sleep ....", "e")
            return 1
        except Exception as e:
            log_event("Failed to request any data from the server", "e")
            return -1

        for ad in server_data:
            ad_data = json.loads(server_data[ad])
            if not ad in self.ads and ad_data["duration"] != {}:
                self.ads[ad] = ad_data
                path = self.download_file(self.ads[ad]["link"])
                if path == -1:
                    del self.ads[ad]
                else:    
                    self.ads[ad]["path"] = path 
        return 0

    def get_updates(self):
        """makes a request to the server for the updates 
        for this client"""
        try:
            response = requests.get("http://{}:{}/push_updates/{}".format(
                                    self.server_host,self.server_port, self.id))
            if response.status_code != 200:
                log_event("Request failed with status code %d" %
                          response.status_code)
            server_data = response.json()
        except ValueError:
            log_event("No updates")
            return 1
        except Exception:
            log_event("failed to connect to server", "e")
            return -1
        else:
            print server_data
            self.delete_ads(server_data["DELETE"])

            create = server_data["CREATE"]

            for ad in create:
                data = json.loads(create[ad])
                if not data["name"] in self.ads:
                    self.retries = 0
                    self.ads[ad] = data
                    self.ads[ad]["path"] =  self.download_file(
                    data["link"])
        return 0

    def download_file(self, link):
        '''takes the link provided with each ad and builds up a 
        url from which the file will be downloaded to the advertisments 
        folder. retries a maximum number of 5 times before giving up'''
        local_filename = link.split("/")[-1]
        local_path = os.path.join(self.ad_folder, local_filename)
        if not os.path.isdir(self.ad_folder):
            os.mkdir(self.ad_folder)

        net_link = "http://%s:%s" % (self.server_host, self.server_port) + link
        try:
            r = requests.get(net_link, stream=True)
            with open(local_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        except:
            self.retries += 1
            if self.retries < 5:
                self.download_file(link)
            else:
                log_event("Download failed after 5 retries")
                self.retries = 0
                return - 1
        else:
            self.retries = 0
            return local_path

    def run(self, loop_interval):
        self.count = 0
        while True:
            if not self.player:
                self.start_player()
            self.query_health()
            if not self.is_connected:
                log_event("Connectivity with the server lost", "e")
                time.sleep(10)
                self.run(loop_interval)

            if self.ads == {}:
                self.get_initial_ads()
                self.sync_playlist()
            
            if self.player.player_status != "playing":
                print "playing"
                self.player.play()

            if self.count % 6 == 0:
                self.upload_health_status()
            if self.count >= 12:
                ret_value=self.get_updates()
                if ret_value == 0:
                    self.sync_playlist()
                self.count = 0

            self.count += 1
            time.sleep(loop_interval)

    def stop(self):
        raise Exception("Client stopped manually")
if __name__ == "__main__":
    if not os.path.exists("config.json"):
        raise Exception("""
        No config file found. Please create a config.json file and populate it as follows:\n
        {'name': <name on server>,
        'host': <ip>,
        'port':<port>,
        'loop interval': '<seconds>'}
        NB: for the name variable replace spaces with the '%' character
        """)

    config_file = open("config.json", "r")
    config=json.load(config_file)

    id = config["name"].replace("%", " ")
    client = Client(id=id,host=config["host"],port=config["port"])
    client.run(int(config["loop interval"]))