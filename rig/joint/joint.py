# -*- coding:utf-8 -*-
import pymel.core as pm
import maya.OpenMaya as om

#
# joint Split, Duplicate
#
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

#
# joint Orient
#
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

#
# Mesh
#
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

#
# converting
#
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

# =============================================================
#
# TODO : 아래 코드들은 검증 필요함.
#
# =============================================================

#
# createJointGeo
#
def createJointGeo( joints=[], constraint=False, parent=True, color=True ):
    if not joints:
        joints = pm.selected(type='joint')

    GEOs = []
    for jnt in joints:
        jnt   = pm.PyNode(jnt)
        child = jnt.getChildren( type='joint' )

        if not child: continue # 자식 조인트가 없으면 넘어감

        # 지오메트리 생성
        geo = pm.polyCube(ch=False)[0]

        #
        geo.setParent(jnt)

        geo.t.set( child[0].t.get() * 0.5 )
        geo.r.set( 0,0,0 )

        # 스케일 조정
        tr   = child[0].t.get()
        abtr = [ abs(val) for val in tr ]

        radius = jnt.radius.get() * 2
        sx = abtr[0] if abtr[0] > 0.001 else radius
        sy = abtr[1] if abtr[1] > 0.001 else radius
        sz = abtr[2] if abtr[2] > 0.001 else radius
        geo.s.set( sx,sy,sz )

        # 이름 변경
        geo.rename( jnt.name()+'_geo' )

        # 지오메트리 pivot 옮김
        copyPivot( jnt, geo )

        # transform 초기화
        pm.makeIdentity(geo, t=True, r=True, s=True, apply=True)

        if color:
            assignColorAxisShader( geo.f[4], 'x' )
            assignColorAxisShader( geo.f[1], 'y' )
            assignColorAxisShader( geo.f[0], 'z' )

        if not parent:
            geo.setParent(w=True)

        # 구속
        if constraint:
            geo.setParent(w=True)
            pm.parentConstraint(jnt,geo)
            pm.scaleConstraint(jnt,geo)

        GEOs.append(geo)

    return GEOs

def assignColorAxisShader( geo, axis ):
    br = .5 # 밝기
    if   axis == 'x':
        axisColor = (1,br,br)
    elif axis == 'y':
        axisColor = (br,1,br)
    elif axis == 'z':
        axisColor = (br,br,1)

    shaderName = 'axisLambert_'+axis

    shader = None
    if pm.objExists( shaderName ):
        shader = pm.PyNode(shaderName)
    else:
        shader = pm.shadingNode( 'lambert', asShader=True,  n=shaderName )
        shader.color.set( axisColor )

    pm.select(geo)
    pm.hyperShade( assign = shader)

