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

zooBuildings = dict()

# Заполним требования материалов на все комьюнити и загоны
for elem in BuildingRequirements.iter():
    if (elem.tag == "reqs" and elem.attrib['ver'] == "2"):
        reqs = elem

for reqsElem in reqs.iter():
    if 'id' in reqsElem.attrib:
        cur_id = reqsElem.attrib['id']
        if ("zoo_" in cur_id or "paddock_" in cur_id):
            zooBuilding = buildingReq()
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

            zooBuildings[cur_id] = zooBuilding

# print zooBuildings
# print zooBuildings['paddock_tiger']

currentLevel = 6
#gameInfo.paddocks['paddock_zebra'] = 1
# gameInfo.communities['zoo_caffe'] = 1
#
# gameInfo.zooBuildingMaterial = 3
#
# testBuildingId = 'paddock_zebra'

# if CheckCanBuild(gameInfo,zooBuildings[testBuildingId],testBuildingId):
#     print testBuildingId+" can be built!"
# else:
#     print testBuildingId+" can NOT be built! :("

# gameInfo.zooLevel = 1
# gameInfo.paddocks['paddock_bear'] = 1

gameInfo.zooLevel = 6

# print currentZooMaterialReqs



for x in range(0,10):
    chestContent = GenerateZooCommunityChestContent(gameInfo,zooBuildings)
    curvalue = getattr(gameInfo,chestContent)
    setattr(gameInfo,chestContent,curvalue+1)
    # получили рандомный материал в дропе и увеличили его количество в сохранк
    print "dropped", chestContent
    print ""
    for key, value in zooBuildings.iteritems():
        if int(value.zooLevel) <= currentLevel:
            #print "    at level "+str(value.zooLevel)+" available "+str(value.id)
            if not CheckAlreadyBuilt(gameInfo,value.id):
                #print "    available and not yet built "+str(value.id)
                if CheckCanBuild(gameInfo,zooBuildings[value.id],value.id):
                    DoBuild(gameInfo,zooBuildings[value.id],value.id)
                    print "!!!!!!! enough materials to build "+value.id+", done!"
                #else: print "     -can not be built"


# attrs = vars(gameInfo)
# print ', '.join("%s: %s" % item for item in attrs.items())
# print ""