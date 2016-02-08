# coding=utf-8

import random
from globalvars import *
from collections import Counter
import xml.etree.ElementTree as xml

def writeLog(divclass,text):
    f.write("<div class='"+divclass+"'>"+text+"</div>")

def writeShortLog(divclass,text):
    fshort.write("<div class='"+divclass+"'>"+text+"</div>")

def writeHtmlHead():
    with open("_htmlhead") as fp:
        for line in fp:
            f.write(line)
            fshort.write(line)

def writeHtmlFoot():
    f.write("<br><br></body></html>")
    fshort.write("<br><br></body></html>")

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
    counter = Counter(chestContent)
    lineToWrite = "<i>random from weights: "
    for key, value in counter.iteritems():
        lineToWrite = lineToWrite+key+" &mdash; "+str(value)+", "
    lineToWrite += "</i> ---> result: <u>"+chestContent[rand]+"</u>"
    writeLog("normalSmall",lineToWrite)
    return chestContent[rand]

def FillCurrentOrdersOnlyZoo():
    curReqs = []
    for key, value in buildingSettings.iteritems():
        if int(value.zooLevel) <= gameInfo.zooLevel and gameInfo.paddocks.get(value.id) != 1:
            # доступно по уровню и еще не построено
            for mat in buildingMatList:
                if getattr(value, mat) > 0:
                    curReqs.append([mat, getattr(value, mat)])

    return curReqs

def FillCurrentZooUpgradePrices():
    curReqs = []
    totalAnimals = sum(gameInfo.paddocksTotalAnimals.itervalues())
    for key, value in gameInfo.communities.iteritems():
        if value == 1: # если комьюнити построено
            curBuildingUpgrade = int(gameInfo.communitiesUpgrades[key]) # количество его текущих апгрейдов
            # upgradesReqs[key][nextUpgrade].animalsCount
            for upNum, upSettings in enumerate(upgradesReqs[key]):
                if upSettings:
                    if upNum <= curBuildingUpgrade: continue
                    elif upSettings.animalsCount > totalAnimals: break
                    else:
                        for mat in buildingMatList:
                            if getattr(upSettings, mat) > 0:
                                curReqs.append([mat, getattr(upSettings, mat)])
                        writeLog("normalSmall","<i>upgrade #"+str(upNum)+
                                    "is available for "+key+" because totalAnimals = "+str(totalAnimals))

    return curReqs


def FindUpdateToBuy():
    totalAnimals = sum(gameInfo.paddocksTotalAnimals.itervalues())
    for key, value in gameInfo.communities.iteritems():
        if value == 1: # если комьюнити построено
            curBuildingUpgrade = int(gameInfo.communitiesUpgrades[key]) # количество его текущих апгрейдов
            for upNum, upSettings in enumerate(upgradesReqs[key]): # пробежимся по всем апгрейдам данного здания
                if upSettings:
                    if upNum <= curBuildingUpgrade: continue # апгрейд уже есть - пропускаем
                    elif upSettings.animalsCount > totalAnimals: break # ушли далеко, прекращаем
                    else: # а вот это уже подходящий апгрейд
                        # хватит ли нам на него материалов?
                        canDo = True
                        for mat in buildingMatList:
                            if getattr(upSettings,mat) > getattr(gameInfo,mat):
                                canDo = False
                                break
                        if canDo:
                            return key, upNum
                        else:
                            return False


