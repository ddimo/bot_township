# coding=utf-8

import random
from classes import *
from collections import Counter
import xml.etree.ElementTree as xml
from os.path import expanduser

def writeHtmlHead(f):
    with open("_htmlhead") as fp:
        for line in fp:
            f.write(line)

def writeHtmlFoot(f):
    f.write("<br><br></body></html>")

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

def GetRandomMaterialOrBrickDef(f,chestContent):
    chestContentLen = len(chestContent)
    rand = random.randint(0,chestContentLen-1)
    counter = Counter(chestContent)
    f.write("<div class='normalSmall'><i>current helping weights: ")
    for key, value in counter.iteritems():
        f.write(key+": "+str(value)+", ")
    f.write("</i> --- result: <u>"+chestContent[rand]+"</u></div>")
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


def GenerateZooCommunityChestContent(f,gameInfo,buildingSettings,animalsReqs):

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

    # заполняем список всех требущихся материалов в недостровенных зданиях
    currentZooMaterialReqs = FillCurrentOrdersOnlyZoo(gameInfo,buildingSettings)

    # Из каждого требования вычитаем колличество материалов имеющихся в амбаре

    # f.write("<div class='normalSmall'>currentZooMaterialReqs before decrementing:<br> ")
    # for key,value in currentZooMaterialReqs:
    #     f.write(key+": "+str(value)+", ")
    x = 0
    for key,value in currentZooMaterialReqs:
        currentZooMaterialReqs[x] = [key,value-getattr(gameInfo,key)]
        if value-getattr(gameInfo,key) < 0: currentZooMaterialReqs[x] = [key,0]
        x = x+1
    # f.write("<br>after:<br>")
    # for key,value in currentZooMaterialReqs:
    #     f.write(key+": "+str(value)+", ")
    # f.write("<br><br></div>")

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
        needBuildingMaterialId = GetRandomMaterialOrBrickDef(f,_buildingMaterials)


    # Заполняет вектор из всех требующихся материалов для улучшения комьюнити в зоопарке
    # Проверяем нужныли в зоопарке материалы для улучшения зданий

    # Проверяем нужны ли материалы на апгрейд амбара (уровень амбара меньше ожидаемого)

    # Проверяем нужны ли материалы на расширения в зоопарке
    # Если в зоопарке уже нужны материалы для расширени


    # Проверяем нужно ли подыграть по камням
    needGem = False
    needGemId = "gem1"
    needGemResult = GenerateZooCommunityChestGemManipulation(f,gameInfo,buildingSettings,animalsReqs,needGemId,needGem)
    needGemId = needGemResult[0]
    needGem = needGemResult[1]
    # если нужно то возвращаем какой камень будет подыгрывать (needGem)



    # Материалы для зданий
    if needBuildingMaterial:
        AddByWeight(chestContent,needBuildingMaterialId,80)
        print "adding "+needBuildingMaterialId+" with weight 80"
        helped[needBuildingMaterialId] = "buildingmat"
        f.write("<div class='normalSmall'><i>helping with <u>"+needBuildingMaterialId+"</u> (weight 80)</i></div>")
    else:
        AddByWeight(chestContent,"Brick",10)
        AddByWeight(chestContent,"Glass",10)
        AddByWeight(chestContent,"Plita",10)
        AddByWeight(chestContent,"zooBuildingMaterial",20)
        AddByWeight(chestContent,"zooServiceMaterial1",10)
        if gameInfo.zooLevel >= 2:
            AddByWeight(chestContent,"zooServiceMaterial2",10)
        if gameInfo.zooLevel >= 4:
            AddByWeight(chestContent,"zooServiceMaterial3",10)

    # Материалы для апгрейдов

    # Материалы для амбара
    AddByWeight(chestContent,"hammerMat",3)
    AddByWeight(chestContent,"nailMat",3)
    AddByWeight(chestContent,"paintRedMat",3)

    # Материалы для расширений
    AddByWeight(chestContent,"zooLandDeed",2)
    AddByWeight(chestContent,"pick",2)
    AddByWeight(chestContent,"axe",2)
    AddByWeight(chestContent,"TNT",1)

    # Камни
    if needGem:
        AddByWeight(chestContent,needGemId,65)
        helped[needGemId] = "needgem"
        print "!!!!!!!!!!!!!!!!!!! adding "+needGemId+" with weight 65"
        f.write("<div class='normalSmall'><i>helping with <u>"+needGemId+"</u> (weight <b>65</b>, from needGem)</i></div>")
    else:
        chestGemContent = []
        gemId = GetNextGem(f,gameInfo,animalsReqs)
        if gemId:
            AddByWeight(chestContent,gemId,65)
            helped[gemId] = "getnextgem"
            print "adding "+gemId+" with weight 65 from GetNextGem"
            f.write("<div class='normalSmall'><i>helping with <u>"+gemId+"</u> (weight <b>65</b>, from GetNextGem)</i></div>")
        else:
            AddByWeight(chestGemContent,"gem1",45)
            AddByWeight(chestGemContent,"gem2",21)
            AddByWeight(chestGemContent,"gem3",17)
            AddByWeight(chestGemContent,"gem4",17)
            randomGem = GetRandomMaterialOrBrickDef(f,chestGemContent)
            AddByWeight(chestContent,randomGem,65) # <<<<<<<<<<<<<<<<<<<<<<<<,, все равно нехило подыгрывает на камни
            helped[randomGem] = "randomgem"
            print "adding "+randomGem+" with weight 65 without helping"
            f.write("<div class='normalSmall'><i>helping with <u>"+randomGem+"</u> (weight <b>65</b>, from randomGem)</i></div>")


    randomMat = GetRandomMaterialOrBrickDef(f,chestContent)
    if randomMat in helped:
        wasHelped = helped.get(randomMat)

    # print Counter(chestContent)

    return randomMat, wasHelped


