# coding=utf-8
__author__ = 'alfred'

import pymel.core as pm

def rigSymmetryTransform( *args, **kwargs):
    '''
    조인트를 미러링 하기 위해서 만들어진 스크립트
    직접 유틸리티 노드로 미러링을 해서 구현을 했으나.
    연결된 노드가 없어지면 조인트가 쪼그라드는 현상이 생김
    이를 방지하기 위해 아래 컨테이너를 하나 거쳐서 연결
    미러를 삭제하려면 아래 컨테니어를 삭제하면 미러링이 깨짐.

    개선의 여지 있음. 제한된 상황에서만 올바르게 작동함.
    '''
    if args:
        pm.select(args)

    sel = pm.selected()
    if not sel:
        print u'뭐라도 하나 선택하고 실행하세요.'
        return

    obj = sel[0]

    target=None
    if len(sel)>1:
        target = sel[1]

    axis      = kwargs.get('axis',     kwargs.get('ax','x') )
    translate = kwargs.get('translate',kwargs.get('t',True) )
    rotate    = kwargs.get('rotate',   kwargs.get('r',True) )
    scale     = kwargs.get('scale',    kwargs.get('s',True) )

    if not target:
        target=pm.spaceLocator( n= obj.name()+'__'+ axis.lower() +'axis_symmetryTrans_LOC')
    else:
        target = pm.PyNode(target)

    # 계산노드
    md = pm.createNode('multiplyDivide')
    md.input2.set(-1,-1,-1)

    # 컨테이너에 연결함.. 직접연결할경우
    cont = pm.container( type='dagContainer', addNode=[md], n=obj.name()+'__'+ axis.lower() +'axis_symmetryTrans_UTIL' )

    if axis == 'x':
        if translate:
            # 해당 축이 꺼짐
            #obj.tx >> target.tx
            if not target.ty.isLocked():
                obj.ty >> cont.ty
                cont.ty >> target.ty
            if not target.tz.isLocked():
                obj.tz >> cont.tz
                cont.tz >> target.tz

            # 해당 축이 켜짐
            if not target.tx.isLocked():
                obj.tx      >> md.input1X
                md.outputX  >> target.tx
                #obj.ty     >> md.input1Y
                #md.outputY >> target.ty
                #obj.tz     >> md.input1Z
                #md.outputZ >> target.tz

        if rotate:
            # 해당 축이 켜짐
            if not target.rx.isLocked():
                obj.rx >> cont.rx
                cont.rx >> target.rx
            #obj.ry >> target.ry
            if not target.rz.isLocked():
                obj.rz >> cont.rz
                cont.rz >> target.rz

            # 해당 축이 꺼짐
            #obj.rx     >> md.input1X
            #md.outputX >> target.rx
            if not target.ry.isLocked():
                obj.ry      >> md.input1Y
                md.outputY  >> target.ry
            if not target.rz.isLocked():
                obj.rz      >> md.input1Z
                md.outputZ  >> target.rz

    elif axis == 'y':
        if translate:
            # 해당 축이 꺼짐
            if not target.tx.isLocked():
                obj.tx >> cont.tx
                cont.tx >> target.tx
            #obj.ty >> target.ty
            if not target.tz.isLocked():
                obj.tz >> cont.tz
                cont.tz >> target.tz

            # 해당 축이 켜짐
            #obj.tx      >> md.input1X
            #md.outputX  >> target.tx
            if not target.ty.isLocked():
                obj.ty     >> md.input1Y
                md.outputY >> target.ty
            #obj.tz     >> md.input1Z
            #md.outputZ >> target.tz

        if rotate:
            # 해당 축이 켜짐
            #obj.rx >> target.rx
            if not target.ry.isLocked():
                obj.ry >> cont.ry
                cont.ry >> target.ry
            #obj.rz >> target.rz

            # 해당 축이 꺼짐
            if not target.rx.isLocked():
                obj.rx     >> md.input1X
                md.outputX >> target.rx
            #obj.ry      >> md.input1Y
            #md.outputY  >> target.ry
            if not target.rz.isLocked():
                obj.rz      >> md.input1Z
                md.outputZ  >> target.rz

    elif axis == 'z':
        if translate:
            # 해당 축이 꺼짐
            if not target.tx.isLocked():
                obj.tx >> cont.tx
                cont.tx >> target.tx
            if not target.ty.isLocked():
                obj.ty >> cont.ty
                cont.ty >> target.ty
            #obj.tz >> target.tz

            # 해당 축이 켜짐
            #obj.tx      >> md.input1X
            #md.outputX  >> target.tx
            #obj.ty     >> md.input1Y
            #md.outputY >> target.ty
            if not target.tz.isLocked():
                obj.tz     >> md.input1Z
                md.outputZ >> target.tz

        if rotate:
            # 해당 축이 꺼짐
            if not target.rx.isLocked():
                obj.rx     >> md.input1X
                md.outputX >> target.rx
            if not target.ry.isLocked():
                obj.ry      >> md.input1Y
                md.outputY  >> target.ry
            #obj.rz      >> md.input1Z
            #md.outputZ  >> target.rz

            # 해당 축이 켜짐
            #obj.rx >> target.rx
            #obj.ry >> target.ry
            if not target.rz.isLocked():
                obj.rz >> cont.rz
                cont.rz >> target.rz

    if scale:
        if not target.sx.isLocked():
            obj.sx >> cont.sx
            cont.sx >> target.sx
        if not target.sy.isLocked():
            obj.sy >> cont.sy
            cont.sy >> target.sy
        if not target.sz.isLocked():
            obj.sz >> cont.sz
            cont.sz >> target.sz

    pm.select( obj )
    return cont, target