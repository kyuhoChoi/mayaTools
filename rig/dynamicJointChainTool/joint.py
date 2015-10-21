# -*- coding:utf-8 -*-
import pymel.core as pm
import maya.OpenMaya as om

#-----------------------------------------
#
# Transform Tools
#
#-----------------------------------------
def zeroGroup( *objs, **kwargs ):
    '''
    @param objs:
    @param kwargs:
    @return:
    '''
    if objs:
        pm.select(objs)
    objs = pm.ls(sl=True, flatten=True)
    if not objs: return

    prefix    = kwargs.get('prefix', kwargs.get('pfx', '' ) )
    suffix    = kwargs.get('suffix', kwargs.get('sfx', '_zro' ) )
    translate = kwargs.get('translate', kwargs.get('t', True ) )
    rotate    = kwargs.get('rotate',    kwargs.get('r', True ) )
    scale     = kwargs.get('scale',     kwargs.get('s', False ) )

    zeroGrps = []
    for obj in objs:
        obj = pm.PyNode(obj)

        grp = pm.group( n=prefix+obj+suffix, em=True)

        if translate : pm.delete( pm.pointConstraint(obj, grp) )
        if rotate    : pm.delete( pm.orientConstraint(obj, grp) )
        if scale     : pm.delete( pm.scaleConstraint(obj, grp) )

        parent = obj.getParent()
        if parent:
            grp.setParent(parent)

        obj.setParent(grp)
        zeroGrps.append( grp )

    if len(zeroGrps) == 1 :
        return zeroGrps[0]

    elif len(zeroGrps) > 1:
        return zeroGrps

#-----------------------------------------
#
# joint Split, Duplicate
#
#-----------------------------------------
def splitJoint( joint, subDiv ):
    '''
    조인트 나눔

    rig.splitJoint( pm.selected()[0], 3)

    update : 2015-04-04

    '''
    sel = pm.selected()

    # Recast
    joint  = pm.PyNode( joint )
    subDiv = int(subDiv)

    childJnt = joint.getChildren()[0]

    endPos  = childJnt.t.get()
    posUnit = endPos / subDiv

    sec_JNTs = [joint]
    for i in range(1,subDiv):
        jnt = pm.duplicate( joint, returnRootsOnly=True, renameChildren=True, parentOnly=True)[0]
        jnt.setParent( joint )
        jnt.t.set( posUnit * i )
        sec_JNTs.append(jnt)
    sec_JNTs.append(childJnt)

    #
    # 역스케일 설정(연결) : 이부분 안해주면.. 큰일남!!! 중요
    #
    for i in range( len( sec_JNTs[:-1]) ):
        sec_JNTs[i+1].inverseScale.disconnect()
        sec_JNTs[i].scale >> sec_JNTs[i+1].inverseScale

    sec_JNTs.reverse()
    for i in range( len( sec_JNTs[:-1]) ):
        sec_JNTs[i].setParent(sec_JNTs[i+1])
    sec_JNTs.reverse()

    if sel:
        pm.select(sel)

    return sec_JNTs

def duplicateJointChain( *joints ):
    '''
    update : 2015-04-04
    '''
    if joints:
        pm.select(joints)
    
    joints = pm.selected(type='joint')

    # 입력된게 없으면 에러
    if not joints:
        raise

    # 선택된게 하나이면?
    if len(joints)==1 :
        dupJnt = pm.duplicate( joints[0], po=True )[0]
        dupJnt.setParent( w=True )
        pm.select(dupJnt)

        return [dupJnt]

    else:
        startJoint = joints[0]
        endJoint   = joints[-1]

        # endJoint가 startJoint의 parent가 아니면 에러
        if endJoint not in startJoint.getChildren( allDescendents=True ):
            raise

        # 복사할 조인트 리스트 만듦
        jointList = [ endJoint ]
        p = endJoint.getParent()
        while p!=startJoint:
            jointList.append( p )
            p = p.getParent()
        jointList.append( startJoint )

        # 새로운 조인트 복사
        newJoint = []
        for jnt in jointList:
            jnt = pm.duplicate(jnt, returnRootsOnly=True, renameChildren=True, parentOnly=True)[0]
            newJoint.append(jnt)

        # parent
        for i in range( len(newJoint[:-1]) ):
            newJoint[i].setParent( newJoint[i+1])

        # 루트로 옮김
        newJoint[-1].setParent(w=True)

        #
        newJoint.reverse()

        return newJoint

def duplicateJoints( *joints ):
    '''
    update : 2015-04-04
    '''
    if joints:
        pm.select(joints)
    
    joints = pm.selected(type='joint')

    # 입력된게 없으면 에러
    if not joints:
        raise

    JNTs=[]
    for jnt in joints:
        dupJnt = pm.duplicate( jnt, po=True )[0]
        dupJnt.setParent( w=True )
        JNTs.append( dupJnt )

    pm.select(JNTs)

    return JNTs

#-----------------------------------------
#
# joint Orient
#
#-----------------------------------------
def strToVec( inputVal ):
    '''
    update : 2015-04-27
    '''
    # 입력된 값이 문자열일경우
    if isinstance( inputVal, basestring ):
        # 입력된 값을 앞뒤 빈칸을 없애고, 소문자로 변경
        inputVal = inputVal.strip().lower()

        # 아래 리스트에 없는 값이 들어오면 에러
        if not inputVal in ['x','y','z','-x','-y','-z']:
            raise

        # 매칭
        if   inputVal.lower()== 'x': return pm.dt.Vector( 1, 0, 0)
        elif inputVal.lower()=='-x': return pm.dt.Vector(-1, 0, 0)
        elif inputVal.lower()== 'y': return pm.dt.Vector( 0, 1, 0)
        elif inputVal.lower()=='-y': return pm.dt.Vector( 0,-1, 0)
        elif inputVal.lower()== 'z': return pm.dt.Vector( 0, 0, 1)
        elif inputVal.lower()=='-z': return pm.dt.Vector( 0, 0,-1)

    # TODO : 보강이 필요함.
    # 그 외의 값이 입력된경우 
    else:
        return pm.datatypes.Vector( inputVal )

