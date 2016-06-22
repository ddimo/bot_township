# coding=utf-8

from gather_info import *

MAX_LEVEL = 34
levelReqs = list()

# upgradesReqs['zoo_caffe'][1] = class with reqs for upgrade #1 (Brick,Plita .. animalsCount)

for i in range(1,MAX_LEVEL+1):   # going through levels from 1 up to 40
    print ""
    print "level "+str(i)

    curLevelMatReqs = dict()
    curLevelMatReqs["Brick"] = 0
    curLevelMatReqs["Glass"] = 0
    curLevelMatReqs["Plita"] = 0
    curLevelMatReqs["zooBuildingMaterial"] = 0
    curLevelMatReqs["zooServiceMaterial1"] = 0
    curLevelMatReqs["zooServiceMaterial2"] = 0
    curLevelMatReqs["zooServiceMaterial3"] = 0

    # 1st lets look for upgrades
    for cid,upgrades in upgradesReqs.iteritems():
        upNum = 0
        for upgrade in upgrades:
            if not upgrade == '':
                upNum+=1
                if upgrade.zooLevel == i:
                    print "upgrade #"+str(upNum)+" for "+str(cid)
                    curLevelMatReqs["Brick"] += upgrade.Brick
                    curLevelMatReqs["Glass"] += upgrade.Glass
                    curLevelMatReqs["Plita"] += upgrade.Plita
                    curLevelMatReqs["zooBuildingMaterial"] += upgrade.zooBuildingMaterial
                    curLevelMatReqs["zooServiceMaterial1"] += upgrade.zooServiceMaterial1
                    curLevelMatReqs["zooServiceMaterial2"] += upgrade.zooServiceMaterial2
                    curLevelMatReqs["zooServiceMaterial3"] += upgrade.zooServiceMaterial3
                elif upgrade.zooLevel > i:
                    continue

    # now constructions
    # buildingSettings["paddock_zebra"].zooBuildingMaterial - количество требуемого материала
    # buildingSettings["zoo_caffe"].zooLevel - требуемый уровень
    for bid in buildingSettings:
        if buildingSettings[bid].zooLevel == i:
            print "construction of "+str(bid)
            curLevelMatReqs["Brick"] += buildingSettings[bid].Brick
            curLevelMatReqs["Glass"] += buildingSettings[bid].Glass
            curLevelMatReqs["Plita"] += buildingSettings[bid].Plita
            curLevelMatReqs["zooBuildingMaterial"] += buildingSettings[bid].zooBuildingMaterial
            curLevelMatReqs["zooServiceMaterial1"] += buildingSettings[bid].zooServiceMaterial1
            curLevelMatReqs["zooServiceMaterial2"] += buildingSettings[bid].zooServiceMaterial2
            curLevelMatReqs["zooServiceMaterial3"] += buildingSettings[bid].zooServiceMaterial3

    print curLevelMatReqs
    levelReqs.append(curLevelMatReqs)

# now lets print diz sheet

print ""
print "printing csv format for copy"
print ""
print "zooLevel,Brick,Glass,Plita,zBM,zSM1,zSM2,zSM3"
for i in range(1,MAX_LEVEL+1):
    print str(i)+","+str(levelReqs[i-1]["Brick"])+","+str(levelReqs[i-1]["Glass"])+","+str(levelReqs[i-1]["Plita"])+","+str(levelReqs[i-1]["zooBuildingMaterial"])+","+str(levelReqs[i-1]["zooServiceMaterial1"])+","+str(levelReqs[i-1]["zooServiceMaterial2"])+","+str(levelReqs[i-1]["zooServiceMaterial3"])