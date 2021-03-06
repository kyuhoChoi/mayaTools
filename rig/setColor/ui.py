# coding=utf-8

import pymel.core as pm
import setColor

# 고정변수
currentPath     = '/'.join( __file__.split('\\')[:-1] ) + '/'
moduleRoot      = '/'.join( __file__.split('\\')[:-2] ) + '/'
iconPath        = currentPath + 'icon/'
alfredIcon      = iconPath + 'alfredLogo.png'

# 사용자정의변수.
win         = 'colorUI'
title       = 'Set Color'
labelWidth  = 200
shelf_icon  = iconPath + 'shelf_icon.png'   # 'pythonFamily.png'
shelf_label = ''
shelf_cmd   = 'import rig\nrig.setColor.ui()'
shelf_anno  = u'리깅 스크립트 모음.'

iconsize   = 50
buttonSize = iconsize + 2

# ======================================
#
# window : version 2015-04-28
#
# ======================================
def ui():
    '''
    update : 2015-04-28
    '''
    if pm.window(win, q=True, exists=True ): 
        pm.deleteUI(win)

    with pm.window(win, wh=[300,600], t=title):
        with pm.frameLayout( lv=False, cll=False, mw=1, mh=1):
            with pm.formLayout() as mainForm:

                # 상단 
                with pm.tabLayout(tv=False) as top:
                    with pm.frameLayout(lv=False, cll=False, mw=2, mh=2, bv=False):
                        with pm.rowLayout(nc=3, adj=2):
                            pm.image( image = shelf_icon )
                            pm.text(l='  %s'%title, fn='boldLabelFont', align='left')
                            pm.image( image = alfredIcon )
               
                # 중단
                with pm.tabLayout(tv=False, scr=True, childResizable=True) as mid:                  
                    with pm.columnLayout(adj=True):
                        uiContents()

                # 하단
                with pm.columnLayout(adj=True) as btm:
                    pm.helpLine()
   
        # 팝업메뉴
        # 왼쪽 마우스 클릭
        pm.popupMenu(button=1, p=top)
        pm.menuItem(l='Add To Shelf',  c=pm.Callback( addToShalf ) )

        # 오른쪽 마우스 클릭
        pm.popupMenu(button=3, p=top)
        pm.menuItem(l='Help', en=False )
        
        # 폼조정
        pm.formLayout( mainForm, e=True, 
            attachForm=[
                (top, 'top', 3), 
                (top, 'left', 3), 
                (top, 'right', 3), 

                (mid, 'left', 3), 
                (mid, 'right', 3), 

                (btm, 'left', 3), 
                (btm, 'right', 3), 
                (btm, 'bottom', 3),
                ], 
            attachControl=[
                (mid, 'top', 3, top), 
                (mid, 'bottom', 0, btm)
                ],
            )

def addToShalf():
    '''
    update : 2015-04-28
    '''

    # 현재 쉐프탭 이름 알아옴.
    currentShelfTab = pm.shelfTabLayout( pm.melGlobals['gShelfTopLevel'], q=True, selectTab=True )

    # 생성
    if True:
        pm.shelfButton(
            commandRepeatable=True,
            image1=shelf_icon,                    # 아이콘
            width=32,
            height=32,
            label=title,                         # 타이틀
            imageOverlayLabel=shelf_label,        # 라벨 (5글자 이하)
            font="smallPlainLabelFont",
            # "boldLabelFont", "smallBoldLabelFont", "tinyBoldLabelFont", "plainLabelFont", "smallPlainLabelFont", "obliqueLabelFont", "smallObliqueLabelFont", "fixedWidthFont", "smallFixedWidthFont".
            #overlayLabelColor     = (1, 1, .25), 
            overlayLabelBackColor=(0, 0, 0, 0),  #(.15, .9, .1, .4),
            annotation=shelf_anno,          # 참조글 
            sourceType='python',
            command=shelf_cmd,                # 명령어
            doubleClickCommand='',
            parent=currentShelfTab,
        )

#
# 사용자정의 UI.
#
def uiContents():
    with pm.frameLayout(l='Color', cll=True, mw=3, mh=3 ):
        with pm.columnLayout(adj=True):

            with pm.rowLayout(nc=2):
                pm.text(label='Set Override Color : ', align='right', w=130)
                with pm.rowColumnLayout( nc=10 ):
                    wh=18
                    for i in range(0,32):
                        rgb = (0,0,0)
                        if i == 0:
                            rgb  = (0.5,0.5,0.5)
                            anno = 'Reset'
                            pm.symbolButton( i=iconPath+'ui_colorNone.png', annotation=anno, w=wh, h=wh, c=pm.Callback( setColor.setColor, color=i ) )

                        else:
                            rgb  = pm.colorIndex( i, q=True )
                            anno = '- index : %d\n- RGB : %03.3f %03.3f %03.3f\n- name : %s'%(i, rgb[0], rgb[1], rgb[2], setColor.color_intToStr(i) )

                            pm.canvas(
                                rgbValue   = rgb,
                                annotation = anno,
                                w=wh, h=wh,
                                pressCommand = pm.Callback( setColor.setColor, color=i )
                                ) #partial( self.setColor, i, True , self._toShape)) #partial( self.setColor, i, False, False))

            pm.separator(h=8,style='in')
            with pm.rowLayout( nc=10 ):
                pm.text(label='Set Wire Frame Color : ', align='right', w=130)
                pm.button(label='Object Color Palette', c=pm.Callback( pm.mel.objectColorPalette ), w=180 )

# ======================================
# Buttons
# ======================================