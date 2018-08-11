#coding:utf-8

import random, time, pygame, sys
import numpy as np
from pygame.locals import *


#====全局变量
FPS = 15
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

#====构图
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
BASIC_SPEED = WINDOW_WIDTH//400
#中间部分
MAIN_TOP = WINDOW_HEIGHT//6
MAIN_BOT = WINDOW_HEIGHT-WINDOW_HEIGHT//6
#石头
ROCK_HEIGHT = WINDOW_HEIGHT//6
ROCK_TOP = MAIN_BOT-ROCK_HEIGHT
ROCK_SPEED = BASIC_SPEED*4
ROCK_GAP_MIN = WINDOW_WIDTH//8
ROCK_GAP_MAX = WINDOW_WIDTH//2
ROCK_WIDTH_MIN = WINDOW_WIDTH//16
ROCK_WIDTH_MAX = WINDOW_WIDTH//2
#人
MAN_HEIGHT = WINDOW_HEIGHT//6
MAN_WIDTH = MAN_HEIGHT//2
MAN_LEFT = WINDOW_WIDTH*3//8
MAN_BOT = ROCK_TOP
MAN_TOP = MAN_BOT-MAN_HEIGHT
MAN_DROP_SPEED = BASIC_SPEED*5
#云
CLOUD_HEIGHT = MAIN_TOP
CLOUD_WIDTH = CLOUD_HEIGHT*4//3
CLOUD_CNT = 4
CLOUD_SPEED = BASIC_SPEED*1
#波浪
WAVE_HEIGHT = WINDOW_HEIGHT-MAIN_BOT
WAVE_WIDTH = WAVE_HEIGHT*3
WAVE_CNT = 3
WAVE_SPEED = BASIC_SPEED*5
#河流
RIVER_HEIGHT_OVERLAP = WINDOW_HEIGHT//12

#====颜色
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

COLOR_BG    = WHITE
COLOR_SKY   = (180, 255, 255)
COLOR_RIVER = (200, 220, 255)
COLOR_ROCK  = BLACK

#====程序主体架构
def main():
    global fps_lock, display_surf

    pygame.init()
    fps_lock = pygame.time.Clock()
    display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Ladder')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()
        
#====主要函数
def showStartScreen():
    pass

def showGameOverScreen():
    pass

def runGame():
    #本地变量，各种标记
    gameOver = False
    move = True
    drop_man = False
    drop_ladder = False

    #本地变量，初始化各个元素
    clouds = initialCloud()
    waves = initialWave()
    man = initialMan()
    rocks = initialRock()
    score = initialScore()
    
    while True:
        #检测退出事件
        checkForQuit()

        #更新各个元素
        clouds = updateCloud(clouds, move)
        waves = updateWave(waves, move)
        man = updateMan(man, move, drop_man)
        rocks = updateRock(rocks, move)
        score = updateScore(score, move)
        
        #根据各个元素最新情况，逻辑部分
        
        #绘图步骤 --------
        drawBackground()
        drawSky()
        drawRiver()
        drawCloud(clouds)
        drawWave(waves)
        drawMan(man)
        drawRock(rocks)
        drawLadder(drop_ladder)
        drawScore(score)

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

def drawBackground():
    display_surf.fill(COLOR_BG)

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
    #print(pos)
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
    #print(pos)
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

rock_gap_min = ROCK_GAP_MIN #随着游戏难度提升，将这四个值做调整
rock_gap_max = ROCK_GAP_MIN + (ROCK_GAP_MAX-ROCK_GAP_MIN)//10
rock_width_min = ROCK_WIDTH_MAX - (ROCK_WIDTH_MAX-ROCK_WIDTH_MIN)//10
rock_width_max = ROCK_WIDTH_MAX       
rock_delta_hard = WINDOW_WIDTH//50 #调整的幅度
def initialRock():
    rocks = []
    #rock [0:横坐标, 1:纵坐标, 2:宽度, 3:高度]
    rock = [0, ROCK_TOP, WINDOW_WIDTH, ROCK_HEIGHT] #第一块，整个长度
    rocks.append(rock)
    return rocks

def updateRock(rocks, move):
    global rock_gap_min, rock_gap_max, rock_width_min, rock_width_max, rock_delta_hard
    if move == True:
        for rock in rocks.copy():
            rock[0] -= ROCK_SPEED
            if rock [0] < -rock[2]: #当前的第一块移出边界，从列表中删除
                rocks.pop(0)
        rock_last = rocks[-1]
        if rock_last[0] + rock_last[2] < WINDOW_WIDTH: #当前最后一块移进边界，准备创造下一块并加入列表
            if True:
                if rock_gap_max < ROCK_GAP_MAX:
                    rock_gap_max += rock_delta_hard
                if rock_width_min > ROCK_WIDTH_MIN:
                    rock_width_min -= rock_delta_hard
                    rock_width_max -= rock_delta_hard
            rock_gap = np.random.randint(rock_gap_min, high=rock_gap_max)
            rock_width = np.random.randint(rock_width_min, high=rock_width_max)
            rock_next = [WINDOW_WIDTH+rock_gap, ROCK_TOP, rock_width, ROCK_HEIGHT]
            rocks.append(rock_next)
    return rocks
        
def drawRock(rocks):
    for rock in rocks:
        rectRock = (rock[0], rock[1], rock[2], rock[3])
        pygame.draw.rect(display_surf, COLOR_ROCK, rectRock)

def drawLadder(drop_ladder):
    pass

def initialScore():
    score = 0
    return score
    
def updateScore(score, move):
    if move == True:
        score += 1
    return score
    
def drawScore(score):
    score_font = pygame.font.Font('freesansbold.ttf', 20)
    textSurfaceObj = score_font.render("SCORE: "+str(score), True, LIGHTBLUE, COLOR_BG)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.topleft = (0 + 10, MAIN_TOP + 10)
    display_surf.blit(textSurfaceObj, textRectObj)




if __name__ == '__main__':
    main()
