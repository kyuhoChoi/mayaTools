# -*- coding:utf-8 -*-
import os, pickle, glob
import stat, locale, time
import fnmatch 
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pyMel

import HIK_Tools

class dirTree():
    _debug = False
    _scriptPath  = os.path.dirname(__file__)
    _iconPath = _scriptPath+'/icons/'

    def __init__(self, _instance, *args, **kwargs):
        self.debugMsg( '__init__() : Call' )
        # --------------------------------------------
        #
        #     instance
        # 
        self.setInstance(_instance)

        # --------------------------------------------
        #
        #     UI
        #
        self._window = self.getInstance()+'_dirTree'
        self._UI_LAY_parentLayout = '_dirTree_parentLayout'
        self._UI_LAY_reloadLayout = '_dirTree_Layout'

        # --------------------------------------------
        #
        #     ignore
        #
        if kwargs.get('ignore') or kwargs.get('ign'):
            _input = ''

            # 해당 키워드에 해당하는 키값을 받아오고
            if   kwargs.get('ignore'): 
                _input = kwargs.get('ignore')
            elif kwargs.get('ign'): 
                _input = kwargs.get('ign')
    
            # 맞으면.. 아래 실행
            self._ignore = _input
        else:
            self._ignore = ['icons', '.mayaSwatches', 'incrementalSave']
        
        # --------------------------------------------
        #
        #     rootPath
        # 
        if kwargs.get('rootPath') or kwargs.get('rp'):
            _input = ''

            # 해당 키워드에 해당하는 키값을 받아오고
            if   kwargs.get('rootPath'): _input = kwargs.get('rootPath')
            elif kwargs.get('rp'):       _input = kwargs.get('rp')
     
            # 맞으면.. 아래 실행
            self.setRootPath(_input)
        else:
            self.setRootPath(self._data[0]['path'])
        
        # --------------------------------------------
        #
        #     startPath
        # 
        if kwargs.get('startPath') or kwargs.get('sp'):
            _input = ''

            # 해당 키워드에 해당하는 키값을 받아오고
            if   kwargs.get('startPath'): _input = kwargs.get('startPath')
            elif kwargs.get('sp'):        _input = kwargs.get('sp')
     
            # 맞으면.. 아래 실행
            self.setStartPath(_input)
        else:
            self.setStartPath(self._data[0]['path'])
        
        # --------------------------------------------
        #
        #     data
        # 
        if not self.loadCache():
            self.setDirData()

        # --------------------------------------------
        #
        #     command
        # 
        if kwargs.get('command') or kwargs.get('c'):
            _input = ''

            # 해당 키워드에 해당하는 키값을 받아오고
            if   kwargs.get('command'): _input = kwargs.get('command')
            elif kwargs.get('c'):       _input = kwargs.get('c')
                
            # 맞으면.. 아래 실행
            self.setCommand( _input )
        else:
            self.setCommand( 'print' )

    # cache
    def saveCache(self, *args):
        self.debugMsg( 'saveCache() : Call' )

        _cacheFile = str(self.getRootPath()+'/dirCache.dat')
        
        # 미리존재하는 파일 삭제
        if os.access( _cacheFile, os.F_OK):
            os.remove(_cacheFile)
             
        _f = open(_cacheFile, 'w') # 쓰기모드(쓸땐 괜찮은데, 다시 쓰려고 하면 에러남)

        #_f = open(_cacheFile, 'a')  # 읽고 쓰기모드 (이렇게 하니까 괜찮음)
        pickle.dump( self._data, _f)
        _f.close()

        # 캐시파일 숨김
        _melCmd = 'system "attrib +h %s"'%_cacheFile
        mel.eval(_melCmd)

        # 잘썼어.
        self.debugMsg( 'saveCache() : True | "%s"'%_cacheFile)
        return True

    def loadCache(self, *args):
        _cacheFile = self.getRootPath()+'/dirCache.dat'
        
        # 파일이 없으면 실패!
        if not os.access(_cacheFile, os.F_OK):
            self.debugMsg( 'loadCache() : False "%s"'%_cacheFile )
            return False
            
        _f = open(_cacheFile, 'r')
        _data = pickle.load(_f)
        _f.close()

        # 읽어온 데이터를 쎗!
        self._data = _data

        # 잘읽었어
        self.debugMsg( 'loadCache() : True "%s"'%_cacheFile )
        return True
    
    # instance
    def setInstance(self, *args):
        self._instance = args[0]
    
    def getInstance(self):
        return self._instance
    
    # callback
    def callback_selectDir(self, *args):
        _startPath = args[0]
        exec ( self._command +'(\'%s\')'%_startPath)
    
    # command
    def setCommand(self, *args):
        self._command = args[0]
    
    def getCommand(self):
        return self._command
    
    # data
    def setDirData(self, *args):
        self.debugMsg( 'setDirData() : Call' )

        def getDirTree(_path):
            # 없는 경로면 종료
            if not os.path.exists(_path):
                print u'경로가 없음 : 프로젝트 셋을 설정했는지 확인하세요.', _path
                return []

            # 작업 디렉토리 설정
            os.chdir(_path)
            
            _dirList  = []
            _ign = self._ignore
            
            for _item in os.listdir(_path):
                if   os.path.isdir (_item):
                    _dirList.append( _item )
                elif not _item in _ign:
                    _ign.append( os.path.splitext(_item)[0] ) 

            # 필터링
            _dirList = list( set(_dirList)-set(_ign) )
            _dirList.sort()    
            _dirPathList  = [ _path+'/'+_myPath for _myPath in _dirList]         
            if not _dirPathList:
                return []

            _return = []
            for _path in _dirPathList:
                _return.append( _path )
                _return += [ a for a in getDirTree(_path)]
            return _return

        _dirList = getDirTree(self._rootPath)
        _dirListNum = len(_dirList)
        _rootPath_depth = len( self._rootPath.split('/') )

        _data=[]
        for _i,_path in zip( range(_dirListNum), _dirList ):
            _label  = os.path.basename(_path)
            _pathDepth = len(_path.split('/'))

            _nextPath_depth = 0
            
            # 다음 path가 있는지 확인하고...
            if _i<_dirListNum-1:
                _nextPath_depth = len( _dirList[_i+1].split('/') )

            # 다음 path의 깊이값이 더 크면 자식을 가지고 있는듯 함.
            _hasChild = _pathDepth<_nextPath_depth

            # 깊이 = _path깊이 - self._rootPath 깊이 -1
            _depth  = _pathDepth - _rootPath_depth -1

            # 프리뷰용 라벨
            #_tmp = 
            _tmp = ''
            if _depth:
                _tmp += (' '*_depth*4)+ '+ '
            _tmp += _label
            _depthLabel = _tmp.rjust(_depth*4)
            
            _data.append( {'label':_label, 'depth':_depth, 'path':_path, 'depthLabel':_depthLabel, 'hasChild':_hasChild} )
        
        self._data = _data

        # 캐쉬 저장
        self.saveCache()

    def getDirData(self):
        self.debugMsg( 'getDirData() : Call' )
        return self._data

    def printDirData(self, *args):
        self.debugMsg( 'printDirData() : Call' )

        _dirData = self.getDirData()

        _depthLabel_max = 0
        _label_max = 0
        for _data in _dirData:
            # 글씨 크기 확인
            if _depthLabel_max < len(_data['depthLabel']): _depthLabel_max = len(_data['depthLabel'])
            if      _label_max < len(_data['label']):           _label_max = len(_data['label'])

        _depthLabel_max+=3
        
        print '--depthLabel--'.center(_depthLabel_max),'--label--'.center(_label_max), '--depth--'.center(9), '--hasChild--'.center(12), '----path----'
        for _data in _dirData:
            print _data['depthLabel'].ljust(_depthLabel_max), \
                  _data['label'].center(_label_max), \
              str(_data['depth']).center(9), \
              str(_data['hasChild']).center(12), \
                  _data['path']
 
    def debugMsg(self,_msg):
        if not self._debug:
            return
        print __name__,'.dirTree().',_msg
    
    # path
    def setPath(self, _rootPath, _startPath):
        self.debugMsg( 'setPath() : in' )

        self.setRootPath(_rootPath)
        self.setStartPath(_startPath)

        # 캐쉬를 읽어 들이고 혹시 실패하면 캐쉬 생성
        if not self.loadCache():
            self.setDirData()

        self.updateUI()

    def setStartPath(self,*args):
        if not os.path.exists(args[0]):
            print u'dirTree().setStartPath() 경로가 없음 :', args[0]
            return
        self._startPath = args[0]
    
    def getStartPath(self):
        self._startPath

    def setRootPath(self,*args):
        if not os.path.exists(args[0]):
            print u'dirTree().setRootPath() 경로가 없음 :', args[0]
            return
        self._rootPath = args[0]

    def getRootPath(self):
        return self._rootPath

    # 익스플로러 폴더 오픈
    def openExplorer(self, *args):
        _path = os.path.normcase(args[0])        
        _mode = args[1]

        if _mode=='root' or _mode=='select':
            _mel = 'system ("explorer %s, %s");'%(_mode, _path.replace('\\','\\\\'))
            #print _mel
            mel.eval( _mel )
            return
        else:
            print u'입력 형식이 맞지 않습니다.'

    def setDebug(self,*args):
        self._debug = not self._debug
        if self._debug:
            print '------------------------ dirTree() : Start Debug ---------------------------'
        else:
            print '------------------------ dirTree() : End Debug -----------------------------'
    
    # updateUI
    def updateUI(self, *args):
        self.debugMsg( 'updateUI() : in' )
        self.Module()
    
    #------------------------------------------------------------------
    #
    # 윈도우 관련
    #
    #------------------------------------------------------------------    
    # 윈도우 모듈
    def Module(self):
        self.debugMsg( 'Module() : ---------------------------------' )
        #------------------------------------------
        #
        #        self._startPath 분석
        #
        _startPath_Parent = [self._startPath]
        for _i in range( 1, len(self._startPath.split('/')) ):
            _dir = os.path.dirname( _startPath_Parent[_i-1] )
            _startPath_Parent.append( _dir )

            # self._startPath = '//alfredstorage/Alfred_asset/Assets/MotionCapture/Hik_5thAve' 일경우 
            #
            # _startPath_Parent[0] = '//alfredstorage/Alfred_asset/Assets/MotionCapture/Hik_5thAve'
            # _startPath_Parent[1] = '//alfredstorage/Alfred_asset/Assets/MotionCapture'
            # _startPath_Parent[2] = '//alfredstorage/Alfred_asset/Assets'
            # _startPath_Parent[3] = '//alfredstorage/Alfred_asset'
            # _startPath_Parent[4] = '//alfredstorage'
            # _startPath_Parent[5] = '//'
            # _startPath_Parent[6] = '//'

        #------------------------------------------
        #
        #        UI
        #
        
        # 윈도우 갱신
        if not cmds.formLayout(self._UI_LAY_parentLayout, q=True, exists=True):
            self._UI_LAY_parentLayout = cmds.formLayout(self._UI_LAY_parentLayout)

        if cmds.scrollLayout(self._UI_LAY_reloadLayout, q=True, exists=True):
            self._UI_LAY_parentLayout = cmds.scrollLayout(self._UI_LAY_reloadLayout, q=True, parent=True)
            cmds.deleteUI(self._UI_LAY_reloadLayout)

        # 재 제작
        self._UI_LAY_reloadLayout = cmds.scrollLayout(cr=True, p=self._UI_LAY_parentLayout)

        # 빈곳 팝업메뉴
        cmds.popupMenu( button=3 )
        cmds.menuItem( l='Update Folder Tree Chache', c=self.setDirData)
        cmds.menuItem( l='print Folder Tree Data', c=self.printDirData)
        cmds.menuItem( l='Open Explore', c=pyMel.Callback( self.openExplorer, self._rootPath, 'root' ) )
        cmds.menuItem( l='toggle Debug', c=self.setDebug )

        cmds.columnLayout(adj=True)
        cmds.iconTextRadioCollection()

        # 독립적으로 움직이려면 겹치지 않을 이름이 필요함.
        # 현재 instance 이름을 prefix로 사용해서 해결 해봄.
        _unique = self._instance
        _currentDepth = 0

        _icon_Hierachy_Collapse  = self._iconPath+'Hierachy_Collapse.png'
        _icon_Hierachy_Expand    = self._iconPath+'Hierachy_Expand.png'
        _icon_Hierachy_None      = self._iconPath+'Hierachy_noChild.png'

        _iconTextRadioButton_sel = ''

        # 디렉토리 데이터 얻어옴
        _dirData = self.getDirData()

        _dataCount = len(_dirData)
        for _i, _data in enumerate( _dirData ):           
            #------------------------------------------
            #
            #        self._data 데이터 파악
            #
            # UI요소들 독립적인 이름 생성 (충돌 피하기위함)
            _depthColLayout = '%s_depthColumn%s'  %(_unique,_i)
            _symbolBtn =      '%s_symbolButton%s' %(_unique,_i)

            # 데이터 분석
            _path =         _data['path']
            _label =        _data['label']
            _depth =        _data['depth']
            _hasChild =     _data['hasChild']

            # 선택한 패쓰경로에 속한 패쓰인지 파악
            _hasStartPath = _path in _startPath_Parent
            
            #------------------------------------------
            #
            #        setParent (ColumnLayout 탈출)
            #
            if _depth < _currentDepth:
                for _tmp in range(_currentDepth - _depth):
                    cmds.setParent('..') # _depthColLayout 나감

            #------------------------------------------
            #
            #        버튼 배치
            #
            cmds.rowLayout( numberOfColumns=_depth+2, adjustableColumn=_depth+2)
            
            #------------------------------------------
            #
            #        + - symbolButton 버튼 설정 : 하위 구조가 존재하면..
            #
            #if cmds.symbolButton(_symbolBtn, q=1, exists=1): deleteUI(_symbolBtn)
            if _hasChild:
                _cmd  = 'import maya.cmds as cmds\n'
                _cmd += '_toggle = cmds.columnLayout(\'%s\', q=True, vis=True)\n'%_depthColLayout
                _cmd += '_toggle = (_toggle+1)%%2\n'
                _cmd += 'cmds.columnLayout(\'%s\', e=True, vis=_toggle)\n'%_depthColLayout
                _cmd += 'if _toggle: cmds.symbolButton(\'%s\', e=True, image=\'%s\')\n'%(_symbolBtn, _icon_Hierachy_Collapse)
                _cmd += 'else :      cmds.symbolButton(\'%s\', e=True, image=\'%s\')\n'%(_symbolBtn, _icon_Hierachy_Expand)

                _icon = ''
                if _hasStartPath: _icon=_icon_Hierachy_Collapse
                else :            _icon=_icon_Hierachy_Expand
                cmds.symbolButton(_symbolBtn, image=_icon, c=_cmd)
            else:
                cmds.symbolButton(_symbolBtn, image=_icon_Hierachy_None)
            
            #------------------------------------------
            #
            #        depth 들여쓰기
            #
            for _tmp in range(_depth):
                cmds.text(label="    ")

            #------------------------------------------
            #
            #        iconTextRadioButton
            #
            self.debugMsg( 'Module() : iconTextRadioButton: %s'%_path )
            _iconTextRadioButton = cmds.iconTextRadioButton(
                                                            label = _label,
                                                            font = 'plainLabelFont',
                                                            style = 'iconAndTextHorizontal',
                                                            image1= self._iconPath+'folder_Close.png',
                                                            selectionImage= self._iconPath+'folder_Close.png',
                                                            onCommand= pyMel.Callback( self.callback_selectDir , _path )
                                                            )
            cmds.popupMenu( button=3 )
            cmds.menuItem( l='Open Explore', c=pyMel.Callback( self.openExplorer, _path, 'root' ) )

            #------------------------------------------
            #
            #        시작시 선택할 버튼 지정
            #
            self.debugMsg( 'Module() :     self._startPath: %s'%self._startPath )
            if _path==self._startPath:
                self.debugMsg( 'Module() :     -----------------------------Match!!-------------------------------------- ')
                _iconTextRadioButton_sel = _iconTextRadioButton

            #------------------------------------------
            #
            #        rowLayout 나감
            #
            cmds.setParent('..') # rowLayout

            #------------------------------------------
            #
            #        columnLayout (하위 구조 감싸는 용도)
            #
            if _hasChild:
                cmds.columnLayout(_depthColLayout, adj=True, vis=_hasStartPath)

            #------------------------------------------
            #
            #        Hieracy 구조 마무리
            #
            if _i==_dataCount-1 and _depth!=0:
                while( _depth>1 ):
                    _depth -= 1
                    cmds.setParent('..')

            # 현재 path의 depth를 임시저장시킴.
            _currentDepth = _depth

        cmds.setParent('..') # iconTextRadioCollection
        cmds.setParent('..') # columnLayout
        cmds.setParent('..') # scrollLayout

        #------------------------------------------
        #
        #        startPath 해당 관련버튼 Select
        #
        if not _iconTextRadioButton_sel: # 해당 디렉토리가 없을 경우 캐쉬에 문제가 있을 가능성 많음, 캐쉬 데이터를 다시생성
            self.setDirData()
        cmds.iconTextRadioButton(_iconTextRadioButton_sel, e=True, select=True)

        cmds.formLayout(
            self._UI_LAY_parentLayout,
            edit=True,
            attachForm=[
                    (self._UI_LAY_reloadLayout, 'top', 0),
                    (self._UI_LAY_reloadLayout, 'left', 0),
                    (self._UI_LAY_reloadLayout, 'right', 0),
                    (self._UI_LAY_reloadLayout, 'bottom', 0)
                    ]
                    )
    
    # 독립 윈도우
    def Window(self):
        if cmds.window(self._window, q=1, exists=1): cmds.deleteUI(self._window)

        cmds.window(self._window)
        self.Module()
        cmds.showWindow(self._window)