def jntOrient( objs=[], orient=True, aimAxis='x', upAxis='y', worldAimVector='x', worldUpVector='y', worldUpType='scene'):
    '''
    update : 2015-04-27

    제약사항 :
        같은 오브젝트를 aim, up
    '''

    # args 처리
    if objs:
        pm.select(objs)
    objs = pm.ls(sl=True, type=['joint','transform'])
    if not objs:
        raise

    # 선택된 노드 리스팅
    sel = pm.selected()

    # 플래그 처리
    if worldUpType not in ['scene','object','objectrotation','vector']:
        raise

    aimAxis        = strToVec( aimAxis )
    worldAimVector = strToVec( worldAimVector )
    upAxis         = strToVec( upAxis )
    worldUpVector  = strToVec( worldUpVector ) 

    #=======================================================================
    #
    # Orient Joint to World 처리
    #
    #=======================================================================
    if not orient:  
        pm.joint( objs[0], e=True, oj='none', ch=False, zso=True )
        return

    #=======================================================================
    #
    # 시좍~
    #
    #=======================================================================
    joint  = None
    upObj  = None
    aimObj = None
    delList = []

    if len(objs)==1:
        # 하나만 선택했을때
        # aim축은 worldAimVector
        # up축은 worldUpVector
        # TODO : 조금 애매.. 함. 하나선택했을때 어떻게 동작할지 다시 생각해봐야할듯.

        joint  = objs[0] 
        aimObj = pm.spaceLocator()
        upObj  = pm.spaceLocator()
        delList.extend([aimObj,upObj])

        pm.delete( pm.pointConstraint( joint, aimObj) )    
        pm.delete( pm.pointConstraint( joint, upObj) )
        pm.move( aimObj, worldAimVector, os=True, r=True, wd=True)
        pm.move( upObj,  worldUpVector,  os=True, r=True, wd=True)

        # worldUpType이 'object', 'objecrotation'일경우엔 플래그 설정대로 작동 안함. 여기서 고쳐줌.
        if worldUpType in ['scene', 'vector']:        
            worldUpType = 'object'

    elif len(objs)==2:
        # 오브젝트를 두개 선택했을때.
        # 
        # up축은 마지막에 선택한 오브젝트를 향하고
        # aim축은 자식조인트를 향함.

        # worldAimVector, worldUpVector 플래그는 무시됨.

        selJnts = pm.ls( objs, type='joint' )
        if not selJnts:
            raise 
        joint  = selJnts[0] 

        objs.remove(joint)
        upObj  = objs[-1]

        aimObj = joint.getChildren( type='joint' )
        if not aimObj:
            raise

        # worldUpType이 'scene', 'vector'일경우엔 플래그 설정대로 작동 안함. 여기서 고쳐줌.
        if worldUpType in ['scene', 'vector']:        
            worldUpType = 'object'

    elif len(objs)>2:
        # 세개 이상의 오브젝트를 선택했을때.        
        # up축은 마지막에 선택한 오브젝트를 향하고
        # aim축은 두번째  오브젝트를 향함
        joint  = objs[0] 
        upObj  = objs[-1]   
        aimObj = objs[1]

        # worldUpType이 'scene', 'vector'일경우엔 플래그 설정대로 작동 안함. 여기서 고쳐줌.
        if worldUpType in ['scene', 'vector']:        
            worldUpType = 'object'

    # 더미생성
    joint_Loc = pm.spaceLocator(n='joint_loc')
    aim_Loc   = pm.spaceLocator(n='aim_loc')
    up_Loc    = pm.spaceLocator(n='up_loc')
    delList.extend([joint_Loc, aim_Loc, up_Loc])

    # 더미 위치조정       
    pm.delete( pm.parentConstraint( joint, joint_Loc ) )
    pm.delete( pm.pointConstraint( aimObj, aim_Loc) )    
    pm.delete( pm.pointConstraint( upObj, up_Loc) )

    # joint hierarchy 
    parent = joint.getParent()
    childs = joint.getChildren( type='transform' )

    # 로케이터를 joint와 같은 space에 놓고. 로케이션값 확인
    if parent:
        pm.parent( joint_Loc, parent )    
    pm.aimConstraint( aim_Loc, joint_Loc, aimVector=aimAxis, upVector=upAxis, worldUpType=worldUpType, worldUpVector=worldUpVector, worldUpObject=upObj)
    
    #
    # 결과값
    #
    result = joint_Loc.rotate.get()

    #=======================================================================
    #
    # 조인트에 값 적용
    #
    #=======================================================================
    # 1. joint에 childs(들)을 잠시 unparent
    if childs:
        pm.parent(childs, world=True)

    # 2. joint의 rotate관련 속성들 모두 초기화
    joint.rotate.     set(0,0,0)
    joint.rotateAxis. set(0,0,0)
    joint.jointOrient.set(result)

    # 3. children 있었으면 원상태로 돌림.
    if childs:
        pm.parent(childs, joint, absolute=True)

    #=======================================================================
    #
    # 정리
    #
    #=======================================================================
    # 관련 노드들 삭제
    pm.delete(delList)

    if sel:
        pm.select(sel)

def jntResetOrient( *joints ):
    '''
    조인트의 로테이션을 초기화
    update : 2015-04-27
    '''
    if joints:
        pm.select(joints)
    joints = pm.ls( sl=True, type='joint' )
    if not joints : 
        raise
    
    for jnt in joints:
        r = jnt.r.get()
        jo = jnt.jo.get()
        jnt.jo.set( r+jo )
        jnt.r.set(0,0,0)

#-----------------------------------------
#
# Mesh
#
#-----------------------------------------
def getClosestVertexOnMesh( mesh, position ):
    '''
    position에 가장 가까운 mesh의 vertex를 리턴
    '''
    mesh = pm.PyNode( mesh )
    pos = pm.dt.Vector( position )

    nodeDagPath = om.MObject()
    try:
        selectionList = om.MSelectionList()
        selectionList.add(mesh.name())
        nodeDagPath = om.MDagPath()
        selectionList.getDagPath(0, nodeDagPath)
    except:
        raise RuntimeError('OpenMaya.MDagPath() failed on %s' % mesh.name())

    mfnMesh = om.MFnMesh(nodeDagPath)

    pointA = om.MPoint(pos.x, pos.y, pos.z)
    pointB = om.MPoint()
    space  = om.MSpace.kWorld

    util = om.MScriptUtil()
    util.createFromInt(0)
    idPointer = util.asIntPtr()

    mfnMesh.getClosestPoint(pointA, pointB, space, idPointer)
    idx = om.MScriptUtil(idPointer).asInt()

    faceVerts = [mesh.vtx[i] for i in mesh.f[idx].getVertices()]
    vtx = None
    minLength = None
    for v in faceVerts:
        thisLength = (pos - v.getPosition(space='world')).length()
        if minLength is None or thisLength < minLength:
            minLength = thisLength
            vtx = v

    return vtx

#-----------------------------------------
#
# display
#
#-----------------------------------------
def toggleDisplayAxis( joints=[], vis=None ):
    '''
    update : 2015-04-27
    '''
    if joints:
        pm.select(joints)
    
    joints = pm.selected()
    if not joints: joints = pm.ls( exactType='joint' )
    if not joints: 
        return

    state = None
    if isinstance( vis, bool ):
        state = vis
    else:
        state = joints[0].displayLocalAxis.get()
        state = not state

    for obj in joints:
        obj.displayLocalAxis.set(state)

