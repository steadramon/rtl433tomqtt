from subprocess import Popen, PIPE
import json

with open('config.json') as json_data_file:
    conf = json.load(json_data_file)

protocols = [];

if len(conf['devices']) == 0:
    print "Please define some devices in config.json"
    exit(1)

for item in conf['devices']:
    p = conf['devices'][item]['protocol']
    if p not in protocols:
        protocols.append(p)

cmd = conf['rtl_433_path']
cmd += " -F json"
cmd += " -R " + " -R " . join(str(x) for x in protocols)

def run(command):
    process = Popen(command, stdout=PIPE, shell=True)
    while True:
        line = process.stdout.readline().rstrip()
        if not line:
            break
        yield line

def is_wanted(json):
    for item in conf['devices']:
        wanted=True
        for id in conf['devices'][item]['id']:
            if id not in json:
                wanted=False
                continue
            if conf['devices'][item]['id'][id] != json[id]:
                wanted = False
                continue
        if wanted == True:
            return conf['devices'][item]['topic']
    return False

if __name__ == "__main__":
    last = ''
    for path in run(cmd):
        try:
            json_object = json.loads(path)
            if last == path:
                continue
            topic = is_wanted(json_object)
            if topic != False:
                print path
                p = Popen("echo '"+path+"' | " + conf['mosquitto_pub_path'] + " -h "+conf['mqtt_host'] + " -r -l -t " + topic, stdout=PIPE, shell=True)
                p.communicate()
            else:
                print "not wanted? " + path
            last = path
        except ValueError, e:
            print "Failed to jsonify: " + path
