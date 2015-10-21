# coding=utf-8
from maya import cmds
import pymel.core as pm
import math

__author__ = 'alfred'

'''
def aimConstraint(*args, **kwargs):
    if args:
        pm.select(args)
    objs = pm.ls(sl=True)

    if len(objs)>2:
        objs = objs[0:1]
        upObj = objs[2]

    return aimConstraint(objs,kwargs)
'''

def getDistance(*args):
    if args:
        pm.select(args)
    objs = pm.ls(sl=True, fl=True)

    dist = 0
    for i in range(len(objs)-1):
        dist += abs( objs[i].getTranslation( space='world' ) - objs[i+1].getTranslation( space='world' ) ).length()

    return dist

def vector_strToVec( inputVal ):
    '''
    Abstract
    ========
        1. 문자를 벡터형으로 리턴

        2. 예제 :
            >> getVectorByChar( 'x' )
            dt.Vector([1.0, 0.0, 0.0])

            >> getVectorByChar( 'y' )
            dt.Vector([1.0, 1.0, 0.0])

    @param inputVal: 'x','y','z','-x','-y','-z', or vector
    @type inputVal: str | tuple | pm.dt.Vector

    @return : 입력된 캐릭터에 대응하는 벡터
    @rtype : pm.dt.Vector

    @version No 0.7
    '''

    # 입력된 값이 문자열일경우
    if isinstance( inputVal, str ) or isinstance( inputVal, unicode ):

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

    else:
        return pm.datatypes.Vector( inputVal )

def rotOrder_strToInt( rotateOrderStr='zxy' ):
    if   rotateOrderStr=="xyz": return 0
    elif rotateOrderStr=="yzx": return 1
    elif rotateOrderStr=="zxy": return 2
    elif rotateOrderStr=="xzy": return 3
    elif rotateOrderStr=="yxz": return 4
    elif rotateOrderStr=="zyx": return 5

def getCenter( nodes, getPivot=True, getScalePivot=False ):
    '''
    선택된 컴포턴트나 트렌스폼노드들의 중심좌표를 리턴

    @param nodes: trnasform, or components 노드들
    @type nodes: list

    @param getPivot: (default True),  transform노드의 pivot을 기준으로 작동, 기본값을 True translate를 사용
    @type getPivot: bool

    @param getScalePivot: (default False), getPivot이 True일때 기본으로 rotatePivot을 사용하는데 scalePivot을 사용하고 싶을때 사용.
    @type getScalePivot: bool

    @return : 중심 좌표
    @rtype : pm.dt.Vector
    '''
    result = []
    if getPivot:
        for obj in nodes:
            if pm.nodeType(obj) == 'transform':
                xformResult = pm.xform( obj, q=True, ws=True, pivots=True)
                rtPiv, scPiv = xformResult[:3], xformResult[3:]

                if getScalePivot: res = scPiv
                else:             res = rtPiv

            else:
                res = pm.xform( obj, q=True, ws=True, t=True)

            result.extend( res )
    else:
        result = pm.xform( nodes, q=True, ws=True, t=True)

    # 입력된 자료의 평균값 알아냄
    points = []
    for i in range( len(result)/3 ):
        pnt = i*3
        x,y,z = result[pnt], result[pnt+1], result[pnt+2]
        points.append( pm.dt.Vector(x,y,z) )

    arr = pm.dt.Array(points)
    sum = pm.dt.Vector( arr.sum(0) )
    avr = sum / len(points)

    # 결과 리턴
    return avr

def toggleDisplayAxis( *objs, **kwargs ):
    if objs:
        pm.select(objs)
    objs = pm.ls( sl=True )

    if not objs: objs = pm.ls( exactType='joint' )
    if not objs: return

    vis = kwargs.get('vis', None)

    if isinstance( vis, bool ):
        condition = vis
    else:
        condition = objs[0].displayLocalAxis.get()
        condition = not condition

    for obj in objs:
        obj.displayLocalAxis.set(condition)

def toggleJointLabel( *objs, **kwargs ):
    if objs:
        pm.select(objs)
    objs = pm.ls( sl=True )
    if not objs: objs = pm.ls( exactType='joint' )
    if not objs: return

    vis = kwargs.get('vis', None)

    condition = None
    if isinstance( vis, bool ):
        condition = vis
    else:
        condition = objs[0].drawLabel.get()
        condition = not condition

    for obj in objs:
        obj.drawLabel.set(condition)

