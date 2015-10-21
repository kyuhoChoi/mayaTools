# coding=utf-8
#
# TODO :
# 스키닝 트랜스퍼를 위해 조인트 라벨 세팅 필요.
#
#
import pymel.core as pm
import copy

class TwistHelper( object ):
    '''
    version : 2015-04-21
    '''
    def __init__(self, prefix='', divide=4, distribute=True, stretch=False, upVector='y', startWorldUpVector='y', endWorldUpVector='y'):        
        #
        # 변수 설정
        #
        self.prefix = prefix
        self.div = divide
        self.distribute = distribute        
        self.upVector           = self._strToVec(upVector)
        self.startWorldUpVector = self._strToVec(startWorldUpVector)
        self.endWorldUpVector   = self._strToVec(endWorldUpVector)
        self.stretch = stretch

        # 상수
        self.aimVector = self._strToVec('x')

        # 생성
        self.create()

        # 프리픽스 설정
        if self.prefix:
            self.setPrefix()

        # 벡터
        self.setUpVector()
        self.setStartWorldUpVector()
        self.setEndWorldUpVector()
        
        # 커브컨트롤러 설정
        self.setLook()
        
    def create(self):
        self.nodes = []

        #------------------------------
        #
        # Create Ctrler
        #
        #------------------------------
        self.root_grp = pm.group( n='TwistHelper_grp', em=True)
        self.constMe_to_parent = pm.group( n='constMe_to_parent', em=True)
        self.constMe_to_start  = pm.group( n='constMe_to_start', em=True)
        self.constMe_to_mid    = pm.group( n='constMe_to_mid', em=True )
        self.constMe_to_end    = pm.group( n='constMe_to_end', em=True)
        self.doNotTouch_grp  = pm.group( n='doNotTouch_grp', em=True)
        pm.parent( self.constMe_to_start, self.constMe_to_mid, self.constMe_to_end, self.constMe_to_parent)
        pm.parent( self.constMe_to_parent, self.doNotTouch_grp, self.root_grp )

        self.start_T_anim = pm.group( n='start_T_anim', em=True)
        self.end_T_anim   = pm.group( n='end_T_anim', em=True)
        pm.parent( self.start_T_anim, self.constMe_to_start )
        pm.parent( self.end_T_anim,   self.constMe_to_end )

        self.mid_T_anim   = pm.group( n='mid_T_anim', em=True )
        self.mid1_T_anim  = pm.group( n='mid1_T_anim', em=True )
        self.mid2_T_anim  = pm.group( n='mid2_T_anim', em=True )
        pm.parent( self.mid1_T_anim, self.mid2_T_anim, self.mid_T_anim )
        pm.parent( self.mid_T_anim, self.constMe_to_mid )

        self.start_R_result = pm.group( n='start_R_result', em=True)
        self.start_up_anim  = pm.group( n='start_up_anim', em=True)
        pm.parent( self.start_R_result, self.start_up_anim, self.start_T_anim )

        self.end_R_result = pm.group( n='end_R_result', em=True)
        self.end_up_anim  = pm.group( n='end_up_anim', em=True)
        pm.parent( self.end_R_result, self.end_up_anim, self.end_T_anim )

        self.doNotTouch_grp.v.set(False)        

        # 어트리뷰트 잠금
        self._lockAndHideAttr([self.start_up_anim, self.end_up_anim],['rx','ry','rz','sx','sy','sz'])
        self._lockAndHideAttr([self.constMe_to_start, self.constMe_to_mid, self.constMe_to_end, self.mid_T_anim, self.constMe_to_parent],['sx','sy','sz','v'])
        self._lockAndHideAttr([self.start_R_result, self.end_R_result],['sx','sy','sz','v'])
        self._lockAndHideAttr([self.start_T_anim, self.end_T_anim, self.mid1_T_anim, self.mid2_T_anim],['rx','ry','rz','sx','sy','sz','v'])
        self._lockAndHideAttr([self.doNotTouch_grp, self.root_grp],['tx','ty','tz','rx','ry','rz','sx','sy','sz'])

        self.nodes.extend([self.root_grp, self.constMe_to_parent, self.constMe_to_start, self.constMe_to_mid, self.constMe_to_end, self.doNotTouch_grp, self.start_T_anim, self.end_T_anim, self.mid_T_anim, self.mid1_T_anim, self.mid2_T_anim, self.start_R_result, self.start_up_anim])
        self.nodes.extend([self.end_R_result, self.end_up_anim])

        #------------------------------
        #
        # config Attribute
        #
        #------------------------------
        ctrl = self.root_grp
        ctrl.addAttr('aimAxis', at='enum', en='PositiveX:NegativeX:', keyable=False) # IK핸들의 Advanced Twist Controls 세팅이 -x축은 고려되어 있지 않음. 의미 없음.
        ctrl.addAttr('aimVector', at='double3')
        ctrl.addAttr('aimVectorX', at='double', p='aimVector', keyable=False)
        ctrl.addAttr('aimVectorY', at='double', p='aimVector', keyable=False)
        ctrl.addAttr('aimVectorZ', at='double', p='aimVector', keyable=False)
        ctrl.addAttr('upAxis', at='enum', en='PositiveY:NegativeY:ClosetY:PositiveZ:NegativeZ:ClosetZ:', keyable=True)
        ctrl.addAttr('upVector', at='double3')
        ctrl.addAttr('upVectorX', at='double', p='upVector', keyable=True)
        ctrl.addAttr('upVectorY', at='double', p='upVector', keyable=True)
        ctrl.addAttr('upVectorZ', at='double', p='upVector', keyable=True)
        ctrl.addAttr('startWorldUpVector', at='double3')
        ctrl.addAttr('startWorldUpVectorX', at='double', p='startWorldUpVector', keyable=True)
        ctrl.addAttr('startWorldUpVectorY', at='double', p='startWorldUpVector', keyable=True)
        ctrl.addAttr('startWorldUpVectorZ', at='double', p='startWorldUpVector', keyable=True)
        ctrl.addAttr('endWorldUpVector', at='double3')
        ctrl.addAttr('endworldUpVectorX', at='double', p='endWorldUpVector', keyable=True)
        ctrl.addAttr('endworldUpVectorY', at='double', p='endWorldUpVector', keyable=True)
        ctrl.addAttr('endworldUpVectorZ', at='double', p='endWorldUpVector', keyable=True)
        ctrl.aimVector.set(self.aimVector)
        ctrl.upVector.set(self.upVector)
        ctrl.startWorldUpVector.set(self.startWorldUpVector)
        ctrl.endWorldUpVector.set(self.endWorldUpVector)

        pm.setDrivenKeyframe( ctrl.aimVectorX, value= 1, currentDriver=ctrl.aimAxis, driverValue=0 ) # positiveX
        pm.setDrivenKeyframe( ctrl.aimVectorY, value= 0, currentDriver=ctrl.aimAxis, driverValue=0 ) # positiveX
        pm.setDrivenKeyframe( ctrl.aimVectorZ, value= 0, currentDriver=ctrl.aimAxis, driverValue=0 ) # positiveX
        pm.setDrivenKeyframe( ctrl.aimVectorX, value=-1, currentDriver=ctrl.aimAxis, driverValue=1 ) # negativeX
        pm.setDrivenKeyframe( ctrl.aimVectorY, value= 0, currentDriver=ctrl.aimAxis, driverValue=1 ) # negativeX
        pm.setDrivenKeyframe( ctrl.aimVectorZ, value= 0, currentDriver=ctrl.aimAxis, driverValue=1 ) # negativeX

        pm.setDrivenKeyframe( ctrl.upVectorX, value= 0, currentDriver=ctrl.upAxis, driverValue=0 ) # positiveY
        pm.setDrivenKeyframe( ctrl.upVectorY, value= 1, currentDriver=ctrl.upAxis, driverValue=0 ) # positiveY
        pm.setDrivenKeyframe( ctrl.upVectorZ, value= 0, currentDriver=ctrl.upAxis, driverValue=0 ) # positiveY
        pm.setDrivenKeyframe( ctrl.upVectorX, value= 0, currentDriver=ctrl.upAxis, driverValue=1 ) # negativeY
        pm.setDrivenKeyframe( ctrl.upVectorY, value=-1, currentDriver=ctrl.upAxis, driverValue=1 ) # negativeY
        pm.setDrivenKeyframe( ctrl.upVectorZ, value= 0, currentDriver=ctrl.upAxis, driverValue=1 ) # negativeY
        pm.setDrivenKeyframe( ctrl.upVectorX, value= 0, currentDriver=ctrl.upAxis, driverValue=3 ) # positiveZ
        pm.setDrivenKeyframe( ctrl.upVectorX, value= 0, currentDriver=ctrl.upAxis, driverValue=2 ) # negativeY
        pm.setDrivenKeyframe( ctrl.upVectorY, value= 1, currentDriver=ctrl.upAxis, driverValue=2 ) # negativeY
        pm.setDrivenKeyframe( ctrl.upVectorZ, value= 0, currentDriver=ctrl.upAxis, driverValue=2 ) # negativeY
        pm.setDrivenKeyframe( ctrl.upVectorX, value= 0, currentDriver=ctrl.upAxis, driverValue=3 ) # positiveZ
        pm.setDrivenKeyframe( ctrl.upVectorY, value= 0, currentDriver=ctrl.upAxis, driverValue=3 ) # positiveZ
        pm.setDrivenKeyframe( ctrl.upVectorZ, value= 1, currentDriver=ctrl.upAxis, driverValue=3 ) # positiveZ
        pm.setDrivenKeyframe( ctrl.upVectorX, value= 0, currentDriver=ctrl.upAxis, driverValue=4 ) # negativeZ
        pm.setDrivenKeyframe( ctrl.upVectorY, value= 0, currentDriver=ctrl.upAxis, driverValue=4 ) # negativeZ
        pm.setDrivenKeyframe( ctrl.upVectorZ, value=-1, currentDriver=ctrl.upAxis, driverValue=4 ) # negativeZ
        pm.setDrivenKeyframe( ctrl.upVectorX, value= 0, currentDriver=ctrl.upAxis, driverValue=5 ) # negativeZ
        pm.setDrivenKeyframe( ctrl.upVectorY, value= 0, currentDriver=ctrl.upAxis, driverValue=5 ) # negativeZ
        pm.setDrivenKeyframe( ctrl.upVectorZ, value= 1, currentDriver=ctrl.upAxis, driverValue=5 ) # negativeZ

        ctrl.setAttr('upVectorX', keyable=False )
        ctrl.setAttr('upVectorY', keyable=False )
        ctrl.setAttr('upVectorZ', keyable=False )

        #
        #
        # base Curve
        #
        #
        crv = pm.curve( n='base_crv', d=3, p=[(0,0,0),(0,0,0),(0,0,0),(0,0,0)], k=[0,0,0,1,1,1] )
        pm.parent( crv, self.doNotTouch_grp )
        crv.it.set(False)
        self.nodes.append(crv)

        # create curve cv clusters
        start_crv_clst = pm.cluster( crv.cv[0], wn=(self.start_T_anim,self.start_T_anim) )[0]
        mid1_crv_clst  = pm.cluster( crv.cv[1], wn=(self.mid1_T_anim, self.mid1_T_anim) )[0]
        mid2_crv_clst  = pm.cluster( crv.cv[2], wn=(self.mid2_T_anim, self.mid2_T_anim) )[0]
        end_crv_clst   = pm.cluster( crv.cv[3], wn=(self.end_T_anim,  self.end_T_anim) )[0]
        self.nodes.extend([start_crv_clst,mid1_crv_clst,mid2_crv_clst,end_crv_clst])

        #
        # 초기위치
        #
        self.start_up_anim.t.set( self.upVector * 10)
        self.end_up_anim  .t.set( self.upVector * 10)
        self.constMe_to_end.t.set( self.aimVector * 10)
        pm.delete( pm.pointConstraint(self.start_T_anim, self.end_T_anim, self.constMe_to_mid)  )
        pm.delete( pm.pointConstraint(self.mid_T_anim, self.start_T_anim, self.mid1_T_anim)  )
        pm.delete( pm.pointConstraint(self.mid_T_anim, self.end_T_anim, self.mid2_T_anim)  )

        #
        #
        # rebuild curve for distribute
        #
        #
        # 커브 리빌드, 익스텐드
        rbdCrv, rbd = pm.rebuildCurve( 
            crv, 
            ch=True, 
            replaceOriginal=False, 
            rebuildType=0, # uniform
            endKnots=1,    # 0 - uniform end knots, 1 - multiple end knots
            keepRange=0,   # 0 - reparameterize the resulting curve from 0 to 1, 1 - keep the original curve parameterization, 2 - reparameterize the result from 0 to number of spans
            keepControlPoints=False, 
            keepEndPoints=True, 
            keepTangents=True, 
            spans=100, 
            degree=3, 
            tol=0.001 
            )

        rdbCrv, extCrv = pm.extendCurve( rbdCrv, cos=0, ch=1, jn=True, rmk=True, rpo=True, 
            distance = 1,
            start=0,         # 0 - end, 1 - start, 2 - both
            extendMethod=0,  # 0 - based on distance, 2 - to a 3D point 
            extensionType=0, # 0 - Linear, 1 - Circular, 2 - Extrapolate  
            )

        rdbCrv.rename('rbdExtnd_crv')
        pm.parent( rdbCrv, self.doNotTouch_grp )
        rdbCrv.it.set(False)

        # extend crv Locator
        crvEnd_loc = pm.spaceLocator(n='extCrvEnd_loc')
        pntOnCrv = pm.PyNode( pm.pointOnCurve( rdbCrv.getShape(), parameter=2.0, ch=True ) )
        pntOnCrv.position >> crvEnd_loc.t
        pm.parent( crvEnd_loc, self.doNotTouch_grp )

        self.nodes.extend([ rbdCrv, rbd,extCrv, crvEnd_loc])

        #
        # Cluster & Constraint
        #
        # constraint Rig
        start_aimConst = pm.aimConstraint( self.end_T_anim, self.start_R_result, aim=self.aimVector, u=self.upVector, wu=self.startWorldUpVector, wut='object', wuo=self.start_up_anim)
        mid_pointConst = pm.pointConstraint( self.start_T_anim, self.end_T_anim, self.constMe_to_mid)
        mid_aimConst   = pm.aimConstraint( self.end_T_anim, self.constMe_to_mid, aim=self.aimVector, u=self.upVector, wu=self.startWorldUpVector, wut='objectrotation', wuo=self.start_R_result)
        end_aimConst   = pm.aimConstraint( crvEnd_loc, self.end_R_result,   aim=self.aimVector, u=self.upVector, wu=self.startWorldUpVector, wut='object', wuo=self.end_up_anim)
        self.nodes.extend([ start_aimConst, mid_pointConst, mid_aimConst, end_aimConst ])

        ctrl.aimVector >> start_aimConst.aimVector
        ctrl.aimVector >> mid_aimConst.aimVector
        ctrl.upVector >> start_aimConst.upVector
        ctrl.upVector >> mid_aimConst.upVector
        ctrl.startWorldUpVector >> start_aimConst.worldUpVector
        ctrl.startWorldUpVector >> mid_aimConst.worldUpVector
        
        #
        #   Locators on Curve
        #
        unit = 1.0 / self.div
        locOnCrvs = []
        for i in range(self.div+1):
            param = unit * i

            #xformOnCrv = pm.group( n='xformOnCrv#', em=True)
            xformOnCrv = pm.spaceLocator( n='xformOnCrv#')

            xformOnCrv.addAttr( 'parameter',        sn='pr',  dv=param, keyable=True )
            xformOnCrv.addAttr( 'turnOnPercentage', sn='top', dv=False, at='bool', keyable=True )
            xformOnCrv.addAttr( 'revRotation',  sn='rot', keyable=True )

            xformOnCrv.it.set(False)
            xformOnCrv.rename( 'xformOnCrv%02d'%i )

            pntOnCrv = pm.PyNode( pm.pointOnCurve( rdbCrv.getShape(), parameter=param, ch=True ) )
            pntOnCrv.turnOnPercentage.set(True)
            pntOnCrv.setAttr('parameter',        keyable=True)
            pntOnCrv.setAttr('turnOnPercentage', keyable=True)
            pntOnCrv.rename( xformOnCrv+'_POC' )

            xformOnCrv.parameter        >> pntOnCrv.parameter
            xformOnCrv.turnOnPercentage >> pntOnCrv.turnOnPercentage
            pntOnCrv.position           >> xformOnCrv.t

            locOnCrvs.append(xformOnCrv)

        pm.parent( locOnCrvs, self.doNotTouch_grp )
        self.nodes.extend( locOnCrvs )

        #
        # distance Rig
        #
        distNodes = []
        for i in range(len(locOnCrvs)-1):
            dist = pm.createNode( 'distanceDimShape' )
            locOnCrvs[i].worldPosition[0]   >> dist.startPoint
            locOnCrvs[i+1].worldPosition[0] >> dist.endPoint
            distNodes.append( dist )

        pm.parent( [dist.getParent() for dist in distNodes], self.doNotTouch_grp )
        self.nodes.extend( [dist.getParent() for dist in distNodes] )

        #
        #
        # Joint
        #
        #
        pm.select(cl=True)
        self.jnts = []
        for i in range(self.div+1):
            self.jnts.append( pm.joint( n='bind%d'%i, p=self.aimVector*i ) )

        if self.stretch:
            # 컨트롤러에 어트리뷰트 추가하고, 리깅까지 마침.
            #ctrl = pm.group( em=True)
            ctrl = self.root_grp
            ctrl.addAttr( 'initialDistance', multi=True, readable=True, indexMatters=False )
            ctrl.addAttr( 'currentDistance', multi=True, readable=True, indexMatters=False )
            ctrl.addAttr( 'scaleOutput',     multi=True, readable=True, indexMatters=False )

            for i in range(len(distNodes)):
                ctrl.initialDistance[i].set( distNodes[i].distance.get() )
                distNodes[i].distance >> ctrl.currentDistance[i]
                
                md = pm.createNode('multiplyDivide')
                md.operation.set(2) # divide    
                ctrl.currentDistance[i] >> md.input1X
                ctrl.initialDistance[i] >> md.input2X
                
                md.outputX >> ctrl.scaleOutput[i]

            for i in range(len( ctrl.scaleOutput.get() )):
                ctrl.scaleOutput[i] >> self.jnts[i].sx

        else:
            for dist, jnt in zip(distNodes, self.jnts[1:]):
                #if ctrl.aimAxis==1: # 아임축이 -일경우.
                md = pm.createNode('multiplyDivide')
                dist.distance   >> md.input1X
                ctrl.aimVectorX >> md.input2X
                md.outputX >> jnt.tx
                
                #else:                
                #    dist.distance >> jnt.tx

        self.nodes.extend(self.jnts)

        #
        #
        # spline IK Handle
        #
        #
        ikHandle, endEff = pm.ikHandle(sol='ikSplineSolver', ccv=False, roc=True, pcv=False, ns=4, sj=self.jnts[0], ee=self.jnts[-1], curve=rdbCrv )
        pm.parent(ikHandle, self.doNotTouch_grp )

        # Enable Twist Controls : start, end Sample OBJ
        sampleObj_start = self.start_R_result
        sampleObj_end   = self.end_R_result

        ikHandle.dTwistControlEnable.set(True)                              # Enable Twist Controls
        ikHandle.dWorldUpType.set(4)                                        # 4:Object Rotation Up (Start/End)
        #sampleObj_start.xformMatrix.connect( foreArm_HDL.dWorldUpMatrix )  # << 요렇게 하면 좆됨
        #sampleObj_end.xformMatrix.connect( foreArm_HDL.dWorldUpMatrixEnd ) # << 요렇게 하면 좆됨
        sampleObj_start.worldMatrix >> ikHandle.dWorldUpMatrix              # << 요렇게 해야함.
        sampleObj_end  .worldMatrix >> ikHandle.dWorldUpMatrixEnd           # << 요렇게 해야함.
        ikHandle.dWorldUpAxis.     set(0)                                   # 0:PositiveY, 1:Positive Z
        ikHandle.dWorldUpVector.   set(self.upVector)
        ikHandle.dWorldUpVectorEnd.set(self.upVector)

        ctrl.aimAxis            >> ikHandle.dWorldUpAxis
        ctrl.startWorldUpVector >> ikHandle.dWorldUpVector
        ctrl.endWorldUpVector   >> ikHandle.dWorldUpVectorEnd

        self.nodes.extend([ikHandle,endEff])

    def constraint(self, parent, start, end ):
        # 축을 start에 먼저 맞추고,
        # 축을 유지한 채로 컨스트레인 검.
        pm.delete( pm.parentConstraint(start, self.constMe_to_start) )        
        pm.parentConstraint(parent, self.constMe_to_parent, mo=True)

        pm.pointConstraint(start, self.constMe_to_start)  
        pm.parentConstraint(end, self.constMe_to_end)  

        pm.delete( pm.pointConstraint(self.mid_T_anim, self.start_T_anim, self.mid1_T_anim)  )
        pm.delete( pm.pointConstraint(self.mid_T_anim, self.end_T_anim, self.mid2_T_anim)  )

    def setPrefix(self, prefix=''):
        if prefix:
            self.prefix = prefix
        
        for node in self.nodes:
            node.rename( '%s__%s'%( self.prefix, node ) )

    def setUpVector(self, input=None):
        if input:
            self.upVector = self._strToVec(input)

        # ctrl.aimAxis : 0:PositiveY, 1:NegativeY, 2:ClosetY, 3:PositiveZ, 4:NegativeZ, 5:ClosetZ

        if self.upVector == self._strToVec('y'):        
            self.root_grp.aimAxis.set(0)

        elif self.upVector == self._strToVec('-y'):        
            self.root_grp.aimAxis.set(1)

        elif self.upVector == self._strToVec('z'):        
            self.root_grp.aimAxis.set(3)

        elif self.upVector == self._strToVec('-z'):        
            self.root_grp.aimAxis.set(4)

        # start up ctrler세팅
        scalar = self.start_up_anim.t.get().length()        
        self.start_up_anim.t.set( self.upVector * scalar )

        scalar = self.end_up_anim.t.get().length()   
        self.end_up_anim.t.set( self.upVector * scalar )

    def setStartWorldUpVector(self, input=None):
        if input:
            self.startWorldUpVector = self._strToVec(input)        
        self.root_grp.startWorldUpVector.set(self.startWorldUpVector)

    def setEndWorldUpVector(self, input=None):
        if input:
            self.endWorldUpVector = self._strToVec(input)
        self.root_grp.endWorldUpVector.set(self.endWorldUpVector)

    def setLook(self, scale=5):
        self._setCtrlerShape( self.start_T_anim,  shape='helper', scale=[scale,scale,scale] )
        self._setCtrlerShape( self.end_T_anim,    shape='helper', scale=[scale,scale,scale] )
        self._setCtrlerShape( self.mid_T_anim,    shape='helper', scale=[scale,scale,scale] )
        self._setCtrlerShape( self.mid1_T_anim,   shape='helper', scale=[scale*.8,scale*.8,scale*.8] )
        self._setCtrlerShape( self.mid2_T_anim,   shape='helper', scale=[scale*.8,scale*.8,scale*.8] )
        self._setCtrlerShape( self.start_up_anim, shape='up',     scale=[scale*.2,scale*.2,scale*.2] )
        self._setCtrlerShape( self.end_up_anim,   shape='up',     scale=[scale*.2,scale*.2,scale*.2] )

        #self.start_up_anim.displayHandle.set(True)
        #self.mid_T_anim.displayHandle.set(True)
        #self.start_T_anim.displayHandle.set(True)
        #self.end_T_anim.displayHandle.set(True)

        for jnt in self.jnts:
            jnt.displayLocalAxis.set(True)

        self._rigCurveConnect( self.start_up_anim, self.start_R_result )
        self._rigCurveConnect( self.end_up_anim, self.end_R_result )

    def setDivide(self, divide=None):
        if divide:
            self.div = divide
  
    def _setCtrlerShape(self, transformNode, shape='helper', scale=[1,1,1] ):
        curveShape = None
        if   shape=='helper': # hexagon2D    
            curveShape = pm.curve( d=1, p=[ (4.063704928114475e-17, 0.433013, 0.25), (-1.1102230246251565e-16, 0.0, 0.5), (-1.516593517436604e-16, -0.433013, 0.25), (-4.063704928114475e-17, -0.433013, -0.25), (1.1102230246251565e-16, 0.0, -0.5), (1.516593517436604e-16, 0.433013, -0.25), (4.063704928114475e-17, 0.433013, 0.25) ], k=[ 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0 ] )

        elif shape =='up': # diamond
            curveShape = pm.curve( d=1, p=[ (0.0, 0.0, 0.5), (0.5, 0.0, 0.0), (0.0, 0.0, -0.5), (-0.5, 0.0, 0.0), (0.0, 0.0, 0.5), (0.0, 0.5, 0.0), (0.0, 0.0, -0.5), (0.0, -0.5, 0.0), (0.0, 0.0, 0.5), (0.0, 0.5, 0.0), (0.5, 0.0, 0.0), (0.0, -0.5, 0.0), (-0.5, 0.0, 0.0), (0.0, 0.5, 0.0) ], k=[ 0.0, 0.707106781187, 1.41421356237, 2.12132034356, 2.82842712475, 3.53553390593, 4.24264068712, 4.94974746831, 5.65685424949, 6.36396103068, 7.07106781187, 7.77817459305, 8.48528137424, 9.19238815543 ] )

        curveShape.s.set(scale)
        pm.makeIdentity( curveShape, apply=True, t=True, r=True, s=True )

        pm.parent( curveShape.getShape(), transformNode, s=True, r=True)
        pm.delete( curveShape )
       
    def _strToVec( self, inputVal ):
        '''
        Abstract
        ========
            1. 문자를 벡터형으로 리턴

            2. 예제 :
                >> getVectorByChar( 'x' )
                dt.Vector([1.0, 0.0, 0.0])

                >> getVectorByChar( 'y' )
                dt.Vector([1.0, 1.0, 0.0])

        @param inputVal: 'x','y','z','-x','-y','-z', or vector
        @type inputVal: str | tuple | pm.dt.Vector

        @return : 입력된 캐릭터에 대응하는 벡터
        @rtype : pm.dt.Vector

        @version No : 2015-04-20
        '''

        # 입력된 값이 문자열일경우
        if isinstance( inputVal, str ) or isinstance( inputVal, unicode ):

            # 입력된 값을 앞뒤 빈칸을 없애고, 소문자로 변경
            inputVal = inputVal.strip().lower()

            # 아래 리스트에 없는 값이 들어오면 에러
            if not inputVal in ['x','y','z','-x','-y','-z']:
                raise

            # 매칭
            if   inputVal.lower()== 'x': return pm.dt.Vector( 1, 0, 0)
            elif inputVal.lower()=='-x': return pm.dt.Vector(-1, 0, 0)
            elif inputVal.lower()== 'y': return pm.dt.Vector( 0, 1, 0)
            elif inputVal.lower()=='-y': return pm.dt.Vector( 0,-1, 0)
            elif inputVal.lower()== 'z': return pm.dt.Vector( 0, 0, 1)
            elif inputVal.lower()=='-z': return pm.dt.Vector( 0, 0,-1)

        else:
            return pm.datatypes.Vector( inputVal )

    def _rigCurveConnect( self, *objs, **kwargs ):
        '''
        update : 2015-04-15
        '''
        if objs:
            pm.select(objs)
        
        sel = pm.selected( type='transform')
        if not sel:
            raise

        obj = sel[0]

        # 삭제
        delete = kwargs.get('delete', False)
        if delete:
            for crvShp in obj.getShapes():
                if crvShp.hasAttr('curveConnectedLOC'):
                    try:
                        pm.delete( crvShp, crvShp.curveConnectedLOC.inputs() )
                    except:
                        pass
            return True

        # 타겟 가져옴.
        target = sel[1]

        name     = kwargs.get('name') or kwargs.get('n', target+'_CONNCRV' )
        position = kwargs.get('position') or kwargs.get('p', (0,0,0) )

        # 커브 생성
        crvTrans = pm.curve( n=name, d=1, p=[ position, position ], k=[0,1] )
        crvShape = crvTrans.getShape()

        # obj에 커브 쉐입을 종속 시킴 : 커브를 선택해도 오브젝트를 선택한 효과를 줌.
        pm.parent( crvShape, obj, r=True, s=True)
        pm.delete( crvTrans )

        # target에 locator를 종속 시킴
        loc = pm.pointCurveConstraint( crvShape+'.ep[1]', ch=True)[0]
        loc = pm.PyNode(loc)
        pm.pointConstraint( target, loc )

        # 로케이서 속성 조정
        loc.getShape().localPosition.set(0,0,0)
        loc.getShape().v.set(False)
        loc.v.set(False)
        loc.setParent(obj)
        loc.rename( target+'_CONNLOC' )

        # 커브쉐입에 어트리뷰트 추가
        crvShape.addAttr( 'curveConnectedTo',  at='message' )
        crvShape.addAttr( 'curveConnectedLOC', at='message' )

        # 어트리뷰트 연결
        target.message >> crvShape.curveConnectedTo
        loc.   message >> crvShape.curveConnectedLOC

        return loc

    def _lockAndHideAttr( self, objs=[], attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']):        
        if objs:
            pm.select(objs)

        objs = pm.ls(sl=True)
        
        for obj in objs:
            for attr in attrs:
                pm.setAttr( '%s.%s'%(obj,attr), lock=True, keyable=False, channelBox=False )

def rigTwistHelper( prefix='', divide=4):
    twistHelper = TwistHelper(prefix=prefix, divide=divide)

#
# TDD
#
'''
divide=4

LeftArmTwist = TwistHelper(prefix='LeftArmTwist', divide=divide)
LeftArmTwist.constraint( parent='LeftShoulder', start='LeftArm', end='LeftForeArm')
LeftArmTwist.setUpVector('y')
LeftArmTwist.setStartWorldUpVector('y')
LeftArmTwist.setEndWorldUpVector('y')

LeftForeArmTwist = TwistHelper(prefix='LeftForeArmTwist', divide=divide)
LeftForeArmTwist.constraint( parent='LeftForeArm', start='LeftForeArm', end='LeftHand')
LeftForeArmTwist.setUpVector('-z')
LeftForeArmTwist.setStartWorldUpVector('-z')
LeftForeArmTwist.setEndWorldUpVector('-z')

RightArmTwist = TwistHelper(prefix='RightArmTwist', divide=divide)
RightArmTwist.constraint( parent='RightShoulder', start='RightArm', end='RightForeArm')
RightArmTwist.setUpVector('-y')
RightArmTwist.setStartWorldUpVector('-y')
RightArmTwist.setEndWorldUpVector('-y')

RightForeArmTwist = TwistHelper(prefix='RightForeArmTwist', divide=divide)
RightForeArmTwist.constraint( parent='RightForeArm', start='RightForeArm', end='RightHand')
RightForeArmTwist.setUpVector('z')
RightForeArmTwist.setStartWorldUpVector('-z')
RightForeArmTwist.setEndWorldUpVector('-z')

LeftArmTwist.setUpVector('z')
LeftArmTwist.setStartWorldUpVector('z')
LeftArmTwist.setEndWorldUpVector('z')
LeftForeArmTwist.setUpVector('y')
LeftForeArmTwist.setStartWorldUpVector('y')
LeftForeArmTwist.setEndWorldUpVector('y')
RightArmTwist.setUpVector('-z')
RightArmTwist.setStartWorldUpVector('-z')
RightArmTwist.setEndWorldUpVector('-z')
RightForeArmTwist.setUpVector('-y')
RightForeArmTwist.setStartWorldUpVector('y')
RightForeArmTwist.setEndWorldUpVector('y')
'''