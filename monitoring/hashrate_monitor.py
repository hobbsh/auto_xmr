#!/usr/bin/env python
# Copyright Wylie Hobbs - 2018
#
# This script will SSH into your Windows 10 installation and restart xmr-stak 
# if the hashrate drops below a certain threshold
#
# Requires SSH key auth to be setup and working in addition to a working clone of this repo


import os
import logging
import logging.handlers
import requests
import subprocess
import sys
import json
import time

#Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

#When the total hashrate drops this amount, restart xmr-stak
hash_threshold = 10000

#Set restart threshold (in seconds) to  prevent restarting too frequently
start_time = int(time.time())
restart_threshold = 3600

#The private IP of your xmr-stak host and xmr-stak http port
xmr_stak_ip = "10.1.10.189"
xmr_stak_port = "8080"
powershell = r'C:\WINDOWS\system32\WindowsPowerShell\v1.0\Powershell.exe'
autoxmr_path = r'C:\auto_monero'

#Do some pidfile stuff to prevent overlapping runs
pidfile = "/tmp/hashrate_monitor.pid"
set_pidfile()

def main():
  last_run_time = get_last_run()
  timediff = start_time - last_run_time

  current_hashrate = get_api(path=('hashrate', 'total'))
  uptime = get_api(path=('connection', 'uptime'))

  if not current_hashrate:
    if timediff < restart_threshold and uptime:
      logger.info("xmr-stak hashrate dropped but we are restarting too frequently - timediff is only %s seconds" % timediff)
      os.unlink(pidfile)
      sys.exit(0)
    else:
      logger.info("xmr-stak is not running - starting mining")
      start_mining()

  elif current_hashrate < hash_threshold:
    logger.info("Current hashrate is %d - restarting xmr-stak" % current_hashrate)
    xmr_proc = get_process('xmr-stak')
    if xmr_proc:
      logger.info("Killing xmr-stak")
      if stop_process(xmr_proc):
        start_mining()
  else:
    logger.info("Current hashrate is %d - all good" % current_hashrate)
    os.unlink(pidfile)
    sys.exit(1)

def stop_process(proc_id):
  command = "Stop-Process %s -PassThru" % proc_id
  kill = run_remote_cmd(command, powershell)
  if get_process(proc_id):
    time.sleep(3) 
  else:
    return True

def get_process(process):
  command = "Get-Process %s" % process
  proc = run_remote_cmd(command, powershell)
  if proc:
    proc_id = parse_procline(proc, 5)
    logger.info("%s has a process ID of %s" % (process, proc_id))
    return proc_id
  else:
    logger.info("Process %s could not be found!" % proc )
    return None

def parse_procline(raw, retval):
  #retval index = 0: NPM, 1: PM, 2: WS, 3: VM, 4: CPU, 5: ID, 6: Machinename, 7: processname
  procline = raw.split('\r\n')[3]
  if debug:
    print procline
  proc_val = procline.split()[retval]
  return proc_val

def start_mining():
  "https://decoder.cloud/2017/02/03/bypassing-uac-from-a-remote-powershell-and-escalting-to-system/"
  mine = r"%s\mine.ps1" % autoxmr_path
  command = " -File %s -WindowStyle Normal" % mine

  logger.info("Starting xmr-stak, then waiting 120s")
  run_remote_cmd(command, powershell)

  while not get_api(path=('hashrate', 'total')):
    time.sleep(5)

  if get_process('xmr-stak'):
    logger.info("xmr-stak started successfully")
    kill_ssh()
    os.unlink(pidfile)
    write_last_run()
    sys.exit(0)
  else:
    logger.info("Something didn't go right when starting xmr-stak, exiting")
    sys.exit(1)

def kill_ssh():
  logger.info("Killing outstanding SSH processes")
  os.system("kill `ps aux | grep 'mine.ps1' | grep -v grep | awk '{print $2}'`")

def set_pidfile():
  pid = str(os.getpid())

  if os.path.isfile(pidfile):
    logger.info( "%s already exists, exiting" % pidfile )
    sys.exit()

  file(pidfile, 'w').write(pid)

def get_last_run():
  try:
    with open('/tmp/hashrate_monitor_lastrun') as f: 
      t = f.read()
  except IOError:
    write_last_run()
    t = get_last_run()

  return int(t)

def write_last_run():
  now = str(int(time.time()))
  with open('/tmp/hashrate_monitor_lastrun', 'w') as f:
    f.write(now)

  f.close()

def get_api(path=('a', 'b')):
  url = "http://%s:%s/api.json" % (xmr_stak_ip, xmr_stak_port)

  try:
    req = requests.get(url)
  except requests.ConnectionError, e:
    logger.info("xmr-stak web API not responsive, assuming xmr-stak is not running")
    return None

  if req.status_code == 200:
    data = json.loads(req.text)
    retval = reduce(dict.get, path, data)
    if 'hashrate' in path:
      return int(retval[0])
    else:
      return  retval
  else:
    logger.info("Something bad happened requesting a response from %s" % url)
    return None

def run_remote_cmd(cmd_args, cmd_path = ""):
  HOST = xmr_stak_ip
  if cmd_path:
    COMMAND = "%s %s" % (cmd_path, cmd_args)
  else:
    COMMAND = cmd_args

  ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

  #Bypass process communcation for the mine.ps1 case
  if "mine.ps1" in cmd_args:
    return "Success"
  
  result = ssh.stdout.read()
  print result

  if result == []:
    error = ssh.stderr.readlines()
    print >>sys.stderr, "ERROR: %s" % error
  else:
    return result


if __name__ == "__main__":
  main()

