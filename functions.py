# coding=utf-8

import random
from globalvars import *
from collections import Counter
import xml.etree.ElementTree as xml
import numpy as np

def writeLog(divclass,text,gameInfo):
    if FULL_LOG_FOR_LEVEL == 0:
        if gameInfo.zooLevel >= FULL_LOG_FROM_LEVEL:
            f.write("<div class='"+divclass+"'>"+text+"</div>")
    elif gameInfo.zooLevel == FULL_LOG_FOR_LEVEL:
        f.write("<div class='"+divclass+"'>"+text+"</div>")

def writeShortLog(divclass,text):
    fshort.write("<div class='"+divclass+"'>"+text+"</div>")

def writeAvrgLog(divclass,text):
    favrg.write("<div class='"+divclass+"'>"+text+"</div>")

def writeHtmlHead():
    with open("_htmlhead") as fp:
        for line in fp:
            f.write(line)
            fshort.write(line)
            favrg.write(line)

def writeHtmlFoot():
    f.write("<br><br></body></html>")
    fshort.write("<br><br></body></html>")
    favrg.write("<br><br></body></html>")

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
    writeLog("normalSmall",lineToWrite,gameInfo)
    return chestContent[rand]

def FillCurrentOrders(gameInfo):
    curReqs = []
    for key, value in buildingSettings.iteritems():
        canBeBuilt = False
        if int(value.zooLevel) <= gameInfo.zooLevel:
            if "zoo_" in value.id:
                if gameInfo.communities.get(value.id) != 1:
                    canBeBuilt = True
            elif "paddock_" in value.id:
                if gameInfo.paddocks.get(value.id) != 1:
                    canBeBuilt = True
            if canBeBuilt:
                # доступно по уровню и еще не построено
                writeLog("normalSmall","<u>not yet built "+str(value.id)+"</u>",gameInfo)
                for mat in buildingMatList:
                    if getattr(value, mat) > 0:
                        curReqs.append([mat, getattr(value, mat)])

    return curReqs


def CompareForZooMats(buildId, upgradeId, upgradeNum, gameInfo):
    # сравним требования на строительство здания buildId с требованиями апгрейда #upgradeNum здания upgradeId
    # на предмет наличия общих требований по зоо-материалам
    for mat in zooBuildingMatList:
        if getattr(buildingSettings[buildId],mat):
            if getattr(upgradesReqs[upgradeId][upgradeNum],mat) > 0:
                # отсечем случаи, когда совпадающий материал по количеству требуется намного больше - в таких случаях не будем ждать
                matUp = getattr(upgradesReqs[upgradeId][upgradeNum],mat)
                matBuild = getattr(buildingSettings[buildId],mat)
                CONST = 4
                if gameInfo.zooLevel<5: CONST = 6
                if matBuild/matUp < CONST:
                    line = GetBuildingReqsLine("build",buildId,0,gameInfo)
                    writeLog("normalSmall","upgrade has same requirements for zoo mats as pending construction of "+buildId+" ("+line+") - lets wait then",gameInfo)
                    return True
    writeLog("normalSmall","upgrade has different reqs, can update",gameInfo)
    return False


def FillCurrentZooUpgradePrices(gameInfo):
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
                        for mat in zooBuildingMatList:
                            if getattr(upSettings, mat) > 0:
                                curReqs.append([mat, getattr(upSettings, mat)])
                        reqsLine = GetBuildingReqsLine("upgrade",key,upNum,gameInfo)
                        writeLog("normalSmall","<i>upgrade #"+str(upNum)+
                                    " is available for "+key+" ("+reqsLine+")",gameInfo)

    return curReqs


def FindUpdateToBuy(gameInfo):
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
                            break
    return False


def CheckZooCommunityIsReady(commId,gameInfo):
    # фейк, проверяет всего лишь доступность комьюнити по уровню, а не "готово" ли оно
    zooLevel = gameInfo.zooLevel
    if buildingSettings[commId].zooLevel <= zooLevel:
        return True
    else:
        return False


