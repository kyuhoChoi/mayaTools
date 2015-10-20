# -*- coding:utf-8 -*-
'''
# 파이썬 경로 추가
_newPath = '//alfredstorage/Alfred_asset/Maya_Shared_Environment/scripts_Python/Alfred_AssetTools'
if not _newPath in sys.path:
    sys.path.append(_newPath)    

import Gun_Tools_UI

reload(Gun_Tools_UI)
Gun_Tools_UI.UI()

import Gun_Tools
reload(Gun_Tools)
'''

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pyMel

import Gun_Tools

_window = 'Gun_Tools_Window'
_dock   = 'Gun_Tools_Dock'
_tilte  = 'Gun Tools'

_UI_TXF_currentChar = ''
_UI_TXF_namespace = ''
_UI_TXF_side = ''
_UI_CHG_deSelClearData = ''

#----------------------------------------
#
#     Model(Data)
#
#----------------------------------------
_debug      = cmds.optionVar( q='ui_debug' )
_updateMode = cmds.optionVar( q='ui_updateMode' )

_HIKCharacterNode = []
_namespace = []
_Side = []

def setToDefault(*args):
    cmds.optionVar( intValue=('ui_DefaultMode', 1) )
    cmds.optionVar( intValue=('ui_selectedTabIndex', 1) )
    cmds.optionVar( intValue=('ui_debug', 0) )
    cmds.optionVar( intValue=('ui_updateMode', 1) )

    cmds.optionVar( intValue=('ui_OptionVar', 1) )

#----------------------------------------
#
#     View(UI)
#
#----------------------------------------
def UI():
    if not cmds.optionVar( exists='ui_OptionVar' ):
        setToDefault()

    if cmds.optionVar( query ='ui_DefaultMode' ):
        Dock()
    else:
        Window()

    update_from_Select()

def UI_top():
    global _UI_TXF_currentChar, _UI_TXF_namespace, _UI_TXF_side

    cmds.separator(style='in')
    
    cmds.rowLayout( numberOfColumns=2, adj=2 )
    cmds.text(label = ' namespace : ', align='right', w=120)
    _UI_TXF_namespace = cmds.textField( font='boldLabelFont' , editable= False)
    cmds.setParent( '..' )
    
    cmds.rowLayout( numberOfColumns=2, adj=2 )
    cmds.text(label = ' HIK Character Node : ', align='right', w=120)
    _UI_TXF_currentChar = cmds.textField( font='boldLabelFont' , editable= False)
    cmds.setParent( '..' )

    cmds.rowLayout( numberOfColumns=2, adj=2 )
    cmds.text(label = ' Side : ', align='right', w=120)
    _UI_TXF_side = cmds.textField( font='boldLabelFont' , editable= False)
    cmds.setParent( '..' )

    cmds.separator(style='in')

    cmds.rowLayout( numberOfColumns=3, adj=2 )
    cmds.text(label = ' Gun Reference Root : ', align='right', w=120)
    _UI_TXF_gunRefRoot = cmds.textField( font='boldLabelFont' , editable= False)
    cmds.button(l='<<')
    cmds.setParent( '..' )

    cmds.separator(style='in')

    addScriptJob()

def UI_tab():
    _form = cmds.formLayout()
    _colm = cmds.columnLayout(adj=True); UI_top(); cmds.setParent( '..' )
    _tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

    cmds.formLayout( _form, edit=True, attachForm=((_colm, 'top', 0), (_colm, 'left', 0), (_colm, 'right', 0), (_tabs, 'left', 0), (_tabs, 'bottom', 0), (_tabs, 'right', 0)),  attachControl=(_tabs, 'top', 0, _colm), attachNone=(_colm, 'bottom') )
    _tab_1 = Tab_1()
    _tab_2 = Tab_2()

    _selTabIndex = cmds.optionVar( query ='ui_selectedTabIndex' )
    cmds.tabLayout(
        _tabs, 
        edit=True, 
        tabLabel=(
            (_tab_1, 'Gun Rig'),
            (_tab_2, 'Gun Anim')
            ), 
        selectTabIndex= _selTabIndex,
        changeCommand= pyMel.Callback( UI_TAB_changeCommand, _tabs ) 
    )

def Module():
    MenuBar()
    UI_tab()
    #cmds.setParent('..')

def MenuBar():
    _menuBarLayout = cmds.menuBarLayout()

    cmds.menu( label='Options' )
    cmds.menuItem( label='Switch Window, Dock', c= SwitchUI)

    cmds.menuItem( divider=True ) #-----------------------------------------------------------------------------------------------

    cmds.menuItem( label='Reload Script', c= reloadScript)
    cmds.menuItem( label='Script Debug', checkBox=_debug, c= setDebug)

    cmds.menuItem( divider=True ) #-----------------------------------------------------------------------------------------------

    cmds.menuItem( label='Set to Default',      c= setToDefault)
    
    cmds.menuItem( subMenu=True, label='Update Mode' )
    cmds.radioMenuItemCollection()
    cmds.menuItem( label='Update by selection',            radioButton= _updateMode==1, c= pyMel.Callback(UI_RBG_updateMode,1) )
    cmds.menuItem( label='Remind the last selection data', radioButton= _updateMode==2, c= pyMel.Callback(UI_RBG_updateMode,2))
    cmds.setParent( '..', menu=True )

    cmds.menuItem( subMenu=True, label='scriptJob' )
    cmds.menuItem( label='Add scriptJob', c=addScriptJob)
    cmds.menuItem( label='Remove scriptJob', c=removeScriptJob)
    cmds.setParent( '..', menu=True )

    cmds.menuItem( divider=True ) #-----------------------------------------------------------------------------------------------  

    cmds.menuItem( label='Print Current Data', c= btnCmd_printCurrentState)


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
    global _window, _dock, _tilte

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

