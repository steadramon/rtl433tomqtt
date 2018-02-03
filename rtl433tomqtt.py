import paho.mqtt.client as mqtt
from subprocess import Popen, PIPE
import json

with open('config.json') as json_data_file:
  conf = json.load(json_data_file)

client = mqtt.Client(conf['mqtt_id'])

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

def read_line(line):
  try:
    json_object = json.loads(line)
    topic = is_wanted(json_object)
    if topic != False:
      print line
      client.publish(topic , line)#publish
    else:
      print "not wanted? " + line
  except ValueError, e:
    print "Failed to jsonify: " + line

if __name__ == "__main__":
  last = ''

  print "Starting"
  client.connect(conf['mqtt_host'])

  try:
    client.loop_start()
    for line in run(cmd):
      if last == line:
        continue
      last = line
      read_line(line)
  except:
    print "BORK"
