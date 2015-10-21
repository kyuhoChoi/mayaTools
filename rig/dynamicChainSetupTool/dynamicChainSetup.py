
'''
@author: Riham Tolan
This tool creates a dynamic setup on joints using maya nHair system
Maya: 2014, 2015
example:
from dynamicChainSetupTool import dynamicChainSetup as dc
dc.show()
'''

import maya.cmds as cmds
import shiboken
from PySide import QtGui, QtCore
import os
import maya.OpenMayaUI as mui
import maya.OpenMaya as OpenMaya
import shapes as shapes

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

import pysideuic
import xml.etree.ElementTree as xml
from cStringIO import StringIO

def loadUiType(uiFile):
    """
    :author: Jason Parks
    Pyside lacks the "loadUiType" command, so we have to convert the ui file to py code in-memory first
    and then execute it in a special frame to retrieve the form_class.
    """
    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text
    
    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}
            
        pysideuic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame
            
        #Fetch the base_class and form class based on their type in the xml from designer
        form_class = frame['Ui_%s'%form_class]
        base_class = getattr(QtGui, widget_class)
    return form_class, base_class

def wrapinstance(ptr, base=None):
    """
    :author: Nathan Horne
    Utility to convert a pointer to a Qt class instance (PySide/PyQt compatible)

    :param ptr: Pointer to QObject in memory

    :type ptr: long or Swig instance

    :param base: (Optional) Base class to wrap with (Defaults to QObject, which should handle anything)

    :type base: QtGui.QWidget

    :return: QWidget or subclass instance

    :rtype: QtGui.QWidget
     """
    if ptr is None:
        return None

    ptr = long(ptr) #Ensure type
    if globals().has_key('shiboken'):

        if base is None:
            qObj = shiboken.wrapInstance(long(ptr), QtCore.QObject)
            metaObj = qObj.metaObject()
            cls = metaObj.className()
            superCls = metaObj.superClass().className()
            if hasattr(QtGui, cls):
                base = getattr(QtGui, cls)
            elif hasattr(QtGui, superCls):
                base = getattr(QtGui, superCls)
            else:
                base = QtGui.QWidget
        return shiboken.wrapInstance(long(ptr), base)

def getMayaWindow():
    
    #'Get the maya main window as a QMainWindow instance'    
    ptr = mui.MQtUtil.mainWindow()
    if ptr:
        return wrapinstance(long(ptr))

def show():
    global UiWindow
    try:
        UiWindow.close()
    except:
        pass
    UiWindow=DynamicSetupUI()
    UiWindow.show()
    return UiWindow

## Get the absolute path to my ui file
uiFile =os.path.join(os.path.dirname(__file__), 'dynamicChainSetup.ui')
form_class, base_class = loadUiType(uiFile)

