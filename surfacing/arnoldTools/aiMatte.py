# -*- coding:utf-8  -*-
import pymel.core as pm
import maya.cmds as cmds
import os 

def redCmd(*arg):
    shader=[]
    select_mesh = pm.selected()
    mat_R = pm.shadingNode("surfaceShader",asShader=True,name="mat_R")
    mat_R.outColor.set([1,0,0])
    for node in select_mesh:
        shape = node.getShape()
        SG = shape.outputs(type='shadingEngine')[0]
        shader = SG.surfaceShader.inputs()
        print SG
        print SG.displacementShader.connections()
        print len(SG.displacementShader.connections())
        print len(shader[0].opacity.connections())
        if     len(SG.displacementShader.connections())==True and len(shader[0].opacity.connections())==True:
            print "displacement and opacity"
            opacity_file = shader[0].opacity.inputs()
            dis_file = SG.displacementShader.inputs()
            mat_R_op_dis = pm.shadingNode("surfaceShader",asShader=True,name="mat_R_op_dis_"+node.name()+"_")
            mat_R_op_dis.outColor.set([1,0,0])
            
            mat_R_reverse = pm.shadingNode("reverse",asShader=True,name="mat_R_reverse_"+shape.name()+"_")
            pm.connectAttr(mat_R_reverse.output,mat_R_op_dis.outTransparency)
            pm.connectAttr(opacity_file[0].outColor,mat_R_reverse.input)

            pm.select(node)
            pm.hyperShade(a = "mat_R_op_dis_"+node.name()+"_")

            # 오퍼시티를     mat_R_op_dis의 오퍼시티에 넣어주면 알파가 안 뽑힌다.
            #pm.connectAttr(opacity_file[0].outColor,mat_R_op_dis.outTransparency) 
            # 오퍼시티가 Transparency매트로 가면서 맵을 인버트해줘야 된다.        
            #get_invert = opacity_file[0].invert.get()
            #mat_R_op_dis.outTransparency.inputs()[0].invert.set(not get_invert)
            
            new_SG = node.getShape().outputs(type = 'shadingEngine')[0]
            pm.connectAttr(dis_file[0].displacement,new_SG.displacementShader)
            pm.select(clear=True)
        elif len(SG.displacementShader.connections())==True and len(shader[0].opacity.connections())==False:
            print "only displacement"
            dis_file = SG.displacementShader.inputs()
            mat_R_dis = pm.shadingNode("surfaceShader",asShader=True,name="mat_R_dis_" + node.name() + "_")
            mat_R_dis.outColor.set([1,0,0])
            pm.select(node)
            pm.hyperShade(a = "mat_R_dis_" + node.name() + "_")
            new_SG = node.getShape().outputs(type = 'shadingEngine')[0]
            pm.connectAttr(dis_file[0].displacement,new_SG.displacementShader)
            pm.select(clear=True)
        elif len(SG.displacementShader.connections())==False and len(shader[0].opacity.connections())==True:
            print "only opacity"
            opacity_file = shader[0].opacity.inputs()
            mat_R_op = pm.shadingNode("surfaceShader",asShader=True,name="mat_R_op_"+node.name()+"_")
            mat_R_op.outColor.set([1,0,0])

            #invert node 를 만들어 준다.
            mat_R_reverse = pm.shadingNode("reverse",asShader=True,name="mat_R_op_"+shape.name()+"_")
            pm.connectAttr(mat_R_reverse.output,mat_R_op.outTransparency)
            pm.connectAttr(opacity_file[0].outColor,mat_R_reverse.input)

            pm.select(node)
            pm.hyperShade(a = "mat_R_op_"+node.name()+"_")
            #pm.connectAttr(opacity_file[0].outColor,mat_R_op.outTransparency)
            # 오퍼시티가 Transparency매트로 가면서 맵을 인버트해줘야 된다.
            #get_invert = opacity_file[0].invert.get()   
            #mat_R_op.outTransparency.inputs()[0].invert.set(not get_invert)
            pm.select(clear=True)
        else:
            print "no opacity and no displacement"
            pm.select(node)
            pm.hyperShade(a="mat_R")
            pm.select(clear=True)
            
