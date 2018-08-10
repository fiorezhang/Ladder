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

ROCK_HEIGHT = WINDOW_HEIGHT//6

MAN_HEIGHT = WINDOW_HEIGHT//6
MAN_WIDTH = MAN_HEIGHT//2
MAN_LEFT = WINDOW_WIDTH*3//8
MAN_BOT = MAIN_BOT-ROCK_HEIGHT
MAN_TOP = MAN_BOT-MAN_HEIGHT
MAN_DROP_SPEED = 5


CLOUD_HEIGHT = MAIN_TOP
CLOUD_WIDTH = CLOUD_HEIGHT*4//3
CLOUD_CNT = 4
CLOUD_SPEED = 1

WAVE_HEIGHT = WINDOW_HEIGHT-MAIN_BOT
WAVE_WIDTH = WAVE_HEIGHT*3
WAVE_CNT = 3
WAVE_SPEED = 5

RIVER_HEIGHT_OVERLAP = WINDOW_HEIGHT//12


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

COLOR_SKY   = (180, 255, 255)
COLOR_RIVER = (200, 220, 255)

def main():
    global fps_lock, display_surf, basic_font

    pygame.init()
    fps_lock = pygame.time.Clock()
    display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    basic_font = pygame.font.Font('freesansbold.ttf', 20)
    pygame.display.set_caption('Ladder')

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
    waves = initialWave()
    man = initialMan()
    
    while True:
        checkForQuit()

        clouds = updateCloud(clouds, move)
        waves = updateWave(waves, move)
        man = updateMan(man, move, drop_man)
        
        display_surf.fill(WHITE)
        drawSky()
        drawRiver()
        drawCloud(clouds)
        drawWave(waves)
        drawMan(man)
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
    pygame.quit()
    sys.exit()

    
    
def drawSky():
    sky = pygame.Rect(0, 0, WINDOW_WIDTH, CLOUD_HEIGHT)
    pygame.draw.rect(display_surf, COLOR_SKY, sky)

def drawRiver():
    river = pygame.Rect(0, MAIN_BOT - RIVER_HEIGHT_OVERLAP, WINDOW_WIDTH, WAVE_HEIGHT+RIVER_HEIGHT_OVERLAP)
    pygame.draw.rect(display_surf, COLOR_RIVER, river)
    
def initialCloud():
    clouds = []
    pos = np.random.randint(0, high=WINDOW_WIDTH-CLOUD_WIDTH*(CLOUD_CNT-1), size=(CLOUD_CNT))
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

def initialWave():
    waves = []
    pos = np.random.randint(0, high=WINDOW_WIDTH-WAVE_WIDTH*(WAVE_CNT-1), size=(WAVE_CNT))
    pos = np.sort(pos)
    print(pos)
    for i in range(WAVE_CNT):
        wave_img = pygame.image.load("resource/wave/wave.png")
        wave_img = pygame.transform.scale(wave_img, (WAVE_WIDTH, WAVE_HEIGHT))
        wave_pos = (i*WAVE_WIDTH+pos[i], MAIN_BOT)
        wave = [wave_img, wave_pos]
        waves.append(wave)
    return waves
    
def updateWave(waves, move):
    if move == True:
        for i, wave in enumerate(waves):
            wave_img, wave_pos = wave[0], wave[1]
            wave_pos = (wave_pos[0] - WAVE_SPEED, wave_pos[1])
            if wave_pos[0] < -WAVE_WIDTH:
                wave_pos = (WINDOW_WIDTH, wave_pos[1])
            wave = [wave_img, wave_pos]
            waves[i] = wave
    return waves
        
def drawWave(waves):
    for wave in waves:
        wave_img, wave_pos = wave[0], wave[1]
        display_surf.blit(wave_img, wave_pos)

man_pose_num = 0 #全局变量
MAN_POSE_CNT = 6
def initialMan():
    global man_pose_num
    man_img = pygame.image.load("resource/man/man"+str(man_pose_num)+".png")
    man_img = pygame.transform.scale(man_img, (MAN_WIDTH, MAN_HEIGHT))
    man_pos = (MAN_LEFT, MAN_BOT-MAN_HEIGHT)
    man = [man_img, man_pos]    
    return man
    
def updateMan(man, move, drop_man):
    global man_pose_num
    man_img, man_pos = man[0], man[1]
    if move == True:
        man_pose_num += 1
        if man_pose_num == MAN_POSE_CNT:
            man_pose_num = 0
        man_img = pygame.image.load("resource/man/man"+str(man_pose_num)+".png")
        man_img = pygame.transform.scale(man_img, (MAN_WIDTH, MAN_HEIGHT))
        man = [man_img, man_pos]
    elif drop_man == True:
        man_img = pygame.image.load("resource/man/man"+str(man_pose_num)+".png")
        man_img = pygame.transform.scale(man_img, (MAN_WIDTH, MAN_HEIGHT))
        man_pos = (man_pos[0], man_pos[1]+MAN_DROP_SPEED) #碰撞检测在主循环获取man_pos的值后做
        man = [man_img, man_pos]
    return man
        
def drawMan(man):
    man_img, man_pos = man[0], man[1]
    display_surf.blit(man_img, man_pos)
    

def drawRock(move):
    pass

def drawLadder(drop_ladder):
    pass






if __name__ == '__main__':
    main()
