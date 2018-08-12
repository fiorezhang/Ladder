#coding:utf-8

import random, time, pygame, sys
import numpy as np
from pygame.locals import *


#====全局变量
FPS = 15
MUSIC = True
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

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
ROCK_GAP_MIN = WINDOW_WIDTH//16
ROCK_GAP_MAX = WINDOW_WIDTH*7//16
ROCK_WIDTH_MIN = WINDOW_WIDTH//16
ROCK_WIDTH_MAX = WINDOW_WIDTH//2
ROCK_GAP_WIDTH_DELTA = WINDOW_WIDTH//40 #调整的幅度
#人
MAN_HEIGHT = WINDOW_HEIGHT//6
MAN_WIDTH = MAN_HEIGHT//2
MAN_LEFT = WINDOW_WIDTH*3//8
MAN_CENTER = MAN_LEFT+MAN_WIDTH//2
MAN_BOT = ROCK_TOP
MAN_TOP = MAN_BOT-MAN_HEIGHT
MAN_DROP_SPEED = BASIC_SPEED*5
#梯子
LADDER_LEN_MAX = WINDOW_WIDTH//2
LADDER_RAISE_SPEED = BASIC_SPEED*10
LADDER_DROP_SPEED = BASIC_SPEED*5
LADDER_DROP_MAX = MAIN_BOT
LADDER_ANGLE_DELTA = 10
LADDER_ANGLE_MAX = 90
LADDER_WIDTH = 3
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

COLOR_SKY   = (180, 255, 255)
COLOR_RIVER = (200, 220, 255)
COLOR_ROCK     = BLACK
COLOR_LADDER   = BLACK
COLOR_BG       = WHITE
COLOR_BG_OVER  = BLACK
COLOR_BG_START =WHITE

#====程序主体架构
def main():
    global fps_lock, display_surf

    pygame.init()
    pygame.mixer.init()
    fps_lock = pygame.time.Clock()
    display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Ladder')

    showStartScreen()
    while True:
        score = runGame()
        showGameOverScreen(score)
        