def toggleDisplayHandle( joints=[], vis=None  ):
    '''
    update : 2015-04-27
    '''
    if joints:
        pm.select(joints)
    
    joints = pm.selected()
    #if not joints: joints = pm.ls( exactType='joint' )
    if not joints: 
        return

    state = None
    if isinstance( vis, bool ):
        state = vis
    else:
        state = joints[0].displayHandle.get()
        state = not state

    for obj in joints:
        obj.displayHandle.set(state)

def toggleJointLabel( joints=[], vis=None  ):
    '''
    update : 2015-04-27
    '''
    if joints:
        pm.select(joints)    
    joints = pm.selected()
    if not joints: joints = pm.ls( exactType='joint' )
    if not joints: 
        return

    state = None
    if isinstance( vis, bool ):
        state = vis
    else:
        state = joints[0].drawLabel.get()
        state = not state

    for obj in joints:
        obj.drawLabel.set(state)

#-----------------------------------------
#
# converting
#
#-----------------------------------------
def edgeToJnt( edges=None, reverse=False, dispCV=False, dispAxis=False, createCurve=False):
    '''
    update : 2015-04-27
    '''
    if not edges:
        edges = pm.filterExpand( sm=32 )

    if not edges:
        raise

    # recast
    # edges = [ pm.PyNode(edge) for edge in edges ] # 이렇게 하면 파이멜이 엣지를 제대로 처리 못함 선택한걸로 해야 할듯
    pm.select(edges)
    edges = pm.selected()

    # 엣지 이름에서 폴리곤 이름 알아옴
    mesh = pm.PyNode( edges[0].name().split('.')[0] )

    # 폴리곤에서 커브 추출
    crvFromPoly = pm.polyToCurve( form=0, degree=1, ch=False )[0]
    curve = pm.PyNode( crvFromPoly )
    curve.dispCV.set(dispCV)

    # cv좌표 얻어옴.
    points = curve.getCVs()

    # 좌표에 조인트 생성
    pm.select(cl=True)
    jnts = []
    for point in points:
        jnt = pm.joint( p=point )
        jnt.displayLocalAxis.set( dispAxis )
        jnts.append( jnt )

    # 뒤집기
    if reverse:
        # 조인트 뒤집음
        pm.select( jnts[-1] )
        pm.mel.RerootSkeleton()

        pm.reverseCurve( curve, replaceOriginal=True, ch=False )

        jnts.reverse()

    # 조인트 오리엔트 조정
    for jnt in jnts:
        parentJnt = jnt.getParent()
        if parentJnt:
            # point에서 가장 가까운 Vertex의 Normal을 up으로 설정
            pos   = parentJnt.getTranslation( ws=True)
            vtx   = getClosestVertexOnMesh( mesh, pos )
            pos   = vtx.getPosition( space='world' )
            norm  = vtx.getNormal()
            upPos = pos + norm

            upLoc = pm.spaceLocator(n='parentJnt_upLoc#')
            upLoc.t.set( upPos )

            jntOrient( [parentJnt, jnt, upLoc], aimAxis='x', worldAimVector='x', upAxis='y', worldUpVector='y' )

            #pm.joint( parentJnt, edit=True, zso=True, oj='xyz', sao='yup' )
            pm.delete( upLoc ) # 버텍스의 위치를 확인하고 싶으면 이 구문을 주석 처리할것
            pm.select( jnt )

    # 끝 조인트 오리엔트 조정
    pm.joint( jnts[-1], edit=True, oj='none' )

    if not createCurve:
        pm.delete( curve )

    return jnts

def crvToJnt( objs=[], div=None, ep=True ):
    '''
    update : 2015-04-27

    curve, upMesh 순으로 선택하고 실행
    div 를 명시하면 일정간격의 조인트를 얻음.

    import rig.joint as jnt
    jnt.crvToJnt()
    jnt.crvToJnt(ep=False)         # 해당 없음. 커브 cv 위치에 조인트가 생김
    jnt.crvToJnt(div=10)
    jnt.crvToJnt(ep=True)          # 해당 없음. 커브 ep 위치에 조인트가 생김
    jnt.crvToJnt(ep=False)         # 해당 없음. 커브 cv 위치에 조인트가 생김
    jnt.crvToJnt(div=10, ep=True)  # 해당 없음. 커브 cv 위치에 조인트가 생김
    jnt.crvToJnt(div=10, ep=False) # 해당 없음. 커브 cv 위치에 조인트가 생김

    '''
    # args
    if objs:
        pm.selec(objs)
    objs = pm.selected()
    if not objs:
        raise
   
    curves  = [pm.PyNode(c) for c in pm.filterExpand(sm=9) ]
    if not curves:
        raise

    upMeshs = []
    if pm.filterExpand(sm=12):    
        upMeshs = [pm.PyNode(c) for c in pm.filterExpand(sm=12) ] # 업축으로 사용할 메쉬

    node = curves[-1]
    nodeType = node.nodeType()
    #cv = True
    #ep = True

    transform = None
    crvShape  = None
    if nodeType == 'nurbsCurve':
        crvShape  = node
        transform = crvShape.getParent()
    elif nodeType == 'transform':
        transform = node
        crvShape  = transform.getShapes( type='nurbsCurve' )[0]

    if div:
        rebCrv, rebuild = pm.rebuildCurve( crvShape, ch=True, rpo=False, rt=4, end=1, kr=0, kcp=0, kep=1, kt=0, s=4, d=3, tol=0.001 ) # curvature type
        transform = rebCrv
        crvShape  = transform.getShapes( type='nurbsCurve' )[0]

    # 위치값 챙김.
    p=[]
    if div:
        if ep:
            for i in range(div+1):
                # 커브를 일정하게 나눈 위치 값을 가져옴
                p.append( pm.pointOnCurve( crvShape, turnOnPercentage=True, parameter=(1.0/div)*i ) )
        else:
            rebuild.rebuildType.set(0) # uniform
            rebuild.spans.set(div+1)
            for i in range( len( rebCrv.getCVs() ) ):
                p.append( crvShape.cv[i].getPosition() )

    else:
        if ep:
            # editPoint의 위치값을 가져옴
            for i in range( crvShape.numEPs() ):
                p.append( pm.xform( crvShape.ep[i], q=True, ws=True, t=True) )
        else:
            # cv의 위치값을 가져옴
            for i in range( len( crvShape.getCVs() ) ):
                p.append( crvShape.cv[i].getPosition() )

    if div:
        pm.delete( transform )

    JNTs = []
    pm.select(cl=True)
    for pos in p:
        JNTs.append( pm.joint( p=pos) )

    # 조인트 오리엔트 조정: 메쉬의 가장 가까운 점의 노말을 조인트의 up으로 설정
    if upMeshs:
        for jnt in JNTs:
            parentJnt = jnt.getParent()
            if parentJnt:
                # point에서 가장 가까운 Vertex의 Normal을 up으로 설정
                pos   = parentJnt.getTranslation( ws=True)
                vtx   = getClosestVertexOnMesh( upMeshs[0], pos )
                pos   = vtx.getPosition()
                norm  = vtx.getNormal()
                upPos = pos + norm * 1000000 # 노말 위치가 가까우면 방향이 틀어져 버림.. 그래서 큰 수를 곱함.

                upLoc = pm.spaceLocator(n='parentJnt_upLoc#')
                upLoc.t.set( upPos )

                jntOrient( [parentJnt, jnt, upLoc] )
                #pm.joint( parentJnt, edit=True, zso=True, oj='xyz', sao='yup' )
                pm.delete( upLoc )

    else:
        for jnt in JNTs:
            parentJnt = jnt.getParent()
            if parentJnt:
                up = pm.spaceLocator()

                grandParent = parentJnt.getParent()
                if grandParent:
                    pm.delete( pm.parentConstraint( grandParent, up ) )                    
                else:
                    pm.delete( pm.parentConstraint( parentJnt, up ) )

                jntOrient( [parentJnt, jnt, up], worldUpType='objectrotation' )
                pm.refresh()
                pm.select(jnt)
                pm.delete(up)

    # 끝 조인트 오리엔트 조정
    pm.joint( JNTs[-1], edit=True, oj='none' )

    pm.select( JNTs )

    return JNTs