class DynamicSetupUI(base_class, form_class):

    def __init__(self, parent= getMayaWindow()):
        super(DynamicSetupUI, self).__init__(parent)
        self.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        ##create Rigging tab
        self.connect(self.startJointGet_BTN, QtCore.SIGNAL("clicked()") , self.addStartJoint)
        self.connect(self.endJointGet_BTN, QtCore.SIGNAL("clicked()") , self.addEndJoint)
        self.connect(self.refreshSolvers_BTN, QtCore.SIGNAL("clicked()") , self.refreshAddSolvers)
        self.connect(self.createRig_BTN, QtCore.SIGNAL("clicked()") , self.createRig)
        self.addShapes()
        self.refreshAddSolvers()
        #simulation Tab
        self.selectionDynamicsCls=DynamicSetup()
        self.refreshReplaceSolvers()
        self.connect(self.selectHairSystem_BTN, QtCore.SIGNAL("clicked()"), self.selectHairSystem)
        self.connect(self.selectNucleus_BTN, QtCore.SIGNAL("clicked()"), self.selectNucleus)
        self.connect(self.selectIkCtrls_BTN, QtCore.SIGNAL("clicked()"), self.selectIkCtrls)
        self.connect(self.selectBakeCtrls_BTN, QtCore.SIGNAL("clicked()"), self.selectBakeCtrls)
        self.connect(self.selectBakeJoints_BTN, QtCore.SIGNAL("clicked()"), self.selectBakeJoints)
        self.connect(self.selectIkJoints_BTN, QtCore.SIGNAL("clicked()"), self.selectIkJoints)
        self.connect(self.selectDynamicsCurve_BTN, QtCore.SIGNAL("clicked()"), self.selectDynamicsCurve)
        self.connect(self.selectIkCurve_BTN, QtCore.SIGNAL("clicked()"), self.selectIkCurve)
        self.connect(self.selectOrigJoints_BTN, QtCore.SIGNAL("clicked()"), self.selectOrigJoints)
        self.connect(self.selectSettingsGrp_BTN, QtCore.SIGNAL("clicked()"), self.selectSettingsGrp)
        self.connect(self.bake_BTN, QtCore.SIGNAL("clicked()"), self.bakeSimulation)
        self.connect(self.replaceNucleus_BTN, QtCore.SIGNAL("clicked()"), self.replaceNucleus)
        self.connect(self.replaceHairSystem_BTN, QtCore.SIGNAL("clicked()"), self.replaceHairSystem)
        self.connect(self.refresh_replace_BTN, QtCore.SIGNAL("clicked()"), self.refreshReplaceSolvers)

    ## ------------create Rigging-------------------##
    def getHairSystems(self):
        hairSystemItemList = ["New"]
        hairSystemShapesList= cmds.ls(type="hairSystem")
        for hairSystemShape in hairSystemShapesList:
            hairSystemTransform = cmds.listRelatives(hairSystemShape , parent=True)[0]
            hairSystemItemList.append(hairSystemTransform)
        return hairSystemItemList
        
    def getNucleus(self):
        nucleusItemList = ["New"]
        nucleusList = cmds.ls(type="nucleus")
        for nucleus in nucleusList:
            nucleusItemList.append(nucleus)
        return nucleusItemList
        
    def addEndJoint(self):
        endJointDag=self.addSelectedJoint()
        self.endJointTxt.setText(str(endJointDag.fullPathName()))
        
    def addSelectedJoint(self):
        '''
        This method adds the selected joints to the startJoint text QLineEdit
        '''
        sel=cmds.ls(sl=True)
        if not sel:
            log.warning("Please select the start joint to add")
            return 
        if len(sel)>1:
            log.warning("Please select only one joint to add")
            return
        if not cmds.nodeType(sel[0])=="joint":
            log.warning("%s is not a joint, please select joints only!"%sel[0])
            return
        return getMDagPath(sel[0])

    def addShapes(self):
        localIconPath = os.path.join(os.path.dirname(__file__), 'icons')
        if not os.path.exists(localIconPath):
            log.info("icons folder not found: %s"%localIconPath)
            return 
        shapesList = ["circle01", "arrow01", "star", "cross01" ,"square"]
            
        ##add shapes to the Ctrls combo boxes
        for shape in shapesList:
            self.ctrlShape_CMB.addItem(QtGui.QIcon(os.path.join(localIconPath, "%s.bmp"%shape)),shape)

    def addStartJoint(self):
        startJointDag=self.addSelectedJoint()
        self.startJointTxt.setText(str(startJointDag.fullPathName()))

    def refreshAddSolvers(self):
        self.NucleusCMB.clear()
        self.HairCMB.clear()
        self.NucleusCMB.addItems(self.getNucleus())
        self.HairCMB.addItems(self.getHairSystems())

    def createRig(self):
        dynamicsSetup=DynamicSetup()
        dynamicsSetup.startJoint=str(self.startJointTxt.text())
        dynamicsSetup.endJoint=str(self.endJointTxt.text())
        dynamicsSetup.numCtrls=self.noOfControls.value()
        dynamicsSetup.prefix=str(self.prefixTxt.text())
        dynamicsSetup.controllersShape=str(self.ctrlShape_CMB.currentText())
        if str(self.HairCMB.currentText())=="New":
            dynamicsSetup.hairSystem=None
        else:
            dynamicsSetup.hairSystem=str(self.HairCMB.currentText())
            
        if str(self.NucleusCMB.currentText())=="New":
            dynamicsSetup.nucleus=None
        else:
            dynamicsSetup.nucleus=str(self.NucleusCMB.currentText())
            
        cmds.undoInfo(openChunk=True)
        try:
            dynamicsSetup.createSetup()
            self.refreshAddSolvers()
        except RuntimeError, error:
            log.warning(error)
        finally:
            cmds.undoInfo(closeChunk=True)
    
    ## ------------simulation tab-------------------##
    
    def bakeSimulation(self):
        self.getSettingsGrp()
        self.selectionDynamicsCls.bakeSimulation()
    
    def replaceNucleus(self):
        self.getSettingsGrp()
        newNucleus=str(self.replaceNucleus_CMB.currentText())
        if newNucleus=="New":
            newNucleus=None
        self.selectionDynamicsCls.replaceNucleus(newNucleus)
    
    def replaceHairSystem(self):
        self.getSettingsGrp()
        newHairSystem=str(self.replaceHairSystem_CMB.currentText())
        if newHairSystem=="New":
            newHairSystem=None
        self.selectionDynamicsCls.replaceHairSystem(newHairSystem)
        
    def refreshReplaceSolvers(self):
        self.replaceNucleus_CMB.clear()
        self.replaceHairSystem_CMB.clear()
        self.replaceNucleus_CMB.addItems(self.getNucleus())
        self.replaceHairSystem_CMB.addItems(self.getHairSystems())
    
    def selectHairSystem(self):
        self.getSettingsGrp()
        self.getSettingsGrpAttrs("hairSystem")

    def selectNucleus(self):
        self.getSettingsGrp()
        self.getSettingsGrpAttrs("nucleus")

    def selectBakeCtrls(self):
        self.getSettingsGrp()
        self.getSettingsGrpAttrs("bakeControllers")
    
    def selectIkCtrls(self):
        self.getSettingsGrp()
        self.getSettingsGrpAttrs("ikControllers")
        
    def selectBakeJoints(self):
        self.getSettingsGrp()
        self.getSettingsGrpAttrs("bakingJoints")
        
    def selectIkJoints(self):
        self.getSettingsGrp()
        self.getSettingsGrpAttrs("ikJoints")
        
    def selectDynamicsCurve(self):
        self.getSettingsGrp()
        self.getSettingsGrpAttrs("dynamicOutCurve")
        
    def selectIkCurve(self):
        self.getSettingsGrp()
        self.getSettingsGrpAttrs("ikCurve")
        
    def selectOrigJoints(self):
        self.getSettingsGrp()
        self.getSettingsGrpAttrs("originalJoints")
        
    def selectSettingsGrp(self):
        self.getSettingsGrp()
        self.getSettingsGrpAttrs("settingsGrp")
        
    def getSettingsGrp(self):
        sel=cmds.ls(selection=True)
        if not sel:
            log.warning("Please select a controller to get the info from")
            return
        if len(sel)>1:
            log.warning("Select one controller only")
            return
        if not cmds.attributeQuery("settingsGrp", node=sel[0], exists=True):
            log.warning("settings Grp attribute not found, please make sure you select a controller created by the tool")
            return
        settingsGrp=getMsgAttrValue(sel[0], "settingsGrp")
        if not settingsGrp:
            log.warning("settings Grp not found!!")
            return
        settingsGrp=getMDagPath(settingsGrp)
        self.selectionDynamicsCls.settingsGrp=settingsGrp.fullPathName()
        
    def getSettingsGrpAttrs(self, attr):
        if not self.selectionDynamicsCls.settingsGrp:
            log.warning("please get a settingsGrp first!!")
            return
        attrValue=getattr(self.selectionDynamicsCls, attr)
        if not attrValue:
            log.warning("couldn't find connected %s in the scene,looks like it got deleted!!"%attr)
            return
        cmds.select(attrValue)
        return attrValue
        