def AnyFamilyReady(gameInfo):
    for curPaddockId in gameInfo.paddocksTotalAnimals:
        if gameInfo.paddocksTotalAnimals[curPaddockId] == 4:
            return True
    return False



def GenerateZooCommunityChestGemManipulation(f,gameInfo,buildingSettings,animalsReqs,needGemId,needGem):
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
                        differenceGems = GetDiffrenceGemsForNextPaddockAnimal(gameInfo,buildingSettings,animalsReqs,paddock)
                        if differenceGems:
                            INDX = random.randint(0,len(differenceGems)-1)
                            needGemId = differenceGems[INDX]
                            needGem = True
                            print "gem manipulation worked for #"+str(ANIMALS_COUNT+1)+" animal in "+paddock
                            f.write("<div class='smallGrey'>need <b>"+needGemId+"</b> for animal #"+str(ANIMALS_COUNT+1)+" in <b>"+paddock+"</b></div>")
                            return needGemId,needGem
                        else:
                            continue
                    elif (gameInfo.zooLevel-levelNeed >= LEVEL_DIFF and MANIPULATION):
                        differenceGems = GetDiffrenceGemsForNextPaddockAnimal(gameInfo,buildingSettings,animalsReqs,paddock)
                        if differenceGems:
                            INDX = random.randint(0,len(differenceGems)-1)
                            needGemId = differenceGems[INDX]
                            needGem = True
                            print "gem manipulation worked for "+str(ANIMALS_COUNT+1)+"animal in "+paddock
                            f.write("<div class='smallGrey'>need <b>"+needGemId+"</b> for animal #"+str(ANIMALS_COUNT+1)+" in <b>"+paddock+"</b></div>")
                            return needGemId,needGem
                        else:
                            continue
                    elif not MANIPULATION:
                        print "gem manipulation failed due to random"
                        f.write("<div class='normalSmall'>not manipulating gems (random)</div>")
                        return needGemId,needGem
                    else:
                        print "gem manipulation just failed"
                        f.write("<div class='normalSmall'>no need to manipulate gems</div>")
                        return needGemId,needGem

    return needGemId,needGem


def GetNextGem(f,gameInfo,animalsReqs):
    gems = [gameInfo.gem1,gameInfo.gem2,gameInfo.gem3,gameInfo.gem4]
    foundId = ""
    foundWeight = 0
    defProb = {'gem1':48, 'gem2':27, 'gem3':13, 'gem4':12}
    maxGems = 4
    i = 1
    # f.write("<div class='normalSmall'><br>GetNextGem:<br>")

    while i <= maxGems:
        wasnot = gameInfo.wasnot['gem'+str(i)]
        # f.write("gem"+str(i)+" wasnot = "+str(wasnot)+"<br>")
        should = 100/defProb['gem'+str(i)]
        if wasnot > should:
            if not foundId or (wasnot/should > foundWeight):
                foundId = "gem"+str(i)
                foundWeight = wasnot/should
        i = i+1

    # f.write("<br></div>")
    return foundId