def GenerateZooCommunityChestContent(gameInfo):

    helped = {}
    wasHelped = "no"

    playerLevel = gameInfo.playerLevel
    zooLevel = gameInfo.zooLevel
    isSurplusGem = IsSurplusGems(gameInfo)

    _zooCommunityChestContent = []
    chestWithoutLandDeed = gameInfo.chestWithoutLandDeed
    countZooCommunityChest = gameInfo.countZooCommunityChest

    if countZooCommunityChest == 0:
        curvalue = getattr(gameInfo,"countZooCommunityChest")
        setattr(gameInfo,"countZooCommunityChest",curvalue+1)
        return "zooBuildingMaterial", "firstDrops"
    elif countZooCommunityChest == 1:
        curvalue = getattr(gameInfo,"countZooCommunityChest")
        setattr(gameInfo,"countZooCommunityChest",curvalue+1)
        return "zooServiceMaterial2", "firstDrops"
    elif countZooCommunityChest == 2:
        curvalue = getattr(gameInfo,"countZooCommunityChest")
        setattr(gameInfo,"countZooCommunityChest",curvalue+1)
        return "zooBuildingMaterial", "firstDrops"
    elif countZooCommunityChest == 3:
        curvalue = getattr(gameInfo,"countZooCommunityChest")
        setattr(gameInfo,"countZooCommunityChest",curvalue+1)
        return "pick", "firstDrops"

    # //Заполняет вектор из всех требующихся материалов в строящихся и не завершенных комьюнити в зоопарке + загоны тоже
    currentZooMaterialReqs = FillCurrentOrders(gameInfo)

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
            if (key == "zooServiceMaterial3" and not CheckZooCommunityIsReady("zoo_cinema",gameInfo)) or (key == "zooServiceMaterial2" and not CheckZooCommunityIsReady("zoo_icecream_shop",gameInfo) and gameInfo.zooServiceMaterial2 >= 9):
                # print "костыль, не выдаем этот материал пока не достроим комьюнити"
                aa = 0
            else:
                AddByWeight(_buildingMaterials,key,value+zooLevel)
    if _buildingMaterials:
        needBuildingMaterial = True
        needBuildingMaterialId = GetRandomMaterialOrBrickDef(_buildingMaterials)
    # else:
    #    print "NO NEED FOR BUILDING MATERIALS! :("

    # Заполняет вектор из всех требующихся материалов для улучшения комьюнити в зоопарке
    currentZooUpgradeMaterialsReqs = FillCurrentZooUpgradePrices(gameInfo)

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
            if key == "zooServiceMaterial2" and not CheckZooCommunityIsReady("zoo_icecream_shop",gameInfo) and gameInfo.zooServiceMaterial2 >= 9:
                # print "костыль, не выдаем этот материал пока не достроим комьюнити"
                aa = 0
            else:
                AddByWeight(_buildingUpgradeMaterials,key,value+zooLevel)
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
    if nextExp in expandReqs:
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

            if alreadyHelped:
                needZooExpandMaterial = True


    # Проверяем нужно ли подыграть по камням
    needGem = False
    needGemId = "gem1"
    # Проверяем нужно ли подыгрывать по камням (needGemId), если нужно то возвращаем какой камень будет подыгрывать (needGem)
    needGemResult = GenerateZooCommunityChestGemManipulation(needGemId,needGem,gameInfo)
    needGemId = needGemResult[0]
    needGem = needGemResult[1]

    writeLog("normalSmall","-----------------------------------------------------------------------------------------",gameInfo)

    # Материалы для зданий
    if needBuildingMaterial:
        AddByWeight(_zooCommunityChestContent,needBuildingMaterialId,80)
        helped[needBuildingMaterialId] = "buildingmat"
        writeLog("normalSmall","<i>helping with <u>"+needBuildingMaterialId+"</u> for build (weight 80)</i>",gameInfo)
    else:
        # print "needBuildingMaterial FALSE!!!!!!!!!!!!!!!!!!!!!"
        if zooLevel < 7: # в коде условие по playerLevel<50
            AddByWeight(_zooCommunityChestContent,"Brick",10)
            AddByWeight(_zooCommunityChestContent,"Glass",10)
            AddByWeight(_zooCommunityChestContent,"Plita",10)
        AddByWeight(_zooCommunityChestContent,"zooBuildingMaterial",20)
        AddByWeight(_zooCommunityChestContent,"zooServiceMaterial1",10)
        if zooLevel >= 2:
            if CheckZooCommunityIsReady("zoo_icecream_shop",gameInfo) or (not CheckZooCommunityIsReady("zoo_icecream_shop",gameInfo) and gameInfo.zooServiceMaterial2 < 9):
                # или icecream_shop уже доступен для строительства, или недоступен но zSM2 меньше 9 - значит можно его выдавать
                AddByWeight(_zooCommunityChestContent,"zooServiceMaterial2",10)
        if zooLevel >= 4 and CheckZooCommunityIsReady("zoo_cinema",gameInfo):
            # cinema доступен для строительства - можно выдавать zSM3
            AddByWeight(_zooCommunityChestContent,"zooServiceMaterial3",10)


    # Материалы для апгрейдов
    if needUpgradeBuildingMaterial:
        AddByWeight(_zooCommunityChestContent,needUpgradeBuildingMaterialId,80)
        helped[needUpgradeBuildingMaterialId] = "upgrademat"
        writeLog("normalSmall","<i>helping with <u>"+needUpgradeBuildingMaterialId+"</u> "
                 "for upgrade (weight 80)</i>",gameInfo)


    # Материалы для амбара
    if needWarehauseMaterial:
        AddByWeight(_zooCommunityChestContent,needWarehauseMaterialId,20)
        helped[needWarehauseMaterialId] = "warehousemat"
        writeLog("normalSmall","<i>helping with <u>"+needWarehauseMaterialId+"</u> "
                 "for warehouse upgrade (weight 20)</i>",gameInfo)
    else:
        AddByWeight(_zooCommunityChestContent,"hammerMat",3)
        AddByWeight(_zooCommunityChestContent,"nailMat",3)
        AddByWeight(_zooCommunityChestContent,"paintRedMat",3)


    # Материалы для расширений
    if needZooExpandMaterial:
        AddByWeight(_zooCommunityChestContent,needZooExpandMaterialId,45)
        helped[needZooExpandMaterialId] = "expandmat"
        writeLog("normalSmall","<i>helping with <u>"+needZooExpandMaterialId+"</u> "
                 "for expand (weight 45)</i>",gameInfo)
    else:
        if expandReqs[nextExp].zooLandDeed > 0:
            AddByWeight(_zooCommunityChestContent,"zooLandDeed",2)
        if expandReqs[nextExp].pick > 0:
            AddByWeight(_zooCommunityChestContent,"pick",2)
        if expandReqs[nextExp].axe > 0:
            AddByWeight(_zooCommunityChestContent,"axe",2)
        if expandReqs[nextExp].TNT > 0:
            AddByWeight(_zooCommunityChestContent,"TNT",1)

    # Камни
    if needGem:
        AddByWeight(_zooCommunityChestContent,needGemId,65)
        helped[needGemId] = "needgem"
        writeLog("normalSmall","<i>helping with <u>"+needGemId+"</u> (weight <b>65</b>, from needGem)</i>",gameInfo)
    else:
        # _gems = []
        gemId = GetNextGem(gameInfo)
        gemWeight = 30
        if isSurplusGem:
            gemWeight = 10
        if gemId:
            AddByWeight(_zooCommunityChestContent,gemId,gemWeight)
            helped[gemId] = "getnextgem"
            writeLog("normalSmall","<div class='normalSmall'><i>helping with <u>"+gemId+"</u> "
                     "(weight <b>"+str(gemWeight)+"</b>, from GetNextGem)</i>",gameInfo)
        else:
            _gems = GetGemsWithCorrectionWeight(45,21,17,17,gameInfo)
            gemId = GetRandomMaterialOrBrickDef(_gems)
            AddByWeight(_zooCommunityChestContent,gemId,gemWeight)
            helped[gemId] = "randomgem"
            writeLog("normalSmall","<div class='normalSmall'><i>helping with <u>"+gemId+"</u> "
                     "(weight <b>"+str(gemWeight)+"</b>, from randomGem)</i>",gameInfo)


    randomMat = GetRandomMaterialOrBrickDef(_zooCommunityChestContent)
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


