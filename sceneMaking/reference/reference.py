import pymel.core as pm
import maya.cmds as cmds
import os

def getReferenceNode( *nodes ):
    if nodes:
        pm.select(nodes)    
    nodes = pm.ls(sl=True)
    if not nodes:
        raise
        
    refNodes = []    
    # 알아오기
    for node in nodes:

        # 레퍼런스가 아니면 제낌
        if not pm.referenceQuery( node, isNodeReferenced=True ):
            continue

        refNode = pm.referenceQuery( node, referenceNode=True )
        refNode = pm.PyNode( refNode )
        refNodes.append( refNode )
    
    # 중복 파일 제거
    refNodes = list(set(refNodes))

    return refNodes

def getReferenceFilepath( *nodes ):
    if nodes:
        pm.select(nodes)    
    nodes = pm.ls(sl=True)
    if not nodes:
        raise
    
    refNodes = getReferenceNode( nodes )
    
    # 알아오기
    filePaths = []
    for refNode in refNodes:
        filePath = pm.referenceQuery( refNode, filename=True )
        filePaths.append( filePath )
    
    return filePaths

def getMayaFileType( filePath ):               # filePath = 'X:/scenes/character/TR_EXT_07.mb'
    _path, _ext = os.path.splitext(filePath)   # Result: ('X:/scenes/character/TR_EXT_07', '.mb')
    _ext = _ext[1:]                            # Result: 'mb' 

    if   _ext == 'mb'  : return 'mayaBinary'
    elif _ext == 'ma'  : return 'mayaAscii'
    elif _ext == 'mel' : return 'mel'
    elif _ext == 'fbx' : return 'FBX'
    elif _ext == 'obj' : return 'OBJ'
    elif _ext in ['jpg','png','tga','tif','psd'] : 
        return 'image'
    else: 
        return _ext

def getBasename( filePath ):
    return pm.mel.basenameEx(filePath)

def getNamespace( *nodes ):
    if nodes:
        pm.select(nodes)    
    nodes = pm.ls(sl=True)
    if not nodes:
        raise

    return nodes[0].namespace()

def getAllReferenceNodes():
    return pm.ls(type='reference')

def refCreate( filePath, namespace='REF' ):
    # mel : file -r -type "mayaBinary" -gl -loadReferenceDepth "all" -mergeNamespacesOnClash false -namespace "Torres" -options "v=0;" "X:/2012_CounterStrike2_V2/3D_project/Share/scenes/character/TR_EXT_07.mb";
    cmds.file(
        filePath,
        r = True,
        type = getMayaFileType(filePath),
        gl = True,
        loadReferenceDepth = 'all',
        mergeNamespacesOnClash = False,
        namespace = namespace,
        options="v=0;"
        )
    # return 

def refReplace( referenceNode, filePath ):
    # 레퍼런스 불러오기
    #file -r -type "mayaBinary" -gl -loadReferenceDepth "all" -mergeNamespacesOnClash false -namespace "MC" -options "v=0;" "X:/2012_chaguchagu/3D_project/scenes/Characters/Extra_Reporter_M_05.mb";

    # 레퍼런스 교체
    #cmds.file( "X:/2012_chaguchagu/3D_project/scenes/Characters/Extra_W_02.mb", loadReference="Extra07RN", type="mayaBinary", options="v=0" )

    refNodes   = []
    # 입력된 값이 순서열인지, 스트링인지 확인
    if   type(referenceNode) in [list,tuple,set]:
        refNodes = referenceNode
    elif type(referenceNode) in [str,unicode]:
        refNodes = [referenceNode]

    # 중복 파일 제거
    refNodes = list(set(refNodes))

    # 
    if not refNodes:
        return

    print u'#------- 교체할 레퍼런스 리스트 : '
    print 'referenceNode = [\'%s\']'%'\', \''.join(refNodes)
    
    # 교체
    _RNnum = len(refNodes)
    for _i,referenceNode in enumerate(refNodes):
        print u'#------- 레퍼런스 교체중 (%s/%s): %s --> "%s"  '%(_i+1,_RNnum, referenceNode, filePath)
        cmds.file( filePath, loadReference=referenceNode, type="mayaBinary", options="v=0" )

