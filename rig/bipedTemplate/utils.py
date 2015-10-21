# coding=utf-8
'''
템플릿 리깅 스크립트
'''
import pymel.core as pm

#=============================================================================
#
#
#
#=============================================================================
def setColor( *args, **kwargs ):
    COLORINDEX = {
    'none'       : 0,  'black'      : 1,  'darkgray'   : 2,  'gray'       : 3,  'darkred'    : 4,
    'darkblue'   : 5,  'blue'       : 6,  'darkgreen'  : 7,  'darkpurple' : 8,  'purple'     : 9,
    'lightbrown' : 10, 'darkbrown'  : 11, 'brown'      : 12, 'red'        : 13, 'green'      : 14,
    'white'      : 16, 'yellow'     : 17, 'yellowgray' : 22, 'brownlight' : 24, 'greengray'  : 26,
    'bluegray'   : 29, 'redgray'    : 31,

    'root'       : 12,
    'left'       : 19, 'right'      : 20, 'center'     : 22,
    'up'         : 18, 'aim'        : 21,

    'fk'         : 18,
    'ik'         : 22,
    ''           : 0
    }

    def color_intToStr( colorIndex ):
        '''입력된 값의 컬러이름을 리턴.'''
        result = []
        tmp = []
        for k,v in COLORINDEX.iteritems():
            tmp.append( [v, k] )
        tmp.sort()

        for k,v in tmp:
            if k==colorIndex:
                result.append( v )

        if not result:
            result = ['untitled']

        return ', '.join(result)

    def color_strToInt( colorName ):
        '''입력된 컬러이름의 index를 리턴.'''
        colorIndex = None

        # 스트링 형으로 인풋이 들어오면.
        if isinstance( colorName, (str,unicode) ):
            colorIndex = COLORINDEX[ colorName.replace(' ','').lower() ]

        # 정수형으로 인풋이 들어오면
        elif isinstance( colorName, (int,float)):
            colorIndex = int(colorName)

        return colorIndex

    if args:
        pm.select(args)
    objs = pm.ls( sl=True )
    if not objs: return

    # 파이노드로 리캐스팅
    objs = [pm.PyNode(obj) for obj in objs]

    color = kwargs.get('color', kwargs.get('col', kwargs.get('c', 0)))

    for obj in objs:
        obj.overrideColor.set( color_strToInt(color) )

        if color==0: obj.overrideEnabled.set( False )
        else:        obj.overrideEnabled.set( True )

def strToVec( inputVal ):
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

    @version : 2015-02-26
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

def setAttrs( nodes, *attrs, **kwargs):
    '''
    어트리뷰트 일괄 세팅

    Sample:
      - sample1:

        setAttrs( node,  'tx','ty','tz', 'rx','ry','rz', 'sx','sy','sz', 'v', keyable=False, lock=True, channelBox=False)
        setAttrs( node, 'rx','ry','rz', 'sx','sy','sz', 'v', keyable=False, lock=True, channelBox=False)

        for attr in ['rx','ry','rz','sx','sy','sz','v']:
            pm.setAttr( '%s.%s'%(node,attr), lock=True, keyable=False, channelBox=False )

    Parameters:
      - nodes : list[PyNode|node]

      - attrs : cmds.setAttr attributes

      - kwargs : cmds.setAttr flags
    '''
    objs = []
    if isinstance( nodes, (list, tuple, set)):
        objs = [ pm.PyNode( obj )  for obj in nodes ]
    else:
        objs = [ pm.PyNode( nodes ) ]

    for obj in objs:
        for attr in attrs:
            obj.setAttr(attr, **kwargs)