def GetGemsWithCorrectionWeight(weight_1,weight_2,weight_3,weight_4,gameInfo):
    # Самоцветы с весами
    gemsWeight = {'gem1':weight_1, 'gem2':weight_2, 'gem3':weight_3, 'gem4':weight_4}

    # Каких и сколько самоцветов у нас есть
    gemsCount = {'gem1':gameInfo.gem1, 'gem2':gameInfo.gem2, 'gem3':gameInfo.gem3, 'gem4':gameInfo.gem4}

    # Ищем минимальное и максимальное кол-во самоцветов
    mini = min(gemsCount, key=gemsCount.get)
    maxi = max(gemsCount, key=gemsCount.get)
    mini = float(getattr(gameInfo,mini))
    maxi = float(getattr(gameInfo,maxi))
    if mini == 0:
        mini = 1.0

    if maxi/mini > 5.0:
        allGemsCount = 0
        for key,value in gemsCount.iteritems():
            allGemsCount += value
        for key,value in gemsCount.iteritems():
            # Процентная доля от общего
            percentage = (value/float(allGemsCount))*100.0
            id = key

            # Если разница меньше то увеличиваем, если разница больше, то уменьшаем
            gemsWeight[id] -= percentage - gemsWeight[id]
            if gemsWeight[id] < 1:
                gemsWeight[id] = 1

    _gemsCorrected = []
    for key,value in gemsWeight.iteritems():
        curweight = int(value)
        AddByWeight(_gemsCorrected,key,int(curweight))

    return _gemsCorrected


