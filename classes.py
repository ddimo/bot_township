class gameInfoClass:
    def __init__(self):
        self.countZooCommunityChest = 0
        self.chestWithoutLandDeed = 0
        self.playerLevel = 40
        self.zooLevel = 1
        self.zooExpandLevel = 0
        self.rating = 0

        self.Brick = 30
        self.Glass = 30
        self.Plita = 30
        self.zooBuildingMaterial = 0
        self.zooServiceMaterial1 = 0
        self.zooServiceMaterial2 = 0
        self.zooServiceMaterial3 = 0
        self.zooLandDeed = 0
        self.hammerMat = 10
        self.nailMat = 10
        self.paintRedMat = 10
        self.pick = 10
        self.axe = 10
        self.TNT = 10

        self.gem1 = 10
        self.gem2 = 8
        self.gem3 = 6
        self.gem4 = 0

        self.wasnot = {'gem1':0, 'gem2':0, 'gem3':0, 'gem4':0}

        self.paddocks = dict()
        self.paddocksTotalAnimals = dict()
        self.communities = dict()
        self.communitiesUpgrades = dict()

        self.upgradeWait = 0
        self.chestWithoutLandDeed = 0
        self.zooChestCounter = 0

        self.levelDrop = dict()
        self.levelDropHelped = dict()

class buildingSettingsClass:
    def __init__(self):
        self.id = ""
        self.Brick = 0
        self.Plita = 0
        self.Glass = 0
        self.zooBuildingMaterial = 0
        self.zooServiceMaterial1 = 0
        self.zooServiceMaterial2 = 0
        self.zooServiceMaterial3 = 0
        self.price = 0
        self.zooLevel = 0
        self.bonusRating = 0


class buildingUpgradesSettingsClass:
    def __init__(self):
        self.Brick = 0
        self.Plita = 0
        self.Glass = 0
        self.zooBuildingMaterial = 0
        self.zooServiceMaterial1 = 0
        self.zooServiceMaterial2 = 0
        self.zooServiceMaterial3 = 0
        self.animalsCount = 0


class animalReqsClass:
    def __init__(self):
        self.gem1 = 0
        self.gem2 = 0
        self.gem3 = 0
        self.gem4 = 0



class zooExpansionClass:
    def __init__(self):
        self.animals = 0
        self.zooLandDeed = 0
        self.pick = 0
        self.axe = 0
        self.TNT = 0



class weightsList:
    def __init__(self):
        self.Brick = 0
        self.Plita = 0
        self.Glass = 0
        self.zooBuildingMaterial = 0
        self.zooServiceMaterial1 = 0
        self.zooServiceMaterial2 = 0
        self.zooServiceMaterial3 = 0