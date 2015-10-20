# coding=utf-8
'''
1. 동작 애니메이션 클립화. 레퍼런스로 불러도 타임라인 조정 가능함
2. 애니메이션 클립 내보냄.
'''

__author__ = 'alfred'
import pymel.core as pm
import math
import glob

# 모션캡쳐 조인트리스트
mocapJoints = [
    'Hips',
    'Spine',
    'Spine1',
    'Spine2',
    'Neck',
    'Head',

    'LeftShoulder',
    'LeftArm',
    'LeftForeArm',
    'LeftHand',
    'LeftFingerBase',

    'RightShoulder',
    'RightArm',
    'RightForeArm',
    'RightHand',
    'RightFingerBase',

    'LeftUpLeg',
    'LeftLeg',
    'LeftFoot',
    'LeftToeBase',

    'RightUpLeg',
    'RightLeg',
    'RightFoot',
    'RightToeBase',
    ]

# 모션캡쳐용 마야 파일 위치
maFile = '/'.join( __file__.split('\\')[:-1] ) + '/file/MC.ma'

def makeAsset( source_mcDir=None, export_mcDir=None, export_clipDir=None, source_namespace='' ):
    ''' 
    모션캡쳐 업체에서 받은 파일을 정리해줌 (동작 클립화)

    1. 타이밍을 조정 할 수 있도록 모션캡쳐 업체에서 받은 데이터를 클립화 시킴.
    2. MC.ma 파일을 업체에 보내야햠.
    3. Trax Editor에서 모션블렌드용 animclip도 따로 clip폴더로 내보냄.

    >>> convert( source_mcDir  = r'X:\2014_Nexon_Durango\3D_project\Share\scenes\MotionCapture\Recieved_Files', export_mcDir = r'X:\2014_Nexon_Durango\3D_project\Share\scenes\MotionCapture')
    
    '''
    #
    # 입력이 없을경우 기본값 설정
    #
    #if not source_mcDir: raise
    #if not export_mcDir: raise
    #if not export_clipDir: raise
    '''
    prjSet = pm.workspace(q=True, rd=True)
    
    workspace_clipsDir = None
    fileRules = pm.workspace(q = True, fileRule=True )
    fileRules = [ [fileRules[i*2], fileRules[i*2+1]] for i in range( int(len(fileRules)*.5 )) ]
    
    # 클립폴더 찾기
    find_clipsDir = None
    for rule, wsDir in fileRules:
        if rule=='clips':
            find_clipsDir = wsDir

    if not export_clipDir:
        export_clipDir = '%s%s' % ( prjSet, find_clipsDir)
    '''
   

    fileList = glob.glob( source_mcDir + "/*.mb")
    fileList.extend( glob.glob( source_mcDir + "/*.ma") )
    fileList.extend( glob.glob( source_mcDir + "/*.fbx") )

    print fileList
    
    # 폴더에있는 파일들 처리
    for i, mcFile in enumerate(fileList):
        # 이름
        sceneName = pm.mel.basenameEx( mcFile )

        # 새파일
        pm.newFile( force=True )

        # 모션캡쳐 캐릭터 파일 임포트
        #maFile = __file__.split('\\')[:-1] + '\\file\\MC.ma'
        pm.importFile( maFile )
        charSet = pm.PyNode('set') # 모캡 파일안에 있는 캐릭터 셋

        # 레퍼런스로 모션 부름
        refNode = pm.createReference( mcFile, namespace='mcData')

        # 모션캡쳐 조인트에서 자료 복사
        errorLine = []
        for jnt in mocapJoints:            
            #f = 'mcData:*%s'%jnt
            f = 'mcData:%s%s'%( source_namespace+':' if source_namespace else '', jnt)
            t = jnt

            print '%s --> %s'%(f, t)

            if jnt=='Hips':
                attrs = ['tx','ty','tz','rx','ry','rz']
            else:
                attrs = ['rx','ry','rz']

            for attr in attrs:                
                try:
                    pm.copyKey( f+'.'+attr )
                    pm.pasteKey( t+'.'+attr, option='merge' )

                except:
                    errorLine.append( u'#    %s.%s >> %s.%s' % (f, attr, t, attr ) )

                    # 그냥 값을 입력받아서 적어넣음.
                    pm.Attribute( t+'.'+attr ).set( pm.Attribute( f+'.'+attr ).get() )

        if errorLine:
            print u'# '
            print u'# "%s"'%mcFile
            print u'# '

            print '\n'.join(errorLine)

            print u'# '
            print u'# 어트리뷰트 key 복사, 붙이기 과정에서 에러가 발생했습니당. 아래내용을 확인해주세요.'                    
            print u'#    1. 모션캡쳐파일에 animation Layer가 사용된경우 --> animation Layer를 merge시키세요.'
            print u'#    2. 위 attribute에 key가 존재하지않을경우 --> 처리된 파일엔 문제가 없을수도 있습니다. 이 에러가 마음에 걸리면, 위 어트리뷰트에 임의의 키를 주세요.'
            print u'#    3. 해당 노드가 삭제된 경우 --> 모션캡쳐 업체에 다시 문의하세요.'
            print u'# '

        # 레퍼런스 날림
        refNode.remove()

        # 타임라인 조정
        animNodes = pm.keyframe('Hips', q=True, name=True )
        times = pm.keyframe('Hips',at='rx',q=True, tc=True)
        pm.playbackOptions(
            min= math.floor(times[ 0]),
            max= math.ceil (times[-1])
            )

        # 애니메이션 클립 생성
        animClip = pm.clip(charSet, name='animClip', scheduleClip=True, allAbsolute=True, animCurveRange=True)[0]
        animClip = pm.PyNode( animClip )
        animClip.rename( pm.mel.formValidObjectName( sceneName ) )

        # 애니메이션 클립 내보냄 
        # 프로젝트의 clip폴더로 내보냄.
        # projectDir = pm.workspace( q=True, rd=True)
        # clipDir    = projectDir+'clips/'
        # exportPath = clipDir + sceneName
        exportPath = '%s\\%s.mb'%( export_clipDir, sceneName)

        pm.select(animClip)
        pm.mel.source( "doExportClipArgList.mel" )
        pm.mel.clipEditorExportClip( exportPath, "ma")

        # 파일저장
        print export_mcDir
        pm.saveAs( '%s\\%s.mb'%( export_mcDir, sceneName) )

        # 결과 출력
        print '#---------------------------------------------'
        print '#'
        print '# %d%% convert! (%03d/%03d) "%s"'%( math.floor( float(i+1)/len(fileList)*100 ), i+1,len(fileList),sceneName)
        print '#'
        print '#---------------------------------------------'