class glidLister():
    _currentFile = ''
    _extension = ['mb','ma','fbx']
    _iconRenderRes = 512

    _scriptPath = os.path.dirname(__file__)
    _iconPath = _scriptPath+'/icons/'
    _icon_setNamespace = _iconPath+'setNamespace_1.png'

    _UI_LAY_gridParent = ''
    _UI_GRD_gridLayout = ''

    _initValue = None
    _namespace = ''

    _command = {
        'lmb':'print "%s"',
        'alt':'print "%s"'
        }

    def __init__(self, _instance, *args, **kwargs):
        self._instance  = _instance
        self._cmdPrefix = __name__+'.'+_instance+'.'
        self._window    = __name__+_instance+'_glidLister'
        self._dock      = __name__+_instance+'_glidLister_doc'
        self._iconSize  = 128
        self._iconRenderRes = 512
        self._UI_TFG_namespace = ''
        self._UI_ISG_iconSlider = ''

        # 입력 키워드 분석
        _key = [_key for _key in kwargs.keys()]
        
        # path 입력 분석
        if kwargs.get('path') or kwargs.get('p'):
            _input = ''

            # 해당 키워드에 해당하는 키값을 받아오고
            if   kwargs.get('path'): _input = kwargs.get('path')
            elif kwargs.get('p'):    _input = kwargs.get('p')

            self._path=_input
        else:
            self._path='c:/'
       
        # 레퍼런스용 namespace 분석
        if kwargs.get('namespace') or kwargs.get('ns'):
            _input = ''

            # 해당 키워드에 해당하는 키값을 받아오고
            if   kwargs.get('namespace'): 
                _input = kwargs.get('namespace')
            elif kwargs.get('ns'): 
                _input = kwargs.get('ns')
    
            # 맞으면.. 아래 실행
            self._namespace = _input
        else:
            self._namespace = 'Reference'
        
        #--------------------------------------------
        #
        #     command
        # 
        if kwargs.get('command') or kwargs.get('c'):
            _input = ''

            # 해당 키워드에 해당하는 키값을 받아오고
            if   kwargs.get('command'): _input = kwargs.get('command')
            elif kwargs.get('c'):       _input = kwargs.get('c')
                
            self.setCommand( _input )
        else:
            self.setCommand( 'print' )
        
        self.setFileList()
       
    #------------------------------------------------------------------
    #
    # path
    #
    #------------------------------------------------------------------
    # Path
    def setPath(self, *args):
        self._path = '%s'%args[0]

        self.setFileList()
        self.setCurrentFile('')
        self.updateUI()
        self.updateGrid()

    def getPath(self):
        return self._path
    
    def setPath_fromBrower(self, *args):
        _startPath = self.getPath()

        _result = cmds.fileDialog2(
                    fileFilter='All Files (*.*)',
                    fileMode=2,
                    dialogStyle=1,
                    startingDirectory=_startPath,
                    caption='Select Folder',
                    okCaption = 'Select',
                    cancelCaption = 'Cancel'
                    )

        if not _result:
            return

        _startPath = _result[0].replace('\\','/')        
        self.setPath( _startPath )

        return _startPath

    # Current File
    def setCurrentFile(self, *args):
        if not args[0]:
            self._currentFile = ''
            return

        _dir = os.path.dirname(args[0]) # 디렉토리명

        if _dir != self._path:
            self.setPath(_dir)

        self._currentFile = args[0].replace('\\','/')
    
    def getCurrentFile(self, *args):
        return self._currentFile

    # File List
    def setFileList(self, *args):
        self._fileList = [ _file.replace('\\','/') for _file in glob.glob( self.getPath()+'/*.*')]
        self._fileNameList = [ os.path.basename(_file) for _file in self._fileList]

    def getFileList(self, *args):
        return self._fileList
    
    def getFileNameList(self, *args):
        return self._fileNameList

    # File Info
    def getDirInfo(self, _path, _sort, _reverse, _print):
        # getDirData('D:/Users/Desktop',['ext'], False, True)

        _path=_path.replace('\\','/')    

        _result = []
        _listDir = os.listdir(_path)

        for _item in _listDir:
            _filePath = _path+'/'+_item
            _file = os.path.basename(_item)
            _ext = os.path.splitext(_item)[1][1:]
            _type = ''

            # 종류표시
            if   os.path.isfile(_filePath):
                _type = 'file'
            elif os.path.isdir(_filePath):
                _type = 'dir'
            elif os.path.islink(_filePath):
                _type = 'link'
            elif os.path.ismount(_filePath):
                _type = 'mount'

            # 크기     
            _size = os.stat(_filePath)[stat.ST_SIZE]
            _subfix = 'byte'
            _fsize = 1.0
            
            if _size>1024:
                _fsize = _size/1024.0
                _subfix = 'Kb  '

            if _size>1048576:
                _fsize = _size/1048576.0
                _subfix = 'Mb  '

            if _size>1.0737e+9:
                _fsize = _size/1.0737e+9
                _subfix = 'Gb  '

            _fileSize = locale.format('%.1f ', _fsize, True) + _subfix

            # 생성시간        
            _ctime = time.localtime(os.path.getctime(_filePath))
            _ctime = '%04d %02d.%02d %02d:%02d'%(_ctime[0],_ctime[1],_ctime[2],_ctime[3],_ctime[4])

            # 최근 수정시간
            _mtime = time.localtime(os.path.getmtime(_filePath))
            _mtime = '%04d %02d.%02d %02d:%02d'%(_mtime[0],_mtime[1],_mtime[2],_mtime[3],_mtime[4])

            # 결과 저장
            _result.append( {'type':_type, 'ext':_ext, 'size':_size, 'fsize':_fileSize, 'ctime':_ctime, 'mtime':_mtime, 'name':_file } )
        
        # 사전형 정렬
        if _sort:
            for _key in _sort:
                _result = [_val for (_key,_val) in sorted([(_dicItem[ _key ],_dicItem) for _dicItem in _result])]
                if _reverse:
                    _result.reverse()

        # 내용 출력
        if _print:
            print "Directory =", _path
            for _item in _result:
                _mtime = _item['mtime']
                if _item['ctime'] == _mtime:
                    _mtime = ''

                print _item['name'].ljust(30)[:30], _item['type'].rjust(5), _item['ext'].ljust(5), _item['fsize'].rjust(12), _item['ctime'].center(20), _mtime.center(20)

        return _result
    
    def getFileInfo( self, _filePath ):
        _result=[]
        _file = os.path.basename(_filePath)
        _ext  = os.path.splitext(_filePath)[1][1:]
        _type = ''

        # 종류표시
        if   os.path.isfile(_filePath):
            _type = 'file'
        elif os.path.isdir(_filePath):
            _type = 'dir'
        elif os.path.islink(_filePath):
            _type = 'link'
        elif os.path.ismount(_filePath):
            _type = 'mount'

        # 크기     
        _size = os.stat(_filePath)[stat.ST_SIZE]
        _subfix = 'byte'
        _fsize = 1.0
        
        if _size>1024:
            _fsize = _size/1024.0
            _subfix = 'Kb  '

        if _size>1048576:
            _fsize = _size/1048576.0
            _subfix = 'Mb  '

        if _size>1.0737e+9:
            _fsize = _size/1.0737e+9
            _subfix = 'Gb  '

        _fileSize = locale.format('%.1f ', _fsize, True) + _subfix

        # 생성시간        
        _ctime = time.localtime(os.path.getctime(_filePath))
        _ctime = '%04d %02d.%02d %02d:%02d'%(_ctime[0],_ctime[1],_ctime[2],_ctime[3],_ctime[4])

        # 최근 수정시간
        _mtime = time.localtime(os.path.getmtime(_filePath))
        _mtime = '%04d %02d.%02d %02d:%02d'%(_mtime[0],_mtime[1],_mtime[2],_mtime[3],_mtime[4])

        # 결과 저장
        _result= {'type':_type, 'ext':_ext, 'size':_size, 'fsize':_fileSize, 'ctime':_ctime, 'mtime':_mtime, 'name':_file }
        
        return _result
    
    #------------------------------------------------------------------
    #
    # namespace
    #
    #------------------------------------------------------------------
    def setNamespace(self, *args):
        self._namespace = args[0]
        self.updateUI()
    
    def getNamespace(self):
        return self._namespace
    
    def setNamespace_fromBtn(self, *args):
        _UI_TFG_namespace = self._UI_TFG_namespace.split('|')[-1]
        _namespace = cmds.textFieldGrp( _UI_TFG_namespace,  q=True, text=True)
        self.setNamespace( _namespace )

    #------------------------------------------------------------------
    #
    # command
    #
    #------------------------------------------------------------------
    # callback
    def callback_selectFile(self, *args):
        exec ( self._command +'(\'%s\')'%args[0])
    
    def setCommand(self, *args):
        self._command= args[0]
    
    def getCommand(self):
        return self._command
    
    def excute(self, *args):
        _mod = cmds.getModifiers()
        _file = args[0]

        self.setCurrentFile(_file)

        if   _mod==13:    # Control + Shift + Alt
            print 'Control + Shift + Alt', _file
        elif _mod== 5:    # Control + Shift
            # print 'Control + Shift', _file
            self.Open( _file )
        elif _mod==12:    # Control + Alt
            print 'Control + Alt', _file
        elif _mod== 9:    # Alt + Shift
            print 'Alt + Shift', _file
        elif _mod==16:    # Command(Window)
            print 'Command(Window)', _file
        elif _mod== 4:    # Control
            print 'Control', _file
        elif _mod== 1:    # Shift
            print 'Shift', _file
        elif _mod== 8:    # Alt
            print 'alt', _file
        else:             # LMB
            #self.Reference(_file)
            exec ( self._command +'(\'%s\')'%_file)

    #------------------------------------------------------------------
    #
    # updateUI
    #
    #------------------------------------------------------------------
    def updateGrid(self, *args):
        self.UI_Grid()
    
    def updateUI(self, *args):
        _pathTextfield = self._pathTFG.split('|')[-1]
        _UI_GRD_gridLayout = self._UI_GRD_gridLayout

        # Top
        cmds.textFieldGrp( _pathTextfield, edit=True, text=self._path)

        # 인터페이스 조정
        cmds.gridLayout(   _UI_GRD_gridLayout, edit=True, cellWidthHeight=[self._iconSize,self._iconSize] )

        if cmds.textFieldGrp( self._UI_TFG_namespace,  q=True, exists=True ):
            cmds.textFieldGrp( self._UI_TFG_namespace,  edit=True, text=self._namespace)
        
        if cmds.intSliderGrp( self._UI_ISG_iconSlider,  q=True, exists=True ):
            cmds.intSliderGrp( self._UI_ISG_iconSlider,  edit=True, value=self._iconSize )
    
    #------------------------------------------------------------------
    #
    # 파일 관련
    #
    #------------------------------------------------------------------
    def Open(self, *args):
        if not args:
            return

        if not os.access(args[0], os.F_OK):
            return 'no Path'

        _ext = args[0][-3:]
        if   _ext=='.ma':
            _type='mayaAscii'
        elif _ext=='.mb':
            _type='mayaBinary'
        elif _ext=='mel':
            _type='mel'
        else:
            _type=''
        
        _file = args[0]

        cmds.file( _file, open=True, force=True, options='v=0', ignoreVersion=True, type=_type )
        mel.eval( 'addRecentFile(\"%s\",\"%s\")'%(_file, _type) )

    def Reference(self, *args):
        _file = self.getCurrentFile()
        if args:
            _file = args[0]

        
        _referenceNode = ''
        _namespaceObj = cmds.ls( self.getNamespace()+":*" )

        if _namespaceObj and cmds.referenceQuery( _namespaceObj[0], isNodeReferenced=True ):
            _referenceNode = cmds.referenceQuery( _namespaceObj[0], referenceNode=True)
            # 현제 레퍼런스 파일 갱샌
            cmds.file( _file , loadReference=_referenceNode, options= 'v=0;')

        else:
            # 레퍼런스 파일 새로 생성
            cmds.file( 
                    _file,
                    reference=True,
                    namespace= self.getNamespace(),
                    loadReferenceDepth='all', 
                    sharedNodes='shadingNetworks',
                    ignoreVersion=True,
                    mergeNamespacesOnClash=False,
                    options= 'v=0;'
                    )

        self.setCurrentFile(_file)

    #------------------------------------------------------------------
    #
    # 아이콘 관련
    #
    #------------------------------------------------------------------
    # 아이콘 만듦
    def renderIcon_setting(self, *args):
        _mod = cmds.getModifiers();
        _presetFile = 'renderIcons02.mb'

        # 씬 안에 'renderIconsFile' 이라는 노드가 존재하면 여기서 종료 (버튼을 한번 더 누른거 같으므로 UI만 갱신)
        if _mod!=4 and cmds.ls('*makeIcon_renderFile*'):
            #self.UI_renderIcons()
            self.renderIcons()
            return True

        # 작업중인 데이터가 있으면, 사용자에게 컨펌 받음.
        _result = cmds.confirmDialog( 
            title=u'아이콘 렌더링 화면을 준비합니다', 
            message=u'주의 : 작업중인 데이터가 쑝 날아갑니다.  그래도, 계속 할거에요?', 
            button=['Yes','No'], 
            defaultButton='Yes', 
            cancelButton='No', 
            dismissString='No' 
            )

        # 아니면 중단.
        if _result != "Yes":
            return False

        # 렌더 프리셋 파일 경로
        _renderIconsFile = self._scriptPath + '/Files/renderIcons/' + _presetFile;
        
        # Ctrl키를 누르고 실행했으면 프리셋 파일을 Open : 프리셋 파일을 수정용
        if _mod==4:
            self.Open(_renderIconsFile)
            return False

        # 플러그인 로드 되어있는지 확인
        _plugIn = 'Mayatomr'
        if not cmds.pluginInfo(_plugIn, q=1, loaded=True):
            cmds.loadPlugin(_plugIn)
        
        # 새 파일을 만들고
        cmds.file(f=True, new=True)

        # 아이콘 렌더 프리셋 파일을 임포트 (프리셋 파일보호용)
        cmds.file( 
                _renderIconsFile ,
                i=True, 
                ignoreVersion=True,
                removeDuplicateNetworks = True,
                renamingPrefix = self._namespace,
                preserveReferences = True,
                loadReferenceDepth = 'all',
                options='v=0;p=17'
                )        

        cmds.playbackOptions(min=0, max=2000)

        cmds.setAttr('defaultRenderGlobals.currentRenderer', 'mentalRay', type='string')
        cmds.setAttr('defaultRenderGlobals.imageFormat', 32) # png
        cmds.setAttr('defaultRenderGlobals.enableDefaultLight', 0)

        cmds.setAttr('defaultResolution.width', 512)
        cmds.setAttr('defaultResolution.height', 512)
        cmds.setAttr('defaultResolution.deviceAspectRatio', 1)

        cmds.setAttr('perspShape.filmFit', 3)            # Overscan
        cmds.setAttr('perspShape.displayResolution', 1)
        cmds.setAttr('perspShape.displayGateMask', 1)
        cmds.setAttr('perspShape.overscan', 1.25)

        cmds.setAttr('perspShape.focalLength', 100)
        cmds.setAttr('perspShape.horizontalFilmAperture', 1)
        cmds.setAttr('perspShape.verticalFilmAperture', 1)

        cmds.parentConstraint('persp','makeIcon_renderFile')
        
        cmds.setAttr('mssge.translateY', -0.70)
        cmds.setAttr('mssge.translateZ', -5)

        return True
    
    # 아이콘 렌더 시작
    def renderIcons(self, *args):
        # 로딩된 파일이 없으면 중단
        if not self._currentFile:
            print u'렌더링 할 파일을 로드하쇼.'
            return

        # 필요 변수 설정
        _dir            = os.path.dirname(self._currentFile)                # 디렉토리명
        _file           = mel.eval('basenameEx("%s")'%self._currentFile)    # 파일명(확장자x)
        _renderIconFile = _dir+'/icons/'+_file                              # 아이콘 렌더링 경로

        # 아이콘 폴더 숨김
        _iconDir = os.path.dirname(_renderIconFile).replace('/','\\\\')
        _melCmd = 'system "attrib +h %s"'%_iconDir
        #print _melCmd
        mel.eval(_melCmd)

        # 렌더글로벌 조정 : 파일 이름
        cmds.setAttr('defaultRenderGlobals.imageFilePrefix',_renderIconFile, type='string')

        # 아이콘 렌더 : 렌더~
        print u' ---- 아이콘 렌더시작 (%dx%d) :%s ------------------------------------'%(self._iconRenderRes, self._iconRenderRes, _renderIconFile+'.png')
        cmds.Mayatomr( preview=True, camera='perspShape', xResolution=self._iconRenderRes, yResolution=self._iconRenderRes )         
        cmds.sysFile(_renderIconFile+'_tmp.png', rename=_renderIconFile+'.png')

        # 그리드레이아웃 갱신 : 렌더 끝
        print u' ---- 렌더완료 (%dx%d) :%s -------------------------------------------'%(self._iconRenderRes, self._iconRenderRes, _renderIconFile+'.png')
        self.updateGrid()

        # 명령 아웃
        print u'%s.renderIcons() '%(self._instance)
    
    # 아이콘 배치 렌더
    def iconBatchRender(self, *args):
        #print 'args', args
        # 아이콘 렌더링
        if not self.renderIcon_setting():
            print u' iconBatchRender : 중단 되었습니다. ------------------------------'
            return False

        for _file in self.getFileList(): 
            # 레퍼런스로 파일 로드
            self.Reference(_file)
            cmds.refresh()

            # 자동 핏
            if args:
                if args[0]>0:
                    _type = ['mesh','nurbsSurface','joint']
                    cmds.select( cmds.ls( self._namespace+':*', type=_type, visible=True ) )
                    cmds.pickWalk(direction='up' )
                    cmds.viewFit( 'perspShape', 
                        allObjects=False,
                        animate=True,
                        )
                    cmds.select( cl=True )
            
                # 갱신
                cmds.refresh()

                # 프리뷰만..
                if args[0]==2:
                    continue

            # 아이콘 렌더
            self.renderIcons()
    
    # 아이콘 크기 설정
    def setIconSize(self, *args):
        if not args:
            return
        # 멤버 변수 조정
        self._iconSize = args[0]
        
        _mod = cmds.getModifiers()
        if _mod== 4 or _mod== 1 or _mod== 8:
            if   32 <= self._iconSize < 64-16:
                self._iconSize = 32
            elif 64-16 <= self._iconSize < 128-32:
                self._iconSize = 64
            elif 128-32 <= self._iconSize < 256-64:
                self._iconSize = 128
            elif 256-64 <= self._iconSize < 512-128:
                self._iconSize = 256
            elif 512-128 <= self._iconSize:
                self._iconSize = 512 
                
        self.updateUI()

    def getIconSize(self):
        return self._iconSize

    # 아이콘 렌더 크기 설정
    def setIconRenderRes(self, *args):
        self._iconRenderRes = args[0]
    
    def getIconRenderRes(self):
        return self._iconRenderRes

    #------------------------------------------------------------------
    #
    # UI 모듈
    #
    #------------------------------------------------------------------
    def UI_Grid(self): 
        # 경로 : 아이콘 경로
        _thumbnailPath  = self.getPath()+'/icons/'
        _iconEmpty = self._iconPath+'emptyIcon.png' # 경로 : 아이콘 없는 파일 위치
        
        # 그리드 레이아웃 : 삭제하고, 부모 레이아웃 확인
        if cmds.gridLayout(self._UI_GRD_gridLayout, q=1, exists=True):
            self._UI_LAY_gridParent = cmds.gridLayout(self._UI_GRD_gridLayout, q=1, parent=True)
            cmds.deleteUI(self._UI_GRD_gridLayout)

        # 그리드 레이아웃 : 시작
        self._UI_GRD_gridLayout = cmds.gridLayout(
                                            parent = self._UI_LAY_gridParent,
                                            columnsResizable=True,
                                            autoGrow=True,
                                            allowEmptyCells=False,
                                            cellWidthHeight=[1,1],
                                            cellHeight=1,
                                            numberOfRowsColumns = [1,3],
                                            cellWidth=1
                                            )        

        # 아이콘들 배치
        for _file in self.getFileList():
            # -------------- icon 이미지 경로 -------------            
            _baseName = mel.eval( 'basenameEx("%s")'%_file )
            _fileName = os.path.basename(_file)
            _icon = _thumbnailPath + _baseName +'.png'
            if not os.access(_icon, os.F_OK):
                _icon = _iconEmpty

            # -------------- 파일 정보
            # 'type':_type, 'ext':_ext, 'size':_size, 'fsize':_fileSize, 'ctime':_ctime, 'mtime':_mtime, 'name':_file
            _fileInfo = self.getFileInfo(_file)

            # 시간 체크 라벨 컬러 바꿈
            _mtime = time.localtime(os.path.getmtime(_file))[2]
            _today = time.localtime()[2]

            _labelColor = [.8,.8,.8]
            if   (_today-_mtime)<1: # 오늘꺼
                _labelColor = [1,.5,.5]
            elif (_today-_mtime)<2: # 2일전꺼
                _labelColor = [.9,.8,.8]
                
            # -------------- Thumbnail FormLayout ---------
            _iconForm  = cmds.formLayout() 
            
            # -------------- Thumbnail Icon ---------------
            _iconFrame = cmds.frameLayout( borderVisible=False, labelVisible=False )
            
            _annotation  = '\n'            
            _annotation += u'     경로 : '+_file+'  \n'
            _annotation += u'     형식 : '+_fileInfo['ext']+'  \n'
            _annotation += u'     크기 : '+_fileInfo['fsize']+'\n'
            _annotation += u'  생성일 : '+_fileInfo['ctime']+'\n'
            _annotation += u'  수정일 : '+_fileInfo['mtime']+'\n'
            
            cmds.iconTextButton(            
                                label=_fileName,
                                preventOverride=False,
                                marginHeight=0,
                                style='iconOnly',
                                width=2,
                                height=2,
                                image= _icon,
                                annotation= _annotation,
                                command= pyMel.Callback(self.excute, _file)
                                )
            cmds.setParent('..') # _iconFrame Out
            
            # -------------- Thumbnail Label ---------------
            _iconText = cmds.columnLayout(adj=1) # 텍스트가 제대로 안나와서 레이아웃 하나 더 붙임

            cmds.rowLayout(
                        nc = 2,
                        #h = 16,
                        enableBackground=True, 
                        backgroundColor=_labelColor
                        )
            #cmds.checkBox(
            #            #label='',
            #            label=' '+_file+'  ' , 
            #            )
            cmds.text(  label=' >',
                        font='smallPlainLabelFont'
                        )
            cmds.text( 
                        label=' '+_fileName+'  ' , 
                        align='left', 
                        #font='boldLabelFont', 
                        #font='smallBoldLabelFont', 
                        #font='tinyBoldLabelFont', 
                        #font='plainLabelFont', 
                        font='smallPlainLabelFont', 
                        #font='obliqueLabelFont', 
                        #font='smallObliqueLabelFont', 
                        #font='fixedWidthFont', 
                        #font='smallFixedWidthFont', 
                        recomputeSize=True 
                        )
            cmds.setParent('..')
            cmds.setParent('..') # _iconText columnLayout Out

            cmds.setParent('..') # _iconForm Out
            cmds.formLayout(
                _iconForm,
                edit=True,
                attachForm=[
                    (_iconFrame, 'top', 0),
                    (_iconFrame, 'left', 0),
                    (_iconFrame, 'right', 0),
                    (_iconFrame, 'bottom', 0),

                    (_iconText, 'left', 0),
                    (_iconText, 'bottom', -1)
                    ],
                attachNone=[
                    (_iconText, 'right'),
                    (_iconText, 'top')
                    ]
                )

        # 그리드 레이아웃 : 끝
        cmds.setParent('..') # _UI_GRD_gridLayout Out

        cmds.refresh() # 갱신
        cmds.gridLayout(self._UI_GRD_gridLayout, e=1, allowEmptyCells=False, cellWidthHeight=[self._iconSize,self._iconSize])
        cmds.refresh() # 갱신

    def UI_Top(self):
        _return = cmds.rowLayout(nc=2, adjustableColumn=1, vis=False)
        self._pathTFG = cmds.textFieldGrp( label='Path : ', text=self._path, adjustableColumn=2, columnWidth2=[50,30], cc=self.setPath)
        cmds.symbolButton( image='navButtonBrowse.png', c=self.setPath_fromBrower )
        cmds.setParent('..')
        return _return

    def UI_Middle(self):
        _return = cmds.scrollLayout(childResizable=True)
        cmds.columnLayout(adj=1)
        self._UI_LAY_gridParent = cmds.frameLayout( collapsable=False, borderVisible=False, labelVisible=False)
        self.UI_Grid()
        cmds.setParent('..') # frameLayout Out
        cmds.setParent('..') # columnLayout Out
        cmds.setParent('..') # scrollLayout Out
        return _return

    def UI_Bottom(self):
        _return = cmds.columnLayout( adj=True, )

        cmds.frameLayout(labelVisible=False)
        cmds.helpLine()
        cmds.setParent('..')
        
        #cmds.rowLayout( numberOfColumns=2 )
        #self.UI_namespace()
        #self.UI_iconTools()
        #cmds.setParent('..') # rowLayout out
        return _return

    def UI_namespace(self):
        # namespace
        cmds.rowLayout( numberOfColumns=2 )
        self._UI_TFG_namespace = cmds.textFieldGrp(label = 'namespace : ', cw2=[80,80])
        cmds.popupMenu( button=3 )
        cmds.menuItem( l='Open Reference Editor', c='import maya.mel;maya.mel.eval(\'ReferenceEditor\')')
        cmds.menuItem( l='Open Namespace Editor', c='import maya.mel;maya.mel.eval(\'namespaceEditor\')')
        cmds.symbolButton( image=self._icon_setNamespace, c=self.setNamespace_fromBtn)
        cmds.setParent('..') # rowLayout out
    
    def UI_iconTools(self):
        cmds.rowLayout( numberOfColumns=2 )

        cmds.rowLayout( numberOfColumns=2 )
        cmds.symbolButton( image=self._iconPath +'sepBar.png' )
        cmds.symbolButton( image=self._iconPath+'renderIcons.png', c=self.renderIcon_setting)

        cmds.popupMenu( button=3 )
        cmds.menuItem ( label='Render All Icons (currentView)',     c= pyMel.Callback( self.iconBatchRender, 0 ))
        cmds.menuItem ( label='Render All Icons (viewFit)',         c= pyMel.Callback( self.iconBatchRender, 1 ))
        cmds.menuItem ( label='Render All Icons (viewFit preView)', c= pyMel.Callback( self.iconBatchRender, 2 ))
        cmds.menuItem( divider=True )
        cmds.menuItem ( subMenu=True, label='icon Resolution' )
        cmds.radioMenuItemCollection()
        cmds.menuItem ( label='128', radioButton=self._iconRenderRes==128 ,c= pyMel.Callback( self.setIconRenderRes, 128 ))
        cmds.menuItem ( label='256', radioButton=self._iconRenderRes==256 ,c= pyMel.Callback( self.setIconRenderRes, 256 ))
        cmds.menuItem ( label='512', radioButton=self._iconRenderRes==512 ,c= pyMel.Callback( self.setIconRenderRes, 512 ))
        cmds.setParent( '..', menu=True )

        cmds.setParent('..') # rowLayout out

        # 3. -------------------------------------- in
        cmds.rowLayout( numberOfColumns=2, adjustableColumn=2)
        cmds.symbolButton( image=self._iconPath+'sepBar.png' )
        self._UI_ISG_iconSlider=cmds.intSliderGrp( 
                            label='icon Size : ', 
                            columnWidth3=[52,30,80], 
                            field=True, 
                            minValue=32, maxValue=512,
                            fieldMinValue=32, fieldMaxValue=512,
                            value=self._iconSize,
                            dragCommand=self.setIconSize, 
                            changeCommand=self.setIconSize
                            )
        cmds.setParent('..') # rowLayout out
        # 3. -------------------------------------- out

        cmds.setParent( '..')
    
    #------------------------------------------------------------------
    #
    # 윈도우 관련
    #
    #------------------------------------------------------------------
    # 윈도우 모듈
    def Module(self):
        _return = cmds.formLayout()

        _top = self.UI_Top()
        _mid = self.UI_Middle()
        _btm = self.UI_Bottom()

        #cmds.setParent('..')
        
        cmds.formLayout(
            _return, 
            edit=True, 

            attachForm=[
                (_top, 'top', 0),
                (_top, 'left', 0),
                (_top, 'right', 0),

                (_btm, 'left', 0),
                (_btm, 'right', 0),
                (_btm, 'bottom', 0),

                (_mid, 'left', 0),
                (_mid, 'right', 0)
                ],

            attachControl=[
                (_mid, 'top', 0, _top),
                (_mid, 'bottom', 0, _btm)
                ],

            attachNone=[
                (_top, 'bottom'),
                (_btm, 'top')
                ]
                        )
        self.updateUI()
        return _return
    
    # 독립 윈도우
    def Window(self):
        '''Open Window'''

        if cmds.window(self._window, q=1, exists=1): cmds.deleteUI(self._window)

        cmds.window(self._window)
        self.Module()
        cmds.showWindow(self._window)

        if cmds.dockControl(self._dock, q=1, exists=1):             
            cmds.deleteUI(self._dock)
    
    # dock 형식 윈도우
    def Dock(self):
        '''Open Window'''

        if cmds.window(self._window, q=1, exists=1): cmds.deleteUI(self._window)

        cmds.window(self._window)
        self.Module()

        _area = 'right'
        _floating = False
        _label = 'Asset'
        _width = 330
        _allowedAreas = ['right', 'left']

        if cmds.dockControl(self._dock, q=1, exists=1):             
            _area     = cmds.dockControl(self._dock, q=1, area=True)
            _floating = cmds.dockControl(self._dock, q=1, floating=True)
            _width    = cmds.dockControl(self._dock, q=1, width=True)
            cmds.deleteUI(self._dock)

        cmds.dockControl(
            self._dock,
            area = _area,
            label = _label,
            floating = _floating,
            width = _width,
            content = self._window,
            allowedArea = _allowedAreas
            )

    # Window, Dock 전환
    def switch_Dock_Window(self, *args):
        if cmds.dockControl(self._dock, q=1, exists=1):
            self.Window()
        else:
            self.Dock()