def crvToJnt( curves=[], div=None, ep=True ):
    '''
    update : 2015-04-29
    '''
    # args
    if curves:
        pm.selec(curves)
    curves  = [pm.PyNode(c) for c in pm.filterExpand(sm=9) ]
    if not curves:
        raise

    node     = curves[-1]
    nodeType = node.nodeType()

    transform = None
    crvShape  = None
    if nodeType == 'nurbsCurve':
        crvShape  = node
        transform = crvShape.getParent()
    elif nodeType == 'transform':
        transform = node
        crvShape  = transform.getShapes( type='nurbsCurve' )[0]

    if div:
        rebCrv, rebuild = pm.rebuildCurve( crvShape, ch=True, rpo=False, rt=4, end=1, kr=0, kcp=0, kep=1, kt=0, s=4, d=3, tol=0.001 ) # curvature type
        transform = rebCrv
        crvShape  = transform.getShapes( type='nurbsCurve' )[0]

    # 위치값 챙김.
    p=[]
    if div:
        if ep:
            for i in range(div+1):
                # 커브를 일정하게 나눈 위치 값을 가져옴
                p.append( pm.pointOnCurve( crvShape, turnOnPercentage=True, parameter=(1.0/div)*i ) )
        else:
            rebuild.rebuildType.set(0) # uniform
            rebuild.spans.set(div+1)
            for i in range( len( rebCrv.getCVs() ) ):
                p.append( crvShape.cv[i].getPosition() )

    else:
        if ep:
            # editPoint의 위치값을 가져옴
            for i in range( crvShape.numEPs() ):
                p.append( pm.xform( crvShape.ep[i], q=True, ws=True, t=True) )
        else:
            # cv의 위치값을 가져옴
            for i in range( len( crvShape.getCVs() ) ):
                p.append( crvShape.cv[i].getPosition() )

    if div:
        pm.delete( transform )

    JNTs = []

    pm.select(cl=True)
    for pos in p:
        JNTs.append( pm.joint( p=pos) )

    # 조인트 오리엔트 디폴트
    pm.joint( JNTs[0], e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True )
    
    pm.select( JNTs )

    return JNTs

def jntToCrv( joints=[], degree=3, ep=True ):
    '''
    update : 2015-04-27

    pm.select( hi=True )
    jointChain = pm.selected()
    curve = ut.jntToCrv( jointChain )
    HDL, EFF = pm.ikHandle( startJoint=jointChain[0], endEffector=jointChain[-1], curve=curve, createCurve=False, parentCurve=False, solver='ikSplineSolver' )
    '''
    if joints:
        pm.select(joints)
    joints = pm.ls(sl=True, type='joint')
    if not joints:
        raise

    # reCast
    #jnts = [ pm.PyNode(jnt) for jnt in joints]
    jnts = joints

    # 조인트 위치 가져옴
    points = []
    for jnt in jnts:
        point = jnt.getTranslation( ws=True )
        points.append( point )

    # 커브 생성
    crv = None
    if ep:
        crv= pm.curve( d=degree, ep=points )
        #rebuildCurve -ch 1 -rpo 1 -rt 0 -end 1 -kr 2 -kcp 1 -kep 1 -kt 0 -s 15 -d 1 -tol 0.01
        #pm.rebuildCurve( crv, ch=False, rpo=True, rt=0, end=1, kr=2, kcp=1, kep=1, kt=0, s=len(joints)+1, d=degree, tol=0.01 )

    else:
        crv= pm.curve( d=degree, p=points )

    return crv

def jointChainOrient( objs=[] ): # wip
    '''
    update : 2015-04-29
    '''
    if objs:
        pm.selec(objs)
    objs = pm.ls(sl=True, o=True)
    if not objs:
        raise

    joints = pm.ls(sl=True, type='joint')
    if not joints:
        raise

    upMeshs = []
    if pm.filterExpand(sm=12):    
        upMeshs = [pm.PyNode(c) for c in pm.filterExpand(sm=12) ] # 업축으로 사용할 메쉬

    # 조인트 오리엔트 조정: 메쉬의 가장 가까운 점의 노말을 조인트의 up으로 설정
    if upMeshs:
        for jnt in joints:
            parentJnt = jnt.getParent()
            if parentJnt:
                # point에서 가장 가까운 Vertex의 Normal을 up으로 설정
                pos   = parentJnt.getTranslation( ws=True)
                vtx   = getClosestVertexOnMesh( upMeshs[0], pos )
                pos   = vtx.getPosition()
                norm  = vtx.getNormal()
                upPos = pos + norm * 1000000 # 노말 위치가 가까우면 방향이 틀어져 버림.. 그래서 큰 수를 곱함.

                upLoc = pm.spaceLocator(n='parentJnt_upLoc#')
                upLoc.t.set( upPos )

                jntOrient( [parentJnt, jnt, upLoc] )
                #pm.joint( parentJnt, edit=True, zso=True, oj='xyz', sao='yup' )
                pm.delete( upLoc )

    else:
        for jnt in joints:
            parentJnt = jnt.getParent()
            if parentJnt and parentJnt.type()=='joint':
                print jnt
                up = pm.spaceLocator()

                grandParent = parentJnt.getParent()
                if grandParent and grandParent.type()=='joint':
                    pm.delete( pm.parentConstraint( grandParent, up ) )                    
                else:
                    pm.delete( pm.parentConstraint( parentJnt, up ) )

                jntOrient( [parentJnt, jnt, up], worldUpType='objectrotation' )
                pm.refresh()
                pm.select(jnt)
                pm.delete(up)

    # 끝 조인트 오리엔트 조정
    if len(joints)>1:    
        pm.joint( joints[-1], edit=True, oj='none' )