class DynamicSetup(object):
    '''
    The working class of the tool, all the setup is done here
    if settingsGrp given, you can query all the info from that settings grp
    @param startJoint: the name of your chain start joint
    @type startJoint: string
    @param endJoint: the name of your chain end joint
    @type endJoint: string
    @param numCtrls: the number of controllers you want to build
    @type numCtrls: int
    @param settingsGrp: the name of the settings Grp you want to query info from
    @type settingsGrp: string
    @param hairSystem: the name of the hair system you want to use for the rig, if None a new one will be created
    @type hairSystem: string
    @param nucleus: the name of the nucleus solver you want to use for the rig, if None a new one will be created
    @type nucleus: string
    @param prefix: a prefix for the rig
    @type prefix: string
    @param create: if True the setup will be built when the object is instantiated
    @type create: Bool 
    '''
    
    def __init__(self,settingsGrp=None,create=False,**kws):
        self._endJointDag=None
        self._startJointDag=None
        self._hairSystemDag=None
        self._nucleusDag=None
        self._settingsGrpDag=None
        self._ikControllers=[]
        self._bakingControllers=[]
        self._originalJoints=[]
        self._ikJoints=[]
        self._bakingJoints=[]
        self._numCtrls=2
        self.controllersShape="circle01"
        self.prefix=kws.setdefault("prefix", None)
        self.settingsGrp=settingsGrp
        self.startJoint=kws.setdefault("startJoint", None)
        self.endJoint=kws.setdefault("endJoint", None)
        self.hairSytem=kws.setdefault("hairSytem", None)
        self.nucleus=kws.setdefault("nucleus", None)
        self.numCtrls=kws.setdefault("numCtrls", 2)
        if create:
            self.createSetup()
   
    ##Begin properties
    @property
    def bakeControllers(self):
        return cmds.listConnections(self.settingsGrp+".bakeControllers")
    
    @property
    def bakingJoints(self):
        return cmds.listConnections(self.settingsGrp+".bakingJoints")
    
    @property
    def blendConstraints(self):
        return cmds.listConnections(self.settingsGrp+".blendConstraints")
    
    @property
    def blendShapeNode(self):
        return getMsgAttrValue(self.settingsGrp, "blendShapeNode")
    
    @property
    def controllersGrp(self):
        return getMsgAttrValue(self.settingsGrp, "controllersGrp")
    
    @property
    def dynamicInCurve(self):
        return getMsgAttrValue(self.settingsGrp, "dynamicInCurve")
    
    @property
    def dynamicOutCurve(self):
        return getMsgAttrValue(self.settingsGrp, "dynamicOutCurve")
    
    @property
    def endJoint(self):
        if self.settingsGrp:
            return getMsgAttrValue(self.settingsGrp, "endJoint")
        elif self._endJointDag:
            return self._endJointDag.fullPathName()
        else:
            return self._endJointDag
        
    @endJoint.setter
    def endJoint(self, jnt):
        if not jnt:
            return
        validateJoint(jnt)
        self._endJointDag=getMDagPath(jnt)
        if self.settingsGrp:
            log.warning("can't set end joint after rig being built")
            return
             
    @property
    def extrasGrp(self):
        return getMsgAttrValue(self.settingsGrp, "extrasGrp")
            
    @property
    def follicle(self):
        return getMsgAttrValue(self.settingsGrp, "follicle")

    @property
    def hairSystem(self):
        if self.settingsGrp:
            return getMsgAttrValue(self.settingsGrp, "hairSystem")
        elif self._hairSystemDag:
            return self._hairSystemDag.fullPathName()
        else:
            return self._hairSystemDag
        
    @hairSystem.setter
    def hairSystem(self, hairSystem):
        '''
        Sets the hair system you want to use for the rig.
        If there is an existing settingsGrp it means you already have a setup built, you can't set the hair system after creating the rig.
        You can use replaceHairSystem method to replace the existing hair system with a different or new one.
        '''
        if not hairSystem:
            return
        if not cmds.nodeType(cmds.listRelatives(hairSystem, shapes=True)[0])=="hairSystem":
            log.warning("%s is not a hairSystem"%hairSystem)
            return
        if self.settingsGrp:
            log.warning("can't set hairSystem after rig being built, use replaceHairSystem method instead")
            return
        self._hairSystemDag=getMDagPath(hairSystem)
        
    @property
    def hairSystemShape(self):
        if not self.hairSystem:
            return
        return cmds.listRelatives(self.hairSystem, shapes=True)[0]

    @property
    def ikControllers(self):
        return cmds.listConnections(self.settingsGrp+".ikControllers")
    
    @property
    def ikCurve(self):
        return getMsgAttrValue(self.settingsGrp, "ikCurve")
    
    @property
    def ikCurveHandle(self):
        return getMsgAttrValue(self.settingsGrp, "ikHandle")
    
    @property
    def ikJoints(self):
        return cmds.listConnections(self.settingsGrp+".ikJoints")

    @property
    def jointsGrp(self):
        return getMsgAttrValue(self.settingsGrp, "jointsGrp")

    @property
    def nucleus(self):
        if self.settingsGrp:
            return getMsgAttrValue(self.settingsGrp, "nucleus")
        elif self._nucleusDag:
            return self._nucleusDag.fullPathName()
        else:
            return self._nucleusDag
    
    @nucleus.setter
    def nucleus(self, nucleusSolver):
        '''
        Sets the nucleus you want to use for the rig.
        If there is an existing settingsGrp it means you already have a setup built, you wan't set the nucleus after creating the rig.
        You can use replaceNucleus method to replace the existing nucleus with a different or new one.
        '''
        if not nucleusSolver:
            return
        if not cmds.nodeType(nucleusSolver)=="nucleus":
            log.warning("%s is not a nucleus"%nucleusSolver)
            return
        if self.settingsGrp:
            log.warning("can't set nucleus after rig being built, use replaceNucleus method instead")
            return
        self._nucleusDag=getMDagPath(nucleusSolver)

    @property
    def numCtrls(self):
        return self._numCtrls
    
    @numCtrls.setter
    def numCtrls(self, num):
        if not isinstance(num, int):
            log.error("need an int input and it shouldn't be less than 2")
        if num<1:
            log.error("number of ctrls can't be less than 1")
        self._numCtrls=num

    @property
    def originalJoints(self):
        return cmds.listConnections(self.settingsGrp+".originalJoints")
    
    @property
    def parentGrp(self):
        return getMsgAttrValue(self.settingsGrp, "parentGrp")
    
    @property
    def settingsGrp(self):
        if self._settingsGrpDag:
            return self._settingsGrpDag.fullPathName()
        else:
            return self._settingsGrpDag

    @settingsGrp.setter
    def settingsGrp(self, grp):
        if not grp:
            return
        if not cmds.attributeQuery("mClass", node=grp, exists=True):
            log.warning("couldn't find the mClass attribute on the %s.. skipping!!"%grp)
            return
                      
        if not cmds.getAttr(grp+".mClass") == "DynamicChain":
            log.warning("settings Grp mClass is not a DynamicChain.probably not built with this class.. skipping!!"%grp)
            return
        self._settingsGrpDag=getMDagPath(grp)
    
    @property
    def startJoint(self):
        if self.settingsGrp:
            return getMsgAttrValue(self.settingsGrp, "startJoint")
        elif self._startJointDag:
            return self._startJointDag.fullPathName()
        else:
            return self._startJointDag

    @startJoint.setter
    def startJoint(self, jnt):
        if not jnt:
            return
        validateJoint(jnt)
        self._startJointDag=getMDagPath(jnt)
        if self.settingsGrp:
            log.warning("can't set start joint after rig being built")
            return
        
    def bakeSimulation(self):
        '''
        This method bakes the dynamics simulation on the baking controllers.
        '''
        startFrame=int(cmds.playbackOptions(q=True, minTime=True))
        endFrame=int(cmds.playbackOptions(query=True , maxTime=True))
        tempConst01=None
        tempConstList=[]
        cmds.undoInfo(openChunk=True)
        try:
            for bakeCtrl in self.bakeControllers:
                simJnt=getMsgAttrValue(bakeCtrl, "simJoint")
                tempConst01=cmds.parentConstraint(simJnt, bakeCtrl, maintainOffset=False)[0]       
                tempConstList.append(tempConst01)
            cmds.bakeResults(self.bakeControllers, time=(startFrame,endFrame), simulation=True, sampleBy=1, disableImplicitControl=True,
                             preserveOutsideKeys=False, sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False, bakeOnOverrideLayer=False,
                             minimizeRotation=True, controlPoints=False, shape=False)
            cmds.delete(tempConstList)
            #look for the blendAttribute
            for ctrl in self.bakeControllers:
                if cmds.attributeQuery("blendParent1", node=ctrl, exists=True):
                    cmds.deleteAttr(name=ctrl, attribute="blendParent1")
        finally:
            cmds.undoInfo(closeChunk=True)

    def blendSetups(self):
        constraintsList=[]
        for i, jnt in enumerate(self._originalJoints):
            const=cmds.parentConstraint(self._ikJoints[i], self._bakingJoints[i], jnt)[0]
            constraintsList.append(const)
            cmds.addAttr(const, longName="settingsGrp", attributeType="message")
            cmds.connectAttr(self.settingsGrp+".blendConstraints", const+".settingsGrp")
        #add blending attribute to the settings GRP
        if not cmds.attributeQuery("dynamicsSwitch", node=self.settingsGrp, exists=True):
            cmds.addAttr(self.settingsGrp, longName="dynamicsSwitch", attributeType="double", keyable=True, min= 0, max=1 ,dv=1)
        if not cmds.attributeQuery("bakingRig", node=self.settingsGrp, exists=True):
            cmds.addAttr(self.settingsGrp, longName="bakingRig", attributeType="double", keyable=True, min= 0, max=1 ,dv=0)
        #create the blendshape Node
        splineCurveBS=cmds.blendShape(self.dynamicOutCurve, self.ikCurve, name="%s_BS"%getShortName(self.ikCurve))[0]
        #connect blending attrs
        cmds.connectAttr("%s.dynamicsSwitch"%self.settingsGrp, "%s.%s"%(splineCurveBS, self.dynamicOutCurve))
        #create the reverse node
        reverseNode=cmds.shadingNode("reverse", asUtility=True, name="%s_rev"%getShortName(self.settingsGrp))
        cmds.connectAttr("%s.bakingRig"%self.settingsGrp, "%s.inputX"%reverseNode)
        for const in constraintsList:
            weights=cmds.parentConstraint(const, weightAliasList=True, query=True)
            cmds.connectAttr("%s.outputX"%reverseNode, "%s.%s"%(const, weights[0]))
            cmds.connectAttr("%s.bakingRig"%self.settingsGrp, "%s.%s"%(const, weights[1]))
        #connect the reverse output to the ik setup controllers visibility
        for ctrl in self.ikControllers:
            cmds.connectAttr("%s.outputX"%reverseNode, "%s.visibility"%cmds.listRelatives(ctrl, shapes=True)[0])
        for ctrl in self.bakeControllers:
            cmds.connectAttr("%s.bakingRig"%self.settingsGrp, "%s.visibility"%cmds.listRelatives(ctrl, shapes=True)[0])
        
    def createBakingSetup(self):
        tempBakingJnt=None
        self._bakingJoints=[]
        self._bakingControllers=[]
        for i, ikJnt in enumerate(self._ikJoints):
            bakingJnt=cmds.duplicate(ikJnt , parentOnly=True, name="%s_bake_chain"%getShortName(self._originalJoints[i]))[0]
            self._bakingJoints.append(bakingJnt)
            if tempBakingJnt:
                cmds.parent(bakingJnt, tempBakingJnt)
            tempBakingJnt=bakingJnt
            #connect to settings Grp
            if not cmds.attributeQuery("settingsGrp", node=bakingJnt, exists=True):
                cmds.addAttr(bakingJnt, longName="settingsGrp", attributeType="message")
            try:
                cmds.connectAttr(self.settingsGrp+".bakingJoints", bakingJnt+".settingsGrp", force=True)
            except RuntimeError:
                pass
            
        #create controllers
        tempCtrl=None
        for i, bakingJnt in enumerate(self._bakingJoints):
            ctrlName=bakingJnt
            if self.prefix:
                ctrlName="%s_%s"%(self.prefix,i+1)
            ctrl, ctrlOffset=createController("%s_baking_CTRL"%ctrlName,self.controllersShape, lockAndHide=["scaleX", "scaleY", "scaleZ", "visibility"])
            self._bakingControllers.append(ctrl)
            #align controllers to joints
            tempPos=cmds.pointConstraint(bakingJnt, ctrlOffset)
            tempOrient=cmds.orientConstraint(bakingJnt, ctrlOffset)
            cmds.delete(tempPos, tempOrient)
            #constrain the joint to the controller
            cmds.parentConstraint(ctrl, bakingJnt)
            if tempCtrl:
                cmds.parent(ctrlOffset, tempCtrl)
            tempCtrl=ctrl
            #add the target sim joint on the controllers
            cmds.addAttr(ctrl, longName="simJoint", attributeType="message")
            cmds.connectAttr("%s.bakeCtrl"%self._ikJoints[i], ctrl+".simJoint", force=True)
            #connect the controllers to the settings GRP
            cmds.addAttr(ctrl, longName="settingsGrp", attributeType="message")
            cmds.connectAttr(self.settingsGrp+".bakeControllers", ctrl+".settingsGrp")
        return self._bakingJoints

    def createFollicle(self):
        '''
        This method creates the follicle
        '''
        follicleName="follicle"
        if self.prefix:
            follicleName="%s_follicle"%self.prefix
        elif self.startJoint:
            follicleName="%s_follicle"%getShortName(self.startJoint)
        #Now create the follicle
        follicleShape=cmds.createNode("follicle", skipSelect=True, name="%sShape"%follicleName)
        follicleTransform=cmds.listRelatives(follicleShape, parent=True)[0]
        cmds.setAttr(follicleShape+".restPose", 1)
        cmds.setAttr(follicleShape+".startDirection", 1)
        cmds.setAttr(follicleShape+".degree", 3)
        cmds.addAttr(follicleTransform, longName="settingsGrp", attributeType="message")
        cmds.connectAttr(self.settingsGrp+".follicle", follicleTransform+".settingsGrp")
        #rename transform
        cmds.rename(self.follicle, follicleName)
        return self.follicle

    def createHairSystem(self):
        '''
        This method creates the hair system
        '''
        hairSystemName="hairSystem"
        if self.prefix:
            hairSystemName="%s_hairSystem"%self.prefix
        elif self.startJoint:
            hairSystemName="%s_hairSystem"%getShortName(self.startJoint)
        hairSystemShape=cmds.createNode('hairSystem', skipSelect=True, name="%sShape"%hairSystemName)
        hairSystemTransform=cmds.listRelatives(hairSystemShape, parent=True)[0]
        cmds.connectAttr("time1.outTime", "%s.currentTime"%hairSystemShape, force=True)
        cmds.setAttr(hairSystemShape+".active", 1)
        #connect to settingsGrp
        cmds.addAttr(hairSystemTransform, longName="settingsGrp", attributeType="message")
        cmds.connectAttr(hairSystemTransform+".settingsGrp", self.settingsGrp+".hairSystem", force=True)
        #rename transform
        cmds.rename(self.hairSystem, hairSystemName)
        return self.hairSystem

    def createHairSystemCurve(self):
        cmds.parent(self.dynamicInCurve, self.follicle)
        #rebuild the dynamic in curve
        rebuiltCurve, rebuildNode=cmds.rebuildCurve(self.dynamicInCurve, rebuildType=0, degree=1, tolerance=0.1, endKnots=1, keepRange=0,
                                                    keepTangents=False, keepControlPoints=True, constructionHistory=True, replaceOriginal=False)
        rebuildNode=cmds.rename(rebuildNode, "%s_rebuildNode"%self.dynamicInCurve)
        cmds.parent(cmds.listRelatives(rebuiltCurve, shapes=True)[0], self.dynamicInCurve, add=True, shape=True)
        #create dynamic out curve
        dynamicOutCurve=cmds.duplicate(self.ikCurve, name="%s_dynamicOutCurve"%self.ikCurve)[0]
        dynamicOutCurveShape=cmds.listRelatives(dynamicOutCurve, shapes=True)[0]
        #connect to settings grp
        if not cmds.attributeQuery("settingsGrp", node=dynamicOutCurve, exists=True):
            cmds.addAttr(dynamicOutCurve, longName="settingsGrp", attributeType="message")
        cmds.connectAttr(self.settingsGrp+".dynamicOutCurve", dynamicOutCurve+".settingsGrp")
        #connect to hair system
        cmds.connectAttr(self.dynamicInCurve+".worldMatrix[0]", self.follicle+".startPositionMatrix", force=True)
        cmds.connectAttr("%s.local"%cmds.listRelatives(rebuiltCurve, shapes=True)[0], "%s.startPosition"%self.follicle, force=True)
        cmds.connectAttr(self.follicle+".outCurve", dynamicOutCurveShape+".create", force=True)
        cmds.delete(rebuiltCurve)

    def createIkSetup(self):
        name=self.startJoint
        if self.prefix:
            name=self.prefix
        #start with the spline Ik chain
        self._originalJoints=[]
        self._ikJoints=[]
        self._ikControllers=[]
        self._originalJoints=getJointChain(self.startJoint, self.endJoint)
        tempSplineJnt=None
        for jnt in self._originalJoints:
            if not cmds.attributeQuery("settingsGrp", node=jnt, exists=True):
                cmds.addAttr(jnt, longName="settingsGrp", attributeType="message")
            try:
                cmds.connectAttr(self.settingsGrp+".originalJoints", jnt+".settingsGrp", force=True)
            except RuntimeError:
                pass
            splineJnt=cmds.duplicate(jnt, parentOnly=True, name="%s_IK_chain"%getShortName(jnt))[0]
            if cmds.listRelatives(splineJnt, parent=True):
                cmds.parent(splineJnt, world=True)
            cmds.connectAttr(self.settingsGrp+".ikJoints", splineJnt+".settingsGrp", force=True)
            self._ikJoints.append(splineJnt)
            #add an attribute to be able to get the bake ctrl info later from the joint
            cmds.addAttr(splineJnt, longName="bakeCtrl", attributeType="message")
            if tempSplineJnt:
                cmds.parent(splineJnt, tempSplineJnt)
            tempSplineJnt=splineJnt
        #create spline setup
        ikHandle, ikEffector, ikCurve=cmds.ikHandle(name="%s_IKH"%name ,startJoint=self._ikJoints[0], endEffector=self._ikJoints[-1], solver="ikSplineSolver",
                                                    createCurve=True ,parentCurve=False, simplifyCurve=True, numSpans=self.numCtrls)

        cmds.addAttr(ikHandle, longName="settingsGrp", attributeType="message")
        cmds.connectAttr(self.settingsGrp+".ikHandle", ikHandle+".settingsGrp")
        cmds.addAttr(ikCurve, longName="settingsGrp", attributeType="message")
        cmds.connectAttr(self.settingsGrp+".ikCurve", ikCurve+".settingsGrp")
        cmds.rename(self.ikCurve, "%s_IKH_curve"%name)
        cmds.rename(ikEffector, "%s_IKH_curve"%name)

        #create locators for the curveCvs
        ikLocsList=[]
        curveCvs=cmds.ls(self.ikCurve+'.cv[*]', flatten=True)
        ##get the position of the first and last cvs
        startPt=cmds.xform(curveCvs[0], worldSpace=True, translation=True, query=True)
        endPt=cmds.xform(curveCvs[-1], worldSpace=True, translation=True, query=True)

        ##create a locator handle for the first cluster 
        cvStartLocator=cmds.spaceLocator(name='%s_1_loc'%(self.ikCurve))[0]
        cmds.xform(cvStartLocator, worldSpace=True, translation=startPt)
        cmds.cluster([curveCvs[0], curveCvs[1]], bindState=True, relative=False, weightedNode=[cvStartLocator, "%s"%cmds.listRelatives(cvStartLocator, shapes=True)[0]])
        ikLocsList.append(cvStartLocator)
        
        ##create a locator handle for the end cluster
        cvEndLocator=cmds.spaceLocator(name='%s_%s_loc'%(self.ikCurve, len(curveCvs)-2))[0]
        cmds.xform(cvEndLocator, worldSpace=True, translation=endPt)
        endCluster=cmds.cluster([curveCvs[-2], curveCvs[-1]], bindState=True, relative=False, weightedNode=[cvEndLocator, "%s"%cmds.listRelatives(cvEndLocator, shapes=True)[0]])
        
        ##create middle locators
        for cv in [curveCvs[0], curveCvs[1], curveCvs[-1], curveCvs[-2]]:
            curveCvs.remove(cv)
        if not len(curveCvs):
            endMedClus=endCluster[0]
        else:
            for i, cv in enumerate(curveCvs):                
                cvMiddleLocator=cmds.spaceLocator(name='%s_%s_loc'%(self.ikCurve, i+2))[0]
                midCvPosition=cmds.xform(cv, worldSpace=True, translation=True, query=True)
                cmds.xform(cvMiddleLocator, worldSpace=True, translation=midCvPosition)
                curveLoc=cmds.cluster(cv, bindState=True, relative=False, weightedNode=[cvMiddleLocator, "%s"%cmds.listRelatives(cvMiddleLocator, shapes=True)[0]])
                ikLocsList.append(cvMiddleLocator)
            endMedClus=curveLoc[0]
        ikLocsList.append(cvEndLocator)
                 
        #create controllers
        tempCtrl=None
        for i, loc in enumerate(ikLocsList[:-1]):
            pos=cmds.xform(loc, worldSpace=True, translation=True, query=True)
            ctrl, ctrlOffset=createController("%s_%s_IK_CTRL"%(name, i+1), self.controllersShape, lockAndHide=["scaleX", "scaleY", "scaleZ", "visibility"])
            self._ikControllers.append(ctrl)
            cmds.xform(ctrlOffset, worldSpace=True, translation=pos)
            locPosVec=OpenMaya.MVector(pos[0],pos[1],pos[2])
            closestJntList=[]
            comparedLen = {}
            #try to orient the controllers according to the closest joints orientation
            for jnt in self._ikJoints:
                averagePos = cmds.xform(jnt, worldSpace=True, translation=True, query=True)
                averagePosVec = OpenMaya.MVector(averagePos[0],averagePos[1],averagePos[2])
                diff = averagePosVec - locPosVec
                vecLen = diff.length()
                comparedLen.setdefault(jnt, vecLen)

                closestJntList = sorted(comparedLen, key=comparedLen.__getitem__)
            temp=cmds.orientConstraint(closestJntList[0], closestJntList[1] , ctrlOffset, maintainOffset=0)
            cmds.delete(temp)
            #parent clusters under the controllers
            cmds.parent(loc,ctrl)
            if tempCtrl:
                cmds.parent(ctrlOffset, tempCtrl)
            tempCtrl=ctrl
            #hide the ik locators
            cmds.setAttr(loc+".visibility", 0)
            #connect the controllers to the settings GRP
            cmds.addAttr(ctrl, longName="settingsGrp", attributeType="message")
            cmds.connectAttr(self.settingsGrp+".ikControllers", ctrl+".settingsGrp")
        #parent the last ik Loc under the last controller
        cmds.parent(ikLocsList[-1], ctrl)
        cmds.setAttr("%s.visibility"%ikLocsList[-1], 0)
        
        #add twist attribute on the start Ctrl
        if not cmds.attributeQuery("ikTwist", node=self._ikControllers[0], exists=True):
            cmds.addAttr(self._ikControllers[0], longName="ikTwist", attributeType="double", dv=0, keyable=True)
        cmds.connectAttr(self._ikControllers[0]+".ikTwist", self.ikCurveHandle+".twist", force=True)

        #create dynamicInCurve
        dynamicInCurve=cmds.duplicate(self.ikCurve, name="%s_dynamicInCurve"%self.ikCurve)[0]
        if not cmds.attributeQuery("settingsGrp", node=dynamicInCurve, exists=True):
            cmds.addAttr(dynamicInCurve, longName="settingsGrp", attributeType="message")
        cmds.connectAttr(self.settingsGrp+".dynamicInCurve", dynamicInCurve+".settingsGrp")
        
        ##connect the dynamic curve to the same rig of the spline curve
        cmds.connectAttr("%s.outputGeometry[0]"%endMedClus, "%s.create"%cmds.listRelatives(dynamicInCurve ,shapes=True)[0])
        return self._ikJoints

    def createNucleus(self):
        '''
        This method creates the nucleus
        '''
        nucleusName="nucleus"
        if self.prefix:
            nucleusName="%s_nucleus"%self.prefix
        elif self.startJoint:
            nucleusName="%s_nucleus"%getShortName(self.startJoint)
        nucleus=cmds.createNode("nucleus", skipSelect=True, name=nucleusName)
        #connect to settings grp
        cmds.addAttr(nucleus, longName="settingsGrp", attributeType="message")
        cmds.connectAttr(nucleus+".settingsGrp", self.settingsGrp+".nucleus", force=True)
        #connect time out time to the nucleus current time
        cmds.connectAttr('time1.outTime', self.nucleus+".currentTime", force=True)
        #get the scene coordinations
        MayaUpAxis=OpenMaya.MGlobal.upAxis()
        if MayaUpAxis.z:
            cmds.setAttr(self.nucleus+".gravityDirectionZ", -1)
            cmds.setAttr(self.nucleus+".gravityDirectionY", 0)
        if MayaUpAxis.y:
            cmds.setAttr(self.nucleus+".gravityDirectionZ", 0)
            cmds.setAttr(self.nucleus+".gravityDirectionY", -1)
        return self.nucleus
    
    def createRigGroups(self):
        '''
        This method creates groups for the dynamic rig.
        Feel free to re-order the rig the way you want.
        Just make sure the transforms in the extras grp don't move with rig to avoid double transformations.
        '''
        name=self.startJoint
        if self.prefix:
            name=self.prefix
        extrasGrp=cmds.group(empty=True, world=True, name="%s_extras_GRP"%name)
        jointsGrp=cmds.group(empty=True, world=True, name="%s_joints_GRP"%name)
        controllersGrp=cmds.group(empty=True, world=True, name="%s_controllers_GRP"%name)
        parentGrp=cmds.group(extrasGrp, jointsGrp, controllersGrp, world=True, name="%s_dynamicsSetup_GRP"%name)
        for grp in [parentGrp, extrasGrp, jointsGrp, controllersGrp]:
            cmds.addAttr(grp, longName="settingsGrp", attributeType="message")
        cmds.connectAttr(self.settingsGrp+".parentGrp", parentGrp+".settingsGrp")
        cmds.connectAttr(self.settingsGrp+".extrasGrp", extrasGrp+".settingsGrp")
        cmds.connectAttr(self.settingsGrp+".jointsGrp", jointsGrp+".settingsGrp")
        cmds.connectAttr(self.settingsGrp+".controllersGrp", controllersGrp+".settingsGrp")
        #re group the rig components under these groups
        #get the offset group of the controllers
        ikCtrlOffset=getMsgAttrValue(self._ikControllers[0], "offsetGrp")
        bakeCtrlOffset=getMsgAttrValue(self._bakingControllers[0], "offsetGrp")
        
        cmds.parent(ikCtrlOffset, bakeCtrlOffset, controllersGrp)
        cmds.parent(self._bakingJoints[0], self._ikJoints[0], jointsGrp)
        cmds.parent(self.settingsGrp, parentGrp)
        
        extrasGrpComp=[self.nucleus, self.hairSystem, self.follicle, self.ikCurve, self.dynamicOutCurve, self.ikCurveHandle]
        for comp in extrasGrpComp:
            if not comp:
                extrasGrpComp.remove(comp)
        cmds.parent(extrasGrpComp, extrasGrp)
        #extras grp should not move or inherit transformations
        for attr in ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ"]:
            cmds.setAttr("%s.%s"%(extrasGrp,attr), lock=True, keyable=False)
        cmds.setAttr("%s.inheritsTransform"%extrasGrp, 0)
        cmds.setAttr(extrasGrp+".visibility", 0)
        cmds.setAttr(jointsGrp+".visibility", 0)
        
        return parentGrp
        
    def createSettingsGrp(self):
        if not self.startJoint:
            log.warning("start joint hasn't been set yet")
            return
        if not self.endJoint:
            log.warning("end joint hasn't been set yet")
            return
        #make sure the joint chain is acceptable
        getJointChain(self.startJoint, self.endJoint)
        #create the settings grp
        settingsGrpName="dynamicChain_settings_GRP"
        if self.prefix:
            settingsGrpName="%s_%s"%(self.prefix, settingsGrpName)
        else:
            settingsGrpName="%s_%s"%(getShortName(self.startJoint), settingsGrpName)
        settingsGrp=cmds.group(name=settingsGrpName, world=True, empty=True)
        #lock and hide unused channels
        for attr in ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ"]:
            cmds.setAttr("%s.%s"%(settingsGrp,attr), lock=True, keyable=False)
        cmds.setAttr(settingsGrp+".visibility", lock=True, keyable=False)
        #add mClass attr and lock it
        cmds.addAttr(settingsGrp, longName='mClass', dt="string")
        cmds.setAttr(settingsGrp+".mClass", "DynamicChain", type="string")
        cmds.setAttr(settingsGrp+".mClass", lock=True)
        #add meta data attributes
        for attr in ["startJoint", "endJoint", "nucleus", "hairSystem", "follicle", "ikControllers","bakeControllers",
                     "blendConstraints", "blendShapeNode", "dynamicInCurve","dynamicOutCurve", "ikCurve", "ikHandle",
                     "ikJoints", "originalJoints", "bakingJoints", "splineIkHandle", "parentGrp", "extrasGrp", "jointsGrp",
                     "controllersGrp"]:
            cmds.addAttr(settingsGrp, longName=attr, attributeType="message")
        '''
        Connect args to the settings grp
        '''
        #add end Joint
        if not cmds.attributeQuery("endJoint", node=self.endJoint, exists=True):
            cmds.addAttr(self.endJoint, longName="endJoint", attributeType="message")
        try:
            #connect the endJoint attribute on the settings GRP to the new attr on the endJoint
            cmds.connectAttr(settingsGrp+".endJoint", self.endJoint+".endJoint", force=True)
        except RuntimeError, error:
            log.warning(error)
        
        #add start joint
        if not cmds.attributeQuery("startJoint", node=self.startJoint, exists=True):
            cmds.addAttr(self.startJoint, longName="startJoint", attributeType="message")
        try:
            #connect the startJoint attribute on the settings GRP to the new attr on the startJoint
            cmds.connectAttr(settingsGrp+".startJoint", self.startJoint+".startJoint", force=True)
        except RuntimeError, error:
            log.warning(error)
        
        #add the hair system
        if self.hairSystem:
            if not cmds.attributeQuery("settingsGrp", node=self.hairSystem, exists=True):
                cmds.addAttr(self.hairSystem, longName="settingsGrp", attributeType="message")
            #connect the hairSystem settings Grp attribute to the settings GRP thairSyatem attribute
            cmds.connectAttr(self.hairSystem+".settingsGrp", settingsGrp+".hairSystem", force=True)
        
        #add nucleus
        if self.nucleus:
            #add msg attr on the nucleus
            if not cmds.attributeQuery("settingsGrp", node=self.nucleus, exists=True):
                cmds.addAttr(self.nucleus, longName="settingsGrp", attributeType="message")
            #connect the nucleusSolver settings Grp attribute to the settings GRP nucleus attribute
            cmds.connectAttr(self.nucleus+".settingsGrp", settingsGrp+".nucleus", force=True)
        self.settingsGrp=settingsGrp
            
    def createSetup(self):
        '''
        This method creates the chain rig
        '''
        self.createSettingsGrp()
        self.createIkSetup()
        self.createBakingSetup()
        if not self.hairSystem:
            self.createHairSystem()
        if not self.nucleus:
            self.createNucleus()
        self.createFollicle()
        self.connectFollicleToHairSystem()
        self.connectHairSystemToNucleus()
        self.createHairSystemCurve()
        self.blendSetups()
        self.createRigGroups()
        
    def connectFollicleToHairSystem(self):
        '''
        This method connects the follicle to the hairSystem
        '''
        if not self.hairSystem:
            log.warning("The hair system hasn't been set yet.. Skipping!!")
            return
        if not self.follicle:
            log.warning("There is no follicle to connect to the hair.. Skipping!!")
            return
        hairCurveInputHair=cmds.listConnections(self.hairSystemShape+".inputHair")
        hairCurveIndex=0
        if hairCurveInputHair:
            hairCurveIndex=len(hairCurveInputHair)
        try:
            cmds.connectAttr(self.follicle+".outHair", "%s.inputHair[%s]"%(self.hairSystemShape, hairCurveIndex), force=True)
            cmds.connectAttr("%s.outputHair[%s]"%(self.hairSystemShape, hairCurveIndex), self.follicle+".currentPosition", force=True)
        except RuntimeError, error:
            log.warning(error)

    def connectHairSystemToNucleus(self):
        if not self.nucleus:
            log.warning("The nucleus hasn't been set yet.. Skipping!")
            return
        
        if not self.hairSystem:
            log.warning("The hair system hasn't been set yet.. Skipping!!")
            return
        
        connectedNucleus=cmds.listConnections(self.hairSystemShape+".startFrame")
        if connectedNucleus:
            if connectedNucleus[0]==getShortName(self.nucleus):
                log.info("seems like the hair system %s is already connected to the nucleus %s"%(self.hairSystem, self.nucleus))
                return

        inputActiveStartLen=0
        inputActiveLen=0
        outputObjectsLen=0
        inputActiveStart = cmds.listConnections(self.nucleus+".inputActiveStart")
        inputActive=cmds.listConnections(self.nucleus+ ".inputActive")
        outputObjects=cmds.listConnections(self.nucleus+ ".outputObjects")
        if inputActiveStart:
            inputActiveStartLen=len(inputActiveStart)
        if inputActive:
            inputActiveLen=len(inputActive)  
        if outputObjects:
            outputObjectsLen=len(outputObjects)
        try:
            cmds.connectAttr(self.nucleus+".startFrame", self.hairSystemShape+".startFrame", force=True)
            cmds.connectAttr("%s.outputObjects[%s]"%(self.nucleus, outputObjectsLen), self.hairSystemShape+".nextState", force=True)
            cmds.connectAttr(self.hairSystemShape+".startState", "%s.inputActiveStart[%s]"%(self.nucleus, inputActiveStartLen), force=True)
            cmds.connectAttr(self.hairSystemShape+".currentState", "%s.inputActive[%s]"%(self.nucleus, inputActiveLen), force=True)
        except RuntimeError, error:
            log.warning(error)
        
    def replaceNucleus(self, newNucleus=None):
        if not newNucleus:
            self.createNucleus()
            cmds.parent(self.nucleus, self.extrasGrp)
        elif newNucleus==self.nucleus:
            log.info("%s is already connected to setup"%self.nucleus)
            return
        else:
            #connect to settingsGrp
            if not cmds.attributeQuery("settingsGrp", node=newNucleus, exists=True):
                cmds.addAttr(newNucleus, longName="settingsGrp", attributeType="message")
            cmds.connectAttr(newNucleus+".settingsGrp", self.settingsGrp+".nucleus", force=True)
        self.connectHairSystemToNucleus()
        
    def replaceHairSystem(self, newHairSystem=None):
        if not newHairSystem:
            self.createHairSystem()
            cmds.parent(self.hairSystem, self.extrasGrp)
        elif newHairSystem==self.hairSystem:
            log.info("%s is already connected to setup"%self.hairSystem)
            return
        else:
            #connect to settingsGrp
            if not cmds.attributeQuery("settingsGrp", node=newHairSystem, exists=True):
                cmds.addAttr(newHairSystem, longName="settingsGrp", attributeType="message")
            cmds.connectAttr(newHairSystem+".settingsGrp", self.settingsGrp+".hairSystem", force=True)
        self.connectHairSystemToNucleus()
        self.connectFollicleToHairSystem()
        
