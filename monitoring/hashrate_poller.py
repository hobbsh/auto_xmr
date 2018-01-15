#!/usr/bin/env python
# Author: Wylie Hobbs - 01/15/2018

import requests
import sys
import json
import socket
import time
from bs4 import BeautifulSoup

# Set your carbon server's IP/port 
debug = False
carbon_server = "10.1.10.6"
carbon_port = 2003

#Fill in your real miner IP and port
def main():
  xmr_miner_ip = "YOUR MINER IP"
  xmr_miner_port = "PORT YOU EXPOSED HTTP ON IN config.txt"
  xmr_stak_url = "http://%s:%s/h" % (xmr_miner_ip, xmr_miner_port)
  raw_content = get_raw_page(xmr_stak_url)
  hashrate_report =  parse_content(raw_content)

  for thread_id, metrics in hashrate_report['threads'].iteritems():
    for metric, value in metrics.iteritems():
      metric_path = 'threads.%s.%s' % (thread_id, metric)
      send_graphite(metric_path, value)
      
  for metric, value in hashrate_report['totals'].iteritems():
    send_graphite(metric, value)

  if debug:
    print json.dumps(hashrate_report, sort_keys=True, indent=4)

def parse_content(raw_content):
  soup = BeautifulSoup(raw_content, 'html.parser')
  hashrate_report = {}
  hashrate_report['threads'] = {}
  hashrate_report['totals'] = {}
  for row in soup.find_all('tr')[1:]:
    data = row.text.encode('utf-8').split()
    if data[0] == 'Totals:':
      hashrate_report['totals']['ten_sec_total'] = data[1]
      hashrate_report['totals']['sixty_sec_total'] = data[2]
      try:
        hashrate_report['totals']['fifteen_min_total'] = data[3]
      except:
        print "No data for fifteen minute mark yet"
    elif data[0] == 'Highest:':
      hashrate_report['totals']['highest'] = data[1]
    else:
      thread_id = data[0]
      hashrate_report['threads'][thread_id] = {}
      hashrate_report['threads'][thread_id]['ten_sec_hashrate'] = data[1]
      hashrate_report['threads'][thread_id]['sixty_sec_hashrate'] = data[2]
      try:
        hashrate_report['threads'][thread_id]['fifteen_min_hashrate'] = data[3]
      except:
        print "No data for fiften minute mark yet"
        
  return hashrate_report

def get_raw_page(url):
  req = requests.get(url)
  if req.status_code == 200:
    return req.text
  else:
    print "Error requesting %s - response was %s" % (url, req)
    sys.exit(1)

def send_graphite(metric, metric_value):
  metric_root = 'servers.electrozig.xmr_stak.hashrates'
  timestamp = int(time.time())
  message = "%s.%s %s %d\n" % (metric_root, metric, metric_value, timestamp)
  if debug:
    print message
  sock = socket.socket()
  sock.connect((carbon_server, carbon_port))
  sock.sendall(message)
  sock.close()

main()
