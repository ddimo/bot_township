# coding=utf-8

import random
from classes import *
from collections import Counter
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

def FillCurrentOrdersOnlyZoo(gameInfo,buildingSettings):
    curReqs = []
    for key, value in buildingSettings.iteritems():
        if int(value.zooLevel) <= gameInfo.zooLevel and gameInfo.paddocks.get(value.id) != 1:
            # доступно по уровню и еще не построено
            if value.Brick > 0: curReqs.append(["Brick", value.Brick])
            if value.Plita > 0: curReqs.append(["Plita", value.Plita])
            if value.Glass > 0: curReqs.append(["Glass", value.Glass])
            if value.zooBuildingMaterial > 0: curReqs.append(["zooBuildingMaterial", value.zooBuildingMaterial])
            if value.zooServiceMaterial1 > 0: curReqs.append(["zooServiceMaterial1", value.zooServiceMaterial1])
            if value.zooServiceMaterial2 > 0: curReqs.append(["zooServiceMaterial2", value.zooServiceMaterial2])
            if value.zooServiceMaterial3 > 0: curReqs.append(["zooServiceMaterial3", value.zooServiceMaterial3])

    return curReqs


def GenerateZooCommunityChestContent(gameInfo,buildingSettings):
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

    # заполняем список всех требущихся материалов в недостровенных зданиях
    currentZooMaterialReqs = FillCurrentOrdersOnlyZoo(gameInfo,buildingSettings)

    # Из каждого требования вычитаем колличество материалов имеющихся в амбаре
    x = 0
    for key,value in currentZooMaterialReqs:
        currentZooMaterialReqs[x] = [key,value-getattr(gameInfo,key)]
        if value-getattr(gameInfo,key) < 0: currentZooMaterialReqs[x] = [key,0]
        x = x+1

    # Проверяем нужныли в зоопарке обычные материалы для строящихся или не завершенных зданий
    needBuildingMaterial = False
    needBuildingMaterialId = "zooBuildingMaterial"
    _buildingMaterials = []
    if currentZooMaterialReqs:
        for key,value in currentZooMaterialReqs:
            AddByWeight(_buildingMaterials,key,value+gameInfo.zooLevel)
    if _buildingMaterials:
        needBuildingMaterial = True
        needBuildingMaterialId = GetRandomMaterialOrBrickDef(_buildingMaterials)

    chestContent = []

    if needBuildingMaterial:
        AddByWeight(chestContent,needBuildingMaterialId,80)
        # print "adding "+needBuildingMaterialId+" with weight 80"

    AddByWeight(chestContent,"Brick",10)
    AddByWeight(chestContent,"Glass",10)
    AddByWeight(chestContent,"Plita",10)
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
    # print Counter(chestContent)

    return randomMat


def AnyFamilyReady(gameInfo):
    print "starting AnyFamilyReady function"
    for curPaddockId in gameInfo.paddocksTotalAnimals:
        #print gameInfo.paddocksTotalAnimals[curPaddockId]
        if gameInfo.paddocksTotalAnimals[curPaddockId] == 4:
            print "some family IS ready!"
            return True
    print "not a singly family is ready"
    return False



