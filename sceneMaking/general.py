# coding=utf-8
import pymel.core as pm

def setCamPlaybackRange():
    modelPanel = pm.playblast(activeEditor=True).split('|')[-1]

    activeCam  = pm.PyNode( pm.modelPanel( modelPanel, q=True, camera=True ) )
    startFrame = activeCam.startFrame.get()
    endFrame   = activeCam.endFrame.get()

    pm.playbackOptions(min=endFrame, max=startFrame)

def toggleDisplayCharacterGeo():
    sel = pm.selected()
    namespace = sel[0].namespace()
    Ref = pm.PyNode( namespace + 'Reference')
    Ref.displayGeo.set( not Ref.displayGeo.get()  )