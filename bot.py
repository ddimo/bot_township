# coding=utf-8

import random
from classes import *
from functions import *
import xml.etree.ElementTree as xml
import os.path

gameInfo = gameInfoClass()

gameBalanceXml = xml.parse('../township/base/GameBalance.xml', parser=CommentsParser())
gameBalanceRoot = gameBalanceXml.getroot()
BuildingRequirements = gameBalanceRoot.find('BuildingRequirements')

buildingsLocksXml = xml.parse('../township/base/BuildingsLocks_v1.xml', parser=CommentsParser())
buildingsLocksRoot = buildingsLocksXml.getroot()

buildingSettings = dict()
reqs = []

# Заполним требования материалов на все комьюнити и загоны
for elem in BuildingRequirements.iter():
    if (elem.tag == "reqs" and elem.attrib['ver'] == "2"):
        reqs = elem

for reqsElem in reqs.iter():
    if 'id' in reqsElem.attrib:
        cur_id = reqsElem.attrib['id']
        if ("zoo_" in cur_id or "paddock_" in cur_id):
            zooBuilding = buildingSettingsClass()
            zooBuilding.id = reqsElem.attrib['id']
            if 'Brick' in reqsElem.attrib:
                zooBuilding.Brick = int(reqsElem.attrib['Brick'])
            if 'Plita' in reqsElem.attrib:
                zooBuilding.Plita = int(reqsElem.attrib['Plita'])
            if 'Glass' in reqsElem.attrib:
                zooBuilding.Glass = int(reqsElem.attrib['Glass'])
            if 'zooBuildingMaterial' in reqsElem.attrib:
                zooBuilding.zooBuildingMaterial = int(reqsElem.attrib['zooBuildingMaterial'])
            if 'zooServiceMaterial1' in reqsElem.attrib:
                zooBuilding.zooServiceMaterial1 = int(reqsElem.attrib['zooServiceMaterial1'])
            if 'zooServiceMaterial2' in reqsElem.attrib:
                zooBuilding.zooServiceMaterial2 = int(reqsElem.attrib['zooServiceMaterial2'])
            if 'zooServiceMaterial3' in reqsElem.attrib:
                zooBuilding.zooServiceMaterial3 = int(reqsElem.attrib['zooServiceMaterial3'])

            # добавим также информацию об уровне и цене из файла BuildingLocks
            for target in buildingsLocksRoot.findall("./building[@buildingId='"+zooBuilding.id+"']"):
                params = target.find('params')
                zooBuilding.zooLevel = int(params.attrib['zooLevel'])
                zooBuilding.price = int(params.attrib['price'])

            buildingSettings[cur_id] = zooBuilding
            if "paddock_" in cur_id:
                gameInfo.paddocks[cur_id] = 0
                gameInfo.paddocksTotalAnimals[cur_id] = 0
            elif "zoo_" in cur_id:
                gameInfo.communities[cur_id] = 0
                gameInfo.communitiesUpgrades[cur_id] = 0

# итого buildingSettings[building_id] = элемент класса buildingSettingsClass
# например:
# buildingSettings["paddock_zebra"].zooBuildingMaterial - количество требуемого материала
# buildingSettings["zoo_caffe"].zooLevel - требуемый уровень
# buildingSettings["zoo_caffe"].price - сколько дает рейтинга за постройку



# сбор инфы об апгрейдах
upgradesReqs = dict()
upgradesXml = xml.parse('../township/base/ZooUpgrade.xml', parser=CommentsParser())
upgradesRoot = upgradesXml.getroot()
UpgradesSettingsXml = upgradesRoot.find('Community')
for upgradeBuildingElem in UpgradesSettingsXml:
    if upgradeBuildingElem.tag == "Building":
        buildingId = upgradeBuildingElem.attrib['id']
        upgradesReqs[buildingId] = ['']
        upgradesReqs[buildingId][0] = ''
        x = 1
        for upgradeElem in upgradeBuildingElem:
           if upgradeElem.tag == "upgrade":
                curUpgradeReqs = buildingUpgradesSettingsClass()
                if 'Brick' not in upgradeElem.attrib and 'Plita' not in upgradeElem.attrib and 'Glass' not in upgradeElem.attrib and 'zooBuildingMaterial' not in upgradeElem.attrib and 'zooServiceMaterial1' not in upgradeElem.attrib and 'zooServiceMaterial2' not in upgradeElem.attrib and 'zooServiceMaterial3' not in upgradeElem.attrib:
                    # не указано ни одного требования на материалы
                    continue
                if 'Brick' in upgradeElem.attrib: curUpgradeReqs.Brick = int(upgradeElem.attrib['Brick'])
                if 'Plita' in upgradeElem.attrib: curUpgradeReqs.Plita = int(upgradeElem.attrib['Plita'])
                if 'Glass' in upgradeElem.attrib: curUpgradeReqs.Glass = int(upgradeElem.attrib['Glass'])
                if 'zooBuildingMaterial' in upgradeElem.attrib: curUpgradeReqs.zooBuildingMaterial = int(upgradeElem.attrib['zooBuildingMaterial'])
                if 'zooServiceMaterial1' in upgradeElem.attrib: curUpgradeReqs.zooServiceMaterial1 = int(upgradeElem.attrib['zooServiceMaterial1'])
                if 'zooServiceMaterial2' in upgradeElem.attrib: curUpgradeReqs.zooServiceMaterial2 = int(upgradeElem.attrib['zooServiceMaterial2'])
                if 'zooServiceMaterial3' in upgradeElem.attrib: curUpgradeReqs.zooServiceMaterial3 = int(upgradeElem.attrib['zooServiceMaterial3'])
                if 'animalsCount' in upgradeElem.attrib: curUpgradeReqs.animalsCount = int(upgradeElem.attrib['animalsCount'])
                upgradesReqs[buildingId].append(curUpgradeReqs)
                x = x+1

