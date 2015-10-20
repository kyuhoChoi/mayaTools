# -*- coding:utf-8 -*-
import pymel.core as pm
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
        self.title        = u'Add Arnold Attribute'
        self.annotation   = u'선택한 노드에 aiUserData용 어트리뷰트를 생성합니다..'
        self.buttonLabel  = 'Add'
        self.helpURL      = None

        self.shelfIcon    = 'shelf_arnold_label.png'
        self.shelfLabel   = 'attr'
        self.shelfCommand = None   

        # optionVar로 저장될 변수들
        self.attrName   = ui.OptionVar('alfred_arnold_addAttr__attrName', 'color')
        self.addToShape = ui.OptionVar('alfred_arnold_addAttr__addToShape', True)
        self.dataType   = ui.OptionVar('alfred_arnold_addAttr__dataType', 1)
        self.aiUserData = ui.OptionVar('alfred_arnold_addAttr__aiUserData', False)
 
    def contents(self):
        with pm.columnLayout(adj=True):
            # Tools ------------------------------------------------------------------------------------
            with pm.rowLayout(nc=10):
                pm.text(l=' Sub Tools : ', w=140, align='right')
                pm.button( l='Set Vertex Color', c=pm.Callback( self.uiCmd, 'vtxColor' ) )
                #pm.symbolButton( i='shelf_displayAxis.png',     c=pm.Callback( self._uiCmd, 'toggleDisplayAxis' ) )
                #pm.symbolButton( i='shelf_locatorAtCenter.png', c=pm.Callback( self._uiCmd, 'locAtCenter' ) )
                #pm.symbolButton( i='orientJoint.png',           c=pm.mel.OrientJointOptions )

            # Attribute Name ---------------------------------------------------------------------------------------
            pm.separator(h=8, style='in')
            with pm.rowLayout(nc=2, adj=2):
                pm.text(l='Attribute Name : ', w=140, align='right')
                pm.textFieldGrp(l='mtoa_constant_', text=self.attrName.get(), tcc=pm.CallbackWithArgs( self.attrName.set ), cw=[1,80], adj=2 )
            
            pm.checkBoxGrp(l='', ncb=1, vertical=True,
                l1  ='Add To Shape Node',
                v1  = self.addToShape.get(),
                cc1 = self.addToShape.set,
                )
            
            # Data Type --------------------------------------------------------------------------------------------
            pm.separator(h=8, style='in')
            pm.radioButtonGrp( 'dt_RBG',  l='Data Type : ', nrb=4, cw5=[140,80,80,80,80],
                l1='Color',   en1=True,  on1=pm.Callback( self.dataType.set, 1),
                l2='Vector',  en2=True,  on2=pm.Callback( self.dataType.set, 2),
                l3='Integer', en3=True, on3=pm.Callback( self.dataType.set, 3),
                l4='String',  en4=True, on4=pm.Callback( self.dataType.set, 4),
                )
            pm.radioButtonGrp( 'dt_RBG2', l='', nrb=4, cw5=[140,80,80,80,80], shareCollection='dt_RBG',
                l1='Float',   en1=True,  on1=pm.Callback( self.dataType.set, 5),
                l2='Boolean', en2=True,  on2=pm.Callback( self.dataType.set, 6),
                l3='Enum',    en3=False, on3=pm.Callback( self.dataType.set, 7),
                l4='Pnt2',    en4=True,  on4=pm.Callback( self.dataType.set, 8),
                )  
            pm.checkBoxGrp(l='', ncb=1, vertical=True,
                l1  ='Create aiUserData Node',
                v1  = self.aiUserData.get(),
                cc1 = self.aiUserData.set,
                #en1 = False
                )

        if   self.dataType.get()==1: pm.radioButtonGrp( 'dt_RBG',  e=True, select=1 )
        elif self.dataType.get()==2: pm.radioButtonGrp( 'dt_RBG',  e=True, select=2 )
        elif self.dataType.get()==3: pm.radioButtonGrp( 'dt_RBG',  e=True, select=3 )
        elif self.dataType.get()==4: pm.radioButtonGrp( 'dt_RBG',  e=True, select=4 )
        elif self.dataType.get()==5: pm.radioButtonGrp( 'dt_RBG2', e=True, select=1 )
        elif self.dataType.get()==6: pm.radioButtonGrp( 'dt_RBG2', e=True, select=2 )
        elif self.dataType.get()==7: pm.radioButtonGrp( 'dt_RBG2', e=True, select=3 )
    
    def uiCmd(self,mode,*args):
        if mode=='vtxColor':
            import arnold_setVtsColor_by_arnoldAttrUI as vtxColor
            reload(vtxColor)
            vtxColor.showWindow()

    def doIt(self, *args):
        dtList = ['Color', 'Vector', 'Integer', 'String', 'Float', 'Boolean', 'Enum', 'Pnt2']
        addAttribute(
            attrName   = self.attrName.get(),
            dataType   = dtList[self.dataType.get()-1],
            addToShape = self.addToShape.get(),
            aiUserData = self.aiUserData.get()
            )
            