def setLabel( *nodes, **kwargs):
    '''
    :Sample:
        setLabel( 'locator1', label='Hello' )
        setLabel( pm.selected(), label='Hello' )
        setLabel( pm.selected() )                       # 오브젝트 이름으로 라벨링
        setLabel( pm.selected(), d=True )               #
        setLabel( 'locator1','locator2', l='Hello' )

    :Parameters:
        nodes  : node or nodes

        label  : string
        side   : left or right
        delete : bool

    :문제점:
        조인트에 적용하면 아웃리니어에서 joint아이콘이 anotation아이콘으로 변경됨.
        조인트에 적용했을때 어떻게 할지 결정 필요.

    :Version:
        2014-04-15 : v0.9

    :Author:
        Kyuho Choi
    '''
    #
    # 선택 리스트 저장
    #
    sel = pm.selected()

    #
    # flatten args : v20140415
    #
    objs = []
    for node in nodes:
        if   isinstance( node,(list,tuple,set)):
            objs.extend( [ obj for obj in node ] )
        elif isinstance( node,(str,unicode)):
            objs.append( node )
        else:
            objs.append( node ) # 파이썬 기본타입이 아닌, PyNode일 수도 있음.

    # pynode로 리캐스팅
    objs = [pm.PyNode(obj) for obj in objs]

    #
    # kwargs 처리
    #
    label  = kwargs.get('label',  kwargs.get('l',   None))
    side   = kwargs.get('side',   kwargs.get('s',   None))
    delete = kwargs.get('delete', kwargs.get('d', False))

    #
    # 판별 속성 : 이이름의 어트리뷰트가 있으면 이 스크립트로 만들어진 라벨임.
    #
    keyAttrName = 'customLabelObject'

    # 오브젝트에 라벨을 붙임.
    annotationShapes = []
    for obj in objs:
        #
        # transform 노드에만 적용 됨.
        #if pm.nodeType(obj) == 'transform':
        #    continue

        #
        # 이미 라벨이 존재할경우 일단 삭제.
        #
        for shapeNode in obj.getShapes():
            if shapeNode.hasAttr( keyAttrName ):
                # 왜 예외처리했는진 기억 안남.. ㅠㅠ 혹시몰라 놔둠.
                try:
                    pm.delete( shapeNode )
                except:
                    pass

        #
        # 삭제 모드일경우 여기서 중단.
        #
        if delete:
            continue

        #
        # 좌측 우측관련 입력이 있을경우... 라벨 조정
        #
        if side:
            side = side.replace(' ','').lower()
            if side=='left':
                label += ' (L)'
            elif side=='right':
                label += ' (R)'

        #
        # 라벨 생성
        #
        annotationShape = pm.createNode('annotationShape', n='label#', p=obj)
        annotationShape.text.set( label if label else obj.name() )
        annotationShape.displayArrow.set( False )

        # message type의 판별 속성 추가 : 중요~!
        annotationShape.addAttr(  keyAttrName, at='message' )

        # 오브젝트와 연결
        obj.message >> annotationShape.customLabelObject

        annotationShapes.append( annotationShape )

    #
    # 선택 복원
    #
    if sel:
        pm.select(sel)

    return annotationShapes

def setRotationOrder( *objs, **kwargs ):
    #
    # args
    #
    if objs:
        pm.select(objs)

    objs = pm.ls(sl=True,fl=True)

    if not objs:
        objs = pm.selected(type='transform')
    if not objs:
        return

    #
    # kwargs
    #
    rotationOrder = kwargs.get('rotationOrder',kwargs.get('ro','zxy') )

    # doIt
    for obj in objs:
        ro = rotOrder_strToInt( rotationOrder )
        obj.rotateOrder.set( ro )

