# coding=utf-8
'''
커브위에 존재하는 로케이터 생성
'''
__author__ = 'alfred'

import pymel.core as pm

class LocatorOnCurve(object):
    '''
    :parameters:
        curve ,                         # 커브이름
        parameter = 0.5,                # 커브 상의 위치
        name = None                     # 이름을 명시할 경우 해당이름으로 그렇지 않으면, locatorShape이 'locator'일땐 'locOnCrv#', 'group'일땐 'grpOnCrv#'
        turnOnPercentage = False,       # curvePoint를 값으로? 아님. percentage로 할건가? *주의 : percentage로 한다고 해서 커브의 비율로 계한하는게 아님.
        rotate = None,                  # None, aim, orient 중하나
        aimVector ='x',                 # x, y, z, -x, -y, -z, vector 중 하나
        upVector  ='y',                 # x, y, z, -x, -y, -z, vector 중 하나
        worldAimType = 'tangent',       # tangent, normal, vector, object,
        worldUpType  = 'curverotation', # tangent, normal, scene, vector, object, objectrotation, curverotation
        worldAimVector ='x',            # worldAimType 이 scene, vector 일때만 유효.
        worldUpVector  ='y',            # worldUpType  이 scene, vector 일때만 유효.
        aimObject = None,               # worldAimType 이 object, objectrotation 일때만 유효.
        worldUpObject  = None,          # worldUpType  이 object, objectrotation 일때만 유효.
        locatorShape ='locator',        # locator, group 중 하나
        vectorShape  ='group',          # locator, group 중 하나

    :TODO : worldAimType 에 objectrotation, curverotation 사용 할 수 있도록 방법 찾아야함.

    :sample:
        # sample 1:
            curve = pm.curve( d=3, p=[ (5.398530435027274, 0.0, 2.636910065983344), (4.344566726592057, 0.0, 3.517847071376655), (2.2366393097216077, 0.0, 5.279721082163249), (-3.343728636037937, 0.0, 2.716482506849595), (-0.22912241191149801, 0.0, -4.813534894925304), (-0.5614162589497707, 0.0, -9.402385791812858), (-3.979692990558796, 0.0, -9.30078556056116), (-5.68883135636331, 0.0, -9.249985444935318) ], k=[ 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 5.0, 5.0 ] )
            upLoc = pm.spaceLocator()
            upLoc.ty.set(10)
            LocatorOnCurve( curve, parameter=1.0, rotate=None )     # 로테이션 리깅은 안. 제일 빠름.
            LocatorOnCurve( curve, parameter=3.0, rotate='orient' ) # 로테이션(Orient)은 커브의 트랜스폼을 사용.
            LocatorOnCurve( curve, parameter=2.0, rotate='aim' )    # 로테이션(aim)  worldUpType을 명시하지 않을경우, aim은 커브의 tangent crv의 rotation을 up으로 사용
            LocatorOnCurve( curve, parameter=0.5, rotate='aim', worldUpType='object', worldUpObject=upLoc )

    :version:
        2014-04-27 : doc 수정
        2014-09-24 : 파라메터 조정, doc 수정
    '''

    def __init__(self, *args, **kwargs):
        if args:
            pm.select(args)

        curves = pm.filterExpand( sm=9,  expand=True ) # Nurbs Curves
        cps    = pm.filterExpand( sm=39, expand=True ) # Curve Parameter Points
        eps    = pm.filterExpand( sm=30, expand=True ) # Edit Points
        cvs    = pm.filterExpand( sm=28, expand=True ) # Control Vertices (CVs)
        knots  = pm.filterExpand( sm=40, expand=True ) # Curve Knot

        #print args
        #print curves, cps, eps, cvs, knots

        # Nurbs Curves
        if curves:
            self.curve = pm.PyNode( curves[0] )
            self.param = kwargs.get( 'parameter', kwargs.get( 'p', 0.5))

        # Curve Parameter Points
        if cps:
            curveStr, paramStr = cps[0].split('.u[')
            self.curve = pm.PyNode( curveStr )
            self.param = float( paramStr[:-1] )

        # Edit Points
        if eps:
            # 커브쉐입 이름 가져옴
            curve = pm.PyNode( eps[0].split('.ep[')[0] )
            epNum = int( eps[0].split('.ep[')[1][:-1] ) # 이름에서 순서만 따옴.

            #
            # knotValue들이 parameter값들로 추정됨.
            #
            # knotValue( parameter )값 가져옴.
            # degree가 1일경우엔   : editPoint의순서와 knotValue의 순서가 1:1로 매핑됨.
            #          2이상일경우 : editPoint degree-1부터 -(degree-1)
            #
            degree     = curve.degree() # degree
            knotValues = curve.getKnots()
            if not degree == 1:
                knotValues = knotValues[ degree-1 : -(degree-1) ] # degree가 1이면 어레이 조정
            param = knotValues[ epNum ]

            self.curve = curve
            self.param = param

        #print self.curve, self.param

        self.name = kwargs.get( 'name', kwargs.get( 'n', 'xformOnCrv#'))
        self.turnOnPercentage= kwargs.get( 'turnOnPercentage', kwargs.get( 'top', False))

        self.locatorShape = kwargs.get( 'locatorShape', kwargs.get( 'shape', 'locator'))  # locator, group 중 하나
        self.vectorShape  ='group'    # locator, group 중 하나

        #
        # 로케이터 회전 형식 : None, aim, orient 중하나
        #
        self.rotate = kwargs.get( 'rotate', kwargs.get( 'r', None))

        # 로케이터 aim축 : x, y, z, -x, -y, -z, vector 중 하나
        self.aimVector = self._strToVec( kwargs.get( 'aimVector', kwargs.get( 'aim', 'x')) )

        # 로케이터 up축 : x, y, z, -x, -y, -z, vector 중 하나
        self.upVector  = self._strToVec( kwargs.get( 'upVector',  kwargs.get( 'up',  'y')) )

        # 로케이터 aim축 대상 : tangent, normal, vector, object 중 하나
        self.worldAimType = kwargs.get( 'worldAimType', kwargs.get( 'waimt', 'tangent'))

        # 로케이터 up축 대상: tangent, normal, scene, vector, object, objectrotation, curverotation 중 하나
        self.worldUpType = kwargs.get( 'worldUpType', kwargs.get( 'wupt', 'curverotation'))

        self.worldAimVector = self._strToVec( kwargs.get( 'worldAimVector', kwargs.get( 'waim', 'x')) ) # x, y, z, -x, -y, -z, vector 중 하나, worldAimType 이 scene, vector 일때만 유효.
        self.worldUpVector  = self._strToVec( kwargs.get( 'worldUpVector',  kwargs.get( 'wup',  'y')) ) # x, y, z, -x, -y, -z, vector 중 하나, worldUpType  이 scene, vector 일때만 유효.
        self.worldAimObject = kwargs.get( 'aimObject', kwargs.get( 'wao', None)) # worldAimType 이 object, objectrotation 일때만 유효.
        self.worldUpObject  = kwargs.get( 'worldUpObject',  kwargs.get( 'wuo', None)) # worldUpType  이 object, objectrotation 일때만 유효.

        self.create()

    def create(self):
        ''' 로케이터 생성 '''
        self.positionRig()
        if self.rotate == 'aim':
            self.aimRig()
        elif self.rotate == 'orient':
            self.orientRig()

        pm.select( self.locator)

    def positionRig(self):
        #
        # 로케이터 생성
        #
        LOC = None
        if self.locatorShape=='locator':
            LOC = pm.spaceLocator( n='locOnCrv#')
        else:
            LOC = pm.group( n='grpOnCrv#', em=True)

        if self.name:
            LOC.rename( self.name )

        LOC.addAttr( 'parameter',        sn='pr',  dv=self.param,        keyable=True )
        LOC.addAttr( 'turnOnPercentage', sn='top', dv=self.turnOnPercentage, at='bool', keyable=True )
        LOC.it.set(False)

        #
        # pointOnCurve 리깅
        #
        pntOnCrv = pm.PyNode( pm.pointOnCurve( self.curve, parameter=self.param, ch=True ) )
        pntOnCrv.turnOnPercentage.set(True)

        pntOnCrv.setAttr('parameter',        keyable=True)
        pntOnCrv.setAttr('turnOnPercentage', keyable=True)

        pntOnCrv.rename( LOC+'_POC' )

        #
        # Position 리깅
        #
        LOC.parameter        >> pntOnCrv.parameter
        LOC.turnOnPercentage >> pntOnCrv.turnOnPercentage
        pntOnCrv.position    >> LOC.t

        self.locator = LOC
        self.pointOnCurve = pntOnCrv

    def aimRig(self):
        aimVector      = self.aimVector
        upVector       = self.upVector
        worldAimVector = self.worldAimVector
        worldUpVector  = self.worldUpVector
        LOC = self.locator
        pntOnCrv = self.pointOnCurve

        # -------------------------------------
        #
        # aimConstraint : 생성
        #
        # -------------------------------------
        aimConst = pm.createNode( 'aimConstraint', p=LOC )
        aimConst.aimVector.set( aimVector )
        aimConst.upVector .set( upVector )

        # -------------------------------------
        #
        # aimConstraint : LOC --> aimConstraint
        #
        # -------------------------------------
        LOC.translate              >> aimConst.constraintTranslate
        LOC.rotateOrder            >> aimConst.constraintRotateOrder
        LOC.rotatePivot            >> aimConst.constraintRotatePivot
        LOC.rotatePivotTranslate   >> aimConst.constraintRotateTranslate
        LOC.parentInverseMatrix[0] >> aimConst.constraintParentInverseMatrix

        aimConst.constraintRotate >> LOC.r

        # 컨트르레인 어트리뷰트 잠금
        for attr in ['tx','ty','tz', 'rx','ry','rz', 'sx','sy','sz', 'v']:
            pm.setAttr( aimConst + '.' + attr, keyable=False, lock=True, channelBox=False )

        # -------------------------------------
        #
        # aimConstraint : worldAimType
        #
        # -------------------------------------
        aimConst.target[0].targetWeight.set(1)

        if self.worldAimType=='tangent':
            pntOnCrv.addAttr( 'worldTangent',  sn='wt',  at='double3')
            pntOnCrv.addAttr( 'worldTangentX', sn='wtx', at='double', p='worldTangent')
            pntOnCrv.addAttr( 'worldTangentY', sn='wty', at='double', p='worldTangent')
            pntOnCrv.addAttr( 'worldTangentZ', sn='wtz', at='double', p='worldTangent')

            # 덧셈노드
            plus_wt = pm.createNode( 'plusMinusAverage', n=pntOnCrv+'_plus_worldTangent' )

            # 리깅
            pntOnCrv.position          >> plus_wt.input3D[0]
            pntOnCrv.normalizedTangent >> plus_wt.input3D[1]
            plus_wt.output3D           >> pntOnCrv.worldTangent

            pntOnCrv.worldTangent  >> aimConst.target[0].targetTranslate

        elif self.worldAimType=='normal':
            pntOnCrv.addAttr( 'worldNormal',  sn='wt',  at='double3')
            pntOnCrv.addAttr( 'worldNormalX', sn='wtx', at='double', p='worldNormal')
            pntOnCrv.addAttr( 'worldNormalY', sn='wty', at='double', p='worldNormal')
            pntOnCrv.addAttr( 'worldNormalZ', sn='wtz', at='double', p='worldNormal')

            # 덧셈노드
            plus_wt = pm.createNode( 'plusMinusAverage', n=pntOnCrv+'_plus_worldNormal' )

            # 리깅
            pntOnCrv.position         >> plus_wt.input3D[0]
            pntOnCrv.normalizedNormal >> plus_wt.input3D[1]
            plus_wt.output3D          >> pntOnCrv.worldNormal

            pntOnCrv.worldNormal >> aimConst.target[0].targetTranslate

        elif self.worldAimType=='vector':
            aimConst.addAttr( 'worldAimVector',  sn='wn',  at='double3')
            aimConst.addAttr( 'worldAimVectorX', sn='wnx', at='double', p='worldAimVector')
            aimConst.addAttr( 'worldAimVectorY', sn='wny', at='double', p='worldAimVector')
            aimConst.addAttr( 'worldAimVectorZ', sn='wnz', at='double', p='worldAimVector')
            aimConst.worldAimVector.set(worldAimVector)

            # 덧셈노드
            plus_worldAimVec = pm.createNode( 'plusMinusAverage', n=pntOnCrv+'_plus_worldAimVector' )

            # 리깅
            pntOnCrv.position       >> plus_worldAimVec.input3D[0]
            aimConst.worldAimVector >> plus_worldAimVec.input3D[1]

            plus_worldAimVec.output3D  >> aimConst.target[0].targetTranslate

        elif self.worldAimType=='object':
            worldAimObject = pm.PyNode( self.worldAimObject )
            worldAimObject.translate            >> aimConst.target[0].targetTranslate
            worldAimObject.rotatePivot          >> aimConst.target[0].targetRotatePivot
            worldAimObject.rotatePivotTranslate >> aimConst.target[0].targetRotateTranslate
            worldAimObject.parentMatrix[0]      >> aimConst.target[0].targetParentMatrix

        elif self.worldAimType=='curverotate':
            # mtx = pm.createNode('addMatrix')
            # crvTrans.worldMatrix[0] >> mtx.matrixIn[0]
            # crvTrans.parentMatrix[0] >> aimConst.target[0].targetParentMatrix
            # mtx.matrixIn[1].set( 1.0, 0.0, 0.0, 0.0,     0.0, 1.0, 0.0, 0.0,     0.0, 0.0, 1.0, 0.0,      0.0, 1.0, 0.0, 1.0,   type='matrix' )

            mtx = pm.createNode('composeMatrix')
            mtx = pm.createNode('decomposeMatrix')

        # -------------------------------------
        #
        # aimConstraint : worldUpType
        #
        # -------------------------------------
        if   self.worldUpType=='tangent':
            pntOnCrv.tangent  >> aimConst.worldUpVector

        elif self.worldUpType=='normal':
            pntOnCrv.normal        >> aimConst.worldUpVector

        elif self.worldUpType=='vector':
            aimConst.worldUpVector.set( worldUpVector )

        elif self.worldUpType=='object':
            worldUpObject = pm.PyNode( self.worldUpObject )
            worldUpObject.worldMatrix[0] >> aimConst.worldUpMatrix
            aimConst.worldUpType.set( 1 )

        elif self.worldUpType=='objectrotation':
            worldUpObject = pm.PyNode( self.worldUpObject )
            worldUpObject.worldMatrix[0] >> aimConst.worldUpMatrix
            aimConst.worldUpType.set( 2 )

        elif self.worldUpType=='curverotation':
            self.curve.worldMatrix[0] >> aimConst.worldUpMatrix
            aimConst.worldUpType.set( 2 )

        elif self.worldUpType=='scene':
            aimConst.worldUpType.set( 0 )

    def orientRig(self):
        pm.orientConstraint( self.curve, self.locator )

    def _strToVec( self, inputVal ):
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

def locatorOnCurve(*args, **kwargs):
    if args:
        pm.select(args)

    locs = []
    for item in pm.selected(fl=True):
        loc = LocatorOnCurve( item, **kwargs )
        locs.append(loc)

    return locs