def GenerateZooCommunityChestContent():

    helped = {}
    wasHelped = "no"

    if gameInfo.countZooCommunityChest == 0:
        curvalue = getattr(gameInfo,"countZooCommunityChest")
        setattr(gameInfo,"countZooCommunityChest",curvalue+1)
        return "zooBuildingMaterial", "firstDrops"
    elif gameInfo.countZooCommunityChest == 1:
        curvalue = getattr(gameInfo,"countZooCommunityChest")
        setattr(gameInfo,"countZooCommunityChest",curvalue+1)
        return "zooServiceMaterial2", "firstDrops"
    elif gameInfo.countZooCommunityChest == 2:
        curvalue = getattr(gameInfo,"countZooCommunityChest")
        setattr(gameInfo,"countZooCommunityChest",curvalue+1)
        return "zooBuildingMaterial", "firstDrops"
    elif gameInfo.countZooCommunityChest == 3:
        curvalue = getattr(gameInfo,"countZooCommunityChest")
        setattr(gameInfo,"countZooCommunityChest",curvalue+1)
        return "pick", "firstDrops"

    chestContent = []
    chestWithoutLandDeed = gameInfo.chestWithoutLandDeed

    # заполняем список всех требущихся материалов в недостровенных зданиях
    currentZooMaterialReqs = FillCurrentOrdersOnlyZoo()

    # Из каждого требования вычитаем колличество материалов имеющихся в амбаре

    x = 0
    for key,value in currentZooMaterialReqs:
        currentZooMaterialReqs[x] = [key,value-getattr(gameInfo,key)]
        if value-getattr(gameInfo,key) < 0: currentZooMaterialReqs[x] = [key,0]
        x += 1

    # Проверяем нужныли в зоопарке обычные материалы для строящихся или не завершенных зданий
    needBuildingMaterial = False
    needBuildingMaterialId = "zooBuildingMaterial"
    _buildingMaterials = []
    if currentZooMaterialReqs:
        for key,value in currentZooMaterialReqs:
            #if value>0: # здесь может подыграться даже если материал не нужен, главное что он есть в активных требованиях
            AddByWeight(_buildingMaterials,key,value+gameInfo.zooLevel)
    if _buildingMaterials:
        needBuildingMaterial = True
        needBuildingMaterialId = GetRandomMaterialOrBrickDef(_buildingMaterials)


    # Заполняет вектор из всех требующихся материалов для улучшения комьюнити в зоопарке
    currentZooUpgradeMaterialsReqs = FillCurrentZooUpgradePrices()

    # Из каждого требования вычитаем колличество материалов имеющихся в амбаре
    x = 0
    for key,value in currentZooUpgradeMaterialsReqs:
        currentZooUpgradeMaterialsReqs[x] = [key,value-getattr(gameInfo,key)]
        if value-getattr(gameInfo,key) < 0: currentZooUpgradeMaterialsReqs[x] = [key,0]
        x += 1

    # Проверяем нужныли в зоопарке материалы для улучшения зданий
    needUpgradeBuildingMaterial = False
    needUpgradeBuildingMaterialId = "zooBuildingMaterial"
    _buildingUpgradeMaterials = []
    if currentZooUpgradeMaterialsReqs:
        for key,value in currentZooUpgradeMaterialsReqs:
            AddByWeight(_buildingUpgradeMaterials,key,value+gameInfo.zooLevel)
    if _buildingUpgradeMaterials:
        needUpgradeBuildingMaterial = True
        needUpgradeBuildingMaterialId = GetRandomMaterialOrBrickDef(_buildingUpgradeMaterials)


    # Проверяем нужны ли материалы на апгрейд амбара (уровень амбара меньше ожидаемого)
    needWarehauseMaterial = False
    needWarehauseMaterialId = "hammerMat"
    if random.randint(1,100) < 20: # имитация проверки - обычный рандом
        _upgradeMaterials = []
        AddByWeight(_upgradeMaterials,"hammerMat",45)
        AddByWeight(_upgradeMaterials,"nailMat",45)
        AddByWeight(_upgradeMaterials,"paintRedMat",45)

        needWarehauseMaterial = True
        needWarehauseMaterialId = GetRandomMaterialOrBrickDef(_upgradeMaterials)


    # Проверяем нужны ли материалы на расширения в зоопарке
    needZooExpandMaterial = False
    needZooExpandMaterialId = "zooLandDeed"

    zoocurrentExpand = gameInfo.zooExpandLevel
    nextExp = zoocurrentExpand+1

    # Если в зоопарке уже нужны материалы для расширени
    if expandReqs[nextExp].zooLandDeed > 0:
        zooLandDeedCount = gameInfo.zooLandDeed
        pickCount = gameInfo.pick
        axeCount = gameInfo.axe
        tntCount = gameInfo.TNT

        zooLandDeedNeeded = expandReqs[nextExp].zooLandDeed - zooLandDeedCount
        pickNeeded = expandReqs[nextExp].pick - pickCount
        axeNeeded = expandReqs[nextExp].axe - axeCount
        tntNeeded = expandReqs[nextExp].TNT - tntCount

        alreadyHelped = False

        if zooLandDeedNeeded > 0 and chestWithoutLandDeed >= 10:
            gameInfo.chestWithoutLandDeed = 0
            return "zooLandDeed", "chestWithoutLandDeed"

        if zooLandDeedNeeded > 1 or (zooLandDeedNeeded == 1 and random.randint(0,100) < 80):
            needZooExpandMaterialId = "zooLandDeed"
            alreadyHelped = True

        if not alreadyHelped or (pickNeeded > 0 and random.randint(0,100) < 50):
            if pickNeeded > 1 or (pickNeeded == 1 and random.randint(0,100) < 70):
                needZooExpandMaterialId = "pick"
                alreadyHelped = True

        if not alreadyHelped and random.randint(0,100) < 90:
            if axeNeeded > 1 or (axeNeeded == 1 and random.randint(0,100) < 70):
                needZooExpandMaterialId = "axe"
                alreadyHelped = True

        if not alreadyHelped and random.randint(0,100) < 80:
            if tntNeeded > 1 or (tntNeeded == 1 and random.randint(0,100) < 70):
                needZooExpandMaterialId = "TNT"
                alreadyHelped = True

        if alreadyHelped: needZooExpandMaterial = True


    # Проверяем нужно ли подыграть по камням
    needGem = False
    needGemId = "gem1"
    needGemResult = GenerateZooCommunityChestGemManipulation(needGemId,needGem)
    needGemId = needGemResult[0]
    needGem = needGemResult[1]
    # если нужно то возвращаем какой камень будет подыгрывать (needGem)




    writeLog("normalSmall","-----------------------------------------------------------------------------------------")

    # needBuildingMaterialId = "Glass"        # test
    # needBuildingMaterial = True             # test
    # Материалы для зданий
    if needBuildingMaterial:
        AddByWeight(chestContent,needBuildingMaterialId,80)
        helped[needBuildingMaterialId] = "buildingmat"
        writeLog("normalSmall","<i>helping with <u>"+needBuildingMaterialId+"</u> for build (weight 80)</i>")
    else:
        if gameInfo.zooLevel < 7: # в коде условие по playerLevel<50
            AddByWeight(chestContent,"Brick",10)
            AddByWeight(chestContent,"Glass",10)
            AddByWeight(chestContent,"Plita",10)
        AddByWeight(chestContent,"zooBuildingMaterial",20)
        AddByWeight(chestContent,"zooServiceMaterial1",10)
        if gameInfo.zooLevel >= 2:
            AddByWeight(chestContent,"zooServiceMaterial2",10)
        if gameInfo.zooLevel >= 4:
            AddByWeight(chestContent,"zooServiceMaterial3",10)


    # needUpgradeBuildingMaterialId = "Glass" # test
    # needUpgradeBuildingMaterial = True      # test
    # Материалы для апгрейдов
    if needUpgradeBuildingMaterial:
        AddByWeight(chestContent,needUpgradeBuildingMaterialId,80)
        helped[needUpgradeBuildingMaterialId] = "upgrademat"
        writeLog("normalSmall","<i>helping with <u>"+needUpgradeBuildingMaterialId+"</u> "
                 "for upgrade (weight 80)</i>")


    # Материалы для амбара
    if needWarehauseMaterial:
        AddByWeight(chestContent,needWarehauseMaterialId,20)
        helped[needWarehauseMaterialId] = "warehousemat"
        writeLog("normalSmall","<i>helping with <u>"+needWarehauseMaterialId+"</u> "
                 "for warehouse upgrade (weight 20)</i>")
    else:
        AddByWeight(chestContent,"hammerMat",3)
        AddByWeight(chestContent,"nailMat",3)
        AddByWeight(chestContent,"paintRedMat",3)


    # Материалы для расширений
    if needZooExpandMaterial:
        AddByWeight(chestContent,needZooExpandMaterialId,45)
        helped[needZooExpandMaterialId] = "expandmat"
        writeLog("normalSmall","<i>helping with <u>"+needZooExpandMaterialId+"</u> "
                 "for expand (weight 45)</i>")
    else:
        if expandReqs[nextExp].zooLandDeed > 0:
            AddByWeight(chestContent,"zooLandDeed",2)
        if expandReqs[nextExp].pick > 0:
            AddByWeight(chestContent,"pick",2)
        if expandReqs[nextExp].axe > 0:
            AddByWeight(chestContent,"axe",2)
        if expandReqs[nextExp].TNT > 0:
            AddByWeight(chestContent,"TNT",1)

    # Камни
    if needGem:
        AddByWeight(chestContent,needGemId,65)
        helped[needGemId] = "needgem"
        writeLog("normalSmall","<i>helping with <u>"+needGemId+"</u> (weight <b>65</b>, from needGem)</i>")
    else:
        _gems = []
        gemId = GetNextGem()
        if gemId:
            AddByWeight(chestContent,gemId,65)
            helped[gemId] = "getnextgem"
            writeLog("normalSmall","<div class='normalSmall'><i>helping with <u>"+gemId+"</u> "
                     "(weight <b>65</b>, from GetNextGem)</i>")
        else:
            AddByWeight(_gems,"gem1",45)
            AddByWeight(_gems,"gem2",21)
            AddByWeight(_gems,"gem3",17)
            AddByWeight(_gems,"gem4",17)
            randomGem = GetRandomMaterialOrBrickDef(_gems)
            AddByWeight(chestContent,randomGem,65) # <<<<<<<<<<<<<<<<<<<<<<<< все равно нехило подыгрывает на камни
            helped[randomGem] = "randomgem"
            writeLog("normalSmall","<div class='normalSmall'><i>helping with <u>"+randomGem+"</u> "
                     "(weight <b>65</b>, from randomGem)</i>")


    randomMat = GetRandomMaterialOrBrickDef(chestContent)
    if randomMat == "zooLandDeed":
        gameInfo.chestWithoutLandDeed = 0
    else:
        zooLandDeedCount = gameInfo.zooLandDeed
        zooLandDeedNeeded = expandReqs[nextExp].zooLandDeed - zooLandDeedCount
        if zooLandDeedNeeded > 0:
            gameInfo.chestWithoutLandDeed += 1
        elif chestWithoutLandDeed > 0:
            gameInfo.chestWithoutLandDeed = 0

    if randomMat in helped:
        wasHelped = helped.get(randomMat)

    # print Counter(chestContent)
    return randomMat, wasHelped