#----------------------------------------
#
#     View(UI)
#     Tabs
#
#----------------------------------------
def Tab_1():
    _return = cmds.scrollLayout( childResizable=True )    
    cmds.frameLayout( label='HIK Rig', borderStyle='etchedIn', collapsable=True )
    cmds.columnLayout(adj=True)
    cmds.button(l=u'Floor Contact 리깅', c=btnCmd_Rig_FloorContact ) 
    cmds.setParent( '..' )
    cmds.setParent( '..' )

    cmds.frameLayout( label='Gun Rig', borderStyle='etchedIn', collapsable=True )
    cmds.columnLayout(adj=True)

    cmds.button(l=u'총 리깅', c=btnCmd_Rig_sniperGunRig ) 
    
    cmds.frameLayout( label='Character Part', borderStyle='etchedIn', collapsable=True )
    cmds.columnLayout(adj=True)
    cmds.button(l=u'총 리깅', c=btnCmd_Rig_sniperGunRig ) 
    cmds.setParent( '..' )
    cmds.setParent( '..' )

    cmds.frameLayout( label='Gun Part', borderStyle='etchedIn', collapsable=True )
    cmds.columnLayout(adj=True)
    cmds.button(l=u'총 리깅', c=btnCmd_Rig_sniperGunRig ) 
    cmds.setParent( '..' )
    cmds.setParent( '..' )

    cmds.setParent( '..' )
    cmds.setParent( '..' )

    cmds.frameLayout( label='Display', borderStyle='etchedIn', collapsable=True )
    cmds.columnLayout(adj=True)
    cmds.button(l=u'커브 연결', c=btnCmd_Rig_displayConnect_curve ) 
    cmds.button(l=u'화살표 연결', c=btnCmd_Rig_displayConnect_arrow ) 
    cmds.setParent( '..' )
    cmds.setParent( '..' )

    cmds.setParent( '..' )

    return _return

def Tab_2():
    _return = cmds.scrollLayout( childResizable=True )  
    
    cmds.frameLayout( label='HIK Controls', borderStyle='etchedIn', collapsable=True )
    cmds.columnLayout(adj=True)
    
    cmds.rowLayout( numberOfColumns=2, adj=2 )
    cmds.text(label = u'HIK Character Controls Tool : ', align='right', w=180)
    cmds.button(l=u'Window', c='import maya; maya.mel.eval(\'HIKCharacterControlsTool;\')')
    cmds.setParent( '..' )

    cmds.rowLayout( numberOfColumns=2, adj=2 )
    cmds.text(label = u'Select HIK Node : ', align='right', w=180)
    cmds.button(l=u'HIKCharacter', al='left', c=selectHIKCharacterNode )
    cmds.setParent( '..' )

    cmds.rowLayout( numberOfColumns=2, adj=2 )
    cmds.text(label = '', w=180)
    cmds.button(l=u'HIKProperty2State', al='left', c=selectHIKProperty2State )
    cmds.setParent( '..' )

    cmds.rowLayout( numberOfColumns=2, adj=2 )
    cmds.text(label = '', w=180)
    cmds.button(l=u'HIK Hand FKCtrl', al='left', c=select_HIK_Finger )
    cmds.setParent( '..' )

    cmds.setParent( '..' )
    cmds.setParent( '..' )

    cmds.frameLayout( label='Select HIK Node', borderStyle='etchedIn', collapsable=True )
    cmds.columnLayout(adj=True)
    cmds.button(l=u'왼손 HIK FKCtrl 선택', c=select_HIK_Finger)
    cmds.button(l=u'오른손 HIK FKCtrl 선택', c='from maya import mel\nmel.eval( \'select -add `ls -exactType "hikFKJoint" "*:*RightHand*"`;\') ')
    cmds.setParent( '..' )
    cmds.setParent( '..' )

    cmds.setParent( '..' )

    return _return

#----------------------------------------
#
#     Control(UI Control)
#
#----------------------------------------
def SwitchUI(*args):
    if cmds.dockControl(_dock, q=1, exists=1):
        Window()
        cmds.optionVar( intValue=('ui_DefaultMode', 0) )
    else:
        Dock()
        cmds.optionVar( intValue=('ui_DefaultMode', 1) )

    update_from_Select()
        
def reloadScript(*args):
    mel.eval('python( "reload(%s)" );\n'%__name__)
    UI()

