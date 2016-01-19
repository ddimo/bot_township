import random

class gameInfoClass:
    def __init__(self):
        self.countZooCommunityChest = 0
        self.chestWithoutLandDeed = 0
        self.playerLevel = 40
        self.zooLevel = 1

        self.Brick = 30
        self.Glass = 30
        self.Plita = 30
        self.zooBuildingMaterial = 0
        self.zooServiceMaterial1 = 0
        self.zooServiceMaterial2 = 0
        self.zooServiceMaterial3 = 0
        self.zooLandDeed = 0
        self.hammerMat = 10
        self.nailMat = 10
        self.paintRedMat = 10
        self.pick = 10
        self.axe = 10
        self.TNT = 10

gameInfo = gameInfoClass()

attrs = vars(gameInfo)
print ', '.join("%s: %s" % item for item in attrs.items())
print ""

def AddByWeight(weights_string,newvalue,amount):
    for x in range(0,amount):
        weights_string.append(newvalue)

def GetRandomMaterialOrBrickDef(chestContent):
    chestContentLen = len(chestContent)
    rand = random.randint(0,chestContentLen-1)
    return chestContent[rand]

def GenerateZooCommunityChestContent():
    if gameInfo.countZooCommunityChest == 0:
        curvalue = getattr(gameInfo,"countZooCommunityChest")
        setattr(gameInfo,"countZooCommunityChest",curvalue+1)
        return "zooBuildingMaterial"
    elif gameInfo.countZooCommunityChest == 1:
        curvalue = getattr(gameInfo,"countZooCommunityChest")
        setattr(gameInfo,"countZooCommunityChest",curvalue+1)
        return "zooServiceMaterial2"
    elif gameInfo.countZooCommunityChest == 2:
        curvalue = getattr(gameInfo,"countZooCommunityChest")
        setattr(gameInfo,"countZooCommunityChest",curvalue+1)
        return "zooBuildingMaterial"
    elif gameInfo.countZooCommunityChest == 3:
        curvalue = getattr(gameInfo,"countZooCommunityChest")
        setattr(gameInfo,"countZooCommunityChest",curvalue+1)
        return "pick"

    chestContent = []
    AddByWeight(chestContent,"Brick",155)
    AddByWeight(chestContent,"Glass",155)
    AddByWeight(chestContent,"Plita",155)
    AddByWeight(chestContent,"zooBuildingMaterial",20)
    AddByWeight(chestContent,"zooServiceMaterial1",10)
    AddByWeight(chestContent,"zooServiceMaterial2",10)
    AddByWeight(chestContent,"zooServiceMaterial3",10)
    AddByWeight(chestContent,"hammerMat",3)
    AddByWeight(chestContent,"nailMat",3)
    AddByWeight(chestContent,"paintRedMat",3)
    AddByWeight(chestContent,"zooLandDeed",2)
    AddByWeight(chestContent,"pick",2)
    AddByWeight(chestContent,"axe",2)
    AddByWeight(chestContent,"TNT",1)

    randomMat = GetRandomMaterialOrBrickDef(chestContent)

    return randomMat

# for s in range(0,len(chestContent)):
#     print chestContent[s]
# print " "

for x in range(0,10):
    randomMat = GenerateZooCommunityChestContent()
    curvalue = getattr(gameInfo,randomMat)
    setattr(gameInfo,randomMat,curvalue+1)
    print "random value is:", randomMat

attrs = vars(gameInfo)
print ""
print ', '.join("%s: %s" % item for item in attrs.items())