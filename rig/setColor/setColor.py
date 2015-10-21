# -*- coding:utf-8 -*-
import pymel.core as pm
import maya.cmds as cmds

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

def setColor( *objs, **kwargs ):
    '''
    setColor( 'locator1', 'Red' )

    :Parameters:
        nodes : node or nodes

        color : color name or index val
            'none'       : 0, ' black'      : 1,  'darkgray'   : 2,  'gray'       : 3,  'darkred'    : 4,
            'darkblue'   : 5,  'blue'       : 6,  'darkgreen'  : 7,  'darkpurple' : 8,  'purple'     : 9,
            'lightbrown' : 10, 'darkbrown'  : 11, 'brown'      : 12, 'red'        : 13, 'green'      : 14,
            'white'      : 16, 'yellow'     : 17, 'yellowgray' : 22, 'brownlight' : 24, 'greengray'  : 26,
            'bluegray'   : 29, 'redgray'    : 31,

            'root'       : 12,
            'left'       : 19, 'right'      : 20, 'center'     : 22,
            'up'         : 18, 'aim'        : 21,

            'fk'         : 18,
            'ik'         : 22,
    '''

    if objs:
        pm.select(objs)
    
    objs = pm.selected()

    if not objs: 
        raise

    color = kwargs.get('color', kwargs.get('col', kwargs.get('c', 0)))    
    colorIndex = 0
    #
    # 스트링 형으로 인풋이 들어오면.
    #
    if isinstance( color, (str,unicode) ):

        # 예약된 명령어가 아닐경우 에러.
        if color not in COLORINDEX.keys():
            keywards = [key for key in COLORINDEX.keys()]
            prnt = '", "'.join(keywards)
            print '# select color keyward : ["%s"]'%prnt
            raise

        colorIndex = COLORINDEX[ color.replace(' ','').lower() ]


    #
    # 정수형으로 인풋이 들어오면
    #
    elif isinstance( color, (int,float)):
        colorIndex = int(color)

    # 파이노드로 리캐스팅
    objs = [pm.PyNode(obj) for obj in objs]    

    # 컬러 오버라이드.
    for obj in objs:
        obj.overrideColor.set( colorIndex )

        if color==0: obj.overrideEnabled.set( False )
        else:        obj.overrideEnabled.set( True )

