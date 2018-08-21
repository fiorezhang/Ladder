#coding:utf-8
#copyright: fiorezhang@sina.com

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
ROCK_GAP_WIDTH_DELTA = WINDOW_WIDTH//40 #调整的幅度, 可以调整难度，越大游戏难度增长越快
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
LADDER_RAISE_SPEED = BASIC_SPEED*10 #梯子上升速度，原则上越大游戏越难
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
COLOR_BG_START = WHITE

#====程序主体架构
def main():
    ''' Initialization. 
    Fps and main surface is globalized, for all scenes. 
    Game start with a start screen, then loop in main routine and end screen(show a score)
    '''
    global fps_lock, display_surf

    pygame.init()
    pygame.mixer.init()
    fps_lock = pygame.time.Clock()
    display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Ladder for Leah')

    showStartScreen()
    while True:
        score = runGame()
        showGameOverScreen(score)
        
#====主要函数
def showStartScreen():
    ''' Start screen. 
    Play start music. Show title and button prompt. Show more items for good look. 
    '''
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
    ''' Game over screen. 
    Play music and taunt. Show score and button prompt. 
    '''
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
        time.sleep(1) #避免过快跳过游戏结束界面开始下一局
        if checkForSpaceDown() == True:
            if MUSIC == True:
                pygame.mixer.music.stop()
            break

        
def runGame():
    ''' Main routine. 
    Play main music, sound effects. Initialize elements and flags. In main loop, update elements in state machine, then draw. 
    Major elements include: man, rocks, ladder, and other landscape blobs. 
    Man keep walk on rocks and stop automatically at edge, raise the ladder to cross the gap. Ladder too short or too long will lead to a failure. 
    '''
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

        #更新各个元素
        clouds = updateCloud(clouds, move)
        waves = updateWave(waves, move)
        man = updateMan(man, move, drop_man)
        rocks = updateRock(rocks, move)
        score = updateScore(score, move)
        ladder = updateLadder(ladder)
                
        #根据各个元素最新情况，逻辑部分. 尤其是ladder相关的几个参数逻辑比较复杂，都在这里实现，便于维护
        '''
        if move is True:
            # Everything updated just now - clouds, waves, man, most importantly rocks
            # Either man normally walk on a rock, or man walk on the ladder
            if move_on_ladder is True:
                # Update ladder position, speed MUST as well as rock
                # Judge if still on ladder, if no if right on any rock, if still no then mark drop_man
                # Specially, if end of ladder is close to end of rock, directly judge whether next ladder here, to avoid 'critical section' miss in normal walk routine
            if move_on_ladder is False:
                # Judge whether close to end of rock, if yes then mark raise_ladder
        if move is False:
            # Below situations when not move: raise ladder, rotate ladder, drop ladder, drop man
                if raise_ladder is True:
                    # Add ladder lenth until the MAX value
                    # Important: Cleared key press before enter here
                    # Catch button down for starting raising
                    # Catch button up for end, trigger rotate_ladder
                if rotate_ladder is True:
                    # Increase the digree, judge whether hit next rock when flat, if so set move_on_ladder, or set drop_ladder
                if drop_ladder is True:
                    # Drop until the bottom, game over
                if drop_man is True:
                    # Drop until the bottom, game over
        '''
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
                        if man_x_center >= rock_x_left and man_x_center < rock_x_right: 
                            drop_man = False
                            if man_x_center + ROCK_SPEED >= rock_x_right: #本次已经走进临界区，所以直接放梯子
                                #print("x. Critical Sesson")
                                move = False
                                raise_ladder = True
                                rock_current = rock
                                rock_next = rocks[i+1]
                                clearKeyEvent() #把行走过程中所有按键事件清空，为接下来的放梯子做准备
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
                        ladder_left = rock_current[0]+rock_current[2]#-ROCK_SPEED
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
    ''' Check for quit by system or esc button
    Throw back all button event to avoid missing in following routine
    '''
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event) #放回所有的事件

def clearKeyEvent():
    ''' Clear existing button event
    Used like before ladder raise. Ensure no residual button state interference the logics. 
    '''
    pygame.event.get([KEYDOWN, KEYUP])
    
def checkForSpaceDown():
    ''' Check for space button down, ignore and clear other button event
    '''
    for event in pygame.event.get(KEYDOWN):
        if event.key == K_SPACE:
            return True
    return False