class namespaceEditor():
    _scriptPath = os.path.dirname(__file__)
    
    _iconPath = _scriptPath+'/icons/'

    _icon_bar = _iconPath+'sepBar.png'

    _icon_autoNamespace_0 = _iconPath+'autoNamespace_0.png'
    _icon_autoNamespace_1 = _iconPath+'autoNamespace_1.png'
    _icon_autoNamespace = _icon_autoNamespace_0

    _icon_importRef_0 = _iconPath+'importRef_0.png'
    _icon_importRef_1 = _iconPath+'importRef_1.png'
    _icon_importRef = _icon_importRef_0

    _icon_removeRef_0 = _iconPath+'removeRef_0.png'
    _icon_removeRef_1 = _iconPath+'removeRef_1.png'
    _icon_removeRef = _icon_removeRef_0

    _icon_setNamespace_0 = _iconPath+'setNamespace_0.png'
    _icon_setNamespace_1 = _iconPath+'setNamespace_1.png'
    _icon_setNamespace = _icon_setNamespace_0

    _icon_renameNamespace_0 = _iconPath+'renameNamespace_0.png'
    _icon_renameNamespace_1 = _iconPath+'renameNamespace_1.png'
    _icon_renameNamespace = _icon_renameNamespace_0

    _autoNamespace = True
    _defaultNamespace = ''

    _data = []
    _namespace = []
    _refFile = []
    _refNode = []
    _debug = False

    # importOption
    _removeNamespace = 0

    def __init__(self, _instance, *args, **kwargs):
        # set instance
        self._instance = _instance

        # UI
        self._Window = self.getInstance()+'_namespaceEditor'
        self._Module = self.getInstance()+'_namespaceEditor_Module'

        # 입력 키워드 분석
        _key = [_key for _key in kwargs.keys()]
        
        # command
        if kwargs.get('command') or kwargs.get('c'):
            _input = ''

            # 해당 키워드에 해당하는 키값을 받아오고
            if   kwargs.get('command'): _input = kwargs.get('command')
            elif kwargs.get('c'):       _input = kwargs.get('c')
                
            self._command= _input
        else:
            self._command= _instance+'.defaultCallback'

        # autoNamespace
        if kwargs.get('autoNamespace') or kwargs.get('ans'):
            _input = ''

            # 해당 키워드에 해당하는 키값을 받아오고
            if   kwargs.get('autoNamespace'): _input = kwargs.get('command')
            elif kwargs.get('ans'):           _input = kwargs.get('ans')
                
            self._autoNamespace = _input
        else:
            self._autoNamespace = False
        
        # prefix
        if kwargs.get('prefix') or kwargs.get('pre'):
            _input = ''

            # 해당 키워드에 해당하는 키값을 받아오고
            if   kwargs.get('prefix'): _input = kwargs.get('prefix')
            elif kwargs.get('pre'):    _input = kwargs.get('pre')
                
            self._prefix = _input
        else:
            self._prefix = ''

        # subfix
        if kwargs.get('subfix') or kwargs.get('sub'):
            _input = ''

            # 해당 키워드에 해당하는 키값을 받아오고
            if   kwargs.get('subfix'): _input = kwargs.get('subfix')
            elif kwargs.get('sub'):    _input = kwargs.get('sub')
                
            self._subfix = _input
        else:
            self._subfix = ''

        # defaultNamespace
        if kwargs.get('namespace') or kwargs.get('ns'):
            _input = ''

            # 해당 키워드에 해당하는 키값을 받아오고
            if   kwargs.get('namespace'): _input = kwargs.get('namespace')
            elif kwargs.get('ns'):              _input = kwargs.get('ns')
                
            self._defaultNamespace = _input[0]
        else:
            self._defaultNamespace = 'REF'
    
    # instance
    def setInstance(self, *args):
        self._instance  = args[0]

    def getInstance(self, *args):
        return self._instance
    
    # callBack
    def callbackCmd(self, *args):
        _cmd= self.getCommand()+'()'
        #print _cmd
        exec ( _cmd )

        if False:
            print self.getInstance()+'.callbackCmd:'
            print 'reference Namespace :', self.getNamespace()
            print '     reference Node :', self.getReferenceNode()
            print '     reference File :', self.getReferenceFile()
    
    def defaultCallback(self, *args):
        print self.getInstance()+'.defaultCallback:'
        print '    reference Namespace :', self.getNamespace()
        print '         reference Node :', self.getReferenceNode()
        print '         reference File :', self.getReferenceFile()
    
    def setCommand(self, *args):
        self._command = args[0]

    def getCommand(self, *args):
        return self._command

    #------------------------------------------------------------------
    #
    # namespace
    #
    #------------------------------------------------------------------  
    # namespace 관련
    def setDefaultNamespace(self, *args):
        self._defaultNamespace = args[0]

    def setNamespace(self, *args):
        if args:
            if type(args[0]) == list:
                self._namespace = args[0]
            if type(args[0]) == str:
                self._namespace = [args[0]]

        _namespaceTxt = ''
        for _txt in self._namespace: _namespaceTxt += _txt+', '
        _namespaceTxt = _namespaceTxt[:-2]

        #self.setAutoNamespace(0)
        cmds.textField( self._UI_TFD_namespace, e=True, text=_namespaceTxt)
        #print 'namespaceEditor().setNamespace(\'%s\')'%_namespaceTxt

        #self.updateUI()
   
    def getNamespace(self):
        return self._namespace

    def renameNamespace(self, *args):
        _selNamespace = self._namespace[-1]

        # 현재 네임스페이스 임시저장
        _currentNamespace = cmds.namespaceInfo( currentNamespace=True )

        # 현재 네임스페이스 루트로 변경
        cmds.namespace( set=':' )

        # 입력 받음 : 함수
        def newName( _namespace , _message ):
            _return = ''
            
            _result = cmds.promptDialog(
                title='Rename Namespace',
                message=_message,
                text = _namespace,
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel'
                )
            if _result != 'OK':
                return ''

            _return = cmds.promptDialog(query=True, text=True)
            
            if cmds.namespace( exists=':'+_return ):
                _return = newName( _namespace, u'":%s"는 이미 존재하는 namespace입니다. \n다른 namespace를 입력하세요.'%_return )

            return _return

        # 입력 받음
        _newName = newName( _selNamespace, u'":%s" namespace 변경.'%_selNamespace )
        
        # 변경
        if _newName:
            # namespace 변경
            cmds.namespace( rename=[_selNamespace, _newName])
            
            # Refresh : 아래 구문이 없으면, 네임스페이스를 변경해도 리프레시가 안됨.
            _sel = cmds.ls(sl=True)
            self.updateUI()
            cmds.select(_sel)

        # 저장된 네임스페이스로 되돌림
        cmds.namespace( set=_currentNamespace )

    # reference 관련
    def getReferenceNode(self):
        return self._refNode
    
    def getReferenceFile(self):
        return self._refFile
    
    # debug 관련
    def toggleDebug(self, *args):
        _tmp = (self._debug+1)%2
        self.setDebug( _tmp )

    def setDebug(self,*args):
        self._debug=args[0]
        self.updateUI()
    
    # auto namespace 관련
    def toggleAutoNamespace(self, *args):
        _autoNamespace = not self._autoNamespace
        #_autoNamespace = (self._autoNamespace+1)%2
        self.setAutoNamespace( _autoNamespace )
        self.updateUI()

    def setAutoNamespace(self, *args):
        # 멤버변수 조정
        self._autoNamespace = args[0]

        # UI 조정
        #self.updateUI()
    
    def getAutoNamespace(self, *args):
        return self._autoNamespace
    
    # prefix, subfix 관련
    def setPrefix(self, *args):
        self._prefix = args[0]
        #self.updateUI()

    def getPrefix(self):
        return self._prefix

    def setSubfix(self, *args):
        self._subfix = args[0]
        #self.updateUI()

    def getSubfix(self):
        return self._subfix
    #------------------------------------------------------------------
    #
    # updateUI
    #
    #------------------------------------------------------------------      
    def updateUI(self,*args):
        #print '---------------------- namespace updateUI : call---------------------------------'

        # 옵션
        _reformText = False
        _fromTextField = ''

        #--------------------------------------------------
        #
        # 입력 자료 분석
        #
        #--------------------------------------------------
        self._data = []

        self._selObj = []
        self._refNode= []
        self._refFile= []
        self._namespace= []

        #--------------------------------------------------
        #
        # 선택한 오브젝트로부터 데이터 입력
        #
        #--------------------------------------------------
        if self.getAutoNamespace():
            _sel = cmds.ls( sl=True )
            for _node in _sel:
                # _node가 레퍼런스 관련 노드만 추림
                if cmds.referenceQuery( _node, isNodeReferenced=True ) or cmds.nodeType(_node)=='reference':                    
                    
                    # namespace prefix, subfix
                    _prefix = self.getPrefix()
                    _subfix = self.getSubfix()
                    _namespace = cmds.referenceQuery( _node, namespace=True )[1:]

                    if _prefix and not _prefix == _namespace[:len(_prefix)]  : _namespace = _prefix + _namespace                    
                    if _subfix and not _subfix == _namespace[-len(_subfix):] : _namespace = _namespace + _subfix

                    _referenceNode =''
                    _referenceFile =''
                    _referenceObj  =''

                    _ls = cmds.ls(_namespace+':*')
                    if _ls:
                        _referenceObj = _ls[0]
                        _referenceNode = cmds.referenceQuery( _referenceObj, referenceNode=True)
                        _referenceFile = cmds.referenceQuery( _referenceNode, filename=True)
                    
                    _data = {   'namespace'    : _namespace, 
                                'referenceNode': _referenceNode,
                                'referenceFile': _referenceFile,
                                'referenceObj' : _referenceObj
                                 }
                    
                    # 중복데이터 이면 통과
                    if _data in self._data:
                        continue
                    
                    # 자료 입력
                    self._data.append(_data)
                    
                    self._selObj.append( _referenceObj )
                    self._refNode.append( _referenceNode )
                    self._refFile.append( _referenceFile )
                    self._namespace.append( _namespace )
        #--------------------------------------------------
        #
        # 텍스트 필드에 입력된 데이터 처리
        #
        #--------------------------------------------------
        else:
            # 텍스트 필드에 입력된 내용을 입력
            _fromTextField = cmds.textField( self._UI_TFD_namespace, q=True, text=True)

            #print '_fromTextField :',_fromTextField
            
            # 입력된 네임스페이스들을 나눠서 _namespace에 입력
            _inputNamespace = [ _item.strip(' ') for _item in _fromTextField.replace(',',' ').split( ' ' ) if _item ]

            # 씬안에 있는 네임스페이스들검색
            _namespaceList     = [_nsList         for _nsList in cmds.namespaceInfo( listOnlyNamespaces=True )]
            _namespaceList_low = [_nsList.lower() for _nsList in _namespaceList]

            _namespaces = []
            # 와일드카드 검색
            for _ns in _inputNamespace:
                if not _ns:
                    continue

                _fnmatchFilter = fnmatch.filter( _namespaceList, _ns)
                if _fnmatchFilter:
                    _namespaces += _fnmatchFilter
                    #print u'와일드카드 검색(%s) :'%_ns, u'있어서 추가'
                else:
                    _namespaces += [_ns]
                    #print u'와일드카드 검색(%s) :'%_ns, u'없지만 추가'

            #print u'결정된 네임 스페이스 :', _namespaces

            
            # 텍스트필드에 입력된 namespace를 분석해서 다시 정리함.
            for _i, _namespace in enumerate(_namespaces):
                #print _namespace, u'확인' 

                _referenceNode = ''
                _referenceFile = ''
                _referendeObj = ''

                # 빈 텍스트면 통과
                if not _namespace:
                    #print u'빈 텍스트여서 통과 :', _namespaces
                    continue
                
                # _namespace로 시작하는 오브젝트 선택
                _sel = cmds.ls( _namespace+':*')

                # 선택된 레퍼런스 관련 오브젝트가 있으면
                if _sel and cmds.referenceQuery( _sel[0], isNodeReferenced=True ):
                    # 첫번째 선택된 오브젝트를 _refObj에 입력
                    _referendeObj  = _sel[0]
                    _referenceNode = cmds.referenceQuery( _referendeObj, referenceNode=True)
                    _referenceFile = cmds.referenceQuery( _referendeObj, filename=True)
                
                _data = {
                    'namespace'    : _namespace, 
                    'referenceNode': _referenceNode,
                    'referenceFile': _referenceFile,
                    'referenceObj' : _referendeObj
                     }
                
                # 중복데이터 이면 패스
                if _data in self._data:
                    continue

                self._data.append(_data)                
                self._selObj.append(_referendeObj)
                self._refNode.append(_referenceNode)
                self._refFile.append(_referenceFile)
                self._namespace.append(_namespace) # :name 에서 ":" 삭제
                #print u'추가된 데이터 :', _i, _namespaces, 
                        
        if not self._data:
            #print 'self._defaultNamespace : ',self._defaultNamespace
            _namespace     = self._defaultNamespace
            _referenceNode =''
            _referenceFile =''
            _referenceObj  =''

            _ls = cmds.ls(_namespace+':*')
            if _namespace and _ls:
                _referenceObj = _ls[0]
                _referenceNode = cmds.referenceQuery( _referenceObj, referenceNode=True)
                _referenceFile = cmds.referenceQuery( _referenceNode, filename=True)

            _data = {   'namespace'    : _namespace, 
                        'referenceNode': _referenceNode,
                        'referenceFile': _referenceFile,
                        'referenceObj' : _referenceObj
                         }
    
            # 자료 입력
            self._data = [_data]
            
            self._selObj = [ _referenceObj]
            self._refNode = [ _referenceNode]
            self._refFile = [ _referenceFile]
            self._namespace = [ _namespace]    

        #print u'마무리 된 데이터들 :', 
        #for _txt in self._data: print _txt

        #--------------------------------------------------
        #
        # Callback
        #
        #--------------------------------------------------
        # data out
        #self.callbackCmd()
        
        #--------------------------------------------------
        #
        # UI 조정
        #
        #--------------------------------------------------
        # 관련 버튼 초기화
        _icon_autoNamespace   = self._icon_autoNamespace_0
        _icon_setNamespace    = self._icon_setNamespace_0
        _icon_renameNamespace = self._icon_renameNamespace_0
        _icon_removeRef       = self._icon_removeRef_0
        _icon_importRef       = self._icon_importRef_0

        _en_namespaceTextField = False
        _en_setNamespace       = False
        _en_renameNamespace    = False
        _en_removeReference    = False
        _en_importReference    = False
        
        #--------------------------------------------------
        # _debug
        #
        self._UI_ROL_debug = cmds.rowLayout(self._UI_ROL_debug, edit=True, vis=self._debug )
        
        #--------------------------------------------------
        # Text Scroll List Update
        #
        def updateTSL(_tsl, _list):
            cmds.textScrollList( _tsl, edit=True, removeAll=True)
            if _list:
                cmds.textScrollList( _tsl, edit=True, append=_list)

        updateTSL( self._UI_TSL_selObj,    self._selObj)
        updateTSL( self._UI_TSL_refNode,   self._refNode)
        updateTSL( self._UI_TSL_namespace, self._namespace)
        updateTSL( self._UI_TSL_refFile,   self._refFile)    
        
        #--------------------------------------------------
        # Auto Namespace
        #
        if self._autoNamespace:
            _icon_autoNamespace = self._icon_autoNamespace_1

        cmds.symbolButton( self._UI_BTN_autoNamespace, edit=True, image=_icon_autoNamespace)  
        
        #--------------------------------------------------
        # namespace Texfield
        #
        if not self._autoNamespace:
            _en_namespaceTextField = True
        
        _textField = ''
        for _namespace in self._namespace:
            _textField += _namespace +', '
        _textField = _textField[:-2]

        cmds.textField( self._UI_TFD_namespace, edit=True, editable=_en_namespaceTextField, text=_textField)
        
        #--------------------------------------------------
        # Set Namespace
        #
        if not self._autoNamespace:
            _en_setNamespace = True
            _icon_setNamespace = self._icon_setNamespace_1

        cmds.symbolButton( self._UI_BTN_namespaceSet , edit=True, image=_icon_setNamespace, enable=_en_setNamespace)
        
        #--------------------------------------------------
        # Rename Namespace
        #
        # 네임스페이스가 하나만 선택되어있고,
        # 존재하는 네임스페이스 이면
        # 사용자가 네임스페이스 변경 가능
        if len(self._namespace)==1 and cmds.namespace( exists=':'+self._namespace[0] ):
            _en_renameNamespace   = True
            _icon_renameNamespace = self._icon_renameNamespace_1

        cmds.symbolButton( self._UI_BTN_namespaceRename, edit=True, image=_icon_renameNamespace, enable=_en_renameNamespace)

        #--------------------------------------------------
        # Remove Reference
        #
        # 해당 레퍼런스 노드가 존재하면 레퍼런스 삭제 가능
        if self._refNode:
            _en_removeReference = True
            _icon_removeRef = self._icon_removeRef_1
            
        cmds.symbolButton( self._UI_BTN_removeRef, edit=True, image=_icon_removeRef, enable=_en_removeReference)
        
        #--------------------------------------------------
        # Import Reference
        #
        # 해당 레퍼런스 노드가 존재하면 레퍼런스 임포트 가능
        if self._refNode:
            _en_importReference = True
            _icon_importRef = self._icon_importRef_1

        cmds.symbolButton( self._UI_BTN_importRef, edit=True, image=_icon_importRef, enable=_en_importReference)

    #------------------------------------------------------------------
    #
    # Open
    #
    #------------------------------------------------------------------  
    def Open(self, *args):
        if not args:
            return

        if not os.access(args[0], os.F_OK):
            return 'no Path'

        _ext = args[0][-3:]
        if   _ext=='.ma':
            _type='mayaAscii'
        elif _ext=='.mb':
            _type='mayaBinary'
        elif _ext=='mel':
            _type='mel'
        else:
            _type=''
        
        _file = args[0]

        cmds.file( _file, open=True, force=True, options='v=0', ignoreVersion=True, type=_type )
        mel.eval( 'addRecentFile(\"%s\",\"%s\")'%(_file, _type) )

    #------------------------------------------------------------------
    #
    # reference
    #
    #------------------------------------------------------------------ 
    def Reference(self, *args):
        if not args:
            return

        if not os.access(args[0], os.F_OK):
            return 'no Path'

        _refFile = args[0]
        self._currentFilePath = _refFile.replace('\\','/')
        _referenceNode = self._namespace+'RN'

        if cmds.objExists(_referenceNode) and cmds.nodeType(_referenceNode)=='reference':
            # 현제 레퍼런스 파일 삭제
            # cmds.file(removeReference=True, referenceNode=_referenceNode)

            # 현제 레퍼런스 파일 갱샌
            cmds.file( self._currentFilePath, loadReference=_referenceNode, options= 'v=0;')
        else:
            cmds.file( 
                self._currentFilePath, 
                reference=True,
                namespace=self._namespace,
                loadReferenceDepth='all', 
                sharedNodes='shadingNetworks',
                ignoreVersion=True,
                mergenamespacesOnClash=False,
                options= 'v=0;'
                )
   
    def removeReference(self, *args):
        if not self._refNode:
            return False

        # 확인 받을것
        _list =''
        for _reference in self._refNode:
            if _reference:
                _list += _reference+'\n'
        
        if not _list:
            print u'namespace에 해당하는 레퍼런스가 없습니다. namespace를 확인하세요.'
            return
        
        _result = cmds.confirmDialog( 
            title=u'레퍼런스를 삭제합니다.', 
            message=u'%s \n위 레퍼런스를 삭제하시겠습니까?'%_list, 
            button=['Yes','No'], 
            defaultButton='Yes', 
            cancelButton='No', 
            dismissString='No' 
            )

        if _result != "Yes":
            return False

        # 삭제
        for _reference in self._refNode:
            cmds.file( removeReference=True, referenceNode=_reference )
        
        return True

    #------------------------------------------------------------------
    #
    # import
    #
    #------------------------------------------------------------------ 
    def importReference(self, *args):
        if not self._refNode:
            return False
        
         # 확인 받을것
        _list =''
        for _reference in self._refNode:
            _list += _reference+'\n'

        _result = cmds.confirmDialog( 
            title=u'임포트.', 
            message=u'%s\n 위 파일들을 임포트 하시겠습니까?'%_list,
            button=['Yes','No'], 
            defaultButton='Yes', 
            cancelButton='No', 
            dismissString='No' 
            )

        if _result != "Yes":
            return False
        
        # 임포트
        for _reference in self._refNode:
            # 로드된 레퍼런스이면.
            if cmds.referenceQuery(_reference, isLoaded=True):
                _namespace = cmds.referenceQuery( _reference, namespace=True )[1:]
                _objList   = cmds.referenceQuery( _reference, nodes=True )
			    # 임포트
                cmds.file( importReference=True, referenceNode=_reference )
                
                # 네임스페이스 처리                
                if self._removeNamespace == 0:
                    #_objList = cmds.ls(_namespace+':*')
                    for _obj in _objList:
                        
                        _newName = ''
                        if ':' in _obj:
                            _newName = _namespace+'__'+_obj[len(_namespace)+1:]
                        else:
                            _newName = _namespace+'__'+_obj

                        if cmds.objExists(_obj):
                            cmds.rename(_obj, _newName)
                            print (_obj +'    >>    '+_newName).center(150)
                        else:
                            print (_obj +'   Fail   '+_newName).center(150)
                    cmds.namespace( removeNamespace = _namespace, mergeNamespaceWithRoot = True) 
                    
                elif self._removeNamespace == 1:
                    cmds.namespace( removeNamespace = _namespace, mergeNamespaceWithRoot = True)

        return True

    def setRemoveNamespaceOption(self, *args): 
        if   cmds.menuItem( self._UI_MIT_removeNamespaceOpt_0, q=1, radioButton=True) : self._removeNamespace=0
        elif cmds.menuItem( self._UI_MIT_removeNamespaceOpt_1, q=1, radioButton=True) : self._removeNamespace=1
        elif cmds.menuItem( self._UI_MIT_removeNamespaceOpt_2, q=1, radioButton=True) : self._removeNamespace=2
    #------------------------------------------------------------------
    #
    # UI 모듈
    #
    #------------------------------------------------------------------  
    def getModule(self, *args):
        return cmds.columnLayout( self._Module, q=1, exists=True )
    
    def Module(self):
        self._Module = cmds.columnLayout( adj=True )

        # rowLayout : 상태 파악 용 #--------------------------------------------------------------------------------
        self._UI_ROL_debug = cmds.rowLayout( numberOfColumns=4,  columnWidth4=(80, 80, 80, 80), adjustableColumn=4)
        
        cmds.columnLayout( adj=True )
        cmds.text(label='selObj',         align='center')
        self._UI_TSL_selObj    = cmds.textScrollList()
        cmds.setParent('..')

        cmds.columnLayout( adj=True )
        cmds.text(label='refNode',        align='center')
        self._UI_TSL_refNode   = cmds.textScrollList()
        cmds.setParent('..')

        cmds.columnLayout( adj=True )
        cmds.text(label='Namespace',      align='center')
        self._UI_TSL_namespace = cmds.textScrollList()
        cmds.setParent('..')

        cmds.columnLayout( adj=True )
        cmds.text(label='Reference File', align='center')
        self._UI_TSL_refFile   = cmds.textScrollList( w=10)
        cmds.setParent('..') 

        cmds.setParent('..')
        # rowLayout : 상태 파악 용 Out -----------------------------------------------------------------------------

        # rowLayout1
        cmds.rowLayout( numberOfColumns=2 , adjustableColumn=2)
        _UI_BTN_visToggle = cmds.symbolButton( image=self._icon_bar )

        # rowLayout2
        self._UI_RCL_nsGrp = cmds.rowLayout( numberOfColumns=6, adjustableColumn=3 )

        # autonamespace
        if self._autoNamespace: 
            self._icon_autoNamespace = self._icon_autoNamespace_1
        self._UI_BTN_autoNamespace = cmds.symbolButton( image=self._icon_autoNamespace, c=self.toggleAutoNamespace)
        
        # namespace
        cmds.text(label = 'namespace :')
        cmds.popupMenu( button=3 )
        cmds.menuItem( l='Open Reference Editor', c='import maya.mel;maya.mel.eval(\'ReferenceEditor\')')
        cmds.menuItem( l='Open Namespace Editor', c='import maya.mel;maya.mel.eval(\'namespaceEditor\')')
        
        # rowLayout3
        self._UI_TFD_namespaceGrp    = cmds.rowLayout( numberOfColumns=3 , adjustableColumn=1)
        self._UI_TFD_namespace       = cmds.textField( editable=not self._autoNamespace, font='boldLabelFont' , width = 150, h=32, enableBackground=False,  backgroundColor=[0,0,0], cc=self.updateUI)
        self._UI_BTN_namespaceSet    = cmds.symbolButton( image=self._icon_setNamespace, enable=not self._autoNamespace, c=self.updateUI)
        self._UI_BTN_namespaceRename = cmds.symbolButton( image=self._icon_renameNamespace, enable=True, c=self.renameNamespace)
        cmds.scriptJob( parent=self._UI_TFD_namespace, event=['SelectionChanged', self.updateUI] )
        cmds.setParent('..') 
        # rowLayout3 out

        # rowLayout4
        # remove reference
        cmds.rowLayout( numberOfColumns=3)
        cmds.symbolButton( image=self._icon_bar )
        self._UI_BTN_removeRef = cmds.symbolButton( image=self._icon_removeRef, enable=False, c=self.removeReference )
        self._UI_BTN_importRef = cmds.symbolButton( image=self._icon_importRef, enable=False, c=self.importReference)
        cmds.popupMenu( button=3 )
        cmds.menuItem ( subMenu=True, label='Import Namespace Option' )
        cmds.radioMenuItemCollection()
        self._UI_MIT_removeNamespaceOpt_0=cmds.menuItem ( label='Change Namespace to Prefix', radioButton= self._removeNamespace==0 ,c= self.setRemoveNamespaceOption)
        self._UI_MIT_removeNamespaceOpt_1=cmds.menuItem ( label='Remove Namespace',           radioButton= self._removeNamespace==1 ,c= self.setRemoveNamespaceOption)
        self._UI_MIT_removeNamespaceOpt_2=cmds.menuItem ( label='Leave Namespace',            radioButton= self._removeNamespace==2 ,c= self.setRemoveNamespaceOption)        
        cmds.setParent( '..', menu=True )

        cmds.setParent('..') 
        # rowLayout4 out

        cmds.setParent('..') 
        # rowLayout2 out

        cmds.setParent('..') # rowLayout1 out
        cmds.setParent('..') # columnLayout out

        cmds.symbolButton( _UI_BTN_visToggle, edit=True, c=self.togglenamespaceWindow)

        self.updateUI()
    
    def togglenamespaceWindow(self, *args):
        _target = self._UI_RCL_nsGrp
        _vis = cmds.rowLayout( _target, q=True ,vis=True)
        _vis = (_vis+1)%2
        cmds.rowLayout( _target, e=True ,vis=_vis)

    #------------------------------------------------------------------
    #
    # 윈도우 관련
    #
    #------------------------------------------------------------------
    def Window(self):
        self._Window = 'namespaceEditor2'
        if cmds.window(self._Window, q=1, exists=1): cmds.deleteUI(self._Window)

        cmds.window(self._Window)
        self.Module()
        cmds.showWindow(self._Window)

