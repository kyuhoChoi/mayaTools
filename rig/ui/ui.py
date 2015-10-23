# coding=utf-8

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
win         = 'alfredRiggingUI'
title       = 'Alfred Rigging Tools'
labelWidth  = 200
shelf_icon  = iconPath + 'shelf_icon.png'  # 'pythonFamily.png'
shelf_label = ''
shelf_cmd   = 'import rig\nrig.ui()'
shelf_anno  = u'리깅 스크립트 모음.'

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
                sti=pm.optionVar['alfredRigTabSel'] if pm.optionVar.has_key('alfredRigTabSel') else 1, 
                cc=self.tabSelect, 
                tabLabel=[(tab1,'Tools'),(tab2,'Transform'),(tab3,'Deformer')]
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

    def tabSelect(self):
        selIndex = pm.tabLayout( self.mid, q=True, sti=True)
        pm.optionVar['alfredRigTabSel'] = selIndex

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
                    pm.button( l=' Open UI..', w= 160, c=pm.Callback( btn_bipedTemplate ))

    # Rigging -----------------------
        with pm.frameLayout(l='Modules', cll=True, mw=3, mh=3 ):
            with pm.columnLayout(adj=True):

                with pm.rowLayout(nc=4):
                    pm.text(l='Create Character Group : ', w= labelWidth, align='right')
                    pm.button( l='Create', w= 160, c=pm.Callback( btn_rigCharacterGrp ))

                with pm.rowLayout(nc=5):
                    pm.text(l='Twist Helper (wip) : ', w= labelWidth, align='right')
                    pm.button( l='Create..', w=160, c=pm.Callback( btn_rigTwistHelper ) )

                with pm.rowLayout(nc=10):
                    pm.text(l=u'Variable FK Rigger 1.0 (ext) : ', w=labelWidth, align='right')
                    pm.button( l='Open UI..', c=pm.Callback( btn_variableFKRigger ), w=160)
                    pm.button(l='d', w=20, c=pm.Callback( pm.launch, web="http://www.creativecrash.com/maya/script/variable-fk-rigger") ) 
                    pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="https://vimeo.com/86643864") )   
                    pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="https://vimeo.com/72424469") ) 
                
                #pm.separator( h=8, style='in')
                
    # Rigging -----------------------
        with pm.frameLayout(l='Tools', cll=True, mw=3, mh=3 ):
            with pm.columnLayout(adj=True):

                with pm.rowLayout(nc=5):
                    pm.text(l='Dynamic Chain Setup Tool (ext) : ', w= labelWidth, align='right')
                    pm.button( l='Open UI..', w=160, c=pm.Callback( btn_dynamicChainSetupTool ) )
                    pm.button(l='d', w=20, c=pm.Callback( pm.launch, web="http://www.rihamtolan.com/blog/2015/1/1/dynamicchainsetuptool-is-here") )
                    pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="https://www.youtube.com/watch?v=1BEAEJ2E01o") )

                with pm.rowLayout(nc=10):
                    pm.text(l=u'Geo Maya Hair 2 (ext) : ', w=labelWidth, align='right')
                    pm.button( l='Open UI..', c=pm.Callback( btn_GMH2 ), w=160)
                    pm.button(l='d', w=20, c=pm.Callback( pm.launch, web="http://www.thundercloud-studio.com/index.php?page=/shop/1.script/0.GMH2/GMH2_manual/") ) 
                    pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="http://www.thundercloud-studio.com/index.php?page=tutorial#GMH2") )

                with pm.rowLayout(nc=10):
                    pm.text(l=u'Alfred Dynamic Joint Chain Tool (wip) : ', w=labelWidth, align='right')
                    pm.button( l='Open UI..', c=pm.Callback( btn_dynamicJointChainTool ), w=160)

