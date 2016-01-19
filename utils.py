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