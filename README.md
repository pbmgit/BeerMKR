# BeerMKR
Extensions to BeerMKR machine to keep brewing if no AWS

History

I've really enjoyed brewing with the BeerMKR and I'm an Engineer (at least that's what my 40 year old degree says).
So I link to tinker and understand how and why things work.  

That applies to the beer I brew, I like to experiment.
And now that applies to the BeerMKR machine.

My BeerMKR tinkering started when I just wasn't cooling as well as I once was.  I started measuring voltages and currents on the Pelteir and decided that the heating and cooling cycles on the Peltier might have caused cracking in the solder joints which caused the resistance to rise and the current flow to fall.  With a Peltier heat transfer is proportional to current flow.
Part of that was based on this article https://www.sameskydevices.com/blog/reliability-considerations-for-peltier-modules
I also researched and changed my vibrator motor since the bushings on the original motor were so far gone that the rotor was hitting the magnets.

When I replaced the Peltier I found that I was cooling better than ever but I had some odd issues with brewing.  That got me to investigating how and when the heaters go turned on.
After that I brewed with my board connected, but clear out of my machine as I tried to figure things out.
It seems that the software on my BeerMKR board just wasn't compatible with my new Peltier.  So I started to figure out how to do the job without the BeerMKR computer.

I mapped out the connectors and ordered some of them.
I gleaned what I could from the BeerMKR board design - what parts do what.

Development

I started thinking about what I could without completely inventing the wheel.  Unrelated to my brewing I had been updating my 3D printer.  The 3D printer has temperature readings and power controls to manage the heated bed and extruder.  I thought I might use that to control the Peltier and heaters on the BeerMKR instead.
I successfully got a code change into the Marlin project that allows the heated bed power circuitry to be used to control a Peltier device (in 3D printing, when you want to cool down you just turn off whichever heater - you don't actively cool)

The BeerMKR board uses an "H-Bridge" consisting of 4 power FET transistors to turn on the Peltier in either direction.  Since the Peltier draws in excess of 8A that takes some care to replicate.
For my first pass I just used a DPDT relay configured as an H-Bridge.
For my Marlin setup I used an Arduino Mega board with a "RAMPS" (RepRap Arduino Mega Pololu Shield) to plug in on top of the Mega.  The RAMPS board has some power electronics for the heaters that we'll use and some sockets for Pololu stepper motor controls that we won't use.

For the first test the Mega was plugged into a laptop and the brewing was controlled through a serial port.  Not exactly automation, but it worked.
