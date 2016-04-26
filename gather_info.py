# coding=utf-8

from gather_info import *
from functions import *
from globalvars import *
import xml.etree.ElementTree as xml

USE_340_XMLS = False        # если True - используем хмл из 340 версии, больше не работает, т.к. в расчете лимиты камней в 360

xmlPath = '../township/base/'
if USE_340_XMLS:
    xmlPath = './v340/'

gameBalanceXml = xml.parse(xmlPath+'GameBalance.xml', parser=CommentsParser())
buildingsLocksXml = xml.parse(xmlPath+'BuildingsLocks_v1.xml', parser=CommentsParser())
upgradesXml = xml.parse(xmlPath+'ZooUpgrade.xml', parser=CommentsParser())
paddocksXml = xml.parse(xmlPath+'All_AnimalPaddocks.xml', parser=CommentsParser())
buildingsZooXml = xml.parse(xmlPath+'buildings_zoo.xml', parser=CommentsParser())
levelupInfoXml = xml.parse(xmlPath+'LevelupInfo_v1.xml', parser=CommentsParser())
expandXml = xml.parse(xmlPath+'expand_zoo.xml', parser=CommentsParser())

gameBalanceRoot = gameBalanceXml.getroot()
BuildingRequirements = gameBalanceRoot.find('BuildingRequirements')

buildingsLocksRoot = buildingsLocksXml.getroot()

reqs = []

# Заполним требования материалов на все комьюнити и загоны
if USE_340_XMLS:
    reqs = BuildingRequirements
else:
    for elem in BuildingRequirements.iter():
        if elem.tag == "reqs" and elem.attrib['ver'] == "2":
            reqs = elem

for reqsElem in reqs.iter():
    if 'id' in reqsElem.attrib:
        cur_id = reqsElem.attrib['id']
        if "zoo_" in cur_id or "paddock_" in cur_id:
            zooBuilding = buildingSettingsClass()
            zooBuilding.id = reqsElem.attrib['id']

            for mat in buildingMatList:
                if mat in reqsElem.attrib:
                    setattr(zooBuilding,mat,int(reqsElem.attrib[mat]))

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
                for mat in buildingMatList:
                    if mat in upgradeElem.attrib: setattr(curUpgradeReqs,mat,int(upgradeElem.attrib[mat]))
                if 'animalsCount' in upgradeElem.attrib: curUpgradeReqs.animalsCount = int(upgradeElem.attrib['animalsCount'])
                upgradesReqs[buildingId].append(curUpgradeReqs)
                x += 1

# upgradesReqs['zoo_caffe'][1] = class with reqs for upgrade #1 (Brick,Plita .. animalsCount)



# теперь соберем инфу сколько рейтинга дает постройка загона, а также какие требования на животных из All_AnimalPaddocks
paddocksSettings = paddocksXml.find('AnimalPaddocks')
for paddockElem in paddocksSettings:
    if paddockElem.tag == 'paddock':
        elemId = paddockElem.attrib['type']
        elemRating = int(paddockElem.attrib['rating'])
        buildingSettings[elemId].bonusRating = elemRating
        animalNumber = 1
        animalsReqs[elemId] = [0,0,0,0,0]
        for childPaddockElem in paddockElem:
            if childPaddockElem.tag == "animal":
                curAnimalReqs = animalReqsClass()
                for g in gemsList:
                    if g in childPaddockElem.attrib: setattr(curAnimalReqs,g,int(childPaddockElem.attrib[g]))
                animalsReqs[elemId][animalNumber] = curAnimalReqs
                animalNumber += 1

# инфа о бонусном рейтинге положена в buildingSettings: buildingSettings["zoo_caffe"].bonusRating
# требования камней на животных - в animalsReqs:
# animalsReqs['paddock_turtle'][1] - dict по идентификаторам загона, внутри list с номером животного,
# каждый элемент которого - класс animalReqsClass
# пример: animalsReqs['paddock_turtle'][1].gem2 = требования gem2 на первое животное из загона черепах



# также добавим инфу о бонусном рейтинге за комьюнити
zooCommunitySettings = buildingsZooXml.find('zoo_community')
for zooCommunityElem in zooCommunitySettings:
    elemId = zooCommunityElem.attrib['buildingId']
    elemRating = int(zooCommunityElem.attrib['rating'])
    buildingSettings[elemId].bonusRating = elemRating
# инфу по бонусному рейтингу положили в buildingSettings[building_id].bonusRating


# теперь соберем инфу о левелапах в зоопарке
levelupInfoRoot = levelupInfoXml.getroot()
zooLevelups = levelupInfoRoot.find('zooLevels')
for levelupElem in zooLevelups:
    elemLevel = int(levelupElem.attrib['level'])
    elemRatingForChest = int(levelupElem.attrib['ratingForChest'])
    elemExp = int(levelupElem.attrib['experience'])
    ratingForChest[elemLevel] = elemRatingForChest
    ratingToLevelup[elemLevel] = elemExp

# ratingForChest[level] - сколько рейтинга нужно на подарок во время уровня level
# ratingToLevelup[level] - сколько требуется рейтинга суммарно для перехода на уровень level




# теперь соберем инфу о лимитах камней по уровням
gemLimits = gameBalanceRoot.find('GemsLimits')
for gemLimitsElem in gemLimits:
    elem = gemLimitClass()
    elem.fromZooLevel = int(gemLimitsElem.attrib['fromZooLevel'])
    elem.toZooLevel = int(gemLimitsElem.attrib['toZooLevel'])
    elem.gem1 = int(gemLimitsElem.attrib['gem1'])
    elem.gem2 = int(gemLimitsElem.attrib['gem2'])
    elem.gem3 = int(gemLimitsElem.attrib['gem3'])
    elem.gem4 = int(gemLimitsElem.attrib['gem4'])
    gemLimitRanges.append(elem)

_gemsWithCorrectionWeightCoefficient = gameBalanceRoot.find('GemsWithCorrectionWeightCoefficient')
_gemsWithCorrectionWeightCoefficient = float(_gemsWithCorrectionWeightCoefficient.attrib['k'].replace("f",""))

# соберем инфу о расширениях в зоопарке
expandXmlRoot = expandXml.getroot()
for expandElem in expandXmlRoot:
    curExpand = zooExpansionClass()
    if 'animals' in expandElem.attrib: curExpand.animals = int(expandElem.attrib['animals'])
    if 'zooLandDeed' in expandElem.attrib: curExpand.zooLandDeed = int(expandElem.attrib['zooLandDeed'])
    if 'pick' in expandElem.attrib: curExpand.pick = int(expandElem.attrib['pick'])
    if 'axe' in expandElem.attrib: curExpand.axe = int(expandElem.attrib['axe'])
    if 'TNT' in expandElem.attrib: curExpand.TNT = int(expandElem.attrib['TNT'])
    expandReqs.append(curExpand)

# expandReqs[number] = class (animals,zooLandDeed, pick, axe, TNT)