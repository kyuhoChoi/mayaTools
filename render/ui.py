# coding=utf-8
#
# Author : Kyuho Choi
#
# Description :
#   
#
# History : 
#   2015-10-21 : 
#

import pymel.core as pm

# 고정변수
documentPath    = '//alfredstorage/Alfred_asset/Maya_Shared_Environment/scripts_Documents/'
currentPath     = '/'.join( __file__.split('\\')[:-1] ) + '/'
moduleRoot      = '/'.join( __file__.split('\\')[:-2] ) + '/'
iconPath        = currentPath + 'icon/'
alfredIcon      = iconPath + 'alfredLogo.png'

# 사용자정의변수.
win         = 'alfredRenderHelpToolsUI'
title       = 'Alfred Render Help Tools'
labelWidth  = 200

shelf_icon  = iconPath + 'shelf_icon.png'  # 'pythonFamily.png'
shelf_label = ''
shelf_cmds = []
shelf_cmds.append('import render')
shelf_cmds.append('render.ui()')
shelf_cmd   = '\n'.join(shelf_cmds)
shelf_anno  = u'Render 도구 모음'

# ======================================
#
# window : version 2015-04-29
# 이부분은 건드리지 않아도 됨.
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
                   
                    #
                    # Contents start ===========================================================
                    # 중단
                    with pm.tabLayout(tv=False, scr=True, childResizable=True) as self.mid:
                        #with pm.columnLayout(adj=True):
                        with pm.frameLayout( lv=False, cll=False, mw=3, mh=3, bv=False):
                            uiContents()

                    #
                    # Contents end =============================================================
                    #
                    
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
    '''
    윈도우에서 파일 자동 실행
    '''
    import os
    os.system( documentPath + fileName)

def scriptWindow( document ):
    '''
    스크립트 윈도우 열기
    '''
    win = pm.window( title='Sniplet', wh=(700,300))
    pm.frameLayout(labelVisible=False, borderVisible=False)
    # -----------------------------------------------
    
    pm.cmdScrollFieldExecuter( sourceType="python", text=document )
    
    # -----------------------------------------------            
    pm.showWindow(win)

# ======================================
#
# 사용자정의 UI.
# 상태에 맞게 조정할것.
#
# ======================================
def uiContents():
    with pm.frameLayout(l='Preview Render', cll=True, mw=3, mh=3, bs='etchedIn'):
        with pm.columnLayout(adj=True):
            with pm.rowLayout(nc=10):
                pm.text(l='Create Camera Solid BG : ', w= labelWidth, align='right')
                pm.button( l='Create', w= 160, c=pm.Callback( btn_createCamSolidBG ))

            with pm.rowLayout(nc=4):
                pm.text(l='Save All RenderView Images : ', w= labelWidth, align='right')
                pm.button( l='Save', w= 160, c=pm.Callback( btn_saveAllRenderViewImages ))

    with pm.frameLayout(l='Render', cll=True, mw=3, mh=3, bs='etchedIn'):
        with pm.columnLayout( adj=True ):
            with pm.rowLayout(nc=4):
                pm.text(l='Backburner Script : ', w= labelWidth, align='right')
                pm.button( l='Open UI..', w= 160, c=pm.Callback( btn_backburnner ))

def btn_createCamSolidBG():
    import general as mdl
    reload(mdl)
    mdl.createCamSolidBG()

def btn_saveAllRenderViewImages():
    import general as mdl
    reload(mdl)
    mdl.saveAllRenderViewImages()

def btn_backburnner():
    import render.backburnerTools as bb
    reload(bb)
    bb.ui()
    