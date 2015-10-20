# -*- coding:utf-8 -*-
import pymel.core as pm
import maya.cmds as cmds
import alfredTools.ui.v140123 as ui
reload(ui)

def showWindow():
    Window.showWindow()

class Window(ui.Window):
    '''
    Window.showWindow()
    '''
    def __init__(self):
        super( Window, self ).__init__()

        self.titleIcon    = 'shelf_arnold.png'
        self.title        = u'Set Vertex Color by Arnold aiUserData Attribute'
        self.annotation   = u'aiUserData용 어트리뷰트로\n 선택한 오브젝트에 버텍스컬러를 세팅합니다..'
        self.buttonLabel  = 'Set'
        self.helpURL      = None

        self.shelfIcon    = 'shelf_arnold_label.png'
        self.shelfLabel   = 'vtxc'
        self.shelfCommand = None   

        # optionVar로 저장될 변수들
        self.objName  = ui.OptionVar('alfred_arnold_addAttr__objName', '',  optionVar=False)
        self.attrName = ui.OptionVar('alfred_arnold_addAttr__attrName', '', optionVar=False)
 
    def contents(self):
        with ui.TopMidDownLayout(): 
            with pm.columnLayout(adj=True):
                ui.ObjectSelector( label='Sample Object : ', pht='Select Object',  optVar=self.objName, height=22, auto=True, id=-1 )
                pm.separator(h=8, style='in')
            
            self.TSL = pm.textScrollList( w=10, h=20, selectCommand=pm.Callback( self.uiCmds, 'TSL_select') )
            
            pm.separator(h=1,style='none')
            
        # update
        self.uiCmds('scriptJob_selectionChange')

        # add ScriptJob
        pm.scriptJob( parent=self.TSL, event=['SelectionChanged', pm.Callback( self.uiCmds, 'scriptJob_selectionChange') ] )
   
    def uiCmds(self, mode, *args):
        if mode=='scriptJob_selectionChange':

            sel = cmds.ls( sl=True, o=True )            
            pm.textScrollList( self.TSL, e=True, removeAll=True )

            if sel:
                if pm.objExists( sel[-1] ) :
                    validAttr = getValidAttributes( sel[-1] )

                    if validAttr:
                        pm.textScrollList( self.TSL, e=True, append=validAttr )
            else:
                self.objName.set('')
                self.attrName.set('')
        
        elif mode=='TSL_select':            
            attr = pm.textScrollList( self.TSL, q=True, selectItem=True )
            if attr:
                self.attrName.set( attr[0] )

    def doIt(self, *args):
        #print '   objName : ', self.objName.get() 
        #print '  attrName : ', self.attrName.get() 

        setVtxColorFromArnoldAttr(
            attrName   = self.attrName.get(),
            )

   
def setVtxColorFromArnoldAttr( attrName='color' ):
    if attrName.startswith('mtoa_constant_'):
        attrName = attrName[14:]

    for obj in pm.selected():
        try:
            shp = obj.getShape()
            attr = 'mtoa_constant_'+attrName
            rgb = []
            if shp.hasAttr( attr ):
                rgb = shp.getAttr( attr )
                pm.polyColorPerVertex( obj, colorRGB=rgb, alpha=1, colorDisplayOption=True)
        except:
            continue

def getValidAttributes( obj ):
    obj = pm.PyNode(obj)
    shp = obj.getShape()

    validAttr = []
    for attr in shp.listAttr():
        if attr.name( includeNode=False ).startswith('mtoa_constant_'):
            if attr.type()[-1]=='3':
                validAttr.append( attr.name( includeNode=False ) )

    return validAttr