def IsSurplusGems(gameInfo):
    zooLevel = gameInfo.zooLevel
    res = True
    find = False
    gem1_count = gameInfo.gem1
    gem2_count = gameInfo.gem2
    gem3_count = gameInfo.gem3
    gem4_count = gameInfo.gem4
    for gl in gemLimitRanges:
        if gl.fromZooLevel <= zooLevel and gl.toZooLevel >= zooLevel:
            res = res and gem1_count >= gl.gem1
            res = res and gem2_count >= gl.gem2
            res = res and gem3_count >= gl.gem3
            res = res and gem4_count >= gl.gem4
            find = True
            break

    if not find:
        print "Неучтенный отрезок уровней в лимите камней"
        return False

    return res


def AnyFamilyReady(gameInfo):
    for curPaddockId in gameInfo.paddocksTotalAnimals:
        if gameInfo.paddocksTotalAnimals[curPaddockId] == 4:
            return True
    return False


def GenerateZooCommunityChestGemManipulation(needGemId,needGem,gameInfo):
    ANY_FAMILY_READY = AnyFamilyReady(gameInfo)
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
                        differenceGems = GetDiffrenceGemsForNextPaddockAnimal(paddock,gameInfo)
                        if differenceGems:
                            INDX = random.randint(0,len(differenceGems)-1)
                            needGemId = differenceGems[INDX]
                            needGem = True
                            writeLog("smallGrey","need <b>"+needGemId+"</b> for animal #"+str(ANIMALS_COUNT+1)+" "
                                     "in <b>"+paddock+"</b>",gameInfo)
                            return needGemId,needGem
                        else:
                            continue
                    elif gameInfo.zooLevel-levelNeed >= LEVEL_DIFF and MANIPULATION:
                        differenceGems = GetDiffrenceGemsForNextPaddockAnimal(paddock,gameInfo)
                        if differenceGems:
                            INDX = random.randint(0,len(differenceGems)-1)
                            needGemId = differenceGems[INDX]
                            needGem = True
                            writeLog("smallGrey","need <b>"+needGemId+"</b> for animal #"+str(ANIMALS_COUNT+1)+" "
                                     "in <b>"+paddock+"</b>",gameInfo)
                            return needGemId,needGem
                        else:
                            continue
                    elif not MANIPULATION:
                        writeLog("normalSmall","not manipulating gems (random)",gameInfo)
                        return needGemId,needGem
                    else:
                        writeLog("normalSmall","no need to manipulate gems",gameInfo)
                        return needGemId,needGem

    return needGemId,needGem