#-----------------------------------------
#
# JointChain
#
#-----------------------------------------
def jointChain( joints=[], prefix='chain', ctrlNum=3 ):
    if joints:
        pm.select(joints)
    joints = pm.ls(sl=True, type='joint')
    if not joints:
        raise

    if ctrlNum < 2:
        raise
    
    jointNum = len(joints)
    degree = 3
    if ctrlNum == 3:
        degree = 2    

    # =============================
    #
    #  컨트롤러 
    #
    # =============================
    crv = jntToCrv(joints, degree=3, ep=True )
    
    ctrlRbd_crv, ctrlRbd_rbd = pm.rebuildCurve( crv, 
        ch=True, 
        replaceOriginal=False, 
        rebuildType=0, 
        endKnots=1, 
        keepRange=0, 
        keepControlPoints=0, 
        keepEndPoints=1, 
        keepTangents=0, 
        spans=ctrlNum-degree, 
        degree=degree,
        tol=0.01
        )

    # create curve cv clusters    

    anims = []

    pm.select( ctrlRbd_crv.cv )    
    for cv in pm.ls(sl=True, fl=True):
        anims.append( pm.cluster( cv )[0] )
        #anim = pm.cluster( cv, wn=(self.start_T_anim,self.start_T_anim) )[0]

    #
    #
    # ikHandle
    #
    HDL, EFF = pm.ikHandle( solver='ikSplineSolver', startJoint=joints[0], endEffector=joints[-1], createCurve=False, curve=ctrlRbd_crv, parentCurve=False )
    HDL.rename( prefix+'_HDL')
    EFF.rename( prefix+'_EFF')

    #
    #
    # 그루핑
    #
    rigGrp = pm.group(n=prefix+'_jointChain_grp#',em=True)
    rigGrp.v.set(False)
    pm.parent( HDL, crv, ctrlRbd_crv, rigGrp)


    # =============================
    #
    #  spline IK, Stretch & Distribute Joint
    #
    # =============================
    #
    # 커브 리빌드, 익스텐드
    #
    rdbCrv, rbd = pm.rebuildCurve( 
        ctrlRbd_crv, 
        ch=True, 
        replaceOriginal=False, 
        rebuildType=0, # uniform
        endKnots=1,    # 0 - uniform end knots, 1 - multiple end knots
        keepRange=0,   # 0 - reparameterize the resulting curve from 0 to 1, 1 - keep the original curve parameterization, 2 - reparameterize the result from 0 to number of spans
        keepControlPoints=False, 
        keepEndPoints=True, 
        keepTangents=True, 
        spans=len(joints), 
        degree=3, 
        tol=0.001 
        )

    #
    #   Locators on Curve
    #
    unit = 1.0 / (len(joints)-1)
    locOnCrvs = []
    for i in range(len(joints)):
        param = unit * i

        xformOnCrv = pm.spaceLocator( n='xformOnCrv#')

        xformOnCrv.addAttr( 'parameter',        sn='pr',  dv=param, keyable=True )
        xformOnCrv.addAttr( 'turnOnPercentage', sn='top', dv=False, at='bool', keyable=True )
        xformOnCrv.addAttr( 'revRotation',  sn='rot', keyable=True )

        xformOnCrv.it.set(False)
        xformOnCrv.rename( 'xformOnCrv%02d'%i )

        pntOnCrv = pm.PyNode( pm.pointOnCurve( rdbCrv.getShape(), parameter=param, ch=True ) )
        pntOnCrv.turnOnPercentage.set(True)
        pntOnCrv.setAttr('parameter',        keyable=True)
        pntOnCrv.setAttr('turnOnPercentage', keyable=True)
        pntOnCrv.rename( xformOnCrv+'_POC' )

        xformOnCrv.parameter        >> pntOnCrv.parameter
        xformOnCrv.turnOnPercentage >> pntOnCrv.turnOnPercentage
        pntOnCrv.position           >> xformOnCrv.t

        locOnCrvs.append(xformOnCrv)

    #
    # distance Rig
    #
    distNodes = []
    for i in range(len(locOnCrvs)-1):
        dist = pm.createNode( 'distanceDimShape' )
        locOnCrvs[i].worldPosition[0]   >> dist.startPoint
        locOnCrvs[i+1].worldPosition[0] >> dist.endPoint
        distNodes.append( dist )

    #
    # ik핸들 커브 변경
    #
    pm.ikHandle( HDL, e=True, curve=rdbCrv )

    #
    # connect To Joint
    #
    for dist, jnt in zip(distNodes, joints[1:]):
        dist.distance >> jnt.tx

    #
    # 그루핑
    #
    pm.parent(rdbCrv, locOnCrvs, [dist.getParent() for dist in distNodes], rigGrp)

def jointChainToDynamicChain( nodes=[] ):
    if nodes:
        pm.select(nodes)

    nodes = pm.ls(sl=True)

    # get joints
    joints = pm.ls(sl=True, type='joint')
    if not joints:
        raise

    crv = findSplineIKCrv( joints )[0]
    hdl = findIKHandle( joints )[0]
    pocs = crv.getShape().listHistory( future=True, type='pointOnCurveInfo' )

    #
    # makeDymicChain
    #
    outputCurve, follicle, hairSystem, nucleus = makeCurvesDynamic( crv )

    #
    # 일정간격 유지를 위해 커브 리빌드
    #
    rdbCrv, rbd = pm.rebuildCurve( 
        outputCurve, 
        ch=True, 
        replaceOriginal=False, 
        rebuildType=0, # uniform
        endKnots=1,    # 0 - uniform end knots, 1 - multiple end knots
        keepRange=0,   # 0 - reparameterize the resulting curve from 0 to 1, 1 - keep the original curve parameterization, 2 - reparameterize the result from 0 to number of spans
        keepControlPoints=False, 
        keepEndPoints=True, 
        keepTangents=True, 
        spans=100, 
        degree=3, 
        tol=0.001 
        )

    #
    # ik핸들 커브 변경
    #
    pm.ikHandle( hdl, e=True, curve=outputCurve )

    #
    # pointOnCurveInfo 변경
    #
    for poc in pocs:
        rdbCrv.worldSpace[0] >> poc.inputCurve
        
    pm.select(outputCurve)

