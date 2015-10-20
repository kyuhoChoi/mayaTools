# -*- coding:utf-8 -*-
import os,glob 
import fnmatch 
import maya.cmds as cmds
import maya.mel as mel

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

    _defaultNamespace = 'initNamespace'
    _autoNamespace = True
    _namespace = []
    _refFile = []
    _refNode = []
    _debug = False

    # importOption
    _removeNamespace = 0

    #------------------------------------------------------------------
    #
    # namespace
    #
    #------------------------------------------------------------------  
    # namespace 관련
    def setNamespace(self, *args):
        if args:
            if type(args[0]) == list:
                self._namespace = args[0]
            if type(args[0]) == str:
                self._namespace = [args[0]]
                
        

        _namespaceTxt = ''
        for _txt in self._namespace: _namespaceTxt += _txt+', '
        _namespaceTxt = _namespaceTxt[:-2]

        self.setAutoNamespace(0)
        cmds.textField( self._UI_TFD_namespace, e=True, text=_namespaceTxt)

        self.updateUI()
   
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

    def getReferenceNode(self):
        return self._refNode
    
    def getReferenceFile(self):
        return self._refFile
    
    def setDebug(self,*args):
        self._debug=args[0]
        self.updateUI()
    
    def updateUI(self,*args):
        # 옵션
                _reformText = False
                _fromTextField = ''
        #--------------------------------------------------
        #
        # 입력 자료 분석
        #
        #--------------------------------------------------
                self._selObj = []
                self._refNode= []
                self._refFile= []
                self._namespace= []

            #--------------------------------------------------
            #
            # 선택한 오브젝트로부터 데이터 입력
            #
            #--------------------------------------------------
                if self._autoNamespace:
                    # 선택한 오브젝트
                    _sel = cmds.ls( sl=True )
                    
                    for _node in _sel:
                        if cmds.referenceQuery( _node, isNodeReferenced=True ) or cmds.nodeType(_node)=='reference':
                            # 레퍼런스 노드 알아옴
                            _referenceNode = cmds.referenceQuery( _node, referenceNode=True)
                            
                            # 중복데이터 삭제
                            if _referenceNode in self._refNode:
                                continue
                            
                            # 자료 입력
                            self._selObj.append( _node )
                            self._refNode.append(_referenceNode)
                            self._refFile.append(   cmds.referenceQuery( _referenceNode, filename=True)       )
                            self._namespace.append( cmds.referenceQuery( _referenceNode, namespace=True )[1:] ) # :name 에서 ":" 삭제
            #--------------------------------------------------
            #
            # 텍스트 필드에 입력된 데이터 처리
            #
            #--------------------------------------------------
                else:
                    # 텍스트 필드에 입력된 내용을 대문자로 바꿔서 입력
                    _fromTextField = cmds.textField( self._UI_TFD_namespace, q=True, text=True)
                    
                    # 입력된 네임스페이스들을 나눠서 _namespace에 입력
                    _inputNamespace = [_item.strip(',') for _item in _fromTextField.split(' ')]

                    # 씬안에 있는 네임스페이스들검색
                    _namespaceList     = [_nsList         for _nsList in cmds.namespaceInfo( listOnlyNamespaces=True )]
                    _namespaceList_low = [_nsList.lower() for _nsList in _namespaceList]

                    _namespace = []
                    # 와일드카드 검색
                    for _ns in _inputNamespace:
                        _namespace += fnmatch.filter( _namespaceList, _ns)
                    
                    # 텍스트필드에 입력된 namespace를 분석해서 다시 정리함.
                    for _ns in _namespace:
                        # 빈 텍스트면 통과
                        if not _ns:
                            continue
                        
                        # _namespace로 시작하는 오브젝트 선택
                        _sel = cmds.ls( _ns+':*')

                        # 선택된 오브젝트가 없으면 통과
                        if not _sel:
                            continue

                        # 첫번째 선택된 오브젝트를 _refObj에 입력
                        _refObj = _sel[0]

                        # 레퍼런스 노드가 아니면 통과
                        if not cmds.referenceQuery( _refObj, isNodeReferenced=True ):
                            continue

                        # _refObj의 reference node를 _reference에 입력
                        _reference = cmds.referenceQuery( _refObj, referenceNode=True)

                        self._selObj.append(    _refObj)
                        self._refNode.append(   _reference)
                        self._refFile.append(   cmds.referenceQuery( _reference, filename=True)       )
                        self._namespace.append( cmds.referenceQuery( _reference, namespace=True )[1:] ) # :name 에서 ":" 삭제

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
                for _ns in self._namespace:
                    _textField += _ns +', '
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
        
    # auto namespace 관련
    def toggleAutoNamespace(self, *args):
        _autoNamespace = (self._autoNamespace+1)%2
        self.setAutoNamespace( _autoNamespace )

    def setAutoNamespace(self, *args):
        # 멤버변수 조정
        self._autoNamespace = args[0]

        # UI 조정
        self.updateUI()
    
    def getAutoNamespace(self, *args):
        return self._autoNamespace
    
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
            _list += _reference+'\n'

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
        print self._removeNamespace
    #------------------------------------------------------------------
    #
    # UI 모듈
    #
    #------------------------------------------------------------------  
    def Module(self):
        cmds.columnLayout( adj=True )

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
        cmds.rowLayout( numberOfColumns=4 , adjustableColumn=2)
        _UI_BTN_visToggle = cmds.symbolButton( image=self._icon_bar )

        # rowLayout2
        self._UI_RCL_nsGrp     = cmds.rowLayout( numberOfColumns=6, adjustableColumn=3 )

        # autonamespace
        if self._autoNamespace: 
            self._icon_autoNamespace = self._icon_autoNamespace_1
        self._UI_BTN_autoNamespace = cmds.symbolButton( image=self._icon_autoNamespace, c=self.toggleAutoNamespace)
        
        # namespace
        cmds.text(label = 'namespace : ')
        cmds.popupMenu( button=3 )
        cmds.menuItem( l='Open Reference Editor', c='import maya.mel;maya.mel.eval(\'ReferenceEditor\')')
        cmds.menuItem( l='Open Namespace Editor', c='import maya.mel;maya.mel.eval(\'namespaceEditor\')')
        
        # rowLayout3
        self._UI_TFD_namespaceGrp    = cmds.rowLayout( numberOfColumns=3 , adjustableColumn=1)
        self._UI_TFD_namespace       = cmds.textField( editable=not self._autoNamespace, width = 40, cc=self.updateUI)
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

        # add item
        cmds.symbolButton( image=self._icon_bar )
        cmds.symbolButton( image=self._iconPath+'addItem.png')
        
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
        _window = 'namespaceEditor2'
        if cmds.window(_window, q=1, exists=1): cmds.deleteUI(_window)

        cmds.window(_window)
        self.Module()
        cmds.showWindow(_window)
