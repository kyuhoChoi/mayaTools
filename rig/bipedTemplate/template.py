# coding=utf-8
'''
import rig
reload(rig)
rig.template.loadJoint()
rig.template.arm()
rig.template.leg()
'''
import pymel.core as pm
import utils as ut
reload(ut)

def importJoint():
    path = '/'.join( __file__.split('\\')[:-1] ) + '/masterJoint.mb'
    pm.importFile( path )

def loadJoint():
    path = '/'.join( __file__.split('\\')[:-1] ) + '/masterJoint.mb'
    pm.openFile( path, f=True )

def arm():   
    arm = ut.Limb('LeftArm','LeftForeArm','LeftHand', prefix='Arm', aimVec='x', startUpVec='y', startWorldUpVec='y', middleUpVec='-z', middleWorldUpVec='-z', endUpVec='y', endWorldUpVec='y')
    arm.create()

def fingers():
    index = ut.Finger( prefix='indexFinger',  joints=['LeftHandIndex1','LeftHandIndex2','LeftHandIndex3','LeftHandIndex4'],      worldUpVec='y' )
    middle = ut.Finger( prefix='middleFinger', joints=['LeftHandMiddle1','LeftHandMiddle2','LeftHandMiddle3','LeftHandMiddle4'], worldUpVec='y' )
    ring   = ut.Finger( prefix='ringFinger',   joints=['LeftHandRing1','LeftHandRing2','LeftHandRing3','LeftHandRing4'],         worldUpVec='y' )
    pinky  = ut.Finger( prefix='pinkyFinger',  joints=['LeftHandPinky1','LeftHandPinky2','LeftHandPinky3','LeftHandPinky4'],     worldUpVec='y' )
    thumb  = ut.Finger( prefix='thumbFinger',  joints=['LeftHandThumb2','LeftHandThumb3','LeftHandThumb4'],                      worldUpVec='y' )

    index .create()
    middle.create()
    ring  .create()
    pinky .create()
    thumb .create()

def leg():
    leg = ut.Limb('LeftUpLeg','LeftLeg','LeftFoot', prefix='Leg')
    leg.create()

def foot():
    foot = ut.Foot()
    foot.create()

def head():
    head = ut.Head()
    head.create()

def torso():
    torso = ut.Torso()
    torso.create()

def jointScaler():
    root = pm.group(em=True)
    for jnt in pm.selected():
        grp = pm.group(n=jnt+'_tmp', em=True)
        grp.displayHandle.set(True)
        pm.delete( pm.parentConstraint( jnt, grp) )
        const = pm.parentConstraint( grp, jnt )
        pm.parent( const, grp )
        pm.parent( grp, root )