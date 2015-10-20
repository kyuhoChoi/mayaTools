# -*- coding:utf-8 -*-
'''
# 파이썬 경로 추가
_newPath = '//alfredstorage/Alfred_asset/Maya_Shared_Environment/scripts_Python/Alfred_AssetTools'
if not _newPath in sys.path:
    sys.path.append(_newPath)    

import HIK_Tools_UI

reload(HIK_Tools_UI)
HIK_Tools_UI.UI()

import HIK_Tools
reload(HIK_Tools)
'''

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pyMel

import HIK_Tools

_window = 'HIK_Tools_Window'
_dock   = 'HIK_Tools_Dock'
_tilte  = 'HIK Tools'

_UI_TXF_currentChar = ''

def UI():
    if not cmds.optionVar( exists='ui_OptionVar' ):
        setToDefault()

    if cmds.optionVar( query ='ui_DefaultMode' ):
        Dock()
    else:
        Window()

    updateUI()

def UI_top():
    global _UI_TXF_currentChar

    cmds.rowLayout(numberOfColumns=3, adj=2)    
    cmds.text(label = ' Character :')
    _UI_TXF_currentChar = cmds.textField( font='boldLabelFont' , editable= False)
    addScriptJob()

    cmds.rowLayout(nc=2, adj=2)
    # cmds.button(l='HIK',   h=32, c=selectHIKCharacterNode )
    #cmds.button(l='HIKpr', c=selectHIKProperty2State ) 
    #cmds.symbolButton( image='humanIK_CharCtrl.png', c='import maya; maya.mel.eval(\'HIKCharacterControlsTool;\')')
    cmds.setParent( '..' )

    cmds.setParent( '..' )

def Module():
    MenuBar()
    _form = cmds.formLayout()
    _colm = cmds.columnLayout(adj=True); UI_top(); cmds.setParent( '..' )
    _tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

    cmds.formLayout( _form, edit=True, attachForm=((_colm, 'top', 0), (_colm, 'left', 0), (_colm, 'right', 0), (_tabs, 'left', 0), (_tabs, 'bottom', 0), (_tabs, 'right', 0)),  attachControl=(_tabs, 'top', 0, _colm), attachNone=(_colm, 'bottom') )
    
    _child1 = cmds.scrollLayout( childResizable=True )  
    
    cmds.frameLayout( label='HIK Window', borderStyle='etchedIn', collapsable=True )
    cmds.columnLayout(adj=True)
    cmds.button(l=u'Character Control 윈도우', c='import maya; maya.mel.eval(\'HIKCharacterControlsTool;\')')
    cmds.setParent( '..' )
    cmds.setParent( '..' )

    cmds.frameLayout( label='Select HIK Node', borderStyle='etchedIn', collapsable=True )
    cmds.columnLayout(adj=True)
    cmds.button(l=u'HIKCharacter Node 선택', al='left', c=selectHIKCharacterNode ) 
    cmds.button(l=u'HIKProperty2State Node 선택', c=selectHIKProperty2State ) 
    cmds.setParent( '..' )
    cmds.setParent( '..' )

    cmds.setParent( '..' )    

    _child2 = cmds.scrollLayout( childResizable=True )    
    cmds.frameLayout( label='HIK Rig Tools', borderStyle='etchedIn', collapsable=True )
    cmds.columnLayout(adj=True)
    cmds.button(l=u'Floor Contact 리깅', c=btnCmd_Rig_FloorContact ) 
    cmds.setParent( '..' )
    cmds.setParent( '..' )

    cmds.frameLayout( label='Counter Strike RigTools', borderStyle='etchedIn', collapsable=True )
    cmds.columnLayout(adj=True)
    cmds.button(l=u'총 리깅', c=btnCmd_Rig_sniperGunRig ) 
    cmds.setParent( '..' )
    cmds.setParent( '..' )

    cmds.frameLayout( label='Display', borderStyle='etchedIn', collapsable=True )
    cmds.columnLayout(adj=True)
    cmds.button(l=u'커브 연결', c=btnCmd_Rig_displayConnect_curve ) 
    cmds.button(l=u'화살표 연결', c=btnCmd_Rig_displayConnect_arrow ) 
    cmds.setParent( '..' )
    cmds.setParent( '..' )

    cmds.setParent( '..' )

    _child3 = cmds.rowColumnLayout(numberOfColumns=2)
    cmds.button()
    cmds.button()
    cmds.button()
    cmds.setParent( '..' )
    
    cmds.tabLayout( _tabs, edit=True, tabLabel=((_child1, 'HIK Setting'), (_child2, 'HIK Rig'), (_child3, 'Motion Capture Edit')) )
    #cmds.setParent('..')