def GenerateZooCommunityChestGemManipulation(gameInfo,buildingSettings,animalsReqs,needGemId):
    ANY_FAMILY_READY = AnyFamilyReady(gameInfo)
    # Бежим по всем готовым загонам к заселению
    for curReadyPaddock in gameInfo.paddocks:
        print ""
        print "starting "+curReadyPaddock
        # Требуемый уровень для постройки
        levelNeed = buildingSettings[curReadyPaddock].zooLevel
        # Максимальный уровень для подыгрвания
        MAX_LEVEL_FOR_GEM_MANIPULATION = 3
        # Будем ли подыгрывать, если уже есть хотябы один завершенный
        if random.randint(0,99) < 50:
            MANIPULATION = True
            print "MANIPULATION is true"
        else:
            MANIPULATION = False
            print "MANIPULATION is false"
        # Минимальная разница между уровнем зоопарка и уровнем загона, с которого начинаем подыгрывать
        LEVEL_DIFF = 3
        if levelNeed > MAX_LEVEL_FOR_GEM_MANIPULATION:
            # Переходим на следующий цикл итерации если требуемый уровень больше MAX_LEVEL_FOR_GEM_MANIPULATION
            print curReadyPaddock+" levelNeed is "+str(levelNeed)+" which is greater than "+str(MAX_LEVEL_FOR_GEM_MANIPULATION)
            continue
        else:
            paddock = curReadyPaddock
            ANIMALS_COUNT = gameInfo.paddocksTotalAnimals[paddock]
            print "ANIMALS_COUNT for "+paddock+" (levelNeed = "+str(levelNeed)+ ") is "+str(ANIMALS_COUNT)
            if ANIMALS_COUNT < 4:
                print "  ANIMALS_COUNT less than 4"
                if levelNeed == 1 and not ANY_FAMILY_READY:
                    print "  levelNeed is 1 and not ANY_FAMILY_READY"
                    differenceGems = GetDiffrenceGemsForNextPaddockAnimal(gameInfo,buildingSettings,animalsReqs,paddock)
                    if differenceGems:
                        print "  returned differenceGems is not empty: "+str(differenceGems)
                        INDX = random.randint(0,len(differenceGems)-1)
                        needGemId = differenceGems[INDX]
                        print "  randomised gem id is: "+needGemId
                        return needGemId
                    else:
                        print "  returned differenceGems is empty, continue"
                        continue
                elif (gameInfo.zooLevel-levelNeed >= LEVEL_DIFF and MANIPULATION):
                    print "  "+str(gameInfo.zooLevel)+"-"+str(levelNeed)+" >= LEVEL_DIFF ("+str(LEVEL_DIFF)+") and also MANIPULATION is True"
                    differenceGems = GetDiffrenceGemsForNextPaddockAnimal(gameInfo,buildingSettings,animalsReqs,paddock)
                    if differenceGems:
                        print "  returned differenceGems is not empty: "+str(differenceGems)
                        INDX = random.randint(0,len(differenceGems)-1)
                        needGemId = differenceGems[INDX]
                        print "  randomised gem id is: "+needGemId
                        return needGemId
                    else:
                        print "  returned differenceGems is empty, continue"
                        continue
                elif not MANIPULATION:
                    print "  manipulation failed"
                    return needGemId
                else:
                    print "  no ifs worked (levelneed>1 or familyready) or (zoolevel-needlevel < 3 or not manipulation) or (manipulation)"
                    return needGemId
            else:
                print "  ANIMALS_COUNT more than 4"
                return needGemId




def GetDiffrenceGemsForNextPaddockAnimal(gameInfo,buildingSettings,animalsReqs,paddock):
    nextAnimalNumber = gameInfo.paddocksTotalAnimals[paddock]+1
    price = animalsReqs[paddock][nextAnimalNumber]
    print "     nextAnimalNumber for "+paddock+ " is "+str(nextAnimalNumber)+" and its price is: "+str(vars(price))
    print "     current amounts are: gem1="+str(gameInfo.gem1)+", gem2="+str(gameInfo.gem2)+", gem3="+str(gameInfo.gem3)+", gem4="+str(gameInfo.gem4)
    differenceGems = []
    if gameInfo.gem1-price.gem1 < 0:
        print "     lacking gem1 because have only "+str(gameInfo.gem1)
        differenceGems.append("gem1")
    if gameInfo.gem2-price.gem2 < 0:
        print "     lacking gem2 because have only "+str(gameInfo.gem2)
        differenceGems.append("gem2")
    if gameInfo.gem3-price.gem3 < 0:
        print "     lacking gem3 because have only "+str(gameInfo.gem3)
        differenceGems.append("gem3")
    if gameInfo.gem4-price.gem4 < 0:
        print "     lacking gem4 because have only "+str(gameInfo.gem4)
        differenceGems.append("gem4")
    return differenceGems


def CheckAlreadyBuilt(gameInfo,buildingId):
    if gameInfo.paddocks.get(buildingId) == 1 or gameInfo.communities.get(buildingId) == 1:
        return True
    else:
        return False