def AnyFamilyReady():
    for curPaddockId in gameInfo.paddocksTotalAnimals:
        if gameInfo.paddocksTotalAnimals[curPaddockId] == 4:
            return True
    return False



def GenerateZooCommunityChestGemManipulation(needGemId,needGem):
    ANY_FAMILY_READY = AnyFamilyReady()
    # Бежим по всем готовым загонам к заселению
    for curReadyPaddock in gameInfo.paddocks:
        if gameInfo.paddocks[curReadyPaddock] == 1:
            levelNeed = buildingSettings[curReadyPaddock].zooLevel
            MAX_LEVEL_FOR_GEM_MANIPULATION = 3
            if random.randint(0,99) < 50: MANIPULATION = True
            else: MANIPULATION = False
            LEVEL_DIFF = 3
            if levelNeed > MAX_LEVEL_FOR_GEM_MANIPULATION:
                continue
            else:
                paddock = curReadyPaddock
                ANIMALS_COUNT = gameInfo.paddocksTotalAnimals[paddock]
                if ANIMALS_COUNT < 4:
                    if levelNeed == 1 and not ANY_FAMILY_READY:
                        differenceGems = GetDiffrenceGemsForNextPaddockAnimal(paddock)
                        if differenceGems:
                            INDX = random.randint(0,len(differenceGems)-1)
                            needGemId = differenceGems[INDX]
                            needGem = True
                            writeLog("smallGrey","need <b>"+needGemId+"</b> for animal #"+str(ANIMALS_COUNT+1)+" "
                                     "in <b>"+paddock+"</b>")
                            return needGemId,needGem
                        else:
                            continue
                    elif gameInfo.zooLevel-levelNeed >= LEVEL_DIFF and MANIPULATION:
                        differenceGems = GetDiffrenceGemsForNextPaddockAnimal(paddock)
                        if differenceGems:
                            INDX = random.randint(0,len(differenceGems)-1)
                            needGemId = differenceGems[INDX]
                            needGem = True
                            writeLog("smallGrey","need <b>"+needGemId+"</b> for animal #"+str(ANIMALS_COUNT+1)+" "
                                     "in <b>"+paddock+"</b>")
                            return needGemId,needGem
                        else:
                            continue
                    elif not MANIPULATION:
                        writeLog("normalSmall","not manipulating gems (random)")
                        return needGemId,needGem
                    else:
                        writeLog("normalSmall","no need to manipulate gems")
                        return needGemId,needGem

    return needGemId,needGem