def makeCurvesDynamic( nodes=[], prefix='' ):
    '''
    update : 2015-05-08

    #
    # 마야에서 기본으로 같은 기능을 하는 MakeCurvesDynamic 스크립트가 있으나 
    # 리턴 값이 없어 사용이 불가
    # pm.runtime.MakeCurvesDynamic('curve1')
    #
    # makeCurvesDynamic 2 { "0", "1", "0", "1", "0"};
    # $args[0] = surfaceAttach	  If true then connect the hairs to a surface(also selected) basing the uv on the nearest point to the first curve cv 
    # $args[1] = snapToSurface    If true and attaching to a surface then also snap the curve to the surface. 
    # $args[2] = matchPosition	  If true then make the input curve a degree one so resulting output curve exactly matches the position. 
    # $args[3] = createOutCurves  If true then output curves are created 
    # $args[4] = createPfxHair	  If true then hair is created.
    #
    '''

    # =========================================
    #
    #     입력
    #
    # =========================================
    if nodes:
        pm.select(nodes)

    # args
    curves = []
    curves  = [pm.PyNode(c) for c in pm.filterExpand(sm=9) ]
    if not curves:
        raise

    # get hairSystem
    hairSystem=None
    hairSystems = pm.ls(sl=True, dag=True, type='hairSystem')    
    if hairSystems:
        hairSystem = hairSystems[-1]
    
    # get nucleus
    nucleus=None
    nucleuss = pm.ls(sl=True, dag=True, type='nucleus')
    if nucleuss:
        nucleus = nucleuss[-1]


    # =========================================
    #
    #     생성
    #
    # =========================================
    #
    # 노드생성(1/4) : nucleus
    #
    if not nucleus and not hairSystem:       
        nucleus = pm.createNode( 'nucleus' )
        nucleus.rename( prefix+'_nucleus' )
        pm.PyNode('time1').outTime >> nucleus.currentTime
    
    #
    # 노드생성(2/4) : hairSystem
    #
    hairSystemTr = None
    if hairSystem:
        hairSystemTr = hairSystem.getParent()

    else:
        hairSystem   = pm.createNode( 'hairSystem' )
        hairSystemTr = hairSystem.getParent()
        hairSystemTr.rename( prefix+'_hairSys' )

        # 새로 생성된 헤어와 뉴클리어스 연결 << connectAttr nextAvailable플래그로 해결해보려했으나.. 복잡.. 아래처럼 멜을 사용하는게 제일 편함.
        #pm.PyNode('time1').outTime >> hairSystem.currentTime
        #hairSystem.currentState  >> nucleus.inputActive[0]
        #hairSystem.startState    >> nucleus.inputActiveStart[0]
        #nucleus.outputObjects[0] >> hairSystem.nextState
        #nucleus.startFrame       >> hairSystem.startFrame

        # 새로 생성된 헤어와 뉴클리어스 연결
        pm.mel.assignNSolver( nucleus )

        # default Value
        hairSystem.active.set( True )

    #
    # 노드생성(3/4) : follicle 생성
    #
    follicle   = pm.createNode( 'follicle' )
    follicleTr = follicle.getParent()
    follicleTr.rename( prefix+'_follicle' )

    # 기본값
    follicle.restPose.set(1)       # same as start
    follicle.startDirection.set(1) # start Curve base
    follicle.degree.set(2)
    follicle.clumpWidth.set(5)     # 폴리클 디스플레이 크기

    #
    # 노드생성(4/4) : curve Setting
    #
    # startCurve 생성
    startCurve = curves[-1]
    startCurve.setParent( follicleTr )
    startCurve.rename( prefix+'_startCurve' )

    # outputCurve 생성
    outputCurveShape = pm.createNode( 'nurbsCurve' )
    outputCurve      = outputCurveShape.getParent()
    outputCurve.rename( prefix+'_outputCurve' )


    # =========================================
    #
    #    연결
    #
    # =========================================
    settableNum = 0
    while True:    
        if hairSystem.inputHair[ settableNum ].isSettable():
            break
        settableNum +=1
    startCurve.getShape().worldSpace     >> follicle.startPosition
    follicle.outHair                     >> hairSystem.inputHair[ settableNum ]
    hairSystem.outputHair[ settableNum ] >> follicle.currentPosition    
    pm.connectAttr( follicle+'.outCurve', outputCurveShape+'.create' ) # follicle.outCurve >> outputCurveShape.create    # 이부분에서 다음 경고 발생:  Warning: pymel.core.general : Could not create desired MFn. Defaulting to MFnDagNode. # 

    # =========================================
    #
    #    리턴
    #
    # =========================================
    return outputCurve, follicle, hairSystem, nucleus

