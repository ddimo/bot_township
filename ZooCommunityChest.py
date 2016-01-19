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

zooBuildings = []

for elem in BuildingRequirements.iter():
    if (elem.tag == "reqs" and elem.attrib['ver'] == "2"):
        reqs = elem

# Заполним требования материалов на все комьюнити и загоны
for reqsElem in reqs.iter():
    if 'id' in reqsElem.attrib:
        if ("zoo_" in reqsElem.attrib['id'] or "paddock_" in reqsElem.attrib['id']):
            zooBuilding = buildingReq()
            zooBuilding.id = reqsElem.attrib['id']
            if 'Brick' in reqsElem.attrib:
                zooBuilding.Brick = reqsElem.attrib['Brick']
            if 'Plita' in reqsElem.attrib:
                zooBuilding.Plita = reqsElem.attrib['Plita']
            if 'Glass' in reqsElem.attrib:
                zooBuilding.Glass = reqsElem.attrib['Glass']
            if 'zooBuildingMaterial' in reqsElem.attrib:
                zooBuilding.zooBuildingMaterial = reqsElem.attrib['zooBuildingMaterial']
            if 'zooServiceMaterial1' in reqsElem.attrib:
                zooBuilding.zooServiceMaterial1 = reqsElem.attrib['zooServiceMaterial1']
            if 'zooServiceMaterial2' in reqsElem.attrib:
                zooBuilding.zooServiceMaterial2 = reqsElem.attrib['zooServiceMaterial2']
            if 'zooServiceMaterial3' in reqsElem.attrib:
                zooBuilding.zooServiceMaterial3 = reqsElem.attrib['zooServiceMaterial3']

            # добавим также информацию об уровне и цене из файла BuildingLocks
            for target in buildingsLocksRoot.findall("./building[@buildingId='"+zooBuilding.id+"']"):
                params = target.find('params')
                zooBuilding.zooLevel = params.attrib['zooLevel']
                zooBuilding.price = params.attrib['price']

            zooBuildings.append(zooBuilding)


currentLevel = 1

for x in zooBuildings:
    if int(x.zooLevel) <= currentLevel:
        print "at level "+x.zooLevel+" available "+x.id


attrs = vars(gameInfo)
#print ', '.join("%s: %s" % item for item in attrs.items())
#print ""

for x in range(0,10):
    randomMat = GenerateZooCommunityChestContent(gameInfo)
    curvalue = getattr(gameInfo,randomMat)
    setattr(gameInfo,randomMat,curvalue+1)
    #print "random value is:", randomMat

attrs = vars(gameInfo)
#print ""
#print ', '.join("%s: %s" % item for item in attrs.items())