def GetNextGem(gameInfo):
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


def AddGems(gemId,increment,gameInfo):
    i = 1
    while i <= 4:
        if gemId == "gem"+str(i):
            gameInfo.wasnot[gemId] = 0
        else:
            gameInfo.wasnot["gem"+str(i)]+=1
        i += 1
    if increment: gameInfo.gemsFromZoo += 1


def CalcBuildingCompletePercent(buildingId,gameInfo):
    curLevel = gameInfo.zooLevel
    curRating = gameInfo.rating
    buildingUnlockLevel = buildingSettings[buildingId].zooLevel
    ratingToUnlockLevel = ratingToLevelup[buildingUnlockLevel]
    ratingToNextLevel = ratingToLevelup[buildingUnlockLevel+1]
    ratingBetween = ratingToNextLevel-ratingToUnlockLevel
    ratingOnLevel = curRating-ratingToUnlockLevel

    if buildingUnlockLevel <= curLevel:
        percent = int(round((float(ratingOnLevel)/float(ratingBetween))*100.0,0))
    # elif buildingUnlockLevel < curLevel:
    #     percent = "100+"
    else:
        percent = "error"

    return percent



def AddExtraGems(source,gameInfo):
    # берем или соответствующее уровню значение или последнее из массива рейтов
    if gameInfo.zooLevel < len(extraGemsRate[source]):
        levelRate = extraGemsRate[source][gameInfo.zooLevel]
    else:
        levelRate = extraGemsRate[source][len(extraGemsRate[source])]

    # высчитываем текущий фактический рейт или ставим его в 0
    if gameInfo.gemsFromZoo > 0: curRate = float(getattr(gameInfo,"gemsFrom"+source))/float(gameInfo.gemsFromZoo)
    else: curRate = 0

    if curRate < levelRate and gameInfo.gemsFromZoo > 0:
        # нужно добавить камень
        _gems = GetGemsWithCorrectionWeight(45,21,17,17,gameInfo)
        gemId = GetRandomMaterialOrBrickDef(_gems)

        writeLog("normalSmall", "<font color='red'>curRate < levelRate"
                              " ("+str(getattr(gameInfo,"gemsFrom"+source))+"/"+str(gameInfo.gemsFromZoo)+" < "+str(levelRate)+") "
                              "giving "+gemId+" from "+source+"!</font>",gameInfo)

        setattr(gameInfo,gemId,getattr(gameInfo,gemId)+1)
        AddGems(gemId,False,gameInfo)
        setattr(gameInfo,"gemsFrom"+source,getattr(gameInfo,"gemsFrom"+source)+1)
        if gemId not in gameInfo.extraGems:
            gameInfo.extraGems[gemId] = 1
        else:
            gameInfo.extraGems[gemId] += 1

    else:
        writeLog("normalSmall", "<font color='red'>curRate > levelRate"
                              " ("+str(getattr(gameInfo,"gemsFrom"+source))+"/"+str(gameInfo.gemsFromZoo)+" > "+str(levelRate)+")</font>",gameInfo)