def setDebug(*args):
    global _debug
    _debug = args[0]
    cmds.optionVar( intValue=('ui_debug', _debug) )
    UI()

def UI_TAB_changeCommand(*args):
    _selTabIndex = cmds.tabLayout(args[0], q=True, selectTabIndex=True)
    cmds.optionVar( intValue=('ui_selectedTabIndex', _selTabIndex) )

def UI_RBG_updateMode(*args):
    global _updateMode

    _updateMode = args[0]
    cmds.optionVar( intValue=('ui_updateMode', _updateMode ))

    update_from_Select()

#----------------------------------------
#
#     Control(UI Control)
#     업데이트 관련
#
#----------------------------------------
def updateUI(*args):
    _HIKCharacterNode_txt = ''
    _namespace_txt = ''
    _side_txt = ''

    for _i in _HIKCharacterNode : _HIKCharacterNode_txt += _i+'  '
    for _i in _namespace        : _namespace_txt += _i[:-1]+'  '
    for _i in _Side             : _side_txt += _i+'  '

    cmds.textField(_UI_TXF_currentChar, edit=True, text=_HIKCharacterNode_txt )
    cmds.textField(_UI_TXF_namespace,   edit=True, text=_namespace_txt )
    cmds.textField(_UI_TXF_side,        edit=True, text=_side_txt )

def update_from_Select(*args):
    # 변경할 global 변수
    global _HIKCharacterNode, _namespace, _Side

    # 글로벌 변수 초기화
    if _updateMode == 1:
        _HIKCharacterNode = []
        _namespace = []
        _Side = []
    
    # 선택
    _sel = cmds.ls(sl=True)

    # 선택한게 없음 나감
    if not _sel: 
        updateUI()
        return

    # 글로벌 변수 조정
    _HIKCharacterNode = Gun_Tools.getHIKCharacterNode(_sel)
    _namespace        = Gun_Tools.getNamespace(_sel)
    _Side             = Gun_Tools.getSide(_sel)

    if _HIKCharacterNode:
        Gun_Tools.setHIKCharacterNode(_HIKCharacterNode[-1])

    # UI Update
    updateUI()

#----------------------------------------
#
#     Control(UI Control)
#     Script Job
#
#----------------------------------------
def addScriptJob(*args):
    global _UI_TXF_currentChar

    for _job in cmds.scriptJob( listJobs=True ):
        if 'update_from_Select' in _job:
            # scriptJob 이름이 아래처럼 출력됨.
            # 2207: event=['SelectionChanged', 'Gun_Tools.update_HIKCurrentCharacter_from_select()'], parent='hikCharacterControlsDock'
            #
            print u'+ scriptJob이 이미 존재합니다 :',_job
            return

    cmds.scriptJob( parent=_UI_TXF_currentChar, killWithScene=True, event=['SelectionChanged', __name__+'.update_from_Select()'] )

def removeScriptJob(*args):
    for _job in cmds.scriptJob( listJobs=True ):
        if 'update_from_Select' in _job:
            # scriptJob 이름이 아래처럼 출력됨.
            # 2207: event=['SelectionChanged', 'Gun_Tools.update_HIKCurrentCharacter_from_select()'], parent='hikCharacterControlsDock'
            #
            _split = _job.split(':')
            _jobNum = int(_split[0])
            cmds.scriptJob( kill=_jobNum, force=True)
            print u'+ scriptJob 삭제 :',_job

#----------------------------------------
#
#     Control(UI Control)
#     Button Commands
#
#----------------------------------------
def selectHIKCharacterNode(*args):
    cmds.select(_HIKCharacterNode)
    mel.eval('AttributeEditor;')

def selectHIKProperty2State(*args):
    _HIKProperty2State = []
    for _hik in _HIKCharacterNode:
        _HIKProperty2State.append( Gun_Tools.getHIKProperty2State( _hik ) )
    
    cmds.select( _HIKProperty2State )
    mel.eval('AttributeEditor;')

def select_HIK_Finger(*args):
    _sel = []
    _side = []
    
    if not _Side:
        _side = ['Left','Right']
    else:
        _side = _Side

    for _ns in _namespace:
        for _s in _side:
            for _node in cmds.ls( _ns+'*'+_s+'Hand*', exactType='hikFKJoint'):
                _sel.append(_node)

    if _sel:
        cmds.select(_sel, r=True)

def btnCmd_Rig_FloorContact(*args):
    Gun_Tools.setFloorContact()

def btnCmd_Rig_displayConnect_curve(*args):
    _sel = cmds.ls(sl=True)
    Gun_Tools.displayConnect_curve(_sel)

def btnCmd_Rig_displayConnect_arrow(*args):
    _sel = cmds.ls(sl=True)
    Gun_Tools.displayConnect_arrow(_sel)

def btnCmd_Rig_sniperGunRig(*args):
    Gun_Tools.Gun_Rig()

def btnCmd_printCurrentState(*args):
    _char = 20
    print '_HIKCharacterNode :'.rjust(_char), _HIKCharacterNode
    print '_namespace :'.rjust(_char),        _namespace
    print '_Side :'.rjust(_char),             _Side
    print '_updateMode :'.rjust(_char),   _updateMode