def snap( *args, **kwargs ):
    #TODO : 뭐든 조금 고쳐야 함
    '''
    @TODO : 완전히 작동하게 해야함.
    @param args: 오브젝트 리스트
    @type args: L{PyNode|unicode}

    @keyword type: 'point' | 'orient' | 'parent' | 'scale' | 'aim' | 'trans' | 'compo'
    @keyword aimVector:     type='aim' 일때만 작동
    @keyword upVector:      type='aim' 일때만 작동
    @keyword worldUpVector: type='aim' 일때만 작동

    @return : None
    @rtype : None

    @see Func: locAtCenter
    @version No: 0.5
    @author Name: Kyuho Choi
    @todo 1: 버그 잡아야함.
    '''
    if args:
        pm.select(args)
    args = pm.ls(sl=True, flatten=True)

    if not args: 
        raise

    type = kwargs.pop('type', 'point')  # @ReservedAssignment
    #print type
    print args

    if type=='point':
        pm.delete( pm.pointConstraint( *args, **kwargs) )
        return

    elif type=='orient':
        pm.delete( pm.orientConstraint( *args, **kwargs) )
        return

    elif type=='parent':
        pm.delete( pm.parentConstraint( *args, **kwargs) )
        return

    elif type=='scale':
        pm.delete( pm.scaleConstraint( *args, **kwargs) )
        return

    elif type=='aim':
        kwargs['aimVector']     = vector_strToVec( kwargs.pop('aim') if 'aim' in kwargs.keys() else kwargs.get('aimVector',    'x') )
        kwargs['upVector']      = vector_strToVec( kwargs.pop('u')   if 'u'   in kwargs.keys() else kwargs.get('upVector',     'y') )
        kwargs['worldUpVector'] = vector_strToVec( kwargs.pop('wu')  if 'wu'  in kwargs.keys() else kwargs.get('worldUpVector','y') )

        if len(args)>2:
            #세개 이상선택 됐을때 세번째 선택된 오브젝트를 up오브젝트로 사용하도록 설정
            kwargs['worldUpType']   = 'object'
            kwargs['worldUpObject'] = args[2]

        pm.delete( pm.aimConstraint( args[0], args[1], **kwargs) )
        return

    elif type=='trans':
        point1 = pm.PyNode(args[0])
        point2 = pm.PyNode(args)

        pos = point1.getTranslation( space='world' )
        point2.setTranslation( pos, space='world')

    elif type=='compo':
        pos = getCenter( args[:-1] )
        point2 = pm.PyNode( args[-1] )
        point2.setTranslation(pos, space='world')

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

def copyPivot( *objs ):
    '''
    뒤에선택된 물체의 pivot을, 먼저선택된 물체의 pivot으로 맞춤
    @param objs: Transform Nodes
    @return: None
    @rtype: None
    '''
    tmp = []
    for obj in objs:
        if isinstance(obj,(list,tuple,set)):
            tmp.extend( list(obj) )
        else:
            tmp.append( obj )
    objs = tmp

    if not objs:
        objs = pm.selected(type='transform')

    if len(objs)<2 :
        pm.mel.error("Not enough objects selected.. exiting\n")

    if len(objs)>2 :
        pm.mel.warning("more than two objects selected.  Copying the pivot from the first object onto all the other objects..")

    objs = [ pm.PyNode(obj) for obj in objs ]

    # doIt
    pos = pm.xform( objs[0], q=True, ws=True, rp=True)
    objs[1].setPivots( pos, ws=True )

def locAtCenter( *args, **kwargs ):
    """
    @rtype : None
    """
    if args:
        pm.select(args)
    objs = cmds.ls(sl=True, flatten=True) # 파이멜은 컴포넌트처리가 잘 안됨, 입력값을 그대로 넘김
    if not objs: return

    # kwargs
    getPivot      = kwargs.get('getPivot',True)
    getScalePivot = kwargs.get('getScalePivot',False)

    avr = getCenter( objs, kwargs )

    # 해당 위치에 로케이터 위치시킴
    loc = pm.spaceLocator()
    loc.t.set( avr )

def locAtCenter(*args):
    if args:
        pm.select(args)
    sel = pm.ls(sl=True, fl=True)
    if not sel : return

    pm.select(sel)


    pm.mel.ConvertSelectionToVertices()
    clst = pm.cluster()
    loc = pm.spaceLocator()
    pm.pointConstraint(clst,loc)
    pm.delete(clst)
    return loc

def locAtPivot(*args):
    if args:
        pm.select(args)
    objs = cmds.ls(sl=True, flatten=True) # 파이멜은 컴포넌트처리가 잘 안됨, 입력값을 그대로 넘김
    if not objs: 
        return

    LOCs = []
    for obj in objs:
        loc = pm.spaceLocator()
        pm.delete( pm.parentConstraint( obj,loc ) )
        loc.rename('locAlign_'+obj)
        pm.select(cl=True)
        LOCs.append(loc)

    pm.select(LOCs)
    
    return LOCs

