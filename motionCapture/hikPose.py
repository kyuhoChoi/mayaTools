# coding=utf-8
'''
a = hikPose()
a.getHikCtrl()
a.HIKCharacterNode
'''

__author__ = 'Kyuho Choi | coke25@aiw.co.kr | Alfred Imageworks'

import pymel.core as pm

class hikPose(object):
    def __init__(self):
        self.HIKCharacterNode = None
        self.HIKControlSetNode = None

    def getHikCtrl(self):
        for node in pm.ls(type=['hikIKEffector','hikFKJoint']):
            for attr in node.listAttr( keyable=True ):
                print attr.split(':')[-1]

    def setHIKCharacterNode(self):
        sel = pm.selected()

        if not sel: raise 

        node = sel[0]
        ns = node.namespace()
        nodes = pm.ls('%s*'%ns, type='HIKCharacterNode')

        if not nodes: raise

        self.HIKCharacterNode = nodes[0]

    def setHIKControlSetNode(self):
        sel = pm.selected()

        if not sel: raise 

        node = sel[0]
        ns = node.namespace()
        nodes = pm.ls('%s*'%ns, type='HIKControlSetNode')

        if not nodes: raise

        self.HIKControlSetNode = nodes[0]

    def printPose(self):
        cmd = '''
        # ---------------------------------
        import pymel.core as pm

        sel = pm.selected()
        if sel:
            ns = sel[0].namespace()
        else:
            ns = ''
        '''
        for hikCtrl in pm.ls(type=['hikIKEffector','hikFKJoint']):
            for attr in hikCtrl.listAttr( keyable=True ):
                name = attr.split(':')[-1]
                cmd += 'pm.Attribute( ns+"%s" ).set(%s)\n'%(name,attr.get())
        cmd+='# ---------------------------------'
        print cmd