import random
from gameInfo import *
from utils import *
import xml.etree.ElementTree as xml

gameInfo = gameInfoClass()

gameBalanceXml = xml.parse('../township/base/GameBalance.xml', parser = CommentsParser())
gameBalanceRoot = gameBalanceXml.getroot()

attrs = vars(gameInfo)
print ', '.join("%s: %s" % item for item in attrs.items())
print ""

for x in range(0,10):
    randomMat = GenerateZooCommunityChestContent(gameInfo)
    curvalue = getattr(gameInfo,randomMat)
    setattr(gameInfo,randomMat,curvalue+1)
    print "random value is:", randomMat

attrs = vars(gameInfo)
print ""
print ', '.join("%s: %s" % item for item in attrs.items())