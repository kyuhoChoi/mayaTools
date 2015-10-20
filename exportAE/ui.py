# coding=utf-8
#
# Author : Kyuho Choi
#
# Description :
#   마야와 애프트이펙트 간에 카메라, 널 교환
#
# History : 
#   2015-10-06 : LG VR작업용으로 작성
#

#
# ma 익스포트
# newScene
# ma 임포트
# 화면 맞춤
# 프레임레이트 맞춤
# 타임레인지 맞춤
# ma로 덮어씀
#

import pymel.core as pm
import maya.cmds as cmds

# 고정변수
currentPath     = '/'.join( __file__.split('\\')[:-1] ) + '/'
moduleRoot      = '/'.join( __file__.split('\\')[:-2] ) + '/'
documentPath    = '//alfredstorage/Alfred_asset/Maya_Shared_Environment/scripts_Documents/'
iconPath        = currentPath + 'icon/'
alfredIcon      = iconPath + 'alfredLogo.png'

# mem변수
uiMem = [10,'jiggle','upperLip','upperArm','arc01']

# 사용자정의변수.
win         = 'exportToAeUI'
title       = 'Export To AE Tools'
labelWidth  = 200
shelf_icon  = iconPath + 'shelf_icon.png'  # 'pythonFamily.png'
shelf_label = ''
shelf_cmd   = 'import exportAE\nexportAE.ui()'
shelf_anno  = u'Export To After Effect Tools.'

# ======================================
#
# window : version 2015-04-29
#
# ======================================
class UI(object):
    def __init__(self):
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
                    #with pm.tabLayout(tv=False, scr=True, childResizable=True) as mid:   
                    with pm.tabLayout(tv=True, scr=True, childResizable=True ) as self.mid:  
                        with pm.columnLayout(adj=True) as tab1:
                            uiContents_tab1()
                        
                        with pm.columnLayout(adj=True) as tab2:
                            uiContents_tab2()

                        with pm.columnLayout(adj=True) as tab3:
                            uiContents_tab3()

                    # 하단
                    with pm.columnLayout(adj=True) as btm:
                        pm.helpLine()
       
            # 팝업메뉴
            # 왼쪽 마우스 클릭
            pm.popupMenu(button=1, p=top)
            pm.menuItem(l='Add To Shelf',  c=pm.Callback( self.addToShalf ) )

            # 오른쪽 마우스 클릭
            pm.popupMenu(button=3, p=top)
            pm.menuItem(l='Help', en=False )
            
            # 탭 조정
            pm.tabLayout(self.mid, e=True, 
                sti=pm.optionVar[win] if pm.optionVar.has_key(win) else 1, 
                cc=self.tabSelect, 
                tabLabel=[
                    (tab1,'Tools'),
                    (tab2,'Transform'),
                    (tab3,'Deformer')
                    ]
                )
            
            # 폼조정
            pm.formLayout( mainForm, e=True, 
                attachForm=[
                    (top, 'top', 3), 
                    (top, 'left', 3), 
                    (top, 'right', 3), 

                    (self.mid, 'left', 3), 
                    (self.mid, 'right', 3), 

                    (btm, 'left', 3), 
                    (btm, 'right', 3), 
                    (btm, 'bottom', 3),
                    ], 
                attachControl=[
                    (self.mid, 'top', 3, top), 
                    (self.mid, 'bottom', 0, btm)
                    ],
                )

    def addToShalf(self):
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
                label=title,                          # 타이틀
                imageOverlayLabel=shelf_label,        # 라벨 (5글자 이하)
                font="smallPlainLabelFont",
                # "boldLabelFont", "smallBoldLabelFont", "tinyBoldLabelFont", "plainLabelFont", "smallPlainLabelFont", "obliqueLabelFont", "smallObliqueLabelFont", "fixedWidthFont", "smallFixedWidthFont".
                #overlayLabelColor     = (1, 1, .25), 
                overlayLabelBackColor=(0, 0, 0, 0),  #(.15, .9, .1, .4),
                annotation=shelf_anno,                # 참조글 
                sourceType='python',
                command=shelf_cmd,                    # 명령어
                doubleClickCommand='',
                parent=currentShelfTab,
            )

    def tabSelect(self):
        selIndex = pm.tabLayout( self.mid, q=True, sti=True)
        pm.optionVar[win] = selIndex

def ui(): UI()

def excuteWindowFile( fileName ):
    import os
    os.system( documentPath + fileName)

#
# 사용자정의 UI.
#
def uiContents_tab1():
    # Joint Layout -----------------------
        with pm.frameLayout(l='Auto Rigging', cll=True, mw=3, mh=3 ):
            with pm.columnLayout( adj=True ):

                with pm.rowLayout(nc=4):
                    pm.text(l='Joint Template (Biped) : ', w= labelWidth, align='right')
                    pm.button( l=' Open UI..', w= 160, c=pm.Callback( btn_tmp ))

    # Rigging -----------------------
        with pm.frameLayout(l='Modules', cll=True, mw=3, mh=3 ):
            with pm.columnLayout(adj=True):

                with pm.rowLayout(nc=4):
                    pm.text(l='Create Character Group : ', w= labelWidth, align='right')
                    pm.button( l='Create', w= 160, c=pm.Callback( btn_tmp ))

                with pm.rowLayout(nc=5):
                    pm.text(l='Twist Helper (wip) : ', w= labelWidth, align='right')
                    pm.button( l='Create..', w=160, c=pm.Callback( btn_tmp ) )

                with pm.rowLayout(nc=10):
                    pm.text(l=u'Variable FK Rigger 1.0 (ext) : ', w=labelWidth, align='right')
                    pm.button( l='Open UI..', c=pm.Callback( btn_tmp ), w=160)
                    pm.button(l='d', w=20, c=pm.Callback( pm.launch, web="http://www.creativecrash.com/maya/script/variable-fk-rigger") ) 
                    pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="https://vimeo.com/86643864") )   
                    pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="https://vimeo.com/72424469") ) 
                
                #pm.separator( h=8, style='in')

def uiContents_tab2():
    with pm.frameLayout(l='Auto Rigging', cll=True, mw=3, mh=3 ):
        with pm.columnLayout( adj=True ):
            pm.button()

def uiContents_tab3():
    with pm.frameLayout(l='Auto Rigging', cll=True, mw=3, mh=3 ):
        with pm.columnLayout( adj=True ):
            pm.button()

def btn_tmp():
    print 'btnClick'