class assetTab():
    _data = []
    _label = []
    _rootPath = []
    _startPath = []
    _window = 'tabTest'
    _command = ''

    # 초기화
    def __init__(self, _instance, **kwargs):
        # 입력 키워드 분석
        _key = [_key for _key in kwargs.keys()]
        
        # tabData
        if kwargs.get('tabData') or kwargs.get('td'):
            _input = ''
            # 해당 키워드에 해당하는 키값을 받아오고
            if   kwargs.get('tabData'): _input = kwargs.get('tabData')
            elif kwargs.get('td'):      _input = kwargs.get('td')
     
            self.setData(_input)            
        else:
            _input = [{
                'index':0, 
                'label':'Project', 
                'rootpath':'X:/2012_CounterStrike2/3D_project/Share/scenes', 
                'startPath':'X:/2012_CounterStrike2/3D_project/Share/scenes/Character',
                'namespace':'CHAR'
                }]
            self.setData(_input)
               
        # command
        if kwargs.get('command') or kwargs.get('c'):
            _input = ''
            # 해당 키워드에 해당하는 키값을 받아오고
            if   kwargs.get('command'): _input = kwargs.get('command')
            elif kwargs.get('c'):       _input = kwargs.get('c')
     
            self.setCommand(_input)
        else:
            self.setCommand('print')
    
    # getData
    def getTabData(self):
        return self._data

    def getLabel(self):
        return self._label
    
    def getRootPath(self):
        return self._rootPath
    
    def getStartPath(self):
        return self._startPath

    def getNamespace(self):
        return self._namespace

    # setData
    def setCommand(self, *args):
        self._command = args[0]
    
    def setData(self, *args):
        self._data = args[0]
        self._label     = [_data['label']     for _data in self._data]
        self._rootPath  = [_data['rootpath']  for _data in self._data]
        self._startPath = [_data['startPath'] for _data in self._data]
        self._namespace = [_data['namespace'] for _data in self._data]
    
    # callback    
    def callback_selectTab(self,*args):
        _selectTabIndex = cmds.tabLayout( self._UI_TAB_tabLayout, q=True, selectTabIndex=True)
        
        _index = _selectTabIndex-1
        _data      = self.getTabData()[_index]

        _label     = self.getLabel()[ _index ]
        _rootpath  = self.getRootPath()[_index]
        _startPath = self.getStartPath()[_index]

        exec( self._command +'(%s)'%_data )

    def Module(self):
        self._UI_TAB_tabLayout = cmds.tabLayout( innerMarginWidth=5, innerMarginHeight=5 )

        for _item in self.getLabel():
            cmds.columnLayout(_item)    
            cmds.setParent('..')

        _label = zip( self.getLabel(), self.getLabel() )
        
        cmds.tabLayout(
                self._UI_TAB_tabLayout,
                edit=True, 
                tabLabel=_label,
                selectCommand= self.callback_selectTab
                )
        cmds.setParent('..')
        return self._UI_TAB_tabLayout
    
    # 독립 윈도우
    def Window(self):
        if cmds.window(self._window, q=1, exists=1): cmds.deleteUI(self._window)

        cmds.window(self._window)
        self.Module()
        cmds.showWindow(self._window)