def AddGems(f,gameInfo,gemId):
    maxGems = 4
    i = 1
    # f.write("<div class='normalSmall'><br>AddGems with "+gemId+":<br>")
    while i <= maxGems:
        var = "wasnot_gem"+str(i)
        if gemId == "gem"+str(i):
            gameInfo.wasnot[gemId] = 0
            # f.write("gem"+str(i)+" wasnot set to 0<br>")
        else:
            gameInfo.wasnot["gem"+str(i)]+=1
            # f.write("gem"+str(i)+" wasnot incremented - new is "+str(gameInfo.wasnot['gem'+str(i)])+"<br>")
        i = i+1
    # f.write("<br></div>")

def GetDiffrenceGemsForNextPaddockAnimal(gameInfo,buildingSettings,animalsReqs,paddock):
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
        # print key,value
        if value == 1: # на всякий случай
            if gameInfo.paddocksTotalAnimals[key] < 4: # животных меньше 4
                if buildingSettings[key].zooLevel < lowestLevel:
                    lowestLevel = buildingSettings[key].zooLevel
                    lowestLevelId = key

    return [lowestLevelId,lowestLevel]


def TryBuild (f,gameInfo,buildingSettings):
    print "<<< lets try to build something"
    for key, value in buildingSettings.iteritems():
        if int(value.zooLevel) <= gameInfo.zooLevel:
            if not CheckAlreadyBuilt(gameInfo,value.id):
                if CheckCanBuild(gameInfo,buildingSettings[value.id],value.id):
                    DoBuild(gameInfo,buildingSettings[value.id],value.id)
                    print ">>> !!!!!!! enough materials to build "+value.id+", done!"

                    f.write("<div class='lightgreen'>")
                    f.write("building <b>"+value.id+"</b> &mdash; <small>")

                    if buildingSettings[value.id].Brick:
                        f.write(str(buildingSettings[value.id].Brick)+" <img src='img/Brick.png' valign='middle'>&nbsp;")
                    if buildingSettings[value.id].Plita:
                        f.write(str(buildingSettings[value.id].Plita)+" <img src='img/Plita.png' valign='middle'>&nbsp;")
                    if buildingSettings[value.id].Glass:
                        f.write(str(buildingSettings[value.id].Glass)+" <img src='img/Glass.png' valign='middle'>&nbsp;")

                    if buildingSettings[value.id].zooBuildingMaterial:
                        f.write(str(buildingSettings[value.id].zooBuildingMaterial)+" <img src='img/zooBuildingMaterial.png' valign='middle'>&nbsp;")
                    if buildingSettings[value.id].zooServiceMaterial1:
                        f.write(str(buildingSettings[value.id].zooServiceMaterial1)+" <img src='img/zooServiceMaterial1.png' valign='middle'>&nbsp;")
                    if buildingSettings[value.id].zooServiceMaterial2:
                        f.write(str(buildingSettings[value.id].zooServiceMaterial2)+" <img src='img/zooServiceMaterial2.png' valign='middle'>&nbsp;")
                    if buildingSettings[value.id].zooServiceMaterial3:
                        f.write(str(buildingSettings[value.id].zooServiceMaterial3)+" <img src='img/zooServiceMaterial3.png' valign='middle'>&nbsp;")

                    f.write("</small></div>")


                    return True
    print ">>> try building completed"
    return False


