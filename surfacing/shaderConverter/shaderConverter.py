# -*- coding:utf-8 -*-
u'''
Created on 2013. 6. 22.

@author: Kyuho Choi

'''

import pymel.core as pm
import maya.cmds as cmds
import shaderConverter_mappingData as mapdat
reload(mapdat)
from shaderConverter_mappingData import *

def simpleConverter( shader, oldShaderType='blinn', newShaderType='aiStandard', attrMappingTable=[('color','color')], deleteOldShader=False, assignToObject=False, addSubfix=True ):
    # oldShader가 oldShaderType 인지 확인
    if not ( pm.nodeType(shader) == oldShaderType ):
        return

    # 새로운 쉐이더 생성
    newShader = pm.shadingNode( newShaderType, asShader=True ) 

    # 연결된 노드가 있으면 새쉐이더 어트리뷰트에 연결,
    # 그렇지 않으면 값을 복사에서 붙임 (value/color)
    for fromAttr, toAttr in attrMappingTable:
        # 어트리뷰트 캐스팅
        fromAttr = pm.Attribute( shader+'.'+fromAttr)
        toAttr   = pm.Attribute( newShader+'.'+toAttr)

        # 어트리뷰트에 연결된 노드가 있으면, 노드의 어트리뷰트를 새쉐이더 어트리뷰트에 연결
        if fromAttr.isConnected():
            fromAttr.inputs( p=True )[0] >> toAttr
        
        # 연결된게 없음, 값을 복사에서 집어넣음.
        else:            
            try:
                toAttr.set( fromAttr.get() )
            except:
                print u'# 대입하려는 값의 형식이 상이 합니다. 확인해주세요. ------------------------------------'
                print u'%60s : %s'%(fromAttr,fromAttr.get())
                print u'%60s : %s'%(toAttr, toAttr.get() )
    
    # 새로생성된 쉐이더 적용 : setAiOpaque보다 나중에 처리되어야 함.
    if assignToObject:
        objs = getObjects_fromMaterial( shader )
        assignMaterialToObject( newShader, objs )
    
    # 이름조정
    if addSubfix:
        newShader.rename( newName +'_'+ newShaderType )

    # 기존 쉐이더 삭제
    if deleteOldShader:
        pm.delete( shader )
   
    return (newShader)

# ------------------------------
# Arnold
# ------------------------------
def mayaShader_to_aiStandard( shader, deleteOldShader=False, assignToObject=False, setAiOpaque=False, addSubfix=True, reconnectHwTx=True, processDisplay=True ):
    # 플러그인 로드
    pm.loadPlugin('mtoa', quiet=True)

    # 재질이 blinn 인지 확인
    #if not ( pm.nodeType(blinn) == "blinn" ):
    #    return

    # aiStandard 생성
    # newShader = pm.shadingNode( 'aiStandard', asShader=True )
    newShader, newSG = createShader( 'aiStandard' )
    
    # 이름조정
    if addSubfix:
        newShader.rename( shader.name()+'_aiStandard' )
    oldShaderName = shader.name()

    # 맵이 연결되어 있으면 연결,
    # 그렇지 않으면 값을 조정 (value/color)
    for fromAttr, toAttr in mayaShader_to_aiStandard_mappingTable:
        # 범프어트리뷰트는 나중에 처리함.
        if toAttr == 'normalCamera':
            continue

        # 어트리뷰트 캐스팅
        try:
            fromAttrPlug = pm.Attribute( shader+'.'+fromAttr)
            toAttrPlug   = pm.Attribute( newShader+ '.'+toAttr)
        except:
            continue

        # 연결된 노드를 생성된 노드에 연결
        if fromAttrPlug.isConnected():
            fromAttrPlug.inputs( p=True )[0] >> toAttrPlug
        
        # 연결된게 없음, 값을 복사에서 집어넣음.
        else:
            try:        
                value = fromAttrPlug.get()

                if toAttr == 'opacity':
                    value = value * -1.0 + 1.0

                toAttrPlug.set( value )
            except:
                print u'#   mayaShader_to_aiStandard : 대입하려는 값의 형식이 상이 합니다. 확인해주세요. ------------------------------------'
                print u'#           %60s : %s'%(fromAttrPlug,fromAttrPlug.get())
                print u'#           %60s : %s'%(toAttrPlug, toAttrPlug.get() )
   
    # 범프가 존재하면, 연결하고 bumpValue 조정
    if shader.normalCamera.isConnected():     
        bumpNode = shader.normalCamera.inputs()[0]
        bumpNode.outNormal >> newShader.normalCamera        

    # opacity일겨우 오브젝트 처리
    if setAiOpaque:
        if pm.dt.Vector( newShader.opacity.get() ) < pm.dt.Vector(1,1,1):
            #print newShader, setAiOpaque, newShader.opacity.get()
            for obj in getObjects_fromMaterial( shader ):               
                obj = pm.PyNode(obj)
                try:
                    obj.aiOpaque.set( False )
                    print "#   mayaShader_to_aiStandard : set opaque attribute. '%s'"% obj
                except:
                    print '#   mayaShader_to_aiStandard : can not set opaque attribute. "%s(%s)"' % (obj, pm.nodeType(obj))
        
    # 새로생성된 쉐이더 적용 : setAiOpaque보다 나중에 처리되어야 함.
    if assignToObject:
        if processDisplay: pm.refresh()

        objs = getObjects_fromMaterial( shader )
        assignMaterialToObject( newShader, objs )

    # 기존 쉐이더 삭제
    if deleteOldShader:
        pm.delete( shader )
        print u"#   mayaShader_to_aiStandard : '%s' deleted"%oldShaderName

    # 하드웨어 텍스쳐 재연결
    if reconnectHwTx:
        reConnectHwTexture( newShader )
    
    # 결과 출력:
    print u"#   mayaShader_to_aiStandard : '%s' → '%s'"%(oldShaderName, newShader)
    
    return (newShader)

