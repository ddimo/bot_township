# coding=utf-8
from classes import *

buildingSettings = dict()
gameInfo = gameInfoClass()
upgradesReqs = dict()
expandReqs = [0]
animalsReqs = dict()
ratingToLevelup = dict()
ratingForChest = dict()
gemLimitRanges = []
_gemsWithCorrectionWeightCoefficient = 0

f = open ("result.html","w")
fshort = open ("short_result.html","w")

buildingMatList = ["Brick", "Plita", "Glass", "zooBuildingMaterial", "zooServiceMaterial1", "zooServiceMaterial2", "zooServiceMaterial3"]
zooBuildingMatList = ["zooBuildingMaterial", "zooServiceMaterial1", "zooServiceMaterial2", "zooServiceMaterial3"]
gemsList = ["gem1", "gem2", "gem3", "gem4"]
expansionMatList = ["axe", "TNT", "pick", "zooLandDeed"]
warehouseMatList = ["nailMat", "paintRedMat", "hammerMat"]

extraGemsRate = {"Plane": [0, 0.2, 0.57, 0.9, 0.97, 0.92, 0.98, 0.92, 0.98, 0.98, 0.98, 1.23],
                 "Mine": [0, 0.1, 0.12, 0.18, 0.28, 0.24, 0.21, 0.15, 0.14, 0.13, 0.12, 0.19],
                 "ALL": [0, 0, 13.0, 6.0, 6.0, 6.0, 6.0, 5.0, 5.0, 4.0, 4.0, 4.0, 3.5, 3.5, 3.0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5]}

extraZooMatsRate = [0, 1.37, 2.13, 2.48, 1.69, 1.03, 0.9, 0.57, 0.51, 0.41, 0.36, 0.28, 0.3, 0.2, 0.24, 0.17, 0.18, 0.11, 0.17, 0.1, 0.1]

gemsFromPlaneRate = [0, 0.2, 0.57, 0.9, 0.97, 0.92, 0.98, 0.92, 0.98, 0.98, 0.98, 1.23] # камней из самолета на каждый камень в зоопарке, на уровне
gemsFromMineRate = [0, 0.1, 0.12, 0.18, 0.28, 0.24, 0.21, 0.15, 0.14, 0.13, 0.12, 0.19] # камней из шахты на каждый камень в зоопарке

# gemsLimits = {"gem1":25, "gem2":18, "gem3":13, "gem4":5}

# enough materials for upgrade #1 in zoo_caffe (needed: zooBuildingMaterial 1, Plita 2, zooServiceMaterial2 1)
# not upgrading, saving (0 times already) for zoo_eatery (needed: Glass 3, Brick 3, zooServiceMaterial1 1)