def checkForSpaceUp():
    ''' Check for space button up, ignore and clear other button event
    '''
    for event in pygame.event.get(KEYUP):
        if event.key == K_SPACE:
            return True
    return False

def terminate():
    ''' Quit game
    '''
    pygame.quit()
    sys.exit()

def drawBackground():
    ''' Draw background for main routine
    '''
    display_surf.fill(COLOR_BG)

def drawSky():
    ''' Draw sky, simply a colorful rectangle
    '''
    sky = pygame.Rect(0, 0, WINDOW_WIDTH, CLOUD_HEIGHT)
    pygame.draw.rect(display_surf, COLOR_SKY, sky)

def drawRiver():
    ''' Draw river, simply a colorful rectangle
    '''
    river = pygame.Rect(0, MAIN_BOT - RIVER_HEIGHT_OVERLAP, WINDOW_WIDTH, WAVE_HEIGHT+RIVER_HEIGHT_OVERLAP)
    pygame.draw.rect(display_surf, COLOR_RIVER, river)
    
def initialCloud():
    ''' Initialize clouds, get random clouds texture
    '''
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
    ''' Update clouds, slow speed. To simple the logics, every cloud redraw at right after remove from left of screen, just randomly change a texture
    When move, change position
    '''
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
    ''' Draw clouds
    '''
    for cloud in clouds:
        cloud_img, cloud_pos = cloud[0], cloud[1]
        display_surf.blit(cloud_img, cloud_pos)

def initialWave():
    ''' Initialize waves, get texture
    '''
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
    ''' Update waves, slightly faster speed than rocks. When move, change position
    '''
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
    ''' Draw waves
    '''
    for wave in waves:
        wave_img, wave_pos = wave[0], wave[1]
        display_surf.blit(wave_img, wave_pos)

man_pose_num = 0 #全局变量
MAN_POSE_CNT = 6
def initialMan():
    ''' Initialize man. Get consequent pose from textures. 
    '''
    global man_pose_num
    man_img = pygame.image.load("resource/man/man"+str(man_pose_num)+".png")
    man_img = pygame.transform.scale(man_img, (MAN_WIDTH, MAN_HEIGHT))
    man_pos = (MAN_LEFT, MAN_BOT-MAN_HEIGHT)
    man = [man_img, man_pos]    
    return man
    
def updateMan(man, move, drop_man):
    ''' Update man. When move, choose next pose texture. When drop, change position. 
    '''
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
    ''' Draw man
    '''
    man_img, man_pos = man[0], man[1]
    display_surf.blit(man_img, man_pos)

rock_gap_min = ROCK_GAP_MIN #随着游戏难度提升，将这四个值做调整
rock_gap_max = ROCK_GAP_MIN + (ROCK_GAP_MAX-ROCK_GAP_MIN)//10
rock_width_min = ROCK_WIDTH_MAX - (ROCK_WIDTH_MAX-ROCK_WIDTH_MIN)//10
rock_width_max = ROCK_WIDTH_MAX       
def initialRock():
    ''' Initialize rocks. 
    Import global values to adjust rock width and gap range. That impact the difficulty. 
    At the beginning, the rocks are wide, and gaps are close. 
    Then along the game, reduce the width MIN and MAX, increase the gap MAX. 
    '''
    global rock_gap_min, rock_gap_max, rock_width_min, rock_width_max, ROCK_GAP_WIDTH_DELTA
    #每次初始化都要重设，否则下一局游戏难度不会还原
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
    ''' Update rocks. 
    Remove rocks which out of screen. 
    When last rock in list fully in screen, prepare a new rock, gap and width randomlly in defined range. 
    '''
    global rock_gap_min, rock_gap_max, rock_width_min, rock_width_max, ROCK_GAP_WIDTH_DELTA
    if move == True:
        for rock in rocks.copy(): # 做copy，因为要删除元素，否则遍历可能出错
            rock[0] -= ROCK_SPEED
            if rock [0] < -rock[2]: #当前的第一块移出边界#加上一定距离，从列表中删除（不要太早删掉，否则判定梯子长度有问题）(通过记录梯子位置，又避免了这个问题)
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
    ''' Draw rocks. 
    '''
    for rock in rocks:
        rect_rock = (rock[0], rock[1], rock[2], rock[3])
        pygame.draw.rect(display_surf, COLOR_ROCK, rect_rock)

