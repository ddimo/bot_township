# coding=utf-8

from gather_info import *
import shared

ITERATIONS = 100
MAX_ZOO_LEVEL = 37

for i in range(1,MAX_ZOO_LEVEL):
    gemsSavingsAtLevel['gem1'][i] = list()
    gemsSavingsAtLevel['gem2'][i] = list()
    gemsSavingsAtLevel['gem3'][i] = list()
    gemsSavingsAtLevel['gem4'][i] = list()

writeHtmlHead('result')
writeHtmlHead('short_result')

for passing in range(1,ITERATIONS+1):

    # в начале строим туториальный загон для медведя, покупаем медведя и строим кафе
    writeLog("pink","building <b>paddock_bear</b> (tutorial)",gameInfo)
    gameInfo.paddocks["paddock_bear"] = 1
    gameInfo.paddocksCompletePercent["paddock_bear"] = 0
    writeLog("orange","buying new animal for <b>paddock_bear</b> (tutorial)",gameInfo)
    gameInfo.paddocksTotalAnimals["paddock_bear"] = 1
    writeLog("lime","building <b>zoo_eatery</b> (tutorial)",gameInfo)
    gameInfo.communities["zoo_eatery"] = 1
    gameInfo.communitiesCompletePercent["zoo_eatery"] = 0

    justLeveluped = 0

    x = 0

    # while gameInfo.paddocksTotalAnimals['paddock_zebra']<4:
    while gameInfo.zooLevel<MAX_ZOO_LEVEL:
        x += 1
        # print ""
        writeLog("normal","&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;",gameInfo)
        # print str(x)+")"

        # получили рандомный материал в дропе и увеличили его количество в сохранке
        chestContentTuple = GenerateZooCommunityChestContent(gameInfo)
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
            AddGems(chestContent,True,gameInfo)
        if "zoo" in chestContent:
            gameInfo.materialsFromZoo += 1

        # раз в Y сундуков увеличим количество городских стройматериалов, как будто они приехали на поезде
        y = 15
        if gameInfo.zooChestCounter % y == 0:
            if gameInfo.axe < 7: gameInfo.axe += 3
            if gameInfo.pick < 7: gameInfo.pick += 3
            if gameInfo.TNT < 7: gameInfo.TNT += 3
            rand = random.randint(1,3)
            if rand == 1:
                if gameInfo.Brick < avrgCityMatsAmmount[gameInfo.zooLevel]: gameInfo.Brick += 10
                if gameInfo.Glass < avrgCityMatsAmmount[gameInfo.zooLevel]: gameInfo.Glass += 7
                if gameInfo.Plita < avrgCityMatsAmmount[gameInfo.zooLevel]: gameInfo.Plita += 5
            elif rand == 2:
                if gameInfo.Glass < avrgCityMatsAmmount[gameInfo.zooLevel]: gameInfo.Glass += 10
                if gameInfo.Plita < avrgCityMatsAmmount[gameInfo.zooLevel]: gameInfo.Plita += 7
                if gameInfo.Brick < avrgCityMatsAmmount[gameInfo.zooLevel]: gameInfo.Brick += 5
            else:
                if gameInfo.Plita < avrgCityMatsAmmount[gameInfo.zooLevel]: gameInfo.Plita += 10
                if gameInfo.Brick < avrgCityMatsAmmount[gameInfo.zooLevel]: gameInfo.Brick += 7
                if gameInfo.Glass < avrgCityMatsAmmount[gameInfo.zooLevel]: gameInfo.Glass += 5


        if (chestContentTuple[1] == "buildingmat" or chestContentTuple[1] == "upgrademat") and (chestContent in buildingMatList):
            if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
            else: gameInfo.levelDropHelped[chestContent] += 1
            writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> dropped <font color='red'><b>"+chestContent+"</b></font>",gameInfo)

        elif (chestContentTuple[1] == "needgem") and (chestContent in gemsList):
            if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
            else: gameInfo.levelDropHelped[chestContent] += 1
            writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> dropped <font color='blue'><b>"+chestContent+"</b></font> <font size='2'>(from needGem)</font>",gameInfo)

        elif (chestContentTuple[1] == "randomgem") and (chestContent in gemsList):
            if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
            else: gameInfo.levelDropHelped[chestContent] += 1
            writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> dropped <font color='green'><b>"+chestContent+"</b></font> <font size='2'>(from randomGem)</font>",gameInfo)

        elif (chestContentTuple[1] == "getnextgem") and (chestContent in gemsList):
            if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
            else: gameInfo.levelDropHelped[chestContent] += 1
            writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> dropped <font color='green'><b>"+chestContent+"</b></font> <font size='2'>(from GetNextGem)</font>",gameInfo)

        elif (chestContentTuple[1] == "warehousemat") and (chestContent in warehouseMatList):
            if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
            else: gameInfo.levelDropHelped[chestContent] += 1
            writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> dropped <font color='orange'><b>"+chestContent+"</b></font> <font size='2'></font>",gameInfo)

        elif (chestContentTuple[1] == "expandmat") and (chestContent in expansionMatList):
            if chestContent not in gameInfo.levelDropHelped: gameInfo.levelDropHelped[chestContent] = 1
            else: gameInfo.levelDropHelped[chestContent] += 1
            writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> dropped <font color='pink'><b>"+chestContent+"</b></font> <font size='2'></font>",gameInfo)

        else:
            writeLog("normalBig","#"+str(x)+" &mdash; <img src='img/"+chestContent+".png' valign='middle'> "+chestContent+" ",gameInfo)

        # print "dropped", chestContent

        ################################ проверим не настало ли время добавить камни с самолета и доп. материалы
        AddExtraGems("ALL",gameInfo)
        AddExtraMaterials(gameInfo)
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

            line += "Extra gems: <br>"
            for key, value in sorted(gameInfo.extraGems.iteritems()):
                 line += "&nbsp; "+key+" = <b>"+str(value)+"</b><br>"

            line += "Extra materials: <br>"
            for key, value in sorted(gameInfo.extraMats.iteritems()):
                 line += "&nbsp; "+key+" = <b>"+str(value)+"</b><br>"
            line += "</small>"

            gameInfo.levelDrop.clear()
            gameInfo.levelDropHelped.clear()
            gameInfo.extraGems.clear()
            gameInfo.extraMats.clear()
            writeLog("darkblue", line,gameInfo)
            writeShortLog("darkblue", line)
            # print "levelup "+str(gameInfo.zooLevel)

            # продадим излишки зоо-материалов
            if gameInfo.zooLevel < 20:
                if gameInfo.zooServiceMaterial1 > 40:
                    gameInfo.zooServiceMaterial1 = 40
                if gameInfo.zooServiceMaterial2 > 40:
                    gameInfo.zooServiceMaterial2 = 40
                if gameInfo.zooServiceMaterial3 > 40:
                    gameInfo.zooServiceMaterial3 = 40

            # запишем данные о накоплениях камней в общий лист средних значений
            gemsSavingsAtLevel['gem1'][gameInfo.zooLevel-1].append(gameInfo.gem1)
            gemsSavingsAtLevel['gem2'][gameInfo.zooLevel-1].append(gameInfo.gem2)
            gemsSavingsAtLevel['gem3'][gameInfo.zooLevel-1].append(gameInfo.gem3)
            gemsSavingsAtLevel['gem4'][gameInfo.zooLevel-1].append(gameInfo.gem4)

            # time.sleep(0.3)

        # пробежимся по всем зданиям и проверим, нельзя ли построить доступное
        while TryBuild(gameInfo):
            # print "try building more"
            aa = 0

        # пробежимся по доступным апгрейдам и проверим, нельзя ли проапгрейдить комьюнити
        if gameInfo.zooLevel < 666: # чтобы можно было отключить апгрйды после какого-нибудь уровня
            if gameInfo.zooLevel > 20:
                shared.MAX_WAIT_FOR_UPGRADE += 50
            availableUpgrade = FindUpdateToBuy(gameInfo)
            if availableUpgrade:
                ubid = availableUpgrade[0] # идентификатор здания
                un = availableUpgrade[1] # номер апгрейда
                line = GetBuildingReqsLine("upgrade", ubid, un, gameInfo)
                writeLog("normalSmall","<i>enough materials for upgrade #"+str(un)+" in "+str(ubid)+" (needed: "+line+")",gameInfo)
                availableToBuild = FindAvailableNotBuilt(gameInfo)
                if availableToBuild:
                    comparision = CompareForZooMats(availableToBuild,ubid,un,gameInfo)
                if not availableToBuild or not comparision or gameInfo.upgradeWait >= shared.MAX_WAIT_FOR_UPGRADE:
                    # do если нет доступных для строительства
                    # или доступно, но нет совпадения по материалам с доступным
                    # или доступно, есть совпадение, но подождали уже долго
                    DoUpgrade(ubid,un,gameInfo)
                    writeLog("normalSmall", "<font color='red'>bought upgrade</font>",gameInfo)
                    gameInfo.upgradeWait = 0
                else:
                    # не будем покупать апгрейд пока копим на строительство доступного загона/комьюнити
                    if gameInfo.upgradeWait < shared.MAX_WAIT_FOR_UPGRADE:
                        line = GetBuildingReqsLine("build",availableToBuild,0,gameInfo)
                        writeLog("normalSmall","not upgrading, saving ("+str(gameInfo.upgradeWait)+" times already) for "+availableToBuild+" (needed: "+line+")",gameInfo)
                        if gameInfo.communities['zoo_eatery'] == 1: # пока не построили zoo_eatery - не будем апгрейдить вообще
                            gameInfo.upgradeWait += 1

        # выведем список зданий, которые еще не построены, но уже доступны - со списком требований
        for key, value in gameInfo.paddocks.items():
            if value == 0:                                                  # еще не построено
                if buildingSettings[key].zooLevel <= gameInfo.zooLevel:     # доступно по уровню
                    line = GetBuildingReqsLine("build",key,0,gameInfo)
                    writeLog("normalSmall","not yet built <b>"+key+"</b> ("+line+")",gameInfo)
        for key, value in gameInfo.communities.items():
            if value == 0:                                                  # еще не построено
                if buildingSettings[key].zooLevel <= gameInfo.zooLevel:     # доступно по уровню
                    line = GetBuildingReqsLine("build",key,0,gameInfo)
                    writeLog("normalSmall","not yet built <b>"+key+"</b> ("+line+")",gameInfo)

        # пробежимся по доступным загонам и проверим, можно ли купить животное
        while TryBuyNewAnimal(gameInfo):
            #print "try to buy another animal"
            aa = 0

        # попробуем купить расширение
        while TryExpand(gameInfo):
            #print "try to expand"
            aa = 0

        writeLog("normalSmall","&nbsp;",gameInfo)

        line = ""
        for g in gemsList:
            line += str(getattr(gameInfo,g))+" <img src='img/"+g+".png' valign='middle'> &nbsp; "
        writeLog("normalSmallOrange", line, gameInfo)
        if justLeveluped:
            writeShortLog("normalSmallOrange", line)

        line = str(gameInfo.zooLandDeed)+" <img src='img/zooLandDeed.png' valign='middle'> &nbsp; "+ \
                str(gameInfo.zooBuildingMaterial)+" <img src='img/zooBuildingMaterial.png' valign='middle'> &nbsp; "+ \
                str(gameInfo.zooServiceMaterial1)+" <img src='img/zooServiceMaterial1.png' valign='middle'> &nbsp; "+ \
                str(gameInfo.zooServiceMaterial2)+" <img src='img/zooServiceMaterial2.png' valign='middle'> &nbsp; "+ \
                str(gameInfo.zooServiceMaterial3)+" <img src='img/zooServiceMaterial3.png' valign='middle'>"
        writeLog("normalSmallGreen", line,gameInfo)
        if justLeveluped:
            writeShortLog("normalSmallGreen", line)

        line = str(gameInfo.Brick)+" <img src='img/Brick.png' valign='middle'> &nbsp; "+ \
                str(gameInfo.Plita)+" <img src='img/Plita.png' valign='middle'> &nbsp; "+ \
                str(gameInfo.Glass)+" <img src='img/Glass.png' valign='middle'> &nbsp; "+ \
                str(gameInfo.pick)+" <img src='img/pick.png' valign='middle'> &nbsp; "+ \
                str(gameInfo.axe)+" <img src='img/axe.png' valign='middle'> &nbsp; "+ \
                str(gameInfo.TNT)+" <img src='img/TNT.png' valign='middle'>"
        writeLog("normalSmallBlue", line,gameInfo)
        if justLeveluped:
            writeShortLog("normalSmallBlue", line)
            writeShortLog("normal","&nbsp;<br>&nbsp;")
            justLeveluped = 0


    # в конце каждого прогона запишем в лист данные о процентах текущего прогона
    for i in range(1,40):
        for key, value in buildingSettings.items():
            if value.zooLevel == i:
                if "paddock_" in value.id:
                    percent = gameInfo.paddocksCompletePercent[key]
                    paddocksCompletePercentAll[key].append(percent)
                elif "zoo_" in value.id:
                    percent = gameInfo.communitiesCompletePercent[key]
                    communitiesCompletePercentAll[key].append(percent)

    gameInfo = gameInfoClass()
    for reqsElem in reqs.iter():
        if 'id' in reqsElem.attrib:
            cur_id = reqsElem.attrib['id']
        if "paddock_" in cur_id:
            gameInfo.paddocks[cur_id] = 0
            gameInfo.paddocksTotalAnimals[cur_id] = 0
            gameInfo.paddocksCompletePercent[cur_id] = 0
        elif "zoo_" in cur_id:
            gameInfo.communities[cur_id] = 0
            gameInfo.communitiesUpgrades[cur_id] = 0
            gameInfo.communitiesCompletePercent[cur_id] = 0

    print "Iteration "+str(passing)+" completed"
    if not shared.RESULT_FILES_SAVED:
        writeHtmlFoot("result")
        writeHtmlFoot("short_result")
        shared.f.close()
        shared.fshort.close()
        shared.RESULT_FILES_SAVED = True


