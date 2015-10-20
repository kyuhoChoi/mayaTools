from maya import cmds

# joint
cmds.select('Hips',hi=True)
_joint = cmds.ls(sl=True)

# skinMesh
_skinMesh = 'SkinBody'

# mesh
cmds.select('Mesh_High',hi=True)
_meshShape = cmds.ls(sl=True, type='mesh')
cmds.select(_meshShape)
_mesh= cmds.pickWalk(d='up')

# bindSkin
cmds.select(_joint,_mesh)

# copy
for _item in _mesh:
    cmds.select(_skinMesh,_item)
    cmds.copySkinWeights(noMirror=True, surfaceAssociation='closestPoint', influenceAssociation=['closestJoint','closestBone','oneToOne'], normalize=True)

# HIK Remove Finger
from maya import mel
_fingerJnt = [
    ( 50,'LeftHandThumb1'),
    ( 51,'LeftHandThumb2'),        # 51
    ( 52,'LeftHandThumb3'),        # 52
    ( 53,'LeftHandThumb4'),        # 53
    ( 54,'LeftHandIndex1'),        # 54
    ( 55,'LeftHandIndex2'),        # 55 ----
    ( 56,'LeftHandIndex3'),        # 56
    ( 57,'LeftHandIndex4'),        # 57
    ( 58,'LeftHandMiddle1'),       # 58
    ( 59,'LeftHandMiddle2'),       # 59
    ( 60,'LeftHandMiddle3'),       # 60 ----
    ( 61,'LeftHandMiddle4'),       # 61
    ( 62,'LeftHandRing1'),         # 62
    ( 63,'LeftHandRing2'),         # 63
    ( 64,'LeftHandRing3'),         # 64
    ( 65,'LeftHandRing4'),         # 65 ----
    ( 66,'LeftHandPinky1'),        # 66
    ( 67,'LeftHandPinky2'),        # 67
    ( 68,'LeftHandPinky3'),        # 68
    ( 69,'LeftHandPinky4'),        # 69
    ( 70,'LeftHandExtraFinger1'),  # 70 ----
    ( 71,'LeftHandExtraFinger2'),  # 71
    ( 72,'LeftHandExtraFinger3'),  # 72
    ( 73,'LeftHandExtraFinger4'),  # 73
    ( 74,'RightHandThumb1'),       # 74
    ( 75,'RightHandThumb2'),       # 75 ----
    ( 76,'RightHandThumb3'),       # 76
    ( 77,'RightHandThumb4'),       # 77
    ( 78,'RightHandIndex1'),       # 78
    ( 79,'RightHandIndex2'),       # 79
    ( 80,'RightHandIndex3'),       # 80 ----
    ( 81,'RightHandIndex4'),       # 81
    ( 82,'RightHandMiddle1'),      # 82
    ( 83,'RightHandMiddle2'),      # 83
    ( 84,'RightHandMiddle3'),      # 84
    ( 85,'RightHandMiddle4'),      # 85 ----
    ( 86,'RightHandRing1'),        # 86
    ( 87,'RightHandRing2'),        # 87
    ( 88,'RightHandRing3'),        # 88
    ( 89,'RightHandRing4'),        # 89
    ( 90,'RightHandPinky1'),       # 90 ----
    ( 91,'RightHandPinky2'),       # 91
    ( 92,'RightHandPinky3'),       # 92
    ( 93,'RightHandPinky4'),       # 93
    ( 94,'RightHandExtraFinger1'), # 94
    ( 95,'RightHandExtraFinger2'), # 95 ----
    ( 96,'RightHandExtraFinger3'), # 96
    ( 97,'RightHandExtraFinger4'), # 97
    (146,'LeftInHandThumb'),       # 146
    (147,'LeftInHandIndex'),       # 147
    (148,'LeftInHandMiddle'),      # 148
    (149,'LeftInHandRing'),        # 149
    (150,'LeftInHandPinky'),       # 150 ----
    (151,'LeftInHandExtraFinger'), # 151
    (152,'RightInHandThumb'),      # 152
    (153,'RightInHandIndex'),      # 153
    (154,'RightInHandMiddle'),     # 154
    (155,'RightInHandRing'),       # 155 ----
    (156,'RightInHandPinky'),      # 156
    (157,'RightInHandExtraFinger') # 157
]
_HIKNode = 'MC'
for _i,_jnt in enumerate(_fingerJnt):
    mel.eval( 'setCharacterObject("","%s",%d,0);'%(_HIKNode,_jnt[0]) )

