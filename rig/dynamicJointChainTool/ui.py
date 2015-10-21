# coding=utf-8

import pymel.core as pm
import maya.cmds as cmds

import joint as jnt
reload(jnt)

# 고정변수
currentPath     = '/'.join( __file__.split('\\')[:-1] ) + '/'
moduleRoot      = '/'.join( __file__.split('\\')[:-2] ) + '/'
documentPath    = '//alfredstorage/Alfred_asset/Maya_Shared_Environment/scripts_Documents/'
iconPath        = currentPath + 'icon/'
alfredIcon      = iconPath + 'alfredLogo.png'

# mem변수
uiMem = [10,'jiggle',4]

# 사용자정의변수.
win         = 'dynamicJointChainRigUI'
title       = 'Dynamic Joint Chain'
labelWidth  = 200
shelf_icon  = iconPath + 'shelf_icon.png'  # 'pythonFamily.png'
shelf_label = ''
shelf_cmd   = 'import rig.dynamicJointChainTool as jc\njc.ui()'
shelf_anno  = u''

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
                sti = self.loadOptionVar('mainTab'), 
                cc  = pm.Callback( self.saveOptionVar, 'mainTab' ), 
                tabLabel = [
                    (tab1,'Joint Chain'),
                    (tab2,'hairSys Type'),
                    (tab3,'nCloth Type')
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

    def saveOptionVar(self, widget ):
        if widget=='mainTab':        
            selIndex = pm.tabLayout( self.mid, q=True, sti=True)
            pm.optionVar[ win+'mainTabSel' ] = selIndex

    def loadOptionVar(self, widget ):
        if widget=='mainTab':
            if pm.optionVar.has_key( win+'mainTabSel' ):
                return pm.optionVar[ win+'mainTabSel' ]
            else :
                return 1
        
def ui(): UI()

#
# 사용자정의 UI.
#
widget = {}
def uiContents_tab1():
    # Transform -----------------------
        with pm.frameLayout(l='Joint Tools', cll=True, mw=3, mh=3, cl=False ):
            with pm.columnLayout(adj=True):

                with pm.rowLayout(nc=4):
                    pm.text(l='Joint Display : ', w= labelWidth, align='right')
                    pm.button( l='Axis',   w= 39, c=pm.Callback( jnt.toggleDisplayAxis ))
                    pm.button( l='Handle', w= 39, c=pm.Callback( jnt.toggleDisplayHandle ))
                    pm.button( l='Label',  w= 39, c=pm.Callback( jnt.toggleJointLabel ))

                with pm.rowLayout(nc=5):
                    pm.text(l=u'Joint Display Scale : ', w=labelWidth, align='right')
                    w= 155 / 4
                    pm.button(l='2.00', c=pm.Callback( pm.jointDisplayScale, 2.0 ), w=w)
                    pm.button(l='1.00', c=pm.Callback( pm.jointDisplayScale, 1.0 ), w=w)
                    pm.button(l='0.50', c=pm.Callback( pm.jointDisplayScale, 0.5 ), w=w)
                    pm.button(l='0.1',  c=pm.Callback( pm.jointDisplayScale, 0.1 ), w=w) 

                pm.separator( h=8, style='in')

                with pm.rowLayout(nc=4):
                    pm.text(l='Joint Orient : ', w= labelWidth, align='right')
                    pm.button( l=u'Orient', w= 100, c=pm.Callback( jnt.jntOrient, orient=True ), ann=u'joint, [aimObj], upObj 순서로 선택')   
                    pm.button( l=u'None',   w= 60,  c=pm.Callback( jnt.jntOrient, orient=False ), ann=u'Parent의 Orient를 따라감.')   

                with pm.rowLayout(nc=4):
                    pm.text(l='Joint Orient Set Zro: ', w= labelWidth, align='right')
                    pm.button( l=u'Set Joint Orient Zero', w= 160, c=pm.Callback( jnt.jntResetOrient ) ) 

                with pm.rowLayout(nc=4):
                    pm.text(l='Joint Chain Orient : ', w= labelWidth, align='right')
                    pm.button( l=u'Parent Y Axis or Polynormal', w= 160, c=pm.Callback( jnt.jointChainOrient ) )   

                with pm.rowLayout(nc=5):
                    pm.text(l='Split Joint : ', w= labelWidth, align='right')
                    pm.button( l='Split', w=160, c=pm.Callback(  btn_splitJoint ) )
                
                with pm.rowLayout(nc=5):
                    pm.text(l='Duplicate Joint : ', w= labelWidth, align='right')
                    pm.button( l='Dup Chain',  w=79, c=pm.Callback(  jnt.duplicateJointChain ) )
                    pm.button( l='Dup Single', w=79, c=pm.Callback(  jnt.duplicateJoints ) )  

                pm.separator( h=8, style='in')

                with pm.rowLayout(nc=5):
                    pm.text(l='Zero Group : ', w= labelWidth, align='right')
                    pm.button( l='Create', w=160, c=pm.Callback( jnt.zeroGroup ) )

        with pm.frameLayout(l='Get Joint Chain', cll=True, mw=3, mh=3, cl=False ):
            with pm.columnLayout(adj=True):

                with pm.rowLayout(nc=5):
                    pm.text(l='Edge To Curve : ', w= labelWidth, align='right')
                    pm.button( l='edgeToCrv', w=79, c=pm.Callback(  pm.mel.CreateCurveFromPoly ) )
                    pm.button( l='Rebuild',   w=79, c=pm.Callback(  pm.mel.RebuildCurveOptions ) )  

                pm.separator( h=8, style='in')

                with pm.rowLayout(nc=5):
                    pm.text(l='Edge To Joint Chain : ', w= labelWidth, align='right')
                    pm.button( l='Create',  w=79, c=pm.Callback(  jnt.edgeToJnt ) )
                    pm.button( l='Reverse', w=79, c=pm.Callback(  jnt.edgeToJnt, reverse=True ) )  

                with pm.rowLayout(nc=5):
                    pm.text(l='Curve To Joint Chain : ', w= labelWidth, align='right')
                    pm.button( l='ep (divide)', w=79, c=pm.Callback(  btn_crvToJnt, div=10 ) )  
                    pm.button( l='ep',          w=79, c=pm.Callback(  btn_crvToJnt ) )                    
                with pm.rowLayout(nc=5):
                    pm.text(l='', w= labelWidth, align='right')                    
                    pm.button( l='cv (divide)', w=79, c=pm.Callback(  btn_crvToJnt, div=10, ep=False ) )  
                    pm.button( l='cv',          w=79, c=pm.Callback(  btn_crvToJnt, ep=False ) )

                pm.separator( h=8, style='in')
                
                with pm.rowLayout(nc=5):
                    pm.text(l='Joint Chain To Curve : ', w= labelWidth, align='right')
                    pm.button( l='ep deg1',  w=52, c=pm.Callback(  jnt.jntToCrv, degree=1, ep=True ) )
                    pm.button( l='ep deg2',  w=52, c=pm.Callback(  jnt.jntToCrv, degree=2, ep=True ) )
                    pm.button( l='ep deg3',  w=52, c=pm.Callback(  jnt.jntToCrv, degree=3, ep=True ) )
                with pm.rowLayout(nc=5):
                    pm.text(l='', w= labelWidth, align='right')
                    pm.button( l='cv deg2',  w=52, c=pm.Callback(  jnt.jntToCrv, degree=2, ep=False ) )
                    pm.button( l='cv deg3',  w=52, c=pm.Callback(  jnt.jntToCrv, degree=3, ep=False ) )

        with pm.frameLayout(l='Joint Chain Rig', cll=True, mw=3, mh=3, cl=False ):
            with pm.columnLayout(adj=True):

                with pm.rowLayout(nc=5):
                    pm.text(l='Select Joint Chain : ', w= labelWidth, align='right')
                    pm.button( l='Select', w=160, c=pm.Callback( jnt.findJointChain ) )

                with pm.rowLayout(nc=5, ann=u'연이은 조인트들을 선택하고 실행.'):
                    pm.text(l='Rig Joint Chain : ', w= labelWidth, align='right')
                    pm.button( l='Rig', w=160, c=pm.Callback( btn_jointChain ) )

                with pm.rowLayout(nc=5):
                    pm.text(l='Convert To Dynamic Joint: ', w= labelWidth, align='right')
                    pm.button( l='Rig', w=160, c=pm.Callback( jnt.jointChainToDynamicChain ) )

def uiContents_tab2():
        with pm.frameLayout(l='2. Joint Chain Rig', cll=True, mw=3, mh=3 ):
            with pm.columnLayout(adj=True):

                with pm.rowLayout(nc=5):
                    pm.text(l='Select Joint Chain : ', w= labelWidth, align='right')
                    pm.button( l='Select', w=80, c=pm.Callback( jnt.findJointChain ) )

                pm.separator( h=8, style='in')

                with pm.rowLayout(nc=5, ann=u'연이은 조인트들을 선택하고 실행. \n원하는헤어시스템이나 뉴클리어스 노드가 존재하면 함께 선택할것'):
                    pm.text(l='Rig Hair Jiggle Joint Chain : ', w= labelWidth, align='right')
                    pm.button( l='Non Stretch',         w=80, c=pm.Callback( btn_hairJiggle, stretchable=False ) )
                    pm.button( l='Stretch', w=80, c=pm.Callback( btn_hairJiggle, stretchable=True  ) )

        with pm.frameLayout(l='3. Simulation', cll=True, mw=3, mh=3 ):
            with pm.columnLayout(adj=True):

                with pm.rowLayout(nc=5):
                    pm.text(l='Selection : \n( Please select a joint in Chain )  ', w= labelWidth, align='right')
                    with pm.rowColumnLayout(nc=2):
                        pm.button(l='HairSystem',    c=pm.Callback( jnt.findHairSystem ), w=80)
                        pm.button(l='Nucleus',       c=pm.Callback( jnt.findNucleus ), w=80)
                        pm.button(l='Follicle',      c=pm.Callback( jnt.findFollicle ))
                        pm.button(l='ikHandle',      c=pm.Callback( jnt.findIKHandle ))
                        pm.button(l='splineIKCurve', c=pm.Callback( jnt.findSplineIKCrv ))
                        pm.button(l='Dynamic Curve', c=pm.Callback( jnt.findDynamicCurve ))
                        pm.button(l='JointChain',    c=pm.Callback( jnt.findJointChain ))

                pm.separator( h=8, style='in')

                with pm.rowLayout(nc=5):
                    pm.text(l='Interactive Playback : ', w= labelWidth, align='right')
                    #pm.button( l='>>', w=160, c=pm.Callback(  pm.mel.InteractivePlayback ) ) # interactivePlayback.png
                    widget['playButton'] = pm.symbolButton( image='interactivePlayback.png', w=32, h=32, c=pm.Callback( btn_play ) )


                with pm.rowLayout(nc=5):
                    pm.text(l='Bake Simulation : ', w= labelWidth, align='right')
                    pm.button( l='Open UI..', w=160, c=pm.Callback(  pm.mel.BakeSimulationOptions ) )

def uiContents_tab3():
    # Joint -----------------------
        with pm.frameLayout(l='Select', cll=True, mw=3, mh=3 ):
            with pm.columnLayout(adj=True):

                with pm.rowLayout(nc=4):
                    pm.text(l='Joint Display : ', w= labelWidth, align='right')
                    pm.button( l='Axis',   w= 39)
                    pm.button( l='Handle', w= 39)
                    pm.button( l='Label',  w= 39)

#
# Joint
#
def btn_play():
    if pm.play( q=True, state=True ):
        pm.symbolButton( widget['playButton'], e=True, image='interactivePlayback.png' )
        pm.play( state=False )
    else:
        pm.symbolButton( widget['playButton'], e=True, image='timestop.png' )
        pm.mel.InteractivePlayback()

    #currentTime 

def btn_splitJoint():
    sel = pm.selected( type='joint' )
    if not sel:
        raise

    sd = input()
    if not sd:
        raise

    jnt.splitJoint( sel[0], sd )

def btn_crvToJnt( **kwargs ):
    global uiMem

    if 'div' in kwargs.keys():
        result = pm.promptDialog(m='Divide Num', text=uiMem[0])
        if result=='Confirm':
            kwargs['div'] = int( pm.promptDialog(q=True, text=True) )      
            uiMem[0] = kwargs['div']
            jnt.crvToJnt( **kwargs )

def btn_hairJiggle( **kwargs):
    result = pm.promptDialog(m='Prefix : ', text=uiMem[1])
    if result=='Confirm':
        kwargs['prefix'] = pm.promptDialog(q=True, text=True)
        uiMem[1] = kwargs['prefix']
        jnt.hairJiggle(**kwargs)

def btn_jointChain():

    result = pm.promptDialog(m='ctrlNum : ', text=uiMem[2])
    if result=='Confirm':
        num = int( pm.promptDialog(q=True, text=True) )
        uiMem[2] = num

        jnt.jointChain( ctrlNum=num )
    