def VRayMtl_to_aiStandard( oldShader, deleteOldShader=False, assignToObject=False, setAiOpaque=False, addSubfix=True, reconnectHwTx=True, processDisplay=True ):
    # 플러그인 로드
    pm.loadPlugin('vrayformaya', quiet=True)
    pm.loadPlugin('mtoa', quiet=True)

    # 재질이 VRayMtl 인지 확인
    if not ( pm.nodeType(oldShader) == "VRayMtl" ):
        return

    # aiStandard 생성
    #newShader = pm.shadingNode( 'aiStandard', asShader=True ) 
    newShader, newSG = createShader( 'aiStandard' )

    # 이름조정
    if addSubfix:
        spl = oldShader.name().split('_')        
        for a in spl:
            if 'VRay'.lower() in a.lower(): 
                spl.remove(a)
        prefix = '_'.join(spl)
        newShader.rename( prefix +'_aiStandard' )
        newSG.rename( prefix +'_SG'  )
    oldShaderName = oldShader.name()

    # 맵이 연결되어 있으면 연결,
    # 그렇지 않으면 값을 조정 (value/color)
    for fromAttr, toAttr in VRayMtl_to_aiStandard_mappingTable:
        # 범프어트리뷰트는 나중에 처리함.
        if toAttr == 'normalCamera':
            continue

        # 어트리뷰트 캐스팅
        fromAttr = pm.Attribute( oldShader+'.'+fromAttr)
        toAttr   = pm.Attribute( newShader+ '.'+toAttr)

        # 연결된 노드를 생성된 노드에 연결
        if fromAttr.isConnected():
            fromAttr.inputs( p=True )[0] >> toAttr
        
        # 연결된게 없음, 값을 복사에서 집어넣음.
        else:            
            try:
                toAttr.set( fromAttr.get() )
            except:
                print u'#   mayaShader_to_aiStandard : 대입하려는 값의 형식이 상이 합니다. 확인해주세요. ------------------------------------'
                print u'#           %60s : %s'%(fromAttr,fromAttr.get())
                print u'#           %60s : %s'%(toAttr, toAttr.get() )
   
    # 범프가 존재하면, 연결하고 bumpValue 조정
    if oldShader.bumpMap.isConnected():     
        fileNode = oldShader.bumpMap.inputs()[0]

        bumpNode = pm.shadingNode( 'bump2d', asUtility=True )
        fileNode.outAlpha  >> bumpNode.bumpValue
        bumpNode.outNormal >> newShader.normalCamera
        
        # 범프 값 옮김
        bumpNode.bumpDepth.set( oldShader.bumpMult.get() )

    # opacity일겨우 오브젝트 처리
    if setAiOpaque:
        if pm.dt.Vector( newShader.opacity.get() ) < pm.dt.Vector(1,1,1):
            objs = getObjects_fromMaterial( oldShader )
            for obj in objs:
                #if processDisplay: pm.select(obj); pm.refresh()

                obj = pm.PyNode(obj)
                try:
                    obj.aiOpaque.set( False )
                    print "#   VRayMtl_to_aiStandard : set opaque attribute. '%s'"% obj
                except:
                    print '#   VRayMtl_to_aiStandard : can not set opaque attribute. "%s(%s)"' % (obj, pm.nodeType(obj))
                    
    # 새로생성된 쉐이더 적용 : setAiOpaque보다 나중에 처리되어야 함.
    if assignToObject:
        if processDisplay: pm.refresh()
        objs = getObjects_fromMaterial( oldShader )
        assignMaterialToObject( newShader, objs )
    
    # 기존 쉐이더 삭제
    if deleteOldShader:
        pm.delete( oldShader )
        print u"#   VRayMtl_to_aiStandard : '%s' deleted"%oldShaderName

    # 하드웨어 텍스쳐 재연결
    if reconnectHwTx:
        reConnectHwTexture( newShader )
    
    # 결과 출력:
    print u"#   VRayMtl_to_aiStandard : '%s' → '%s' converted."%(oldShaderName, newShader)
    
    return (newShader)

