# coding=utf-8
import pymel.core as pm

def createLinkedCrv( *curves ):
    '''
    update : 2015-04-24
    '''
    if curves:
        pm.select( curves )
    curves = pm.selected()
    if not curves:
        raise

    #curves = pm.filterExpand( sm=9 )
    #curves = [ pm.PyNode(curve) for curve in curves ]

    linkedCrvs = []

    for curve in curves:       
        # 입력된 커브의 트랜스폼 노드의 히아라키 위치를 맞춰줌
        linkedCrv = pm.group(em=True)
        parent = curve.getParent()
        if parent:
            linkedCrv.setParent(space, r=True)
        linkedCrv.setMatrix( curve.getMatrix( ws=True ), ws=True )

        # 피봇 위치 맞춤
        rotatePiv = curve.getRotatePivot( space='world' )
        scalePiv  = curve.getScalePivot(  space='world' )    
        linkedCrv.setRotatePivot( rotatePiv, ws=True )
        linkedCrv.setScalePivot(  scalePiv,  ws=True )

        # 커브 쉐입 생성
        linkedCrvShape = pm.createNode('nurbsCurve', p=linkedCrv )

        # 연결 : 핵심 !
        curve.getShape().worldSpace[0] >> linkedCrvShape.create

        # 컬러 변경
        pm.color( linkedCrvShape, ud=1 )

        # 이름 변경 
        linkedCrv.rename( curve+'_linkedCrv#')

        linkedCrvs.append( linkedCrv )

    pm.select(linkedCrvs)
    return linkedCrvs

def createMiddleCrv( curves=[], parameter=0.5 ):
    '''
    update : 2015-04-24
    '''
    if curves:
        curves = pm.select(curves)
    curves = pm.selected()
    if not curves:
        raise    

    surface, loft = pm.loft( 
        curves, 
        ch           = True, 
        uniform      = True, 
        close        = False, 
        autoReverse  = True, 
        degree       = 3, 
        sectionSpans = 1, 
        range        = False, 
        polygon=0,  # 0: nurbs surface 
                    # 1: polygon (use nurbsToPolygonsPref to set the parameters for the conversion) 
                    # 2: subdivision surface (use nurbsToSubdivPref to set the parameters for the conversion) 
                    # 3: Bezier surface 
                    # 4: subdivision surface solid (use nurbsToSubdivPref to set the parameters for the conversion) 
        reverseSurfaceNormals = True )

    dupCrv, crvFromSurf = pm.duplicateCurve( surface.getShape().v[ parameter ], ch=True, range=False, local=False )
    pm.delete( surface, loft, crvFromSurf )

    dupCrv = pm.PyNode( dupCrv )
    dupCrv.rename('middleCrv#')   

    return dupCrv

def twoPointArcRig( prefix='arc1' ):
    '''
    리깅된 아크 커브를 생성한다.
    a = createTowPointArcRig( 'arc_L' )
    '''
    pointA = pm.spaceLocator()
    pointB = pm.spaceLocator()
    arcCenter = pm.spaceLocator()
    arcCenter.it.set(False)
    center = pm.spaceLocator()
    up = pm.spaceLocator()
    pointA.tx.set(10)
    pointB.tx.set(-10)
    up.ty.set(5)
    
    makeArc = pm.createNode('makeTwoPointCircularArc')
    makeArc.radius.set(20)
    makeArc.directionVector.set(0,1,0)
    
    pointA.worldPosition[0] >> makeArc.pt1
    pointB.worldPosition[0] >> makeArc.pt2

    # upVector
    minus = pm.createNode( 'plusMinusAverage' )
    up.worldPosition[0] >> minus.input3D[0]
    center.worldPosition[0] >> minus.input3D[1]
    minus.operation.set(2) # minus
    minus.output3D >> makeArc.directionVector
    
    pm.select(cl=True)
    crv = pm.group(em=True)
    crv.it.set(False)
    crv.addAttr('radius', keyable=True)
    crv.radius.set(20)
    crvShape = pm.createNode('nurbsCurve', p=crv)
    makeArc.outputCurve >> crvShape.create
    crv.radius >> makeArc.radius
    
    # Point On Curve Node
    poc = pm.PyNode( pm.pointOnCurve( crv, pr=0.5, ch=True ) )
    poc.curvatureCenter >> arcCenter.t

    # Locator on Curve 
    locOnCrv = pm.spaceLocator()
    locOnCrv.it.set(False)
    locOnCrv.addAttr('parameter', keyable=True, dv=0.5, min=0, max=1 )
    poc.p >> locOnCrv.t
    poc.turnOnPercentage.set(True)    
    locOnCrv.parameter >> poc.parameter
    
    # Group
    grp = pm.group( em=True )
    pm.parent( locOnCrv, pointA, pointB, arcCenter, up, center, crv, grp )
    
    # Rename
    pointA.rename( prefix + '_pt1')
    pointB.rename( prefix + '_pt2')
    arcCenter.rename( prefix + '_arcCenter')
    crv.rename( prefix + '_crv')
    grp.rename( prefix + '_grp')
    poc.rename( prefix + '_poc')
    makeArc.rename( prefix + '_makeArc')
    locOnCrv.rename( prefix + '_locOnCrv')   
    up.rename( prefix + '_up')
    center.rename( prefix + '_center')

    # Visible
    center.v.set(False)
    up.v.set(False)
    arcCenter.v.set(False)
    
    return [grp, crv, locOnCrv, pointA, pointB, arcCenter, poc, up, center, makeArc ]
    