class assetTool():
    _scriptPath  = os.path.dirname(__file__)
    _iconPath = _scriptPath+'/icons/'

    _assetRoot = ''
    _rootPath = ''
    _startPath = ''

    def __init__(self, _instance):
        # 초기 변수 설정
        self.setInstance(_instance)
        _projectSetPath = os.path.dirname( cmds.workspace( q=1, rd=1) )

        self._autoSetPlaybackRangeToEnabledClips = False

        _aiwData = [
            {'index':0,         'label':'Project',       
                             'rootpath': _projectSetPath+'/scenes',
                            'startPath': _projectSetPath+'/scenes/Character',   
                        'autoNamespace':True,  
                            'namespace':'CHAR', 
                               'prefix':'', 
                               'subfix':'',    
                              'gridCmd':'Reference' 
                },
            {'index':1,         'label':'Character',     
                             'rootpath':'//alfredstorage/Alfred_asset/Assets/Character',       
                            'startPath':'//alfredstorage/Alfred_asset/Assets/Character/FreeStyle2',      
                        'autoNamespace':True,  
                            'namespace':'HIK',
                               'prefix':'', 
                               'subfix':'',    
                              'gridCmd':'Reference' 
                },
            {'index':2,         'label':'MotionCapture', 
                             'rootpath':'//alfredstorage/Alfred_asset/Assets/MotionCapture',   
                            'startPath':'//alfredstorage/Alfred_asset/Assets/MotionCapture/HIK_CounterStrike2/Rough_Clip',  
                        'autoNamespace':True,  
                            'namespace':'MC',   
                               'prefix':'', 
                               'subfix':'_MC', 
                              'gridCmd':'Reference_HIK' 
                },
            {'index':3,         'label':'Pose',          
                             'rootpath':'//alfredstorage/Alfred_asset/Assets/Pose',            
                            'startPath':'//alfredstorage/Alfred_asset/Assets/Pose/Body',                 
                        'autoNamespace':True,  
                            'namespace':'',     
                               'prefix':'', 
                               'subfix':'',    
                              'gridCmd':'Reference' 
                },
            {'index':4,         'label':'Modeling',      
                             'rootpath':'//alfredstorage/Alfred_asset/Assets/Modeling',        
                            'startPath':'//alfredstorage/Alfred_asset/Assets/Modeling/Vegetable',        
                        'autoNamespace':False, 
                            'namespace':'PROB', 
                               'prefix':'', 
                               'subfix':'',    
                              'gridCmd':'Reference' 
                },

            {'index':5,         'label':'Lighting',          
                             'rootpath':'//alfredstorage/Alfred_asset/Assets/Lighting',            
                            'startPath':'//alfredstorage/Alfred_asset/Assets/Lighting/sIBL_MentalRay_Standard',                 
                        'autoNamespace':True,  
                            'namespace':'Lighting',     
                               'prefix':'', 
                               'subfix':'',
                              'gridCmd':'Reference' 
                }
            ]

        _homeData = [
            {'index':0,         'label':'Project',       
                             'rootpath': _projectSetPath,      
                            'startPath': _projectSetPath+'/scenes',
                        'autoNamespace':False,  
                            'namespace':'CHAR', 
                               'prefix':'', 
                               'subfix':'',    
                              'gridCmd':'Reference' 
                },

            {'index':1,         'label':'Character',     
                             'rootpath':'E:/Assets/Character',       
                            'startPath':'E:/Assets/Character/FreeStyle2',      
                        'autoNamespace':False,  
                            'namespace':'HIK',
                               'prefix':'', 
                               'subfix':'',    
                              'gridCmd':'Reference' 
                },

            {'index':2,         'label':'Modeling',      
                             'rootpath':'E:/Assets/Modeling',        
                            'startPath':'E:/Assets/Modeling/Vegetable',        
                        'autoNamespace':False, 
                            'namespace':'PROB', 
                               'prefix':'', 
                               'subfix':'',    
                              'gridCmd':'Reference' 
                },

            {'index':3,         'label':'MotionCapture', 
                             'rootpath':'E:/Assets/MotionCapture',   
                            'startPath':'E:/Assets/MotionCapture/HIK_CounterStrike2/Rough_Clip',  
                        'autoNamespace':True,  
                            'namespace':'MC',
                               'prefix':'', 
                               'subfix':'_MC', 
                              'gridCmd':'Reference_HIK' 
                },

            {'index':4,         'label':'Pose',          
                             'rootpath':'E:/Assets/Pose',            
                            'startPath':'E:/Assets/Pose/Body',                 
                        'autoNamespace':True,  
                            'namespace':'POS',     
                               'prefix':'', 
                               'subfix':'',    
                              'gridCmd':'Reference' 
                }
            
            ]

        #self._tabData = _homeData
        self._tabData = _aiwData
        # 초기값
        self._rootPath  =           self._tabData[0]['rootpath']
        self._startPath =           self._tabData[0]['startPath']
        self._autoNamespace =       self._tabData[0]['autoNamespace']
        self._namespace =           self._tabData[0]['namespace']        

        # 모듈 인스턴스
        self._Tab  = assetTab(       '_Tab', command= '_asset.callBack_tab' , tabData =self._tabData)
        self._Tree = dirTree (      '_Tree', command= '_asset.callBack_tree', rootPath=self._rootPath, startPath=self._startPath )
        self._Grid = glidLister(    '_Grid', command= '_asset.Reference',     path=self._startPath )
        self._NS   = namespaceEditor( '_NS', command= '_asset.callBack_namespace', namespace=[self._namespace])

        # 윈도우 확인
        self._window = 'AssetWindow'
        if cmds.window(self._window, q=True, exists=True): cmds.deleteUI(self._window)

        # 윈도우 시작
        cmds.window(self._window)
        _form = cmds.formLayout()

        _tab = self._Tab.Module()

        # 상단 툴바
        _toolBar = cmds.rowLayout( numberOfColumns=3, adjustableColumn=1)

        self._NS.Module()
        self._UI_toolsParent=cmds.columnLayout(adj=1)
        # 교체되는 부분 (시작)
        self._UI_toolsChild=cmds.rowLayout(nc=1)
        cmds.text(l=' ')
        cmds.setParent('..')
        # 교체되는 부분 (끝)
        cmds.setParent('..')

        self._Grid.UI_iconTools()
        cmds.setParent('..')

        # 내용
        _pane = cmds.paneLayout( configuration='vertical2', staticWidthPane=1, paneSize=[1, 20, 100] )
        self._Tree.Module()
        self._Grid.Module()
        cmds.setParent('..')

        # 조정
        cmds.formLayout(
            _form, 
            edit=True, 

            attachForm=[
                (_tab, 'top', 0),
                (_tab, 'left', 0),
                (_tab, 'right', 0),

                (_toolBar, 'left', 0),
                (_toolBar, 'right', 0),

                (_pane, 'left', 0),
                (_pane, 'right', 0),
                (_pane, 'bottom', 0)
                ],

            attachControl=[
            
                (_toolBar, 'top', 0, _tab),
                (_pane, 'top', 0, _toolBar)
                ],

            attachNone=[
                (_toolBar, 'bottom'),
                (_tab, 'bottom')
                ]
            )

        # 윈도우 오픈
        cmds.showWindow(self._window)
    
    # _Grid Cmd : Call Back Commands
    def Reference(self, *args):
        _sel = cmds.ls(sl=True)
        #print 'call : Reference(self, *args)'
        self._currentFile   = self._Grid.getCurrentFile()
        self._referenceNode = self._NS.getReferenceNode()

        for _namespace in self._NS.getNamespace():

            _referenceNode = ''
            _namespaceObj = cmds.ls( _namespace+":*" )
            if _namespaceObj:
                if cmds.referenceQuery( _namespaceObj[0], isNodeReferenced=True ):
                    _referenceNode = cmds.referenceQuery( _namespaceObj[0], referenceNode=True)

            if cmds.objExists(_referenceNode) and cmds.nodeType(_referenceNode)=='reference':
                # 현제 레퍼런스 파일 갱샌
                cmds.file( self._currentFile , loadReference=_referenceNode, options= 'v=0;')

            else:
                # 레퍼런스 파일 새로 생성
                cmds.file( 
                        self._currentFile,
                        reference=True,
                        namespace= _namespace,
                        loadReferenceDepth='all', 
                        sharedNodes='shadingNetworks',
                        ignoreVersion=True,
                        mergeNamespacesOnClash=False,
                        options= 'v=0;'
                        )

        if _sel:
            cmds.select(_sel)
    
    def Reference_HIK(self, *args):
        _sel = cmds.ls(sl=True)

        self._currentFile   = self._Grid.getCurrentFile()
        self._referenceNode = self._NS.getReferenceNode()

        for _namespace in self._NS.getNamespace():

            _referenceNode = ''
            _namespaceObj = cmds.ls( _namespace+":*" )
            if _namespaceObj:
                if cmds.referenceQuery( _namespaceObj[0], isNodeReferenced=True ):
                    _referenceNode = cmds.referenceQuery( _namespaceObj[0], referenceNode=True)

            if cmds.objExists(_referenceNode) and cmds.nodeType(_referenceNode)=='reference':
                # 현제 레퍼런스 파일 갱샌
                cmds.file( self._currentFile , loadReference=_referenceNode, options= 'v=0;')

            else:
                # 레퍼런스 파일 새로 생성
                cmds.file( 
                        self._currentFile,
                        reference=True,
                        namespace= _namespace,
                        loadReferenceDepth='all', 
                        sharedNodes='shadingNetworks',
                        ignoreVersion=True,
                        mergeNamespacesOnClash=False,
                        options= 'v=0;'
                        )

            # HIK 자동 연결
            if _namespace[-3:]=='_MC':
                _targetNs = _namespace[:-3]
                _sourceNs = _namespace

                _ls = cmds.ls( _targetNs+":*", type="HIKCharacterNode");
                _HIK_target = _ls[0]

                _ls = cmds.ls( _sourceNs+":*", type="HIKCharacterNode");
                _HIK_source = _ls[0]

                print _sourceNs, '-->',  _targetNs
                print _HIK_source, '-->', _HIK_target

                HIK_Tools.setCharacterInput(_HIK_target,_HIK_source, sourceHide=True )
                
        if _sel:
            cmds.select(_sel)

        if self._autoSetPlaybackRangeToEnabledClips:
            if cmds.ls(type='animClip'):
                mel.eval('setPlaybackRangeToEnabledClips')
            else:
                mel.eval('setPlaybackRangeToMinMax')
    
    # _Tab Cmd : 각 어셋 특성에 맞는 명령어 전달
    def callBack_tab(self, *args):
        _index         = args[0]['index']
        _label         = args[0]['label']
        _rootpath      = args[0]['rootpath']
        _startPath     = args[0]['startPath']
        _autoNamespace = args[0]['autoNamespace']
        _namespace     = args[0]['namespace']
        _prefix        = args[0]['prefix']
        _subfix        = args[0]['subfix']
        _gridCmd       = self.getInstance()+'.'+args[0]['gridCmd']    # 각탭마다 해당 Asset에 맞는 명령어를 전달

        self._Tree.setPath(_rootpath,_startPath)

        self._Grid.setPath(_startPath)
        self._Grid.setCommand(_gridCmd)
        
        self._NS.setDefaultNamespace(_namespace)
        self._NS.setNamespace(_namespace)
        self._NS.setPrefix(_prefix)
        self._NS.setSubfix(_subfix)
        #self._NS.setAutoNamespace(_autoNamespace)
        self._NS.updateUI()

        self.UI_changeTools(_index)
        
        if False:
            print '  command:',self.getInstance()+'.callBack_tab(%s)'%args[0]
            print '    index:',_index
            print '    label:',_label
            print ' rootpath:',_rootpath
            print 'startPath:',_startPath
            print 'namespace:',_namespace
       
    # _Tree Cmd : 선택한 디렉토리의 내용을 _Grid에 뿌려줌
    def callBack_tree(self, *args):
        self._startPath = args[0]
        self._Grid.setPath(self._startPath)

        if False:
            print '  command:',self.getInstance()+'.callBack_tree(\'%s\')'%args[0]
            print 'startPath:',args[0]
            
    # _NS Cmd : 네임스페이스가 바뀔때마다 해당 내용을 가져옴
    def callBack_namespace(self, *args):
        self._namespace = self._NS.getNamespace()
        self._refNode   = self._NS.getReferenceNode()
        self._refFile   = self._NS.getReferenceFile()

        if False:
            print self.getInstance()+'.callBack_namespace:'
            print '    reference Namespace :', self._NS.getNamespace()
            print '         reference Node :', self._NS.getReferenceNode()
            print '         reference File :', self._NS.getReferenceFile()
    
    def UI_changeTools(self,*args):
        if cmds.rowLayout(self._UI_toolsChild, q=1, exists=True): cmds.deleteUI(self._UI_toolsChild)

        if args:
            if args[0] in [0,1,3]:
                self._UI_toolsChild=cmds.rowLayout(nc=2,p=self._UI_toolsParent)
                #cmds.symbolButton( image=self._iconPath+'humanIK_CharCtrl_20x20.png', c=self.UI_btnCmd_openHikWindow )
                cmds.symbolButton( image=self._iconPath+'humanIK_CharCtrl.png', c=self.UI_btnCmd_openHikWindow )
                cmds.setParent('..')

            elif args[0] in [2]: # Motion Capture
                self._UI_toolsChild=cmds.rowLayout(nc=3,p=self._UI_toolsParent)                
                cmds.symbolButton( image=self._iconPath+'humanIK_CharCtrl.png', c=self.UI_btnCmd_openHikWindow )
                cmds.symbolButton( image='cameraAim.png' )
                cmds.popupMenu( button=1 )
                cmds.menuItem( l='Hip Constraint Type', c= pyMel.Callback( HipsFallowCam, 0 ) )
                cmds.menuItem( l='Hip Fallow type',     c= pyMel.Callback( HipsFallowCam, 1 ) )
                self._UI_autoRange = cmds.symbolButton( image=self._iconPath+'autoRange_%d.png'%int(self._autoSetPlaybackRangeToEnabledClips), c=self.setAutoRange )
                cmds.setParent('..')
        else :
            self._UI_toolsChild=cmds.rowLayout(nc=1,p=self._UI_toolsParent)
            cmds.text(l=' ')
            cmds.setParent('..')
    
    def UI_btnCmd_openHikWindow(self,*args):
        _mel  = u'// --------- HIKCharacterControlsTool : caracter: optionMenuGrp 자동 선택 (namespace가 있는 캐릭터에만 적용됨) -------------------\n'
        _mel += 'HIKCharacterControlsTool();\n'
        _mel += '\n'
        _mel += 'global proc HIK_tool_AutoSelect_Character() {\n'
        _mel += '    global string $gHIKCurrentCharacter;\n'
        _mel += '\n'
        _mel += u'    // 선택한 오브젝트의\n'
        _mel += '    string $sel[] = `ls -sl`;\n'
        _mel += '    if (size($sel)==0) return;\n'
        _mel += '\n'
        _mel += u'    // 네임스페이스를 알아오고\n'
        _mel += '    string $buffer[];\n'
        _mel += '    tokenize $sel[0] ":" $buffer;\n'
        _mel += '    if (!size($buffer)>1) return;\n'
        _mel += '    string $namespace = $buffer[0];\n'
        _mel += '\n'
        _mel += u'    // 네임스페이스안에 있는 HIKCharacterNode를 알아오고.\n'
        _mel += '    $sel = `ls -type "HIKCharacterNode" ($namespace+":*")`;\n'
        _mel += '    if (size($sel)==0) return;\n'
        _mel += '    $HIKCharacterNode = $sel[0];\n'
        _mel += '\n'
        _mel += '    $gHIKCurrentCharacter = $HIKCharacterNode;\n'
        _mel += '    hikUpdateCurrentCharacterFromScene();\n'
        _mel += '}\n'
        _mel += '\n'
        _mel += '// scriptJob Kill\n'
        _mel += '{\n'
        _mel += '    string $listJobs[] = `scriptJob -listJobs`;\n'
        _mel += '    for ($i=0; $i<size($listJobs); $i++) {\n'
        _mel += '        if (`gmatch $listJobs[$i] "*HIK_tool_AutoSelect_Character*"`) {\n'
        _mel += '            string $buffer[];\n'
        _mel += '            tokenize $listJobs[$i] ":" $buffer;\n'
        _mel += '            int $jobNum = int($buffer[0]);\n'
        _mel += '\n'
        _mel += '            scriptJob -kill $jobNum -force;\n'
        _mel += '            //print ("scriptJob ("+$jobNum+") Killed ! \\n");\n'
        _mel += '        }\n'
        _mel += '    }\n'
        _mel += '}\n'
        _mel += '\n'
        _mel += u'// 스크롤 레이아웃에 스크립트 잡 내용 붙임\n'
        _mel += 'if (`dockControl -q -exists "hikCharacterControlsDock"`)\n'
        _mel += '    scriptJob -parent "hikCharacterControlsDock" -event "SelectionChanged" "HIK_tool_AutoSelect_Character";\n'
        _mel += '\n'
        _mel += u'// -------------------------------------------------------------------------------------------\n'
        print _mel
        #mel.eval( _mel )
    
    # setDatas
    def setInstance(self, _instance):
        self._instance = _instance
    
    def getInstance(self):
        return self._instance

    def setAutoRange(self, *args):
        _val = not self._autoSetPlaybackRangeToEnabledClips
        self._autoSetPlaybackRangeToEnabledClips = _val
        cmds.symbolButton( self._UI_autoRange, e=True, image=self._iconPath+'autoRange_%d.png'%int(self._autoSetPlaybackRangeToEnabledClips) )
 
