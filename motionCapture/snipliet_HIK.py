__author__ = 'alfred'

import pymel.core as pm

# T포즈로 변경
pm.select('bodyMesh')
pm.mel.gotoBindPose()

pm.mel.HIKCharacterControlsTool() # 툴 로드 : 이구문이 있어야 HIK툴을 로딩함

# HIK 노드 생성
pm.mel.hikCreateDefinition();
HIK = pm.PyNode( pm.melGlobals['gHIKCurrentCharacter'] )
HIK.rename('MC')
#pm.mel.refreshAllCharacterLists()

# 각 파트 어싸인
pm.mel.setCharacterObject("Hips",'MC',1,0)
pm.mel.setCharacterObject("LeftUpLeg",'MC',2,0)
pm.mel.setCharacterObject("LeftLeg",'MC',3,0)
pm.mel.setCharacterObject("LeftFoot",'MC',4,0)
pm.mel.setCharacterObject("RightUpLeg",'MC',5,0)
pm.mel.setCharacterObject("RightLeg",'MC',6,0)
pm.mel.setCharacterObject("RightFoot",'MC',7,0)
pm.mel.setCharacterObject("Spine",'MC',8,0)
pm.mel.setCharacterObject("LeftArm",'MC',9,0)
pm.mel.setCharacterObject("LeftForeArm",'MC',10,0)
pm.mel.setCharacterObject("LeftHand",'MC',11,0)
pm.mel.setCharacterObject("RightArm",'MC',12,0)
pm.mel.setCharacterObject("Head",'MC',15,0)
pm.mel.setCharacterObject("RightForeArm",'MC',13,0)
pm.mel.setCharacterObject("RightHand",'MC',14,0)
pm.mel.setCharacterObject("LeftToeBase",'MC',16,0)
pm.mel.setCharacterObject("RightToeBase",'MC',17,0)
pm.mel.setCharacterObject("LeftShoulder",'MC',18,0)
pm.mel.setCharacterObject("RightShoulder",'MC',19,0)
pm.mel.setCharacterObject("Neck",'MC',20,0)
pm.mel.setCharacterObject("LeftFingerBase",'MC',21,0)
pm.mel.setCharacterObject("RightFingerBase",'MC',22,0)
pm.mel.setCharacterObject("Spine1",'MC',23,0)
pm.mel.setCharacterObject("Spine2",'MC',24,0)

# 잠금
pm.mel.HIKCharacterControlsTool() # 업데이트
lockState = pm.mel.hikIsDefinitionLocked('MC')
pm.mel.hikCharacterLock('MC',not lockState,1)
pm.mel.hikUpdateDefinitionButtonState() # Update the button states