def snap( *args, **kwargs ):
    #TODO : 뭐든 조금 고쳐야 함
    '''
    @TODO : 완전히 작동하게 해야함.
    @param args: 오브젝트 리스트
    @type args: L{PyNode|unicode}

    @keyword type: 'point' | 'orient' | 'parent' | 'scale' | 'aim' | 'trans'
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
        return

    # 컨스트레인 명령어에 포함되면 안되는 플래그들 삭제.
    type = kwargs.pop('type', 'point')

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
        kwargs['aimVector']     = strToVec( kwargs.pop('aim') if 'aim' in kwargs.keys() else kwargs.get('aimVector',    'x') )
        kwargs['upVector']      = strToVec( kwargs.pop('u')   if 'u'   in kwargs.keys() else kwargs.get('upVector',     'y') )
        kwargs['worldUpVector'] = strToVec( kwargs.pop('wu')  if 'wu'  in kwargs.keys() else kwargs.get('worldUpVector','y') )

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

def getDistance(*args):
    if args:
        pm.select(args)
    objs = pm.ls(sl=True, fl=True)

    dist = 0
    for i in range(len(objs)-1):
        dist += abs( objs[i].getTranslation( space='world' ) - objs[i+1].getTranslation( space='world' ) ).length()

    return dist

class CurveConnect(object):
    def __init__(self, name='', startObj=None, endObj=None):
        '''
        connecting curve at obj

        Version: 2015-02-23

        Example:
        ================================
        link = CurveConnect()
        loc1 = pm.spaceLocator()
        loc2 = pm.spaceLocator()
        pm.select(loc1,loc2)
        sel = pm.selected()
        link.startObj = sel[0]
        link.endObj = sel[1]
        link.create()
        link.curve
        link.locator
        link.delete()
        link.create()
        '''
        self.name = name
        self.startObj = startObj
        self.endObj = endObj

    def __call__(self, *args, **kwargs):
        sel = []
        if args:
            sel = pm.select(args)
        if not sel:
            sel = pm.selected()
        if not sel:
            raise

        self.startObj = sel[0]
        self.endObj = sel[1]

        self.create()
        return self.locator

    def create(self):
        pointA = self.startObj
        pointB = self.endObj
        position = (0,0,0)

        # 커브 생성
        crv = pm.curve( d=1, p=[ position, position ], k=[0,1] )
        self.curve = crv.getShape()

        # obj에 커브 쉐입을 종속 시킴 : 커브를 선택해도 오브젝트를 선택한 효과를 줌.
        pm.parent( self.curve, pointA, r=True, s=True)
        pm.delete( crv )

        # target에 locator를 종속 시킴
        self.locator = pm.pointCurveConstraint( self.curve+'.ep[1]', ch=True)[0]
        self.locator = pm.PyNode(self.locator)
        pm.pointConstraint( pointB, self.locator )

        # 로케이서 속성 조정
        self.locator.getShape().localPosition.set(0,0,0) #이 로케이터는 보이지 않음
        self.locator.getShape().v.set(False)             #이 로케이터는 보이지 않음
        self.locator.v.set(False)                        #이 로케이터는 보이지 않음
        self.locator.setParent(pointA)
        self.locator.rename( pointB+'_CONNLOC' )

        # 커브쉐입에 어트리뷰트 추가
        self.curve.addAttr( 'curveConnectedTo',  at='message' )
        self.curve.addAttr( 'curveConnectedLOC', at='message' )

        # 어트리뷰트 연결
        pointB.message >> self.curve.curveConnectedTo
        self.locator.message >> self.curve.curveConnectedLOC

    def delete(self):
        pm.delete( self.curve, self.locator)
        '''
        for crvShp in obj.getShapes():
            if crvShp.hasAttr('curveConnectedLOC'):
                try:
                    pm.delete( crvShp, crvShp.curveConnectedLOC.inputs() )
                except:
                    pass
        '''
curveConnect = CurveConnect()

#=============================================================================
#
#
#
#=============================================================================

class NodeGroup(object):
    pass

class Template(object):
    rootNode = None
    rootName = 'bipedTemplate_grp'
    groupNode = None
    typeAttrName = 'bipedTemplateType'

    def createGroup(self, groupName):
        '''그룹 생성'''
        assert isinstance(groupName, basestring)
        self.groupName = groupName

        # 씬에서 그룹노드를 찾아보고
        self.groupNode = self.findNode( self.groupName, self.typeAttrName)

        # 존재하면 삭제.
        if self.groupNode:
            pm.delete(self.groupNode)

        # 없으면 생성
        self.groupNode = pm.group(n=groupName, em=True)

        # 노드 등록 : 식별용 어트리뷰트 추가
        self.groupNode.addAttr( self.typeAttrName, dt='string')
        self.groupNode.setAttr( self.typeAttrName, 'bodyPartGroup')

        # 루트에 페어런트
        self.createRoot()
        pm.parent( self.groupNode, self.rootNode )

        return self.groupNode
    
    def deleteGroup(self):
        '''그룹 삭제'''
        # 씬에서 그룹노드를 찾아보고
        self.groupNode = self.findNode( self.groupName, self.typeAttrName)

        # 존재하면 삭제.
        if self.groupNode:
            pm.delete(self.groupNode)

    def createRoot(self):
        '''루트 생성'''
        # 씬에서 루트노드를 찾아보고
        self.rootNode = self.findNode( self.rootName, self.typeAttrName)

        # 루트노드가 있으면 나가버림.
        if self.rootNode:
            return

        # 없으면 생성
        self.rootNode = pm.group(n=self.rootName, em=True)

        # 노드 등록 : 식별용 어트리뷰트 추가
        self.rootNode.addAttr( self.typeAttrName, dt='string')
        self.rootNode.setAttr( self.typeAttrName, 'Root')

    def findNode(self, name, attr):
        '''템플릿용 해당 노드 찾아 리턴'''
        # 씬에서 찾음
        sel = pm.ls( name )

        # 같은 이름의 노드중 식별어트리뷰트가 있는 노드 찾음.
        for node in sel:
            if node.hasAttr( attr ):
                return node

    def delayProcess(self):
        for i in range(100):
            pm.refresh()


class Handle(object):
    def __init__(self, prefix='', aimVector=(1,0,0), upVector=(0,1,0), curveConnect=True):
        self.prefix = prefix
        self.aimVec    = pm.dt.Vector(aimVector)
        self.upVec     = pm.dt.Vector(upVector)
        self.create()

    def create(self):
        self.handle   = pm.group(em=True)
        self.result   = pm.group(em=True)
        self.aim      = pm.group(em=True)
        self.up       = pm.group(em=True)
        
        pm.parent(self.result, self.aim, self.up, self.handle )
        
        # 초기위치 조정
        mult = 20
        self.aim.t.set(self.aimVec * mult)
        self.up.t.set(self.upVec * mult)
        
        self.aimConstraint = pm.aimConstraint(self.aim, self.result, aim=self.aimVec, u=self.upVec, wut='object', wuo=self.up)
        
        # 시각화
        self.handle.displayHandle.set(True)
        #self.result.displayLocalAxis.set(True)
        
        # 어트리뷰트 잠금
        setAttrs( self.result, 'tx','ty','tz','sx','sy','sz','v' )
        setAttrs( self.aim,    'rx','ry','rz','sx','sy','sz','v' )
        setAttrs( self.up,     'rx','ry','rz','sx','sy','sz','v' )

        # 이름변경
        self.setPrefix( self.prefix )
        
    def snapTo(self, xform, type='parent'):
        snap(xform, self.handle, type=type)

    def setPrefix( self, prefix ):
        self.prefix = prefix

        if self.prefix and self.prefix[-1] is not '_':
            self.prefix += '_'

        self.handle.rename( self.prefix + 'handle' )
        self.result.rename( self.prefix + 'result' )
        self.aim.   rename( self.prefix + 'aim' )
        self.up.    rename( self.prefix + 'up' )

class Limb(Template):
    def __init__(self, startJnt, middleJnt, endJnt, prefix='', aimVec='x', startUpVec='y', startWorldUpVec='y', middleUpVec='y', middleWorldUpVec='y', endUpVec='y', endWorldUpVec='y', parentSlot=None, childrenSlot=None):
        '''
        startJnt,           basestring, pm.PyNode
        middleJnt,          basestring, pm.PyNode
        endJnt,             basestring, pm.PyNode
        prefix,             basestring
        aimVec,             ['x','y','z','-x','-y','-z'], pm.dt.Vector
        startUpVec,         ['x','y','z','-x','-y','-z'], pm.dt.Vector
        startWorldUpVec,    ['x','y','z','-x','-y','-z'], pm.dt.Vector
        middleUpVec,        ['x','y','z','-x','-y','-z'], pm.dt.Vector
        middleWorldUpVec,   ['x','y','z','-x','-y','-z'], pm.dt.Vector
        endUpVec,           ['x','y','z','-x','-y','-z'], pm.dt.Vector
        endWorldUpVec,      ['x','y','z','-x','-y','-z'], pm.dt.Vector
        '''

        self.startJnt  = pm.PyNode(startJnt)
        self.middleJnt = pm.PyNode(middleJnt)
        self.endJnt    = pm.PyNode(endJnt)
        self.prefix    = prefix

        self.aimVec           = strToVec( aimVec )
        self.startUpVec       = strToVec( startUpVec )
        self.startWorldUpVec  = strToVec( startWorldUpVec )
        self.middleUpVec      = strToVec( middleUpVec )
        self.middleWorldUpVec = strToVec( middleWorldUpVec )
        self.endUpVec         = strToVec( endUpVec )
        self.endWorldUpVec    = strToVec( endWorldUpVec )

        self.groupName = prefix+'_grp'
        self.parentSlot = parentSlot
        self.childSlot = childrenSlot

    def create(self):
        grp = self.createGroup( self.groupName )
        snap( self.startJnt, grp, type='point' )

        root    = Handle()
        start   = Handle()
        middle  = Handle()
        end     = Handle()
        poleVec = NodeGroup()
        poleVec.grp    = pm.group( em=True )
        poleVec.handle = pm.group( em=True )        

        # 핸들리깅
        pm.parent( middle.handle, poleVec.grp )
        pm.parent( start.handle, poleVec.grp, root.result )        
        #pm.parent( poleVec.handle, root.result )
        
        pm.parent( root.handle, end.handle, poleVec.handle, grp)

        # 위치조정
        root.snapTo(self.startJnt, 'parent')
        end.snapTo(self.endJnt)

        # 리깅
        pm.pointConstraint(end.result,    root.aim)    
        pm.pointConstraint(end.result,    middle.aim) 
        pm.pointConstraint(middle.result, start.aim)        
        
        pm.delete( pm.parentConstraint( root.result, end.result, poleVec.handle ) )
        pm.delete( pm.aimConstraint( end.result, poleVec.handle, aim=self.aimVec, u=self.middleUpVec, wu=self.middleUpVec, wut='objectrotation', wuo=self.middleJnt) )
        pm.delete( pm.pointConstraint( self.middleJnt, poleVec.handle ) ) 
        
        mag = 20
        polevec_pos = self.middleWorldUpVec * mag
        pm.move( poleVec.handle, polevec_pos.x, polevec_pos.y, polevec_pos.z, r=True, os=True, wd=True )

        pm.pointConstraint( end.result, start.result, poleVec.grp)
        pm.aimConstraint( end.result, poleVec.grp, aim=self.aimVec, u=self.middleUpVec, wut='object', wuo=poleVec.handle)
        pm.delete( pm.pointConstraint( self.middleJnt, middle.handle ) )
        
        pm.pointConstraint( root.up, start.up)
        
        # 시각화 조정        
        start. result.displayLocalAxis.set(True)
        middle.result.displayLocalAxis.set(True)
        end.   result.displayLocalAxis.set(True)

        start.handle.displayHandle.set(False)

        # 컬러조정
        setColor( root.up, end.up, poleVec.handle, c='greengray')
        setColor( end.aim, c='darkred')
        setColor( root.handle, middle.handle, end.handle, c='red')
        
        # 어트리뷰트 조정
        setAttrs( middle.handle,  'rx','ry','rz','sx','sy','sz','v', lock=True, keyable=False, channelBox=False )
        setAttrs( poleVec.handle, 'rx','ry','rz','sx','sy','sz','v', lock=True, keyable=False, channelBox=False )
            
        pm.parent( pm.parentConstraint(start.result,  self.startJnt),    start.handle )
        pm.parent( pm.parentConstraint(middle.result, self.middleJnt),   middle.handle )
        pm.parent( pm.parentConstraint(end.result,    self.endJnt),      end.handle )

        # 선연결
        curveConnect( root.up, start.result, )
        curveConnect( poleVec.handle, middle.result, )
        curveConnect( end.up,  end.result, )
        curveConnect( end.aim, end.result, )

        self.grp = grp
        self.root = root
        self.end = end

        self.setPrefix()

    def setPrefix(self, prefix=None):
        #grp     = pm.group( em=True )
        #root    = Handle()
        #start   = Handle()
        #middle  = Handle()
        #end     = Handle()
        #poleVec = NodeGroup()
        #poleVec.grp    = pm.group( em=True )
        #poleVec.handle = pm.group( em=True )
        if prefix:
            self.prefix = prefix

        if self.prefix:
            print self.prefix
            if not self.prefix[-1]=='_':
                self.prefix += '_'
            
        self.grp.rename( self.prefix +'grp' )

class Finger(Template):
    fingerGroupName = 'Finger_grp'

    def __init__(self, joints=[], prefix='', aimVec='x', upVec='y', worldUpVec='y'):
        self.joints = joints
        self.prefix = prefix
        self.aimVec = strToVec(aimVec)
        self.upVec = strToVec(upVec)
        self.worldUpVec = strToVec(worldUpVec)

        self.groupName = prefix+'_grp'
        self.parentSlot = 'Finger_grp'
        self.childSlot = None

    def createFingerGrp(self):
        '''루트 생성'''
        # 씬에서 루트노드를 찾아보고
        self.fingerGrp = self.findNode( self.fingerGroupName, self.typeAttrName)

        # 루트노드가 있으면 나가버림.
        if self.fingerGrp:
            return

        # 없으면 생성
        self.fingerGrp = pm.group(n=self.fingerGroupName, em=True)

        # 노드 등록 : 식별용 어트리뷰트 추가
        self.fingerGrp.addAttr( self.typeAttrName, dt='string')
        self.fingerGrp.setAttr( self.typeAttrName, 'Finger_grp')

        # 루트에 페어런트
        self.createRoot()
        pm.parent( self.fingerGrp, self.rootNode )

        # 컨스트레인 연결
        if pm.objExists('LeftHand'):
            snap('LeftHand', self.fingerGrp)
            pm.parentConstraint('LeftHand', self.fingerGrp)

        return

        #
        # 엄지 세팅 (임시)
        #
        hdls = []
        for jnt in ['LeftFingerBase', 'LeftHandThumb1',     'LeftInHandThumb', 'LeftInHandIndex', 'LeftInHandMiddle', 'LeftInHandRing', 'LeftInHandPinky']:
            jnt = pm.PyNode(jnt)
            hdl = pm.group(n=jnt+'_hdl',em=True)
            snap( jnt, hdl, type='parent')
            pm.parent( pm.parentConstraint( hdl, jnt ), hdl)
            setAttrs( hdl, 'rx','ry','rz','sx','sy','sz','v', lock=True, keyable=False, channelBox=False )
            pm.parent( hdl, self.fingerGrp)
            hdls.append(hdl)
        hdls[0].displayHandle.set(True)
        hdls[1].displayHandle.set(True)        
        setColor( hdls[0], hdls[1], c='red' )

        return self.fingerGrp

    def create(self):
        # 그룹 세팅
        grp = self.createGroup( self.groupName )
        snap( self.joints[0],  grp, type='parent' )

        # 핑거그룹 세팅
        self.createFingerGrp()
        pm.parent( grp, self.fingerGrp)

        # 로테이션 루트 세팅
        root = Handle()
        snap( self.joints[0],  root.handle, type='point' )
        snap( self.joints[-1], root.handle, type='aim', aim=self.aimVec, u=self.upVec, wu=self.worldUpVec, wut='objectrotation', wuo=self.joints[0] )
        
        # 조인트들 총 길이.
        tmp = pm.group(em=True)
        dist = getDistance(self.joints)
        snap( self.joints, tmp, type='parent' )
        tmpVec = self.worldUpVec * dist
        pm.move( tmp, tmpVec.x, tmpVec.y, tmpVec.z, r=True, os=True, wd=True )
        snap( tmp, root.up )
        pm.delete(tmp)

        handles = []
        for jnt in self.joints:
            hdl = Handle()
            snap( jnt, hdl.handle, type='parent' )
            pm.parent( hdl.handle, root.result)
            hdl.result.displayLocalAxis.set(True)
            handles.append(hdl)

        pm.parent( handles[-1].handle, w=True)
        pm.pointConstraint( handles[-1].result, root.aim )

        for i,hdl in enumerate(handles[:-1]):
            pm.pointConstraint( handles[i+1].result, hdl.aim )
        
        pm.delete( handles[-1].aimConstraint )
        pm.orientConstraint( handles[-2].result, handles[-1].result)

        for hdl, jnt in zip(handles, self.joints):
            const = pm.parentConstraint( hdl.result, jnt )
            pm.parent( const, hdl.result )

        # 컬러조정
        for hdl in handles:
            #setColor( root.up, end.up, poleVec.handle, c='greengray')
            #setColor( end.aim, c='darkred')
            setColor( hdl.handle, c='red')
        
            # 어트리뷰트 조정
            #setAttrs( hdl.handle,  'rx','ry','rz','sx','sy','sz','v', lock=True, keyable=False, channelBox=False )

        # 선연결
        curveConnect( root.up, root.result)
        curveConnect( root.up, handles[-1].result)
        setColor( root.up, c='greengray')

        # 
        self.root = root
        self.end = handles[-1]

        # 주요노드 페어런팅.
        pm.parent(root.handle, handles[-1].handle, grp)

        # 부모처럼 움직일 노드에 컨스트레인
        if pm.objExists(self.parentSlot):
            pm.parent( pm.parentConstraint( self.parentSlot, grp, mo=True ), self.parentSlot)
            pm.parent( pm.scaleConstraint ( self.parentSlot, grp, mo=True ), self.parentSlot)

class Foot(Template):
    def __init__(self):
        self.footJnt    = pm.PyNode('LeftFoot')
        self.toeBaseJnt = pm.PyNode('LeftToeBase')
        self.toeEndJnt  = pm.PyNode('LeftToeEnd')

        self.groupName = 'Foot_grp'
        self.parentSlot = 'footTemplateHandle'
        self.childSlot = None

    def create(self):
        grp = self.createGroup( self.groupName )

        toeBase = pm.group(n='toeBase_hdl',em=True)
        toeEnd  = pm.group(n='toeEnd_hdl',em=True)

        snap( self.footJnt, grp, type='parent')
        snap( self.toeBaseJnt, toeBase, type='parent')
        snap( self.toeEndJnt, toeEnd, type='parent')

        pm.parent( toeBase, toeEnd, grp )

        pm.parent( pm.parentConstraint( toeBase, self.toeBaseJnt ), toeBase)
        pm.parent( pm.parentConstraint( toeEnd,  self.toeEndJnt ),  toeEnd)

        toeBase.displayHandle.set(True)
        toeEnd.displayHandle.set(True)

        setColor( toeBase, toeEnd, c='red' )

        self.toeBase = toeBase
        self.toeEnd = toeEnd

        # 부모처럼 움직일 노드에 컨스트레인
        if pm.objExists('LeftFoot'):
            pm.parentConstraint( 'LeftFoot', grp, mo=True )

class Head(Template):
    def __init__(self):
        self.neckJnt    = pm.PyNode('Neck')
        self.headJnt    = pm.PyNode('Head')
        self.headEndJnt = pm.PyNode('HeadEnd')

        self.groupName = 'Head_grp'
        self.parentSlot = 'chestTemplateHandle'
        self.childSlot = None

    def create(self):
        grp = self.createGroup( self.groupName )
        snap( self.headJnt,    grp,     type='parent')

        neck    = pm.group(n='neck_hdl',em=True)
        head    = pm.group(n='head_hdl',em=True)
        headEnd = pm.group(n='headEnd_hdl',em=True)
        
        snap( self.headJnt,    head,    type='parent')
        snap( self.headEndJnt, headEnd, type='parent')
        snap( self.neckJnt,    neck,    type='parent')

        pm.parent( headEnd, head )
        pm.parent( head, neck, grp )

        pm.parent( pm.parentConstraint( head,     self.headJnt ),    head)
        pm.parent( pm.parentConstraint( headEnd,  self.headEndJnt ), headEnd)
        pm.parent( pm.parentConstraint( neck,     self.neckJnt ),    neck)

        setAttrs( head,    'sx','sy','sz','v', lock=True, keyable=False, channelBox=False )
        setAttrs( headEnd, 'rx','ry','rz','sx','sy','sz','v', lock=True, keyable=False, channelBox=False )
        setAttrs( neck,    'rx','ry','rz','sx','sy','sz','v', lock=True, keyable=False, channelBox=False )

        head.   displayHandle.set(True)
        headEnd.displayHandle.set(True)
        neck.   displayHandle.set(True)

        setColor( neck, head, headEnd, c='red' )

        self.neck = neck
        self.head = head
        self.headEnd = headEnd

class Torso(Template):
    def __init__(self):
        self.hipsTranslationJnt = pm.PyNode('HipsTranslation')
        self.hipsJnt = pm.PyNode('Hips')
        self.spineJnts = pm.ls('Spine*', type='joint')
        self.shoulderJnt = pm.PyNode('LeftShoulder') 

        self.groupName = 'Torso_grp'

    def create(self):
        grp = self.createGroup( self.groupName )
        snap( self.hipsTranslationJnt, grp, type='parent')

        hipsTranslation = pm.group(n='hipsTranslation_hdl',em=True)
        snap( self.hipsTranslationJnt, hipsTranslation, type='parent')
        pm.parent( pm.parentConstraint( hipsTranslation, self.hipsTranslationJnt ), hipsTranslation)
        hipsTranslation.displayHandle.set(True)

        hips = pm.group(n='hips_hdl',em=True)
        snap( self.hipsJnt, hips, type='parent')
        pm.parent( pm.parentConstraint( hips, self.hipsJnt ), hips)
        hips.displayHandle.set(True)

        shoulder = pm.group(n='shoulder_hdl',em=True)
        snap( self.shoulderJnt, shoulder, type='parent')
        pm.parent( pm.parentConstraint( shoulder, self.shoulderJnt ), shoulder)
        setAttrs( shoulder, 'rx','ry','rz','sx','sy','sz','v', lock=True, keyable=False, channelBox=False )
        shoulder.displayHandle.set(True)
        
        spines =[]
        for jnt in self.spineJnts:
            handle = pm.group(n=jnt+'_hdl',em=True)
            snap( jnt, handle, type='parent')
            pm.parent( pm.parentConstraint( handle, jnt ), handle)
            setAttrs( handle, 'rx','ry','rz','sx','sy','sz','v', lock=True, keyable=False, channelBox=False )
            handle.displayHandle.set(True)
            spines.append(handle)

        pm.parent( hips, hipsTranslation)
        pm.parent( hipsTranslation, shoulder, spines, grp )
        setColor( hipsTranslation, hips, shoulder, spines, c='red' )