# ------------------------------
# Vray
# ------------------------------
def miaMaterialX_to_VRayMtl( miaX ):
    '''
    # 하다 말았음 나중에 손볼것!
    #
    # mia_material_x --> VRayMtl
    #

    for miax in pm.ls( type=['mia_material_x', 'mia_material_x_passes'] ):        
        # mia_material_x --> VRayMtl
        vray = miaMaterialX_To_VRayMtl( miax )        
        # 오브젝트에 연결
        assignMaterialToObject( material=vray, objects=getObjects_fromMaterial( miax ) )
    '''
    
    # 재질이 mia_material_x 나 mie_material_x_passes 인지 확인
    if not (pm.nodeType(miaX) == "mia_material_x_passes") or (pm.nodeType(miaX) == "mia_material_x"):
        return
    
    # 비교에 사용할 attribute 목록 작성, 
    # miaX attribute 앞, VRay attribute 뒤        
    attrList = [
        ("diffuse",             "color"),
        ("diffuse_weight",      "diffuseColorAmount"),
        ("diffuse_roughness",   "roughnessAmount"),
        ("refl_color",          "reflectionColor"),
        ("reflectivity",        "reflectionColorAmount"),
        ("refl_gloss",          "reflectionGlossiness"),
        ("refl_gloss_samples",  "reflectionSubdivs"),
        ("refl_falloff_on",     "reflectionDimDistanceOn"),
        ("refl_falloff_dist",   "reflectionDimDistance"),
        ("refl_depth",          "reflectionsMaxDepth"),
        ("refr_ior",            "refractionIOR"),
        ("refr_color",          "refractionColor"),
        ("transparency",        "refractionColorAmount"),
        ("refr_gloss",          "refractionGlossiness"),
        ("refr_gloss_samples",  "refractionSubdivs"),
        ("thin_walled",         "refractionIOR")
        ]

    # VRayMtl 생성
    vRayMtl = createVRayMtl()[0]

    # 맵이 연결되어 있으면 연결,
    # 그렇지 않으면 값을 조정 (value/color)
    for miaAttr, vrayAttr in attrList:

        if pm.connectionInfo( miaX +"."+ miaAttr, id=True):
            outAttr = pm.listConnections( miaX+"."+miaAttr, p=True)[0]
            inAttr  = vRayMtl + "." + vrayAttr
            
            pm.connectAttr( outAttr, inAttr )
            
        else:
            outAttr = pm.getAttr( miaX + "." + miaAttr )
            inAttr  = vRayMtl + "." + vrayAttr
            
            pm.setAttr(inAttr, outAttr)
            
    if pm.getAttr(miaX + ".thin_walled") == 1:
        pm.setAttr(vRayMtl + ".refractionIOR", 1)
    
    
    # 범프가 존재하면
    # 연결하고 multiplier를 조정
    if pm.connectionInfo(miaX + ".standard_bump", id=True):
        
        # 연결
        outAttr  = pm.listConnections(miaX + ".standard_bump")[0]
        outValue = pm.listConnections(outAttr + ".bumpValue", p=True)[0]        
        
        inValue  = vRayMtl + "." + 'bumpMap'                
        pm.connectAttr(outValue, inValue+"R")
        pm.connectAttr(outValue, inValue+"G")
        pm.connectAttr(outValue, inValue+"B")
    
        # 값 적용
        outDepth = pm.getAttr(outAttr + ".bumpDepth")
        inDepth  = vRayMtl + "." + 'bumpMult'
        
        pm.setAttr(inDepth, outDepth)
    
    return (vRayMtl)