def createReverseTransform( prefix = '' ):   
    '''
    update : 2015-04-28
    '''
    origin  = pm.group(n='origin__parentMeToRivet_orientConstMeToLocalSpace',em=True)
    reverse = pm.group(n='reverse',em=True)
    anim    = pm.curve(n='anim__connectMeToCluster',d=3, p=[ (-0.5, 0.0, -0.0), (-0.5, 0.130602, -0.0), (-0.391806, 0.391806, -0.0), (-0.130602, 0.5, -0.0), (0.0, 0.5, -0.0), (0.0, 0.5, 0.130602), (0.0, 0.391806, 0.391806), (0.0, 0.130602, 0.5), (0.0, -0.0, 0.5), (0.130602, -0.0, 0.5), (0.391806, -0.0, 0.391806), (0.5, -0.0, 0.130602), (0.5, -0.0, 0.0), (0.5, 0.130602, -0.0), (0.391806, 0.391806, -0.0), (0.130602, 0.5, -0.0), (0.0, 0.5, -0.0), (0.0, 0.5, -0.130602), (0.0, 0.391806, -0.391806), (-0.0, 0.130602, -0.5), (-0.0, 0.0, -0.5), (0.130602, 0.0, -0.5), (0.391806, 0.0, -0.391806), (0.5, 0.0, -0.130602), (0.5, -0.0, 0.0), (0.5, -0.130602, 0.0), (0.391806, -0.391806, 0.0), (0.130602, -0.5, 0.0), (-0.0, -0.5, 0.0), (-0.130602, -0.5, 0.0), (-0.391806, -0.391806, 0.0), (-0.5, -0.130602, 0.0), (-0.5, 0.0, -0.0), (-0.5, 0.0, -0.130602), (-0.391806, 0.0, -0.391806), (-0.130602, 0.0, -0.5), (0.0, 0.0, -0.5), (-0.0, -0.130602, -0.5), (-0.0, -0.391806, -0.391806), (-0.0, -0.5, -0.130602), (-0.0, -0.5, -0.0), (-0.0, -0.5, 0.130602), (-0.0, -0.391806, 0.391806), (0.0, -0.130602, 0.5), (0.0, -0.0, 0.5), (-0.130602, -0.0, 0.5), (-0.391806, -0.0, 0.391806), (-0.5, -0.0, 0.130602), (-0.5, 0.0, -0.0) ], k=[ 8.0, 8.0, 8.0, 9.0, 10.0, 10.0, 10.0, 11.0, 12.0, 12.0, 12.0, 13.0, 14.0, 14.0, 14.0, 15.0, 16.0, 16.0, 16.0, 17.0, 18.0, 18.0, 18.0, 19.0, 20.0, 20.0, 20.0, 21.0, 22.0, 22.0, 22.0, 23.0, 24.0, 24.0, 24.0, 25.0, 26.0, 26.0, 26.0, 27.0, 28.0, 28.0, 28.0, 29.0, 30.0, 30.0, 30.0, 31.0, 32.0, 32.0, 32.0 ] )
    pm.parent(anim,reverse)
    pm.parent(reverse,origin)
    md = pm.createNode('multiplyDivide',n='reverse_md')
    md.input2.set(-1,-1,-1)
    anim.t >> md.input1
    md.output >> reverse.t
    
    if prefix:
        for node in [origin, reverse, anim, md]:
            node.rename( node.split('__')[0])
            node.rename( '%s_%s'%(prefix,node) )
            
    return [origin,reverse,anim]

def setPin( nodes=[],  value=None ):
    nodes = [pm.PyNode(node) for node in nodes]

    if not nodes:
        nodes = pm.selected()
    if not nodes:
        return

    if not value:
        value = nodes[0].it.get()
        value = not value

    for node in nodes:
        mtx = node.getMatrix( worldSpace=True )
        node.it.set( value )
        node.setMatrix( mtx, worldSpace=True )

def isParallel( startObj, middle, endObj ):
    '''
    다리조인트나 팔조인트가 일자로 세팅 됐는지 확인용으로 제작됨.
    파이멜의 dt.Vector.isParallel(a,b)를 사용.
    입력된 세개의 포인트(?)가 일자로 배열되었는지 확인

    isParallel( 'Hips', 'UpperLeg', 'Leg' )

    일자로 배열된 조인트이면 : True
    그렇지 않으면            : False
    '''
    startObj = pm.PyNode( startObj )
    middle   = pm.PyNode( middle )
    endObj   = pm.PyNode( endObj )

    # 일자형 조인트인지 확인
    o = startObj.getTranslation( space='world' )
    a = middle.  getTranslation( space='world' ) - o
    b = endObj.  getTranslation( space='world' ) - o

    # a, b 벡터가 수평인지 확인
    parallel = pm.dt.Vector.isParallel(a,b)

    return parallel

