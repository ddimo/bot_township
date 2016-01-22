import random
import xml.etree.ElementTree as xml
from os.path import expanduser

class CommentsParser(xml.XMLTreeBuilder):

   def __init__(self):
       xml.XMLTreeBuilder.__init__(self, encoding='utf-8')
       self._parser.CommentHandler = self.comment

   def comment(self, data):
       self._target.start(xml.Comment, {})
       self._target.data(data)
       self._target.end(xml.Comment)


def findElementByAttribute(parent, tagName, attributeName, attributeValue):
    for elem in parent.iter(tagName):
        if elem.get(attributeName) == attributeValue:
            return elem
    return None

def indent(elem, level=0):
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def AddByWeight(weights_string,newvalue,amount):
    for x in range(0,amount):
        weights_string.append(newvalue)

def GetRandomMaterialOrBrickDef(chestContent):
    chestContentLen = len(chestContent)
    rand = random.randint(0,chestContentLen-1)
    return chestContent[rand]

def GenerateZooCommunityChestContent(gameInfo):
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

def CheckAlreadyBuilt(gameInfo,buildingId):
    if buildingId in gameInfo.paddocks:
        if gameInfo.paddocks[buildingId] == 0:
            return False
        else:
            return True
    elif buildingId in gameInfo.communities:
        if gameInfo.communities[buildingId] == 0:
            return False
        else:
            return True
    else:
        return False

def CheckCanBuild(gameInfo,buildingReq,buildingId):
    if gameInfo.Brick < buildingReq.Brick:
        #print "not enough Brick to build "+buildingId+": need "+str(buildingReq.Brick)+", have "+str(gameInfo.Brick)
        return False
    elif gameInfo.Plita < buildingReq.Plita:
        #print "not enough Plita to build "+buildingId+": need "+str(buildingReq.Plita)+", have "+str(gameInfo.Plita)
        return False
    elif gameInfo.Glass < buildingReq.Glass:
        #print "not enough Glass to build "+buildingId+": need "+str(buildingReq.Glass)+", have "+str(gameInfo.Glass)
        return False
    elif gameInfo.zooBuildingMaterial < buildingReq.zooBuildingMaterial:
        #print "not enough zooBuildingMaterial to build "+buildingId+": need "+str(buildingReq.zooBuildingMaterial)+", have "+str(gameInfo.zooBuildingMaterial)
        return False
    elif gameInfo.zooServiceMaterial1 < buildingReq.zooServiceMaterial1:
        #print "not enough zooServiceMaterial1 to build "+buildingId+": need "+str(buildingReq.zooServiceMaterial1)+", have "+str(gameInfo.zooServiceMaterial1)
        return False
    elif gameInfo.zooServiceMaterial2 < buildingReq.zooServiceMaterial2:
        #print "not enough zooServiceMaterial2 to build "+buildingId+": need "+str(buildingReq.zooServiceMaterial2)+", have "+str(gameInfo.zooServiceMaterial2)
        return False
    elif gameInfo.zooServiceMaterial3 < buildingReq.zooServiceMaterial3:
        #print "not enough zooServiceMaterial3 to build "+buildingId+": need "+str(buildingReq.zooServiceMaterial3)+", have "+str(gameInfo.zooServiceMaterial3)
        return False
    else:
        return True


def DoBuild(gameInfo,buildingReq,buildingId):
    if "paddock_" in buildingId:
        gameInfo.paddocks[buildingId] = 1
    elif "zoo_" in buildingId:
        gameInfo.communities[buildingId] = 1

    if buildingReq.Brick>0:
        gameInfo.Brick = gameInfo.Brick-buildingReq.Brick
    if buildingReq.Plita>0:
        gameInfo.Plita = gameInfo.Plita-buildingReq.Plita
    if buildingReq.Glass>0:
        gameInfo.Glass = gameInfo.Glass-buildingReq.Glass
    if buildingReq.zooBuildingMaterial>0:
        gameInfo.zooBuildingMaterial = gameInfo.zooBuildingMaterial-buildingReq.zooBuildingMaterial
    if buildingReq.zooServiceMaterial1>0:
        gameInfo.zooServiceMaterial1 = gameInfo.zooServiceMaterial1-buildingReq.zooServiceMaterial1
    if buildingReq.zooServiceMaterial2>0:
        gameInfo.zooServiceMaterial2 = gameInfo.zooServiceMaterial2-buildingReq.zooServiceMaterial2
    if buildingReq.zooServiceMaterial3>0:
        gameInfo.zooServiceMaterial3 = gameInfo.zooServiceMaterial3-buildingReq.zooServiceMaterial3