def addAttribute( attrName='color', dataType='Vector', addToShape=True, aiUserData=False ):
    dtList = ['Color', 'Vector', 'Integer', 'String', 'Float', 'Boolean', 'Enum', 'Pnt2']

    aiAttrName = 'mtoa_constant_'+attrName

    for item in pm.selected():
        if addToShape:
            item = item.getShape()
        
        if dataType=='Color':
            item.addAttr( aiAttrName, at='float3', usedAsColor=True)
            item.addAttr( aiAttrName+'R', at='float', p=aiAttrName, keyable=True)
            item.addAttr( aiAttrName+'G', at='float', p=aiAttrName, keyable=True)
            item.addAttr( aiAttrName+'B', at='float', p=aiAttrName, keyable=True)
        
        elif dataType=='Vector':
            item.addAttr( aiAttrName, at='double3')
            item.addAttr( aiAttrName+'X', p=aiAttrName, keyable=True)
            item.addAttr( aiAttrName+'Y', p=aiAttrName, keyable=True)
            item.addAttr( aiAttrName+'Z', p=aiAttrName, keyable=True)

        elif dataType=='Float':
            item.addAttr( aiAttrName, at='double', keyable=True)

        elif dataType=='Integer':
            item.addAttr( aiAttrName, at='long', keyable=True)

        elif dataType=='String':
            item.addAttr( aiAttrName, dt='string', keyable=True)
        
        elif dataType=='Boolean':
            item.addAttr( aiAttrName, at='bool', keyable=True)

        elif dataType=='Enum':
            item.addAttr( aiAttrName, at='enum', enumName='Green:Blue:', keyable=True)

    if aiUserData:
        nodeName = 'ai_'+attrName 

        if dataType=='Color':
            node = pm.createNode('aiUserDataColor', n=nodeName )
            node.colorAttrName.set(attrName)
        
        elif dataType=='Vector':
            node = pm.createNode('aiUserDataVector', n=nodeName )
            node.vectorAttrName.set(attrName)

        elif dataType=='Float':
            node = pm.createNode('aiUserDataFloat', n=nodeName )
            node.floatAttrName.set(attrName)

        elif dataType=='Integer':
            node = pm.createNode('aiUserDataInt', n=nodeName )
            node.intAttrName.set(attrName)

        elif dataType=='String':
            node = pm.createNode('aiUserDataString', n=nodeName )
            node.stringAttrName.set(attrName)
        
        elif dataType=='Boolean':
            node = pm.createNode('aiUserDataBool', n=nodeName )
            node.boolAttrName.set(attrName)

        elif dataType=='Enum':
            node = pm.createNode('aiUserDataPnt2', n=nodeName )
            node.pnt2AttrName.set(attrName)