class mShader_to_VRayMtl(object):
    '''
                        file13 .outColor -----------> color. blinn
                                         -----------> color. VRayMtl
                                                
                               .outTransparency ----> transparency. blinn
                                                ----> transparency. VRayMtl
                                                
                                                
                       file15 .outColor -----------> specularColor.   blinn
                                        -----------> reflectionColor. VRayMtl                                            
                               outAlpha -----------> reflectionGlossiness. VRayMtl
                               
                                                     VRayMtl.useFresnel  1
                                                     VRayMtl.lockFresnelIORToRefractionIOR  0
                           
    file14 .outAlpha ----> bumpValue. bump2d .outNormal ---> normalCamera. blinn
           .outColor -------------------------------------------> bumpMap. VRayMtl
                                                 
                                                     VRayMtl.bumpMapType 1
    
    '''
    
    mShaderAttrs = [
        'color',
        'transparency',
        'specularColor',
        'normalCamera',
        ]
    
    def __init__(self):
        pass
    
    def convert(self):
        for shader in cmds.ls( type=['blinn','phong'] ):
            self.mShader  = shader
            self.VRayMtl, self.VRayMtlSG = self.createVRayMtl( self.mShader+'_VRayMtl' )
            
            self.toVrayMtl()
            
            try:
                cmds.select( getObjects_fromMaterial( self.mShader ) )
                cmds.hyperShade( assign= self.VRayMtl )
                cmds.select( cl=True )
            except:
                pass
   
    def toVrayMtl(self ):        
        # 1. blinn에 연결된 노드 VRayMtl로 재연결
        for attr in self.mShaderAttrs:
            input_plug = self.mShader +'.'+ attr            
            inputs     = cmds.listConnections( input_plug, s=True, d=False, p=True )
            if inputs:            
                # 현재 입력 상태
                inputNode_plug = inputs[0]
                inputNode, inputAttr = inputNode_plug.split('.')            
                print "%s --> %s" % (inputNode_plug, input_plug)
                
                # Vray로 연결
                if   attr == 'color':
                    self.connectToVray( inputNode_plug, 'color')
                    
                elif attr == 'transparency':
                    self.connectToVray( inputNode +'.outAlpha','opacityMapR' )
                    self.connectToVray( inputNode +'.outAlpha','opacityMapG' )
                    self.connectToVray( inputNode +'.outAlpha','opacityMapB' )
                    
                elif attr == 'specularColor':
                    self.connectToVray( inputNode_plug,        'reflectionColor' )
                    self.connectToVray( inputNode +'.outAlpha', 'reflectionGlossiness', )
                
                elif attr == 'normalCamera':
                    inputFileNode = cmds.listConnections( inputNode +'.bumpValue',s=True, d=False )[0]
                    
                    self.connectToVray( inputFileNode +'.outColor', 'bumpMap' )
                    
                    cmds.setAttr( self.VRayMtl+'.bumpMapType', 1 )
                    
        # 2. 기본값 조정
        cmds.setAttr( self.VRayMtl+'.useFresnel', 1 )
        cmds.setAttr( self.VRayMtl+'.lockFresnelIORToRefractionIOR', 1 )
        
    def connectToVray( self, inputNode_outputPlug, VRayMtl_input ):
        """속성 연결 : textureNode.xxx ---> VRayMtl.vrayAttr """        
        VRayMtl_inputPlug = self.VRayMtl +'.'+ VRayMtl_input        
        print "connectTo : %s --> %s" % ( inputNode_outputPlug, VRayMtl_inputPlug )         
        cmds.connectAttr( inputNode_outputPlug, VRayMtl_inputPlug, f=True)
    
    def createVRayMtl( self, name='VRayMtl#' ):
        """VRayMtl 생성"""        
        VRayMtl = cmds.shadingNode( 'VRayMtl', n=name, asShader=True )
        VRayMtlSG = cmds.sets( name=VRayMtl+'SG', renderable=True, noSurfaceShader=True, empty=True )
        cmds.connectAttr( VRayMtl+'.outColor', VRayMtlSG+'.surfaceShader', f=True )
        return VRayMtl, VRayMtlSG

