#!/usr/bin/env python
# Author: Wylie Hobbs - 01/15/2018

import requests
import sys
import json
import socket
import time

# Set your carbon server's IP/port 
debug = True
carbon_server = "10.1.10.6"
carbon_port = 2003
miner_name = 'xmr-stak-worker'

#Fill in your real miner IP and port
def main():
  xmr_miner_ip = "YOUR MINER IP"
  xmr_miner_port = "PORT YOU EXPOSED HTTP ON IN config.txt"
  xmr_stak_url = "http://%s:%s/api.json" % (xmr_miner_ip, xmr_miner_port)
  raw_content = get_json(xmr_stak_url)
  json_data = json.loads(raw_content)

  pool = json_data['connection']['pool'].split(':')[0].replace('.','_')
  for metric_key, metrics in json_data.iteritems():
    if metric_key == 'connection':
      wanted = ['ping', 'uptime']
      for metric_name, value in metrics.iteritems():
	if metric_name in wanted:
	  metric_path = '%s.%s.%s' % (pool, metric_key, metric_name)
          send_graphite(metric_path, value)
    elif metric_key == 'hashrate':
      wanted = ['highest', 'threads', 'total']
      for metric_name, value in metrics.iteritems():
        metric_path = '%s.%s.%s' % (pool, metric_key, metric_name)
	if metric_name in wanted:
	  if metric_name == 'threads':
	    for index, thread in enumerate(value):
              _metric_path = '%s.%s' % (metric_path, index)
	      hashrates = { 'ten_second': thread[0], 'sixty_second': thread[1], 'fifteen_minute': thread[2] }
	      hashrate_send(hashrates, _metric_path)
          elif metric_name == 'total':
	    hashrates = { 'ten_second': value[0], 'sixty_second': value[1], 'fifteen_minute': value[2] }
	    hashrate_send(hashrates, metric_path)
	  elif metric_name == 'highest':
	    _metric_path = '%s.%s' % (metric_path, metric_name)
	    send_graphite(_metric_path, value)
    elif metric_key == 'results':
      wanted = ['avg_time', 'diff_current', 'hashes_total', 'shares_good', 'shares_total']
      for metric_name, value in metrics.iteritems():
        if metric_name in wanted:
	  metric_path = '%s.%s.%s' % (pool, metric_key, metric_name)
          send_graphite(metric_path, value)

def hashrate_send(hashrates, metric_key):
  for metric_name, value in hashrates.iteritems():
    metric_path = '%s.%s' % (metric_key, metric_name)
    send_graphite(metric_path, value)

def get_json(url):
  req = requests.get(url)
  if req.status_code == 200:
    return req.text
  else:
    print "Error requesting %s - response was %s" % (url, req)
    sys.exit(1)

def send_graphite(metric, metric_value):
  metric_root = 'servers.%s.xmr_stak' % miner_name
  timestamp = int(time.time())
  message = "%s.%s %s %d\n" % (metric_root, metric, metric_value, timestamp)
  if debug:
    print message
  sock = socket.socket()
  sock.connect((carbon_server, carbon_port))
  sock.sendall(message)
  sock.close()

main()
