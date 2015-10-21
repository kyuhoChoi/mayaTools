# coding=utf-8
import pymel.core as pm

win   = 'arnold_addAttrUI'
title = 'Add Arnold Attribute'
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
    '''
    update : 2015-04-24
    '''
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
                    with pm.columnLayout(adj=True):
                        uiContents()

                #with pm.columnLayout(adj=True) as btm:
                #   pm.helpLine()

                with pm.horizontalLayout() as btm:         
                    pm.button()
                    pm.button()
                    pm.button()

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
            (mid, 'bottom', 3, btm)            
            ]          
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

def btn_assignInitialShader():
    pass

def btn_fileTextureManager():
    pass