def GetNextGem():
    foundId = ""
    foundWeight = 0
    defProb = {'gem1':48, 'gem2':27, 'gem3':13, 'gem4':12}
    maxGems = 4
    i = 1
    while i <= maxGems:
        wasnot = gameInfo.wasnot['gem'+str(i)]
        should = 100/defProb['gem'+str(i)]
        if wasnot > should:
            if not foundId or (wasnot/should > foundWeight):
                foundId = "gem"+str(i)
                foundWeight = wasnot/should
        i += 1
    return foundId


def AddGems(gemId):
    maxGems = 4
    i = 1
    while i <= maxGems:
        if gemId == "gem"+str(i):
            gameInfo.wasnot[gemId] = 0
        else:
            gameInfo.wasnot["gem"+str(i)]+=1
        i += 1


def GetDiffrenceGemsForNextPaddockAnimal(paddock):
    nextAnimalNumber = gameInfo.paddocksTotalAnimals[paddock]+1
    price = animalsReqs[paddock][nextAnimalNumber]
    differenceGems = []
    if gameInfo.gem1-price.gem1 < 0:
        differenceGems.append("gem1")
    if gameInfo.gem2-price.gem2 < 0:
        differenceGems.append("gem2")
    if gameInfo.gem3-price.gem3 < 0:
        differenceGems.append("gem3")
    if gameInfo.gem4-price.gem4 < 0:
        differenceGems.append("gem4")
    return differenceGems


