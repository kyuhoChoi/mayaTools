# coding=utf-8
__author__ = 'Yongjun Wu | wuyongjun@naver.com | Mofac&alfred MG1 FX | 20151021'

import pymel.core as pm
import maya.cmds as cmds

# 
# AbcExport -j "-frameRange 0 9 -step 1 -preRoll -frameRange 10 40 -attr aiExposure -attr aiOpaque -attr aiSubdivType -attr aiSubdivIterations -attr aiSubdivUvSmoothing -attr aiSubdivSmoothDerivs -attr aiSubdivPixelError -attr aiSubdivAdaptiveMetric -ro -uvWrite -worldSpace -writeVisibility -eulerFilter -writeCreases -dataFormat ogawa -root |char_grp|char_B:Group|char_B:Geometry|char_B:RenderGeo_grp|char_B:leoA_highM|char_B:leo_A_body_mo -file Y:/2015_R&D_Project/11_Alembic/soo/3D_project/cache/alembic/tmp1.abc";
#

# 선택리스트 
# print "['%s']"%"', '".join( [n.name() for n in pm.ls(sl=True)] )

def export( filePath, startFrame=0, endFrame=40, step=1 ):
    sel = pm.ls(sl=True)
    #filePath = directory + fileName 
    exportSG ( filePath )
    
    pm.select(sel)
    exportAbc( filePath , startFrame, endFrame, step )


def exportAbc( filePath, startFrame=0, endFrame=40, step=1, ):
    '''
    > General Options 
        Chache time range 
        step : 몇프레임 간격으로 익스포트할지 설정
        Frame relative sample : 물 시뮬레이션처럼 mesh point 개수 변할때 사용
        Pre-Roll : 렌더걸리는 프레임 이전에 시뮬레이션이 필요한 경우에 사용. (클로스 작업할때)

    > Cache Time Ranges 
    
    '''
    ######################
    #
    # export Selected
    #
    ######################

    
    
    #
    # Options
    #
    # filePath = 'Y:/2015_R&D_Project/11_Alembic/soo/3D_project/cache/alembic/tmp1.abc'
    # startFrame = 10
    # endFrame = 40
    # step = 1
    preRoll = True
    ro = True
    uvWrite = True
    stripNamespaces = False
    worldSpace = True
    writeVisibility = True
    eulerFilter = True
    writeCreases = True
    dataFormat = "ogawa"

    #
    # attribute Option (Arnold Setting)
    #
    attrs = [
        'displaySmoothMesh',
        'smoothMeshSelectionMode',
        'displaySubdComps',
        'smoothLevel',
        'useSmoothPreviewForRender',
        'renderSmoothLevel',

        'aiExposure', 
        'aiOpaque', 
        'aiSubdivType', 
        'aiSubdivIterations', 
        'aiSubdivUvSmoothing', 
        'aiSubdivSmoothDerivs', 
        'aiSubdivPixelError', 
        'aiSubdivAdaptiveMetric'
        ]

    #
    # String Operation
    #
    sel = cmds.ls( sl=True, long=True, o=True)
    jobArgs = []
    jobArgs.append( "-frameRange %d %d" % (startFrame,endFrame) )
    if ro               : jobArgs.append( "-ro" )
    if uvWrite          : jobArgs.append( "-uvWrite" )
    if worldSpace       : jobArgs.append( "-worldSpace" )
    if writeVisibility  : jobArgs.append( "-writeVisibility" )
    if eulerFilter      : jobArgs.append( "-eulerFilter" )
    if writeCreases     : jobArgs.append( "-writeCreases" )
    if dataFormat       : jobArgs.append( "-dataFormat %s" % dataFormat )
    for s in sel        : jobArgs.append( "-root %s" % s )
    for attr in attrs   : jobArgs.append( "-attr %s" % attr )
    jobArgs.append( "-file %s"%filePath )

    #
    # DoIt
    #
    pm.AbcExport( jobArg=" ".join(jobArgs) )

