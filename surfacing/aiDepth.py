# -*- coding:utf-8  -*-
import os
import pymel.core as pm
import maya.cmds as cmds
def creatAll(*arg):
    #depth에 필요한 세더를 만든다.
    Mysshdr = cmds.shadingNode("surfaceShader", asShader=True)
    cmds.rename(Mysshdr,"An_XYZ")
    
    Mysampler = cmds.shadingNode("samplerInfo", asUtility=True)
    cmds.rename(Mysampler,"An_sampler")
    
    Myrange = cmds.shadingNode("setRange", asUtility=True)
    cmds.rename(Myrange,"An_range")
    
    Mymltipl = cmds.shadingNode("multiplyDivide", asUtility=True)
    cmds.rename(Mymltipl,"An_multy")
    
    cmds.connectAttr ( "An_sampler.pointCameraX", "An_multy.input1X",force=True)
    cmds.connectAttr ( "An_sampler.pointCameraY", "An_multy.input1Y",force=True)
    cmds.connectAttr ( "An_sampler.pointCameraZ", "An_multy.input1Z",force=True)
    cmds.setAttr("An_multy.input2X", 1)
    cmds.setAttr("An_multy.input2Y", 1)
    cmds.setAttr("An_multy.input2Z", 1)
    
    cmds.connectAttr ( " An_multy.outputX", "An_range.valueX",force=True)
    cmds.connectAttr ( " An_multy.outputY", "An_range.valueY",force=True)
    cmds.connectAttr ( " An_multy.outputZ", "An_range.valueZ",force=True)
    cmds.setAttr("An_range.minX", 1)
    cmds.setAttr("An_range.minY", 1)
    cmds.setAttr("An_range.minZ", 1)
    
    cmds.connectAttr ( " An_range.outValue.outValueX", "An_XYZ.outColorR",force=True)
    cmds.connectAttr ( " An_range.outValue.outValueY", "An_XYZ.outColorG",force=True)
    cmds.connectAttr ( " An_range.outValue.outValueZ", "An_XYZ.outColorB",force=True)
    
    #혹시 aov에 쓸수 있으니깐 aov를 만들어 준다.
    import mtoa.aovs as aovs
    aovs.AOVInterface().addAOV('XYZ') 
    cmds.connectAttr ( "An_XYZ.outColor", "aiAOV_XYZ.defaultValue", force=True)
    
    #viewport에서 지오메트리리 쉐프만 선택한다.
    #select_shape = cmds.ls( geometry=True,v=True )
    select_shape = pm.ls(type="mesh")
    
    get_invert_list=[]
    
    for shape_str in select_shape:
        #shape_str은 스트링으로 출력되서 PyNode를 사용하여 shape_str를 캐스팅해준다고 한다.
        #스트링으로된 이름을 노드로 타입바꿔주는것 같다.
        shape = pm.PyNode(shape_str)
        SG = shape.outputs(type='shadingEngine')[0]
        shader = SG.surfaceShader.inputs()
        print SG.displacementShader.connections()
        if len(SG.displacementShader.connections())==True and len(shader[0].opacity.connections())==True:
            print "displacement and opacity"
    
            opacity_file = shader[0].opacity.inputs()
            
            dis_file = SG.displacementShader.inputs()
            
            XYZdepth_op_dis = pm.shadingNode("surfaceShader",asShader=True,name="XYZdepth_op_dis_"+shape.name()+"_")
            XYZdepth_op_dis.outColor.set([1,0,0])
            #invert node 를 만들어 준다.
            
            XYZdepth_reverse = pm.shadingNode("reverse",asShader=True,name="XYZdepth_reverse_"+shape.name()+"_")
            
            pm.connectAttr(XYZdepth_reverse.output,XYZdepth_op_dis.outTransparency)
            pm.connectAttr(opacity_file[0].outColor,XYZdepth_reverse.input)
    
            pm.select(shape)
            pm.hyperShade(a = "XYZdepth_op_dis_"+shape.name()+"_")
            
            # depth의 컬러 값을 surface shader에 연결해준다.
            pm.connectAttr("An_range.outValue",XYZdepth_op_dis.outColor) 
            # 오퍼시티를     XYZdepth_op_dis의 오퍼시티에 넣어주면 알파가 안 뽑힌다.
            # pm.connectAttr(opacity_file[0].outColor,XYZdepth_op_dis.outTransparency) 
            # 오퍼시티가 Transparency매트로 가면서 맵을 인버트해줘야 된다.        
            
            #get_invert = opacity_file[0].invert.get()
            #get_invert_list.append(not get_invert)
            #print get_invert_list
    
            #XYZdepth_op_dis.outTransparency.inputs()[0].invert.set(get_invert_list[0])
            #print XYZdepth_op_dis.outTransparency.inputs()[0].invert.get()
            
            new_SG = shape.outputs(type = 'shadingEngine')[0]
            pm.connectAttr(dis_file[0].displacement,new_SG.displacementShader)
            
            pm.select(clear=True)
            
        elif len(SG.displacementShader.connections())==True and len(shader[0].opacity.connections())==False:
            print "only displacement"
            dis_file = SG.displacementShader.inputs()
            
            XYZdepth_dis = pm.shadingNode("surfaceShader",asShader=True,name="XYZdepth_dis_" + shape.name() + "_")
            XYZdepth_dis.outColor.set([1,0,0])
            
            pm.select(shape)
            pm.hyperShade(a = "XYZdepth_dis_" + shape.name() + "_")
            # depth의 컬러 값을 surface shader에 연결해준다.
            pm.connectAttr("An_range.outValue",XYZdepth_dis.outColor)
             
            new_SG = shape.outputs(type = 'shadingEngine')[0]
            pm.connectAttr(dis_file[0].displacement,new_SG.displacementShader)
            
            pm.select(clear=True)
            
        elif len(SG.displacementShader.connections())==False and len(shader[0].opacity.connections())==True:
            print "only opacity"
            opacity_file = shader[0].opacity.inputs()
            
            XYZdepth_op = pm.shadingNode("surfaceShader",asShader=True,name="XYZdepth_op_"+shape.name()+"_")
            XYZdepth_op.outColor.set([1,0,0])
            
            #invert node 를 만들어 준다.
            XYZdepth_reverse = pm.shadingNode("reverse",asShader=True,name="XYZdepth_op_"+shape.name()+"_")
            pm.connectAttr(XYZdepth_reverse.output,XYZdepth_op.outTransparency)
            pm.connectAttr(opacity_file[0].outColor,XYZdepth_reverse.input)
            
            pm.select(shape)
            pm.hyperShade(a = "XYZdepth_op_"+shape.name()+"_")
            # depth의 컬러 값을 surface shader에 연결해준다.
            pm.connectAttr("An_range.outValue",XYZdepth_op.outColor)
            
            pm.select(clear=True)
            
        else:
            print "no opacity and no displacement"
            pm.select(shape)
            pm.hyperShade(a="An_XYZ")
            pm.select(clear=True)

