# coding=utf-8

from functions import *
import xml.etree.ElementTree as xml


MAX_WAIT_FOR_UPGRADE = 100 # сколько шагов максимум ждем прежде чем купим апгрейд даже если копим на здание

gameBalanceXml = xml.parse('../township/base/GameBalance.xml', parser=CommentsParser())
gameBalanceRoot = gameBalanceXml.getroot()
BuildingRequirements = gameBalanceRoot.find('BuildingRequirements')
buildingsLocksXml = xml.parse('../township/base/BuildingsLocks_v1.xml', parser=CommentsParser())
buildingsLocksRoot = buildingsLocksXml.getroot()

reqs = []

# Заполним требования материалов на все комьюнити и загоны
for elem in BuildingRequirements.iter():
    if elem.tag == "reqs" and elem.attrib['ver'] == "2":
        reqs = elem

for reqsElem in reqs.iter():
    if 'id' in reqsElem.attrib:
        cur_id = reqsElem.attrib['id']
        if "zoo_" in cur_id or "paddock_" in cur_id:
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
                x += 1

# upgradesReqs['zoo_caffe'][1] = class with reqs for upgrade #1 (Brick,Plita .. animalsCount)



# теперь соберем инфу сколько рейтинга дает постройка загона, а также какие требования на животных из All_AnimalPaddocks
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
            animalNumber += 1

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
for levelupElem in zooLevelups:
    elemLevel = int(levelupElem.attrib['level'])
    elemRatingForChest = int(levelupElem.attrib['ratingForChest'])
    elemExp = int(levelupElem.attrib['experience'])
    ratingForChest[elemLevel] = elemRatingForChest
    ratingToLevelup[elemLevel] = elemExp

# ratingForChest[level] - сколько рейтинга нужно на подарок во время уровня level
# ratingToLevelup[level] - сколько требуется рейтинга суммарно для перехода на уровень level


# соберем инфу о расширениях в зоопарке
expandXml = xml.parse('../township/base/expand_zoo.xml', parser=CommentsParser())
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

gameInfo.communitiesUpgrades['zoo_eatery'] = 2

# ЗАПУСКАЕМ ПОСЛЕДОВАТЕЛЬНОЕ ОТКРЫВАНИЕ ПОДАРКОВ
#for x in range(0,35):
x = 0
# gameInfo.paddocksTotalAnimals['paddock_zebra'] = 0
# while gameInfo.paddocksTotalAnimals['paddock_zebra']<4:
while gameInfo.zooLevel<11:
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
    setattr(gameInfo,chestContent,curvalue+1)
    if "gem" in chestContent:
        AddGems(chestContent)


    if (chestContentTuple[1] == "buildingmat" or chestContentTuple[1] == "upgrademat") and (chestContent in buildingMatList):
        if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
        else: gameInfo.levelDropHelped[chestContent] += 1
        writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> <font color='red'><b>"+chestContent+"</b></font>")

    elif (chestContentTuple[1] == "needgem") and (chestContent in gemsList):
        if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
        else: gameInfo.levelDropHelped[chestContent] += 1
        writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> <font color='blue'><b>"+chestContent+"</b></font> <font size='2'>(from needGem)</font>")

    elif (chestContentTuple[1] == "randomgem") and (chestContent in gemsList):
        if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
        else: gameInfo.levelDropHelped[chestContent] += 1
        writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> <font color='green'><b>"+chestContent+"</b></font> <font size='2'>(from randomGem)</font>")

    elif (chestContentTuple[1] == "getnextgem") and (chestContent in gemsList):
        if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
        else: gameInfo.levelDropHelped[chestContent] += 1
        writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> <font color='green'><b>"+chestContent+"</b></font> <font size='2'>(from GetNextGem)</font>")

    elif (chestContentTuple[1] == "warehousemat") and (chestContent in warehouseMatList):
        if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
        else: gameInfo.levelDropHelped[chestContent] += 1
        writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> <font color='orange'><b>"+chestContent+"</b></font> <font size='2'></font>")

    elif (chestContentTuple[1] == "expandmat") and (chestContent in expansionMatList):
        if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
        else: gameInfo.levelDropHelped[chestContent] += 1
        writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> <font color='pink'><b>"+chestContent+"</b></font> <font size='2'></font>")

    else:
        writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> "+chestContent+" ")

    print "dropped", chestContent

    # добавим рейтинг подарка
    gameInfo.rating = gameInfo.rating + ratingForChest[gameInfo.zooLevel]

    # обрабатываем момент LEVELUP
    if gameInfo.rating > ratingToLevelup[gameInfo.zooLevel+1]:
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
        if not availableToBuild or gameInfo.upgradeWait >= MAX_WAIT_FOR_UPGRADE:
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


    # пробежимся по доступным загонам и проверим, можно ли купить животное
    while TryBuyNewAnimal():
        print "try to buy another animal"

    # попробуем купить расширение
    while TryExpand():
        print "try to expand"

    f.write("<div class='normalSmall'>&nbsp;</div>")

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
    f.write(str(gameInfo.Glass)+" <img src='img/Glass.png' valign='middle'> &nbsp; ")
    f.write(str(gameInfo.pick)+" <img src='img/pick.png' valign='middle'> &nbsp; ")
    f.write(str(gameInfo.axe)+" <img src='img/axe.png' valign='middle'> &nbsp; ")
    f.write(str(gameInfo.TNT)+" <img src='img/TNT.png' valign='middle'> &nbsp; ")
    f.write("</div>")

    print ""
    print "total "+str(x)+" steps"


writeHtmlFoot()
f.close()