# -*- coding:utf-8 -*-
import pymel.core as pm
import alfredTools.ui.v140210 as ui
reload(ui)

import shaderConverter as sc
reload(sc)

class Window(ui.Window):
    def __init__(self):
        super(Window,self).__init__()
        self.title    = 'Shader Converter (v0.1)'
        self.icon     = 'shelf_shaderConverter.png'
        #self.commonBtnLabel = 'Convert'
        self.useCommonBtn = False

        self.selectedTab     = ui.optionVar('selectedTab', 1)
        self.collapseFrames  = ui.optionVar('collapseFrames',[0,0,0,1,0,0,0,0,0] )


        self.selectOpt       = ui.optionVar('selectOpt', 2)

        self.deleteOldShader = ui.optionVar('deleteOldShader', True)
        self.assignToObject  = ui.optionVar('assignToObject', True)
        self.addSubfix       = ui.optionVar('addSubfix', True)
        self.processDisplay  = ui.optionVar('processDisplay', False)
        self.reconnectHwTx   = ui.optionVar('reconnectHwTx', True)

        self.setAiOpaque     = ui.optionVar('setAiOpaque', True)        

        self.floatVal    = ui.optionVar('floatVal', 40)
        self.intVal      = ui.optionVar('intVal', 5)
        self.stringVal   = ui.optionVar('stringVal', 'stringVal( ui.optionVar )')
        self.nodeNameVal = ui.optionVar('nodeNameVal', None)

        #self.collapseFrames.setDefault()
        #print self.collapseFrames.get()
        #self.deleteOldShader.setDefault()
        #self.assignToObject.setDefault()
        #self.addSubfix.setDefault()
    
    def ui(self):
        frameLayOpt  = dict( cll=True, bs='etchedIn', mw=3, mh=3 )
        rowLayOpt    = dict( nc=2 )
        textLabelOpt = dict( align='right', width=250)

        #with pm.frameLayout(lv=False, bv=False,mw=3, mh=3):
        with ui.stackLayout(adj=1, mw=3, mh=3):
            with pm.tabLayout( scr=True, cr=True ) as self.tabLay:
                # Arnold --------------------------------------------------------------------------------
                with pm.frameLayout(lv=False, bv=False,mw=3, mh=3):
                    with pm.columnLayout(adj=1):
                        '''
                        with pm.tabLayout( tv=False ):
                            with pm.columnLayout(adj=1):
                                pm.text(l="Solid Angle Arnold", h= 32, en=False)
                        pm.separator( h=6, style='none')
                        '''
                        with pm.frameLayout(lv=False, bv=True, bs='etchedIn', mw=3, mh=3):
                            with pm.columnLayout(adj=1):
                                pm.checkBoxGrp( l='Arnold options : ', ncb=1, vr=True,
                                    l1='Set opaque (Shape node)', v1=self.setAiOpaque.get(), cc1=self.setAiOpaque.set,
                                    #l2='Assign To Object',  v2=self.assignToObject.get(), cc2=self.assignToObject.set,
                                    #l3='self.boolAttr3', v3=self.boolAttr3.get(), cc3=self.boolAttr3.set 
                                    )                                    
                        pm.separator( h=6, style='none')

                        #with pm.frameLayout( l=u'Maya Software → Arnold', **frameLayOpt):
                        with pm.frameLayout( l=u'Maya Software → Arnold', cl=self.collapseFrames.get()[0], cc=pm.Callback( self.frameColCmd, 0, 1 ), ec=pm.Callback( self.frameColCmd, 0, 0 ), **frameLayOpt):
                            with pm.columnLayout(adj=1):
                                with pm.rowLayout( **rowLayOpt ):
                                    pm.text(l=u'Lambert, Blinn, Phong, PhongE  →  aiStandard : ', **textLabelOpt )
                                    pm.button(l='Convert', c=pm.Callback( self.mayaShader_to_aiStandard ) )                       
                        
                        #with pm.frameLayout( l=u'Mentalray → Arnold', **frameLayOpt):
                        with pm.frameLayout( l=u'Mentalray → Arnold', cl=self.collapseFrames.get()[1], cc=pm.Callback( self.frameColCmd, 1, 1 ), ec=pm.Callback( self.frameColCmd, 1, 0 ), **frameLayOpt):
                            with pm.columnLayout(adj=1):
                                with pm.rowLayout( en=False, **rowLayOpt ):
                                    pm.text(l=u'mia_material_x  →  aiStandard : ', **textLabelOpt )
                                    pm.button(l='Convert')
                                
                                with pm.rowLayout( en=False, **rowLayOpt ):
                                    pm.text(l=u'mia_car_paint_phen_x  →  aiStandard : ', **textLabelOpt )
                                    pm.button(l='Convert')
                        #with pm.frameLayout( l=u'Vray → Arnold', **frameLayOpt):
                        with pm.frameLayout( l=u'Vray → Arnold', cl=self.collapseFrames.get()[2], cc=pm.Callback( self.frameColCmd, 2, 1 ), ec=pm.Callback( self.frameColCmd, 2, 0 ), **frameLayOpt):
                            with pm.columnLayout(adj=1):
                                with pm.rowLayout( **rowLayOpt ):
                                    pm.text(l=u'VRayMtl  →  aiStandard : ', **textLabelOpt )
                                    pm.button(l='Convert', c=pm.Callback( self.VRayMtl_to_aiStandard ) )

                # Vray --------------------------------------------------------------------------------
                with pm.frameLayout(lv=False, bv=False,mw=3, mh=3, en=False):
                    with pm.columnLayout(adj=True):
                        pm.button()
                
                # Mentalray ---------------------------------------------------------------------------
                with pm.frameLayout(lv=False, bv=False,mw=3, mh=3, en=False):
                    with pm.columnLayout(adj=True):
                        pm.button()
                
                # Maya Software -----------------------------------------------------------------------
                with pm.frameLayout(lv=False, bv=False,mw=3, mh=3, en=False):
                    with pm.columnLayout(adj=True):
                        pm.button()
            with pm.frameLayout( l=u'Advanced Options', cl=self.collapseFrames.get()[3], cc=pm.Callback( self.frameColCmd, 3, 1 ), ec=pm.Callback( self.frameColCmd, 3, 0 ), **frameLayOpt):
                with pm.columnLayout(adj=True):
                    pm.radioButtonGrp( l='Select : ', nrb=2, vr=True, cw4=(140,30,30,30),
                        select=self.selectOpt.get(), 
                        l1='Selected shaders only',     on1=pm.Callback( self.selectOpt.set, 1),
                        l2='All Shaders in this scene', on2=pm.Callback( self.selectOpt.set, 2),
                        #l3='3', on3=pm.Callback( self.selectOpt.set, 3),
                        )
                    pm.separator( h=8, style='in')
                    pm.checkBoxGrp( l='Options : ', numberOfCheckBoxes=4, vertical=True,
                        l1='Delete old shader',             v1=self.deleteOldShader.get(),  cc1=self.deleteOldShader.set,
                        l2='Assign to object',              v2=self.assignToObject.get(),   cc2=self.assignToObject.set,
                        l3='Add subfix',                    v3=self.addSubfix.get(),        cc3=self.addSubfix.set,
                        l4='Reconnect Hardware Texture',    v4=self.reconnectHwTx.get(),    cc4=self.reconnectHwTx.set,
                        
                    )
                    pm.checkBoxGrp( l='', numberOfCheckBoxes=1, vertical=True,                        
                        l1='Display process (slow)',   v1=self.processDisplay.get(),  cc1=self.processDisplay.set,
                        #l2='Assign to object',  v2=self.assignToObject.get(),  cc2=self.assignToObject.set,
                        #l3='Add subfix',        v3=self.addSubfix.get(),       cc3=self.addSubfix.set,
                        #l4='Display process (slow)',   v4=self.processDisplay.get(),  cc4=self.processDisplay.set,
                    )
        #
        # 탭 조정
        #
        self.tabLay.setTabLabel( [
            ( self.tabLay.getChildren()[0], 'Arnold'),
            ( self.tabLay.getChildren()[1], 'VRay'),
            ( self.tabLay.getChildren()[2], 'Mentalray'),
            ( self.tabLay.getChildren()[3], 'Maya Software'),
            ] )        
        self.tabLay.changeCommand( lambda: self.selectedTab.set( self.tabLay.getSelectTabIndex() ) )
        try:
            self.tabLay.setSelectTabIndex( self.selectedTab.get() )
        except:
            self.selectedTab.set(1)
            self.tabLay.setSelectTabIndex( self.selectedTab.get() )

    def frameColCmd( self, *args ):
        val = list( self.collapseFrames.get() )        
        val[ args[0] ] = args[1]       
        self.collapseFrames.set( val )
    
    def mayaShader_to_aiStandard(self):
        for mayaShader in self.getSelected( ['lambert','blinn','phong','phongE']):
            sc.mayaShader_to_aiStandard( mayaShader, 
                deleteOldShader = self.deleteOldShader.get(), 
                assignToObject  = self.assignToObject.get(), 
                setAiOpaque     = self.setAiOpaque.get(),  
                addSubfix       = self.addSubfix.get(),
                processDisplay  = self.processDisplay.get(),
                reconnectHwTx   = self.reconnectHwTx.get()
                )
    
    def VRayMtl_to_aiStandard(self):        
        for VRayMtl in self.getSelected('VRayMtl'):
            sc.VRayMtl_to_aiStandard( VRayMtl, 
                deleteOldShader = self.deleteOldShader.get(), 
                assignToObject  = self.assignToObject.get(), 
                setAiOpaque     = self.setAiOpaque.get(),  
                addSubfix       = self.addSubfix.get(),
                processDisplay  = self.processDisplay.get(),
                reconnectHwTx   = self.reconnectHwTx.get()
                )

    def getSelected(self, shaderType):
        sel = []
        if self.selectOpt.get() == 1:
            sel = pm.ls( sl=True, type=shaderType )
            if not sel: 
                pm.confirmDialog( m=u'VRayMtl 노드를 선택하고 실행해 주세요.' )
                return []
        else:
            sel = pm.ls( type=shaderType )
            if not sel: 
                pm.confirmDialog( m=u'scene에 VRayMtl노드가 존재하지 않습니다.' )
                return []
        
        return sel

def showWindow():
    win = Window()
    win.showWindow()