def MenuBar():
    _menuBarLayout = cmds.menuBarLayout()

    cmds.menu( label='Preference' )
    cmds.menuItem( label='Reload Script',       c= 'reload(%s)\n%s.UI()'%(__name__,__name__))
    cmds.menuItem( divider=True )    
    cmds.menuItem( label='Switch Window, Dock', c= SwitchUI)
    cmds.menuItem( label='Set to Default',      c= setToDefault)

    '''
    cmds.menuItem( subMenu=True, label='Colors' )
    cmds.menuItem( label='Blue' )
    cmds.menuItem( label='Green' )
    cmds.menuItem( label='Yellow' )
    cmds.setParent( '..', menu=True )
    cmds.menuItem( divider=True )

    cmds.radioMenuItemCollection()
    cmds.menuItem( label='Yes', radioButton=False )
    cmds.menuItem( label='Maybe', radioButton=False )
    cmds.menuItem( label='No', radioButton=True )
    cmds.menuItem( divider=True )
    cmds.menuItem( label='Top', checkBox=True )
    cmds.menuItem( label='Middle', checkBox=False )
    cmds.menuItem( label='Bottom', checkBox=True )
    cmds.menuItem( divider=True )
    cmds.menuItem( label='Option' )
    cmds.menuItem( optionBox=True )
    '''
    cmds.menu( label='Help' )

def Window():
    global _window,_dock,_tilte

    if cmds.window(_window, q=True, exists=True): cmds.deleteUI(_window)
    cmds.window(_window)
    Module()
    cmds.showWindow(_window)

    # dock 삭제
    if cmds.dockControl(_dock, q=True, exists=True):             
        cmds.deleteUI(_dock)

def Dock():
    global _window,_dock,_tilte

    if cmds.window(_window, q=True, exists=True): cmds.deleteUI(_window)
    cmds.window(_window)
    Module()

    _area = 'right'
    _floating = False
    _label = _tilte
    _width = 330
    _allowedAreas = ['right', 'left']

    if cmds.dockControl(_dock, q=1, exists=1):             
        _area     = cmds.dockControl(_dock, q=1, area=True)
        _floating = cmds.dockControl(_dock, q=1, floating=True)
        _width    = cmds.dockControl(_dock, q=1, width=True)
        cmds.deleteUI(_dock)

    cmds.dockControl(
        _dock,
        area = _area,
        label = _label,
        floating = _floating,
        width = _width,
        content = _window,
        allowedArea = _allowedAreas
        )

def SwitchUI(*args):
    if cmds.dockControl(_dock, q=1, exists=1):
        Window()
        cmds.optionVar( intValue=('ui_DefaultMode', 0) )
    else:
        Dock()
        cmds.optionVar( intValue=('ui_DefaultMode', 1) )
        
def setToDefault(*args):
    cmds.optionVar( intValue=('ui_DefaultMode', 1) )

    cmds.optionVar( intValue=('ui_OptionVar', 1) )

def updateUI(*args):
    cmds.textField(_UI_TXF_currentChar, edit=True, text=HIK_Tools.getHIKCurrentCharacter() )

# Script Job 관련
def updateUI_from_Select(*args):
    _sel = cmds.ls(sl=True)
    if not _sel: return

    _HIK = HIK_Tools.getHIKCharacterNode_from_nodeName(_sel[-1])
    if not _HIK: return

    HIK_Tools.setHIKCharacterNode(_HIK)
    updateUI()

def addScriptJob():
    global _UI_TXF_currentChar

    for _job in cmds.scriptJob( listJobs=True ):
            if 'updateUI_from_Select' in _job:
                # scriptJob 이름이 아래처럼 출력됨.
                # 2207: event=['SelectionChanged', 'HIK_Tools.update_HIKCurrentCharacter_from_select()'], parent='hikCharacterControlsDock'
                #
                print u'+ scriptJob이 이미 존재합니다 :',_job
                return

    cmds.scriptJob( parent=_UI_TXF_currentChar, killWithScene=True, event=['SelectionChanged', __name__+'.updateUI_from_Select()'] )

def selectHIKCharacterNode(*args):
    _node = HIK_Tools.getHIKCurrentCharacter()
    cmds.select(_node)

def selectHIKProperty2State(*args):
    _node = HIK_Tools.getHIKProperty2State( HIK_Tools.getHIKCurrentCharacter() )
    cmds.select(_node)

# button Cmd
def btnCmd_Rig_FloorContact(*args):
    HIK_Tools.setFloorContact()

def btnCmd_Rig_displayConnect_curve(*args):
    _sel = cmds.ls(sl=True)
    HIK_Tools.displayConnect_curve(_sel)

def btnCmd_Rig_displayConnect_arrow(*args):
    _sel = cmds.ls(sl=True)
    HIK_Tools.displayConnect_arrow(_sel)

def btnCmd_Rig_sniperGunRig(*args):
    HIK_Tools.Gun_Rig()

def btnCmd_selectHIKCharacterNode(*args):
    print ''