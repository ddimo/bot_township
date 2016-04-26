# coding=utf-8

from gather_info import *

# upgradesReqs['zoo_caffe'][1] = class with reqs for upgrade #1 (Brick,Plita .. animalsCount)

for i in range(1,40):
    print ""
    print "level "+str(i)
    for cid,upgrades in upgradesReqs.iteritems():
        k = 0
        for upgrade in upgrades:
            if not upgrade == '':
                k+=1
                if upgrade.zooLevel == i:
                    print cid,k
                elif upgrade.zooLevel > i:
                    continue