# 엉덩이 쫓아가는 카메라 생성
def HipsFallowCam(_mode):
    _sel = cmds.ls(sl=True)
    if not _sel:
        print u'뭐라도 좀 선택하세요.'

    _namespace = _sel[0].split(':')[0]+':'
    
    _hips = _namespace+'Hips'
    if cmds.objExists(_namespace+'HipsTranslation'):
        _hips = _namespace+'HipsTranslation'
    
    if not cmds.objExists(_hips):
        print u'Hips Joint가 필요합니다.'
        return
    
    if not cmds.objExists('persp'):
        print u'persp 카메라가 없습니다. 여기서 중단됩니다.'

    _cam = cmds.camera( name=_hips+'_Fallow_cam#')
    _tmp = cmds.parentConstraint('persp',_cam[0])
    cmds.delete(_tmp)

    cmds.select(cl=True)
    _grp = cmds.group(name=_hips+'_Fallow#',em=True) 
    if _mode==0:

        _const = cmds.pointConstraint(_hips, _grp, skip='y')
        cmds.parent(_cam[0], _grp)
    
    else:        
        _loc = cmds.spaceLocator(name='fallowTarget#')
        cmds.pointConstraint( _hips, _loc[0])
        _target = _loc[0]

        _fallower = cmds.group(name=_hips+'_Fallow_CamGrp#',em=True) 
        cmds.parent(_target, _fallower, _grp)

        _tmp = cmds.pointConstraint(_target,_fallower)
        cmds.delete(_tmp)

        cmds.parent(_cam[0], _fallower)

        cmds.addAttr( _fallower, ln='startFrame'         ,at='double'                ,dv=1   ,keyable=True )
        cmds.addAttr( _fallower, ln='multiplyTranslate'  ,at='double'  ,min=0 ,max=1 ,dv=0.1 ,keyable=True )
        cmds.addAttr( _fallower, ln='multiplyRotate'     ,at='double'  ,min=0 ,max=1 ,dv=0.5 ,keyable=True )
        cmds.addAttr( _fallower, ln='multiplyScale'      ,at='double'  ,min=0 ,max=1 ,dv=0.5 ,keyable=True )

        _expCmd  = '// inintialize --------------------------------------------\n'
        _expCmd += '//\n'
        _expCmd += 'startFrame = `playbackOptions -q -min`;\n'
        _expCmd += '\n'
        _expCmd += 'if ( frame <= '+_fallower+'.startFrame)\n'
        _expCmd += '{ \n'
        _expCmd += '    '+_fallower+'.tx = '+_target+'.tx;\n'
        _expCmd += '    '+_fallower+'.ty = '+_target+'.ty;\n'
        _expCmd += '    '+_fallower+'.tz = '+_target+'.tz;\n'
        _expCmd += '\n'
        _expCmd += '    '+_fallower+'.rx = '+_target+'.rx;\n'
        _expCmd += '    '+_fallower+'.ry = '+_target+'.ry;\n'
        _expCmd += '    '+_fallower+'.rz = '+_target+'.rz;\n'
        _expCmd += '\n'
        _expCmd += '    '+_fallower+'.sx = '+_target+'.sx;\n'
        _expCmd += '    '+_fallower+'.sy = '+_target+'.sy;\n'
        _expCmd += '    '+_fallower+'.sz = '+_target+'.sz;\n'
        _expCmd += '}\n'
        _expCmd += '\n'
        _expCmd += 'float $multTranslate = '+_fallower+'.multiplyTranslate;\n'
        _expCmd += 'float $multRotate = '+_fallower+'.multiplyRotate;\n'
        _expCmd += 'float $multScale = '+_fallower+'.multiplyScale;\n'
        _expCmd += '\n'
        _expCmd += '// float to Vector ----------------------------------------\n'
        _expCmd += '//\n'
        _expCmd += 'float $tgt_tx = '+_target+'.tx;\n'
        _expCmd += 'float $tgt_ty = '+_target+'.ty;\n'
        _expCmd += 'float $tgt_tz = '+_target+'.tz;\n'
        _expCmd += 'float $tgt_rx = '+_target+'.rx;\n'
        _expCmd += 'float $tgt_ry = '+_target+'.ry;\n'
        _expCmd += 'float $tgt_rz = '+_target+'.rz;\n'
        _expCmd += 'float $tgt_sx = '+_target+'.sx;\n'
        _expCmd += 'float $tgt_sy = '+_target+'.sy;\n'
        _expCmd += 'float $tgt_sz = '+_target+'.sz;\n'
        _expCmd += ' \n'
        _expCmd += 'float $src_tx = '+_fallower+'.tx;\n'
        _expCmd += 'float $src_ty = '+_fallower+'.ty;\n'
        _expCmd += 'float $src_tz = '+_fallower+'.tz;\n'
        _expCmd += 'float $src_rx = '+_fallower+'.rx;\n'
        _expCmd += 'float $src_ry = '+_fallower+'.ry;\n'
        _expCmd += 'float $src_rz = '+_fallower+'.rz;\n'
        _expCmd += 'float $src_sx = '+_fallower+'.sx;\n'
        _expCmd += 'float $src_sy = '+_fallower+'.sy;\n'
        _expCmd += 'float $src_sz = '+_fallower+'.sz;\n'
        _expCmd += '\n'
        _expCmd += 'vector $tgt_tr = <<$tgt_tx,$tgt_ty,$tgt_tz>>;\n'
        _expCmd += 'vector $tgt_rt = <<$tgt_rx,$tgt_ry,$tgt_rz>>;\n'
        _expCmd += 'vector $tgt_sc = <<$tgt_sx,$tgt_sy,$tgt_sz>>;\n'
        _expCmd += '\n'
        _expCmd += 'vector $src_tr = <<$src_tx,$src_ty,$src_tz>>;\n'
        _expCmd += 'vector $src_rt = <<$src_rx,$src_ry,$src_rz>>;\n'
        _expCmd += 'vector $src_sc = <<$src_sx,$src_sy,$src_sz>>;\n'
        _expCmd += '\n'
        _expCmd += '// calcurate Gap ------------------------------------------\n'
        _expCmd += '//\n'
        _expCmd += 'vector $translateGap    = $tgt_tr - $src_tr;\n'
        _expCmd += 'vector $rotateGap       = $tgt_rt - $src_rt;\n'
        _expCmd += 'vector $scaleGap        = $tgt_sc - $src_sc;\n'
        _expCmd += '\n'
        _expCmd += '// calcurate result ---------------------------------------\n'
        _expCmd += '//\n'
        _expCmd += 'vector $result_tr = <<\n'
        _expCmd += '    $translateGap.x * $multTranslate,\n'
        _expCmd += '    $translateGap.y * $multTranslate,\n'
        _expCmd += '    $translateGap.z * $multTranslate\n'
        _expCmd += '    >>;\n'
        _expCmd += '\n'
        _expCmd += 'vector $result_rt = <<\n'
        _expCmd += '    $rotateGap.x * $multRotate,\n'
        _expCmd += '    $rotateGap.y * $multRotate,\n'
        _expCmd += '    $rotateGap.z * $multRotate\n'
        _expCmd += '    >>;\n'
        _expCmd += '\n'
        _expCmd += 'vector $result_sc = <<\n'
        _expCmd += '    $scaleGap.x * $multScale,\n'
        _expCmd += '    $scaleGap.y * $multScale,\n'
        _expCmd += '    $scaleGap.z * $multScale\n'
        _expCmd += '    >>;\n'
        _expCmd += '\n'
        _expCmd += '// assign result ------------------------------------------\n'
        _expCmd += '//\n'
        _expCmd += ''+_fallower+'.tx += $result_tr.x;\n'
        _expCmd += ''+_fallower+'.ty += $result_tr.y;\n'
        _expCmd += ''+_fallower+'.tz += $result_tr.z;\n'
        _expCmd += ''+_fallower+'.rx += $result_rt.x;\n'
        _expCmd += ''+_fallower+'.ry += $result_rt.y;\n'
        _expCmd += ''+_fallower+'.rz += $result_rt.z;\n'
        _expCmd += ''+_fallower+'.sx += $result_sc.x;\n'
        _expCmd += ''+_fallower+'.sy += $result_sc.y;\n'
        _expCmd += ''+_fallower+'.sz += $result_sc.z;\n'
        cmds.expression( s=_expCmd, o=_fallower, ae=1, uc='all')        

def SkinningToll_skinMesh_to_manyMesh(_skinMesh, _hignMeshGrp):
    from maya import cmds

    # joint
    cmds.select('Hips',hi=True)
    _joint = cmds.ls(sl=True)

    # skinMesh
    #_skinMesh = 'SkinBody'

    # mesh
    #_hignMeshGrp = 'Mesh_High'
    cmds.select(_hignMeshGrp,hi=True)
    _meshShape = cmds.ls(sl=True, type='mesh')
    cmds.select(_meshShape)
    _mesh= cmds.pickWalk(d='up')

    # bindSkin
    #cmds.select(_joint,_mesh)

    # copy
    for _item in _mesh:
        cmds.select(_skinMesh,_item)
        cmds.copySkinWeights(noMirror=True, surfaceAssociation='closestPoint', influenceAssociation=['closestJoint','closestBone','oneToOne'], normalize=True)