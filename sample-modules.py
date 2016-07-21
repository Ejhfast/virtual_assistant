from core import Assistant
import sys
import random
import math
import time
import datetime

assistant = Assistant()

# python sample-modules.py 'turn on Flux when I turn off Word'
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
	print(state1, app1, state2, app2)
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

# python sample-modules.py 'wake me up in 5 min'
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

# python sample-modules.py 'text Sarah "I love you" everyday at 5pm in 6 different ways'
@assistant.register("what is phone number of {person}?")
def getContactNumber(person):
	print("Looking up phone number of " + person)
	number = '555-555-5555'
	return number

@assistant.register("another way to say {string}")
def synonyms(string):
	print("Getting synonyms of " + string)
	synonyms = ["I love you", "love you", "I love you!", "I love you <3", "I <3 you", "ilu"]
	return synonyms

@assistant.register("time object of {string}")
def convertTime(string):
	print("Detecting time format of " + string)
	print("Converting into time object from string")
	return string

@assistant.register("send text {message} to {person}")
def sendSMS(message, person):
	number = getContactNumber(person)
	return(print("Sending text with message " + message + " to " + person + " at " + number))

@assistant.register("do {action} at this {time} {frequency}")
def scheduleCronJob(action, time, frequency):
	print(" is scheduled for " + time + " at frequency of " + frequency)

@assistant.register("text {person} {message} {frequency} at {time} in {n} different ways")
def repeatedText(person, message, frequency, time, n):
	texts = synonyms(message)
	times = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
	for i in range(len(texts)):
		k = i % len(times)
		t = time + " " + times[k]
		j = i % len(texts)
		text = texts[j]
		scheduleCronJob(sendSMS(text, person), t, "every " + str(len(texts)) + " days")


# when should I go to Safeway for 20 min? 
# assumes using current location for origin... hmmm not the event before
def scheduleEvent(name, time, duration):
	print("Scheduling " + name + " at " + time + " for " + str(duration) + " min")

def findFreeTimeSlots(duration):
	print("Finding free time slots available for " + str(duration) + " min")
	slots = ["Tomorrow at 12pm", "Friday at 4pm", "Saturday at 9am"]
	return slots

def scheduleFreeTime(name, duration):
	freeTimes = findFreeTimeSlots(duration)
	scheduleEvent(name, freeTimes[0], duration)
	print("Scheduled event " + name + " in 1st free time slot at " + freeTimes[0] + " for " + str(duration) + " min")

def getCurrentLocation():
	print("Finding current location")
	coordinates = "home"
	return coordinates

def distance(origin, destination):
	print("Finding distance between " + origin + " and " + destination)
	distance = 5
	return distance

@assistant.register("when should I go to {location} for {duration} min?")
def scheduleErrand(location, duration):
	origin = getCurrentLocation()
	travelDistance = distance(origin, location)
	speed = 10
	travelTime = 2 * travelDistance * speed
	scheduleFreeTime("go to " + location, travelTime + duration)


print(assistant.execute(sys.argv[1]))
