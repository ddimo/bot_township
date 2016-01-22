class gameInfoClass:
    def __init__(self):
        self.countZooCommunityChest = 0
        self.chestWithoutLandDeed = 0
        self.playerLevel = 40
        self.zooLevel = 1

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

        self.paddocks = dict()
        self.communities = dict()

class buildingReq:
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