def CheckCanBuild(gameInfo,buildingSettings,buildingId):
    if gameInfo.Brick < buildingSettings.Brick:
        #print "not enough Brick to build "+buildingId+": need "+str(buildingSettings.Brick)+", have "+str(gameInfo.Brick)
        return False
    elif gameInfo.Plita < buildingSettings.Plita:
        #print "not enough Plita to build "+buildingId+": need "+str(buildingSettings.Plita)+", have "+str(gameInfo.Plita)
        return False
    elif gameInfo.Glass < buildingSettings.Glass:
        #print "not enough Glass to build "+buildingId+": need "+str(buildingSettings.Glass)+", have "+str(gameInfo.Glass)
        return False
    elif gameInfo.zooBuildingMaterial < buildingSettings.zooBuildingMaterial:
        #print "not enough zooBuildingMaterial to build "+buildingId+": need "+str(buildingSettings.zooBuildingMaterial)+", have "+str(gameInfo.zooBuildingMaterial)
        return False
    elif gameInfo.zooServiceMaterial1 < buildingSettings.zooServiceMaterial1:
        #print "not enough zooServiceMaterial1 to build "+buildingId+": need "+str(buildingSettings.zooServiceMaterial1)+", have "+str(gameInfo.zooServiceMaterial1)
        return False
    elif gameInfo.zooServiceMaterial2 < buildingSettings.zooServiceMaterial2:
        #print "not enough zooServiceMaterial2 to build "+buildingId+": need "+str(buildingSettings.zooServiceMaterial2)+", have "+str(gameInfo.zooServiceMaterial2)
        return False
    elif gameInfo.zooServiceMaterial3 < buildingSettings.zooServiceMaterial3:
        #print "not enough zooServiceMaterial3 to build "+buildingId+": need "+str(buildingSettings.zooServiceMaterial3)+", have "+str(gameInfo.zooServiceMaterial3)
        return False
    else:
        return True


def DoBuild(gameInfo,buildingSettings,buildingId):
    if "paddock_" in buildingId:
        gameInfo.paddocks[buildingId] = 1
        gameInfo.paddocksTotalAnimals[buildingId] = 0
    elif "zoo_" in buildingId:
        gameInfo.communities[buildingId] = 1

    gameInfo.rating = gameInfo.rating + buildingSettings.bonusRating

    if buildingSettings.Brick>0:
        gameInfo.Brick = gameInfo.Brick-buildingSettings.Brick
    if buildingSettings.Plita>0:
        gameInfo.Plita = gameInfo.Plita-buildingSettings.Plita
    if buildingSettings.Glass>0:
        gameInfo.Glass = gameInfo.Glass-buildingSettings.Glass
    if buildingSettings.zooBuildingMaterial>0:
        gameInfo.zooBuildingMaterial = gameInfo.zooBuildingMaterial-buildingSettings.zooBuildingMaterial
    if buildingSettings.zooServiceMaterial1>0:
        gameInfo.zooServiceMaterial1 = gameInfo.zooServiceMaterial1-buildingSettings.zooServiceMaterial1
    if buildingSettings.zooServiceMaterial2>0:
        gameInfo.zooServiceMaterial2 = gameInfo.zooServiceMaterial2-buildingSettings.zooServiceMaterial2
    if buildingSettings.zooServiceMaterial3>0:
        gameInfo.zooServiceMaterial3 = gameInfo.zooServiceMaterial3-buildingSettings.zooServiceMaterial3

def FindOldestNotFullPaddock(gameInfo,buildingSettings):
    lowestLevel = 666
    lowestLevelId = "n/a"
    for key, value in gameInfo.paddocks.items():
        print key,value
        if value == 1: # на всякий случай
            if gameInfo.paddocksTotalAnimals[key] < 4: # животных меньше 4
                if buildingSettings[key].zooLevel < lowestLevel:
                    lowestLevel = buildingSettings[key].zooLevel
                    lowestLevelId = key

    return [lowestLevelId,lowestLevel]