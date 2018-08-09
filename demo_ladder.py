#coding:utf-8

import random, time, pygame, sys
import numpy as np
from pygame.locals import *


#全局变量
FPS = 15
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

#构图
'''
--------------------------------
|  (  )        ( )    (  )     |
| (    ))    (    )) ((    )   |
|                              |
| 34m                   #      |
|                     #        |
|            o      #          |
|           /|\   #            |
|           /|  #              |
|__     ______#           _____|
|  |   |      |          |     |
|___~~~______~~~______~~~______|
'''

MAIN_TOP = WINDOW_HEIGHT//6
MAIN_BOT = WINDOW_HEIGHT-WINDOW_HEIGHT//6
MAN_CENTER = WINDOW_WIDTH*3//8
MAN_HEIGHT = WINDOW_HEIGHT//6
MAN_TOP = MAIN_BOT-MAN_HEIGHT
MAN_BOT = MAIN_BOT

CLOUD_HEIGHT = MAIN_TOP
CLOUD_WIDTH = CLOUD_HEIGHT*4//3
CLOUD_CNT = 3
CLOUD_SPEED = 1

#RGB
BLACK       = (  0,   0,   0)
WHITE       = (255, 255, 255)
GREY        = (185, 185, 185)
LIGHTGREY   = (225, 225, 225)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 40, 195,  40)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (195, 195,  40)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 40,  40, 195)
RED         = (155,   0,   0)
LIGHTRED    = (195,  40,  40)


def main():
    global exit, fps_lock, display_surf, basic_font

    pygame.init()
    fps_lock = pygame.time.Clock()
    display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    basic_font = pygame.font.Font('freesansbold.ttf', 20)
    pygame.display.set_caption('Ladder')
    exit = False

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()

def showStartScreen():
    pass

def showGameOverScreen():
    pass

def runGame():
    gameOver = False
    move = True
    drop_man = False
    drop_ladder = False

    clouds = initialCloud()
    
    while True:
        checkForQuit()

        clouds = updateCloud(clouds, move)
        
        display_surf.fill(BLACK)
        drawCloud(clouds)
        drawWave(move)
        drawMan(move, drop_man)
        drawRock(move)
        drawLadder(drop_ladder)

        pygame.display.update()
        fps_lock.tick(FPS)

def checkForQuit():
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                terminate()

def terminate():
    exit = True
    pygame.quit()
    sys.exit()

def initialCloud():
    clouds = []
    pos = np.random.randint(0, high=WINDOW_WIDTH-CLOUD_WIDTH*CLOUD_CNT, size=(CLOUD_CNT))
    pos = np.sort(pos)
    print(pos)
    for i in range(CLOUD_CNT):
        cloud_img = pygame.image.load("resource/cloud/cloud"+str(np.random.randint(8))+".png")
        cloud_img = pygame.transform.scale(cloud_img, (CLOUD_WIDTH, CLOUD_HEIGHT))
        cloud_pos = (i*CLOUD_WIDTH+pos[i], 0)
        cloud = [cloud_img, cloud_pos]
        clouds.append(cloud) 
    return clouds

def updateCloud(clouds, move):
    if move == True:
        for i, cloud in enumerate(clouds):
            cloud_img, cloud_pos = cloud[0], cloud[1]
            cloud_pos = (cloud_pos[0] - CLOUD_SPEED, cloud_pos[1])
            if cloud_pos[0] < -CLOUD_WIDTH:
                cloud_pos = (WINDOW_WIDTH, cloud_pos[1])
                cloud_img = pygame.image.load("resource/cloud/cloud"+str(np.random.randint(8))+".png")
                cloud_img = pygame.transform.scale(cloud_img, (CLOUD_WIDTH, CLOUD_HEIGHT))
            cloud = [cloud_img, cloud_pos]
            clouds[i] = cloud
    return clouds

def drawCloud(clouds):
    for cloud in clouds:
        cloud_img, cloud_pos = cloud[0], cloud[1]
        display_surf.blit(cloud_img, cloud_pos)

def drawWave(move):
    pass

def drawMan(move, drop_man):
    pass

def drawRock(move):
    pass

def drawLadder(drop_ladder):
    pass






if __name__ == '__main__':
    main()