def greenCmd(*arg):
    shader=[]
    select_mesh = pm.selected()
    mat_R = pm.shadingNode("surfaceShader",asShader=True,name="mat_G")
    mat_R.outColor.set([0,1,0])
    for node in select_mesh:
        shape = node.getShape()
        SG = shape.outputs(type='shadingEngine')[0]
        shader = SG.surfaceShader.inputs()
        print SG
        print SG.displacementShader.connections()
        print len(SG.displacementShader.connections())
        print len(shader[0].opacity.connections())
        if     len(SG.displacementShader.connections())==True and len(shader[0].opacity.connections())==True:
            print "displacement and opacity"
            opacity_file = shader[0].opacity.inputs()
            dis_file = SG.displacementShader.inputs()
            mat_R_op_dis = pm.shadingNode("surfaceShader",asShader=True,name="mat_G_op_dis_"+node.name()+"_")
            mat_R_op_dis.outColor.set([0,1,0])

            mat_R_reverse = pm.shadingNode("reverse",asShader=True,name="mat_R_reverse_"+shape.name()+"_")
            pm.connectAttr(mat_R_reverse.output,mat_R_op_dis.outTransparency)
            pm.connectAttr(opacity_file[0].outColor,mat_R_reverse.input)

            pm.select(node)
            pm.hyperShade(a = "mat_G_op_dis_"+node.name()+"_")
            
            # 오퍼시티를     mat_R_op_dis의 오퍼시티에 넣어주면 알파가 안 뽑힌다.
            # pm.connectAttr(opacity_file[0].outColor,mat_R_op_dis.outTransparency) 
            # 오퍼시티가 Transparency매트로 가면서 맵을 인버트해줘야 된다.        
            # get_invert = opacity_file[0].invert.get()
            # mat_R_op_dis.outTransparency.inputs()[0].invert.set(not get_invert)
            new_SG = node.getShape().outputs(type = 'shadingEngine')[0]
            pm.connectAttr(dis_file[0].displacement,new_SG.displacementShader)
            pm.select(clear=True)
        elif len(SG.displacementShader.connections())==True and len(shader[0].opacity.connections())==False:
            print "only displacement"
            dis_file = SG.displacementShader.inputs()
            mat_R_dis = pm.shadingNode("surfaceShader",asShader=True,name="mat_G_dis_" + node.name() + "_")
            mat_R_dis.outColor.set([0,1,0])
            pm.select(node)
            pm.hyperShade(a = "mat_G_dis_" + node.name() + "_")
            new_SG = node.getShape().outputs(type = 'shadingEngine')[0]
            pm.connectAttr(dis_file[0].displacement,new_SG.displacementShader)
            pm.select(clear=True)
        elif len(SG.displacementShader.connections())==False and len(shader[0].opacity.connections())==True:
            print "only opacity"
            opacity_file = shader[0].opacity.inputs()
            mat_R_op = pm.shadingNode("surfaceShader",asShader=True,name="mat_G_op_"+node.name()+"_")
            mat_R_op.outColor.set([0,1,0])

            #invert node 를 만들어 준다.
            mat_R_reverse = pm.shadingNode("reverse",asShader=True,name="mat_R_op_"+shape.name()+"_")
            pm.connectAttr(mat_R_reverse.output,mat_R_op.outTransparency)
            pm.connectAttr(opacity_file[0].outColor,mat_R_reverse.input)
            pm.select(node)
            pm.hyperShade(a = "mat_G_op_"+node.name()+"_")
            #pm.connectAttr(opacity_file[0].outColor,mat_R_op.outTransparency)
            # 오퍼시티가 Transparency매트로 가면서 맵을 인버트해줘야 된다.
            #get_invert = opacity_file[0].invert.get()   
            #mat_R_op.outTransparency.inputs()[0].invert.set(not get_invert)
            pm.select(clear=True)
        else:
            print "no opacity and no displacement"
            pm.select(node)
            pm.hyperShade(a="mat_G")
            pm.select(clear=True)
    
