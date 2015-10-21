import pymel.core as pm
# -*- coding:utf-8 -*-

def biped():
    ''' 조인트 템플릿을 로드함 '''
    # \\alfredstorage\Alfred_asset\Maya_Shared_Environment\scripts_Python\alfredRig\file\
    #
    # RigTemplate_biped_Michael6HD.ma
    # RigTemplate_biped_Victoria6HD.ma
    # RigTemplate_biped_dazGen2.ma

    p = __file__.split('\\')
    p = p[:-1] + ['file/RigTemplate_biped_Michael6HD.ma']
    ma = '/'.join(p)
    
    print ma.replace('/','\\')
    
    pm.importFile(ma)
    #pm.file( ma, i=True, type="mayaAscii", mergeNamespacesOnClash=False, rpr="RigTemplate_biped_dazGen2_141001", options="v=0;", pr=True )

def findJointUp():
    ''' 조인트를 먼저 선택하고 실행하면 로케이터가 하나 생성됨, 원하는 방향으로 옮겨서 up위치를 파악함 '''
    jnt = pm.selected()[0]
    loc = pm.spaceLocator( n=jnt.split(':')[-1]+'__up')
    pm.delete( pm.parentConstraint( jnt, loc) )
    pm.select(loc)

    return loc

def lock(*args, **kwargs):
    if args:
        pm.select(args)
    sel = pm.ls(sl=True, o=True )

    t = kwargs.get('t', True)
    r = kwargs.get('r', True)

    locs=[]
    for item in sel:
        loc = pm.spaceLocator()
        loc.rename( 'lock_'+item )
        pm.delete( pm.parentConstraint( item, loc) )

        if t:
            skip = []
            for attr, axis in zip(['tx','ty','tz'],['x','y','z']):
                if pm.Attribute( item + '.' + attr).isLocked():
                    skip.append(axis)
            const = pm.pointConstraint(loc, item, skip=skip)
            pm.parent(const, loc)

        if r:
            skip = []
            for attr, axis in zip(['rx','ry','rz'],['x','y','z']):
                if pm.Attribute( item + '.' + attr).isLocked():
                    skip.append(axis)
            const = pm.orientConstraint(loc, item, skip=skip)
            pm.parent(const, loc)

        locs.append( loc )

    if sel:
        pm.select(locs)

def selectBindJnt():
    jntList = [ 
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
        'RightShoulder',
        'RightArm',
        'RightForeArm',
        'RightHand',

        'LeftUpLeg',
        'LeftLeg',
        'LeftFoot',
        'LeftToeBase',
        'RightUpLeg',
        'RightLeg',
        'RightFoot',
        'RightToeBase',

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

