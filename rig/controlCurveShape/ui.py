# coding=utf-8

import pymel.core as pm
import curveShape

# 고정변수
currentPath     = '/'.join( __file__.split('\\')[:-1] ) + '/'
moduleRoot      = '/'.join( __file__.split('\\')[:-2] ) + '/'
iconPath        = currentPath + 'icon/'
alfredIcon      = iconPath + 'alfredLogo.png'

# 사용자정의변수.
win         = 'controlCurveShapeUI'
title       = 'Control Curve Shape Tools'
labelWidth  = 200
shelf_icon  = iconPath + 'shelf_icon.png'  # 'pythonFamily.png'
shelf_label = ''
shelf_cmd   = 'import rig\nrig.controlCurveShape.ui()'
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
    # Curve Shape -----------------------
        with pm.frameLayout(l='Control Curve Shapes', cll=True, mw=3, mh=3 ):
            with pm.columnLayout(adj=True):

                nc = int( 320 / buttonSize )
                with pm.rowColumnLayout( nc=nc ):
                    wh=buttonSize
                    for key in curveShape.CURVESHAPE.keys():
                        #pm.button(l=key, w=wh, h=wh, c=pm.Callback(curveShape.create, key), annotation=key)
                        #pm.symbolButton( i=iconPath+'ui_thumbnail__%s.png'%key, w=wh, h=wh, c=pm.Callback(curveShape.create, key), annotation=key, bgc=(174.0/255,157.0/255,217.0/255), ebg=True )
                        pm.symbolButton( i=iconPath+'ui_thumbnail__%s.png'%key, w=wh, h=wh, c=pm.Callback(curveShape.create, key), annotation=key  )

                with pm.rowLayout( nc=10 ):
                    pm.text(label=' ', align='right', w=150)
                    pm.button(label='Batch Render Icons', c=pm.Callback( icon_batchRender ), w=118 )
                    pm.button(label='Demo', c=pm.Callback( curveShape.demo ), w=40 )                                    
                
                pm.separator(h=8,style='in')

                with pm.rowLayout( nc=10 ):
                    pm.text(label='Create Curve Text : ', align='right', w=150)
                    pm.button(label='Text', c=pm.Callback( curveShape.createText ), w=160 )

    # Curve Tools -----------------------
        with pm.frameLayout(l='Curve Tools', cll=True, mw=3, mh=3 ):
            with pm.columnLayout(adj=True):

                with pm.rowLayout( nc=10 ):
                    pm.text(label='Print Curve Command : ', align='right', w=150)
                    pm.button(label='Print Command', c=pm.Callback( curveShape.printCurveCommand ), w=160 )

                with pm.rowLayout( nc=10 ):
                    pm.text(label='Curve Command : ', align='right', w=150)
                    pm.button(label='Collapse', c=pm.Callback( curveShape.combine ), w=52 )
                    pm.button(label='Separate', c=pm.Callback( curveShape.separate ), w=52 )
                    pm.button(label='Replace',  c=pm.Callback( curveShape.replace ), w=52)

                with pm.rowLayout(nc=4):
                    pm.text(l='Curve Display : ', w= 150, align='right')
                    pm.button( l='cv',   w= 39, c=pm.Callback( btn_toggleCrvDisp, 'cv'))
                    pm.button( l='ep', w= 39, c=pm.Callback( btn_toggleCrvDisp, 'ep' ))
                    pm.button( l='hull',  w= 39, c=pm.Callback( btn_toggleCrvDisp, 'hull' ))