#-----------------------------------------
#
# dynamic Rig
#
#-----------------------------------------
def hairJiggle( nodes=[], prefix='jiggle', stretchable=True ):
    '''
    update : 2015-04-27

    #
    # 마야에서 기본으로 같은 기능을 하는 MakeCurvesDynamic 스크립트가 있으나 
    # 리턴 값이 없어 사용이 불가
    # pm.runtime.MakeCurvesDynamic('curve1')
    #
    # makeCurvesDynamic 2 { "0", "1", "0", "1", "0"};
    # $args[0] = surfaceAttach	  If true then connect the hairs to a surface(also selected) basing the uv on the nearest point to the first curve cv 
    # $args[1] = snapToSurface    If true and attaching to a surface then also snap the curve to the surface. 
    # $args[2] = matchPosition	  If true then make the input curve a degree one so resulting output curve exactly matches the position. 
    # $args[3] = createOutCurves  If true then output curves are created 
    # $args[4] = createPfxHair	  If true then hair is created.
    #
    '''    
    if nodes:
        pm.select(nodes)

    # get joints
    joints     = pm.ls(sl=True, type='joint')
    if not joints:
        raise

    # get hairSystem
    hairSystem=None
    hairSystems = pm.ls(sl=True, dag=True, type='hairSystem')    
    if hairSystems:
        hairSystem = hairSystems[-1]
    
    # get nucleus
    nucleus=None
    nucleuss = pm.ls(sl=True, dag=True, type='nucleus')
    if nucleuss:
        nucleus = nucleuss[-1]

    # store current state
    currentToolMode = pm.currentCtx()
    pm.setToolTo( 'selectSuperContext' )
    sel = pm.selected()

    #
    # nucleus
    #
    if not nucleus and not hairSystem:       
        nucleus = pm.createNode( 'nucleus' )
        nucleus.rename( prefix+'_nucleus' )
        pm.PyNode('time1').outTime >> nucleus.currentTime
    
    #
    # hairSystem
    #
    hairSystemTr = None
    if hairSystem:
        hairSystemTr = hairSystem.getParent()

    else:
        hairSystem   = pm.createNode( 'hairSystem' )
        hairSystemTr = hairSystem.getParent()
        hairSystemTr.rename( prefix+'_hairSys' )

        # 새로 생성된 헤어와 뉴클리어스 연결 << connectAttr nextAvailable플래그로 해결해보려했으나.. 복잡.. 멜을 사용하는게 제일 편함.
        #pm.PyNode('time1').outTime >> hairSystem.currentTime
        #hairSystem.currentState  >> nucleus.inputActive[0]
        #hairSystem.startState    >> nucleus.inputActiveStart[0]
        #nucleus.outputObjects[0] >> hairSystem.nextState
        #nucleus.startFrame       >> hairSystem.startFrame

        # 새로 생성된 헤어와 뉴클리어스 연결
        pm.mel.assignNSolver( nucleus )

        # default Value
        hairSystem.active.set( True )

    #
    # follicle 생성
    #
    follicle   = pm.createNode( 'follicle' )
    follicleTr = follicle.getParent()
    follicleTr.rename( prefix+'_follicle' )

    # follicle 위치조정
    pm.delete( pm.pointConstraint( joints[0], follicleTr ) )
    pm.delete( pm.orientConstraint( joints[0], follicleTr, offset=(0, 90, 0) ) )
    
    # follicle이 조인트, parent를 따라가도록설정
    # Start Joint의 Parent가 없으면 현재 Start에 페어런트 검.
    parent = joints[0].getParent()
    const = None
    if parent:
        const = pm.parentConstraint( parent, follicleTr, mo=True)
    else:
        const = pm.parentConstraint( joints[0], follicleTr, mo=True)

    # 기본값
    follicle.restPose.set(1)       # same as start
    follicle.startDirection.set(1) # start Curve base
    follicle.degree.set(2)
    follicle.clumpWidth.set(5)     # 폴리클 디스플레이 크기

    #
    # curve Setting
    #
    # startCurve 생성
    startCurve = jntToCrv( joints, degree=3, ep=True )
    startCurve.setParent( follicleTr )
    startCurve.rename( prefix+'_startCurve' )

    # outputCurve 생성
    outputCurveShape = pm.createNode( 'nurbsCurve' )
    outputCurve      = outputCurveShape.getParent()
    outputCurve.rename( prefix+'_outputCurve' )

    #
    # DG 
    #
    settableNum = 0
    while True:    
        if hairSystem.inputHair[ settableNum ].isSettable():
            break
        settableNum +=1
    startCurve.getShape().worldSpace     >> follicle.startPosition
    follicle.outHair                     >> hairSystem.inputHair[ settableNum ]
    hairSystem.outputHair[ settableNum ] >> follicle.currentPosition    
    pm.connectAttr( follicle+'.outCurve', outputCurveShape+'.create' ) # follicle.outCurve >> outputCurveShape.create    # 이부분에서 다음 경고 발생:  Warning: pymel.core.general : Could not create desired MFn. Defaulting to MFnDagNode. # 

    #
    #
    # ikHandle
    #
    HDL, EFF = pm.ikHandle( solver='ikSplineSolver', startJoint=joints[0], endEffector=joints[-1], createCurve=False, curve=outputCurveShape, parentCurve=False )
    HDL.rename( prefix+'_HDL')
    EFF.rename( prefix+'_EFF')

    #
    #
    # 그루핑
    #
    rigGrp = pm.group(n=prefix+'_jointChainRig_grp#',em=True)
    rigGrp.v.set(False)
    pm.parent(follicleTr, HDL, outputCurve, rigGrp)

    #
    #
    # 스트레치 세팅
    #
    if stretchable:
        #
        # 커브 리빌드, 익스텐드
        #
        rdbCrv, rbd = pm.rebuildCurve( 
            outputCurveShape, 
            ch=True, 
            replaceOriginal=False, 
            rebuildType=0, # uniform
            endKnots=1,    # 0 - uniform end knots, 1 - multiple end knots
            keepRange=0,   # 0 - reparameterize the resulting curve from 0 to 1, 1 - keep the original curve parameterization, 2 - reparameterize the result from 0 to number of spans
            keepControlPoints=False, 
            keepEndPoints=True, 
            keepTangents=True, 
            spans=len(joints), 
            degree=3, 
            tol=0.001 
            )

        #
        #   Locators on Curve
        #
        unit = 1.0 / (len(joints)-1)
        locOnCrvs = []
        for i in range(len(joints)):
            param = unit * i

            xformOnCrv = pm.spaceLocator( n='xformOnCrv#')

            xformOnCrv.addAttr( 'parameter',        sn='pr',  dv=param, keyable=True )
            xformOnCrv.addAttr( 'turnOnPercentage', sn='top', dv=False, at='bool', keyable=True )
            xformOnCrv.addAttr( 'revRotation',  sn='rot', keyable=True )

            xformOnCrv.it.set(False)
            xformOnCrv.rename( 'xformOnCrv%02d'%i )

            pntOnCrv = pm.PyNode( pm.pointOnCurve( rdbCrv.getShape(), parameter=param, ch=True ) )
            pntOnCrv.turnOnPercentage.set(True)
            pntOnCrv.setAttr('parameter',        keyable=True)
            pntOnCrv.setAttr('turnOnPercentage', keyable=True)
            pntOnCrv.rename( xformOnCrv+'_POC' )

            xformOnCrv.parameter        >> pntOnCrv.parameter
            xformOnCrv.turnOnPercentage >> pntOnCrv.turnOnPercentage
            pntOnCrv.position           >> xformOnCrv.t

            locOnCrvs.append(xformOnCrv)

        #
        # distance Rig
        #
        distNodes = []
        for i in range(len(locOnCrvs)-1):
            dist = pm.createNode( 'distanceDimShape' )
            locOnCrvs[i].worldPosition[0]   >> dist.startPoint
            locOnCrvs[i+1].worldPosition[0] >> dist.endPoint
            distNodes.append( dist )

        #
        # ik핸들 커브 변경
        #
        pm.ikHandle( HDL, e=True, curve=rdbCrv )

        #
        # connect To Joint
        #
        for dist, jnt in zip(distNodes, joints[1:]):
            dist.distance >> jnt.tx

        #
        # 그루핑
        #
        pm.parent(rdbCrv, locOnCrvs, [dist.getParent() for dist in distNodes], rigGrp)
        
    #
    #
    # restore state
    #
    pm.setToolTo( currentToolMode )
    if sel:
        pm.select(sel)
    else:
        pm.select(cl=True)

#-----------------------------------------
#
# find a Node
#
#-----------------------------------------
def getStartJnt( joint=None ):
    '''
    args:                                 ( joint )
                                              ↓                                
                 jnt1 > jnt2 > jnt3 > jnt4 > jnt5 > jnt6 > jnt7 > jnt8 > jnt9 > jnt10
                  ↓                                         
    return:      jnt1 

    JNTs = pm.selected( type='joint' )
    pm.select( ut.getStartJnt( JNTs[0] ) )
    pm.select( ut.getEndJnt(   JNTs[0] ) )
    pm.select( ut.getStartToEndJnt( JNTs[0],JNTs[-1] ) )
    pm.select( ut.getStartToEndJnt( JNTs[0] ) )
    pm.select( ut.getMiddleJoints( JNTs[0], JNTs[-1] ) )
    update : 2015-04-30
    '''
    if joint:
        pm.select(joint)
    sel = pm.ls(sl=True, type='joint')
    if not sel:
        raise
    
    joint = sel[0]    
    
    for i in range(10000):
        paren = joint.getParent()
        if not paren or len( paren.getChildren(type='joint') ) > 1:
            # parent가 없거나, joint Type동기가 둘 이상이면 정지
            break
        joint = joint.getParent()

    pm.select(joint)
    return joint

