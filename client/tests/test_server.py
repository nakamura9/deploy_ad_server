import cherrypy
import json

class TestServer():
    test_ad = {
               "name": "test_ad",
               "filename": "video.mp4",
               "duration": {"start": "12/12/17",
                            "end": "12/12/17",
                            "days": "['monday']",
                            "interval_one": "0000-1000",
                            "interval_two": "0000-0000",
                            "interval_three": "0000-0000",
                            },
               "link": "media" 
            }
    @cherrypy.expose
    def ads(self):
        return "Ok"

    @cherrypy.expose
    def pull_data(self, data):
        print data
        

    @cherrypy.expose
    def media(self, video):
        return cherrypy.lib.static.serve_file("video.mp4")


    @cherrypy.expose
    def push_initial(self, id):
        return json.dumps(
            {"test ad": json.dumps(self.test_ad)})

    @cherrypy.expose
    def push_updates(self, id):
        return json.dumps({
            "CREATE": {"test ad": self.test_ad},
            "DELETE": ["test ad 2"]
        })
def run():
    conf = {"global": {
                    "server.socket_port": 8000,
                    "server.socket_host":"localhost"
                }
        }

    cherrypy.quickstart(TestServer(), "/", conf)

def stop():
    cherrypy.engine.exit()