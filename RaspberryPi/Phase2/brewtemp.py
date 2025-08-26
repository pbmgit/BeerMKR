#!/usr/bin/python3
import serial
import os
import datetime
import time

def logger(logstate, logstring):
  if not logstate:
    return

  with open('marlinlog.log','a') as log:
    lognow=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logstringdt = lognow + " " + logstring + "\n"
    log.write(logstringdt)

def check_marlin_queue(logstate, rf=True):
  """
  Process commands from marlinqueue.cmd file
  :param logstate: current logging state (True/False)
  :param rf: loop control flag (default True)
  :returns: tuple (logstate, rf) - logging state and loop control
  """
  with open('marlinqueue.cmd','r+') as cmdfile:
    while rf:
      serwrite = True
      cmdline = cmdfile.readline()
      #print('[' + cmdline + ']')
      if cmdline.lower().startswith('logging:on'):
        logstate = True
        serwrite = False
      if cmdline.lower().startswith('logging:off'):
        logger(logstate, cmdline)
        logstate = False
        serwrite = False

      if cmdline.startswith('#'):
        global brewstate
        brewstate = cmdline
        serwrite = False

      if cmdline.startswith('ABORT'):
        cmdfile.truncate(0)
        logger(logstate, cmdline)
        exit()
      if len(cmdline) == 0:
        cmdfile.truncate(0)
        rf = False
        return logstate, rf

      logger(logstate, cmdline)

      if serwrite:
        ser.write(cmdline.encode())

    return logstate, rf

def check_reply(logstate, mreply):
  """
  Process replies from Marlin firmware
  :param logstate: current logging state (True/False)
  """
  while mreply:
    line = ser.readline()
    if len(line) == 0:
      break
    ooo = line.decode()
    logger(logstate, ooo)

    if ooo.startswith(' T:'):
      lognow=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      with open('statusfile','w') as stfile:
        stfile.write(lognow + '\n')
        stfile.write(brewstate)
        stfile.write(ooo)

# Initialize variables
ooo = "Beginning Text"
# To be able to test
logstate = False
mreply = True
brewstate = "brewtemp initialization\n"

ser = serial.Serial(port='/dev/ttyACM0', baudrate=250000, parity=serial.PARITY_NONE, timeout=1)
ser.isOpen()

run = True
# Main Loop only runs when file is executed directly
if __name__ == '__main__':
  while run:
    # Input Command Section
    # Read batch of commands from input file then truncate
    logstate, rf = check_marlin_queue(logstate, True)

    # Marlin reply Section
    check_reply(logstate, mreply)

    time.sleep(5)