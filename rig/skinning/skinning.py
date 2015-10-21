# coding=utf-8
__author__ = 'Kyuho Choi | coke25@aiw.co.kr | Alfred Imageworks'

import pymel.core as pm
import maya.cmds as cmds

def getBindJnt():

    jntList = [
        'Hips',
        'Spine',
        'Spine1',
        'Spine2',
        'Spine3',
        'Spine4',
        'Spine5',
        'Spine6',
        'Spine7',
        'Spine8',
        'Spine9',
        'Neck',
        'Neck1',
        'Neck2',
        'Neck3',
        'Neck4',
        'Neck5',
        'Neck6',
        'Neck7',
        'Neck8',
        'Neck9',
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

        # Finger Joints
        'LeftInHandThumb',
        'LeftHandThumb1',
        'LeftHandThumb2',
        'LeftHandThumb3',
        'LeftInHandIndex',
        'LeftHandIndex1',
        'LeftHandIndex2',
        'LeftHandIndex3',
        'LeftInHandMiddle',
        'LeftHandMiddle1',
        'LeftHandMiddle2',
        'LeftHandMiddle3',
        'LeftInHandRing',
        'LeftHandRing1',
        'LeftHandRing2',
        'LeftHandRing3',
        'LeftInHandPinky',
        'LeftHandPinky1',
        'LeftHandPinky2',
        'LeftHandPinky3',

        'RightInHandThumb',
        'RightHandThumb1',
        'RightHandThumb2',
        'RightHandThumb3',
        'RightInHandIndex',
        'RightHandIndex1',
        'RightHandIndex2',
        'RightHandIndex3',
        'RightInHandMiddle',
        'RightHandMiddle1',
        'RightHandMiddle2',
        'RightHandMiddle3',
        'RightInHandRing',
        'RightHandRing1',
        'RightHandRing2',
        'RightHandRing3',
        'RightInHandPinky',
        'RightHandPinky1',
        'RightHandPinky2',
        'RightHandPinky3',

        # Toe Joints
        'LeftInFootThumb',
        'LeftFootThumb1',
        'LeftFootThumb2',
        'LeftFootThumb3',
        'LeftInFootIndex',
        'LeftFootIndex1',
        'LeftFootIndex2',
        'LeftFootIndex3',
        'LeftInFootMiddle',
        'LeftFootMiddle1',
        'LeftFootMiddle2',
        'LeftFootMiddle3',
        'LeftInFootRing',
        'LeftFootRing1',
        'LeftFootRing2',
        'LeftFootRing3',
        'LeftInFootPinky',
        'LeftFootPinky1',
        'LeftFootPinky2',
        'LeftFootPinky3',

        'RightInFootThumb',
        'RightFootThumb1',
        'RightFootThumb2',
        'RightFootThumb3',
        'RightInFootIndex',
        'RightFootIndex1',
        'RightFootIndex2',
        'RightFootIndex3',
        'RightInFootMiddle',
        'RightFootMiddle1',
        'RightFootMiddle2',
        'RightFootMiddle3',
        'RightInFootRing',
        'RightFootRing1',
        'RightFootRing2',
        'RightFootRing3',
        'RightInFootPinky',
        'RightFootPinky1',
        'RightFootPinky2',
        'RightFootPinky3',

        'Tail',
        'Tail1',
        'Tail2',
        'Tail3',
        'Tail4',
        'Tail5',
        'Tail6',
        'Tail7',
        'Tail8',
        'Tail9',
        'Tail10',

        'LeftPectoral',
        'RightPectoral',
        'facialRoot',
        'Jaw',
        'LeftEye',
        'RightEye',
        ]

    sel = []
    notExists = []
    for node in jntList:
        if pm.objExists(node):
            sel.append(node)
        else :
            print '"%s" is not Exists'%node
            notExists.append(node)

    pm.select(sel)
    print "bindJnts =", sel
    print "notExistsJnt =", notExists

    return sel

def bindSkin( jnts, geometry ):
    return pm.skinCluster( jnts, geometry,
        toSelectedBones   = True,
        bindMethod        = 0,   # 0 - Closest distance between a joint and a point of the geometry.
                                 # 1 - Closest distance between a joint, considering the skeleton hierarchy, and a point of the geometry.
                                 # 2 - Surface heat map diffusion

        skinMethod        = 0,   # 0 - classical linear skinning (default).
                                 # 1 - dual quaternion (volume preserving),
                                 # 2 - a weighted blend between the two

        normalizeWeights  = 1,   # 0 - none,
                                 # 1 - interactive,
                                 # 2 - post (default)
        maximumInfluences = 1,
        dropoffRate       = 4,
        removeUnusedInfluence = False,
        )

def copySkinWeights_old( objs ):
    '''weightTransfer('skin_mesh', cmds.ls(sl=True) )'''
    skinDataObj = objs[0]
    targetObjs  = [pm.PyNode( obj ) for obj in objs[1:]]

    sourceSkin = pm.mel.findRelatedSkinCluster( skinDataObj )
    for i ,mesh in enumerate( targetObjs ):
        destinationSkin = pm.mel.findRelatedSkinCluster( mesh )
        try:
            pm.copySkinWeights(
                ss=sourceSkin,
                ds=destinationSkin,
                noMirror=True,
                surfaceAssociation='closestPoint',
                influenceAssociation=['closestJoint', 'closestBone', 'oneToOne']
                )
            print 'copySkinWeights (%d/%d): "%s" --> "%s"'%( i+1, len(targetObjs), skinDataObj, mesh )

        except :
            print 'copySkinWeights Fail (%d/%d): "%s" --> "%s"'%( i+1, len(targetObjs), skinDataObj, mesh )

