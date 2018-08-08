#coding:utf-8

import random, time, pygame, sys
from pygame.locals import *


#全局变量
FPS = 25
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 960

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
MAN_RIGHT = WINDOW_WIDTH*3//8
MAN_HEIGHT = WINDOW_HEIGHT//6
MAN_TOP = MAIN_BOT-MAN_HEIGHT
MAN_BOT = MAIN_BOT