def refRemove( referenceNode ):
    refNodes   = []
    # 입력된 값이 순서열인지, 스트링인지 확인
    if   type(referenceNode) in [list,tuple,set]:
        refNodes = referenceNode
    elif type(referenceNode) in [str,unicode]:
        refNodes = [referenceNode]

    # 중복 파일 제거
    refNodes = list(set(refNodes))

    # 
    if not refNodes:
        return

    print u'#------- 제거할 레퍼런스 리스트 : '
    print 'referenceNode = [\'%s\']'%'\', \''.join(refNodes)
    
    # 교체
    _RNnum = len(refNodes)
    for _i,referenceNode in enumerate(refNodes):
        print u'#------- 레퍼런스 제거중 (%s/%s): "%s"'%(_i+1, _RNnum, referenceNode),
        
        # 존재하지 않는 노드이면 메세지 출력하고 다음으로 넘어감.
        if not cmds.objExists(referenceNode):
            print u'(노드가 존재하지 않습니다.) '
            continue
        
        print '' #다음줄로 넘어감

        #file -removeReference -referenceNode "object1RN";
        cmds.file( removeReference=True, referenceNode=referenceNode )

def refReload( referenceNode ):
    refNodes   = []
    # 입력된 값이 순서열인지, 스트링인지 확인
    if   type(referenceNode) in [list,tuple,set]:
        refNodes = referenceNode
    elif type(referenceNode) in [str,unicode]:
        refNodes = [referenceNode]

    # 중복 파일 제거
    refNodes = list(set(refNodes))

    # 
    if not refNodes:
        return

    print u'#------- 갱신할 레퍼런스 리스트 : '
    print 'referenceNode = [\'%s\']'%'\', \''.join(refNodes)

    _RNnum = len(refNodes)
    for _i,referenceNode in enumerate(refNodes):
        print u'#------- 레퍼런스 갱신중 (%s/%s): "%s"'%(_i+1, _RNnum, referenceNode),

        # 존재하지 않는 노드이면 메세지 출력하고 다음으로 넘어감.
        if not cmds.objExists(referenceNode):
            print u'(노드가 존재하지 않습니다.) '
            continue
        
        print '' #다음줄로 넘어감

        _lock = cmds.getAttr ( referenceNode +".locked")
        cmds.file( unloadReference=referenceNode )
        cmds.setAttr ( referenceNode +".locked", _lock)
        cmds.file( loadReference=referenceNode )

def refImport( *nodes ):
    '''
    update : 2015-04-23
    return : [unicode]
    '''
    if nodes:
        pm.select(nodes)    
    nodes = pm.ls(sl=True)
    if not nodes:
        raise

    refNodes = getReferenceNode(nodes)
    if not refNodes:
        raise

    print u'#------- import 레퍼런스 리스트 : '
    print 'referenceNode = [\'%s\']'%'\', \''.join(refNodes)

    _RNnum = len(refNodes)
    for _i,referenceNode in enumerate(refNodes):
        print u'#------- 레퍼런스 import 중~ (%s/%s): "%s"'%(_i+1, _RNnum, referenceNode),

        # 존재하지 않는 노드이면 메세지 출력하고 다음으로 넘어감.
        if not cmds.objExists(referenceNode):
            print u'(노드가 존재하지 않습니다.) '
            continue
        
        print '' #다음줄로 넘어감

        cmds.file( importReference=True, referenceNode=referenceNode)

def refUnload( *nodes ):
    '''
    update : 2015-04-23
    return : [unicode]
    '''
    if nodes:
        pm.select(nodes)    
    nodes = pm.ls(sl=True)
    if not nodes:
        raise

    for ref in getReferenceNode( nodes ):
        cmds.file( unloadReference=ref.name() )

def getUnloadedRefs():
    '''
    update : 2015-04-23
    return : [unicode]
    '''
    unloadedRefs = []
    for node in cmds.ls(type='reference'):
        if node == 'sharedReferenceNode':
            continue
            
        cond = cmds.referenceQuery(node, isLoaded=True)
        if not cond:
            unloadedRefs.append( node )
    return unloadedRefs

def loadAllReference():
    '''
    update : 2015-04-23
    return : None
    '''
    for ref in getUnloadedRefs()
        cmds.file( loadReference=ref )
    
