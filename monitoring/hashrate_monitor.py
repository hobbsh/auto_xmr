#!/usr/bin/env python
# Copyright Wylie Hobbs - 2018
#
# This script will SSH into your Windows 10 installation and restart xmr-stak 
# if the hashrate drops below a certain threshold
#
# Requires SSH key auth to be setup and working in addition to a working clone of this repo
#

import os
import logging
import logging.handlers
import requests
import subprocess
import sys
import json
import time

# Set global logging variable
global logger

#When the total hashrate drops this amount, restart xmr-stak
hash_threshold = 10000

#Set restart threshold (in seconds) to  prevent restarting too frequently
start_time = int(time.time())
restart_threshold = 3600

#The private IP of your xmr-stak host and xmr-stak http port
xmr_stak_ip = "10.1.10.190"
xmr_stak_port = "8080"

#Configure your powershell path (if different) and auto_xmr repo path
powershell = r'C:\WINDOWS\system32\WindowsPowerShell\v1.0\Powershell.exe'
autoxmr_path = r'C:\auto_xmr'

#Do some pidfile stuff to prevent overlapping runs
pidfile = "/tmp/hashrate_monitor.pid"

def main():
  last_run_time = get_last_run()
  timediff = start_time - last_run_time
  recent_error = get_errors()
  current_hashrate = get_api(path=('hashrate', 'total'))
  uptime = get_api(path=('connection', 'uptime'))

  if recent_error and not current_hashrate:
    logger.info("There was recently a connection error that may cause an apparent hashdrop - waiting until 3 minutes passes - %s" % recent_error['text'])
    os.unlink(pidfile)
    sys.exit(0)

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
  # Stops a running process by process ID
  command = "Stop-Process %s -PassThru" % proc_id
  kill = run_remote_cmd(command, powershell)
  if get_process(proc_id):
    time.sleep(3) 
  else:
    return True

def get_process(process):
  # Checks to see if a specific process is running and returns the process ID
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
  # Runs mine.ps1 on the remote host
  mine = r"%s\mine.ps1" % autoxmr_path
  command = " -File %s -WindowStyle Normal" % mine

  logger.info("Starting xmr-stak, then waiting waiting for it to be available")
  run_remote_cmd(command, powershell)

  # Continue to check the xmr-stak API every 5 seconds until a hashrate is returned
  while not get_api(path=('hashrate', 'total')):
    time.sleep(5)

  if get_process('xmr-stak'):
    logger.info("xmr-stak started successfully")
    cleanup('success')
  else:
    logger.info("Something didn't go right when starting xmr-stak, exiting")
    cleanup('crash')
    sys.exit(1)

def kill_ssh():
  # Kill outstanding SSH session
  logger.info("Killing outstanding SSH processes")
  os.system("kill `ps aux | grep 'mine.ps1' | grep -v grep | awk '{print $2}'`")

def set_pidfile():
  # Create a pidfile
  pid = str(os.getpid())

  if os.path.isfile(pidfile):
    logger.info( "%s already exists, exiting" % pidfile )
    sys.exit()

  file(pidfile, 'w').write(pid)

def get_errors():
  errors = get_api(path=('connection', 'error_log'))
  if errors:
    for error in errors:
      timediff = start_time - int(error['last_seen'])
      if timediff < 60:
        return error
  else:
    return None

def get_last_run():
  # Get script last run time from tempfile
  try:
    with open('/tmp/hashrate_monitor_lastrun') as f: 
      t = f.read()
  except IOError:
    write_last_run()
    t = get_last_run()

  if t:
    return int(t)
  else:
    return None

def write_last_run():
  # Write last successful run time to tempfile
  now = str(int(time.time()))
  with open('/tmp/hashrate_monitor_lastrun', 'w') as f:
    f.write(now)

  f.close()

def get_api(path=('a', 'b')):
  #Return a value from the xmr-stak API - path here is a dict path
  url = "http://%s:%s/api.json" % (xmr_stak_ip, xmr_stak_port)

  try:
    req = requests.get(url, timeout=8)
    if req.status_code == 200:
      data = json.loads(req.text)
      retval = reduce(dict.get, path, data)
      if (retval is None and 'error_log' not in path) or data['connection']['uptime'] < 10:
        logger.debug("xmr-stak API responded but no data - need to wait for xmr-stak to initialize")
        time.sleep(5)
        get_api(path=path)
      else:
        if 'hashrate' in path and retval:
          retval = int(retval[0])
        logger.debug("xmr-stak API responded for path %s with value %s - returning data" % (str(path), str(retval)))
        return retval
  except requests.exceptions.ReadTimeout:
    logger.debug("Timed out requesting xmr-stak API, will continue to try again")
    get_api(path=path)
  except requests.exceptions.ConnectionError, e:
    logger.debug("xmr-stak web API not responsive, assuming xmr-stak is not running")
    return None
  except Exception, e:
    logger.debug("Something bad happened requesting xmr-stak API - exiting\n %s" % str(e))
    cleanup('crash')

def cleanup(exit_method):
  # Run some basic exit cleanup tasks
  if exit_method == 'crash':
    kill_ssh()
    sys.exit(1)
  else:
    os.unlink(pidfile)
    write_last_run()
    sys.exit(0)

def run_remote_cmd(cmd_args, cmd_path = ""):
  # Run a command on remote host via SSH
  HOST = xmr_stak_ip
  if cmd_path:
    COMMAND = "%s %s" % (cmd_path, cmd_args)
  else:
    COMMAND = cmd_args

  ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

  result = ssh.stdout.read()

  if result == []:
    error = ssh.stderr.readlines()
    logger.error("ERROR running remote command: %s" % error)
  else:
    return result

def setup_logger():
  #Set log path and log file name
  logPath = "/var/log"
  fileName = "hashrate_monitor.log"
  logger = logging.getLogger()

  logging.basicConfig(level=logging.DEBUG)
  logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
  fileHandler = logging.FileHandler("{0}/{1}".format(logPath, fileName))
  fileHandler.setFormatter(logFormatter)

  logger.addHandler(fileHandler)
  consoleHandler = logging.StreamHandler()
  consoleHandler.setFormatter(logFormatter)
  logger.addHandler(consoleHandler)

  return logger

if __name__ == "__main__":
  set_pidfile()
  logger = setup_logger()
  main()