#====主要函数
def showStartScreen():
    if MUSIC == True:
        pygame.mixer.music.load("resource/sound/start.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1, 0.0)
    clouds = initialCloud()
    waves = initialWave()    
    while True:
        checkForQuit()
        clouds = updateCloud(clouds, True)
        waves = updateWave(waves, True)
        drawBackgroundStart()    
        drawSky()
        drawRiver()
        drawCloud(clouds)
        drawWave(waves)
        drawTitleStart()
        drawPromptStart()
        pygame.display.update()
        fps_lock.tick(FPS)
        if checkForSpaceDown() == True:
            pygame.mixer.music.fadeout(1000)
            break
        
def showGameOverScreen(score):
    if MUSIC == True:
        pygame.mixer.music.load("resource/sound/end.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1, 0.0)    
    if np.random.randint(2) == 0:
        sound_end_joke = pygame.mixer.Sound("resource/sound/end_joke_1.wav")
    else:
        sound_end_joke = pygame.mixer.Sound("resource/sound/end_joke_2.wav")
    sound_end_joke.play()
    while True:
        checkForQuit()
        drawBackgroundOver()    
        drawScoreOver(score)
        drawPromptOver()
        pygame.display.update()
        fps_lock.tick(FPS)
        time.sleep(1)
        if checkForSpaceDown() == True:
            if MUSIC == True:
                pygame.mixer.music.stop()
            break

        
def runGame():
    #本地变量，各种标记，缓存
    gameOver = False
    move = True
    move_on_ladder = False
    raise_ladder = False
    raise_ladder_raising = False
    rotate_ladder = False
    rotate_ladder_rotating = False
    drop_man = False
    drop_ladder = False
    drop_ladder_dropping = False
    button_prompt = 0 # 0:false, 1:true, 2:false
    
    rock_current = None
    rock_next = None

    #本地变量，初始化各个元素
    clouds = initialCloud()
    waves = initialWave()
    man = initialMan()
    rocks = initialRock()
    score = initialScore()
    ladder = initialLadder()

    #Ladder的处理在本地，所以参数先拆分
    ladder_left, ladder_drop, ladder_len, ladder_angle = ladder[0], ladder[1], ladder[2], ladder[3]

    #MUSIC
    if MUSIC == True:
        pygame.mixer.music.load("resource/sound/main.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1, 0.0)
    sound_main_raise = pygame.mixer.Sound("resource/sound/main_raise.wav")
    sound_main_success = pygame.mixer.Sound("resource/sound/main_success.wav")
    sound_main_failure_1 = pygame.mixer.Sound("resource/sound/main_failure_1.wav")
    sound_main_failure_2 = pygame.mixer.Sound("resource/sound/main_failure_2.wav")
    sound_main_start = pygame.mixer.Sound("resource/sound/main_start.wav")
    sound_main_start.play()
    
    while gameOver == False:
        #检测退出事件
        checkForQuit()
        
        #根据各个元素最新情况，逻辑部分. 尤其是ladder相关的几个参数逻辑比较复杂，都在这里实现，便于维护
        if move == True: #正在走动时
            if move_on_ladder == True: 
                #print("6. Walk on ladder")
                ladder_left -= ROCK_SPEED
                man_pos = man[1]
                man_x_center = man_pos[0] + MAN_WIDTH//2
                if man_x_center > ladder_left+ladder_len: #走出梯子了
                    move_on_ladder = False
                    drop_man = True #临时设为True，在下面循环中检测有没有落在石头上
                    for i, rock in enumerate(rocks):    #从梯子上下来，马上判断是不是落在某块石头上
                        rock_x_left, rock_width = rock[0], rock[2] #石头的左侧坐标，宽度
                        rock_x_right = rock_x_left + rock_width
                        if man_x_center >= rock_x_left and man_x_center < rock_x_right - ROCK_SPEED: #注意，判定的时候不能太靠近石头的右沿，要给下一次正常循环留出余量，不然可能“跳过”临界区
                            drop_man = False
                            break
                    if drop_man == False:
                        #print("o. Back to normal loop")
                        ladder_left = MAN_CENTER
                        ladder_drop = ROCK_TOP
                        ladder_len = 0
                        ladder_angle = 0
                    else:
                        #print("6.5Drop out of rock")
                        move = False
                        sound_main_failure_2.play()
            else:
                man_pos = man[1]
                man_x_center = man_pos[0] + MAN_WIDTH//2
                for i, rock in enumerate(rocks):
                    rock_x_left, rock_width = rock[0], rock[2] #石头的左侧坐标，宽度
                    rock_x_right = rock_x_left + rock_width
                    if man_x_center < rock_x_right and man_x_center + ROCK_SPEED >= rock_x_right: #走到临界区，准备放梯子
                        #print("1. Ready to raise ladder")
                        move = False
                        raise_ladder = True
                        rock_current = rock
                        rock_next = rocks[i+1]
                        clearKeyEvent() #把行走过程中所有按键事件清空，为接下来的放梯子做准备
                        break
        else:  #没有在走动，放梯子或者下坠
            if raise_ladder == True:
                if raise_ladder_raising == False:
                    if checkForSpaceDown() == True: 
                        #print("2. Raising ladder")
                        button_prompt = 2
                        raise_ladder_raising = True
                        sound_main_raise.play()
                        ladder_len += LADDER_RAISE_SPEED
                        clearKeyEvent() #把行走过程中所有按键事件清空，为接下来的放梯子做准备
                    elif button_prompt == 0:
                        button_prompt = 1
                if raise_ladder_raising == True:
                    if checkForSpaceUp() == True or ladder_len >= LADDER_LEN_MAX:
                        #print("3. Raised ladder")
                        raise_ladder_raising = False
                        raise_ladder = False
                        rotate_ladder = True
                        rotate_ladder_rotating = True 
                        sound_main_raise.stop()
                    else: #按键按下中，增长梯子长度
                        #print("2.5Raising ladder")
                        ladder_len += LADDER_RAISE_SPEED
            if rotate_ladder == True:
                if rotate_ladder_rotating == True:
                    #print("4. Rotating ladder")
                    ladder_angle += LADDER_ANGLE_DELTA
                    if ladder_angle >= LADDER_ANGLE_MAX: 
                        ladder_angle = LADDER_ANGLE_MAX
                        rotate_ladder_rotating = False
                else:
                    #print("5. Rotated ladder")
                    rotate_ladder = False
                    #print(ladder_len)
                    #print(rock_next[0] - rock_current[0] - rock_current[2])
                    if ladder_len <= rock_next[0] - rock_current[0] - rock_current[2]: #梯子连下一块石头都不够(下一块石头左侧坐标 - 当前石头右侧坐标)
                        drop_ladder = True
                        sound_main_failure_1.play()
                    else:
                        move = True
                        move_on_ladder = True
                        sound_main_success.play()
                        ladder_left = rock_current[0]+rock_current[2]-ROCK_SPEED
            if drop_ladder == True:
                #print("*. Drop ladder")
                ladder_drop += LADDER_DROP_SPEED
                if ladder_drop >= LADDER_DROP_MAX:
                    drop_ladder = False
                    gameOver = True
            if drop_man == True:
                #print("7. Drop man")
                man_pos = man[1]
                if man_pos[1] >= MAIN_BOT:
                    drop_man = False
                    gameOver = True
            pass
        
        #Ladder 的处理在本地，逻辑完成后，汇总更新ladder
        ladder = [ladder_left, ladder_drop, ladder_len, ladder_angle]
        
        #更新各个元素
        clouds = updateCloud(clouds, move)
        waves = updateWave(waves, move)
        man = updateMan(man, move, drop_man)
        rocks = updateRock(rocks, move)
        score = updateScore(score, move)
        ladder = updateLadder(ladder)
        
        #绘图步骤 --------
        drawBackground()
        drawSky()
        drawRiver()
        drawCloud(clouds)
        drawWave(waves)
        drawMan(man)
        drawRock(rocks)
        drawLadder(ladder)
        drawScore(score)
        drawButtonPropmt(button_prompt)

        pygame.display.update()
        fps_lock.tick(FPS)
    print("return: %d" % score)
    if MUSIC == True:
        pygame.mixer.music.stop()
    return score
        
def checkForQuit():
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event) #放回所有的事件

def clearKeyEvent():
    pygame.event.get([KEYDOWN, KEYUP])
    
def checkForSpaceDown():
    for event in pygame.event.get(KEYDOWN):
        if event.key == K_SPACE:
            return True
    return False

def checkForSpaceUp():
    for event in pygame.event.get(KEYUP):
        if event.key == K_SPACE:
            return True
    return False

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
def initialRock():
    global rock_gap_min, rock_gap_max, rock_width_min, rock_width_max, ROCK_GAP_WIDTH_DELTA
    rock_gap_min = ROCK_GAP_MIN #随着游戏难度提升，将这四个值做调整
    rock_gap_max = ROCK_GAP_MIN + (ROCK_GAP_MAX-ROCK_GAP_MIN)//10
    rock_width_min = ROCK_WIDTH_MAX - (ROCK_WIDTH_MAX-ROCK_WIDTH_MIN)//10
    rock_width_max = ROCK_WIDTH_MAX       
    rocks = []
    #rock [0:横坐标, 1:纵坐标, 2:宽度, 3:高度]
    rock = [0, ROCK_TOP, WINDOW_WIDTH, ROCK_HEIGHT] #第一块，整个长度
    rocks.append(rock)
    return rocks

def updateRock(rocks, move):
    global rock_gap_min, rock_gap_max, rock_width_min, rock_width_max, ROCK_GAP_WIDTH_DELTA
    if move == True:
        for rock in rocks.copy():
            rock[0] -= ROCK_SPEED
            if rock [0] < -rock[2]: #当前的第一块移出边界加上一定距离，从列表中删除（不要太早删掉，否则判定梯子长度有问题）
                rocks.pop(0)
        rock_last = rocks[-1]
        if rock_last[0] + rock_last[2] < WINDOW_WIDTH: #当前最后一块移进边界，准备创造下一块并加入列表
            if True:
                if rock_gap_max < ROCK_GAP_MAX:
                    rock_gap_max += ROCK_GAP_WIDTH_DELTA
                else:
                    rock_gap_max = ROCK_GAP_MAX
                if rock_width_min > ROCK_WIDTH_MIN:
                    rock_width_min -= ROCK_GAP_WIDTH_DELTA
                    rock_width_max -= ROCK_GAP_WIDTH_DELTA
                else:
                    rock_width_min = ROCK_WIDTH_MIN
                    if rock_width_max < rock_width_min:
                        rock_width_max = rock_width_min
            rock_gap = np.random.randint(rock_gap_min, high=rock_gap_max)
            rock_width = np.random.randint(rock_width_min, high=rock_width_max)
            rock_next = [WINDOW_WIDTH+rock_gap, ROCK_TOP, rock_width, ROCK_HEIGHT]
            rocks.append(rock_next)
    return rocks
        
def drawRock(rocks):
    for rock in rocks:
        rect_rock = (rock[0], rock[1], rock[2], rock[3])
        pygame.draw.rect(display_surf, COLOR_ROCK, rect_rock)

def initialLadder():
    ladder_left = MAN_CENTER
    ladder_drop = ROCK_TOP
    ladder_len = 0
    ladder_angle = 0
    ladder = [ladder_left, ladder_drop, ladder_len, ladder_angle]
    return ladder

def updateLadder(ladder):
    #print(ladder)
    return ladder
        
def drawLadder(ladder):
    ladder_left, ladder_drop, ladder_len, ladder_angle = ladder[0], ladder[1], ladder[2], ladder[3]
    
    ladder_img = pygame.image.load("resource/ladder/ladder.png")
    ladder_img = pygame.transform.scale(ladder_img, (LADDER_WIDTH, ladder_len))
    ladder_img = pygame.transform.rotate(ladder_img, -ladder_angle)
    img_hight = pygame.Surface.get_height(ladder_img)
    display_surf.blit(ladder_img, (ladder_left, ladder_drop-img_hight))
    
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
    
def drawButtonPropmt(prompt):
    if prompt == 1:
        prompt_font = pygame.font.Font('freesansbold.ttf', 30)
        textSurfaceObj = prompt_font.render("Hold space key", True, WHITE, COLOR_ROCK)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.bottomright = (MAN_CENTER-20, MAIN_BOT-20)
        display_surf.blit(textSurfaceObj, textRectObj)        

def drawBackgroundOver():
    display_surf.fill(COLOR_BG_OVER)
    
def drawScoreOver(score):
    gameover_font = pygame.font.Font('freesansbold.ttf', 100)
    textSurfaceObj = gameover_font.render("GAME OVER", True, LIGHTRED, COLOR_BG_OVER)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//3)
    display_surf.blit(textSurfaceObj, textRectObj)
    
    score_font = pygame.font.Font('freesansbold.ttf', 80)
    textSurfaceObj = score_font.render("SCORE: "+str(score), True, LIGHTBLUE, COLOR_BG_OVER)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT*2//3)
    display_surf.blit(textSurfaceObj, textRectObj)
    
def drawPromptOver():
    prompt_font = pygame.font.Font('freesansbold.ttf', 20)
    textSurfaceObj = prompt_font.render("Press space key to continue!", True, WHITE, COLOR_BG_OVER)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT - 40)
    display_surf.blit(textSurfaceObj, textRectObj)

def drawBackgroundStart():
    display_surf.fill(COLOR_BG_START)
    
def drawTitleStart():
    title_font = pygame.font.Font('freesansbold.ttf', 100)
    textSurfaceObj = title_font.render("L A D D E R", True, BLUE, COLOR_BG_START)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//3)
    display_surf.blit(textSurfaceObj, textRectObj)

def drawPromptStart():
    prompt_font = pygame.font.Font('freesansbold.ttf', 20)
    textSurfaceObj = prompt_font.render("Press space key to continue!", True, BLACK, COLOR_BG_START)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (WINDOW_WIDTH//2, MAIN_BOT - RIVER_HEIGHT_OVERLAP - 40)
    display_surf.blit(textSurfaceObj, textRectObj)
    
#====入口
if __name__ == '__main__':
    main()
