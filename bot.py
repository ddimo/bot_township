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

# итого buildingSettings[building_id] = элемент класса buildingSettingsClass
# например:
# buildingSettings["paddock_zebra"].zooBuildingMaterial - количество требуемого материала
# buildingSettings["zoo_caffe"].zooLevel - требуемый уровень
# buildingSettings["zoo_caffe"].price - сколько дает рейтинга за постройку



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
# f.write("<div class='lightgreen'>lightgreen</div>")
# f.write("<div class='darkblue'>darkblue</div>")
# f.write("<div class='lightblue'>lightblue</div>")
# f.write("<div class='newispy'>newispy</div>")
# f.write("<div class='SpendStars'>SpendStars</div>")
# f.write("<div class='expansionResume'>expansionResume</div>")
# f.write("<div class='dayResume'>dayResume</div>")
# f.write("<div class='matQuestInfoStyle'>matQuestInfoStyle</div>")


# в начале строим туториальный загон для медведя, покупаем медведя и строим кафе
f.write("<div class='pink'>building <b>paddock_bear</b> (tutorial)</div>")
gameInfo.paddocks["paddock_bear"] = 1
f.write("<div class='orange'>buying new animal for <b>paddock_bear</b> (tutorial)</div>")
gameInfo.paddocksTotalAnimals["paddock_bear"] = 1
f.write("<div class='lime'>building <b>zoo_caffe</b> (tutorial)</div>")
gameInfo.communities["zoo_caffe"] = 1


# ЗАПУСКАЕМ ПОСЛЕДОВАТЕЛЬНОЕ ОТКРЫВАНИЕ ПОДАРКОВ
#for x in range(0,35):
x = 0
gameInfo.paddocksTotalAnimals['paddock_flamingo'] = 0
while gameInfo.paddocksTotalAnimals['paddock_flamingo']<4:
    x = x+1

    print ""
    f.write("<div class='normal'>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;</div>")
    print str(x)+")"
    # получили рандомный материал в дропе и увеличили его количество в сохранке
    chestContentTuple = GenerateZooCommunityChestContent(f,gameInfo,buildingSettings,animalsReqs)
    chestContent = chestContentTuple[0]
    curvalue = getattr(gameInfo,chestContent)
    setattr(gameInfo,chestContent,curvalue+1)

    if chestContentTuple[1] == "buildingmat":
        f.write("<div class='normalBig'>#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> <font color='red'><b>"+chestContent+"</b></font></div>")
    elif chestContentTuple[1] == "needgem":
        f.write("<div class='normalBig'>#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> <font color='blue'><b>"+chestContent+"</b></font> <font size='2'>(from needGem)</font></div>")
    elif chestContentTuple[1] == "randomgem":
        f.write("<div class='normalBig'>#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> <font color='lightblue'><b>"+chestContent+"</b></font> <font size='2'>(from randomGem)</font></div>")
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

