# coding=utf-8

import pymel.core as pm
import general as sm

win   = 'sceneMakingUI'
title = 'I am Scene Builder'

currentPath = '/'.join( __file__.split('\\')[:-1] ) + '/'
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
            with pm.columnLayout(adj=True):
                with pm.tabLayout(tv=False):
                    with pm.frameLayout(lv=False, cll=False, mw=2, mh=2, bv=False):
                        with pm.rowLayout(nc=3, adj=2):
                            pm.image( image = shelfIcon )
                            pm.text(l=' %s'%title, fn='boldLabelFont', align='left')
                            pm.image( image = alfredIcon )

                pm.separator( h=8, style='in')
                
                with pm.frameLayout(lv=False, cll=False, mw=0, mh=0, bv=False):
                    with pm.frameLayout(lv=False, cll=False, mw=3, mh=3, bv=False):

    # Scene -----------------------
                        with pm.frameLayout(l='Scene', cll=True, mw=3, mh=3 ):
                            with pm.columnLayout(adj=True):

                                with pm.rowLayout( nc=10 ):
                                    pm.text(label='Reference Editor 2 : ', align='right', w=150)
                                    pm.button(label='Open UI...', w=180, en=False )   

                                with pm.rowLayout( nc=10 ):
                                    pm.text(label='File Traveler : ', align='right', w=150)
                                    pm.button(label='Open UI...', w=180, en=False ) 

    # Camera -----------------------
                        with pm.frameLayout(l='Camera', cll=True, mw=3, mh=3 ):
                            with pm.columnLayout(adj=True):

                                with pm.rowLayout( nc=10 ):
                                    pm.text(label='Create Camera : ', align='right', w=150)
                                    with pm.columnLayout():
                                        pm.button(label='Create Turntable Camera', w=180, en=False )
                                        pm.button(label='Create Frustum Camera', w=180, en=False )
                                        pm.button(label='Create Stereo Camera', w=180, en=False )   

                                with pm.rowLayout( nc=10 ):
                                    pm.text(label='Set Camera Playback Range : ', align='right', w=150)
                                    pm.button(label='set', c=pm.Callback( sm.setCamPlaybackRange ), w=180 )  
                                    
                                with pm.rowLayout( nc=10 ):
                                    pm.text(label='HUD : ', align='right', w=150)
                                    pm.button(label='Scene Name HUD', w=180, en=False )

                                with pm.rowLayout( nc=10 ):
                                    pm.text(label='Export Camera : ', align='right', w=150)
                                    pm.button(label='for After Effect...', w=180, en=False )
                                
    # Asset -----------------------
                        with pm.frameLayout(l='Asset', cll=True, mw=3, mh=3 ):
                            with pm.columnLayout(adj=True):
                                with pm.rowLayout( nc=10 ):
                                    pm.text(label='Toggle Display CharacterGeo : ', align='right', w=150)
                                    pm.button(label='( preview / render )', c=pm.Callback( sm.toggleDisplayCharacterGeo ), w=180 )



