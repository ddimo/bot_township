# coding=utf-8

from functions import *
import time
import xml.etree.ElementTree as xml


MAX_WAIT_FOR_UPGRADE = 5    # сколько шагов максимум ждем прежде чем купим апгрейд даже если копим на здание
USE_340_XMLS = True         # если True - используем хмл из 340 версии

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



writeHtmlHead()

# в начале строим туториальный загон для медведя, покупаем медведя и строим кафе
writeLog("pink","building <b>paddock_bear</b> (tutorial)")
gameInfo.paddocks["paddock_bear"] = 1
writeLog("orange","buying new animal for <b>paddock_bear</b> (tutorial)")
gameInfo.paddocksTotalAnimals["paddock_bear"] = 1
writeLog("lime","building <b>zoo_caffe</b> (tutorial)")
gameInfo.communities["zoo_caffe"] = 1

justLeveluped = 0


# ЗАПУСКАЕМ ПОСЛЕДОВАТЕЛЬНОЕ ОТКРЫВАНИЕ ПОДАРКОВ
#for x in range(0,35):
x = 0
# while gameInfo.paddocksTotalAnimals['paddock_zebra']<4:
while gameInfo.zooLevel<12:
    x += 1
    print ""
    writeLog("normal","&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;")
    print str(x)+")"
    # получили рандомный материал в дропе и увеличили его количество в сохранке
    chestContentTuple = GenerateZooCommunityChestContent()
    chestContent = chestContentTuple[0]

    if chestContent not in gameInfo.levelDrop:
        gameInfo.levelDrop[chestContent] = 1
    else:
        gameInfo.levelDrop[chestContent] += 1

    curvalue = getattr(gameInfo,chestContent)
    curChestCounter = gameInfo.zooChestCounter
    setattr(gameInfo,chestContent,curvalue+1)
    gameInfo.zooChestCounter = curChestCounter+1
    if "gem" in chestContent:
        AddGems(chestContent)

    # раз в Y сундуков увеличим количество городских стройматериалов, как будто они приехали на поезде
    y = 20
    if gameInfo.zooChestCounter % y == 0:
        if gameInfo.axe < 7: gameInfo.axe += 3
        if gameInfo.pick < 7: gameInfo.pick += 3
        if gameInfo.TNT < 7: gameInfo.TNT += 3
        rand = random.randint(1,3)
        if rand == 1:
            if gameInfo.Brick < 50: gameInfo.Brick += 10
            if gameInfo.Glass < 50: gameInfo.Glass += 7
            if gameInfo.Plita < 50: gameInfo.Plita += 5
        elif rand == 2:
            if gameInfo.Glass < 50: gameInfo.Glass += 10
            if gameInfo.Plita < 50: gameInfo.Plita += 7
            if gameInfo.Brick < 50: gameInfo.Brick += 5
        else:
            if gameInfo.Plita < 50: gameInfo.Plita += 10
            if gameInfo.Brick < 50: gameInfo.Brick += 7
            if gameInfo.Glass < 50: gameInfo.Glass += 5


    if (chestContentTuple[1] == "buildingmat" or chestContentTuple[1] == "upgrademat") and (chestContent in buildingMatList):
        if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
        else: gameInfo.levelDropHelped[chestContent] += 1
        writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> dropped <font color='red'><b>"+chestContent+"</b></font>")

    elif (chestContentTuple[1] == "needgem") and (chestContent in gemsList):
        if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
        else: gameInfo.levelDropHelped[chestContent] += 1
        writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> dropped <font color='blue'><b>"+chestContent+"</b></font> <font size='2'>(from needGem)</font>")

    elif (chestContentTuple[1] == "randomgem") and (chestContent in gemsList):
        if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
        else: gameInfo.levelDropHelped[chestContent] += 1
        writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> dropped <font color='green'><b>"+chestContent+"</b></font> <font size='2'>(from randomGem)</font>")

    elif (chestContentTuple[1] == "getnextgem") and (chestContent in gemsList):
        if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
        else: gameInfo.levelDropHelped[chestContent] += 1
        writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> dropped <font color='green'><b>"+chestContent+"</b></font> <font size='2'>(from GetNextGem)</font>")

    elif (chestContentTuple[1] == "warehousemat") and (chestContent in warehouseMatList):
        if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
        else: gameInfo.levelDropHelped[chestContent] += 1
        writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> dropped <font color='orange'><b>"+chestContent+"</b></font> <font size='2'></font>")

    elif (chestContentTuple[1] == "expandmat") and (chestContent in expansionMatList):
        if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
        else: gameInfo.levelDropHelped[chestContent] += 1
        writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> dropped <font color='pink'><b>"+chestContent+"</b></font> <font size='2'></font>")

    else:
        writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> "+chestContent+" ")

    print "dropped", chestContent

    # добавим рейтинг подарка
    gameInfo.rating = gameInfo.rating + ratingForChest[gameInfo.zooLevel]

    # обрабатываем момент LEVELUP
    if gameInfo.rating > ratingToLevelup[gameInfo.zooLevel+1]:
        justLeveluped = 1
        gameInfo.zooLevel += 1
        line = "<b>LEVELUP "+str(gameInfo.zooLevel)+"!</b>"

        line += "<br>new buildings available: "
        for key, value in buildingSettings.iteritems():
            if value.zooLevel == gameInfo.zooLevel:
                line += "<b>"+key+"</b>, "

        line += "<br>not yet built: "
        for key, value in buildingSettings.iteritems():
            if value.zooLevel < gameInfo.zooLevel:
                if ("paddock_" in key and gameInfo.paddocks[key] == 0) or ("zoo_" in key and gameInfo.communities[key] == 0):
                    line += "<font color='darkred'><b>"+key+"</b></font> (L"+str(value.zooLevel)+"), "

        line += "<br>not full paddocks: "
        for key, value in buildingSettings.iteritems():
            if value.zooLevel < gameInfo.zooLevel:
                if "paddock_" in key and gameInfo.paddocks[key] == 1 and gameInfo.paddocksTotalAnimals[key] < 4:
                    line += "<font color='darkgreen'><b>"+key+"</b></font> (L"+str(value.zooLevel)+", "+str(gameInfo.paddocksTotalAnimals[key])+"/4 animals), "

        line += "<br>expansion level: <b>"+str(gameInfo.zooExpandLevel)+"</b>"
        totalAnimals = sum(gameInfo.paddocksTotalAnimals.itervalues())
        maxExpand = 0
        for key, value in enumerate(expandReqs):
            if key > 0:
                if value.animals <= totalAnimals:
                    maxExpand = key
        line += "/"+str(maxExpand)

        line += "<br><b>droped "+str(sum(gameInfo.levelDrop.itervalues()))+" total</b>: <Br> <small>"
        for key, value in sorted(gameInfo.levelDrop.iteritems()):
            line += "&nbsp; "+key+" = <b>"+str(value)+"</b>"
            if key in gameInfo.levelDropHelped:
                line += " <i>("+str(gameInfo.levelDropHelped[key])+" helped)</i>"
            else:
                line += " <i>(0 helped)</i>"
            line += "<br>"
        line += "</small>"
        gameInfo.levelDrop.clear()
        gameInfo.levelDropHelped.clear()
        writeLog("darkblue", line)
        writeShortLog("darkblue", line)
        print "levelup "+str(gameInfo.zooLevel)
        time.sleep(0.3)

    # пробежимся по всем зданиям и проверим, нельзя ли построить доступное
    while TryBuild():
        print "try building more"

    # пробежимся по доступным апгрейдам и проверим, нельзя ли проапгрейдить комьюнити
    availableUpgrade = FindUpdateToBuy()
    if availableUpgrade:
        ubid = availableUpgrade[0] # идентификатор здания
        un = availableUpgrade[1] # номер апгрейда
        line = GetBuildingReqsLine("upgrade", ubid, un)
        writeLog("normalSmall","<i>enough materials for upgrade #"+str(un)+" in "+str(ubid)+" (needed: "+line+")")
        availableToBuild = FindAvailableNotBuilt()
        if not availableToBuild or (gameInfo.upgradeWait >= MAX_WAIT_FOR_UPGRADE and not CompareForZooMats(availableToBuild,ubid,un)):
            DoUpgrade(ubid,un)
            writeLog("normalSmall", "<font color='red'>bought upgrade</font>")
            gameInfo.upgradeWait = 0
        else:
            # не будем покупать апгрейд пока копим на строительство доступного загона/комьюнити
            if gameInfo.upgradeWait < MAX_WAIT_FOR_UPGRADE:
                line = GetBuildingReqsLine("build",availableToBuild,0)
                writeLog("normalSmall","not upgrading, saving ("+str(gameInfo.upgradeWait)+" times already) for "+availableToBuild+" (needed: "+line+")")
                if gameInfo.communities['zoo_eatery'] == 1: # пока не построили zoo_eatery - не будем апгрейдить вообще
                    gameInfo.upgradeWait += 1

    # выведем список зданий, которые еще не построены, но уже доступны - со списком требований
    for key, value in gameInfo.paddocks.items():
        if value == 0:                                                  # еще не построено
            if buildingSettings[key].zooLevel <= gameInfo.zooLevel:     # доступно по уровню
                line = GetBuildingReqsLine("build",key,0)
                writeLog("normalSmall","not yet built <b>"+key+"</b> ("+line+")")
    for key, value in gameInfo.communities.items():
        if value == 0:                                                  # еще не построено
            if buildingSettings[key].zooLevel <= gameInfo.zooLevel:     # доступно по уровню
                line = GetBuildingReqsLine("build",key,0)
                writeLog("normalSmall","not yet built <b>"+key+"</b> ("+line+")")


    # пробежимся по доступным загонам и проверим, можно ли купить животное
    while TryBuyNewAnimal():
        print "try to buy another animal"

    # попробуем купить расширение
    while TryExpand():
        print "try to expand"

    writeLog("normalSmall","&nbsp;")

    line = ""
    for g in gemsList:
        line += str(getattr(gameInfo,g))+" <img src='img/"+g+".png' valign='middle'> &nbsp; "
    writeLog("normalSmallOrange", line)
    if justLeveluped: writeShortLog("normalSmallOrange", line)

    line = str(gameInfo.zooLandDeed)+" <img src='img/zooLandDeed.png' valign='middle'> &nbsp; "+ \
            str(gameInfo.zooBuildingMaterial)+" <img src='img/zooBuildingMaterial.png' valign='middle'> &nbsp; "+ \
            str(gameInfo.zooServiceMaterial1)+" <img src='img/zooServiceMaterial1.png' valign='middle'> &nbsp; "+ \
            str(gameInfo.zooServiceMaterial2)+" <img src='img/zooServiceMaterial2.png' valign='middle'> &nbsp; "+ \
            str(gameInfo.zooServiceMaterial3)+" <img src='img/zooServiceMaterial3.png' valign='middle'>"
    writeLog("normalSmallGreen", line)
    if justLeveluped: writeShortLog("normalSmallGreen", line)

    line = str(gameInfo.Brick)+" <img src='img/Brick.png' valign='middle'> &nbsp; "+ \
            str(gameInfo.Plita)+" <img src='img/Plita.png' valign='middle'> &nbsp; "+ \
            str(gameInfo.Glass)+" <img src='img/Glass.png' valign='middle'> &nbsp; "+ \
            str(gameInfo.pick)+" <img src='img/pick.png' valign='middle'> &nbsp; "+ \
            str(gameInfo.axe)+" <img src='img/axe.png' valign='middle'> &nbsp; "+ \
            str(gameInfo.TNT)+" <img src='img/TNT.png' valign='middle'>"
    writeLog("normalSmallBlue", line)
    if justLeveluped:
        writeShortLog("normalSmallBlue", line)
        writeShortLog("normal","&nbsp;<br>&nbsp;")
        justLeveluped = 0


print ""
print "total "+str(x)+" steps"
writeHtmlFoot()
f.close()