def uiContents_tab2():
    # Transform -----------------------
        with pm.frameLayout(l='Transform', cll=True, mw=3, mh=3 ):
            with pm.columnLayout(adj=True):

                with pm.rowLayout(nc=4):
                    pm.text(l='Transform Display : ', w= labelWidth, align='right')
                    pm.button( l='Axis',   w= 39, c=pm.Callback( btn_toggleDisplayAxis ))
                    pm.button( l='Handle', w= 39, c=pm.Callback( btn_toggleDisplayHandle ))

                with pm.rowLayout(nc=4):
                    pm.text(l='Joint Display : ', w= labelWidth, align='right')
                    pm.button( l='Axis',   w= 39, c=pm.Callback( btn_toggleDisplayAxis ))
                    pm.button( l='Handle', w= 39, c=pm.Callback( btn_toggleDisplayHandle ))
                    pm.button( l='Label',  w= 39, c=pm.Callback( btn_toggleJointLabel ))

                with pm.rowLayout(nc=4):
                    pm.text(l='Curve Display : ', w= labelWidth, align='right')
                    pm.button( l='cv',   w= 39, c=pm.Callback( btn_toggleCrvDisp, 'cv'))
                    pm.button( l='ep',   w= 39, c=pm.Callback( btn_toggleCrvDisp, 'ep' ))
                    pm.button( l='hull', w= 39, c=pm.Callback( btn_toggleCrvDisp, 'hull' ))

                with pm.rowLayout(nc=5):
                    pm.text(l='Display Override : ', w= labelWidth, align='right')
                    pm.button( l='Normal',     w=52, c=pm.Callback( btn_displayOverride, typ='normal') )
                    pm.button( l='Template',   w=52, c=pm.Callback( btn_displayOverride, typ='template') )     
                    pm.button( l='Reference',  w=52, c=pm.Callback( btn_displayOverride, typ='reference') )   

                pm.separator( h=8, style='in')
                
                with pm.rowLayout(nc=5):
                    pm.text(l='Control Curve Shape Tools : ', w= labelWidth, align='right')
                    pm.button( l='Open UI..', w=160, c=pm.Callback( btn_controlCurveShape ) )
                                   
                with pm.rowLayout(nc=5):
                    pm.text(l='Set Color : ', w= labelWidth, align='right')
                    pm.button( l='Open UI..', w=160, c=pm.Callback( btn_setColor ) )

                with pm.rowLayout(nc=5):
                    pm.text(l=u'Connect Curve Rig : ', w=labelWidth, align='right')
                    pm.button(l='Create', c=pm.Callback( btn_rigCurveConnect, False ), w=79)
                    pm.button(l='Remove', c=pm.Callback( btn_rigCurveConnect, True ), w=79)
                
                pm.separator( h=8, style='in')

                with pm.rowLayout(nc=5):
                    pm.text(l='Zero Group : ', w= labelWidth, align='right')
                    pm.button( l='Create', w=160, c=pm.Callback( btn_zeroGrp ) )

                with pm.rowLayout(nc=5):
                    pm.text(l='Snap : ',   w= labelWidth, align='right')
                    pm.button( l='point',  w=40, c=pm.Callback( btn_snap, typ='point') )
                    pm.button( l='orient', w=40, c=pm.Callback( btn_snap, typ='orient') )
                    pm.button( l='parent', w=40, c=pm.Callback( btn_snap, typ='parent') )
                    pm.button( l='aim',    w=40, c=pm.Callback( btn_snap, typ='aim') )

                with pm.rowLayout(nc=5):
                    pm.text(l='Locator At : ', w= labelWidth, align='right')
                    pm.button( l='Center', w=79, c=pm.Callback( btn_locAtCenter ) )
                    pm.button( l='Pivot',  w=79, c=pm.Callback( btn_locAtPivot ) )

                with pm.rowLayout(nc=5):
                    pm.text(l='Pivot to : ', w= labelWidth, align='right')
                    pm.button( l='Bottom', w=160, c=pm.Callback( btn_setPivotTobottom ) )

                pm.separator( h=8, style='in')
                
                with pm.rowLayout(nc=5):
                    pm.text(l='Rivet (ext) : ', w= labelWidth, align='right')
                    pm.button( l='Create', w=160, c=pm.Callback( btn_rivet ) )
                    pm.button(l='d', w=20, c=pm.Callback( pm.launch, web="http://www.creativecrash.com/maya/script/rivet-button") )                                       

                with pm.rowLayout(nc=4):
                    pm.text(l='Locator on Curve : ', w= labelWidth, align='right')
                    pm.button( l='R : None', c=pm.Callback( btn_rigLocatorOnCurve, rotate=None ))
                    pm.button( l='R : tangent', c=pm.Callback( btn_rigLocatorOnCurve, rotate='aim' ))
                    pm.button( l='R : orient', c=pm.Callback( btn_rigLocatorOnCurve, rotate='orient' ))

                pm.separator( h=8, style='in')
                
                with pm.rowLayout(nc=5):
                    pm.text(l='Symmetry Transform Rig : ', w= labelWidth, align='right')
                    pm.button( l='Rig (YZ)', w=160, c=pm.Callback( btn_rigSymmetryTransform ) )

                with pm.rowLayout(nc=5):
                    pm.text(l='Create Reverse Transform Ctrl : ', w= labelWidth, align='right')
                    pm.button( l='Create', w=160, c=pm.Callback( btn_createReverseTransform ) )
                    #pm.button(l='t', w=20, c=pm.Callback( excuteWindowFile, r"D:\Users\alfred\Desktop\알아야할 기술들\Rigging_facial\[Lynda.com] Facial Rigging in Maya\VIDEO\03_04_trueface.mp4" ) )
                    pm.button(l='t', w=20, c=pm.Callback( excuteWindowFile, "03_04_trueface.mp4" ) )

    # Attribute -----------------------
        with pm.frameLayout(l='Attribute', cll=True, mw=3, mh=3 ):
            with pm.columnLayout(adj=True):

                with pm.rowLayout(nc=5):
                    pm.text(l='Unhide Hidden Transform Attr : ', w= labelWidth, align='right')
                    pm.button( l='unHide', w=160, c=pm.Callback( btn_unHideTransformAttrs ) )

                pm.separator( h=8, style='in')

                with pm.rowLayout(nc=5, ann='Driver, Driven, Attribute From Channelbox 순으로 선택'):
                    pm.text(l='Connect Attr From Channelbox : ', w= labelWidth, align='right')
                    pm.button( l='Connect',  w=160, c=pm.Callback( btn_connectAttrFromChannelbox ) )

                with pm.rowLayout(nc=5):
                    pm.text(l='Negative Attr Rig : ', w= labelWidth, align='right')
                    pm.button( l='Rig',  w=160, c=pm.Callback( btn_utilRig_negative ) )

    # Joint -----------------------
        with pm.frameLayout(l='Joint', cll=True, mw=3, mh=3 ):
            with pm.columnLayout(adj=True):
                
                with pm.rowLayout(nc=4):
                    pm.text(l='Joint Orient : ', w= labelWidth, align='right')
                    pm.button( l=u'Orient', w= 100, c=pm.Callback( btn_jointOrient, orient=True ), ann=u'joint, [aimObj], upObj 순서로 선택')   
                    pm.button( l=u'None',   w= 60, c=pm.Callback( btn_jointOrient, orient=False ), ann=u'Parent의 Orient를 따라감.')    

                with pm.rowLayout(nc=4):
                    pm.text(l='Joint Chain Orient : ', w= labelWidth, align='right')
                    pm.button( l=u'Parent Y Axis or Polynormal', w= 160, c=pm.Callback( btn_jointChainOrient ) )   

                with pm.rowLayout(nc=5):
                    pm.text(l='Split Joint : ', w= labelWidth, align='right')
                    pm.button( l='Split', w=160, c=pm.Callback(  btn_splitJoint ) )
                
                with pm.rowLayout(nc=5):
                    pm.text(l='Duplicate Joint : ', w= labelWidth, align='right')
                    pm.button( l='Dup Chain',  w=79, c=pm.Callback(  btn_duplicateJointChain ) )
                    pm.button( l='Dup Single', w=79, c=pm.Callback(  btn_duplicateJoints ) )  

    # Curve -----------------------
        with pm.frameLayout(l='Curve', cll=True, mw=3, mh=3 ):
            with pm.columnLayout(adj=True):

                with pm.rowLayout(nc=10):
                    pm.text(l=u'Create Linked Curve : ', w=labelWidth, align='right')
                    pm.button( l='Create', c=pm.Callback( btn_createLinkedCrv ), w=160)

                with pm.rowLayout(nc=10):
                    pm.text(l=u'Create Middle Curve : ', w=labelWidth, align='right')
                    pm.button( l='Create', c=pm.Callback( btn_createMiddleCrv ), w=160) 

                with pm.rowLayout(nc=10):
                    pm.text(l=u'Create towPointArc Rig : ', w=labelWidth, align='right')
                    pm.button( l='Create', c=pm.Callback( btn_createTwoPointArcCrv ), w=160) 

