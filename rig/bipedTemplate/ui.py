# coding=utf-8

import pymel.core as pm
import template as tmp
reload(tmp)

# 고정변수
currentPath     = '/'.join( __file__.split('\\')[:-1] ) + '/'
moduleRoot      = '/'.join( __file__.split('\\')[:-2] ) + '/'
iconPath        = currentPath + 'icon/'
alfredIcon      = iconPath + 'alfredLogo.png'

# 사용자정의변수.
win         = 'bipedTemplateUI'
title       = 'Biped Joint Template'
labelWidth  = 200
shelf_icon  = iconPath + 'shelf_icon.png'  # 'pythonFamily.png'
shelf_label = ''
shelf_cmd   = 'import rig.bipedTemplate\nrig.bipedTemplate.ui()'
shelf_anno  = u'.'

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
    # Joint Layout -----------------------
        with pm.frameLayout(l='Joint Layout', cll=True, mw=3, mh=3 ):
            with pm.columnLayout( adj=True ):

                #with pm.rowLayout(nc=4):
                #    pm.text(l='Joint Template (Biped) : ', w= labelWidth, align='right')
                #    pm.button( l=' Open UI..', w= 160, c=pm.Callback( btn_bipedTemplate ))

                pm.button( l='Import Template Joint', c=pm.Callback( btn_importJoint ))
                pm.button( l='Load Template Joint', c=pm.Callback( btn_loadJoint ))
                pm.separator( h=6, style='in' )
                pm.button( l='Torso', c=pm.Callback( btn_torso ))
                pm.button( l='Head', c=pm.Callback( btn_head ))
                pm.button( l='Arm', c=pm.Callback( btn_arm ))
                pm.button( l='Fingers', c=pm.Callback( btn_fingers ))
                pm.button( l='Leg', c=pm.Callback( btn_leg ))
                pm.button( l='Foot', c=pm.Callback( btn_foot ))
                     
def btn_importJoint():
    reload(tmp)
    tmp.importJoint()

def btn_loadJoint():
    reload(tmp)

    result = pm.promptDialog(m='password : ', text='********')
    if result=='Confirm':
        password = pm.promptDialog(q=True, text=True)
        if password == 'alfred66':
            tmp.loadJoint()

def btn_torso():
    reload(tmp)
    tmp.torso()

def btn_head():
    reload(tmp)
    tmp.head()

def btn_arm():
    reload(tmp)
    tmp.arm()

def btn_fingers():
    reload(tmp)
    tmp.fingers()

def btn_leg():
    reload(tmp)
    tmp.leg()

def btn_foot():
    reload(tmp)
    tmp.foot()