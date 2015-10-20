# coding=utf-8
__author__ = 'alfred'

import pymel.core as pm

# 모션캡쳐 조인트리스트
mocapJoints = [
    'Hips',
    'Spine',
    'Spine1',
    'Spine2',
    'Neck',
    'Head',

    'LeftShoulder',
    'LeftArm',
    'LeftForeArm',
    'LeftHand',
    'LeftFingerBase',

    'RightShoulder',
    'RightArm',
    'RightForeArm',
    'RightHand',
    'RightFingerBase',

    'LeftUpLeg',
    'LeftLeg',
    'LeftFoot',
    'LeftToeBase',

    'RightUpLeg',
    'RightLeg',
    'RightFoot',
    'RightToeBase',
    ]

# 모션캡쳐용 마야 파일 위치
maFile = '/'.join( __file__.split('\\')[:-1] ) + '/file/MC.ma'

def selectMocapJoints():
    pm.select(mocapJoints)

def importMocapCharacter():
    ''' 캐릭터파일을 씬으로 임포트 함, 이 파일을 업체로 보낼것! '''
    return pm.importFile( maFile )

def createFallowCam( ):
    ''' 캐릭터를 따라다니는 카메라 생성 '''

    # 선택한 물체에서 네임 스페이스 얻어옴.
    ns = ''
    sel = pm.selected()
    if sel:
        ns = sel[0].namespace()

    # 컨스트레인 걸 대상 리스트 확보
    jnts = ['Hips','Spine*','*Leg','*Foot']
    #jnts = ['Spine*','*Foot']
    targets = []
    for j in jnts:
        targets.extend( pm.ls( ns + j, exactType='joint' ) )

    # 확보 안됨 끝.
    if not targets:
        print u'캐릭터의 일부를 선택하세요.'
        return

    # 카메라와 그룹 생성
    cam = pm.camera(n='followCam')[0]
    grp = pm.group( cam, n='followCam_grp' )

    # 컨스트레인
    const = pm.pointConstraint( targets, grp ); pm.delete(const) # 우선 위치에 배치하고
    #pm.pointConstraint( targets, grp, skip='y' ) # 컨스트레인
    pm.pointConstraint( targets, grp ) # 컨스트레인

    # 카메라 조정
    cam.tz.set(1200)
    cam.focalLength.set(100)
    cam.centerOfInterest.set(1200)
    cam.filmFit.set(2) # vertical

    # 패널 조정
    activePanel = pm.playblast( activeEditor=True ).split('|')[-1]
    pm.modelPanel( activePanel, edit=True, camera=cam )

def createPreviewGrid( gridScale=1000):
    mesh = pm.polyPlane(sh=10,sw=10)
    mesh[0].s.set(gridScale,gridScale,gridScale) #그리드 하나당 1m
    mesh[0].getShape().overrideEnabled.set(True)
    mesh[0].getShape().overrideDisplayType.set(1) # 템플릿
    mesh[0].getShape().instObjGroups.disconnect()
    pm.polyDelEdge( [mesh[0].e[11], mesh[0].e[32], mesh[0].e[53], mesh[0].e[74], mesh[0].e[95], mesh[0].e[105], mesh[0].e[107], mesh[0].e[109], mesh[0].e[111], mesh[0].e[113], mesh[0].e[115:117], mesh[0].e[119], mesh[0].e[121], mesh[0].e[123], mesh[0].e[137], mesh[0].e[158], mesh[0].e[179], mesh[0].e[200]], cv=True, ch=1 )

    mesh2 = pm.polyPlane(sh=2,sw=2,h=1.005,w=1.005)
    #mesh2[0].s.set(gridScale,gridScale,gridScale) #그리드 하나당 1m
    mesh2[0].getShape().overrideEnabled.set(True)
    mesh2[0].getShape().overrideDisplayType.set(2) # 템플릿
    mesh2[0].getShape().instObjGroups.disconnect()

    pm.parent( mesh2[0].getShape(), mesh[0], s=True, r=True )
    pm.delete( mesh2[0] )   
    
    mesh[0].rename('previewGrid_10mx10m')

    if pm.objExists('Hips'):
        pm.delete( pm.pointConstraint('Hips',mesh[0]) )
        mesh[0].ty.set(0)