#
# joint chain
#
def jntChainToPoly( JntRoots, ch=False, smoothBind=True ):
    '''
    조인트 체인들에 메쉬를 붙여줌.
    C:/Program Files/Autodesk/MayaBonusTools2013/scripts/bt_makeJointsDynamicUI.mel 참고할것
    '''
    curveList = []
    for root in JntRoots:
        root  = pm.PyNode(root)
        chain = root.getChildren( allDescendents=True, type='joint' )
        chain.reverse()
        chain.insert(0,root)
        curveList.append( jntToCrv( chain, degree=1, ep=False) )

    loftedSurface, loft = pm.loft( curveList, ch=1, u=1, c=0, ar=1, d=1, ss=1, rn=0, po=1, rsn=True )
    nurbsTessellate = pm.PyNode( loft.outputSurface.outputs()[0] )

    nurbsTessellate.polygonType.set(1)   # 0.Triangle, 1.Quads
    nurbsTessellate.setAttr('format', 2) # 0.Count, 1.Fit, 2.General, 3.CVs
    nurbsTessellate.uType.set(3)         # 1.Per Surf # of Isofarms in 3D, 2.Per Surf # of Isofarms, 3.Per Span # of Isofarms
    nurbsTessellate.vType.set(3)         # 1.Per Surf # of Isofarms in 3D, 2.Per Surf # of Isofarms, 3.Per Span # of Isofarms
    nurbsTessellate.uNumber.set(1)
    nurbsTessellate.vNumber.set(1)

	#polyNormalizeUV -normalizeType 1 -preserveAspectRatio off ;
    if not ch:
        pm.delete( loftedSurface, ch=True )
        pm.delete( curveList )

    if smoothBind:
        pm.select( JntRoots, hi=True )
        JNTs = pm.selected( type='joint')
        pm.skinCluster( JNTs, loftedSurface,
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

        for jnt in JNTs:
            vtx = getClosestVertexOnMesh( loftedSurface, jnt.getTranslation( ws=True ) )
            setWeight( [vtx], jnt)

    return loftedSurface

def jntChainBlend( rootJnt1, rootJnt2, resultRootJnt, blendCtrlAttr=None ):
    pm.select( rootJnt1, hi=True )
    chain1 = pm.selected( type='joint' )

    pm.select( rootJnt2, hi=True )
    chain2 = pm.selected( type='joint' )

    pm.select( resultRootJnt, hi=True )
    results = pm.selected( type='joint' )

    BLENs = []
    for a,b,result in zip( chain1, chain2, results):
        #print a, b, result
        blen = pm.createNode( 'blendColors' )
        a.rotate >> blen.color1
        b.rotate >> blen.color2
        blen.output >> result.rotate
        BLENs.append(blen)

    # 블렌드 노드에 연결
    if blendCtrlAttr:
        for blend in BLENs:
            #blend.blender.set(0.5)
            blendCtrlAttr >> blend.blender
    else:
        endJnt = results[-1]
        rad = endJnt.radius.get()
        ctrl = ctrlCurveShape( shape='circle', r=(0,0,90), scale = rad*3 )
        ctrl.addAttr('blend', keyable=True, min=0, max=1, dv=0.5)
        ctrl.addAttr('mult', keyable=True, dv=1)

        pm.parentConstraint( results[-1], ctrl )
        blendCtrlAttr = ctrl.blend

    for blend in BLENs:
        #blend.blender.set(0.5)
        blendCtrlAttr >> blend.blender

    # 곱하기 노드 연결
    '''
    MULTs = []
    for a,b,result in zip( chain1, chain2, results):
        #print a, b, result
        mult = pm.createNode( 'multipyDivide' )
        a.rotate >> blen.color1
        b.rotate >> blen.color2
        blen.output >> result.rotate
        BLENs.append(blen)
    '''

#
# Search something in jointChain
#
def getStartJnt( joint ):
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
    '''
    for i in range(10000):
        paren = joint.getParent()
        if not paren or len( paren.getChildren(type='joint') ) > 1:
            # parent가 없거나, joint Type동기가 둘 이상이면 정지
            break
        joint = joint.getParent()
    return joint

def getEndJnt( joint ):
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
    '''
    for i in range(1000):
        childs = joint.getChildren( type='joint' )
        if not childs or len( childs ) > 1:
            # child가 없거나, 둘 이상이면 정지.
            break
        joint = joint.getChildren()[0]

    return joint

def getStartToEndJnt( *joints ):
    '''
    :Summary:
        args:                    ( joint1,                            joint2 )
                                    ↓                                 ↓
                     jnt1 > jnt2 > jnt3 > jnt4 > jnt5 > jnt6 > jnt7 > jnt8 > jnt9 > jnt10
                                    ↓     ↓     ↓     ↓     ↓     ↓
        return:                  [ jnt3,  jnt4,  jnt5,  jnt6,  jnt7,  jnt8 ]

    :Example:
        JNTs = pm.selected( type='joint' )
        pm.select( ut.getStartJnt( JNTs[0] ) )
        pm.select( ut.getEndJnt(   JNTs[0] ) )
        pm.select( ut.getStartToEndJnt( JNTs[0],JNTs[-1] ) )
        pm.select( ut.getStartToEndJnt( JNTs[0] ) )
        pm.select( ut.getMiddleJoints( JNTs[0], JNTs[-1] ) )

        getStartToEndJnt( pm.selected() )
        # Result: [nt.Joint(u'Hip'), nt.Joint(u'Knee'), nt.Joint(u'Ankle')]

    @
    @param joints: 하나의 줄기에 포함된 시작, 끝조인트
    @type joints: [ Joint, Joint, ... ]
    @return : 시작~~끝 조인트들
    @rtype : [ Joint, Joint, ... ]

    @version no: 0.3
    @todo Bug1: 갈라지는 조인트 처리
    @todo Bug2: 조인트를 여러개 선택했을때 어찌할지
    '''

    # 입력 조정 : 리스트들을 플랫하게 만듦
    joints = argsFlatten(joints)

    # 입력 분석
    joint1 = pm.PyNode( joints[0] )

    # joint2 입력이 없을경우 joint2는 체인 끝 조인트로 설정
    if len(joints)>1:
        joint2 = pm.PyNode( joints[-1] )
    else:
        joint2 = getEndJnt( joint1 )

    # 같은 조인트가 입력 될경우 에러 발생
    if joint1 == joint2:
        raise

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

    return JNTs

def getMiddleJoints( startJoint, endJoint ):
    '''
    JNTs = pm.selected( type='joint' )
    pm.select( ut.getStartJnt( JNTs[0] ) )
    pm.select( ut.getEndJnt(   JNTs[0] ) )
    pm.select( ut.getStartToEndJnt( JNTs[0],JNTs[-1] ) )
    pm.select( ut.getStartToEndJnt( JNTs[0] ) )
    pm.select( ut.getMiddleJoints( JNTs[0], JNTs[-1] ) )
    '''
    # 입력 분석
    startJoint = pm.PyNode( startJoint )
    endJoint   = pm.PyNode( endJoint )

    # startJoint가 endJoint의 parent가 아니면 에러
    if endJoint not in startJoint.getChildren( allDescendents=True ):
        raise ValueError( 'endJoint must chlid of startJoint' )

    jnt = []
    parentJoint = endJoint.getParent()
    while parentJoint!=startJoint:
        jnt.append( parentJoint )
        parentJoint = parentJoint.getParent()
    jnt.reverse()

    return jnt

#
# Rig create Stretch Spline
#
def createStretchSpline( ctrl=None, curve=None, maintainVolume=True, globalScaleAttr=None ):
    # PyNode 캐스팅
    if not curve:
        sel = pm.selected()
        if sel:
            curve = sel[0]
    else:
        curve = pm.PyNode( curve )

    # 컨트롤러 캐스팅
    node = curve
    if ctrl:
        node = pm.PyNode(ctrl)

    # ikhandle 알아옴.
    ikHandle = curve.getShape().worldSpace.outputs( type='ikHandle')
    if not ikHandle:
        pm.mel.error(u'select curve for splineIK')

    ikHandle = ikHandle[0]

    # 연결된 조인트 알아옴
    joints = ikHandle.getJointList()

    # ctrl node
    node.addAttr('globalScale',        keyable=True,  dv=1 )
    node.addAttr('stretch',            keyable=True,  dv=1 )
    node.addAttr('maintainVolumne',    keyable=False, dv=1 )

    node.addAttr('currentCurveLength', keyable=True )
    node.addAttr('initCurveLength',    keyable=True  )
    node.addAttr('aimAxisScale',       nn='Aim Axis Scale', keyable=True )

    node.addAttr('sideAxisScale',      keyable=False )
    node.addAttr('sideAxisScaleShape', keyable=False )

    node.setAttr('currentCurveLength', keyable=False, channelBox=True)
    node.setAttr('initCurveLength',    keyable=True,  channelBox=True)
    #node.setAttr('aimAxisScale',       keyable=False, channelBox=True)

    # curveInfo node 생성
    crvInfo = pm.arclen( curve, ch=True )
    crvInfo.setAttr('arcLength', keyable=True)
    initCurveLength = crvInfo.arcLength.get()
    crvInfo.arcLength >> node.currentCurveLength
    node.initCurveLength.set( initCurveLength )

    # we need to figure out which direction the curve should be scaling.
    # do to that, we'll look at the translate values of the second joint.  Whichever translate has the
    # highest value, that'll be the first one and the other two axis will be the shrinking one
    stretchAxis = getStretchAxisAttr( joints[-1] )

    #
    # 노드 계산
    #
    #
    # aimAxisScale = currentCurveLength / initCurveLength
    md1 = pm.createNode( 'multiplyDivide', n=curve.name()+'_initCurveLength' )
    md1.setAttr('operation', keyable=True)
    md1.operation.set(2) # Divide
    node.currentCurveLength >> md1.input1X
    node.initCurveLength    >> md1.input2X
    md1.outputX             >> node.aimAxisScale

    # aimAxisScale = ( currentCurveLength / initCurveLength ) / globalScale
    md2 = pm.createNode( 'multiplyDivide', n=curve.name()+'_multGlobalScale' )
    md2.setAttr('operation', keyable=True)
    md2.operation.set(2) # Divide
    md1.outputX      >> md2.input1X
    node.globalScale >> md2.input2X
    md2.outputX      >> node.aimAxisScale

    # node.stretch 로 stretch가 되고 안되게~
    # aimAxisScale = pow( [ (currentCurveLength / initCurveLength) / globalScale ], stretch )
    stretchable = pm.createNode( 'multiplyDivide', n=curve.name()+'_stretchable_switchPow' )
    stretchable.operation.set(3) # pow
    stretchable.setAttr('operation', keyable=True)
    md2.outputX         >> stretchable.input1X
    node.stretch        >> stretchable.input2X
    stretchable.outputX >> node.aimAxisScale

    for jnt in joints:
        attr = jnt.attr( stretchAxis[0] )
        print 'connecting to "%s"'%attr
        node.aimAxisScale >> attr

    if globalScaleAttr:
        pm.Attribute( globalScaleAttr ) >> node.globalScale

    # maintain Volume Option이 설정 되어 있으면~~
    if maintainVolume:
        node.setAttr('maintainVolumne',    keyable=True, channelBox=False)
        node.setAttr('sideAxisScale',      keyable=True, channelBox=False)
        node.setAttr('sideAxisScaleShape', keyable=True, channelBox=False)

        #
        # sideAxisScale = 1/sqrt( scale )
        #
        sqrtNode = pm.createNode( 'multiplyDivide', n=curve.name()+'_volumnPreserve_sqrt' )
        sqrtNode.operation.set(3) # pow(sqrt)
        sqrtNode.setAttr('operation', keyable=True)
        node.aimAxisScale >> sqrtNode.input1X
        sqrtNode.input2.set(0.5,0.5,0.5)
        # sqrtNode.outputX  >> --->

        divNode = pm.createNode( 'multiplyDivide', n=curve.name()+'_volumnPreserve_div' )
        divNode.operation.set(2) # division
        divNode.setAttr('operation', keyable=True)
        divNode.input1.set(1,1,1)
        sqrtNode.outputX >> divNode.input2X
        divNode.outputX >> node.sideAxisScale

        # node.maintainVolumne 로 볼륨 유지가 되고 안되게~
        maintainVolumneAble = pm.createNode( 'multiplyDivide', n=curve.name()+'_maintainVolumne_switchPow' )
        maintainVolumneAble.operation.set(3) # pow
        maintainVolumneAble.setAttr('operation', keyable=True)
        divNode.outputX      >> maintainVolumneAble.input1X
        node.maintainVolumne >> maintainVolumneAble.input2X
        maintainVolumneAble.outputX >> node.sideAxisScale

        powAttr = rigCurveShapeControl( ctrl=node, attr='sideAxisScaleShape', sampleParams=range( len(joints) ) )

        for i in range( len(joints) ):
            Jnt = joints[i]
            Pow = powAttr[i]

            # pow( 1/sqrt( Scale ), 2 )
            powNode = pm.createNode( 'multiplyDivide', n=curve.name()+'_volumnPreserve_pow' )
            powNode.operation.set(3) # pow
            powNode.setAttr('operation', keyable=True)

            node.sideAxisScale >> powNode.input1X
            Pow                >> powNode.input2X
            powNode.outputX    >> Jnt.attr( stretchAxis[1] )
            powNode.outputX    >> Jnt.attr( stretchAxis[2] )

def getStretchAxisAttr( joint=None ):
    if not joint:
        sel = pm.selected(type='joint')
        if sel:
            joint = sel[0]
        else:
            return

    joint = pm.PyNode(joint)
    tr = joint.t.get()

    for i in range(3):
        tr[i] = abs(tr[i])

    # 가장 큰 수 인덱스를 리턴함.
    idx = tr.index( tr.max() )[0]
    if idx == 0:
        return ['sx','sy','sz']

    if idx == 1:
        return ['sy','sx','sz']

    if idx == 2:
        return ['sz','sx','sy']

def rigCurveShapeControl( ctrl=None, attr=None, sampleParams=[0,1,2,3,4,5,6,7,8,9,10], container=False  ):
    '''
    스쿼시 스트레치시 그래프 에디터 커브로 쉐입을 조정하려고 만들어짐.

    powAttr = rigCurveShapeControl( ctrl='spinCtrl', attr='sideAxisScaleShape', sampleParams=range( len(joints) ) )

    @param ctrl:
    @param attr:
    @param sampleParams:
    @param container:
    @return: ctrl.results 어트리뷰트를 리턴함.
    @rtype: pm.Attribute
    '''
    if not ctrl:
        sel = pm.selected()
        if sel:
            ctrl = sel[0]
        else:
            return

    if not attr:
        attr = 'curveCtrl'
        ctrl.addAttr( attr, keyable=True )

    ctrl     = pm.PyNode(ctrl)
    ctrlAttr = pm.Attribute( ctrl.attr(attr) )

    # 애니메이션 커브 생성
    pm.setKeyframe( ctrlAttr, t=sampleParams[ 0], v=0)
    pm.setKeyframe( ctrlAttr, t=sampleParams[-1], v=0)
    pm. keyTangent( ctrlAttr, weightedTangents=True )
    pm. keyTangent( ctrlAttr, weightLock=False )
    pm. keyTangent( ctrlAttr, e=True, absolute=True, time=[sampleParams[ 0]], outAngle=77, outWeight=1 )
    pm. keyTangent( ctrlAttr, e=True, absolute=True, time=[sampleParams[-1]], inAngle=-77,  inWeight=1 )

    # frameCache노드로 애니메이션 커브의 각 포인트에서 값을 가져옴
    ctrl.addAttr( 'samples', multi=True, readable=True, indexMatters=False )
    ctrl.addAttr( 'results', multi=True, readable=True, indexMatters=False )

    frameCaches = []
    for i,param in enumerate(sampleParams):
        ctrl.samples[i].set( param )

        frameCache = pm.createNode( 'frameCache' )
        pm.connectAttr( ctrlAttr, frameCache.stream)
        pm.connectAttr( ctrl.samples[i], frameCache.varyTime )
        pm.connectAttr( frameCache.varying, ctrl.results, na=True)

        frameCaches.append(frameCache)

    # container Setting : wip
    if container:
        cont = pm.container( type='dagContainer', addNode=frameCaches )
        cont.blackBox.set(True)

    return ctrl.results

#
# for custom bindPose
#
def bindPose_addAttr( joint, **kwargs ):
    '''바인드 포즈용 어트리뷰트 추가'''
    joint = pm.PyNode(joint)

    if not joint.hasAttr('bp_t')   : joint.addAttr('bindPose_Translate',  sn='bp_t',  at='double3')
    if not joint.hasAttr('bp_tx')  : joint.addAttr('bindPose_TranslateX', sn='bp_tx', at='double', p='bindPose_Translate')
    if not joint.hasAttr('bp_ty')  : joint.addAttr('bindPose_TranslateY', sn='bp_ty', at='double', p='bindPose_Translate')
    if not joint.hasAttr('bp_tz')  : joint.addAttr('bindPose_TranslateZ', sn='bp_tz', at='double', p='bindPose_Translate')
    if not joint.hasAttr('bp_r')   : joint.addAttr('bindPose_Rotate',  sn='bp_r',  at='double3')
    if not joint.hasAttr('bp_rx')  : joint.addAttr('bindPose_RotateX', sn='bp_rx', at='double', p='bindPose_Rotate')
    if not joint.hasAttr('bp_ry')  : joint.addAttr('bindPose_RotateY', sn='bp_ry', at='double', p='bindPose_Rotate')
    if not joint.hasAttr('bp_rz')  : joint.addAttr('bindPose_RotateZ', sn='bp_rz', at='double', p='bindPose_Rotate')
    if not joint.hasAttr('bp_s')   : joint.addAttr('bindPose_Scale',  sn='bp_s',  at='double3')
    if not joint.hasAttr('bp_sx')  : joint.addAttr('bindPose_ScaleX', sn='bp_sx', at='double', p='bindPose_Scale')
    if not joint.hasAttr('bp_sy')  : joint.addAttr('bindPose_ScaleY', sn='bp_sy', at='double', p='bindPose_Scale')
    if not joint.hasAttr('bp_sz')  : joint.addAttr('bindPose_ScaleZ', sn='bp_sz', at='double', p='bindPose_Scale')
    if not joint.hasAttr('bp_ra')  : joint.addAttr('bindPose_rotateAxis',  sn='bp_ra',  at='double3')
    if not joint.hasAttr('bp_rax') : joint.addAttr('bindPose_rotateAxisX', sn='bp_rax', at='double', p='bindPose_rotateAxis')
    if not joint.hasAttr('bp_ray') : joint.addAttr('bindPose_rotateAxisY', sn='bp_ray', at='double', p='bindPose_rotateAxis')
    if not joint.hasAttr('bp_raz') : joint.addAttr('bindPose_rotateAxisZ', sn='bp_raz', at='double', p='bindPose_rotateAxis')
    if not joint.hasAttr('bp_jo')  : joint.addAttr('bindPose_jointOrient',  sn='bp_jo',  at='double3')
    if not joint.hasAttr('bp_jox') : joint.addAttr('bindPose_jointOrientX', sn='bp_jox', at='double', p='bindPose_jointOrient')
    if not joint.hasAttr('bp_joy') : joint.addAttr('bindPose_jointOrientY', sn='bp_joy', at='double', p='bindPose_jointOrient')
    if not joint.hasAttr('bp_joz') : joint.addAttr('bindPose_jointOrientZ', sn='bp_joz', at='double', p='bindPose_jointOrient')

    if kwargs:
        for attr in ['bp_tx','bp_ty','bp_tz','bp_rx','bp_ry','bp_rz','bp_sx','bp_sy','bp_sz','bp_rax','bp_ray','bp_raz','bp_jox','bp_joy','bp_joz']:
            joint.setAttr(attr, **kwargs)

def bindPose_get():
    '''바인드 포즈 상태로 조인트를 되돌림'''
    JNTs = pm.ls( type='joint' )
    for jnt in JNTs:
        if jnt.hasAttr('bp_t')  : jnt.t. set(  jnt.bp_t.get() )
        if jnt.hasAttr('bp_r')  : jnt.r. set(  jnt.bp_r.get() )
        if jnt.hasAttr('bp_s')  : jnt.s. set(  jnt.bp_s.get() )
        if jnt.hasAttr('bp_ra') : jnt.ra.set(  jnt.bp_ra.get() )
        if jnt.hasAttr('bp_jo') : jnt.jo.set(  jnt.bp_jo.get() )

def bindPose_set( joint=None ):
    '''조인트의 현재 상태를 저장'''
    JNTs = []
    if not joint:
        JNTs = pm.ls( type='joint' )
    else:
        JNTs = [pm.PyNode( joint )]

    for jnt in JNTs:
        if jnt.hasAttr('bp_t')  :
            for attr in ['bp_tx','bp_ty','bp_tz']: jnt.setAttr( attr, lock=False)
            jnt.bp_t. set(  jnt.t.get() )
            for attr in ['bp_tx','bp_ty','bp_tz']: jnt.setAttr( attr, lock=True)

        if jnt.hasAttr('bp_r')  :
            for attr in ['bp_rx','bp_ry','bp_rz']: jnt.setAttr( attr, lock=False)
            jnt.bp_r.set(  jnt.r.get() )
            for attr in ['bp_rx','bp_ry','bp_rz']: jnt.setAttr( attr, lock=True)

        if jnt.hasAttr('bp_s')  :
            for attr in ['bp_sx','bp_sy','bp_sz']: jnt.setAttr( attr, lock=False)
            jnt.bp_s.set(  jnt.s.get() )
            for attr in ['bp_sx','bp_sy','bp_sz']: jnt.setAttr( attr, lock=True)

        if jnt.hasAttr('bp_ra') :
            for attr in ['bp_rax','bp_ray','bp_raz']: jnt.setAttr( attr, lock=False)
            jnt.bp_ra.set(  jnt.ra.get() )
            for attr in ['bp_rax','bp_ray','bp_raz']: jnt.setAttr( attr, lock=True)

        if jnt.hasAttr('bp_jo') :
            for attr in ['bp_jox','bp_joy','bp_joz']: jnt.setAttr( attr, lock=False)
            jnt.bp_jo.set(  jnt.jo.get() )
            for attr in ['bp_jox','bp_joy','bp_joz']: jnt.setAttr( attr, lock=True)

def bindPose_getData():
    '''바인드 포즈 어트리 뷰트들 dict형식으로 돌려줌'''
    mem = {}
    JNTs = pm.ls( type='joint' )
    for jnt in JNTs:
        if not jnt.hasAttr('bp_t'): continue
        key = jnt.name()
        mem[key] = {}
        mem[key]['bp_t'] = jnt.bp_t.get()
        mem[key]['bp_r'] = jnt.bp_r.get()
        mem[key]['bp_s'] = jnt.bp_s.get()
        mem[key]['bp_ra'] = jnt.bp_ra.get()
        mem[key]['bp_jo'] = jnt.bp_jo.get()
    return mem

