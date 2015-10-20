# coding:utf-8
import os
import shutil
import maya.cmds as cmds

def analizeFilePath():
    _filePath = []
    _fileNode = cmds.ls(type='file')
    for _node in _fileNode:
        _filePath.append( cmds.getAttr (_node+'.fileTextureName') )
    
    for _path in _filePath:
        print _path
    
    return _filePath

def copyFiles(_files, _copyDir):
    _result = []

    _copyDir=_copyDir.replace('\\','/')    

    if not _copyDir[-1]=='/':
        _copyDir+='/'

    if not os.path.exists(_copyDir):            # 지정한 폴더가 없을때 폴더 생성
        os.makedirs(_copyDir)

    for _file in _files:
        _basename = os.path.basename(_file)
        _to = _copyDir+_basename
        _result.append( [shutil.copyfile( _file, _to ), _file, _to] )

    for _res in _result:
        print u'    복사 :'
        print  '    from :',_res[1]
        print  '      to :',_res[2]

# 파일 패스 다시 연결
def reconnectFileTexture():
    _filePath = cmds.file(q=1,sceneName=1)      # 열린 파일의 경로
    _dir = os.path.dirname(_filePath)           # 디렉토리
    _file = os.path.basename(_filePath)         # 파일
    _fileName = os.path.splitext(_file)[0]      # 파일이름
    _ext = os.path.splitext(_file)[1][1:]       # 확장자

    _relativePath = _dir+'/'+_fileName          # 병경될 디렉토리
    _fileNodes = cmds.ls(type='file')           # 현재 씬의 file node들

    for _node in _fileNodes:
        _currentPath = cmds.getAttr (_node+'.fileTextureName')
        _currentFile = os.path.basename(_currentPath)
        _newPath = _relativePath+'/'+_currentFile
        cmds.setAttr (_node+'.fileTextureName', _newPath, type='string')

def fileWorks():
    _filePath = cmds.file(q=1,sceneName=1)      # 열린 파일의 경로
    if not _filePath: 
        print u'경로가 존재하지 않음'
        return

    _dir = os.path.dirname(_filePath)           # 디렉토리
    _file = os.path.basename(_filePath)         # 파일
    _fileName = os.path.splitext(_file)[0]      # 파일이름
    _ext = os.path.splitext(_file)[1][1:]       # 확장자
    
    _copyDir = _dir+'/'+_fileName
    copyFiles(analizeFilePath(),_copyDir)
    reconnectFileTexture()