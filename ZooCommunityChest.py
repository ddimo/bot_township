# coding=utf-8

import random
from classes import *
from utils import *
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


# далее нужно в buildingSettings добавить информацию о бонусном рейтинге при их постройке
paddocksXml = xml.parse('../township/base/All_AnimalPaddocks.xml', parser=CommentsParser())
paddocksSettings = paddocksXml.find('AnimalPaddocks')
for paddockElem in paddocksSettings:
    elemId = paddockElem.attrib['type']
    elemRating = int(paddockElem.attrib['rating'])
    buildingSettings[elemId].bonusRating = elemRating


# также добавим инфу о бонусном рейтинге за комьюнити
buildingsZooXml = xml.parse('../township/base/buildings_zoo.xml', parser=CommentsParser())
zooCommunitySettings = buildingsZooXml.find('zoo_community')
for zooCommunityElem in zooCommunitySettings:
    elemId = zooCommunityElem.attrib['buildingId']
    elemRating = int(zooCommunityElem.attrib['rating'])
    buildingSettings[elemId].bonusRating = elemRating


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



for x in range(0,15):
    chestContent = GenerateZooCommunityChestContent(gameInfo,buildingSettings)
    curvalue = getattr(gameInfo,chestContent)
    setattr(gameInfo,chestContent,curvalue+1)
    # получили рандомный материал в дропе и увеличили его количество в сохранк
    print "dropped", chestContent
    print ""

    # добавим рейтинг подарка и проверим, возможно надо левелапнуть
    gameInfo.rating = gameInfo.rating + ratingForChest[gameInfo.zooLevel]
    print "current sum rating is "+str(gameInfo.rating)
    if gameInfo.rating > ratingToLevelup[gameInfo.zooLevel+1]:
        gameInfo.zooLevel = gameInfo.zooLevel + 1

    print "current level is "+str(gameInfo.zooLevel)

    for key, value in buildingSettings.iteritems():
        if int(value.zooLevel) <= gameInfo.zooLevel:
            #print "    at level "+str(value.zooLevel)+" available "+str(value.id)
            if not CheckAlreadyBuilt(gameInfo,value.id):
                #print "    available and not yet built "+str(value.id)
                if CheckCanBuild(gameInfo,buildingSettings[value.id],value.id):
                    DoBuild(gameInfo,buildingSettings[value.id],value.id)
                    print "!!!!!!! enough materials to build "+value.id+", done!"
                #else: print "     -can not be built"


# attrs = vars(gameInfo)
# print ', '.join("%s: %s" % item for item in attrs.items())
# print ""