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



# ЗАПУСКАЕМ ПОСЛЕДОВАТЕЛЬНОЕ ОТКРЫВАНИЕ ПОДАРКОВ
for x in range(0,5):

    # получили рандомный материал в дропе и увеличили его количество в сохранке
    chestContent = GenerateZooCommunityChestContent(gameInfo,buildingSettings)
    curvalue = getattr(gameInfo,chestContent)
    setattr(gameInfo,chestContent,curvalue+1)
    print "dropped", chestContent
    print ""

    # добавим рейтинг подарка
    gameInfo.rating = gameInfo.rating + ratingForChest[gameInfo.zooLevel]
    print "current sum rating is "+str(gameInfo.rating)

    # проверим, возможно надо левелапнуть
    if gameInfo.rating > ratingToLevelup[gameInfo.zooLevel+1]:
        gameInfo.zooLevel = gameInfo.zooLevel + 1
    print "current level is "+str(gameInfo.zooLevel)

    # пробежимся по всем зданиям и проверим, нельзя ли построить доступное
    for key, value in buildingSettings.iteritems():
        if int(value.zooLevel) <= gameInfo.zooLevel:
            if not CheckAlreadyBuilt(gameInfo,value.id):
                if CheckCanBuild(gameInfo,buildingSettings[value.id],value.id):
                    DoBuild(gameInfo,buildingSettings[value.id],value.id)
                    print "!!!!!!! enough materials to build "+value.id+", done!"

    # пробежимся по доступным загонам и проверим, можно ли купить животное
    lowestPaddock = FindOldestNotFullPaddock(gameInfo,buildingSettings)
    if lowestPaddock[1] != 666:
        paddockName = lowestPaddock[0]
        if gameInfo.paddocksTotalAnimals[paddockName] < 4:
            nextAnimalNumber = gameInfo.paddocksTotalAnimals[paddockName]+1
            print "next animal number is "+str(nextAnimalNumber)
            print "reqs for "+paddockName+ " animal # "+str(nextAnimalNumber)
            print vars(animalsReqs[paddockName][nextAnimalNumber])
            print "now have gems:"
            print gameInfo.gem1, gameInfo.gem2, gameInfo.gem3, gameInfo.gem4





# attrs = vars(gameInfo)
# print ', '.join("%s: %s" % item for item in attrs.items())
# print ""