def CheckAlreadyBuilt(buildingId):
    if gameInfo.paddocks.get(buildingId) == 1 or gameInfo.communities.get(buildingId) == 1:
        return True
    else:
        return False


def CheckCanBuild(bsettings):
    for mat in buildingMatList:
        if getattr(gameInfo,mat) < getattr(bsettings,mat):
            return False
    return True


def DoBuild(bsettings,buildingId):
    if "paddock_" in buildingId:
        gameInfo.paddocks[buildingId] = 1
        gameInfo.paddocksTotalAnimals[buildingId] = 0
    elif "zoo_" in buildingId:
        gameInfo.communities[buildingId] = 1
    gameInfo.rating += bsettings.bonusRating
    for mat in buildingMatList:
        if getattr(bsettings,mat) > 0:
            setattr(gameInfo, mat, getattr(gameInfo,mat)-getattr(bsettings,mat))


def FindAvailableNotBuilt():
    for key, value in gameInfo.paddocks.items():
        if value == 0:                                                  # еще не построено
            if buildingSettings[key].zooLevel <= gameInfo.zooLevel:     # доступно по уровню
                return key
    for key, value in gameInfo.communities.items():
        if value == 0:                                                  # еще не построено
            if buildingSettings[key].zooLevel <= gameInfo.zooLevel:     # доступно по уровню
                return key
    return False


def GetBuildingReqsLine(ttype,bid,uid):
    reqs = {}
    line = ""
    if ttype == "build":
        for mat in buildingMatList:
            if getattr(buildingSettings[bid], mat) > 0:
                reqs[mat] = getattr(buildingSettings[bid], mat)
    elif ttype == "upgrade":
        for mat in buildingMatList:
            if getattr(upgradesReqs[bid][uid], mat) > 0:
                reqs[mat] = getattr(upgradesReqs[bid][uid], mat)
    i = 0
    for key,value in reqs.iteritems():
        if 0 < i < len(reqs):
            line += ", "
        line = line+key+" "
        if getattr(gameInfo,key) < value:
            line += "<b>"
        line += str(value)
        if getattr(gameInfo,key) < value:
            line += "</b>"
        i += 1
    return line


def DoUpgrade(buildingId,upgradeNum):
    curUpgrade = gameInfo.communitiesUpgrades[buildingId]
    if upgradeNum - curUpgrade == 1: # все ок, это апгрейд на 1
        gameInfo.communitiesUpgrades[buildingId] = upgradeNum
        for mat in buildingMatList:
            if getattr(upgradesReqs[buildingId][upgradeNum], mat) > 0:
                setattr(gameInfo, mat, getattr(gameInfo,mat)-getattr(upgradesReqs[buildingId][upgradeNum],mat))
    else:
        writeLog("lightgree","<font size='+3'>ERROR UPGRADING!</font>")


def FindOldestNotFullPaddock():
    lowestLevel = 666
    lowestLevelId = "n/a"
    for key, value in gameInfo.paddocks.items():
        if value == 1: # на всякий случай
            if gameInfo.paddocksTotalAnimals[key] < 4: # животных меньше 4
                if buildingSettings[key].zooLevel < lowestLevel:
                    lowestLevel = buildingSettings[key].zooLevel
                    lowestLevelId = key
    return [lowestLevelId,lowestLevel]


