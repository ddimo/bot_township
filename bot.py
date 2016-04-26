# coding=utf-8

from gather_info import *
import time

MAX_WAIT_FOR_UPGRADE = 100    # сколько шагов максимум ждем прежде чем купим апгрейд даже если копим на здание

writeHtmlHead()

# в начале строим туториальный загон для медведя, покупаем медведя и строим кафе
writeLog("pink","building <b>paddock_bear</b> (tutorial)")
gameInfo.paddocks["paddock_bear"] = 1
gameInfo.paddocksCompletePercent["paddock_bear"] = 0
writeLog("orange","buying new animal for <b>paddock_bear</b> (tutorial)")
gameInfo.paddocksTotalAnimals["paddock_bear"] = 1
writeLog("lime","building <b>zoo_eatery</b> (tutorial)")
gameInfo.communities["zoo_eatery"] = 1
gameInfo.communitiesCompletePercent["zoo_eatery"] = 0

justLeveluped = 0

# ЗАПУСКАЕМ ПОСЛЕДОВАТЕЛЬНОЕ ОТКРЫВАНИЕ ПОДАРКОВ
#for x in range(0,35):
x = 0
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
    curChestCounter = gameInfo.zooChestCounter
    setattr(gameInfo,chestContent,curvalue+1)
    gameInfo.zooChestCounter = curChestCounter+1
    if "gem" in chestContent:
        AddGems(chestContent,True)

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


    ################################ проверим не настало ли время добавить камни с самолета
    AddExtraGems("ALL")
    ###########################################

    ################################ проверим не настало ли время добавить камни с шахты
    # AddExtraGems("Mine")
    ###########################################


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
        line += "Extra gems (from plane and mine): <br>"
        for key, value in sorted(gameInfo.extraGems.iteritems()):
             line += "&nbsp; "+key+" = <b>"+str(value)+"</b><br>"
        line += "</small>"
        gameInfo.levelDrop.clear()
        gameInfo.levelDropHelped.clear()
        gameInfo.extraGems.clear()
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
        if availableToBuild:
            comparision = CompareForZooMats(availableToBuild,ubid,un)
        if not availableToBuild or not comparision or gameInfo.upgradeWait >= MAX_WAIT_FOR_UPGRADE:
            # do если нет доступных для строительства
            # или доступно, но нет совпадения по материалам с доступным
            # или доступно, есть совпадение, но подождали уже долго
            DoUpgrade(ubid,un)
            writeLog("normalSmall", "<font color='red'>bought upgrade</font>")
            gameInfo.upgradeWait = 0
        else: # if available and comparision and wait<=MAX_WAIT
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

line = "<b>REPORT:</b><br><br><table style='border:0px'><tr><td style='font-size:8pt'><b>id</b></td><td style='font-size:8pt'><b>open</b></td><td style='font-size:8pt'><b>complete</b></td></tr>"

for i in range(1,40):
    for key, value in gameInfo.paddocks.items():
        if buildingSettings[key].zooLevel == i and value == 1:
            percent = gameInfo.paddocksCompletePercent[key]
            if percent > 100:
                percent = "<font color='darkred'>"+str(percent)+"</font>"
            else:
                percent = "<font color='green'>"+str(percent)+"</font>"
            line += "<tr><td style='padding-right:10px'>"+str(key)+"</td> <td style='padding-right:10px'> "+ \
                    "L"+str(buildingSettings[key].zooLevel)+"</td> <td><i>"+percent+"%</i></td></tr>"

    for key, value in gameInfo.communities.items():
        if buildingSettings[key].zooLevel == i and value == 1:
            percent = gameInfo.communitiesCompletePercent[key]
            if percent > 100:
                percent = "<font color='darkred'>"+str(percent)+"</font>"
            else:
                percent = "<font color='green'>"+str(percent)+"</font>"
            line += "<tr style='font-weight: bold;'><td style='padding-right:10px'>"+str(key)+"</td> <td style='padding-right:10px'> "+ \
                    "L"+str(buildingSettings[key].zooLevel)+"</td> <td><i>"+percent+"%</i></td></tr>"

line += "</table>"

writeShortLog("darkblue", line)

print ""
print "total "+str(x)+" steps"
writeHtmlFoot()
f.close()