print "All iterations completed!"

writeHtmlHead('avrg_result')

line = "<b>Average percentage after "+str(passing)+" iterations:</b><br><br><table style='border:0px'><tr><td style='font-size:8pt'><b>id</b></td><td style='font-size:8pt'><b>open</b></td><td style='font-size:8pt'><b>complete</b></td></tr>"

for i in range(1,40):  # уровень
    for key, value in gameInfo.paddocks.items():
        if buildingSettings[key].zooLevel == i and paddocksCompletePercentAll[key]:
            percent = int(np.mean(paddocksCompletePercentAll[key]))
            if percent > 100:
                percent = "<font color='darkred'>"+str(percent)+"</font>"
            else:
                percent = "<font color='green'>"+str(percent)+"</font>"
            line += "<tr><td style='padding-right:10px'>"+str(key)+"</td> <td style='padding-right:10px'> "+ \
                    "L"+str(buildingSettings[key].zooLevel)+"</td> <td><i>"+percent+"%</i></td></tr>"

    for key, value in gameInfo.communities.items():
        if buildingSettings[key].zooLevel == i and communitiesCompletePercentAll[key]:
            percent = int(np.mean(communitiesCompletePercentAll[key]))
            if percent > 100:
                percent = "<font color='darkred'>"+str(percent)+"</font>"
            else:
                percent = "<font color='green'>"+str(percent)+"</font>"
            line += "<tr><td style='padding-right:10px; font-weight: bold;'>"+str(key)+"</td> <td style='padding-right:10px; font-weight: bold;'> "+ \
                    "L"+str(buildingSettings[key].zooLevel)+"</td> <td><i>"+percent+"%</i></td></tr>"

line += "</table>"

line += "<br><br><b>Average game savings after "+str(passing)+" iterations:</b><br><br>" \
        "<table style='border:0px'>" \
        "<tr style='padding-bottom:20px'>" \
        "<td style='font-size:8pt'><b>level</b></td>" \
        "<td style='font-size:8pt; text-align: center' colspan='4'><b>gems</b></td>" \
        "</tr>"

for i in range(1,MAX_ZOO_LEVEL):
    line += "<tr><td style='padding-right:10px; text-align:right'><b>L"+str(i)+"</b></td>"
    for g in gemsList:
        curAvrg = int(np.mean(gemsSavingsAtLevel[g][i]))
        line +="<td style='padding-left:25px'><img src='img/"+g+".png' valign='middle'>"+ str(curAvrg)+"</td> "
    line += "</tr>"

line += "</table>"

writeAvrgLog("darkblue", line)

print ""
print "total "+str(x)+" steps"
writeHtmlFoot("avrg_result")
shared.favrg.close()