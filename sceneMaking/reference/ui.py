# -*- coding:utf-8 -*-
'''
2014. 1. 10 : optionWindow 클래스를 사용하여 ui 교체 
2013. 6. 7. : Create

@author: Kuyho Choi

많은 양의 Reference작업을 도와줌.
Scene에서 Reference Node(들)의 일부를 선택하고,
아래 원하는 작업을 실행.

'''
from functools import partial
import os, re
import pymel.core as pm
import maya.cmds as cmds

import alfredToolsMenu.ui.optionWindow as optWin # v:2014.01.10
reload (optWin)

import Reference.commands as Ref


anno  = u'''많은 양의 Reference작업을 도와줌.

Scene에서 Reference Node(들)의 일부를 선택하고,
아래 원하는 작업을 실행.'''

def showWindow():
    UI.showWindow()

class UI(optWin.Window):
    def __init__(self):
        # 제목
        self.WIG['title'] = 'Reference Editor 2'
        
        # 아이콘 파일(있을 경우)
        self.OPT['icon']           = self.getIcon('shelf_referenceTools.png')
        self.OPT['useTitleBar']    = True
        self.OPT['useCommonBtn']   = False
        #self.OPT['commonBtnLabel'] = 'Create'
        self.OPT['helpURL']        = 'http://alfredcgtechblog.blogspot.kr/2014/01/reference-editor-2.html'
        self.OPT['annotation']     = anno       
        self.OPT['dock']           = False

        # optionVar로 저장될 변수들
        self.startPath = optWin.OptionVar('alfred_Ref__startPath', self.getScenePath() )

    def getScenePath(self):
        return ( pm.workspace( q=True, rd=True ) + pm.workspace( 'scene', q=True, fileRuleEntry=True ) ).replace('/','\\')
    
    def setDefault(self):
        self.startPath.set( self.getScenePath() )        
        optWin.Window.setDefault(self)
        
    def uiOptions(self):
        with pm.tabLayout(tv=False, imw=5, imh=5 ) as layout:  
            with pm.columnLayout(adj=1):
                self.navFieldGrp( 'navFieldGrp', label='Work Path : ', text=self.startPath.get(), optVar=self.startPath, fileMode='dir' )
             
                pm.separator(style='in', h=8)       
                with pm.rowLayout(nc=7):
                    pm.text(l=' Work : ', al='right', w=140 )   
                    pm.button(l='Create',      c=partial( self.btnCmd, 'create'), w=50 )
                    pm.button(l='Reload',      c=partial( self.btnCmd, 'reload'), w=50 )    
                    pm.button(l='Replace',     c=partial( self.btnCmd, 'replace'), w=50 )
                    pm.button(l='Import',      c=partial( self.btnCmd, 'import'), w=50 )
                    pm.button(l='Remove',      c=partial( self.btnCmd, 'remove'), w=50 )    
            
                with pm.rowLayout(nc=7):
                    pm.text(l='',al='right', w=140 )    
                    pm.button(l='Print Reference State', c=partial( self.btnCmd, 'state'), w=128 )

                pm.separator(style='in', h=8)                
                with pm.rowLayout(nc=7):
                    pm.text(l='Maya Editor : ',al='right', w=140 )    
                    pm.button(l='Reference Editor',  c=pm.Callback( pm.mel.ReferenceEditor ), w=128 )
                    pm.button(l='Namespace Editor',  c=pm.Callback( pm.mel.NamespaceEditor ), w=128 )

        return layout
    
    def btnCmd(self, *args):    
        if   args[0]=='create':        
            # startPath        = 'X:/2012_CounterStrike2_V2/3D_project/Share/scenes/character'               # 시작 디렉토리
            fileFilter = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"    # 선택 가능한 확장자

            result = pm.fileDialog2( 
                fileFilter        = fileFilter,                   # 선택 가능한 확장자
                dialogStyle       = 1,                                 # 1: 윈도우 스타일, 2: 마야 스타일
                startingDirectory = self.startPath.get(),                   # 시작 디렉토리
                fileMode          = 1                                     # 파일 하나만 선택 하는 모드
                )
                
            if result:    
                self.startPath.set( os.path.dirname(result[0]) )

                res = pm.promptDialog( m='namespace : ', text= Ref.getBasename( result[0] )  )
                
                if res == 'Confirm':
                    print 
                    ns = pm.promptDialog( q=True, text=True)    
                    Ref.refCreate( result[0], namespace=ns )                       # 레퍼런스 생성
                           
        elif args[0]=='reload':
            sel = cmds.ls(sl=True)
            if sel:
                RNs=[]
                for obj in sel:
                    RN = Ref.getReferenceNode( obj )
                    if RN:
                        RNs.append( RN )             # 레퍼런스 노드 이름 알아옴.

                RNs = list(set(RNs))

                if RNs and pm.confirmDialog( m=u' %s\n\n위 레퍼런스(들)를 갱신하겠습니까?'%RNs) == "Confirm":
                    Ref.refReload( RNs  )                                             # 레퍼런스 제거
    
        elif args[0]=='import':
            sel = cmds.ls(sl=True)
            if sel:
                RNs=[]
                for obj in sel:
                    RN = Ref.getReferenceNode( obj )
                    if RN:
                        RNs.append( RN )             # 레퍼런스 노드 이름 알아옴.

                RNs = list(set(RNs))

                if RNs and pm.confirmDialog( m=u' %s\n\n위 레퍼런스(들)를 import 하겠습니까?'%RNs) == "Confirm":
                    Ref.refImport( RNs  )                                             # 레퍼런스 제거
    
        elif args[0]=='replace':         
            # 선택한 오브젝트관련 레퍼런스 파일을, 지정한 파일로 교체
            #
            #
            #startPath        = 'X:/2012_CounterStrike2_V2/3D_project/Share/scenes/character'                       # 시작 디렉토리
            fileFilter = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"    # 선택 가능한 확장자
            sel = cmds.ls(sl=True)
            if sel:
                RNs=[]
                for obj in sel:
                    RN = Ref.getReferenceNode( obj )
                    if RN:
                        RNs.append( RN )             # 레퍼런스 노드 이름 알아옴.

                RNs = list(set(RNs))

                result = pm.fileDialog2( 
                    fileFilter        = fileFilter,                   # 선택 가능한 확장자
                    dialogStyle       = 1,                                 # 1: 윈도우 스타일, 2: 마야 스타일
                    startingDirectory = self.startPath.get(),                   # 시작 디렉토리
                    fileMode          = 1                                     # 파일 하나만 선택 하는 모드
                    )
                    
                if result: 
                    self.startPath.set( os.path.dirname(result[0]).replace('/','\\') )

                    Ref.refReplace( RNs, result[0] )                     # 레퍼런스 교체
                    pm.refresh()
                    pm.confirmDialog( message=u'완료 되었습니다.' )
                else:
                    pm.confirmDialog( message=u'중지 되었습니다.' )
    
        elif args[0]=='remove':         
            RNs = Ref.getReferenceNode( cmds.ls(sl=True) )                    # 선택한 물체에서 레퍼런스 노드 알아옴
            if RNs and pm.confirmDialog( m=u' %s\n\n위 레퍼런스(들)를 삭제하시겠습니까?' % RNs) == "Confirm":
                Ref.refRemove( RNs  )                                         # 레퍼런스 제거
        
        elif args[0]=='browse':
            result = pm.fileDialog2(                            # 디렉토리 선택 모드
                # fileFilter= "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)", # 선택 가능한 확장자
                dialogStyle       = 1,                                  # 1: 윈도우 스타일, 2: 마야 스타일
                startingDirectory = self.startPath.get(),                       # 시작 디렉토리
                fileMode          = 3                                     # 0: 존재하거나 존재하지 않든 상관 없음 1: 한개의 존재하는 파일, 2: 디렉토리 명( 디렉토리와 파일 둘다 보임), 3: 디렉토리 명( 디렉토리만 보임), 4: 하나 이상의 존재하는 파일
                )
            
            if result:
                self.startPath.set(result[0])
    
        elif args[0]=='state':          
            sel  = cmds.ls(sl=True)
            if sel:
                RNs=[]
                for obj in sel:
                    RN = Ref.getReferenceNode( obj )
                    if RN:
                        RNs.append( RN )             # 레퍼런스 노드 이름 알아옴.

                RNs = list(set(RNs))

                if not RNs:
                    print '# -----------------------------------------------------------------------------------------------'
                    print '# '
                    print u'# 레퍼런스가 아닙니다.'
                    print '# '
                    print '# -----------------------------------------------------------------------------------------------'
                    return

                for RN in RNs:
                    _File = Ref.getFile( RN )                          # 레퍼런스 노드 관련된 이름 알아옴
                    _ns   = pm.referenceQuery( RN, namespace=True )                          # 레퍼런스 노드 관련된 이름 알아옴

                    print '# -----------------------------------------------------------------------------------------------'
                    print '# refNode   : %s'%RN                                    # 해당 파일 오픈 스크립트 출력
                    print '# namespace : %s'%_ns                                    # 해당 파일 오픈 스크립트 출력
                    print '# command   : pm.openFile( "%s", f=True )'%_File      # 해당 파일 오픈 스크립트 출력
                    print '# filePath  : %s'%_File.replace('/','\\')                  # 해당 파일 오픈 스크립트 출력
                    print '# -----------------------------------------------------------------------------------------------'