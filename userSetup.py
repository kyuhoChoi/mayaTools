# -*- coding:utf-8  -*-

print '# -------------------------------------------'
print '# Alfred Shared Env / userSetup.py '
print '# -------------------------------------------'
print '# '

#
# 자주 사용되는 파이썬 기본모듈 로딩: os, sys 모듈 추가
#
import os, sys, subprocess, shutil
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as openMaya
import maya.utils as utils
import pymel.core as pm

print '#    import os, sys'
print '#    import maya.cmds as cmds'
print '#    import maya.mel as mel'
print '#    import maya.OpenMaya as openMaya'
print '#    import maya.utils as utils'
print '#    import pymel.core as pm'

#
# 네트워크 드라이브 연결
#
print '#    Connect Network Drive'
os.system( 'net use X: \\\\alfredstorage\\work_2014' )
os.system( 'net use Y: \\\\alfredstorage\\work_2015' )
os.system( 'net use Z: \\\\alfredstorage\\work_2013' )

#
# 커스텀 Python 경로 추가
#
customPythonPath = [
    '\\\\alfredstorage\\Alfred_asset\\Maya_Shared_Environment\\scripts_Python',
    '\\\\alfredstorage\\Alfred_asset\\Maya_Shared_Environment\\scripts_Python_old',
    ]
for p in customPythonPath:
    if p not in sys.path:
        try:
            sys.path.append( p )
            print u'#    sys.path.append( "%s" )' % p
        except:
            pass

#
# Alfred Tools Menu 추가
#
print '#    import alfredToolsMenu'
import alfredToolsMenu
utils.executeDeferred ('alfredToolsMenu.show()') # 마야가 실행 된 다음에 실행되도록 설정하는 부분


#
# Alfred Tools Menu 추가
#
print '#    import alfredToolsMenu2'
import alfredMenu
utils.executeDeferred ('alfredMenu.show()') # 마야가 실행 된 다음에 실행되도록 설정하는 부분


#
# 보너스 툴 메뉴 추가 : 
#
'''
try:
    utils.executeDeferred ('mel.eval( "bonusToolsMenu()" )') # 마야가 실행 된 다음에 실행되도록 설정하는 부분
    print '#    bonusToolsMenu() loaded'
except:
    pass
'''

#
# Maya.env 업데이트 : 
#
updateMayaEnv = True
if updateMayaEnv:
    import pymel.versions
    mayaVersion     = pymel.versions.installName()

    shareMayaAppDir = '//alfredstorage/Alfred_asset/Maya_Shared_Environment'    
    shareMayaAppVersionDir = '%s/%s' % (shareMayaAppDir, mayaVersion )

    userMayaAppDir  = pm.mel.getenv( 'MAYA_APP_DIR' )
    userMayaAppVersionDir  = '%s/%s' % (userMayaAppDir,  mayaVersion ) #userDocPath = subprocess.check_output( 'reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v "Personal"' ).split(' ')[-1].replace('\r','').replace('\n','').replace('\\','/')

    if os.path.isfile(shareMayaAppVersionDir+'/Maya.env'):                                             # 공용 Maya.env 파일이 존재하고,
        if os.path.isdir(userMayaAppVersionDir):                                                       # 로컬 마야 사용자 폴더가 존재하면.
            shutil.copyfile( shareMayaAppVersionDir+'/Maya.env', userMayaAppVersionDir+'/Maya.env' )   # 파일 복사
            print '#    Copy Shared Maya.env'                                                          # 처리결과 출력

#
# 종료 내용 출력
#
print '# '
print '# -------------------------------------------'
print '# Alfred Shared Env / userSetup.py Loaded !! '
print '# -------------------------------------------'
