import subprocess 
import os, logging
import datetime

def log_event(msg, level = "i"):
    timestamp = "%s " % datetime.datetime.now()
    if level.lower() == "w":
        logging.warn(timestamp + msg)
    elif level.lower() == "e":
        logging.error(timestamp + msg)
    else:
        logging.info(timestamp + msg)

messages = []

def add_message(message, error=False):
    global messages

    message_string = "{}: {}".format(datetime.datetime.now().strftime("[%Y/%m/%d %H:%M:%S]"), message) 
    if error:

        messages.append("<p style='text-color: red;'>" + \
                        "Error: " + message_string + "</p>")
        log_event(message_string, "e")
    else:
        messages.append(message_string)
        log_event(message_string)

def create_thumbnail(path):
    if not os.path.isfile(path):
        print path
        raise Exception("There is no such file")

    name = os.path.split(path)[1]
    name = name.split('.')[0]

    folder = os.path.abspath(os.path.join(os.getcwd(), "clientManager", "static", "clientManager","thumbs"))

    if os.path.isfile(folder+name + ".png"):
        os.remove()
    if not os.path.exists(folder):
        os.mkdir(folder)
    

    subprocess.call(['vlc', path, '--rate=1', '--video-filter=scene', '--vout=dummy', '--start-time=4', '--stop-time=5', '--scene-format=png', '--scene-ratio=60', '--scene-prefix={}'.format(name), '--scene-path={}'.format(folder), 'vlc://quit'
    ])
    old_path =os.path.join(folder, name + "00001.png") 
    new_path = os.path.join(folder, name + ".png")
    if os.path.isfile(new_path):
        os.remove(new_path)
    os.rename(old_path,  new_path)

    return "/static/clientManager/thumbs/" + name + ".png"

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise Exception("A file path must be supplied to the program")
    
    create_thumbnail(sys.argv[1])