# ----------------------------------------------------------------------------------
#
# Small Utils
#
# ----------------------------------------------------------------------------------
def createVRayMtl( name='VRayMtl#' ):
    """VRayMtl 생성"""        
    VRayMtl   = pm.shadingNode( 'VRayMtl', n=name, asShader=True )
    VRayMtlSG = pm.sets( name=VRayMtl+'SG', renderable=True, noSurfaceShader=True, empty=True )
    pm.connectAttr( VRayMtl+'.outColor', VRayMtlSG+'.surfaceShader', f=True )
    return VRayMtl, VRayMtlSG

def createShader( shaderType ):
    """VRayMtl 생성"""        
    shader = pm.shadingNode( shaderType, asShader=True )
    SG = pm.sets( name=shader+'SG', renderable=True, noSurfaceShader=True, empty=True )
    pm.connectAttr( shader+'.outColor', SG+'.surfaceShader', f=True )
    return shader, SG

def getMaterials_fromObject( objects ):
    """ 입력된 오브젝트들의 shader 리스트를 리턴 """
    sel = cmds.ls(sl=True)

    pm.select( objects )
    pm.hyperShade( smn=True )
    shaders = cmds.ls(sl=True)
    
    if sel: 
        cmds.select(sel)
    else:
        cmds.select( cl=True )

    return shaders

def getObjects_fromMaterial( material ):
    """ 입력된 shader가 적용된 오브젝트(메쉬,넙스...) 리스트를 리턴 """
    sel = cmds.ls(sl=True)
    
    pm.hyperShade( objects=material ) # 이부분에서 메세지 발생함
    objects = pm.ls(sl=True)
    
    if sel: 
        cmds.select(sel)
    else:
        cmds.select( cl=True )

    return objects

def assignMaterialToObject_old( material, objects ):
    ''' 오브젝트에 쉐이더 어싸인'''
    selected = cmds.ls(sl=True)
    
    pm.select( objects )
    pm.hyperShade( assign= material )# 이부분에서 메세지 발생함
    #cmds.select( cl=True )
    
    if selected:
        cmds.select( selected )
    else:
        cmds.select( cl=True )    

def assignMaterialToObject( material, objects ):
    ''' 오브젝트에 쉐이더 어싸인'''
    selected = cmds.ls(sl=True)

    # 재질에 연결된 쉐이딩 그룹 알아옴.
    SGs = pm.PyNode( material ).outputs( type='shadingEngine')
    if not SGs: 
        return 

    # 오브젝트 선택하고, 쉐이딩 그룹과 선택된 오브젝트 연결
    pm.select( objects )    
    pm.sets( SGs[0], e=True, forceElement=True)

    # 선택 복원
    if selected:
        cmds.select( selected )
    else:
        cmds.select( cl=True )
   
def reConnectHwTexture( shader ):
    '''뿌얘진 하느뒈어 텍스쳐를 재연결'''
    shader        = pm.PyNode( shader )

    fileNodes     = shader.color.inputs()
    materialInfos = shader.outputs( type='materialInfo')
        
    if materialInfos and fileNodes:
        try:
            # 잠깐 끊었다가 
            if pm.isConnected( fileNodes[0].message, materialInfos[0].texture[0] ):
                pm.disconnectAttr( fileNodes[0].message, materialInfos[0].texture[0] )

            # 다시연결
            pm.connectAttr( fileNodes[0].message, materialInfos[0].texture[0], na=True, f=True )

        except:
            pass
