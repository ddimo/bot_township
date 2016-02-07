from classes import *

buildingSettings = dict()
gameInfo = gameInfoClass()
upgradesReqs = dict()
expandReqs = [0]
animalsReqs = dict()
ratingToLevelup = dict()
ratingForChest = dict()

f = open ("result.html","w")
fshort = open ("short_result.html","w")

buildingMatList = ["Brick", "Plita", "Glass", "zooBuildingMaterial", "zooServiceMaterial1", "zooServiceMaterial2", "zooServiceMaterial3"]
gemsList = ["gem1", "gem2", "gem3", "gem4"]
expansionMatList = ["axe", "TNT", "pick", "zooLandDeed"]
warehouseMatList = ["nailMat", "paintRedMat", "hammerMat"]

# enough materials for upgrade #1 in zoo_caffe (needed: zooBuildingMaterial 1, Plita 2, zooServiceMaterial2 1)
# not upgrading, saving (0 times already) for zoo_eatery (needed: Glass 3, Brick 3, zooServiceMaterial1 1)