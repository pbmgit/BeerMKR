#!/usr/bin/python3

import datetime
import time
from datetime import timedelta 

#Delay variables
tempwait = False
timewait = False
buttonwait = False

bagTempWaitValue = 40 
grainTempWaitValue = 0
waitDT = datetime.datetime.now()


filepath = '/home/BeerPi'
recipefile ='recipe.bmkr'
logfilename = 'brewlog.log'
recipestatefile = 'reciperunningstate'
marlinqueue = 'marlinqueue.cmd'
statusfile = 'statusfile'

def logger(logstate, logstring):

   if not logstate:
      return

   with open(logfilename,'a') as log:
      lognow=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      logstringdt = lognow + " " + logstring + "\n"
      log.write(logstringdt)


def marlincmd(cmdstring):
   try: 
        with open('marlinqueue.cmd','a') as cmdfile:
            cmdfile.write(cmdstring + "\n")
            print ('--->' + cmdstring + "\n")
   except Exception as e:
        print(f"An error occurred: {e}")

def checkdelay():
#  this is a blocking module.  Execution will not exit this module until block conditions are passed
   
   checktempdelay()
   checktimedelay()
   checkbutton(buttonwait)

# temperature checking.  This returns when temperature conditions have been met
def  checktempdelay():
   global tempwait
   global bagTempWaitValue
   global grainTempWaitValue
   while tempwait:
      with open(statusfile,'r') as sf:
         timetag = sf.readline()
         statelabel = sf.readline()
         tempstate = sf.readline()
         fields = tempstate.split(' ')
         print(fields)
         tokens = fields[1].split(':')
         graintemp = int(float(tokens[1]))
         tokens = fields[3].split(':')
         bagtemp = int(float(tokens[1]))
         print('In temperature wait loop')
         print(graintemp)
         print(bagtemp)
         if bagTempWaitValue != 0 and bagtemp == bagTempWaitValue:
            tempwait = False
            bagTempWaitValue = 0

         elif grainTempWaitValue != 0 and graintemp == grainTempWaitValue:
            tempwait = False
            grainTempWaitValue = 0
            
        

         loopwait = 15
         time.sleep(loopwait)


def checktimedelay():
    global timewait
    global waitDT
    
    while timewait:
        print('In Time Wait Loop.  Target ' + waitDT.ctime())
        if datetime.datetime.now() > waitDT:
            timewait = False
            
        loopwait = 15
        time.sleep(loopwait)
    
    
def checkbutton():
    global buttonwait
    if buttonwait:
        while buttonwait:
            print('In Button Wait')
            with open('buttonfile','r+') as btfile:
                ptext = btfile.readline()
                print('Bstatus... [' + ptext + ']')
                if ptext.strip().lower() == 'pressed':
                    print('Button Press Detected')
                    buttonwait = False
                    btfile.truncate(0)
                    break
        
            loopwait = 15
            time.sleep(loopwait)

            
    
         




defaultmonitorinterval = 60

recipe = []
rindex = 0

with open(recipefile) as rf:
   for lines in rf:
      recipe.append(lines.strip())


print(recipe)

stepnum = 0

for step in recipe:
    
#check for programmed delays
   checktempdelay()
   checktimedelay()
   checkbutton()
   print('After Delay Checks')

# Parse recipe step
   print(step)
   nugget = step.split(':')
   print(nugget)
   print(nugget[0].lower())

# Steps that require no token parsing
   if step == 'logging:on' or step == 'logging:off':
        marlincmd(step)
        
   elif step.startswith('#'):
        marlincmd(step)
     
# Steps that require examining tokens (nugget variable)
   elif nugget[0].lower() == 'monitor':
# Monitor:Off code
        if nugget[1] == 'off':
            marlincmd('M155 S0')
        elif nugget[1] == 'on':
# Monitor on with optional interval setting
            interval = defaultmonitorinterval
            if len(nugget) > 2:
                interval = int(nugget[2])
       
            marlincmd('M155 S' + str(interval))

# Bag Temperature Set Section
   elif nugget[0].lower() == 'bag':
        if nugget[1].lower() == 'off':
            marlincmd('M140 S0')
        elif nugget[1].lower() == 'set':
            tempC = int(nugget[2])
            marlincmd('M140 S' + str(tempC))
            
            if len(nugget) > 3:
                print("Bag hold temperature detected")
                if nugget[3].lower() == 'wait':
                    tempwait = True
                    bagTempWaitValue = tempC
            

# Grain Temperature Set Section
   elif nugget[0].lower() == 'grain':
        if nugget[1].lower() == 'off':
            marlincmd('M104 S0')
        elif nugget[1].lower() == 'set':

            tempC = int(nugget[2])
            
            marlincmd('M104 S' + str(tempC))
            print("Nugget Length " + str(len(nugget)))
            if len(nugget) > 3:
                if nugget[3].lower() == 'wait':
                    print('Grain hold temperature detected')
                    tempwait = True
                    grainTempWaitValue = tempC

# Wait section
   elif nugget[0].lower() == 'wait':
        print('Wait Parsing')
 
#  Button Wait parsing
        if nugget[1].lower() == 'button':
            print('Button Wait Parsing')
            buttonwait = True
            

# Wait (time) section
        else:
            print('Time Wait Parsing')
            secsdelay = int(nugget[1])
            interval = timedelta(seconds=secsdelay)
            waitDT = datetime.datetime.now() + interval
            timewait = True




