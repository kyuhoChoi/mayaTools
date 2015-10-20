# coding=utf-8
import pymel.core as pm

win   = 'alfredRenderHelpToolsUI'
title = 'Alfred Render Help Tools'
labelWidth  = 160

currentPath = '/'.join( __file__.split('\\')[:-1] ) + '/'
moduleRoot  = '/'.join( __file__.split('\\')[:-2] ) + '/'
iconPath    = currentPath + 'icon/'
shelfIcon   = iconPath + 'shelf_icon.png' 
alfredIcon  = iconPath + 'alfredLogo.png'

#
# window
#
def ui():
    if pm.window(win, q=True, exists=True ): 
        pm.deleteUI(win)

    with pm.window(win, wh=[300,600], t=title):
        with pm.frameLayout( lv=False, cll=False, mw=1, mh=1):
            with pm.formLayout() as mainForm:
                #with pm.columnLayout(adj=True)
                with pm.tabLayout(tv=False) as top:
                    with pm.frameLayout(lv=False, cll=False, mw=2, mh=2, bv=False):
                        with pm.rowLayout(nc=3, adj=2):
                            pm.image( image = shelfIcon )
                            pm.text(l='  %s'%title, fn='boldLabelFont', align='left')
                            pm.image( image = alfredIcon )
               
                with pm.tabLayout(tv=False, scr=True, childResizable=True) as mid:                  
                    #with pm.frameLayout(lv=False, cll=False, mw=0, mh=0, bv=False):
                    with pm.columnLayout(adj=True):
                    #with pm.frameLayout(lv=False, cll=False, mw=3, mh=3, bv=False):

                    # Contents Start -----------------------
                        uiContents()
                    # Contents End -----------------------

                with pm.columnLayout(adj=True) as btm:
                    pm.helpLine()


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
        #attachPosition=[
        #    (b1, 'right', 5, 75), 
        #    (column, 'left', 0, 75)
        #    ], 
        #attachNone=(b2, 'top') 
        )

def uiContents():
    with pm.frameLayout(l='Surfacing', cll=True, mw=3, mh=3 ):
        with pm.columnLayout( adj=True ):

            with pm.rowLayout(nc=10):
                pm.text(l='Assign Initial Shading Group : ', w= labelWidth, align='right')
                pm.button( l='Assign', w= 160, c=pm.Callback( btn_assignInitialShader ))
            
            with pm.rowLayout(nc=10):
                pm.text(l='File Texture Manager : ', w= labelWidth, align='right')
                pm.button( l='Open UI..', w= 160, c=pm.Callback( btn_fileTextureManager ))
                pm.button(l='d', w=20, c=pm.Callback( pm.launch, web="http://www.creativecrash.com/maya/script/filetexturemanager") )
                pm.button(l='t', w=20, c=pm.Callback( pm.launch, web="https://www.youtube.com/watch?v=3bSkVoo6glU") )

            with pm.frameLayout(l='Arnold', cll=True, mw=3, mh=3 ):
                with pm.columnLayout( adj=True ):
                    with pm.rowLayout(nc=10):
                        pm.text(l='Arnold Add Attr : ', w= labelWidth, align='right')
                        pm.button( l='Open UI..', w= 160, c=pm.Callback( btn_arnoldAddAttr ))

                    with pm.rowLayout(nc=10):
                        pm.text(l='Arnold Mesh Subdiv Render : ', w= labelWidth, align='right')
                        pm.button( l='Arnold Mesh Subdiv Render', w= 160, c=pm.Callback( btn_arnoldSubdiv ))

    with pm.frameLayout(l='Preview Render', cll=True, mw=3, mh=3 ):
        with pm.columnLayout( adj=True ):

            with pm.rowLayout(nc=4):
                pm.text(l='Create Camera Solid BG : ', w= labelWidth, align='right')
                pm.button( l='Create', w= 160, c=pm.Callback( btn_createCamSolidBG ))

            with pm.rowLayout(nc=4):
                pm.text(l='Save All RenderView Images : ', w= labelWidth, align='right')
                pm.button( l='Save', w= 160, c=pm.Callback( btn_saveAllRenderViewImages ))

    with pm.frameLayout(l='Render', cll=True, mw=3, mh=3 ):
        with pm.columnLayout( adj=True ):

            with pm.rowLayout(nc=4):
                pm.text(l='Backburner Script : ', w= labelWidth, align='right')
                pm.button( l='Open UI..', w= 160, c=pm.Callback( btn_backburnner ))



def btn_assignInitialShader():
    import general as mdl
    reload(mdl)
    mdl.assignInitialShader()

def btn_createCamSolidBG():
    import general as mdl
    reload(mdl)
    mdl.createCamSolidBG()

def btn_saveAllRenderViewImages():
    import general as mdl
    reload(mdl)
    mdl.saveAllRenderViewImages()

def btn_backburnner():
    import render.backburnerTools as bb
    reload(bb)
    bb.ui()

def btn_fileTextureManager():
    pm.mel.source(currentPath + 'mel/FileTextureManager.mel')
    pm.mel.FileTextureManager()

def btn_arnoldAddAttr():
    import render.arnold.arnold_addAttr_ui as arnoldTool
    reload(arnoldTool)
    arnoldTool.ui()

def btn_arnoldSubdiv():
    import general as mdl
    reload(mdl)
    mdl.arnold_subDiv()
    