def getPoleVecLoc( startJoint, midJoint, endJoint, aimVec='x', upVec='y', name=None, offset=None, locator=True ):
    '''
    getPoleVecLoc( 'Hips', 'UpperLeg', 'Leg' )

    조인트의 구부러진 방향에 PoleVec 로케이터 생성

    @todo : 우선순위 다시 생각해볼것.
    방향 판단 우선순위:
        1. 구부러진 방향
        2. 조인트가 일자형일경우 입력된 upVec방향.
        3.

    @type startJoint: Joint
    @type midJoint: Joint
    @type endJoint: Joint
    @type aimVec: str('x','y','z','-x','-y','-z') | Vector
    @type upVec: str('x','y','z','-x','-y','-z') | Vector
    @type offset: float
    @rtype : Locator
    '''
    startJoint = pm.PyNode( startJoint )
    endJoint   = pm.PyNode( endJoint )
    midJoint   = pm.PyNode( midJoint )

    aimVec = vector_strToVec( aimVec )
    upVec  = vector_strToVec( upVec )
    offset = offset

    if locator:
        LOC = pm.spaceLocator()
    else:
        LOC = pm.group(em=True)

    # 이름 조정
    if name:
        LOC.rename( name )
    else:
        LOC.rename('LOC_polVec#')


    # offset이 지정되지 않으면
    # end_JNT 와 start_JNT 사이 길이의 0.7배 위치를 기본 offset 값으로 정함.
    if not offset:
        offset = ( endJoint.getTranslation( space='world' ) - startJoint.getTranslation( space='world' ) ).length()* 0.7

    # 수평 조인트일경우 : 중간조인트의 up축 offset위치에 로케이터를 위치 시킴
    if isParallel( startJoint, midJoint, endJoint ):
        LOC.setMatrix( midJoint.getMatrix( ws=True ), ws=True )
        LOC.translateBy( upVec * offset, space='preTransform' )

    # 수평 조인트가 이닐경우
    else:
        startLen = ( midJoint.getTranslation( space='world' ) - startJoint.getTranslation( space='world' ) ).length()
        endLen   = ( midJoint.getTranslation( space='world' ) - endJoint.  getTranslation( space='world' ) ).length()

        # 위치 조정 :
        # startJoint, endJoint 사이, 길이 비율 위치에 LOC을 위치 시킨 다음.
        pConst = pm.pointConstraint( startJoint, endJoint, LOC )
        pm.pointConstraint( startJoint, LOC, w= endLen   )
        pm.pointConstraint( endJoint,   LOC, w= startLen )
        pm.delete( pConst )

        # 로테이션 조정 1:
        # 로케이터의 aim축이 endJoint를 바라보고
        # 로케니터의 up축이 mid Jooint를 바라봄.
        pm.delete( pm.aimConstraint(
            endJoint, LOC,
            worldUpObject = midJoint,
            aimVector     = aimVec,
            upVector      = upVec,
            worldUpType   ='object'
            ))
        # 로케이터의 up 축이 midJ oint를 바라보고
        # 로케니터의 aim축이 end Joint를 바라봄.
        pm.delete( pm.aimConstraint( midJoint, LOC,
            worldUpObject = endJoint,
            aimVector     = upVec,
            upVector      = aimVec,
            worldUpType   ='object'   ))

        # 위치 조정 2:
        # midJoint 위치에 LOC을 위치 시킨 다음.
        pm.delete( pm.pointConstraint( midJoint, LOC ))

        # offset값 만큼 떨어뜨림.
        LOC.translateBy( upVec * offset, space='preTransform' )

    return LOC