def exportSG( filePath):
    #filePath = "Y:/2015_R&D_Project/11_Alembic/soo/3D_project/cache/alembic/B_01_SGs.ma"
    
    import pymel.core as pm
    SGs = []
    shaders = []
    connections = []
    for node in pm.ls(sl=True, o=True):
        shape = node.getShape()        
        shadingGrps = shape.outputs( type='shadingEngine' )
        if shadingGrps:
            shader = shadingGrps[0].surfaceShader.inputs()[0]       
            SGs.append(shadingGrps[0])
            shaders.append(shader)
            node_name = node.split(":")[-1]
            print node_name
            #connections.append([node_name,shader.name()])
            connections.append([node.name(),shader.name()])

    #.abc를 없애준다
    filePathDeletAbc = filePath.replace('.abc','')
    # 세이더 정보 txt파일에 쓴다
    connectionsTxtFile=open(filePathDeletAbc+'.txt','w')
    import pickle
    pickle.dump(connections,connectionsTxtFile)
    connectionsTxtFile.close()
	
    # export
    exportLs = shaders
    pm.select(exportLs)
    pm.exportSelected( filePathDeletAbc+'.ma' )
    
    # 연결정보 출력
    # connectionsTxt=[]
    # for con in connections:
        # connectionsTxt="['%s']," % ', '.join(con)
        # print "['%s']," % ', '.join(con)


def importExAbc( abcFile ):
    #ExocortexAlembic 가 laod 되어 있는지를 체크 한다.
    if not pm.pluginInfo('MayaExocortexAlembic', q=True, loaded=True):
        pm.loadPlugin('MayaExocortexAlembic')
    cmds.ExocortexAlembic_import(j=[abcFile])
    #pm.AbcImport( abcFile, mode='import' )

def importAbc( abcFile ):
    if not pm.pluginInfo('MayaExocortexAlembic', q=True, loaded=True):
        pm.loadPlugin('MayaExocortexAlembic')
    pm.AbcImport( abcFile, mode='import' )

def deleteUnknownNodes():
    # 2 things to take care of:
    #   1) you can't delete nodes from references.
    #   2) "delete" will delete all children nodes (hierarchy) in default.
    unknown = pm.ls(type="unknown")
    print unknown
    unknown = filter(lambda node: not node.isReferenced(), unknown)
    for node in unknown:
        if not pm.objExists(node):
            continue
        pm.delete(node)
    
#
# TestCode


#마야 파일을 exprot 한다.
def exportScene():
    filePath= pm.textField('path_TFG', q=True, text=True )
    pm.selected()
    #directory = 'C:/Users/Administrator/Desktop/alembic/'
    #fileName = 'B_02'
    deleteUnknownNodes()
    startFrame = pm.floatFieldGrp( 'timeRange_FFG', q=True, value1=True )
    endFrame   = pm.floatFieldGrp( 'timeRange_FFG', q=True, value2=True )
    export( filePath, startFrame, endFrame, 1 )

#마야 파일을 exprot 한다.
def buildscene():
    #scene building                                                                                                                                                                                                                                                 
    pm.newFile( f=True )
    #anorld 가 laod 되어 있는지를 체크 한다.
    if not pm.pluginInfo('mtoa', q=True, loaded=True):
        pm.loadPlugin('mtoa')
    #랜더러를 anorld로 만들어 준다.
    defaultRenderGlobals = pm.PyNode('defaultRenderGlobals')
    defaultRenderGlobals.currentRenderer.set('arnold')

def importAbcFile():
    importFilePath=pm.textField('path_ABC2', q=True, text=True)
    #.abc를 없애준다
    filePathDeletAbc = importFilePath.replace('.abc','')

    pm.importFile( filePathDeletAbc+'.ma' )
    importAbc( filePathDeletAbc+'.abc' )
    connectionsTxtFile_open = open(filePathDeletAbc+'.txt')
    import pickle
    lst = pickle.load(connectionsTxtFile_open)
    print lst
    for geo, shd in lst:
        cmds.select( geo )
        cmds.hyperShade( assign=shd )

def saveScene():
    saveFilePath = pm.textField('path_TFG2', q=True, text=True )
    pm.saveAs(saveFilePath)

#---------------------------------------------------------------------------------------
def callback_timerangeSelect(*args):
    #print args

    opt = args[0]
    pm.floatFieldGrp( 'timeRange_FFG', e=True, en=False )
    if opt==1:
        try:
            camera = pm.textField( 'camera_TFG', q=True, text=True )
            pm.floatFieldGrp( 'timeRange_FFG', e=True, value1=camera.startFrame.get(), value2=camera.endFrame.get() )
        except:
            pass
    elif opt==2:
        pm.floatFieldGrp( 'timeRange_FFG', e=True, value1=pm.playbackOptions( q=True, min=True ), value2=pm.playbackOptions( q=True, max=True ) )
    elif opt==3:
        pm.floatFieldGrp( 'timeRange_FFG', e=True, en=True )