#
# TODO :
#
def getCrvInfo( curve ):
    node = pm.PyNode( curve )
    nodeType = node.nodeType()

    trans =None
    crv = None
    if nodeType == 'nurbsCurve':
        crv = node
        trans = crv.getParent()
    elif nodeType == 'transform':
        trans = node
        crv   = trans.getShapes( type='nurbsCurve' )[0]

    return {
        'nurbsCurve' : crv.name(),

        'min'    : crv.min.get(),
        'max'    : crv.max.get(),
        'length' : crv.length(),

        'degree'    : crv.degree(),
        'spans'     : crv.spans.get(),
        #'form'      : crv.form(),
        'form'      : int(crv.form())-1, # 대부분 int형 자료가 필요한데 리턴값이 enum으로 되어 있어 불편함.. 
        'isRational': False,
        'dimension' : 3,
        'knotCount' : crv.numKnots(),
        'knots'     : crv.getKnots(),     
        #'cvCount'   : crv.numCVs(),
        'cvCount'   : len( crv.getCVs() ), # periodic 커브(nurbsCircle로 만들어진 커브처럼 마지막 두개의 span이 1,2번 span과 겹쳐짐)일 경우 pymel의 numCVs()함수에서 cv개수가 잘못 나오는듯 함. 실제 cv개수를 계산해서 넣음.
        'cvPosition': crv.getCVs()
        }

