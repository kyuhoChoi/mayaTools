# coding=utf-8
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
import general as mc

# 고정변수
currentPath     = '/'.join( __file__.split('\\')[:-1] ) + '/'
moduleRoot      = '/'.join( __file__.split('\\')[:-2] ) + '/'
documentPath    = '//alfredstorage/Alfred_asset/Maya_Shared_Environment/scripts_Documents/'
iconPath        = currentPath + 'icon/'
alfredIcon      = iconPath + 'alfredLogo.png'

# mem변수
uiMem = []

# 사용자정의변수.
win         = 'motionCaptureWorksflowUI'
title       = 'Motion Capture Workflow'
labelWidth  = 200
shelf_icon  = iconPath + 'shelf_icon.png'  # 'pythonFamily.png'
shelf_label = ''
shelf_cmd   = 'import motionCapture\nmotionCapture.ui()'
shelf_anno  = u'모션캡쳐 워크 플로우.'

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
    import os
    os.system( documentPath + fileName)

#
# 사용자정의 UI.
#
def uiContents():    
    with pm.frameLayout(l='1. Send Motioncapture File', cll=True, mw=3, mh=3, bs='etchedIn'):
        with pm.columnLayout(adj=True):
            pm.text(l=u'모션캡쳐 업체로 보낼 캐릭터파일', h=32)
            pm.button( l='Import MotionCapture Character File', c=pm.Callback( btn_importFile ))

    with pm.frameLayout(l='2. Get Motioncapture File', cll=True, mw=3, mh=3, bs='etchedIn'):
        with pm.columnLayout(adj=True):
            pm.text(l=u'모션캡쳐 업체에서 받은 파일 처리', h=32)
            pm.button( l='Make Asset...', c=pm.Callback( btn_makeAsset ))

    with pm.frameLayout(l='3. Confirm Motion', cll=True, mw=3, mh=3, bs='etchedIn'):
        with pm.columnLayout(adj=True):
            pm.text(l=u'처리된 파일 확인', h=32)                    
            pm.button( l='Create Fallow Camera', c=pm.Callback( btn_createFallowCam ))          
            pm.button( l='Create Preview Grid(10mx10m)', c=pm.Callback( btn_createPreviewGrid ))        
            pm.button( l='Set Clip Range Timeline', c=pm.Callback( btn_setClipRange ))

    with pm.frameLayout(l='4. Motion Blend', cll=True, mw=3, mh=3, bs='etchedIn'):
        with pm.columnLayout(adj=True):
            #pm.text(l=u'motion blend', h=32)
            #pm.button( l='Import Character File for motionblend', c=pm.Callback( btn_importFile ))
            pm.button( l='Motion Blend Setting', c=pm.Callback( btn_openTraxEditor ))

            txt = []
            txt.append( u'    1. Trax Editor > File > Import Animation Clip to Charactoers --> 블렌드할 모션데이터 트렉스로 임포트.')
            txt.append( u'    2. maya scene에서 "Hips" 조인트선택. --> Trax Editor > Edit > Set Clip Ghost Root ')
            txt.append( u'    3. Trax Editor에서 임포트된 클립 선택. --> clip 위에서 오른쪽 마우스 클릭 > Show Clip Ghost' )
            txt.append( u'    4. 블렌드 할 클립들 함께 선택. --> Trax Editor > Create > Blend')
            txt.append( u'    5. 블렌드 작업후 현재 상태로 저장하거나, merge시킨후 모션캡쳐 폴더로 저장. 클립고스트 노드는 삭제권장.')

            pm.text(l= '\n'.join(txt), h=80, al='left')

    with pm.frameLayout(l='Help Tools', cll=True, mw=3, mh=3, bs='etchedIn'):
        with pm.columnLayout(adj=True):
            pm.text(l=u'모션캡쳐 관련툴', h=32)   
            pm.button( l='HIK Character Controls UI...', c=pm.Callback( btn_HIKui ))

def scriptWindow( document ):
    win = pm.window( title='Sniplet', wh=(700,300))
    pm.frameLayout(labelVisible=False, borderVisible=False)
    # -----------------------------------------------
    
    pm.cmdScrollFieldExecuter( sourceType="python", text=document )
    
    # -----------------------------------------------            
    pm.showWindow(win)

def btn_importFile():
    mc.importMocapCharacter()

def btn_createFallowCam():
    mc.createFallowCam()

def btn_createPreviewGrid():
    mc.createPreviewGrid()

def btn_HIKui():
    pm.mel.HIKCharacterControlsTool()

def btn_setClipRange():
    pm.mel.setPlaybackRangeToEnabledClips()

def btn_makeAsset():
    # 명령어
    cmdStr ="""
        #
        # 모션캡쳐 업체에서 받은 파일을 일괄적으로 처리합니다.
        #
        #    1. 모션캡쳐 업체에서 받은 데이터를 animclip으로 변환후 사용자가 지정한 폴더에 저장.
        #    2. 처리된 파일은 레퍼런스로 불러도 타임라인 조정 가능.
        #    3. Trax Editor에서 모션블렌드를 할 수 있도록, 처리된 animclip은 프로젝트셋 clip폴더에 동일한 파일명으로 export.
        #

        import motionCapture as mc
        mc.makeAsset(            
            source_mcDir   = r'Y:\\2015_Nexon_FIFA_Online3\\production\\animation\\motioncapture\\MotionCaptur',   # 모션캡쳐 업체에서 받은파일이 모여있는 폴더
            source_namespace ='',                                                                               # 모션캡쳐 파일에 namespace가 존재 할 경우 네임스페이스를 적을것,
            export_mcDir   = r'Y:\\2015_Nexon_FIFA_Online3\\production\\animation\\motioncapture\\MotionCapture_', # 처리된 파일이 저장될 폴더
            export_clipDir = r'Y:\\2015_Nexon_FIFA_Online3\\production\\animation\\clip',                          # 애니메이션 클립이 저장될 폴더 
            )

        """

    # 들여쓰기 조정
    a = '\n'.join( [ l[8:] for l in cmdStr.split('\n')[1:]] )

    # 한글포한되어 있으므로.. 디코딩해서 프린트
    print a.decode('utf-8')

    scriptWindow( a.decode('utf-8') )

def btn_openTraxEditor():
    #pm.newFile()
    pm.mel.NewScene()
    btn_importFile()
    pm.select('set')
    pm.mel.CharacterAnimationEditor()

    pm.mel.eval('doReload clipEditorPanel1ClipEditor;')
    #pm.mel.eval('doImportClipArgList 4 { "1","1" };')
   
    #pm.select('Hips')
    #pm.clip( 'set', e=True, active='default' )