# upgradesReqs['zoo_caffe'][1] = class with reqs for upgrade #1 (Brick,Plita .. animalsCount)



# теперь соберем инфу сколько рейтинга дает постройка загона, а также какие требования на животных из All_AnimalPaddocks
animalsReqs = dict()
paddocksXml = xml.parse('../township/base/All_AnimalPaddocks.xml', parser=CommentsParser())
paddocksSettings = paddocksXml.find('AnimalPaddocks')
for paddockElem in paddocksSettings:
    elemId = paddockElem.attrib['type']
    elemRating = int(paddockElem.attrib['rating'])
    buildingSettings[elemId].bonusRating = elemRating
    animalNumber = 1
    animalsReqs[elemId] = [0,0,0,0,0]
    for childPaddockElem in paddockElem:
        if childPaddockElem.tag == "animal":
            curAnimalReqs = animalReqsClass()
            if 'gem1' in childPaddockElem.attrib: curAnimalReqs.gem1 = int(childPaddockElem.attrib['gem1'])
            if 'gem2' in childPaddockElem.attrib: curAnimalReqs.gem2 = int(childPaddockElem.attrib['gem2'])
            if 'gem3' in childPaddockElem.attrib: curAnimalReqs.gem3 = int(childPaddockElem.attrib['gem3'])
            if 'gem4' in childPaddockElem.attrib: curAnimalReqs.gem4 = int(childPaddockElem.attrib['gem4'])
            animalsReqs[elemId][animalNumber] = curAnimalReqs
            animalNumber = animalNumber+1

# инфа о бонусном рейтинге положена в buildingSettings: buildingSettings["zoo_caffe"].bonusRating
# требования камней на животных - в animalsReqs:
# animalsReqs['paddock_turtle'][1] - dict по идентификаторам загона, внутри list с номером животного,
# каждый элемент которого - класс animalReqsClass
# пример: animalsReqs['paddock_turtle'][1].gem2 = требования gem2 на первое животное из загона черепах

#print vars(animalsReqs['paddock_turtle'][1])
#exit()


# также добавим инфу о бонусном рейтинге за комьюнити
buildingsZooXml = xml.parse('../township/base/buildings_zoo.xml', parser=CommentsParser())
zooCommunitySettings = buildingsZooXml.find('zoo_community')
for zooCommunityElem in zooCommunitySettings:
    elemId = zooCommunityElem.attrib['buildingId']
    elemRating = int(zooCommunityElem.attrib['rating'])
    buildingSettings[elemId].bonusRating = elemRating
# инфу по бонусному рейтингу положили в buildingSettings[building_id].bonusRating


# теперь соберем инфу о левелапах в зоопарке
levelupInfoXml = xml.parse('../township/base/LevelupInfo_v1.xml', parser=CommentsParser())
levelupInfoRoot = levelupInfoXml.getroot()
zooLevelups = levelupInfoRoot.find('zooLevels')
ratingToLevelup = dict()
ratingForChest = dict()
for levelupElem in zooLevelups:
    elemLevel = int(levelupElem.attrib['level'])
    elemRatingForChest = int(levelupElem.attrib['ratingForChest'])
    elemExp = int(levelupElem.attrib['experience'])
    ratingForChest[elemLevel] = elemRatingForChest
    ratingToLevelup[elemLevel] = elemExp

# ratingForChest[level] - сколько рейтинга нужно на подарок во время уровня level
# ratingToLevelup[level] - сколько требуется рейтинга суммарно для перехода на уровень level

f = open ("result.html","w")
writeHtmlHead(f)


# в начале строим туториальный загон для медведя, покупаем медведя и строим кафе
f.write("<div class='pink'>building <b>paddock_bear</b> (tutorial)</div>")
gameInfo.paddocks["paddock_bear"] = 1
f.write("<div class='orange'>buying new animal for <b>paddock_bear</b> (tutorial)</div>")
gameInfo.paddocksTotalAnimals["paddock_bear"] = 1
f.write("<div class='lime'>building <b>zoo_caffe</b> (tutorial)</div>")
gameInfo.communities["zoo_caffe"] = 1