def getAimUpAxis( originObj, aimObj, upObj):
    '''originObj기준의 aim축과 up축을 리턴함.
    자동으로 aimVector와 upVector를 파악
    '''

    originObj = pm.PyNode(originObj)
    aimObj    = pm.PyNode(aimObj)
    upObj     = pm.PyNode(upObj)

    o = pm.spaceLocator()
    a = pm.spaceLocator()
    u = pm.spaceLocator()
    snap( originObj, o, type='parent' )
    snap( aimObj,    a, type='parent' )
    snap( upObj,     u, type='parent' )

    # getAimVec
    pm.parent( a, o)
    aim_translate = a.t.get()                                       # child의 위치값으로 확인 하려고 함.
    pm.parent( a, w=True )

    aim_abs = pm.dt.Vector( [abs(item) for item in aim_translate] ) # 절대값으로 조정
    aim_id = aim_abs.index( aim_abs.max() )[0]                      # 절대값중 값이 큰 id
    aim_sign = -1.0 if aim_translate[aim_id]<0 else 1               # 음수인지 양수인지 확인
    aimVector = pm.dt.Vector(0,0,0)
    aimVector[ aim_id ] = aim_sign

    # 오리진 축 조정
    tmpUpVec = pm.dt.Vector(0,1,0) if not aimVector==pm.dt.Vector(0,1,0) else pm.dt.Vector(0,1,0) # 이부분 다시 생각해볼것
    tmpWoldUpObj = pm.spaceLocator()
    snap( o, tmpWoldUpObj, type='parent' )
    tmpWoldUpObj.translateBy( tmpUpVec , space='preTransform' )
    pm.delete( pm.aimConstraint( a, o, aim=aimVector, u=tmpUpVec, wuo=tmpWoldUpObj, wut='object'  ) )

    # getUpVec
    pm.parent( u, o)
    up_translate = u.t.get()
    pm.parent( u, w=True )
    up_translate[aim_id] = 0.0                                    # aim축 값은 무시, 겹치는 방향은 무용지물.

    up_abs = pm.dt.Vector( [abs(item) for item in up_translate] ) # 절대값으로 조정
    up_id = up_abs.index( up_abs.max() )[0]                       # 절대값중 값이 큰 id
    up_sign = -1.0 if up_translate[up_id]<0 else 1                # 음수인지 양수인지 확인
    upVector = pm.dt.Vector( 0,0,0 )
    upVector[ up_id ] = up_sign

    # 클린업
    pm.delete( o,a,u,tmpWoldUpObj )

    return aimVector, upVector

def getDistance( obj1, obj2):
    '''
    두 오브젝트 사이의 거리를 리턴

    @param obj1: start transformNode
    @type obj1: PyNode or unicode
    @param obj2: end transformNode
    @type obj2: PyNode or unicode

    @return 두 오브젝트 사이의 거리값
    @rtype : float

    '''
    obj1 = pm.PyNode(obj1)
    obj2 = pm.PyNode(obj2)
    return ( obj1.getTranslation( space='world' ) - obj2.getTranslation( space='world' ) ).length()

def setPivotTobottom():
    for node in pm.selected(type='transform'):
        pm.select( node )
        pm.mel.CenterPivot()
        sizeY = node.boundingBoxSizeY.get()
        pm.move( 0, sizeY*-0.5, 0, node.scalePivot, node.rotatePivot, r=True )

def centerScale( val ):
    '''
    컴포넌트나.. 선택된 오브젝트그룹의 중심을 기준으로 스케일링
    @param val:
    @return:
    '''
    val = pm.dt.Vector( val )
    bbox = pm.xform( q=True, ws=True, boundingBox=True)
    min = pm.dt.Vector( bbox[:3] )
    max = pm.dt.Vector( bbox[3:] )
    cent = min + (max - min) * 0.5
    pm.scale( val, p=cent, relative=True )


'''
def mirrorObject(*objs):
    objs = argsFlatten(objs)
    if not objs : objs = pm.selected()
    if not objs : return

    dups = []
    for obj in objs:
        dup = pm.duplicate( obj, rr=True)[0]
        setAttrs( dup, 'tx','ty','tz','rx','ry','rz','sx','sy','sz', keyable=True, lock=False,channelBox=False)

        grp = pm.group( dup )
        pm.xform( os=True, piv=(0,0,0))
        grp.sx.set(-1)
        pm.parent(dup, w=True)
        pm.makeIdentity( dup, apply=True, t=1,r=1,s=1,n=0)
        pm.delete(grp)

        dups.append(dup)
    return dups

def matchRotateOrder(*objs):
    objs = argsFlatten(objs)
    if not objs : objs = pm.selected()
    if not objs : return

    rotateOrder = pm.xform( objs[-1], q=True, rotateOrder=True )
    pm.xform( objs[:-1], roo=rotateOrder )

'''
