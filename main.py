#!/usr/bin/env python3
import pygame
import random
import numpy as np
WIDTH = 500  # ширина игрового окна
HEIGHT = 500  # высота игрового окна
ANT_W_H = 5  #размер клетки и муравья
FPS = 60 # частота кадров в секунду
NUM_ANTS = 30  # Количество муравьев
NUM_EATS = 50  # Количество еды
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = np.array([255, 0, 0])
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
VIOLET = np.array([255, 0, 255])
pygame.init()  
pygame.mixer.init()  
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Муравьи")
clock = pygame.time.Clock()
class Ferromon(pygame.sprite.Sprite):
    w_h = 5    
    def __init__(self, xy):
        pygame.sprite.Sprite.__init__(self)
        sprites.add(self, layer = 1)
        self.viol = VIOLET.copy()
        self.image = pygame.Surface((self.w_h, self.w_h))
        self.image.fill(self.viol)
        self.rect = self.image.get_rect()
        self.rect.topleft = xy       
    def update(self):
        self.viol[self.viol > 0] -= 3
        if all(i <= 0 for i in self.viol):
            self.kill()
        else:
            self.image.fill(self.viol)
class Eat(pygame.sprite.Sprite):
    w_h = 5
    eatSize = 100
    def __init__(self, xy):
        pygame.sprite.Sprite.__init__(self)
        sprites.add(self, layer = 3)
        self.image = pygame.Surface((self.w_h, self.w_h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = xy
    def update(self):
        self.image.fill(GREEN)
        if self.eatSize <= 0: self.kill()
class Ant(pygame.sprite.Sprite):
    step = 5
    dir = np.array([[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1], [0, 0]])*step
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        sprites.add(self, layer = 2)
        self.id = random.randint(0, 100)
        self.image = pygame.Surface((ANT_W_H, ANT_W_H))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = np.array([x, y])
        self.angleToHome = np.array([0, 0])
        self.countMode0 = 0
        self.choiceDir = np.array([0, 0])
        self.mode = 0       # 0 - поиск еды - выбор направления
                            # 1 - доставка найденной еды - движение домой
                            # 2 - путь к еде по ферромонам
    def calcAngleToHome(self, xy):
        return [x - y for x, y in zip(antHome.rect.topleft, xy)]
    def searchFoodChoiceDir(self, xy, home):
        while True:
            choiceDir = random.choice(self.dir)
            sum = [x + y for x, y in zip(choiceDir, xy)]
            if not ((sum in home) or any(i >= (WIDTH - self.step) for i in sum) or any(i <= self.step for i in sum)):
                break
        return choiceDir
    def searchFoodRunDir(self, xy, choiceDir):
        return [x + y for x, y in zip(xy, choiceDir)]        
    def searchFood(self, xy, home):
        if self.countMode0 == 0:
            self.choiceDir = self.searchFoodChoiceDir(xy, home)
        else:
            sum = self.searchFoodRunDir(xy, self.choiceDir)
            if not ((sum in home) or any(i >= (WIDTH - self.step) for i in sum) or any(i <= self.step for i in sum)): 
                xy = sum
        self.countMode0 += 1          
        if self.countMode0 == 10:
            self.countMode0 = 0        
        return xy
    def setFerromon(self, xy):
        collide = pygame.sprite.spritecollide(self, allFerromon, False, pygame.sprite.collide_rect_ratio(1.1))
        if collide:
            collide[0].viol[collide[0].viol > 0] = 255
        else:
            ferromon = Ferromon(xy)
            allFerromon.add(ferromon)
    def transferFoodToHome(self, xy):
        collide = pygame.sprite.spritecollide(self, allHomes, False, pygame.sprite.collide_rect_ratio(2.1))
        if collide:
            self.mode = 2
        else:
            angleTmp = np.array(self.angleToHome.copy())
            angleTmp[angleTmp > 0] = self.step
            angleTmp[angleTmp < 0] = -self.step
            xy = [x + y for x, y in zip(xy, angleTmp)]
            self.angleToHome = [x - y for x, y in zip(self.angleToHome, angleTmp)]
            self.setFerromon(xy)
        return xy
    def runToEatByFerromons(self):
        collide = pygame.sprite.spritecollide(self, allEats, False, pygame.sprite.collide_rect_ratio(2.1))
        if collide:  # Если еда есть
            self.mode = 1
            for i in collide:
                i.eatSize -= 2
        else:				# Если еды нет, продолжаем идти по ферромонам
            collideOutIn = pygame.sprite.spritecollide(self, allFerromon, False, pygame.sprite.collide_rect_ratio(3.1))
            collideIn = pygame.sprite.spritecollide(self, allFerromon, False)
            collideOut = list(set(collideOutIn) - set(collideIn))
            if collideOut:	# Если есть куда идти
                maxFerr = -1
                for i in collideOut:
                    b = any([(self.rect.topleft[n] - i.rect.topleft[n]) * (antHome.rect.topleft[n] - self.rect.topleft[n]) > 0 for n in range(2)])
                    if (i.viol[0] > maxFerr) and b:
                        maxFerr = i.viol[0]
                        maxI = i                                      
                if maxFerr >= 0:
                    self.rect.topleft = maxI.rect.topleft	
                else:
	              		self.mode = 0
										self.rect.topleft[0], self.rect.topleft[1] = self.rect.topleft[0]+random.randint(-1,2), self.rect.topleft[1]+random.randint(-1,2)
						else:    # Если некуда идти        
                self.mode = 0
								self.rect.topleft[0] = self.rect.topleft[0] + random.randint(-1, 2)
								self.rect.topleft[1] = self.rect.topleft[1] + random.randint(-1, 2)
        return self.rect.topleft
    def update(self):
        xy = self.rect.topleft
        if self.mode == 0:
            xy = self.searchFood(self.rect.topleft, antHome.rect.topleft)
            collide = pygame.sprite.spritecollide(self, allEats, False)
            if collide:
                self.mode = 1
                for i in collide:
                    i.eatSize -= 2
            elif pygame.sprite.spritecollide(self, allFerromon, False, pygame.sprite.collide_rect_ratio(2.1)):
                self.mode = 2
        if self.mode == 1:
            xy = self.transferFoodToHome(self.rect.topleft)
        if self.mode == 2:
            xy = self.runToEatByFerromons()
        self.angleToHome = self.calcAngleToHome(self.rect.topleft)
        self.rect.topleft = xy        
class AntHome(pygame.sprite.Sprite):
    w_h = 5
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        sprites.add(self, layer = 4)
        self.image = pygame.Surface((self.w_h, self.w_h))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def update(self):
        self.image.fill(BLUE)
allEats = pygame.sprite.Group()
allFerromon = pygame.sprite.Group()
allHomes = pygame.sprite.Group()
allAnts = pygame.sprite.Group()
sprites = pygame.sprite.LayeredUpdates()
running = True
antHome = AntHome(WIDTH/2, HEIGHT/2)
allHomes.add(antHome)
for i in range(NUM_ANTS):
    i = Ant(antHome.rect.x, antHome.rect.y)
    allAnts.add(i)
for i in range(NUM_EATS):
    i = Eat((random.randrange(ANT_W_H, WIDTH - ANT_W_H), random.randrange(ANT_W_H, HEIGHT - ANT_W_H)))
    allEats.add(i)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    clock.tick(FPS)
    sprites.update()    
    screen.fill(BLACK)
    sprites.draw(screen)
    pygame.display.flip()
pygame.quit()
