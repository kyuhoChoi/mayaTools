# coding=utf-8
import pymel.core as pm

def rigCurveConnect( *objs, **kwargs ):
    '''
    update : 2015-04-15
    '''
    if objs:
        pm.select(objs)
    
    sel = pm.selected( type='transform')
    if not sel:
        raise

    obj = sel[0]

    # 삭제
    delete = kwargs.get('delete', False)
    if delete:
        for crvShp in obj.getShapes():
            if crvShp.hasAttr('curveConnectedLOC'):
                try:
                    pm.delete( crvShp, crvShp.curveConnectedLOC.inputs() )
                except:
                    pass
        return True

    # 타겟 가져옴.
    target = sel[1]

    name     = kwargs.get('name') or kwargs.get('n', target+'_CONNCRV' )
    position = kwargs.get('position') or kwargs.get('p', (0,0,0) )

    # 커브 생성
    crvTrans = pm.curve( n=name, d=1, p=[ position, position ], k=[0,1] )
    crvShape = crvTrans.getShape()

    # obj에 커브 쉐입을 종속 시킴 : 커브를 선택해도 오브젝트를 선택한 효과를 줌.
    pm.parent( crvShape, obj, r=True, s=True)
    pm.delete( crvTrans )

    # target에 locator를 종속 시킴
    loc = pm.pointCurveConstraint( crvShape+'.ep[1]', ch=True)[0]
    loc = pm.PyNode(loc)
    pm.pointConstraint( target, loc )

    # 로케이서 속성 조정
    loc.getShape().localPosition.set(0,0,0)
    loc.getShape().v.set(False)
    loc.v.set(False)
    loc.setParent(obj)
    loc.rename( target+'_CONNLOC' )

    # 커브쉐입에 어트리뷰트 추가
    crvShape.addAttr( 'curveConnectedTo',  at='message' )
    crvShape.addAttr( 'curveConnectedLOC', at='message' )

    # 어트리뷰트 연결
    target.message >> crvShape.curveConnectedTo
    loc.   message >> crvShape.curveConnectedLOC

    return loc