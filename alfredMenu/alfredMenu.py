# coding: utf-8
import pymel.core as pm

def show():
    if pm.menu('alfredTools2', exists=True): pm.deleteUI('alfredTools2')

    gMainWindow = pm.melGlobals['gMainWindow']
    
    # 마야 상단에 메뉴 생성
    alfredToolsMenu = pm.menu('alfredTools2', 
        label = "Alfred Tools 2",
        parent = gMainWindow, 
        tearOff = True, 
        allowOptionBoxes = True,
        #familyImage = familyImage,
        #mnemonic = 'alfred', # 뭔지 모르겠음.
        #helpMenu = True,     # help메뉴 뒤로감
        )
    pm.menuItem( dl='Asset', divider=True, p=alfredToolsMenu )
    pm.menuItem( l='Modeling', p=alfredToolsMenu, en=False )
    pm.menuItem( l='Surfacing', p=alfredToolsMenu, en=False ) 
    pm.menuItem( l='Rigging', p=alfredToolsMenu, c=pm.Callback( menuCmd_rig ) )
    pm.menuItem( dl='Layout', divider=True, p=alfredToolsMenu )
    pm.menuItem( l='Shot', p=alfredToolsMenu, c=pm.Callback(menuCmd_layout) )
    pm.menuItem( dl='Animation', divider=True, p=alfredToolsMenu )
    pm.menuItem( l='Animation', p=alfredToolsMenu, en=False  )
    pm.menuItem( l='Motion Capture', p=alfredToolsMenu, c=pm.Callback( menuCmd_motionCapture ) )
    pm.menuItem( dl='FX', divider=True, p=alfredToolsMenu )
    pm.menuItem( l='FX', p=alfredToolsMenu, en=False ) 
    pm.menuItem( dl='Render', divider=True, p=alfredToolsMenu )
    pm.menuItem( l='Scene Assembly', p=alfredToolsMenu, en=False ) 
    pm.menuItem( l='Lighting', p=alfredToolsMenu, en=False )       
    pm.menuItem( l='Render', p=alfredToolsMenu, c=pm.Callback(menuCmd_render) )
    
def menuCmd_rig():
    import rig
    rig.ui()

def menuCmd_motionCapture():
    import motionCapture 
    motionCapture.ui()

def menuCmd_render():
    import render
    render.ui()

def menuCmd_layout():
    import sceneMaking
    sceneMaking.ui()
