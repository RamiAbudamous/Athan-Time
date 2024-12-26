import requests
import json
import datetime
from datetime import datetime
import os
from time import sleep

def callAPI(currTime, lat, long):
    #method 2 is North America Islamic Association's method for deciding athan time
    url = f"https://api.aladhan.com/v1/timings/{currTime.month}-{currTime.day}-{currTime.year}"
    querystring = {"latitude":f"{lat}", "longitude":f"{long}", "method":"2"}
    response = requests.request("GET", url, params=querystring)
    return json.loads(response.text)

def getTimings(timings):
    #get timings as int minutes
    fajr = timeToMins(timings["Fajr"])
    sunrise = timeToMins(timings["Sunrise"])
    duhr = timeToMins(timings["Dhuhr"])
    asr = timeToMins(timings["Asr"])
    maghrib = timeToMins(timings["Maghrib"])
    isha = timeToMins(timings["Isha"])
    return [fajr, sunrise, duhr, asr, maghrib, isha]

def timeToMins(time):
    hours, minutes = map(int, time.split(':'))
    return (hours*60)+minutes

def minsToTime(time, blinker=True):
    hours = int(time/60)
    if hours>12: hours-=12 # convert 24 hour time to 12, ex: 14 becomes 2
    if hours==0: hours=12 # midnight is 12 not 0
    mins = time%60

    if (blinker):
        return f"{hours:2}:{str(mins).zfill(2)}"
    else: return f"{hours:2} {str(mins).zfill(2)}"


# define locations
DAVIS = 0
SC = 1

# initial values
currState = 0
blinker = True

while(1): #runs forever
    state=currState
    if state==DAVIS:
        latitude = 38.54491
        longitude = -121.74052
        place = "Davis"
    elif state==SC:
        latitude = 37.35411
        longitude = -121.95524
        place = "Santa Clara"

    while(state==currState): #this checks every 5 mins
        now = datetime.now()
        startTime = f"{now.hour}:{now.minute}"
        startTimeInt = timeToMins(startTime)
        # now = datetime.fromtimestamp(1735328028)

        # print("calling api now")
        data = callAPI(now, latitude, longitude)
        timings = data["data"]["timings"]

        prayerTimes = getTimings(timings)

        #initial currTime
        currTime = f"{now.hour}:{now.minute}"
        currTimeInt = timeToMins(currTime)

        prayerID = {0: "Fajr", 1: "Sunrise", 2: "Duhr", 3: "Asr", 4: "Maghrib", 5: "Isha"}
        nextPrayer = None
        nextPrayerName = None
        for i in range(len(prayerTimes)):
            if prayerTimes[i]>startTimeInt:
                nextPrayer = prayerTimes[i]
                nextPrayerName = prayerID.get(i)
                break

        #this counts every second, and every 5 mins it goes back to the top
        #when the touchscreen gets added, have that change the state, then this code will also check that state==currState
        while(currTimeInt<startTimeInt+10): #these ints are in minutes, not seconds. so it wont be exactly 10 mins but thats fine
            os.system('cls')

            if blinker:
                blinkedColon = ":"
            else: blinkedColon = " "

            #update currTime
            nowNow = datetime.now()
            currTime = f"{nowNow.hour}:{nowNow.minute}"
            currTimeInt = timeToMins(currTime)

            if nextPrayer!=None:
                timeToNext = nextPrayer-currTimeInt
                hoursToNext = int(timeToNext/60)
                minsToNext = int(timeToNext%60)

            # now that everything is calculated, print them all
            print(f"     {minsToTime(timeToMins(currTime), blinker).strip()}{blinkedColon}{nowNow.second}") #mins to time then time to mins is the easiest way to convert from 24 to 12 hour
            print(f"{now.month}/{now.day}/{now.year}, {place}")
            #print timings as time
            print(f"Fajr        {minsToTime(prayerTimes[0])}")
            print(f"Sunrise     {minsToTime(prayerTimes[1])}")
            print(f"Duhr        {minsToTime(prayerTimes[2])}")
            print(f"Asr         {minsToTime(prayerTimes[3])}")
            print(f"Maghrib     {minsToTime(prayerTimes[4])}")
            print(f"Isha        {minsToTime(prayerTimes[5])}")

            if nextPrayer!=None:
                print(f"{nextPrayerName} in {hoursToNext} hours and {minsToNext} minutes")
            else: print("All Prayers Complete!")

            sleep(1) #wait before updating settings