def blueCmd(*arg):
    shader=[]
    select_mesh = pm.selected()
    mat_R = pm.shadingNode("surfaceShader",asShader=True,name="mat_B")
    mat_R.outColor.set([0,0,1])
    for node in select_mesh:
        shape = node.getShape()
        SG = shape.outputs(type='shadingEngine')[0]
        shader = SG.surfaceShader.inputs()
        print SG
        print SG.displacementShader.connections()
        print len(SG.displacementShader.connections())
        print len(shader[0].opacity.connections())
        if     len(SG.displacementShader.connections())==True and len(shader[0].opacity.connections())==True:
            print "displacement and opacity"
            opacity_file = shader[0].opacity.inputs()
            dis_file = SG.displacementShader.inputs()
            mat_R_op_dis = pm.shadingNode("surfaceShader",asShader=True,name="mat_B_op_dis_"+node.name()+"_")
            mat_R_op_dis.outColor.set([0,0,1])

            mat_R_reverse = pm.shadingNode("reverse",asShader=True,name="mat_R_reverse_"+shape.name()+"_")
            pm.connectAttr(mat_R_reverse.output,mat_R_op_dis.outTransparency)
            pm.connectAttr(opacity_file[0].outColor,mat_R_reverse.input)

            pm.select(node)
            pm.hyperShade(a = "mat_B_op_dis_"+node.name()+"_")
            # 오퍼시티를     mat_R_op_dis의 오퍼시티에 넣어주면 알파가 안 뽑힌다.
            #pm.connectAttr(opacity_file[0].outColor,mat_R_op_dis.outTransparency) 
            # 오퍼시티가 Transparency매트로 가면서 맵을 인버트해줘야 된다.        
            #get_invert = opacity_file[0].invert.get()
            #mat_R_op_dis.outTransparency.inputs()[0].invert.set(not get_invert)
            
            new_SG = node.getShape().outputs(type = 'shadingEngine')[0]
            pm.connectAttr(dis_file[0].displacement,new_SG.displacementShader)
            pm.select(clear=True)
        elif len(SG.displacementShader.connections())==True and len(shader[0].opacity.connections())==False:
            print "only displacement"
            dis_file = SG.displacementShader.inputs()
            mat_R_dis = pm.shadingNode("surfaceShader",asShader=True,name="mat_B_dis_" + node.name() + "_")
            mat_R_dis.outColor.set([0,0,1])
            pm.select(node)
            pm.hyperShade(a = "mat_B_dis_" + node.name() + "_")
            new_SG = node.getShape().outputs(type = 'shadingEngine')[0]
            pm.connectAttr(dis_file[0].displacement,new_SG.displacementShader)
            pm.select(clear=True)
        elif len(SG.displacementShader.connections())==False and len(shader[0].opacity.connections())==True:
            print "only opacity"
            opacity_file = shader[0].opacity.inputs()
            mat_R_op = pm.shadingNode("surfaceShader",asShader=True,name="mat_B_op_"+node.name()+"_")
            mat_R_op.outColor.set([0,0,1])

            mat_R_reverse = pm.shadingNode("reverse",asShader=True,name="mat_R_op_"+shape.name()+"_")
            pm.connectAttr(mat_R_reverse.output,mat_R_op.outTransparency)
            pm.connectAttr(opacity_file[0].outColor,mat_R_reverse.input)
            
            pm.select(node)
            pm.hyperShade(a = "mat_B_op_"+node.name()+"_")
            #pm.connectAttr(opacity_file[0].outColor,mat_R_op.outTransparency)
            # 오퍼시티가 Transparency매트로 가면서 맵을 인버트해줘야 된다.
            #get_invert = opacity_file[0].invert.get()   
            #mat_R_op.outTransparency.inputs()[0].invert.set(not get_invert)
            pm.select(clear=True)
        else:
            print "no opacity and no displacement"
            pm.select(node)
            pm.hyperShade(a="mat_B")
            pm.select(clear=True)
    
def alphaCmd(*arg):
    select_mesh=pm.selected()
    
    print pm.objExists('aiMatteSet:Matte' )

    if pm.objExists('aiMatteSet:Matte' )==False:
        #pm.namespace(rm='aiMatteSet',deleteNamespaceContent =True)
        print "improt file"
        pm.importFile( "//ALFREDSTORAGE/Alfred_asset/Maya_Shared_Environment/scripts_Python_old/aiMatte.ma", type = "mayaAscii",namespace="aiMatteSet")
    else:
        pass
    nodes=pm.select(select_mesh)
    for node in select_mesh:
        shape = node.getShape()
        cmds.sets(addElement=shape,add='aiMatteSet:Matte')

    for i in range(0,100):
        if pm.namespace(exists='aiMatteSet'+str(i)):
            pm.namespace(rm='aiMatteSet'+str(i),deleteNamespaceContent =True)
        else:
            pass

def ui():
    #masking이란 윈도우가 있는지를 확인한다. q는 확인하다. exists는 존재여부를 체크한다.
    if pm.window('masking', q=True, exists=True) :
        pm.deleteUI('masking')

    with pm.window('masking',menuBar=True, s=True):
        pm.menu(l='help')
        pm.menuItem(l='document', c=pm.Callback( os.system, "D:/Users/blood/Desktop/eyeTest_01.mov" ))
        pm.menuItem(l='tutorial', c=pm.Callback( pm.launch, web="https://www.youtube.com/watch?v=-JwXfnrX1wM") )
        with pm.columnLayout( adj=True ):
            with pm.rowLayout(nc=4):
                pm.button(l='', w=64, h=64, bgc=(1,0,0), c=redCmd )
                pm.button(l='', w=64, h=64, bgc=(0,1,0), c=greenCmd )
                pm.button(l='', w=64, h=64, bgc=(0,0,1), c=blueCmd)
                pm.button(l='matte', w=64, h=64, bgc=(0.2,0.2,0.2), c=alphaCmd)


