# coding=utf-8
import random
import numpy as np

totals = {"money":0, "cash":0, "bullion":0, "mats":0, "gems":0, "zoomats":0}
totalCash = []

def GenerateErnieBaloonReward():
    reward = "unknown"
    rewardCount = 0

    r = random.randint(0,100)
    if r < 10:
        r = 1 # coins
    elif r < 30:
        r = 2 # cash
    elif r < 45:
        r = 6 # zoomats
    elif r < 81:
        r = 4 # mats
    elif r < 84:
        r = 5 # bullions
    else:
        r = 3 # gems

    if r == 1:
        reward = "money"
        rewardCount = 30
    elif r == 2:
        reward = "cash"
        rewardCount = random.randint(4,5)
        if random.randint(0,100) < 20:
            rewardCount = 6
    elif r == 3:
        reward = "bullion"
        rewardCount = 1
    elif r == 4:
        reward = "mats"
        rewardCount = 1
    elif r == 5:
        reward = "gems"
        rewardCount = 1
    elif r == 6:
        reward = "zoomats"
        rewardCount = 1

    totals[reward] += 1
    if reward == "cash":
        totalCash.append(rewardCount)

i = 0
limit = 100

while i < limit:
    i += 1
    GenerateErnieBaloonReward()

print totals

for key,value in totals.iteritems():
    curPercent = int(round((float(value)/float(limit))*100))
    print key,value,curPercent

avrgCash = np.mean(totalCash)
avrgCash = round(avrgCash,5)

sumCash = sum(totalCash)
avrgCashFromChests = float(sumCash)/float(limit)

print ""
print "average cash:"
print avrgCash

print ""
print "average cash from all chests:"
print avrgCashFromChests