gameInfo.communitiesUpgrades['zoo_eatery'] = 2

# ЗАПУСКАЕМ ПОСЛЕДОВАТЕЛЬНОЕ ОТКРЫВАНИЕ ПОДАРКОВ
#for x in range(0,35):
x = 0
# gameInfo.paddocksTotalAnimals['paddock_zebra'] = 0
while gameInfo.paddocksTotalAnimals['paddock_zebra']<4:
    x = x+1

    print ""
    f.write("<div class='normal'>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;</div>")
    print str(x)+")"
    # получили рандомный материал в дропе и увеличили его количество в сохранке
    chestContentTuple = GenerateZooCommunityChestContent(f,gameInfo,buildingSettings,upgradesReqs,animalsReqs)
    chestContent = chestContentTuple[0]
    curvalue = getattr(gameInfo,chestContent)
    setattr(gameInfo,chestContent,curvalue+1)
    if "gem" in chestContent:
        AddGems(f,gameInfo,chestContent)

    if chestContentTuple[1] == "buildingmat" or chestContentTuple[1] == "upgrademat":
        f.write("<div class='normalBig'>#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> <font color='red'><b>"+chestContent+"</b></font></div>")
    elif chestContentTuple[1] == "needgem":
        f.write("<div class='normalBig'>#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> <font color='blue'><b>"+chestContent+"</b></font> <font size='2'>(from needGem)</font></div>")
    elif chestContentTuple[1] == "randomgem":
        f.write("<div class='normalBig'>#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> <font color='lightblue'><b>"+chestContent+"</b></font> <font size='2'>(from randomGem)</font></div>")
    elif chestContentTuple[1] == "getnextgem":
        f.write("<div class='normalBig'>#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> <font color='lightblue'><b>"+chestContent+"</b></font> <font size='2'>(from GetNextGem)</font></div>")
    else:
        f.write("<div class='normalBig'>#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> "+chestContent+"</div>")

    print "dropped", chestContent

    # добавим рейтинг подарка
    gameInfo.rating = gameInfo.rating + ratingForChest[gameInfo.zooLevel]
    #print "current sum rating is "+str(gameInfo.rating)
    #f.write("<div class='normal'>current sum rating is "+str(gameInfo.rating)+"</div>")

    # проверим, возможно надо левелапнуть
    if gameInfo.rating > ratingToLevelup[gameInfo.zooLevel+1]:
        gameInfo.zooLevel = gameInfo.zooLevel + 1
        # print "<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><> LEVELUP!!!!!!!"
        f.write("<div class='darkblue'><b>LEVELUP! now on level "+str(gameInfo.zooLevel)+"</b></div>")
    #print "current level is "+str(gameInfo.zooLevel)

    # пробежимся по всем зданиям и проверим, нельзя ли построить доступное
    while TryBuild (f,gameInfo,buildingSettings):
        print "try building more"
        #f.write("<div class='normal'>try building more</div>")

    # пробежимся по доступным загонам и проверим, можно ли купить животное
    while TryBuyNewAnimal(f,gameInfo,buildingSettings,animalsReqs):
        print "try to buy another animal"
        #f.write("<div class='normalSmall'>try to buy another animal</div>")

    f.write("<div class='normalSmallOrange'>")
    f.write(str(gameInfo.gem1)+" <img src='img/gem1.png' valign='middle'> &nbsp; ")
    f.write(str(gameInfo.gem2)+" <img src='img/gem2.png' valign='middle'> &nbsp; ")
    f.write(str(gameInfo.gem3)+" <img src='img/gem3.png' valign='middle'> &nbsp; ")
    f.write(str(gameInfo.gem4)+" <img src='img/gem4.png' valign='middle'> ")
    f.write("</div>")

    f.write("<div class='normalSmallGreen'>")
    f.write(str(gameInfo.zooLandDeed)+" <img src='img/zooLandDeed.png' valign='middle'> &nbsp; ")
    f.write(str(gameInfo.zooBuildingMaterial)+" <img src='img/zooBuildingMaterial.png' valign='middle'> &nbsp; ")
    f.write(str(gameInfo.zooServiceMaterial1)+" <img src='img/zooServiceMaterial1.png' valign='middle'> &nbsp; ")
    f.write(str(gameInfo.zooServiceMaterial2)+" <img src='img/zooServiceMaterial2.png' valign='middle'> &nbsp; ")
    f.write(str(gameInfo.zooServiceMaterial3)+" <img src='img/zooServiceMaterial3.png' valign='middle'>")
    f.write("</div>")

    f.write("<div class='normalSmallBlue'>")
    f.write(str(gameInfo.Brick)+" <img src='img/Brick.png' valign='middle'> &nbsp; ")
    f.write(str(gameInfo.Plita)+" <img src='img/Plita.png' valign='middle'> &nbsp; ")
    f.write(str(gameInfo.Glass)+" <img src='img/Glass.png' valign='middle'>")
    f.write("</div>")




writeHtmlFoot(f)
f.close()