def uiContents_tab3():
    # Skinning -----------------------
        with pm.frameLayout(l='Skninning', cll=True, mw=3, mh=3 ):
            with pm.columnLayout(adj=True):

                with pm.rowLayout(nc=5):
                    pm.text(l=u'Set Weight : ', w=labelWidth, align='right')
                    w= 155 / 4
                    pm.button(l='1.00', c=pm.Callback( btn_setWeight, 1.0 ), w=w)
                    pm.button(l='0.75', c=pm.Callback( btn_setWeight, 0.75 ), w=w)
                    pm.button(l='0.50', c=pm.Callback( btn_setWeight, 0.5 ), w=w)
                    pm.button(l='0.25', c=pm.Callback( btn_setWeight, 0.25 ), w=w)                                
                
                with pm.rowLayout(nc=5, ann=u'skinCluster가 적용된 오브젝트를 선택하고 실행'):
                    pm.text(l=u'Select Influences : ', w=labelWidth, align='right')
                    pm.button( l='Select', w=160, c=pm.Callback( btn_getInfluences ))
                
                with pm.rowLayout(nc=5, ann=u'skinCluster가 적용된 오브젝트를 선택하고 실행'):
                    pm.text(l=u'Transfer Weight : ', w=labelWidth, align='right')
                    pm.button( l=u'vtxs, inf1, inf2 순으로선택', w=160, c=pm.Callback( pm.mel.MoveInfluence ))                    
                
                with pm.rowLayout(nc=5, ann=u'skinCluster가 적용된 여러 오브젝트를 먼저 선택. \n마지막에 skinMesh선택하고 실행'):
                    pm.text(l=u'Multi Copy Skin Weights : ', w=labelWidth, align='right')
                    pm.button( l='Copy Weight', w=160, c=pm.Callback( btn_multiCopySkinWeights ))  

    # Blendshape -----------------------
        with pm.frameLayout(l='Blendshape', cll=True, mw=3, mh=3 ):
            with pm.columnLayout(adj=True):

                with pm.columnLayout(adj=True):
                    with pm.rowLayout(nc=10):
                        pm.text(l=u'Split Blendshape (ext) : ', w=labelWidth, align='right')
                        pm.button( l='Create', c=pm.Callback( btn_splitBlendShape ), w=160)
                        pm.button(l='d', w=20, c=pm.Callback( pm.launch, web="http://www.jeffrosenthal.org/split-blendshape-script") )
                        pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="https://www.youtube.com/watch?v=-JwXfnrX1wM") )  

                    with pm.rowLayout(nc=10):
                        pm.text(l=u'Mirror Blendshape (ext) : ', w=labelWidth, align='right')
                        pm.button( l='Open UI..', c=pm.Callback( btn_mirrorBlendshape ), w=160)
                        pm.button(l='d', w=20, c=pm.Callback( pm.launch, web="http://www.creativecrash.com/maya/script/mirror-blendshapes") ) 
                        #pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="https://www.youtube.com/watch?v=-JwXfnrX1wM") )   

                    with pm.rowLayout(nc=10):
                        pm.text(l=u'Corrective Blendshape Creator (ext) : ', w=labelWidth, align='right')
                        pm.button( l='Open UI..', c=pm.Callback( btn_correctiveBlendshapeCreator ), w=160)
                        pm.button(l='d', w=20, c=pm.Callback( pm.launch, web="http://www.creativecrash.com/maya/script/46275/download_page") ) 
                        pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="https://www.youtube.com/watchdv=0yuzPJTy3y0&index=6&list=PL4ZR92iL9G0FEcJI80PADVpzKypQv50Lp") )                                         

                    with pm.rowLayout(nc=10):
                        pm.text(l=u'Extract Deltas (ext) : ', w=labelWidth, align='right')
                        pm.button(l='DupMesh', c=pm.Callback( btn_extractDeltasDuplicateMesh ), w=79)
                        pm.button(l='Perform', c=pm.Callback( btn_performExtractDeltas ), w=79)
                        pm.button(l='d', w=20, c=pm.Callback( pm.launch, web="http://www.braverabbit.de/playground/dp=443") ) 
                        pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="https://www.youtube.com/watch?v=YvNdYseSNFs") )
     
