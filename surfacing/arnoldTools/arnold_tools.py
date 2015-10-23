# coding=utf-8
__author__ = 'Kyuho Choi | coke25@aiw.co.kr | Alfred Imageworks'

import pymel.core as pm

def arnold_subDiv( subD=2 ):
    sel = pm.ls(sl=True, dag=True, type='mesh')
    
    for mesh in sel:
        # 매개 오브젝트이면 패스
        if mesh.intermediateObject.get():
            continue

        # 아놀들 섭디비젼 세팅
        mesh.aiSubdivType.set(1)
        mesh.aiSubdivIterations.set(2)

        print '"%s".aiSubdivIterations.set(%d)' % (mesh,subD)
        