# ======================================
# Buttons
# ======================================
def icon_batchRender():    
    # 초기 세팅
    if not 'icon_batchRender_ing' in pm.ls():
        # 작업중인 데이터가 있으면, 사용자에게 컨펌 받음.
        _result = pm.confirmDialog( 
            title=u'아이콘 렌더링 화면을 준비합니다', 
            message=u'주의 : 작업중인 데이터가 쑝 날아갑니다.  그래도, 계속 할거에요?', 
            button=['Yes','No'], 
            defaultButton='Yes', 
            cancelButton='No', 
            dismissString='No' 
            )

        # 아니면 중단.
        if _result != "Yes":
            return False
       
        # 새 파일을 만들고
        pm.newFile(f=True)

        pm.setAttr('defaultRenderGlobals.currentRenderer', 'mayaHardware2', type='string')
        pm.setAttr('defaultRenderGlobals.imageFormat', 32) # png
        pm.setAttr('defaultRenderGlobals.enableDefaultLight', 0)

        pm.setAttr('defaultResolution.width',  iconsize)
        pm.setAttr('defaultResolution.height', iconsize)
        pm.setAttr('defaultResolution.deviceAspectRatio', 1)
        
        pm.setAttr('hardwareRenderingGlobals.multiSampleEnable', 1)        
        pm.setAttr('hardwareRenderingGlobals.multiSampleCount', 1 )
        #pm.setAttr('hardwareRenderingGlobals.multiSampleCount', 16 )
        hw = pm.PyNode('hardwareRenderingGlobals')
        #hw.objectTypeFilterNameArray.get()
        #hw.objectTypeFilterValueArray.get()
        hw.objectTypeFilterValueArray.set([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        persp = pm.PyNode('persp')
        persp.translateX.set(1.381)
        persp.translateY.set(7.395)
        persp.translateZ.set(5.797)
        persp.rotateX.set(-45)
        persp.rotateX.set(-60)
        persp.rotateY.set(45)
        persp.rotateZ.set(0)

        crv = curveShape.create( 'cube' )
        pm.viewFit('perspShape', all=True, f=.8 )
        pm.delete(crv)

    #perspShape
    pm.setAttr('perspShape.filmFit', 1)            # 0:fill, 1:Horizontal, 2:Vertical 3:Overscan
    pm.setAttr('perspShape.displayResolution', 1)
    pm.setAttr('perspShape.displayGateMask', 1)
    pm.setAttr('perspShape.overscan', 1.6)
    pm.setAttr('perspShape.focalLength', 200)
    pm.setAttr('perspShape.horizontalFilmAperture', 1)
    pm.setAttr('perspShape.verticalFilmAperture', 1)

    viewFitVal = 0.8
    result = pm.promptDialog(m='viewFit factor : ', text=viewFitVal)    
    if result:    
        text =  pm.promptDialog(q=True, text=True)
        viewFitVal = float(text)

    for name in curveShape.CURVESHAPE.keys():
        crv = curveShape.create( name )        
        pm.select(crv)

        colIndex = 16 # white
        colIndex = 18 # skyBlue
        colIndex =  3 # lightGray
        #curveShape.setColor(col=18)
        #curveShape.setColor(col='gray')
        crv.overrideColor.set( colIndex )
        crv.overrideEnabled.set( True )

        # pm.viewFit(all=True )
        #pm.viewFit('perspShape', all=True,)
        pm.viewFit('perspShape', f=viewFitVal )

        pm.select(cl=True)

        if pm.objExists('grid'):             
            pm.select('grid')
            pm.setAttr('grid.v', 1)
            pm.viewFit(f=.7)
            pm.select(cl=True)
            pm.setAttr('grid.v', 0)        

        # 필요 변수 설정
        renderIconFile = iconPath + 'ui_thumbnail__%s'%name             # 아이콘 렌더링 경로

        # 렌더글로벌 조정 : 파일 이름
        pm.setAttr('defaultRenderGlobals.imageFilePrefix',renderIconFile, type='string')

        # 아이콘 렌더 : 렌더~
        #pm.Mayatomr( preview=True, camera='perspShape', xResolution=self._iconRenderRes, yResolution=self._iconRenderRes )         # 멘탈레이 
        pm.ogsRender( w=iconsize, h=iconsize, enableMultisample=True, camera='persp' )         
        pm.sysFile( renderIconFile+'_tmp.png', rename = renderIconFile+'.png')

        pm.refresh()
        pm.delete(crv)

    # UI 갱신
    ui()

    if pm.objExists('grid'):
        pm.setAttr('grid.v', 1)

    # 샘플 오브젝트 생성
    if not pm.objExists('icon_batchRender_ing'):    
        pm.group(n='icon_batchRender_ing',em=True)

def btn_toggleCrvDisp( typ='cv' ):
    sel = pm.selected()

    if typ=='cv':        
        v = sel[0].dispCV.get()
        for node in sel:
            node.dispCV.set( not v )

    elif typ=='ep':        
        v = sel[0].dispEP.get()
        for node in sel:
            node.dispEP.set( not v )

    elif typ=='hull':        
        v = sel[0].dispHull.get()
        for node in sel:
            node.dispHull.set( not v )