def AddExtraMaterials(gameInfo):
    # берем или соответствующее уровню значение или последнее из массива рейтов
    if gameInfo.zooLevel < len(extraZooMatsRate):
        levelRate = extraZooMatsRate[gameInfo.zooLevel]
    else:
        levelRate = extraZooMatsRate[len(extraZooMatsRate)]

    # высчитываем текущий фактический рейт или ставим его в 0
    if gameInfo.materialsFromZoo > 0: curRate = float(getattr(gameInfo,"extraMaterials"))/float(gameInfo.materialsFromZoo)
    else: curRate = 0

    # if gameInfo.zooChestCounter % 10 == 0 and gameInfo.Brick<300 and gameInfo.Glass<300 and gameInfo.Plita<300:
    #     gameInfo.Brick += random.randint(2,4)
    #     gameInfo.Glass += random.randint(2,4)
    #     gameInfo.Plita += random.randint(2,4)

    if curRate < levelRate and gameInfo.materialsFromZoo > 0:
        # нужно добавить материал
        _mats = []
        AddByWeight(_mats,"zooBuildingMaterial",155)
        AddByWeight(_mats,"zooServiceMaterial1",100)
        AddByWeight(_mats,"zooServiceMaterial2",100)
        AddByWeight(_mats,"zooServiceMaterial3",100)
        AddByWeight(_mats,"zooLandDeed",40)
        matId = GetRandomMaterialOrBrickDef(_mats)

        writeLog("normalSmall", "<font color='red'>materials curRate < levelRate"
                              " ("+str(getattr(gameInfo,"extraMaterials"))+"/"+str(gameInfo.materialsFromZoo)+" < "+str(levelRate)+") "
                              "giving "+matId+"!</font>",gameInfo)

        setattr(gameInfo,matId,getattr(gameInfo,matId)+1)
        setattr(gameInfo,"extraMaterials",getattr(gameInfo,"extraMaterials")+1)
        if matId not in gameInfo.extraMats:
            gameInfo.extraMats[matId] = 1
        else:
            gameInfo.extraMats[matId] += 1

    else:
        writeLog("normalSmall", "<font color='red'>materials curRate > levelRate"
                              " ("+str(getattr(gameInfo,"extraMaterials"))+"/"+str(gameInfo.materialsFromZoo)+" > "+str(levelRate)+")</font>",gameInfo)


def GetDiffrenceGemsForNextPaddockAnimal(paddock,gameInfo):
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


def CheckAlreadyBuilt(buildingId,gameInfo):
    if gameInfo.paddocks.get(buildingId) == 1 or gameInfo.communities.get(buildingId) == 1:
        return True
    else:
        return False


def CheckCanBuild(bsettings,gameInfo):
    for mat in buildingMatList:
        if getattr(gameInfo,mat) < getattr(bsettings,mat):
            return False
    return True


def DoBuild(bsettings,buildingId,gameInfo):
    percent = CalcBuildingCompletePercent(buildingId,gameInfo)
    if "paddock_" in buildingId:
        gameInfo.paddocks[buildingId] = 1
        gameInfo.paddocksTotalAnimals[buildingId] = 0
        gameInfo.paddocksCompletePercent[buildingId] = percent
    elif "zoo_" in buildingId:
        gameInfo.communities[buildingId] = 1
        gameInfo.communitiesCompletePercent[buildingId] = percent
    gameInfo.rating += bsettings.bonusRating
    for mat in buildingMatList:
        if getattr(bsettings,mat) > 0:
            setattr(gameInfo, mat, getattr(gameInfo,mat)-getattr(bsettings,mat))