def initialLadder():
    ''' Initialize ladder. 
    Ladder is the most complex item in the game. The changable facts include: length, position, angle
    So use four values to record the status, the left coord, bottom coord, length, and rotate angle(clock)
    '''
    ladder_left = MAN_CENTER
    ladder_drop = ROCK_TOP
    ladder_len = 0
    ladder_angle = 0
    ladder = [ladder_left, ladder_drop, ladder_len, ladder_angle]
    return ladder

def updateLadder(ladder):
    ''' Update ladder
    Do NOTHING. All update implemented in main loop for easy comprehension and maintain
    '''
    #print(ladder)
    return ladder
        
def drawLadder(ladder):
    ''' Draw ladder. 
    Load texture, scale to size(length changed), rotate to right angle. 
    Because the blit function choose topleft as hook point, need to get the surface height then calculate the topleft coordinate
    '''
    ladder_left, ladder_drop, ladder_len, ladder_angle = ladder[0], ladder[1], ladder[2], ladder[3]
    
    ladder_img = pygame.image.load("resource/ladder/ladder.png")
    ladder_img = pygame.transform.scale(ladder_img, (LADDER_WIDTH, ladder_len))
    ladder_img = pygame.transform.rotate(ladder_img, -ladder_angle)
    img_height = pygame.Surface.get_height(ladder_img)
    display_surf.blit(ladder_img, (ladder_left, ladder_drop-img_height))
    
def initialScore():
    ''' Initialize score. 
    '''
    score = 0
    return score
    
def updateScore(score, move):
    ''' Update score. 
    Each move step earn a point
    '''
    if move == True:
        score += 1
    return score
    
def drawScore(score):
    ''' Draw score. 
    '''
    score_font = pygame.font.Font('freesansbold.ttf', 20)
    textSurfaceObj = score_font.render("SCORE: "+str(score), True, LIGHTBLUE, COLOR_BG)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.topleft = (0 + 10, MAIN_TOP + 10)
    display_surf.blit(textSurfaceObj, textRectObj)
    
def drawButtonPropmt(prompt):
    ''' Draw 'hold space key' prompt for new player. 
    Only draw when stop at the edge of the first rock, to help people know what to do
    '''
    if prompt == 1:
        prompt_font = pygame.font.Font('freesansbold.ttf', 30)
        textSurfaceObj = prompt_font.render("Hold space key", True, WHITE, COLOR_ROCK)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.bottomright = (MAN_CENTER-20, MAIN_BOT-20)
        display_surf.blit(textSurfaceObj, textRectObj)        

def drawBackgroundOver():
    ''' Draw background for game over screen. 
    '''
    display_surf.fill(COLOR_BG_OVER)
    
def drawScoreOver(score):
    ''' Draw 'GAME OVER' and score for game over screen. 
    '''
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
    ''' Draw button prompt to back to main routine for game over screen. 
    '''
    prompt_font = pygame.font.Font('freesansbold.ttf', 20)
    textSurfaceObj = prompt_font.render("Press space key to continue!", True, WHITE, COLOR_BG_OVER)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT - 40)
    display_surf.blit(textSurfaceObj, textRectObj)

def drawBackgroundStart():
    ''' Draw background for start screen. 
    '''
    display_surf.fill(COLOR_BG_START)
    
def drawTitleStart():
    ''' Draw title for start screen. 
    '''
    title_font = pygame.font.Font('freesansbold.ttf', 100)
    textSurfaceObj = title_font.render("L A D D E R", True, BLUE, COLOR_BG_START)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//3)
    display_surf.blit(textSurfaceObj, textRectObj)

def drawPromptStart():
    ''' Draw button prompt to start main routine for start screen. 
    '''
    prompt_font = pygame.font.Font('freesansbold.ttf', 20)
    textSurfaceObj = prompt_font.render("Press space key to continue!", True, BLACK, COLOR_BG_START)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (WINDOW_WIDTH//2, MAIN_BOT - RIVER_HEIGHT_OVERLAP - 40)
    display_surf.blit(textSurfaceObj, textRectObj)
    
#====入口
if __name__ == '__main__':
    main()
