# coding=utf-8
__author__ = 'Kyuho Choi | coke25@aiw.co.kr | Alfred Imageworks'

import pymel.core as pm

def assignInitialShader():
    pm.sets( 'initialShadingGroup', e=True, forceElement=True )

def createCamSolidBG( camera=None ):
    '''
    카메라 백으로 사용할 솔리드한 Plane을 세움,
    카메라 이름을 명시하거나, 모델패털을 포커스한 상태에서 실행.

    Version : 2015-02-24
    
    >>> camSolidBG()
    (nt.Transform(u'persp_camSolidBG_grp'), nt.Transform(u'persp_camSolidBG_mesh'), nt.SurfaceShader(u'persp_camSolidBG_surfaceShader'), nt.ShadingEngine(u'persp_camSolidBG_SG'))
    
    >>> camSolidBG( camera='side' )
    (nt.Transform(u'side_camSolidBG_grp'), nt.Transform(u'side_camSolidBG_mesh'), nt.SurfaceShader(u'side_camSolidBG_surfaceShader'), nt.ShadingEngine(u'side_camSolidBG_SG'))
    '''
    if not camera:
        camera = pm.modelPanel( pm.playblast(activeEditor=True).split('|')[-1], q=True, camera=True )

    mesh = pm.polyPlane(sh=1, sw=1, ch=False)[0]
    grp  = pm.group()
    
    pm.parentConstraint(camera, grp)
    mesh.t.set(0,0,-500)
    mesh.r.set(90,0,0)
    mesh.s.set(150,150,150)
    
    shader, SG = pm.createSurfaceShader('surfaceShader')
    shader.outColor.set(0.5,0.5,0.5)
    pm.select(mesh)
    pm.hyperShade(assign=shader)
    
    mesh.castsShadows.set(False)
    mesh.receiveShadows.set(False)
    mesh.motionBlur.set(False)
    mesh.smoothShading.set(False)
    mesh.visibleInReflections.set(False)
    mesh.visibleInRefractions.set(False)
    
    grp.   rename('%s_camSolidBG_grp' % camera)
    mesh.  rename('%s_camSolidBG_mesh' % camera)
    shader.rename('%s_camSolidBG_surfaceShader' % camera)
    SG.    rename('%s_camSolidBG_SG' % camera)
    
    return grp, mesh, shader, SG

def saveAllRenderViewImages( saveTo=None, ext='PNG' ):
    '''
    렌더뷰에 임시저장된 이미지들을 따로 몽땅 저장

    saveAllRenderViewImages( 'D:/Users/Desktop/hello', ext='png')
    saveAllRenderViewImages( 'D:/Users/Desktop/hello.png' )
    '''
    # 렌더뷰 컨트롤 찾기
    renderViewPanels = pm.getPanel( scriptType='renderWindowPanel' )
    if not renderViewPanels:
        pm.error( u"Render View window를 열어주세요." )

    renderViewPanel = renderViewPanels[0]
    renderViewForm = pm.renderWindowEditor( renderViewPanel, q=True, parent=True )
    if not renderViewForm:
        pm.error( u"Render View window를 열어주세요." )

    scrollBarName = '|'.join( renderViewForm.split('|')[:-1] ) + '|scrollBarForm|scrollBar'

    # 어디다 저장할지?
    dirname = None
    basename = None
    padding = 4
    if not saveTo:
        ws      = pm.workspace( q=True, fullName=True )
        images  = pm.workspace( 'images', q=True, fileRuleEntry=True)
        dirname = ws + '/' + images
        basenameEx = '/renderViewCapture'
    else:
        # path = r'Z:\2013_MapleStory2\3D_project\Share\scenes\GameData\Alon.mb'
        dirname    = os.path.dirname( saveTo )
        basename   = os.path.basename( saveTo )
        basenameEx = None
        if '.' in basename:
            basenameEx = '.'.join( basename.split('.')[:-1] )
            ext        = basename.split('.')[-1]
        else:
            basenameEx = basename

        if not os.path.isdir( dirname ):
            pm.error( u'그런 이름의 디렉토리는 없네용' )

    # numPadding
    padding    = basenameEx.count('#')
    basenameEx = basenameEx.replace('#','')
    paddingStr = '%d'
    if padding > 1:
        paddingStr = '%0' + str(padding) +'d'        

    saveTo = dirname + '/' + basenameEx + paddingStr +'.'+ ext.lower()
    #print 'name : "%s"' % saveTo

    # 지금 보고있는 렌더뷰 이미지가 어디 있는지 찾아야해용.
    # 그래서 하나하나 뒤로 돌려봅네당..
    currentIndex = pm.intScrollBar( scrollBarName, q=True, value=True )

    # now step through all the saved images in the render view window, saving each one out
    #int $maxImageIndex = `intScrollBar -query -maxValue $scrollBarName`;
    maxImageIndex = pm.renderWindowEditor( 'renderView', q=True, nbImages=True )    
    imagesWritten = 0
    number = 0 # 파일명이 겹치지 않도록 하는 변수
    for i in range( maxImageIndex+1 ):
        if not maxImageIndex == 0:
            # 한장의 이미지만 있고, 스크롤바가 안생긴 상태가 아니면...
            pm.intScrollBar( scrollBarName, e=True, value=i-1 )

        # 저장될 파일명
        number += 1
        fileName = saveTo % number
        
        # 같은 파일명의 이름이 있으면 뒤에 번호를 더 붙임
        while os.path.exists(fileName):
            #print '"%s" is Exists' % fileName
            number += 1
            fileName = saveTo % number
        
        # 저장
        pm.mel.renderWindowScrollDisplayImage( 'renderView' )
        pm.mel.renderWindowSaveImageCallback( 'renderView', fileName, ext.upper() )
        
        # 내용 출력
        print '# save To : %s' % fileName.replace('/','\\')
        
        # 저장된 이미지 개수 증가
        imagesWritten += 1
    
    # reset the current render view back to what it was before stepping through them
    pm.intScrollBar( scrollBarName, e=True, value=currentIndex )
    pm.mel.renderWindowScrollDisplayImage( 'renderView' )

    if imagesWritten == 0:
        print u"# Error saving: render view 에 이미지가 없습니다.\n"
    else:
        print u"# Save complete: %d장의 render view 이미지가 저장 되었습네다.\n"%imagesWritten

def removeTurtle():
    # 터틀 노드 제거
    pm.unloadPlugin( 'Turtle.mll', f=True )
    turtleNodes = pm.ls('Turtle*')
    for node in turtleNodes:
        node.unlock()
        pm.delete( node )
        print u'"%s" 제거 성공' % node