def TryBuyNewAnimal(f,gameInfo,buildingSettings,animalsReqs):
    print "[[[[[[ lets try to buy new animal"
    lowestPaddock = FindOldestNotFullPaddock(gameInfo,buildingSettings)
    if lowestPaddock[1] != 666:
        paddockName = lowestPaddock[0]
        if gameInfo.paddocksTotalAnimals[paddockName] < 4: # избыточная проверка
            nextAnimalNumber = gameInfo.paddocksTotalAnimals[paddockName]+1
            print "reqs for "+paddockName+ " animal # "+str(nextAnimalNumber)
            print vars(animalsReqs[paddockName][nextAnimalNumber])
            print "now have gems:"
            print gameInfo.gem1, gameInfo.gem2, gameInfo.gem3, gameInfo.gem4
            if (animalsReqs[paddockName][nextAnimalNumber].gem1 <= gameInfo.gem1) and (animalsReqs[paddockName][nextAnimalNumber].gem2 <= gameInfo.gem2) and (animalsReqs[paddockName][nextAnimalNumber].gem3 <= gameInfo.gem3) and (animalsReqs[paddockName][nextAnimalNumber].gem4 <= gameInfo.gem4):
                gameInfo.paddocksTotalAnimals[paddockName] = gameInfo.paddocksTotalAnimals[paddockName]+1
                gameInfo.gem1 = gameInfo.gem1 - animalsReqs[paddockName][nextAnimalNumber].gem1
                gameInfo.gem2 = gameInfo.gem2 - animalsReqs[paddockName][nextAnimalNumber].gem2
                gameInfo.gem3 = gameInfo.gem3 - animalsReqs[paddockName][nextAnimalNumber].gem3
                gameInfo.gem4 = gameInfo.gem4 - animalsReqs[paddockName][nextAnimalNumber].gem4
                print "bought new animal <--------------------------------------------------------------------------"
                f.write("<div class='orange'>buying new animal for <b>"+paddockName+"</b> (#"+str(nextAnimalNumber)+") &mdash; <small>")
                if animalsReqs[paddockName][nextAnimalNumber].gem1:
                    f.write(str(animalsReqs[paddockName][nextAnimalNumber].gem1)+" <img src='img/gem1.png' valign='middle'>&nbsp;")
                if animalsReqs[paddockName][nextAnimalNumber].gem2:
                    f.write(str(animalsReqs[paddockName][nextAnimalNumber].gem2)+" <img src='img/gem2.png' valign='middle'>&nbsp;")
                if animalsReqs[paddockName][nextAnimalNumber].gem3:
                    f.write(str(animalsReqs[paddockName][nextAnimalNumber].gem3)+" <img src='img/gem3.png' valign='middle'>&nbsp;")
                if animalsReqs[paddockName][nextAnimalNumber].gem4:
                    f.write(str(animalsReqs[paddockName][nextAnimalNumber].gem4)+" <img src='img/gem4.png' valign='middle'>&nbsp;")
                f.write("</small></div>")
                return True # купили животное в самом старом неполном загоне

    # если до этого не купили, то попробуем купить в любом загоне из неполных
    for key,value in gameInfo.paddocksTotalAnimals.iteritems():
        if key in gameInfo.paddocks:
            if value < 4 and gameInfo.paddocks[key] == 1: # загон еще не полный и он точно построен
                nextAnimalNumber = value+1
                paddockName = key
                if (animalsReqs[paddockName][nextAnimalNumber].gem1 <= gameInfo.gem1) and (animalsReqs[paddockName][nextAnimalNumber].gem2 <= gameInfo.gem2) and (animalsReqs[paddockName][nextAnimalNumber].gem3 <= gameInfo.gem3) and (animalsReqs[paddockName][nextAnimalNumber].gem4 <= gameInfo.gem4):
                    gameInfo.paddocksTotalAnimals[paddockName] = gameInfo.paddocksTotalAnimals[paddockName]+1
                    gameInfo.gem1 = gameInfo.gem1 - animalsReqs[paddockName][nextAnimalNumber].gem1
                    gameInfo.gem2 = gameInfo.gem2 - animalsReqs[paddockName][nextAnimalNumber].gem2
                    gameInfo.gem3 = gameInfo.gem3 - animalsReqs[paddockName][nextAnimalNumber].gem3
                    gameInfo.gem4 = gameInfo.gem4 - animalsReqs[paddockName][nextAnimalNumber].gem4
                    print "bought new animal <--------------------------------------------------------------------------"
                    f.write("<div class='orange'>buying new animal for <b>"+paddockName+"</b> (#"+str(nextAnimalNumber)+") &mdash; <small>")
                    if animalsReqs[paddockName][nextAnimalNumber].gem1:
                        f.write(str(animalsReqs[paddockName][nextAnimalNumber].gem1)+" <img src='img/gem1.png' valign='middle'>&nbsp;")
                    if animalsReqs[paddockName][nextAnimalNumber].gem2:
                        f.write(str(animalsReqs[paddockName][nextAnimalNumber].gem2)+" <img src='img/gem2.png' valign='middle'>&nbsp;")
                    if animalsReqs[paddockName][nextAnimalNumber].gem3:
                        f.write(str(animalsReqs[paddockName][nextAnimalNumber].gem3)+" <img src='img/gem3.png' valign='middle'>&nbsp;")
                    if animalsReqs[paddockName][nextAnimalNumber].gem4:
                        f.write(str(animalsReqs[paddockName][nextAnimalNumber].gem4)+" <img src='img/gem4.png' valign='middle'>&nbsp;")
                    f.write("</small></div>")
                    return True

    print "]]]]]] Try buying animal completed"
    return False