'''
def dirPath(filePath, fileType):
    pm.textFieldGrp('path_TFG', edit=True, text=str(filePath) )
    return 1
'''

def browseIt( txtFieldName, fileMode=1, multipleFilters="Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)" ):
    cur = pm.textField( txtFieldName, q=True, text=True )
    result = pm.fileDialog2( fileFilter=multipleFilters, fileMode=fileMode, dir=cur )
    if result:
        pm.textField( txtFieldName, e=True, text=result[0] )
    return 

def ui():
    columnWidth1st = 120

    if pm.window('AlembicMasterUI', q=True, exists=True) : pm.deleteUI('AlembicMasterUI')

    with pm.window('AlembicMasterUI',menuBar=True, s=True):
        with pm.columnLayout(adj=True):
            with pm.frameLayout( label='Export Alembic', mw=3, mh=3,cll=True, bs='etchedIn'):
                with pm.columnLayout(adj=True):
                    with pm.rowLayout(nc=3, adj=2):
                        pm.text(label='file :', w=columnWidth1st, align='right')
                        pm.textField('path_TFG', text="D:/")
                        pm.symbolButton( image='navButtonBrowse.png', c=pm.Callback( browseIt, 'path_TFG', 0, 'Alembic (*.abc)'  ) )
                        
                    with pm.rowLayout(nc=2, adj=2 ):
                        startFrame=pm.animation.playbackOptions(q=1, minTime=1)
                        EndFrame=pm.animation.playbackOptions(q=1, maxTime=1)
                        
                    with pm.rowLayout(nc=2, adj=2):
                        pm.text(l='',w=columnWidth1st)
                        pm.button(l='Export',bgc=(0.19,0.29,0.19),c=pm.Callback(exportScene))
                        
                    pm.radioButtonGrp( 'timeRange_RBG', label='Time range :', 
                        labelArray3=['Camera Setting','Time Slider', 'Start/End'], 
                        numberOfRadioButtons=3, 
                        select=1, 
                        cw = [1,columnWidth1st],
                        on1=pm.Callback( callback_timerangeSelect, 1), 
                        on2=pm.Callback( callback_timerangeSelect, 2),
                        on3=pm.Callback( callback_timerangeSelect, 3),
                        )
                        
                    pm.floatFieldGrp( 'timeRange_FFG', label='Start / End : ', value1=1, value2=24, numberOfFields=2, cw = [1,117], en=False)
            
            with pm.frameLayout( label='Rebuild Scene', mw=3, mh=3,cll=True, bs='etchedIn'):
                with pm.columnLayout(adj=True):
                    with pm.rowLayout(nc=2, adj=2):
                        pm.text(l='',w=columnWidth1st)
                        pm.button(l='New Scene', bgc=(0.24,0.49,0.24), c=pm.Callback(buildscene))
                    
            with pm.frameLayout( label='Import Alembic', mw=3, mh=3,cll=True, bs='etchedIn'):
                with pm.columnLayout(adj=True):
                    with pm.rowLayout(nc=3, adj=2):
                        pm.text(label='file :', w=columnWidth1st, align='right')
                        pm.textField('path_ABC2', text="D:/")
                        pm.symbolButton( image='navButtonBrowse.png', c=pm.Callback( browseIt, 'path_ABC2', 1, 'Alembic (*.abc)' ) )

                    with pm.rowLayout(nc=2, adj=2):
                        pm.text(l='',w=columnWidth1st)
                        pm.button(l='Import', bgc=(0.19,0.19,0.28), c=pm.Callback(importAbcFile))
                        
            with pm.frameLayout( label='Save Scene', mw=3, mh=3,cll=True, bs='etchedIn'):
                with pm.columnLayout(adj=True):
                    with pm.rowLayout(nc=3, adj=2):
                        pm.text(label='file :', w=columnWidth1st, align='right')
                        pm.textField('path_TFG2', text="D:/")
                        pm.symbolButton( image='navButtonBrowse.png', c=pm.Callback( browseIt, 'path_TFG2', 0 ) )
                    with pm.rowLayout(nc=2, adj=2):
                        pm.text(l='',w=columnWidth1st)
                        pm.button(l='Save Scene', w=64, bgc=(0.22,0.23,0.43), c=pm.Callback(saveScene))
            
