# coding=utf-8
from maya import cmds
import pymel.core as pm
import math

def getAttrsFromChannelbox():
    '''
    채널박스에서 선택된 어트리뷰트 이름 리턴
    블렌드 쉐입은 잘 안됨..ㅠㅠㅠ
    @return: 어트리뷰트 리스트 리턴
    '''
    mainObjs     = pm.channelBox( pm.melGlobals['gChannelBoxName'], q=True, mainObjectList=True )
    mainAttrs    = pm.channelBox( pm.melGlobals['gChannelBoxName'], q=True, selectedMainAttributes=True )

    shapeObjs    = pm.channelBox( pm.melGlobals['gChannelBoxName'], q=True, shapeObjectList =True)
    shapeAttrs   = pm.channelBox( pm.melGlobals['gChannelBoxName'], q=True, selectedShapeAttributes=True)

    histObjs     = pm.channelBox( pm.melGlobals['gChannelBoxName'], q=True, historyObjectList =True)
    histAttrs    = pm.channelBox( pm.melGlobals['gChannelBoxName'], q=True, selectedHistoryAttributes=True)

    outputObjs   = pm.channelBox( pm.melGlobals['gChannelBoxName'], q=True, outputObjectList =True)
    outputAttrs  = pm.channelBox( pm.melGlobals['gChannelBoxName'], q=True, selectedOutputAttributes=True)

    shortNames = []
    for pair in ((mainObjs, mainAttrs), (shapeObjs, shapeAttrs), (histObjs, histAttrs), (outputObjs, outputAttrs)):
        objs, attrs = pair
        #print pair
        if attrs:
            for obj in objs:
                for attr in attrs:
                    shortNames.append('%s.%s' %(obj,attr) )


    longNames = []
    for pair in ((mainObjs, mainAttrs), (shapeObjs, shapeAttrs), (histObjs, histAttrs), (outputObjs, outputAttrs)):
        objs, attrs = pair
        #print pair
        if attrs is not None:
            for node in objs:
                result = [ objs[0] +'.' + pm.attributeQuery( attr, n=node, ln=True) for attr in attrs ]
                longNames.extend( result )

    longNames = list(set(longNames))


    return shortNames

    #return "%s.%s"%(mainObjs[-1],mainAttrs[-1])

def utilRig_negative( driver=None, driven=None ):
    if not driver or not driven:
        attrs = getAttrsFromChannelbox()
        #print attrs
        if not len(attrs)==2:
            print 'select To Attrs in Channelbox'
            return

        driver = attrs[0]
        driven = attrs[1]

    minus = pm.createNode('plusMinusAverage')
    minus.operation.set(2) # minus
    minus.input1D[0].set(1)

    driver = pm.Attribute(driver)
    driver >> minus.input1D[1]

    driven = pm.Attribute(driven)
    minus.output1D >> driven

def unHideTransformAttrs( *nodes ):
    if nodes:
        pm.select(nodes)
    
    nodes = pm.ls(sl=True)
    if not nodes:
        raise TypeError(u'뭐라도 선택하세요.')

    attrs = ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']

    for node in nodes:
        for attr in attrs:
            #node.setAttr(attr, keyable=True, lock=False )
            node.setAttr(attr, keyable=True )

def connectAttrFromChannelbox( *attrs ):
    '''
    update : 2015-04-28
    '''
    attrs = getAttrsFromChannelbox()    
    attrsF = attrs[len(attrs)/2:] # from
    attrsT = attrs[:len(attrs)/2] # to

    for t,f in zip( attrsF, attrsT ):
        try:
            pm.Attribute(t) >> pm.Attribute(f)
        except:
            print 'Not Connected : %s >> %s'%(t,f)
   
# TODO
buffer = {}
def copyAttrs():
    global buffer
    sel = pm.selected()
    buffer['tx'] = sel[0].tx.get()
    buffer['ty'] = sel[0].ty.get()
    buffer['tz'] = sel[0].tz.get()
    buffer['rx'] = sel[0].rx.get()
    buffer['ry'] = sel[0].ry.get()
    buffer['rz'] = sel[0].rz.get()
    buffer['sx'] = sel[0].sx.get()
    buffer['sy'] = sel[0].sy.get()
    buffer['sz'] = sel[0].sz.get()

def pasteAttrs( t=False, r=True, s=False ):
    for n in pm.selected():
        if t:
            n.tx.set( buffer['tx'] )
            n.ty.set( buffer['ty'] )
            n.tz.set( buffer['tz'] )

        if r:
            n.rx.set( buffer['rx'] )
            n.ry.set( buffer['ry'] )
            n.rz.set( buffer['rz'] )

        if s:
            n.sx.set( buffer['sx'] )
            n.sy.set( buffer['sy'] )
            n.sz.set( buffer['sz'] )

def rigConnectAttrsFromChannelbox( ):
    attrs = getAttrsFromChannelbox()
    num = len(attrs)/2

    for a,b in zip( attrs[num:], attrs[:num] ):
        pm.connectAttr( a, b )
        print a, '-->', b