def getEndJnt( joint=None ):
    '''
    args:                                 ( joint )
                                              ↓                                
                 jnt1 > jnt2 > jnt3 > jnt4 > jnt5 > jnt6 > jnt7 > jnt8 > jnt9 > jnt10
                                                                                 ↓                                         
    return:                                                                     jnt10

    JNTs = pm.selected( type='joint' )
    pm.select( ut.getStartJnt( JNTs[0] ) )
    pm.select( ut.getEndJnt(   JNTs[0] ) )
    pm.select( ut.getStartToEndJnt( JNTs[0],JNTs[-1] ) )
    pm.select( ut.getStartToEndJnt( JNTs[0] ) )
    pm.select( ut.getMiddleJoints( JNTs[0], JNTs[-1] ) )

    update : 2015-04-30
    '''
    if joint:
        pm.select(joint)
    sel = pm.ls(sl=True, type='joint')
    if not sel:
        raise
    
    joint = sel[0]    
    
    for i in range(1000):
        childs = joint.getChildren( type='joint' )
        if not childs or len( childs ) > 1:
            # child가 없거나, 둘 이상이면 정지.
            break
        joint = joint.getChildren()[0]

    pm.select(joint)
    return joint

def getJointChain( *joints ):
    '''
    args:                    ( joint1,                            joint2 )
                                ↓                                 ↓
                 jnt1 > jnt2 > jnt3 > jnt4 > jnt5 > jnt6 > jnt7 > jnt8 > jnt9 > jnt10
                                ↓     ↓     ↓     ↓     ↓     ↓                                         
    return:                  [ jnt3,  jnt4,  jnt5,  jnt6,  jnt7,  jnt8 ] 

    JNTs = pm.selected( type='joint' )
    pm.select( ut.getStartJnt( JNTs[0] ) )
    pm.select( ut.getEndJnt(   JNTs[0] ) )
    pm.select( ut.getStartToEndJnt( JNTs[0],JNTs[-1] ) )
    pm.select( ut.getStartToEndJnt( JNTs[0] ) )
    pm.select( ut.getMiddleJoints( JNTs[0], JNTs[-1] ) )
    '''
    
    if joints:
        pm.select( joints )

    sel = pm.ls( sl=True, type='joint' )
    
    if not sel:
        raise
    
    joint1 = sel[0]
    
    if len(sel)>1:
        joint2 = sel[1]

    # joint2 입력이 없을경우 joint2는 체인 끝 조인트로 설정
    else:
        joint2 = getEndJnt( joint1 )

    # 같은 조인트가 입력 될경우 에러 발생
    if joint1 == joint2:
        pm.mel.error( u'같은 조인트는 안돼요.' )
 
    # 조인트의 상하 관계 파악
    # 같은 체인에 속해있지 않으면 에러 발생
    startJnt = None
    endJnt   = None
    if joint2 in joint1.getChildren( ad=True ):
        startJnt = joint1 
        endJnt   = joint2
    elif joint1 in joint2.getChildren( ad=True ):
        startJnt = joint2
        endJnt   = joint1 
    else:
        pm.mel.error( u'두 조인트가 하나의 체인에 속해야 합니다.' )

    # end joint부터 부모쪽으로 검사, startJnt를 찾기 전까지 중간 조인트들을 저장해놓음.
    JNTs = []
    JNTs.append( endJnt )
    sample = endJnt.getParent()
    while startJnt != sample:        
        JNTs.append( sample )
        sample = sample.getParent()
    JNTs.append( startJnt )

    # 부모 > 자식 순으로 정렬
    JNTs.reverse()

    pm.select(JNTs)
    return JNTs

def findIKHandle( joints=[] ):
    '''
    update : 2015-04-29
    '''
    if joints:
        pm.select(joints)
    joints = pm.ls(sl=True, type='joint')
    if not joints:
        raise TypeError(u'조인트 체인의 조인트이름을 명시하거나 선택하세요.')
    
    ikHandles = []
    for joint in joints:    
        print joint
        while joint:
            history = pm.listHistory( joint, future=True, type='ikHandle' )
            if history:
                ikHandles.append( history[0] )
                break
            else:
                joint = joint.getParent()

    if ikHandles:
        ikHandles = list(set(ikHandles)) # 중복 제거
        pm.select(ikHandles)

    return ikHandles

def findFollicle( joints=[] ):
    '''
    update : 2015-04-29
    '''
    ikHandles = findIKHandle( joints )
    
    follicles = []
    for ikHandle in ikHandles:       
        history = pm.listHistory( ikHandle, type='follicle' )
        if history:
            follicles.append( history[0] )

    if follicles:
        pm.select(follicles)

    return follicles
        
def findHairSystem( joints=[] ):
    '''
    update : 2015-04-29
    '''
    ikHandles = findIKHandle( joints )
    
    hairSystems = []
    for ikHandle in ikHandles:       
        history = pm.listHistory( ikHandle, type='hairSystem' )
        if history:
            hairSystems.append( history[0] )    
    
    if hairSystems:
        pm.select(hairSystems)

    return hairSystems

def findNucleus( joints=[] ):
    '''
    update : 2015-04-29
    '''
    hairSystems = findHairSystem( joints )

    nucleus = []
    for hairSystem in hairSystems:       
        history = pm.listHistory( hairSystem, type='nucleus' )
        if history:
            nucleus.append( history[0] )    
    
    if nucleus:
        pm.select(nucleus)

    return nucleus

def findDynamicCurve( joints=[] ):
    '''
    update : 2015-04-29
    '''
    follicles = findFollicle( joints )

    nurbsCurves = []
    for follicle in follicles:       
        history = pm.listHistory( follicle, future=True, type='nurbsCurve' )
        if history:
            nurbsCurves.append( history[0] )    
    
    if nurbsCurves:
        nurbsCurves = [crv.getParent() for crv in nurbsCurves ]
        pm.select(nurbsCurves)

    return nurbsCurves

def findJointChain( *joints ):
    getJointChain( *joints )

def findSplineIKCrv(joints=[]):
    '''
    update : 2015-05-08
    '''
    ikHandles = findIKHandle( joints )

    ikCurves = []
    for hdl in ikHandles:       
        history = pm.listHistory( hdl, type='nurbsCurve', levels=1 )
        if history:
            ikCurves.append( history[0].getParent() )  
    
    if ikCurves:
        pm.select(ikCurves)

    return ikCurves
