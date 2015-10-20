# coding=utf-8
'''
모션챕쳐 작업에 도움주는 스크립트 집합입니다.

# 모션캡쳐 캐릭터 파일 임포트
# 이 파일을 모션캡쳐 업체에 보낼것
mc.importMocapCharacter()

# 모션데이터가 입혀져 돌아온 파일을 
# 조정이 가능하도록 animation Clip화 하여 처리함.
# 모션블렌드를 위해 animationClip은 프로젝트 clip디렉토리에 따로 저장됨.
mc.makeAsset(
    mcFolder  = r'X:\2014_Nexon_Durango\3D_project\Share\scenes\MotionCapture\Recieved_Files', 
    exportDir = r'D:\Users\alfred\Desktop\tmp'
)

# 캐릭터를 따라다니는 카메라를 생성.
# 프리뷰 영상을 제작할때 사용
mc.createFallowCam()

'''

__author__ = 'Kyuho Choi | coke25@aiw.co.kr | Alfred Imageworks'

import makeAsset
reload(makeAsset)

from general import *
from makeAsset import *
from hikPose import *

import ui 
reload(ui)
from ui import ui