def adjustAll(*arg):
    xyz=pm.window(title="XYZ Adjust", s=True, wh=(100, 50))
    with pm.columnLayout(adj=True):
            pm.text(l="Adjust the Min & Max values")
            pm.attrControlGrp( l="X Min", attribute='An_range.oldMinX' )
            pm.attrControlGrp( l="X Max", attribute='An_range.oldMaxX' )
            pm.attrControlGrp( l="Y Min", attribute='An_range.oldMinY' )
            pm.attrControlGrp( l="Y Max", attribute='An_range.oldMaxY' )
            pm.attrControlGrp( l="Z Min", attribute='An_range.oldMinZ' )
            pm.attrControlGrp( l="Z Max", attribute='An_range.oldMaxZ' )
    pm.showWindow(xyz) 
#ui로 한번 감싸준다.
def ui():
    if pm.window('Depth tool',q=True, exists=True):
        pm.deleteUI('Depth tool')
    with pm.window('Depth tool',menuBar=True,s=False):
        pm.menu(l='help')
        pm.menuItem(l='document', c=pm.Callback( os.system, "D:/Users/blood/Desktop/eyeTest_01.mov" ))
        pm.menuItem(l='tutorial', c=pm.Callback( pm.launch, web="https://www.youtube.com/watch?v=-JwXfnrX1wM") )
        with pm.columnLayout(adj=True):
            with pm.rowLayout(nc=2):
                pm.button(l='Create'+'\n'+'Depth', w=64, h=64,bgc=(0.2,0.2,0.2), c=creatAll )
                pm.button(l='Adjust'+'\n'+'Min&&Max', w=64, h=64, bgc=(0.8,0.8,0.8), c=adjustAll)
