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

# 고정변수
documentPath    = '//alfredstorage/Alfred_asset/Maya_Shared_Environment/scripts_Documents/'
currentPath     = '/'.join( __file__.split('\\')[:-1] ) + '/'
moduleRoot      = '/'.join( __file__.split('\\')[:-2] ) + '/'
iconPath        = currentPath + 'icon/'
alfredIcon      = iconPath + 'alfredLogo.png'

# 사용자정의변수.
win         = 'exportToAEUI'
title       = 'Export to After Effects'
labelWidth  = 200

shelf_icon  = iconPath + 'shelf_icon.png'  # 'pythonFamily.png'
shelf_label = ''
shelf_cmds = []
shelf_cmds.append('import sceneAssembly.exportAE as exportAE')
shelf_cmds.append('exportAE.ui()')
shelf_cmd   = '\n'.join(shelf_cmds)
shelf_anno  = u'애프터 이펙트로 널 내보냄.'

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
    with pm.frameLayout(l='Export To AE Tools', cll=True, mw=3, mh=3, bs='etchedIn'):
        with pm.columnLayout(adj=True):
            with pm.rowLayout(nc=10):
                pm.text(l='Create Static Null : ', w=labelWidth, align='right')
                pm.button(l='Select Transform and Excute', c=pm.Callback( btn_createStaticNull ), w=160)
                #pm.button(l='d', w=20, c=pm.Callback( pm.launch, web="http://www.braverabbit.de/playground/dp=443") ) 
                #pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="https://www.youtube.com/watch?v=YvNdYseSNFs") )
                #pm.button(l='t', w=20, c=pm.Callback( excuteWindowFile, 'alembicExporter.flv') )
            with pm.rowLayout(nc=10):
                pm.text(l='Create Active Null : ', w=labelWidth, align='right')
                pm.button(l='Select Transform and Excute', c=pm.Callback( btn_createActiveNull ), w=160)
                #pm.button(l='d', w=20, c=pm.Callback( pm.launch, web="http://www.braverabbit.de/playground/dp=443") ) 
                #pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="https://www.youtube.com/watch?v=YvNdYseSNFs") )
                #pm.button(l='t', w=20, c=pm.Callback( excuteWindowFile, 'alembicExporter.flv') )
            with pm.rowLayout(nc=10):
                pm.text(l='Create aeCamera : ', w=labelWidth, align='right')
                pm.button(l='Select Camera and Excute', c=pm.Callback( btn_createAECam ), w=160)
                #pm.button(l='d', w=20, c=pm.Callback( pm.launch, web="http://www.braverabbit.de/playground/dp=443") ) 
                #pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="https://www.youtube.com/watch?v=YvNdYseSNFs") )
                #pm.button(l='t', w=20, c=pm.Callback( excuteWindowFile, 'alembicExporter.flv') )

    with pm.frameLayout(l='Support Tools', cll=True, mw=3, mh=3, bs='etchedIn'):
        with pm.columnLayout(adj=True):
            with pm.rowLayout(nc=10):
                pm.text(l='PrimaryVis : ', w=labelWidth, align='right')
                pm.button(l='OFF', c=pm.Callback( btn_primaryVisibilityOff ), w=160)
                #pm.button(l='d', w=20, c=pm.Callback( pm.launch, web="http://www.braverabbit.de/playground/dp=443") ) 
                #pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="https://www.youtube.com/watch?v=YvNdYseSNFs") )
                #pm.button(l='t', w=20, c=pm.Callback( excuteWindowFile, 'alembicExporter.flv') )

def btn_createStaticNull():
    sel = pm.ls( sl=True, type='transform' )
    for node in sel:
        loc = pm.spaceLocator()
        pm.delete( pm.parentConstraint(node,loc) )
        loc.rename( 'null_' + node.name() )

def btn_createActiveNull():
    sel = pm.ls( sl=True, type='transform' )

    nulls = []
    const = []
    for node in sel:
        loc = pm.spaceLocator()
        nulls.append( loc )    
       
        const.append( pm.pointConstraint(node,loc) )  
        const.append( pm.orientConstraint(node,loc) )
        
        loc.rename( 'null_' + node.name() )    

    pm.select( nulls )
    pm.mel.BakeSimulationOptions()

    # pm.select( const )
    # pm.delete( const )

def btn_createAECam():
    sel = pm.ls(sl=True, type='transform')
    if sel:
        if not pm.nodeType( sel[0].getShape() ) == 'camera':
            raise 
            
    consts = []
    camTrn = sel[0]
    camShp = sel[0].getShape()

    aeCamTrn = pm.duplicate( camTrn )[0]
    aeCamShp = aeCamTrn.getShape()
    aeCamTrn.rename('afterEffectCam#')

    consts.append( pm.parentConstraint( camTrn, aeCamTrn ) )
    camShp.focalLength >> aeCamShp.focalLength

    # pm.mel.BakeSimulationOptions()  
    # pm.select( const )
    # pm.delete( const )
    pm.bakeResults(
        aeCamTrn, 
        simulation=True,
        t="%d:%d"%( pm.playbackOptions(q=True, min=True), pm.playbackOptions(q=True, max=True)),
        sampleBy=1, 
        disableImplicitControl=True,
        preserveOutsideKeys=True,
        sparseAnimCurveBake=False,
        removeBakedAttributeFromLayer=False,
        removeBakedAnimFromLayer=False,
        bakeOnOverrideLayer=False,
        minimizeRotation=True,
        controlPoints=False,
        shape=True
        )
        
    aeCamShp.filmFit.set(2) # vertical
    pm.delete( consts )
    pm.select( aeCamTrn )

def btn_primaryVisibilityOff():
    for node in pm.selected(o=True):
        node.primaryVisibility.set(0)