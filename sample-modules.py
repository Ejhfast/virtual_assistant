from core import Assistant
import sys
import random
import math

assistant = Assistant()

# turn on Flux when I turn off Word
@assistant.register("open {app}")
def open(app):
	print("Opened", app)
	return

@assistant.register("quit {app}")
def quit(app):
	print("Quit", app)
	return

@assistant.register("listen to {app}")
def listen(app):
	print("Listening to the state of the app", app)
	states = ["on", "off"]
	state = random.choice(states)
	print("State of the app", app, "is", state)
	return state

@assistant.register("turn {state1} {app1} when I turn {state2} {app2}")
def toggleWithChangedState(state1, app1, state2, app2):
	while state1 not in ["on","off"]:
		state1 = input("Would you like to turn " + app1 + " on or off? ")
	param = "listen to " + app2
	while True:
		currState = assistant.execute(param)
		if currState == state2:
			break
	print("User has decided to turn", state2, app2)
	print("Turning the app", app1, state1)
	if state1 == "on":
		param = "open " + app1
		assistant.execute(param)
	else:
		param = "quit " + app1
		assistant.execute(param)
	return

# wake me up in 5 min
@assistant.register("set countdown for {time}")
def setTimer(time):
	print("Setting countdown timer (in ms) for", time)
	for i in range(int(time)):
		if i % 60000 == 0:
			print("1 min passed by")
	return

@assistant.register("trigger alarm")
def triggerAlarm():
	print("ALARM!!!")

@assistant.register("convert {amount1} {unit1} to {unit2}")
def convert(amount1, unit1, unit2):
	print("Converting", amount1, unit1, "into", unit2)
	amount2 = 300000
	return amount2

@assistant.register("wake me up in {n} {unit}")
def alarm(n, unit):
	unitTime = "ms"
	param = "convert " + str(n) + " " + unit + " to " + unitTime
	amountTime = assistant.execute(param)
	assistant.execute("set countdown for " + str(amountTime))
	assistant.execute("trigger alarm")
	return

# tell Sarah I love you everyday at 5pm in different ways
@assistant.register("tell {person} {message} {frequency} at {time} in different ways")
def repeatedText(person, message, frequency, time):


# when should I go to Safeway? 
#ask: where are you now? determine distance + calendar sync to find when available
@assistant.register("when should I go to {location}")


# Notify people I’m meeting with later if I’m going to be late
#detect invites to events in calendar, detect where I am now and distance from the event location;
# if past time that I can get there on time, text/email the invitees
@assistant.register("tell people I'm meeting with later if I'm going to be late")


print(assistant.execute(sys.argv[1]))