def getCrvCmd( curve, type='pythonAttr', singleLine=False ):
    '''
    커브 실행 명령을 리턴함.

    type = 'mel', 'python', 'pymel',  'melAttr', 'pythonAttr', 'pymelAttr', 'melCreate', 'pythonCreate'
    '''
    crvInfo = getCrvInfo( curve )
    crvInfo['cvPosition'] =  ', '.join( [ str(tuple(pos)) for pos in crvInfo['cvPosition']] ) # dt.Point 타입을 스트링으로 바꿔서 다시 저장 줘야함
    
    crvCmd = ''

    #
    # python
    #
    if   type == 'pythonCreate':
        crvCmd = '%(degree)d, %(spans)d, %(form)d, %(isRational)r, %(dimension)d, %(knots)s, %(knotCount)d, %(cvCount)d, %(cvPosition)s, type="nurbsCurve"' % crvInfo
    
    elif type == 'pythonAttr':
        #crv = cmds.createNode("nurbsCurve")
        #cmds.setAttr( crv+".cc", 3, 1, 0, False, 3, [0.0, 0.0, 0.0, 1.0, 1.0, 1.0], 6, 4, (0.0, 0.0, 0.0), (0.33333333333333326, 0.0, 0.0), (0.6666666666666666, 0.0, 0.0), (1.0, 0.0, 0.0), type="nurbsCurve" )
        crvCmd  = 'crv = cmds.createNode("nurbsCurve")\n'
        crvCmd += 'cmds.setAttr( crv+".cc", %(degree)d, %(spans)d, %(form)d, %(isRational)r, %(dimension)d, %(knots)s, %(knotCount)d, %(cvCount)d, %(cvPosition)s, type="nurbsCurve" )' % crvInfo
        crvCmd = crvCmd % crvInfo
    
    elif type == 'pymelAttr':
        #crv = pm.createNode("nurbsCurve")
        #crv.setAttr( "cc", 3, 1, 0, False, 3, [0.0, 0.0, 0.0, 1.0, 1.0, 1.0], 6, 4, (0.0, 0.0, 0.0), (0.33333333333333326, 0.0, 0.0), (0.6666666666666666, 0.0, 0.0), (1.0, 0.0, 0.0), type="nurbsCurve" )
        crvCmd  = 'crv = pm.createNode("nurbsCurve")\n'
        crvCmd += 'crv.setAttr( "cc", %(degree)d, %(spans)d, %(form)d, %(isRational)r, %(dimension)d, %(knots)s, %(knotCount)d, %(cvCount)d, %(cvPosition)s, type="nurbsCurve" )' % crvInfo
        crvCmd = crvCmd % crvInfo
    
    elif type == 'pymel' or type == 'python':
        # curve( d=3, periodic=False, p=[(0.0, 0.0, 0.0), (0.333, 0.0, 0.0), (0.666, 0.0, 0.0), (1.0, 0.0, 0.0)], k=[0.0, 0.0, 0.0, 1.0, 1.0, 1.0])
        crvInfo['form'] = True if crvInfo['form'] == 1 or crvInfo['form'] == 2 else False # close or periodic
        crvCmd = 'curve( d=%(degree)d, periodic=%(form)r, p=[%(cvPosition)s], k=%(knots)s)' % crvInfo

    #
    # mel
    #    
    elif type == 'melCreate':
        # -type "nurbsCurve" 3 1 0 false 3 6 0.0 0.0 0.0 1.0 1.0 1.0 4 0.0 0.0 0.0 0.333 0.0 0.0 0.666 0.0 0.0 1.0 0.0 0.0 
        crvInfo['isRational'] = str(crvInfo['isRational']).lower()
        crvInfo['cvPosition'] = crvInfo['cvPosition'].replace('), (', ' ' % crvInfo).replace(',','').replace('(','').replace(')','')
        crvInfo['knots']      = str(crvInfo['knots']).replace(', ', ' ').replace('[','').replace(']','')
        crvCmd = '-type "nurbsCurve" %(degree)d %(spans)d %(form)d %(isRational)s %(dimension)d %(knotCount)d %(knots)s %(cvCount)d %(cvPosition)s ' % crvInfo

    elif type == 'melAttr':
        '''
        createNode nurbsCurve -n "curveShape1";  
        setAttr ".cc" -type "nurbsCurve"  
            3 1 0 false 3  
            6  
            0.0 0.0 0.0 1.0 1.0 1.0  
            4  
            0.0 0.0 0.0  
            0.333 0.0 0.0  
            0.666 0.0 0.0  
            1.0 0.0 0.0;  
        '''
        if singleLine:
            crvInfo['n'] = ''
            crvInfo['t'] = ''
        else:
            crvInfo['n'] = ' \n'
            crvInfo['t'] = '    '

        crvInfo['isRational'] = str(crvInfo['isRational']).lower()
        crvInfo['cvPosition'] = crvInfo['cvPosition'] .replace('), (', ' %(n)s%(t)s' % crvInfo).replace(',','').replace('(','').replace(')','')
        crvInfo['knots']      = str(crvInfo['knots']) .replace(', ',   ' ')                .replace('[','').replace(']','')

        crvCmd += 'createNode nurbsCurve -n "%(nurbsCurve)s"; %(n)s'
        crvCmd += 'setAttr ".cc" -type "nurbsCurve" %(n)s%(t)s'
        crvCmd += '%(degree)d %(spans)d %(form)d %(isRational)s %(dimension)d %(n)s%(t)s'
        crvCmd += '%(knotCount)d %(n)s%(t)s'
        crvCmd += '%(knots)s %(n)s%(t)s'
        crvCmd += '%(cvCount)s %(n)s%(t)s'
        crvCmd += '%(cvPosition)s; %(n)s'
        crvCmd = crvCmd % crvInfo
    
    elif type == 'mel':
        # curve -d 3 -periodic false -p 0.0 0.0 0.0 -p 0.33333333333333326 0.0 0.0 -p 0.6666666666666666 0.0 0.0 -p 1.0 0.0 0.0 -k 0.0 -k 0.0 -k 0.0 -k 1.0 -k 1.0 -k 1.0;
        crvInfo['form']       = 'true' if crvInfo['form'] == 1 or crvInfo['form'] == 2 else 'false' # close or periodic
        crvInfo['cvPosition'] = crvInfo['cvPosition'] .replace('), (', ' -p ').replace(',','').replace('(','-p ').replace(')','')
        crvInfo['knots']      = str(crvInfo['knots']) .replace(', ',   ' -k ')                .replace('[','-k ').replace(']','')
        crvCmd = 'curve -d %(degree)d -periodic %(form)s %(cvPosition)s %(knots)s;' % crvInfo
    
    return crvCmd