# ======================================
# Buttons
# ======================================

def btn_bipedTemplate():
    import rig.bipedTemplate as bp
    #from rig.bipedTemplate import ui
    bp.ui()
    #reload(..bipedTemplate)
    #..bipedTemplate.ui()

def btn_rigCharacterGrp():
    import rig.rigModule as mdl
    reload(mdl)
    mdl.rigCharacterGrp()

def btn_rigLocatorOnCurve(**kwargs):
    import rig.rigModule as mdl
    reload(mdl)

    mdl.locatorOnCurve( **kwargs )     # 로테이션 리깅은 안. 제일 빠름.
    #LocatorOnCurve( curve, parameter=3.0, rotate='orient' ) # 로테이션(Orient)은 커브의 트랜스폼을 사용.
    #LocatorOnCurve( curve, parameter=2.0, rotate='aim' )    # 로테이션(aim)  worldUpType을 명시하지 않을경우, aim은 커브의 tangent crv의 rotation을 up으로 사용
    #LocatorOnCurve( curve, parameter=0.5, rotate='aim', worldUpType='object', worldUpObject=upLoc )

    l=[]
    l.append('import rig.rigLocatorOnCurve as locOnCrv')
    l.append('locOnCrv.locatorOnCurve(%s)'%kwargs)