def validateJoint(jnt):
    '''
    This method validates if the input is of type joint
    @param jnt: the name of the joint
    @type jnt: string
    '''
    if not cmds.objExists(jnt):
        log.warning("%s deosn't exist in the scene"%jnt)
        return
    
    if not cmds.objectType(jnt)=='joint':
        log.warning("%s is not a joint"%jnt)
        return
    return True

def getMsgAttrValue(node, attr):
    '''
    This method returns the connected node to a message attribute.
    Returns only the first item on a list.
    Don't use if you have more than one node connected to that MSG attr.
    
    @param node: node where you will query the msg attr from
    @type node: string
    
    @param attr: the message attribute name
    @type attr: string
    
    @return: string
    '''
    if not cmds.objExists(node):
        log.info("%s does not exist"%node)
        return
    if not cmds.attributeQuery(attr, node=node, exists=True):
        log.info("%s attribute does not exist"%attr)
        return
    
    value=cmds.listConnections("%s.%s"%(node,attr))
    if value:
        return value[0]
    else:
        return    
    
def getMDagPath(node):
    dagpath=OpenMaya.MDagPath()
    selList=OpenMaya.MSelectionList()
    selList.add(node)
    selList.getDagPath(0, dagpath)
    return dagpath

def getShortName(name):
    return name.split('|')[-1]