def copySkinWeights(*args):
    '''
    스킨 웨이트를 여러 오브젝트에 옮겨줌
    디폴트 스킨이 적용된 여러 오브젝트를 먼저 선택한 후, 스키닝 데이터가 적용된 메쉬를 제일 마지막에 선택, 실행해줌.
    옵션은 마야 CopySkinWeightsOptions 세팅을 따름.
    '''
    if args:
        pm.select( args )
    sel = cmds.ls(sl=True, fl=True )
    if len(sel)<2 : return

    geos = sel[:-1]
    skinMesh = sel[-1]

    failedGeo = []
    for geo in geos:
        try:
            pm.select(skinMesh, geo)
            pm.mel.CopySkinWeights()
            pm.refresh()

            print '#--------------------------------------'
            print '#'
            print '#  copy weight (Success): "%s" --> "%s"'%(skinMesh, geo)
            print '#'
            print '#--------------------------------------'
        except:
            failedGeo.append(geo)
            print '#  copy weight (Fail) : "%s" --> "%s"'%(skinMesh, geo)

    if failedGeo:
        print 'failedGeo = ', failedGeo
        pm.select(failedGeo)

def getSkinCluster( obj ):
    '''return SkinCluster node of obj'''
    return pm.mel.findRelatedSkinCluster( obj )

def getInfluences( *args ):
    '''return influence nodes of obj'''
    if args:
        pm.select(args)

    OBJs = pm.ls( sl=True )
    if not OBJs: return

    INFs = []
    for obj in OBJs:
        inf = pm.skinCluster( pm.mel.findRelatedSkinCluster( obj ), query=True, inf=True)
        INFs.extend(inf)

    pm.select(INFs)
    return INFs

def setWeight( *args, **kwargs ):
    '''
    setWeight( componenets, influence, weightValue )
    setWeight( mesh.vtx[0], mesh.vtx[1]..., 'joint1', 1.0 )

    :version:
        2014-10-28 : args만으로 처리 할 수 있도록 조정

    :Sample Code:
        # ex1) 웨이트는 1.0
        setWeight( mesh.vtx[0], mesh.vtx[1], mesh.vtx[2], 'joint1', 1.0 )

        # ex2) 웨이트는 기본값으로 처리
        setWeight( mesh.vtx[0], mesh.vtx[1], mesh.vtx[2], 'joint1')

        # ex3) 웨이트는 0.5
        pm.select(mesh.vtx[0], mesh.vtx[1], mesh.vtx[2], 'joint1')
        setWeight(0.5)

        # ex4) 웨이트는 기본값으로 처리
        pm.select(mesh.vtx[0], mesh.vtx[1], mesh.vtx[2], 'joint1')
        setWeight()
    '''

    #
    # 웨이트부터 처리함, 인자 마지막값으로 정수나 실수가들어오면 웨이트 값으로 처리
    # 그렇지 않으면 기본값 1로 처리함.
    weight = 1
    if args:
        if isinstance(args[-1],int) or isinstance(args[-1],float):
            args = list(args)
            weight = float( args.pop(-1) )

    #
    # 입력된 오브젝트가 있는지 확인 : 없음 종료
    if args:
        pm.select( args )
    sel = cmds.ls(sl=True, fl=True)
    if len(sel)<2: return

    #
    # 요소 분리
    influences = cmds.ls(sel, type=['joint','transform'] )
    if not influences:
        print u'influence 오브젝트 하나는 선택해주세요.'
        return

    for inf in influences:
        sel.remove(inf)
    components = sel

    # 해당 인플루언스가 스킨클러스터에 포함 안된경우 경우 추가 할건지?
    addInfluence = kwargs.get('addInfluence', False)

    print '  components :',components
    print '   influence :',influences
    print '      weight :',weight
    print 'addInfluence :',addInfluence

    for comp in components:
        # 상이한 지오메트리 콤포넌트를 선택한 경우 스킨클러스터가 각기 다름.
        # 콤포넌트의 지오메트리를 확인하고, 콤포넌트별 해당 스킨클러스터를 파악함.
        geo = comp.split('.')[0]
        skinCluster = pm.mel.findRelatedSkinCluster( geo )

        if addInfluence:
            if influences not in pm.skinCluster( skinCluster, query=True, inf=True): # 콤포넌트마다 체크해야 해서 무거움.
                #
                # 인플루언스 추가
                pm.skinCluster( skinCluster, e=True, lw=True, wt=0.0, addInfluence=influence )
                print u'("%s") %s : "%s" 인플루언스 오브젝트 추가' %(skinCluster, geo, influence)

        #------------------------------
        #
        #        웨이트값 변경
        #
        #------------------------------
        w = float(weight) / len(influences)
        tv = []
        for influence in influences:
            tv.append((influence,w))
        print '("%s") %s : %s '%(skinCluster, comp, tv)

        # pm.skinPercent( skinCluster, comp, tv=[(influence, w)] )
        pm.skinPercent( skinCluster, comp, tv=tv )