def FindAvailableNotBuilt(gameInfo):
    for key, value in gameInfo.paddocks.items():
        if value == 0:                                                  # еще не построено
            if buildingSettings[key].zooLevel <= gameInfo.zooLevel:     # доступно по уровню
                return key
    for key, value in gameInfo.communities.items():
        if value == 0:                                                  # еще не построено
            if buildingSettings[key].zooLevel <= gameInfo.zooLevel:     # доступно по уровню
                return key
    return False


def GetBuildingReqsLine(ttype,bid,uid,gameInfo):
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


def DoUpgrade(buildingId,upgradeNum,gameInfo):
    curUpgrade = gameInfo.communitiesUpgrades[buildingId]
    if upgradeNum - curUpgrade == 1: # все ок, это апгрейд на 1
        gameInfo.communitiesUpgrades[buildingId] = upgradeNum
        for mat in buildingMatList:
            if getattr(upgradesReqs[buildingId][upgradeNum], mat) > 0:
                setattr(gameInfo, mat, getattr(gameInfo,mat)-getattr(upgradesReqs[buildingId][upgradeNum],mat))
    else:
        writeLog("lightgree","<font size='+3'>ERROR UPGRADING!</font>",gameInfo)


def FindOldestNotFullPaddock(gameInfo):
    lowestLevel = 666
    lowestLevelId = "n/a"
    for key, value in gameInfo.paddocks.items():
        if value == 1: # на всякий случай
            if gameInfo.paddocksTotalAnimals[key] < 4: # животных меньше 4
                if buildingSettings[key].zooLevel < lowestLevel:
                    lowestLevel = buildingSettings[key].zooLevel
                    lowestLevelId = key
    return [lowestLevelId,lowestLevel]


def TryExpand(gameInfo):
    curExpand = gameInfo.zooExpandLevel
    totalAnimals = sum(gameInfo.paddocksTotalAnimals.itervalues())
    for key, value in enumerate(expandReqs):
        if key <= curExpand: continue
        if value.animals > totalAnimals: break
        if value.zooLandDeed <= gameInfo.zooLandDeed and value.axe <= gameInfo.axe and value.pick <= gameInfo.pick and value.TNT <= gameInfo.TNT:
            # хватает материалов на расширение
            writeLog("normal","<font color='red'>expanding #"+str(key)+" (totalAnimals = "+str(totalAnimals)+")</font>",gameInfo)
            gameInfo.zooExpandLevel += 1
            gameInfo.zooLandDeed -= value.zooLandDeed
            gameInfo.axe -= value.axe
            gameInfo.pick -= value.pick
            gameInfo.TNT -= value.TNT


def TryBuild(gameInfo):
    for key, value in buildingSettings.iteritems():
        if int(value.zooLevel) <= gameInfo.zooLevel:
            if not CheckAlreadyBuilt(value.id,gameInfo):
                if CheckCanBuild(buildingSettings[value.id],gameInfo):
                    DoBuild(buildingSettings[value.id],value.id,gameInfo)
                    if "paddock" in value.id:
                        percent = gameInfo.paddocksCompletePercent[value.id]
                    elif "zoo" in value.id:
                        percent = gameInfo.communitiesCompletePercent[value.id]
                    line = "building <b>"+value.id+"</b> ("+str(percent)+"%) &mdash; <small>"
                    for mat in buildingMatList:
                        if getattr(buildingSettings[value.id], mat):
                            line += str(getattr(buildingSettings[value.id],mat))+" <img src='img/"+mat+".png' valign='middle'>&nbsp;"
                    line += "</small>"
                    writeLog("lightgreen",line,gameInfo)
                    return True
    return False


def TryBuyNewAnimal(gameInfo):
    lowestPaddock = FindOldestNotFullPaddock(gameInfo)
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
            writeLog("orange", line,gameInfo)
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
                    writeLog("orange", line,gameInfo)
                    return True
    return False