#------------------------------------
#
#           Mila
#
#------------------------------------
from maya import cmds
# joint
_Mila_SkinJnt = ['Hips','Spine','Spine1','Spine2','Spine3','Neck','Head','jiggle_Hair_C1','jiggle_Hair_C2','jiggle_Hair_C3','jiggle_Hair_R1','jiggle_Hair_R2','jiggle_Hair_R3','jiggle_Hair_L1','jiggle_Hair_L2','jiggle_Hair_L3','LeftShoulder','LeftArm','LeftArmRoll','LeftForeArm','LeftForeArmRoll','LeftHand','LeftInHandThumb','LeftHandThumb1','LeftHandThumb2','LeftHandThumb3','LeftInHandIndex','LeftHandIndex1','LeftHandIndex2','LeftHandIndex3','LeftInHandMiddle','LeftHandMiddle1','LeftHandMiddle2','LeftHandMiddle3','LeftInHandRing','LeftHandRing1','LeftHandRing2','LeftHandRing3','LeftInHandPinky','LeftHandPinky1','LeftHandPinky2','LeftHandPinky3','RightShoulder','RightArm','RightArmRoll','RightForeArm','RightForeArmRoll','RightHand','RightInHandThumb','RightHandThumb1','RightHandThumb2','RightHandThumb3','RightInHandIndex','RightHandIndex1','RightHandIndex2','RightHandIndex3','RightInHandMiddle','RightHandMiddle1','RightHandMiddle2','RightHandMiddle3','RightInHandRing','RightHandRing1','RightHandRing2','RightHandRing3','RightInHandPinky','RightHandPinky1','RightHandPinky2','RightHandPinky3','jiggle_Neckband_1','jiggle_Neckband_2','LeftUpLeg','LeftUpLegRoll','LeftLeg','LeftLegRoll','LeftFoot','LeftToeBase','RightUpLeg','RightUpLegRoll','RightLeg','RightLegRoll','RightFoot','RightToeBase']
cmds.select( _Mila_SkinJnt )

# mesh
cmds.select('Mesh_High',hi=True)
_meshShape = cmds.ls(sl=True, type='mesh')
cmds.select(_meshShape)
_mesh= cmds.pickWalk(d='up')

# bindSkin
cmds.select(_Mila_SkinJnt,_mesh)

# skinMesh
_skinMesh = 'SkinBody'
# copy
for _item in _mesh:
    cmds.select(_skinMesh,_item)
    cmds.copySkinWeights(noMirror=True, surfaceAssociation='closestPoint', influenceAssociation=['closestJoint','closestBone','oneToOne'], normalize=True)

#------------------------------------
#
#           Sniper Gun Rig
#
#------------------------------------
_hipsJnt  = 'CHAR:Hips'
_spineJnt = 'CHAR:Spine2'
_handJnt = 'CHAR:LeftHand'
_buttPlate_Point = 'CHAR:RightArm'

_prefix           = 'snperGun_'
_rigRoot          = _prefix+'Rig'
_buttPlate_pos    = _prefix+'buttPlate_pos'
_buttPlate_offset = _prefix+'buttPlate_offset'
_up               = _prefix+'up'
_aim              = _prefix+'aim'
_grapHand         = _prefix+'grapHand'
_gunPos_offset    = _prefix+'gunPos_offset'
_gunPos           = _prefix+'gunPos'

_rigRoot = cmds.group(name=_rigRoot, em=True)
cmds.parentConstraint( _hipsJnt, _rigRoot )

_grapHand = cmds.group(name=_grapHand, em=True)
cmds.parentConstraint( _handJnt, _grapHand )
cmds.parent(_grapHand, _rigRoot)

_aim = cmds.spaceLocator( name=_aim )[0]
cmds.setAttr( _aim+'.displayHandle', 1)
_tmp = cmds.pointConstraint( _grapHand, _aim); cmds.delete(_tmp)
cmds.parent(_aim, _grapHand)

_buttPlate_pos    = cmds.spaceLocator( name=_buttPlate )[0]
cmds.setAttr( _buttPlate_pos+'.displayHandle', 1)

_buttPlate_offset = cmds.group( _buttPlate_pos, name=_buttPlate_offset)
cmds.parentConstraint( _spineJnt, _buttPlate_offset )
_tmp = cmds.pointConstraint( _buttPlate_Point, _buttPlate_pos ); cmds.delete(_tmp)
cmds.parent(_buttPlate_offset, _rigRoot)

_up    = cmds.spaceLocator( name=_up )[0]
cmds.setAttr( _up+'.displayHandle', 1)

_tmp = cmds.pointConstraint( _buttPlate_Point, _up, offset=[0,5,0] ); cmds.delete(_tmp)
cmds.parent(_up, _rigRoot)

cmds.aimConstraint( _aim, _buttPlate_pos, aimVector=[0,0,1], upVector=[0,1,0], worldUpType='object', worldUpObject=_up)

_gunPos = cmds.spaceLocator( name=_gunPos )[0]
cmds.setAttr( _gunPos+'.displayHandle', 1)

_gunPos_offset = cmds.group( _gunPos, name=_gunPos_offset)
cmds.pointConstraint (_aim, _buttPlate_pos, _gunPos_offset)
cmds.aimConstraint( _aim, _gunPos_offset, aimVector=[0,0,1], upVector=[0,1,0], worldUpType='object', worldUpObject=_up)
cmds.parent(_gunPos_offset, _rigRoot)





