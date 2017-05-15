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
    def __init__(self, host="localhost", port="8080", id=""):
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
        self.count = 0

    def start_player(self):
        """Starts an instance of the video player"""
        # if no ads try and start the player 5 minutes later
        print "starting player"
        if self.ads == {}:
            self.get_initial_ads()
            log_event("The player currently has no ads. \
            Attempting to get initial ads")
            return

        if not self.player:
            self.player = VLC()
            self.player.create_player()
            log_event("Instance of vlc_player started")

        self.sync_playlist()

        self.player.play()
        log_event("player running...")

    def ad_expired(self, ad):
        today = datetime.date.today()

        ad = self.ads[ad]
        end_date = datetime.datetime.strptime(
            ad["duration"]["end"], "%Y-%m-%d").date()

        if today > end_date:
            return True
        return False

    def ad_is_current(self, ad):
        today = datetime.date.today()
        ad = self.ads[ad]
        start_date = datetime.datetime.strptime(
            ad["duration"]["start"], "%Y-%m-%d").date()

        if self.weekdays[today.weekday()] not in ad["duration"]["days"]:
            return False

        def in_interval(interval):
            start, end = tuple(interval.split("-"))
            start_time = datetime.datetime.strptime(start, "%H%M").time()
            end_time = datetime.datetime.strptime(end, "%H%M").time()
            now = datetime.datetime.now().time()
            if now >= start_time and now < end_time:
                return True
            else:
                return False

        if today >= start_date:
            if in_interval(ad["duration"]["interval_one"]) or in_interval(ad["duration"]["interval_two"]) or in_interval(ad["duration"]["interval_three"]):
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

    def get_cpu_temperature(self):
        process = subprocess.Popen(['vcgencmd', 'measure_temp'],
                                   stdout=subprocess.PIPE)
        output, _error = process.communicate()
        return float(output[output.index('=') +
                            1:output.rindex("'")])

    def get_disk_space(self):
        if platform.platform().lower().startswith("windows"):
            return 99
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
        parameters = "-n 1"\
                     if platform.system().lower() == "windows" \
                     else "-c 1"

        if self.server_host == "localhost":
            output = subprocess.call(["ping",
                                      "localhost", "-n 1"], stdout=subprocess.PIPE)
            return output == 0
        else:
            output = subprocess.call(["ping",
                                      parameters, "http://%s:%s/ads" %
                                      (self.server_host, self.server_port)],
                                     stdout=subprocess.PIPE)
            return output == 0

    def query_health(self):
        """Functionality that interrogates the device hardware
        for the current state of the pi
        checks if the player is running"""

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
        self.health["playing"].append(None)
        self.health["disk_space"].append(
            self.get_disk_usage())

        log_event("querying health...")

    def upload_health_status(self):
        """Creates a json file regarding status of the client
        in the last 10 minutes """
        log_event("uploading health data...")

        try:
            response = requests.post("http://{}:{}/pull_data/{}".format(self.server_host, self.server_port,
                                                                        self.id),
                                     json=json.dumps(self.health)
                                     )
            if response.status_code == 200:
                log_event("Upload successful")

        except:
            log_event("the data upload failed, connection lost")
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

    def delete_currently_playing_ad(self, path):
        log_event("ad %s is currently playing")
        if not os.path.exists(path):
            log_event("delete was called on a non-exisiting file", "w")
            return

        self.player.stop()
        time.sleep(2)
        try:
            os.remove(path)
        except Exception as e:
            log_event("failed to delete %s because of %s" %
                      (path, e))

        finally:
            self.start_player()

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

        if self.ads != {}:
            # shouldn't get initial data if ads are already present
            log_event(
                "get initial should not have been called, ads are present on the client", "e")
            self.get_updates()
            return

        try:
            response = requests.get("http://{}:{}/push_initial/{}".format(self.server_host,
                                                                          self.server_port,
                                                                          self.id))
            if response.status_code != 200:
                log_event("the response failed with status code %d" %
                          response.status_code, "e")

            server_data = response.json()

        except ValueError:
            log_event("no json data sent from server, going to sleep ....", "e")
            time.sleep(300)
            log_event("trying again to get initial data")
            self.get_initial_ads()

        except Exception as e:
            log_event("Failed to request any data from the server", "e")
            return

        for ad in server_data:
            ad_data = json.loads(server_data[ad])
            if not ad in self.ads and ad_data["duration"] != {}:
                self.ads[ad] = ad_data
                self.ads[ad]["path"] = self.download_file(
                    self.ads[ad]["link"])
        self.start_player()

    def get_updates(self):
        """makes a request to the server for the updates 
        for this client"""
        if self.ads == {}:
            # when no ads are present, first get initial ads
            self.get_initial_ads()
            return

        try:
            response = requests.get("http://{}:{}/push_updates/{}".format(self.server_host,
                                                                          self.server_port, self.id))
            if response.status_code != 200:
                log_event("request failed with status code %d" %
                          response.status_code)
            server_data = response.json()
        except ValueError:
            log_event("No updates")
            return
        except Exception:
            log_event("failed to connect to server", "e")
            return

        self.delete_ads(server_data["DELETE"])

        create = server_data["CREATE"]

        for ad in create:
            if not create[ad]["name"] in self.ads:
                self.retries = 0
                self.ads[ad] = create[ad]
                self.ads[ad]["path"] = self.download_file(
                    create[ad]["link"])

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

        return local_path

    def periodic_method(self):  # dont like the name
        """call this function every 5 minutes to check whether the a request must be made to the server and if so, of what nature.Uses the count variable to determine what will be done during this call.
        > Every 5 minutes the health of the device and connectivity are 
        tested. 
        > Every hour updates are requested from the server
        > Every 10 minutes updates concerning the health of the client are 
        updated to the server."""

        self.query_health()
        self.start_player()

        if self.count % 6 == 0:
            self.upload_health_status()

        if self.count % 12 == 0:
            self.get_updates()
            self.count = 0

        self.count += 1


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        raise Exception("""there are not enough parameters to start the application
        The arguments that must be provided when starting the application are:
        1.Name of client registered with server(replace spaces with % character)
        2.IP address of server
        3.Port on server
        NB. 2 and 3 are optional""")

    id = sys.argv[1].replace("%", " ")

    host = sys.argv[2]
    port = sys.argv[3]

    client = Client(id=id,
                    host=host,
                    port=port)

    client.get_initial_ads()

    # named mcGrath after glen McGrath, cricketer nicknamed metronome
    mcGrath = sched.scheduler(time.time, time.sleep)

    def metronome(sc):
        client.periodic_method()
        sc.enter(300, 1, metronome, (sc, ))

    mcGrath.enter(300, 1, metronome, (mcGrath, ))
    mcGrath.run()