def createKnotVectorString(cvNum, degree):
    """
    @param int cvNum: number of CVs in constructing curve.
    @param int degree: degree of constructing curve.
    @return list
    """
    if cvNum <= degree:
        print "warning, number of CVs can't be less than degree + 1"
        return None
    tailsSize = degree
    knotsNum  = cvNum + degree - 1
    knotsArray = [0]*knotsNum
    for i in range(0, len(knotsArray)-degree+1):
        knotsArray[i + degree-1] = i
    tailValue = knotsArray[-tailsSize-1] + 1
    for i in range(1,tailsSize):
        knotsArray[-i] = tailValue
    return knotsArray

# expression
def traceCurveParticle( curveShape, particleShape ):
    # python( "ut.traceCurveParticle( 'curveShape1', 'particleShape1')" );

    particleShape = pm.PyNode( particleShape )
    curveShape    = pm.PyNode( curveShape )

    ptcIDs = particleShape.particleIds()
    ptcIDs.sort()

    cvPos = []
    for i in ptcIDs:
        try:
            pos = particleShape.getParticleId( id=i, attribute='position')
            cvPos.append( tuple(pos) )
        except:
            pass
    
    try:
        degree     = 3
        spans      = len(cvPos) - degree
        form       = 0     # open
        isRational = False
        dimension  = 3
        knots      = tuple( createKnotVectorString( len(cvPos), degree ) )

        curveShape.setAttr( "cc", degree, spans, form, isRational, dimension, knots, len(knots), len(cvPos), *cvPos, type="nurbsCurve" )

    except:
        pass

def distributeCrv( transformNodes, curve=None, uniform=True ):
    nodes = [pm.PyNode(node) for node in transformNodes]

    crv = pm.PyNode(curve)
    crvShape = crv.getShape()
    
    nodeNums = len(nodes)    

    contMembers = []    
    if uniform:
        rebCrv, reb = pm.rebuildCurve( crvShape, ch=True, rpo=False, rt=4, end=1, kr=0, kcp=0, kep=1, kt=0, s=4, d=3, tol=0.001 )
        crvShape  = rebCrv.getShapes( type='nurbsCurve' )[0]

        rebCrv.rename( crv+'_rebCrv' )
        reb.rename( crv+'_rebuildCrv' )

        contMembers.append( pm.parentConstraint( crv, rebCrv ) )
        contMembers.append( pm.scaleConstraint(  crv, rebCrv ) )
        contMembers.append( rebCrv )
        contMembers.append( reb )

    unit = None
    if crv.form() == 'periodic':
        unit = (1.0/nodeNums)
    else:
        unit = (1.0/(nodeNums-1))

    for i, node in enumerate( nodes ):
        pointOnCurve = pm.PyNode( pm.pointOnCurve( crvShape, ch=True ) )
        pointOnCurve.rename( node+'_POC' )
        pointOnCurve.turnOnPercentage.set(True)

        pointOnCurve.parameter.set( unit*i  )
        pointOnCurve.p >> node.t

        pointOnCurve.setAttr('parameter', keyable=True)

        contMembers.append( pointOnCurve )

    cont = pm.container( type='dagContainer', addNode=contMembers, n=crv+'_distributeCrv#' )
    cont.v.set(False)

    return cont    

# conversion
def epToParam( ep ):
    #
    # 에딧 포인트를 선택했을 경우
    #

    # 커브쉐입 이름 가져옴
    curveShape = pm.PyNode( ep.split('.ep[')[0] )

    # degree
    degree = curveShape.degree()
    
    # knotValue( parameter )값 가져옴.
    knotValue = curveShape.getKnots()
    if not degree == 1:
        knotValue = knotValue[ degree-1 : -(degree-1) ]

    epNum = int( ep.split('.ep[')[1][:-1] )

    parameter = knotValue[ epNum ]

    return parameter

def crvPointToParam( u ):
    curveShape = u.split('.u[')[0]
    parameter = float( u.split('.u[')[1][:-1] )

    return parameter

