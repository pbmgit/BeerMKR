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


#log = open('marlinlog.log', 'a')
ooo = "Beginning Text"
logstate = False 
brewstate = "brewtemp initialization\n"

ser = serial.Serial(port='/dev/ttyACM0', baudrate=250000, parity=serial.PARITY_NONE, timeout=1)
ser.isOpen()

run = True
while run:
#
#Input Command Section
#Read batch of commands from input file then truncate

  with open('marlinqueue.cmd','r+') as cmdfile:
    rf = True
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
        brewstate = cmdline
        serwrite = False

      if cmdline.startswith('ABORT'):
        cmdfile.truncate(0)
        logger(logstate, cmdline)
        exit()
      if len(cmdline) == 0:
        cmdfile.truncate(0)
        break

      logger(logstate, cmdline)

      if serwrite:
         ser.write(cmdline.encode())

#
# Marlin reply Section
#
  mreply = True
  while mreply:
    line = ser.readline()
    #print(line)

    if len(line) == 0:
      break
    ooo = line.decode()
    #print(ooo)

    logger(logstate, ooo)

    if ooo.startswith(' T:'):
      lognow=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

      with open('statusfile','w') as stfile:
        stfile.write(lognow + '\n')
        stfile.write(brewstate)
        stfile.write(ooo)

  time.sleep(5)
