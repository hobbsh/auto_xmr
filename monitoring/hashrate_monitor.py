#!/usr/bin/env python

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

#Since this should be run from the host xmr-stak is run on, use localhost
xmr_stak_ip = "10.1.10.189"
xmr_stak_port = "8080"
powershell = r'C:\WINDOWS\system32\WindowsPowerShell\v1.0\Powershell.exe'
debug = True

pid = str(os.getpid())
pidfile = "/tmp/hashrate_monitor.pid"

if os.path.isfile(pidfile):
  logger.info( "%s already exists, exiting" % pidfile )
  sys.exit()

file(pidfile, 'w').write(pid)

def main():
  current_hashrate = get_hashrate()

  if not current_hashrate:
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
  mine = r"C:\auto_monero\mine.ps1"
  command = " -File %s -WindowStyle Hidden" % mine

  logger.info("Starting xmr-stak, then waiting 120s")
  run_remote_cmd(command, powershell)
  time.sleep(120)

  if get_process('xmr-stak') and get_hashrate() > hash_threshold:
    logger.info("xmr-stak started successfully")
    kill_ssh()
    os.unlink(pidfile)
    sys.exit(0)
  else:
    logger.info("Something didn't go right when starting xmr-stak, exiting")
    sys.exit(1)

def kill_ssh():
  logger.info("Killing outstanding SSH processes")
  os.system("kill `ps aux | grep 'mine.ps1' | grep -v grep | awk '{print $2}'`")
  
def get_hashrate():
  url = "http://%s:%s/api.json" % (xmr_stak_ip, xmr_stak_port)
  try:
    req = requests.get(url)
  except requests.ConnectionError, e:
    logger.info("xmr-stak web API not responsive, assuming xmr-stak is not running")
    return None

  if req.status_code == 200:
    data = json.loads(req.text)
    total_hashrate = data['hashrate']['total']
    return int(total_hashrate[0])
  else:
    logger.info("Could not get a response from %s" % url)

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
  
  (output, error) = ssh.communicate()

  if not error:
    return output


if __name__ == "__main__":
  main()