def btn_rigTwistHelper():
    import rig.rigTwistHelper as tw
    reload(tw)

    result = pm.promptDialog(m='Prefix : ', text=uiMem[3])
    if result=='Confirm':
        prefix = pm.promptDialog(q=True, text=True)
        uiMem[3] = prefix
        tw.rigTwistHelper( prefix=prefix, divide=4 )

def btn_variableFKRigger():
    import rig.variableFKRigger as mdl
    reload(mdl)
    mdl.UI()
    # 	jo_varFk.UI()
        
def btn_displayOverride( typ='normal' ):
    sel = pm.selected()

    if typ=='normal':
        for node in sel:
            node.overrideEnabled.set(False)
            node.overrideDisplayType.set(0) # Normal

    elif typ=='template':
        for node in sel:
            node.overrideEnabled.set(True)
            node.overrideDisplayType.set(1) # Template

    elif typ=='reference':
        for node in sel:
            node.overrideEnabled.set(True)
            node.overrideDisplayType.set(2) # Reference

def btn_GMH2():
    pm.mel.source("THUNDERCLOUD/GMH2/GMH2_starter.mel")

def btn_dynamicJointChainTool():
    import rig.dynamicJointChainTool as jc
    reload(jc)
    jc.ui()

#
# Attribute
#
def btn_connectAttrFromChannelbox():
    import rig.attribute as attr
    reload(attr)
    attr.connectAttrFromChannelbox()      

def btn_unHideTransformAttrs():
    import rig.attribute as attr
    attr.unHideTransformAttrs()    

def btn_utilRig_negative():
    import rig.attribute as attr
    attr.utilRig_negative()

#
# Blendshape
#
def btn_splitBlendShape():
    import rig.blendshape.splitBlendShape as bs
    reload(bs)
    bs.splitBlendShape()

def btn_mirrorBlendshape():
    pm.mel.source(moduleRoot + 'blendshape/mp_mirrorBlendshapesUI.mel')
    #print moduleRoot + 'blendshape/mp_mirrorBlendshapesUI.mel'

def btn_correctiveBlendshapeCreator():
    import rig.blendshape.correctiveBlendshapeCreator as correct
    correct.showCorrectiveBlendshapeWindow()
    
def btn_extractDeltasDuplicateMesh():
    if not pm.pluginInfo('extractDeltas', q=True, l=True):
        pm.loadPlugin(moduleRoot + 'blendshape/extractDeltas/plug-ins/extractDeltas.py')

    pm.mel.extractDeltasDuplicateMesh()

def btn_performExtractDeltas():
    if not pm.pluginInfo('extractDeltas', q=True, l=True):
        pm.loadPlugin(moduleRoot + 'blendshape/extractDeltas/plug-ins/extractDeltas.py')

    pm.mel.performExtractDeltas()

#
# Transform
#
def btn_zeroGrp():
    import rig.transform as tr
    tr.zeroGroup()

def btn_snap( typ='parent' ):
    import rig.transform as tr
    tr.snap( type=typ )

def btn_rivet():
    pm.mel.source( moduleRoot + 'transform/rivet.mel')
    print "rivet()"
    #pm.mel.rivet()

def btn_locAtCenter():
    import rig.transform as tr
    tr.locAtCenter()

def btn_locAtPivot():
    import rig.transform as tr
    tr.locAtPivot()

def btn_setPivotTobottom():
    import rig.transform as tr
    tr.setPivotTobottom()

def btn_rigSymmetryTransform():
    import rig.transform as tr
    tr.rigSymmetryTransform()