def TryExpand():
    curExpand = gameInfo.zooExpandLevel
    totalAnimals = sum(gameInfo.paddocksTotalAnimals.itervalues())
    for key, value in enumerate(expandReqs):
        if key <= curExpand: continue
        if value.animals > totalAnimals: break
        if value.zooLandDeed <= gameInfo.zooLandDeed and value.axe <= gameInfo.axe and value.pick <= gameInfo.pick and value.TNT <= gameInfo.TNT:
            # хватает материалов на расширение
            writeLog("normal","<font color='red'>expanding #"+str(key)+" (totalAnimals = "+str(totalAnimals)+")</font>")
            gameInfo.zooExpandLevel += 1
            gameInfo.zooLandDeed -= value.zooLandDeed
            gameInfo.axe -= value.axe
            gameInfo.pick -= value.pick
            gameInfo.TNT -= value.TNT



def TryBuild():
    for key, value in buildingSettings.iteritems():
        if int(value.zooLevel) <= gameInfo.zooLevel:
            if not CheckAlreadyBuilt(value.id):
                if CheckCanBuild(buildingSettings[value.id]):
                    DoBuild(buildingSettings[value.id],value.id)
                    line = "building <b>"+value.id+"</b> &mdash; <small>"
                    for mat in buildingMatList:
                        if getattr(buildingSettings[value.id], mat):
                            line += str(getattr(buildingSettings[value.id],mat))+" <img src='img/"+mat+".png' valign='middle'>&nbsp;"
                    line += "</small>"
                    writeLog("lightgreen",line)
                    return True
    return False


def TryBuyNewAnimal():
    lowestPaddock = FindOldestNotFullPaddock()
    if lowestPaddock[1] != 666:
        paddockName = lowestPaddock[0]
        nextAnimalNumber = gameInfo.paddocksTotalAnimals[paddockName]+1
        if (animalsReqs[paddockName][nextAnimalNumber].gem1 <= gameInfo.gem1) and \
                (animalsReqs[paddockName][nextAnimalNumber].gem2 <= gameInfo.gem2) and \
                (animalsReqs[paddockName][nextAnimalNumber].gem3 <= gameInfo.gem3) and \
                (animalsReqs[paddockName][nextAnimalNumber].gem4 <= gameInfo.gem4):
            gameInfo.paddocksTotalAnimals[paddockName] += 1
            for g in gemsList:
                setattr(gameInfo, g, getattr(gameInfo,g)-getattr(animalsReqs[paddockName][nextAnimalNumber],g))
            line = "buying new animal for <b>"+paddockName+"</b> (#"+str(nextAnimalNumber)+") &mdash; <small>"
            for g in gemsList:
                if getattr(animalsReqs[paddockName][nextAnimalNumber], g):
                    line += str(getattr(animalsReqs[paddockName][nextAnimalNumber], g))+" <img src='img/"+g+".png' " \
                            "valign='middle'>&nbsp;"
            line += "</small>"
            writeLog("orange", line)
            return True # купили животное в самом старом неполном загоне

    # если до этого не купили, то попробуем купить в любом загоне из неполных
    for key,value in gameInfo.paddocksTotalAnimals.iteritems():
        if key in gameInfo.paddocks:
            if value < 4 and gameInfo.paddocks[key] == 1: # загон еще не полный и он точно построен
                nextAnimalNumber = value+1
                paddockName = key
                if (animalsReqs[paddockName][nextAnimalNumber].gem1 <= gameInfo.gem1) and \
                        (animalsReqs[paddockName][nextAnimalNumber].gem2 <= gameInfo.gem2) and \
                        (animalsReqs[paddockName][nextAnimalNumber].gem3 <= gameInfo.gem3) and \
                        (animalsReqs[paddockName][nextAnimalNumber].gem4 <= gameInfo.gem4):
                    gameInfo.paddocksTotalAnimals[paddockName] += 1
                    for g in gemsList:
                        setattr(gameInfo, g, getattr(gameInfo,g)-getattr(animalsReqs[paddockName][nextAnimalNumber],g))

                    line = "buying new animal for <b>"+paddockName+"</b> (#"+str(nextAnimalNumber)+") &mdash; <small>"
                    for g in gemsList:
                        if getattr(animalsReqs[paddockName][nextAnimalNumber], g):
                            line += str(getattr(animalsReqs[paddockName][nextAnimalNumber], g))+ \
                                    "<img src='img/"+g+".png' valign='middle'>&nbsp;"
                    line += "</small>"
                    writeLog("orange", line)
                    return True
    return False