'''
Created on Feb 23, 2014

@author: Matthew
'''
#Karlim
import pygame
import os
import sys
import random
import math
import time
#BALROG
path = os.path.abspath(sys.argv[0]) # more than one class needs path
pathIdx = path.rfind("\\")
path = path[:pathIdx+1]

class KhazadDum():
    terrainXorig = 0
    terrainYorig = 0
    terrainIndex = 0
    terrainXindex = 0
    terrainYindex = 0
    maxRow = 0
    
    clock = pygame.time.Clock()
    FPS = 40
    deltaTime = clock.tick(FPS)  
    loopNum = 0
    
    hole = pygame.image.load(path+"\\Images\\Hole.png") 
    stone = pygame.image.load(path+"\\Images\\Stone.jpg")
    iron = pygame.image.load(path+"\\Images\\Iron.png")
    silver = pygame.image.load(path+"\\Images\\Silver.png")
    gold = pygame.image.load(path+"\\Images\\Gold.png")    
    sapphire = pygame.image.load(path+"\\Images\\Sapphire.png")
    ruby = pygame.image.load(path+"\\Images\\Ruby.png")    
    diamond = pygame.image.load(path+"\\Images\\Diamond.png")
    emerald = pygame.image.load(path+"\\Images\\Emerald.png")
    mithril = pygame.image.load(path+"\\Images\\Mithril.png")
    shopImage = pygame.image.load(path+"\\Images\\ShopTable.jpg")
    tileWidth = hole.get_width()
    tileHeight = hole.get_height() # hole is a square, but might as well keep both variables in case I decide to change it
    height = 640
    width = 800
    numOfColumns = (width*3//tileWidth)
    
    screen = pygame.display.set_mode((width,height))
    miningScreen = pygame.Surface(screen.get_size())     
    miningScreen = miningScreen.convert()
    shopScreen = pygame.Surface(screen.get_size())
    shopScreen = shopScreen.convert()
    shopImagePos = shopImage.get_rect()
    shopImagePos.centerx = shopScreen.get_rect().centerx
    shopOrMining = "mining"
    visitedShop = True
    messageList = []
    messageDict = {}
    
    chanceDict = {"iron": 1, "silver": 10, "gold": 30, "sapphire": 45, "ruby":50, "diamond": 70, "emerald":80, "mithril":100}
    priceOreDict = {"iron": 30, "silver": 100, "gold": 250, "sapphire": 750, "ruby":2000, "diamond": 5000, "emerald":20000, "mithril":100000}
    pickDict = {(5,172,150,222):["Iron Pick",2,1000, "speed"], (5,224,150,274):["Steel Pick",3,2000, "speed"], 
                (5,278,150,328):["Adamant Pick",4,5000, "speed"], (5,331,150,383):["Mithril Pick",5,10000, "speed"], 
                (5,385,150,435):["Galvorn Pick",6,20000, "speed"]}
    fitnessDict = {(153,172,299,222):["DMI average",4,2000, "hunger growth"], (153,224,299,274):["Traveler",3,5000, "hunger growth"], 
                   (153,278,299,328):["Fit as a Fiddle",2,20000, "hunger growth"],(153,331,299,383):["Lean Mean Digging Machine",1,100000, "hunger growth"]} 
    foodStorageDict = {(302,172,447,222):["Honey Cake",1000,1500, "food storage"], (302,224,447,274):["Cram",2000,3000, "food storage"],
                       (302,278,447,328):["Miruvor",5000,10000, "food storage"], (302,331,447,383):["Petty-Dwarf Roots",20000,20000, "food storage"],
                       (302,385,447,435):["Beard Storage",100000,50000, "food storage"]}   
    oreCapacityDict = {(450,172,597,222):["Cargo Shirt",20,1000,"capacity"], (450,224,597,274):["Bucket Hat",40,2000,"capacity"], 
                (450,278,597,328):["Zirak Pack",100,5000,"capacity"], (450,331,597,383):["Sidecart",200,20000,"capacity"], 
                (450,385,597,435):["Bucket Lift","instant",200000,"capacity"]}
    categoryDict = {(5,172,150,435):pickDict, (153,172,299,435):fitnessDict, (302,172,447,435):foodStorageDict,
                    (450,172,597,435):oreCapacityDict}
    
    balrog = pygame.image.load(path+"\\Images\\Balrog.jpg")
    balrog = pygame.transform.scale(balrog, (width, height)) 
    balrogPos = balrog.get_rect()
    balrogPos.centerx = screen.get_rect().centerx #Balrog is centered and will come up from the bottom of the screen
    balrogPos.top = screen.get_rect().bottom
    holeRows = 0
    balrogLoopNum = 0
    
    def __init__(self):
        pygame.init() 
        pygame.display.set_caption("Khazad-dum")
        self.bigFont = pygame.font.Font(None, 36) #base class
        self.smallFont = pygame.font.Font(None, 24) #base class
        self.MakeMap()
        self.LoadDwarfSprite()          
        self.minerWidth = self.miner.rect[2]
        self.minerHeight = self.miner.rect[3] 
        self.MainLoop()
        
    def MainLoop(self):           
        while True:  
            self.loopNum += 1  
            if self.shopOrMining == "mining":    
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: # allows for closing the program without Windows Task Manager
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        self.miner.AttemptToMove(event.key)
                    elif event.type == pygame.KEYUP:
                        self.miner.Stop(event.key)
                self.miner.Move(self.mapList)
                self.CheckForHQ()
                self.ChangeToHole(self.miner.minerIndex, self.miner.rect[0], self.miner.rect[1], self.miner.xMoveTrue, self.miner.yMoveTrue)        
                self.DrawMiningScreen()   ############ MESSY, redraws whole map every tick to clear movement trail
                self.minerSprite.draw(self.screen)
                if self.loopNum % self.FPS == 0: # loopNum will continue, but eating only occurs while mining
                    self.Eat()
                    
            elif self.shopOrMining == "shop":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: # allows for closing the program without Windows Task Manager
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.Buy(pygame.mouse.get_pos())
                        self.CheckForExitShop(pygame.mouse.get_pos())
                self.DrawShop()
            
            elif self.shopOrMining == "balrog": #ending
                self.Balrog()                
            pygame.display.update()
            
    def LoadDwarfSprite(self):
        #Load the sprites that we need
        self.miner = Miner(self.numOfColumns, self.tileWidth, self.tileHeight)
        self.minerSprite = pygame.sprite.RenderPlain((self.miner))
                
    def DrawMiningScreen(self):
        moveX = 0
        moveY = 0
        self.terrainIndex = 0
        if self.miner.minerIndex%self.numOfColumns >= (self.width//self.tileWidth)/2:
            # need to shift terrain left or right
            if self.miner.minerIndex%self.numOfColumns >= self.numOfColumns-(self.width//self.tileWidth)/2:
                self.terrainXindex = self.numOfColumns-(self.width//self.tileWidth) # no shifting at far right
            else:
                self.terrainXindex = (self.miner.minerIndex%self.numOfColumns)-(self.width//self.tileWidth)/2 # shift otherwise
            if self.terrainXindex > self.terrainXorig: # if the original is 1 to the left, 
                self.miner.rect.move_ip(-self.tileWidth,0) # then the dwarf should be shifted one left
                self.terrainXorig = self.terrainXindex
            elif self.terrainXindex < self.terrainXorig:  # so if the original is 1 to the right, 
                self.miner.rect.move_ip(self.tileWidth,0) # then the dwarf should be shifted one right
                self.terrainXorig = self.terrainXindex
            self.terrainIndex += self.terrainXindex # adds the x component to shifting

        if self.miner.minerIndex//self.numOfColumns >= (self.height//self.tileHeight)/2: # need to check for both, not one or the other
            # need to shift terrain up or down
            self.terrainYindex = ((self.miner.minerIndex//self.numOfColumns)-((self.height//self.tileHeight)/2))*self.numOfColumns # shift otherwise
            if self.terrainYindex > self.terrainYorig: # if the original is higher, 
                self.miner.rect.move_ip(0,-self.tileHeight) # then the dwarf should be shifted one up
                self.terrainYorig = self.terrainYindex
                if len(self.mapList)//self.numOfColumns < (self.terrainYindex+(self.numOfColumns*(self.height//self.tileHeight)))//self.numOfColumns:
                    self.CreateRow(self.numOfColumns) # adds extra row to bottom of map when needed
            elif self.terrainYindex < self.terrainYorig:  # if the original is lower, 
                self.miner.rect.move_ip(0,self.tileHeight) # then the dwarf should be shifted one down
                self.terrainYorig = self.terrainYindex
            self.terrainIndex += self.terrainYindex # adds the y component to shifting
            
        elif not self.miner.minerIndex%self.numOfColumns >= (self.width//self.tileWidth)/2: # everything is normal. 
            # Two If statements, 2nd doesn't need to be redone, but the 1st does.
            self.terrainIndex = 0
            
        yCoord = 0
        while yCoord < self.height:
            xCoord = 0
            while xCoord < self.width:
                self.miningScreen.blit(getattr(self,self.mapList[self.terrainIndex]),(xCoord,yCoord))
                self.terrainIndex += 1
                xCoord += self.tileWidth
            yCoord += self.tileHeight
            self.terrainIndex += self.numOfColumns-((self.width//self.tileWidth)) # skips by tiles off screen edge
        if self.shopOrMining != "balrog":
            self.UpdateOverlay()
        self.screen.blit(self.miningScreen, (0,0))
    
    def MakeMap(self):
        self.mapList = []
        for row in range(self.height//self.tileHeight): # 15 necessary for starting window
            self.CreateRow(self.numOfColumns)
        self.mapList[0] = "hole" # have to start on a hole
        
    def CreateRow(self, columns): 
        holesOnly = False
        oreList = []    
        num = 0
        for column in range(columns): # for each tile
            num += 1
            randomList = []
            for oreName in self.chanceDict.keys():
                if self.maxRow <= 110: # patterned up until this depth
                    if math.fabs(self.maxRow-self.chanceDict[oreName])<=20:
                        for num in range(20-math.trunc(math.fabs(self.maxRow-self.chanceDict[oreName]))): # adds number of chances <20 for specific ores
                            randomList.append(oreName)
                else: # past start of mithril, free for all tons of ore all over. More of a treasure hunt for the best ones  
                    if self.maxRow <= 120 or ((self.maxRow-110)%(self.height//self.tileHeight) < (self.height//self.tileHeight)//2):
                        for each in range(100): # 10 bonus and then alternating
                            randomList.append(oreName)
                    else:
                        holesOnly = True
            for each in range(60): 
                randomList.append("stone")
            for each in range(10):
                randomList.append("hole")
            if holesOnly: # for the balrog/bonus levels
                oreList.append("hole")                
            else:
                oreList.append(random.choice(randomList)) 
        if holesOnly:
            self.holeRows += 1
        if self.holeRows == ((self.height//self.tileHeight)//2)*3 - 1: # two half windows of bonanza, then balrog after digging out last solid row
            self.shopOrMining = "balrog"
            for row in range(15):
                self.mapList.extend(oreList)
        self.maxRow += 1
        self.mapList.extend(oreList)        
    
    def ChangeToHole(self, minerIndex, xMiner, yMiner, xMove, yMove): # digs out holes
        if self.mapList[minerIndex] != "hole" and xMove < 0 and xMiner%self.tileWidth < (self.tileWidth//2): # digging left
            self.AddToOreInventory(minerIndex)
            self.mapList[minerIndex] = "hole"
        if self.mapList[minerIndex+1] != "hole" and xMove > 0 and xMiner%self.tileWidth > (self.tileWidth*3//2)-self.minerWidth: # digging right
            self.AddToOreInventory(minerIndex+1)
            self.mapList[minerIndex+1] = "hole"
        if self.mapList[minerIndex+self.numOfColumns] != "hole" and yMove > 0 and yMiner%self.tileHeight > (self.tileHeight*3//2)-self.minerHeight: # digging down
            self.AddToOreInventory(minerIndex+self.numOfColumns)
            self.mapList[minerIndex+self.numOfColumns] = "hole"
    
    def AddToOreInventory(self, oreIndex):
        if self.mapList[oreIndex] in self.chanceDict.keys() and len(self.miner.oreInventory) < self.miner.accessoryInventory["capacity"]:
            self.miner.oreInventory.append(self.mapList[oreIndex]) 
        if len(self.miner.oreInventory) >= self.miner.accessoryInventory["capacity"]:
            self.AddToMessageList("ore capacity filled")
    
    def CheckForHQ(self):
        if self.miner.minerIndex == 0:            
            self.Sell()
            self.Resupply()  
            if self.visitedShop == False:
                self.shopOrMining = "shop"
        if self.miner.minerIndex != 0: # you can visit the shop anytime, but if you are already in base than it will not reset until you leave
            self.visitedShop = False         
        if self.miner.accessoryInventory["capacity"] == "instant":
            self.Sell() # sells every loop
            
    def Resupply(self):
        costFoodLost = (self.miner.accessoryInventory["food storage"]-self.miner.accessoryInventory["actual food"])//10
        cost = self.miner.accessoryInventory["gold"] if (costFoodLost > self.miner.accessoryInventory["gold"]) else costFoodLost
        # spends what miner has
        if self.miner.accessoryInventory["gold"] == 0:
            self.AddToMessageList("you have no money for food")
        else:
            self.miner.accessoryInventory["actual food"] = self.miner.accessoryInventory["food storage"]  
            self.miner.accessoryInventory["gold"] -= cost  
            self.AddToMessageList("you bought food for " + str(cost)+" gold") 
            # shopping becomes possible on the next loop so everything is sold before visiting
            
    def Sell(self):
        if len(self.miner.oreInventory) > 0: # don't repeat
            for ore in self.miner.oreInventory:
                self.miner.accessoryInventory["gold"] += self.priceOreDict[ore]
            self.miner.oreInventory = []
                
    def AddToMessageList(self, message):
        if message not in self.messageList:
            self.messageList.append(message)
        self.messageDict[message] = self.loopNum + self.FPS*4 # either creates or renews the expiration
        
    def DrawMessages(self,bottomTextPos):
        listNum = 0
        for message in self.messageList:
            if self.messageDict[message] < self.loopNum:
                self.messageDict.pop(message) # removes message when time has elapsed
                self.messageList.remove(message)
            if self.shopOrMining == "mining":
                setattr(self, "msgText"+str(listNum), self.smallFont.render(message, 1, (245,193,0))) #RGB
                setattr(self, "msgTextPos"+str(listNum), getattr(self,"msgText"+str(listNum)).get_rect())
                setattr(getattr(self, "msgTextPos"+str(listNum)),"centerx", self.miningScreen.get_rect().centerx) # centers it
                if listNum != 0: # takes from previous message
                    setattr(getattr(self, "msgTextPos"+str(listNum)),"top", getattr(getattr(self, "msgTextPos"+str(listNum-1)),"bottom"))
                else: # takes from lowest constant text. Different between the shop and mining screens
                    setattr(getattr(self, "msgTextPos"+str(listNum)),"top", bottomTextPos) 
                self.miningScreen.blit(getattr(self, "msgText"+str(listNum)), getattr(self, "msgTextPos"+str(listNum)))
            elif self.shopOrMining == "shop":
                setattr(self, "msgText"+str(listNum), self.smallFont.render(message, 1, (0,0,0))) #RGB
                setattr(self, "msgTextPos"+str(listNum), getattr(self,"msgText"+str(listNum)).get_rect())
                setattr(getattr(self, "msgTextPos"+str(listNum)),"left", 0) # centers it
                if listNum != 0: # takes from previous message
                    setattr(getattr(self, "msgTextPos"+str(listNum)),"top", getattr(getattr(self, "msgTextPos"+str(listNum-1)),"bottom"))
                else: # takes from lowest constant text. Different between the shop and mining screens
                    setattr(getattr(self, "msgTextPos"+str(listNum)),"top", bottomTextPos) 
                self.shopScreen.blit(getattr(self, "msgText"+str(listNum)), getattr(self, "msgTextPos"+str(listNum)))
            listNum += 1
            
                        
    def UpdateOverlay(self):
        moneyText = self.bigFont.render(("Gold: " + str(self.miner.accessoryInventory["gold"])), 1, (245,193,0)) #RGB
        foodText = self.bigFont.render(("Food Level:" + 
            str(self.miner.accessoryInventory["actual food"]*100.0/self.miner.accessoryInventory["food storage"])), 1, (245,193,0))
        moneyTextPos = moneyText.get_rect()
        moneyTextPos.centerx = self.miningScreen.get_rect().centerx
        foodTextPos = foodText.get_rect()
        foodTextPos.centerx = moneyTextPos.centerx
        foodTextPos.top = moneyTextPos.bottom
        self.miningScreen.blit(moneyText, moneyTextPos)
        self.miningScreen.blit(foodText, foodTextPos)
        self.DrawMessages(foodTextPos.bottom)
            
    def DrawShop(self):
        self.shopScreen.fill((254,242,0))
        self.shopScreen.blit(self.shopImage, self.shopImagePos)
        moneyText = self.bigFont.render(("Gold: " + str(self.miner.accessoryInventory["gold"])), 1, (0,0,0)) #RGB
        moneyTextPos = moneyText.get_rect()
        self.DrawMessages(self.shopImagePos.bottom)
        self.shopScreen.blit(moneyText, moneyTextPos)
        self.screen.blit(self.shopScreen, (0,0))
        
    
    def Buy(self, mousePos):
        for categoryTuple in self.categoryDict.keys():
            if self.CheckInRectangle(categoryTuple, (mousePos[0]-self.shopImagePos.left,mousePos[1])): # finds category
                for itemTuple in self.categoryDict[categoryTuple].keys(): # keys of the sub-item-dict 
                    if self.CheckInRectangle(itemTuple, (mousePos[0]-self.shopImagePos.left,mousePos[1])): # finds item
                        if self.miner.accessoryInventory["gold"] < self.categoryDict[categoryTuple][itemTuple][2]: # checks gold level
                            self.AddToMessageList("You don't have enough gold")
                        elif not self.CheckForBetterItemThanOwned(self.categoryDict[categoryTuple][itemTuple]): 
                            self.AddToMessageList("This item is no better than what you already have")
                        else:
                            self.miner.accessoryInventory[self.categoryDict[categoryTuple][itemTuple][3]] = self.categoryDict[categoryTuple][itemTuple][1]
                            self.miner.accessoryInventory["actual food"] = self.miner.accessoryInventory["food storage"]
                            # changes attribute
                            self.miner.accessoryInventory["gold"] -= self.categoryDict[categoryTuple][itemTuple][2]
                            # buys
                            self.AddToMessageList("You have bought " + str(self.categoryDict[categoryTuple][itemTuple][0]) + " for " + str(self.categoryDict[categoryTuple][itemTuple][2]))
                        break # break once location is found by if statement
                break # break once location is found by if statement
        
    def CheckInRectangle(self, (xRectTL,yRectTL,xRectBR,yRectBR), (xCheck,yCheck)):
        if (xCheck <= xRectBR and xCheck >= xRectTL) and (yCheck <= yRectBR and yCheck >= yRectTL):
            return True
        else:
            return False
    
    def CheckForBetterItemThanOwned(self, item): 
        if item[3] == "hunger growth": # the only attribute which gets better as it decreases
            if item[1] >= self.miner.accessoryInventory[item[3]]: # attribute number
                return False # Item is not better than currently owned
            else:
                return True # Item is better than currently owned
        else: # all others grow as they get better
            if item[1] <= self.miner.accessoryInventory[item[3]]:
                return False # Item is not better than currently owned
            else:
                return True # Item is better than currently owned    
    
    def CheckForExitShop(self, mousePos):  
        if self.CheckInRectangle((546,11,575,40),(mousePos[0]-self.shopImagePos.left,mousePos[1])):
            self.shopOrMining = "mining"
            self.visitedShop = True
            self.miner.xMoveRaw = 0
            self.miner.yMoveRaw = 0 # problem with continual movement through after exiting.
            
    def Eat(self):
        self.miner.accessoryInventory["actual food"] -= self.miner.accessoryInventory["hunger growth"]*(len(self.miner.oreInventory)+1) 
        # +1 so he always eats something even on empty inventory
        if self.miner.accessoryInventory["actual food"] <= 0:
            starveText = self.bigFont.render(("You have starved to death in the mines"), 1, (245,193,0))
            starveTextPos = starveText.get_rect()
            starveTextPos.centerx = self.miningScreen.get_rect().centerx
            starveTextPos.centery = self.miningScreen.get_rect().centery
            self.screen.blit(starveText, starveTextPos)
            pygame.display.update() # it will not update otherwise because the next update is at the end of MainLoop, which is never reached stopping here
            time.sleep(3)
            sys.exit()
            
    def Balrog(self):
        self.balrogLoopNum += 1
        if self.balrogLoopNum < (self.height//self.tileHeight):
            time.sleep(.3)
            self.miner.minerIndex += self.numOfColumns # moves minerIndex so terrain will shift
            self.miner.rect.move_ip(0,self.tileHeight)
            self.DrawMiningScreen()
            self.screen.blit(self.miner.image,self.miner.rect)
        else:
            time.sleep(.05)
            self.DrawMiningScreen()
            if self.miner.rect.top < self.balrogPos.top: # eaten when reached
                self.screen.blit(self.miner.image,self.miner.rect) # miner must be before the balrog or he might cover it
            self.screen.blit(self.balrog, self.balrogPos)
            self.balrogPos.top -= 2
            if self.balrogPos.top <= self.screen.get_rect().top:
                balrogText = self.bigFont.render(("You delved too greedily and too deeply"), 1, (245,193,0))
                balrogTextPos = balrogText.get_rect()
                balrogTextPos.centerx = selWf.miningScreen.get_rect().centerx
                balrogTextPos.centery = self.miningScreen.get_rect().centery
                balrogText2 = self.bigFont.render(("In the darkness of Khazad-dum"), 1, (245,193,0))
                balrogTextPos2 = balrogText2.get_rect()
                balrogTextPos2.centerx = balrogTextPos.centerx
                balrogTextPos2.top = balrogTextPos.bottom
                balrogText3 = self.bigFont.render(("You have awoken shadow and flame"), 1, (245,193,0))
                balrogTextPos3 = balrogText3.get_rect()
                balrogTextPos3.centerx = balrogTextPos2.centerx
                balrogTextPos3.top = balrogTextPos2.bottom
                self.screen.blit(balrogText, balrogTextPos)
                self.screen.blit(balrogText2, balrogTextPos2)
                self.screen.blit(balrogText3, balrogTextPos3)
                pygame.display.update()
                time.sleep(5)
                sys.exit()

             
class Miner(pygame.sprite.Sprite):
    xMoveRaw = 0 # this will only change on being held or released by keyboard
    yMoveRaw = 0
    xMoveTrue = 0  # this will depend on whether or not the dwarf is on a tile edge
    yMoveTrue = 0
    minerXindex = 0
    minerYindex = 0
    minerIndex = 0
    oreInventory = []
    
    def __init__(self, numOfColumns, tileWidth, tileHeight):
        self.numOfColumns = numOfColumns
        self.tileWidth = tileWidth
        self.tileHeight = tileHeight
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path+"\\Images\\DwarfMiner.png") # rect is top left coords and pixel dimensions(x,y,x,y)
        self.rect = self.image.get_rect()
        self.minerWidth = self.rect[2]
        self.minerHeight = self.rect[3]
        self.accessoryInventory = {"gold":0, "food storage":500, "actual food":500, "speed":1, "capacity":10, "hunger growth":5} # tileHeight so increased size increases speed
                
    def AttemptToMove(self, key):
        # AttemptToMove is the first step of moving, but many checks have to be made first.
        if key == pygame.K_RIGHT: 
            self.xMoveRaw = 1
        elif key == pygame.K_LEFT:
            self.xMoveRaw = -1
        elif key == pygame.K_UP:
            self.yMoveRaw = -1
        elif key == pygame.K_DOWN:
            self.yMoveRaw = 1
            
    def Move(self, mapList): # this actually runs all the collision and gravity calculations
        dwarfSpeed = self.accessoryInventory["speed"]*(self.tileHeight//40)
        maxSpeed = 2*(self.tileHeight//40) if dwarfSpeed < 2*(self.tileHeight//40) else dwarfSpeed # maxSpeed is either gravity or dwarven speed. More tiles equals more gravity

        if (self.xMoveRaw == 1 and ((self.rect[0] % self.tileWidth < (self.tileWidth-self.minerWidth)) or # just within a column of tiles
        (self.rect[1] % self.tileHeight <= (self.tileHeight-self.minerHeight+maxSpeed) and mapList[self.minerIndex+1] == "hole") or # move left anywhere within the tile if a hole exists 
        (self.rect[1] % self.tileHeight in range(self.tileHeight-self.minerHeight, self.tileHeight-self.minerHeight+maxSpeed) and 
         mapList[self.minerIndex+self.numOfColumns] != "hole") or # dig right only resting on the bottom
        (mapList[self.minerIndex+self.numOfColumns+1] == "hole" and mapList[self.minerIndex+1] == "hole")) and  # if two holes to the right, don't worry about collision
        (self.minerXindex < (((self.numOfColumns-1)*self.tileWidth)+(self.tileWidth-self.minerWidth-maxSpeed)))): # right map edge
        # right only in presence of hole or on bottom tile, and not on right map edge            
            self.xMoveTrue = self.xMoveRaw*dwarfSpeed
        elif (self.xMoveRaw == -1 and ((self.rect[0] % self.tileWidth > maxSpeed) or # just within a column of tiles
        (self.rect[1] % self.tileHeight <= (self.tileHeight-self.minerHeight+maxSpeed) and mapList[self.minerIndex-1] == "hole") or 
        (self.rect[1] % self.tileHeight in range(self.tileHeight-self.minerHeight, self.tileHeight-self.minerHeight+maxSpeed) and 
         mapList[self.minerIndex+self.numOfColumns] != "hole") or # dig left only resting on the bottom
        (mapList[self.minerIndex-1] == "hole" and mapList[self.minerIndex+self.numOfColumns-1] == "hole")) and (self.minerXindex > maxSpeed)): # if two holes to the left, don't worry about collision. 2nd is the left wall 
        # left only in presence of holes or on bottom tile, and not on left map edge            
            self.xMoveTrue = self.xMoveRaw*dwarfSpeed
        else:
            self.xMoveTrue = 0

        if (self.yMoveRaw == 1 and (self.rect[1]%self.tileHeight < (self.tileHeight-self.minerHeight) or # within a row of tiles 
        self.rect[0]%self.tileWidth <= (self.tileWidth-self.minerWidth+maxSpeed) or  # within a column of tiles
        (mapList[self.minerIndex+self.numOfColumns+1] == "hole" and mapList[self.minerIndex+self.numOfColumns] == "hole"))): # if two holes below, don't worry about collision 
            self.yMoveTrue = self.yMoveRaw*dwarfSpeed
        elif (self.yMoveRaw == -1 and (self.rect[1] % self.tileHeight > maxSpeed or # within a row of tiles 
        (self.rect[0] % self.tileWidth <= (self.tileWidth-self.minerWidth+maxSpeed) and mapList[self.minerIndex-self.numOfColumns] == "hole") or # within a column of tiles and there is a hole above (no mining up)
        (mapList[self.minerIndex-self.numOfColumns] == "hole" and mapList[self.minerIndex-self.numOfColumns+1] == "hole")) and # if two holes above, don't worry about collision
        self.minerYindex > 0): # below top of map
        # up only within a tile or with a hole directly above
            self.yMoveTrue = self.yMoveRaw*dwarfSpeed
        elif (self.yMoveRaw == 0 and ((self.rect[1] % self.tileHeight < (self.tileHeight-self.minerHeight)) or  #gravity
        (self.rect[0] % self.tileWidth <= (self.tileWidth-self.minerWidth+maxSpeed) and mapList[self.minerIndex+self.numOfColumns] == "hole") or # gravity above 1 hole 
        (mapList[self.minerIndex+self.numOfColumns] == "hole" and mapList[self.minerIndex+self.numOfColumns+1] == "hole"))): # gravity above 2 holes 
            self.yMoveTrue = 2*(self.tileHeight//40) # gravity needs to be faster than the lowest dwarf speed
        else:
            self.yMoveTrue = 0
        
        self.rect.move_ip(self.xMoveTrue,self.yMoveTrue)
        self.minerXindex += self.xMoveTrue
        self.minerYindex += self.yMoveTrue
        self.minerIndex = (self.minerXindex//self.tileWidth) + (self.minerYindex//self.tileHeight)*self.numOfColumns # finds it in the mapList

    def Stop(self,key):
        if (key == pygame.K_RIGHT):
            self.xMoveRaw = 0
        elif (key == pygame.K_LEFT):
            self.xMoveRaw = 0
        elif (key == pygame.K_UP):
            self.yMoveRaw = 0
        elif (key == pygame.K_DOWN):
            self.yMoveRaw = 0
    
if __name__ == "__main__":
    KhazadDum()