def btn_createReverseTransform():
    import rig.transform as tr
    reload(tr)

    result = pm.promptDialog(m='Prefix : ', text=uiMem[2])
    if result=='Confirm':
        prefix = pm.promptDialog(q=True, text=True)
        uiMem[1] = prefix
        tr.createReverseTransform( prefix=prefix )

#
# Joint
#
def btn_toggleDisplayAxis():
    import rig.joint
    reload(rig.joint)

    rig.joint.toggleDisplayAxis()

def btn_toggleDisplayHandle():
    import rig.joint
    reload(rig.joint)

    rig.joint.toggleDisplayHandle()

def btn_toggleJointLabel():
    import rig.joint
    reload(rig.joint)

    rig.joint.toggleJointLabel()

def btn_splitJoint():
    import rig.joint
    reload(rig.joint)
    
    sel = pm.selected( type='joint' )
    if not sel:
        raise

    sd = input()
    if not sd:
        raise

    rig.joint.splitJoint( sel[0], sd )

def btn_duplicateJoints():
    import rig.joint
    reload(rig.joint)

    rig.joint.duplicateJoints()

def btn_duplicateJoints():
    import rig.joint
    reload(rig.joint)

    rig.joint.duplicateJoints()

def btn_duplicateJointChain():
    import rig.joint
    reload(rig.joint)

    rig.joint.duplicateJointChain()

def btn_jointOrient( orient=True ):
    import rig.joint
    reload(rig.joint)
    
    rig.joint.jntOrient(orient=orient)

    l = []
    l.append(u"# ---------------------------------")
    l.append(u"import rig")
    l.append(u"rig.joint.jntOrient( objs=[], orient=True, aimAxis='x', upAxis='y', worldAimVector='x', worldUpVector='y', worldUpType='scene') # 사용법")
    l.append(u"rig.joint.jntOrient() # 조인트 오리엔트")
    l.append(u"rig.joint.jntOrient(orient=None) # 조인트오리엔트 리셋")
    l.append(u"# ---------------------------------")
    print '\n'.join(l)

def btn_jointChainOrient():
    import rig.joint
    reload(rig.joint)
    
    rig.joint.jointChainOrient()

#
# Skinning
#
def btn_multiCopySkinWeights():    
    '''skinCluster가 적용된 여러 오브젝트를 먼저 선택. 마지막에 skinMesh선택하고 실행'''
    cmdStr = []
    cmdStr.append('import rig.skinning')
    cmdStr.append('rig.skinning.copySkinWeights()')
    print '\n'.join(cmdStr)    

    import rig.skinning as skin
    skin.copySkinWeights()

def btn_setWeight( val=1 ):
    cmdStr = []
    cmdStr.append('import pymel.core as pm')
    cmdStr.append('import rig.skinning')
    cmdStr.append('rig.skinning.setWeight( pm.selected(), %s )'% val )
    print '\n'.join(cmdStr)

    import rig.skinning
    rig.skinning.setWeight( pm.selected(), val )

def btn_getInfluences():
    cmdStr = []
    cmdStr.append('import rig.skinning')
    cmdStr.append('rig.skinning.getInfluences()')
    print '\n'.join(cmdStr)

    import rig.skinning as skin
    skin.getInfluences()

#
# Ctrl
#
def btn_rigCurveConnect( val ):
    import rig.rigModule as mdl
    reload(mdl)
    '''skinCluster가 적용된 여러 오브젝트를 먼저 선택. 마지막에 skinMesh선택하고 실행'''
    mdl.rigCurveConnect( pm.selected(), delete=val )

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

def btn_controlCurveShape():
    import rig.controlCurveShape
    reload(rig.controlCurveShape)
    rig.controlCurveShape.ui()

def btn_setColor():
    import rig.setColor
    reload(rig.setColor)
    rig.setColor.ui()

#
# dynamic
#
def btn_dynamicChainSetupTool():
    import rig.dynamicChainSetupTool
    from dynamicChainSetupTool import dynamicChainSetup as dc
    dc.show()

#
# Curve -----------------------
#
def btn_createLinkedCrv():
    import rig.curve as crv
    crv.createLinkedCrv()

def btn_createMiddleCrv():
    import rig.curve as crv
    crv.createMiddleCrv()

def btn_createTwoPointArcCrv():
    import rig.curve as crv

    result = pm.promptDialog(m='Prefix : ', text=uiMem[3])
    if result=='Confirm':
        prefix = pm.promptDialog(q=True, text=True)
        uiMem[4] = prefix
        crv.twoPointArcRig( prefix=prefix )