def getJointChain(startJoint, endJoint):
    '''
    Return the all the joints in the chain using start/end
    @param startJoint: start of chain
    @param endJoint: end of chain
    @return Return the all the joints in the chain using start/end
    '''
    startJntLP= cmds.ls(startJoint, long=True)[0]
    endJntParentsList=[endJoint]
    endJntParent= endJoint

    while (endJntParent!=None):
        endJntParent = cmds.listRelatives(endJntParent, parent=True, fullPath=True)[0]
        if endJntParent:
            endJntParentsList.append(endJntParent)
        if endJntParent==startJntLP:
            break
    if not startJntLP in endJntParentsList:
        raise StandardError("%s is not a parent of %s"%(startJntLP, endJoint))
    else:
        endJntParentsList.reverse()
        return endJntParentsList

def createController(name, shape="circle01", lockAndHide=[]):
    availableShapes=["circle01", "arrow01", "star", "square", "cross01"]
    if not shape in availableShapes:
        log.warning("choose available shape from %s"%availableShapes)
        controlCurve=eval("shapes.circle01(name='%s')"%name)
    else:
        controlCurve=eval("shapes.%s(name='%s')"%(shape, name))
    offsetGrp=cmds.group(controlCurve, name="%s_offset"%name)
    cmds.addAttr(controlCurve, longName="offsetGrp", attributeType="message")
    cmds.addAttr(offsetGrp, longName="ctrl", attributeType="message")
    cmds.connectAttr(controlCurve+".offsetGrp", offsetGrp+".ctrl")
    if lockAndHide:
        for attr in lockAndHide:
            cmds.setAttr("%s.%s"%(controlCurve, attr), lock=True)
            cmds.setAttr("%s.%s"%(controlCurve, attr), keyable=False)
    return[controlCurve, offsetGrp]

