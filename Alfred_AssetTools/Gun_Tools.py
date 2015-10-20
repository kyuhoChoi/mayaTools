# -*- coding:utf-8 -*-
import maya.cmds as cmds
import maya.mel as mel

#----------------------------------------
#
#     HIK Rigging 도와주는 도구
#
#----------------------------------------
# HIK_Tool : floor Contact 설정: 사용한뒤 로케이터를 지울것
def setFloorContact():
    if cmds.objExists('HIK_floorContact_Rig'):
        print u'HIK_floorContact_Rig가 이미 존재합니다.'
        return

    # 프로퍼티가 하나일경우에만 작동함
    _ls = cmds.ls( type='HIKProperty2State' )
    if not _ls or len(_ls)>1:
        print u'HIKProperty2State 노드가 없거나, 두개이상입니다. 이 스크립트는 HIKProperty2State가 하나일때만 작동합니다.'
        return
    _HIKproperties = _ls[0]

    _ls = cmds.ls( type='HIKCharacterNode' )
    if not _ls or len(_ls)>1:
        print u'HIKCharacterNode 노드가 없거나, 두개이상입니다. 이 스크립트는 HIKCharacterNode가 하나일때만 작동합니다.'
        return
    _HIKCharacterNode = _ls[0]

    _HIK_Foot_Ctrl = _HIKCharacterNode+'_Ctrl_LeftFoot'

    _FootBottomToAnkle = cmds.getAttr( _HIKproperties+'.FootBottomToAnkle')
    _FootBackToAnkle   = cmds.getAttr( _HIKproperties+'.FootBackToAnkle')
    _FootMiddleToAnkle = cmds.getAttr( _HIKproperties+'.FootMiddleToAnkle')
    _FootFrontToMiddle = cmds.getAttr( _HIKproperties+'.FootFrontToMiddle')
    _FootInToAnkle     = cmds.getAttr( _HIKproperties+'.FootInToAnkle')
    _FootOutToAnkle    = cmds.getAttr( _HIKproperties+'.FootOutToAnkle')

    _Ankle  = cmds.spaceLocator(name='HIK_floorContact_Rig') ; _Ankle.append(  cmds.listRelatives(_Ankle[0],  s=True)[0] )
    _Bottom = cmds.spaceLocator(name='Bottom')               ; _Bottom.append( cmds.listRelatives(_Bottom[0], s=True)[0] )
    _Back   = cmds.spaceLocator(name='Back')                 ; _Back.append(   cmds.listRelatives(_Back[0],   s=True)[0] )
    _Middle = cmds.spaceLocator(name='Middle')               ; _Middle.append( cmds.listRelatives(_Middle[0], s=True)[0] )
    _Front  = cmds.spaceLocator(name='Front')                ; _Front.append(  cmds.listRelatives(_Front[0],  s=True)[0] )
    _In     = cmds.spaceLocator(name='In')                   ; _In.append(     cmds.listRelatives(_In[0],     s=True)[0] )
    _Out    = cmds.spaceLocator(name='Out')                  ; _Out.append(    cmds.listRelatives(_Out[0],    s=True)[0] )

    _Back_Offset = cmds.group( _Back[0], name = 'Back_Offset') ; cmds.setAttr( _Back_Offset+".ry", 180)
    _Out_Offset  = cmds.group( _Out[0],  name = 'Back_Offset') ; cmds.setAttr( _Out_Offset+".ry",  180)

    cmds.parent( _Front[0], _Middle[0] )
    cmds.parent( _Middle[0],_Back_Offset,_In[0],_Out_Offset, _Bottom[0] )
    cmds.parent( _Bottom[0], _Ankle[0] )

    cmds.pointConstraint( _HIK_Foot_Ctrl, _Ankle[0])
    cmds.orientConstraint( _HIK_Foot_Ctrl, _Ankle[0], offset=[0,0,180])
    cmds.setAttr( _Bottom[0]+'.ty', _FootBottomToAnkle )
    cmds.setAttr( _Back[0]+'.tz',   _FootBackToAnkle )
    cmds.setAttr( _Middle[0]+'.tz', _FootMiddleToAnkle )
    cmds.setAttr( _Front[0]+'.tz',  _FootFrontToMiddle )
    cmds.setAttr( _In[0]+'.tx',     _FootInToAnkle )
    cmds.setAttr( _Out[0]+'.tx',    _FootOutToAnkle )

    # 연결
    cmds.connectAttr(_Bottom[0]+'.ty', _HIKproperties+'.FootBottomToAnkle')
    cmds.connectAttr(_Back[0]+'.tz',  _HIKproperties+'.FootBackToAnkle')
    cmds.connectAttr(_Middle[0]+'.tz', _HIKproperties+'.FootMiddleToAnkle')
    cmds.connectAttr(_Front[0]+'.tz',  _HIKproperties+'.FootFrontToMiddle')
    cmds.connectAttr(_In[0]+'.tx',     _HIKproperties+'.FootInToAnkle')
    cmds.connectAttr(_Out[0]+'.tx',    _HIKproperties+'.FootOutToAnkle')

    # 정리
    cmds.setAttr( _Ankle[0]+'.tx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Ankle[0]+'.ty', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Ankle[0]+'.tz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Ankle[0]+'.rx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Ankle[0]+'.ry', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Ankle[0]+'.rz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Ankle[0]+'.sx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Ankle[0]+'.sy', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Ankle[0]+'.sz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Ankle[0]+'.v' , lock=True, keyable=False, channelBox=False )

    cmds.setAttr( _Bottom[0]+'.tx', lock=True, keyable=False, channelBox=False )
    #cmds.setAttr( _Bottom[0]+'.ty', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Bottom[0]+'.tz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Bottom[0]+'.rx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Bottom[0]+'.ry', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Bottom[0]+'.rz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Bottom[0]+'.sx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Bottom[0]+'.sy', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Bottom[0]+'.sz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Bottom[0]+'.v' , lock=True, keyable=False, channelBox=False )

    cmds.setAttr( _Middle[0]+'.tx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Middle[0]+'.ty', lock=True, keyable=False, channelBox=False )
    #cmds.setAttr( _Middle[0]+'.tz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Middle[0]+'.rx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Middle[0]+'.ry', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Middle[0]+'.rz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Middle[0]+'.sx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Middle[0]+'.sy', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Middle[0]+'.sz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Middle[0]+'.v' , lock=True, keyable=False, channelBox=False )

    cmds.setAttr( _Front[0]+'.tx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Front[0]+'.ty', lock=True, keyable=False, channelBox=False )
    #cmds.setAttr( _Front[0]+'.tz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Front[0]+'.rx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Front[0]+'.ry', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Front[0]+'.rz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Front[0]+'.sx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Front[0]+'.sy', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Front[0]+'.sz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Front[0]+'.v' , lock=True, keyable=False, channelBox=False )

    cmds.setAttr( _Back[0]+'.tx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Back[0]+'.ty', lock=True, keyable=False, channelBox=False )
    #cmds.setAttr( _Back[0]+'.tz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Back[0]+'.rx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Back[0]+'.ry', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Back[0]+'.rz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Back[0]+'.sx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Back[0]+'.sy', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Back[0]+'.sz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Back[0]+'.v' , lock=True, keyable=False, channelBox=False )

    #cmds.setAttr( _In[0]+'.tx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _In[0]+'.ty', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _In[0]+'.tz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _In[0]+'.rx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _In[0]+'.ry', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _In[0]+'.rz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _In[0]+'.sx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _In[0]+'.sy', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _In[0]+'.sz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _In[0]+'.v' , lock=True, keyable=False, channelBox=False )

    #cmds.setAttr( _Out[0]+'.tx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Out[0]+'.ty', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Out[0]+'.tz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Out[0]+'.rx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Out[0]+'.ry', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Out[0]+'.rz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Out[0]+'.sx', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Out[0]+'.sy', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Out[0]+'.sz', lock=True, keyable=False, channelBox=False )
    cmds.setAttr( _Out[0]+'.v' , lock=True, keyable=False, channelBox=False )

#----------------------------------------
#
#     HIK 조작 도구
#
#----------------------------------------
# HIK 모션캡쳐 파일 연결
def setCharacterInput(_HIK, _HIK_source, **kwargs):
    if not ( cmds.nodeType(_HIK) == 'HIKCharacterNode' and cmds.nodeType(_HIK_source) == 'HIKCharacterNode' ):
        print u'HIKCharacterNode를 입력하세요.'
        return

    # sourceHide
    _sourceHide = False
    if kwargs.get('sourceHide') or kwargs.get('sh'):
        _input = ''

        # 해당 키워드에 해당하는 키값을 받아오고
        if   kwargs.get('sourceHide'): 
            _input = kwargs.get('sourceHide')
        elif kwargs.get('sh'): 
            _input = kwargs.get('sh')

        # 맞으면.. 아래 실행
        _sourceHide = _input

    # 연결
    mel.eval( 'mayaHIKsetCharacterInput( "%s", "%s" );'%(_HIK, _HIK_source) )
    mel.eval( '$gHIKCurrentCharacter = "%s";'%_HIK)
    mel.eval( 'hikUpdateCurrentCharacterFromScene();')

    if _sourceHide:
        # 소스 루트 알아옴.
        _root = getRootParent(_HIK_source)
        cmds.setAttr(_root+'.v',0)

#----------------------------------------
#
#     HIK Pose 도구
#
#----------------------------------------
# handPose Shelf for HIK
def handPose_fromSelect_toShelf():
    _shelfName = 'pose_Hand'
    if not cmds.shelfLayout( _shelfName, q=True, exists=True):
         mel.eval('addNewShelfTab "%s";'%_shelfName)

         _cmd  ='\n'
         _cmd +='import maya.cmds as cmds\n'
         _cmd +='import sys\n'
         _cmd +='\n'
         _cmd +=u'# 파이썬 경로 추가\n'
         _cmd +='_newPath = \'//alfredstorage/Alfred_asset/Maya_Shared_Environment/scripts_Python/Alfred_AssetTools\'\n'
         _cmd +='if not _newPath in sys.path:\n'
         _cmd +='    sys.path.append(_newPath)\n'
         _cmd +='\n'
         _cmd +=u'# UI Load\n'
         _cmd +='import Alfred_AssetTools\n'
         _cmd +='reload(Alfred_AssetTools)\n'
         _cmd +=__name__+'.handPose_fromSelect_toShelf()\n'
         
         cmds.shelfButton(
            commandRepeatable = True ,
            image1            = 'pythonFamily.png' ,
            label             = 'getHandPose',
            annotation        = 'getHandPose from Selection',
            sourceType        = 'python',
            command           = _cmd ,
            imageOverlayLabel = 'getHandPose',
            parent            = _shelfName,
            )

    _cmd = getData_from_selection()
    if not _cmd:
        return
    
    _result = cmds.promptDialog(
        title='name',
        message='pose name:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel'
        )
    if _result != 'OK':
        print _cmd
        return

    _label = cmds.promptDialog(query=True, text=True)
    
    cmds.shelfButton(
        commandRepeatable =True ,
        image1            ='commandButton.png' ,
        label             ='handPose_'+_label ,
        annotation        ='handPose_'+_label ,
        sourceType        ='mel',
        command           = _cmd ,
        imageOverlayLabel =_label,
        parent            =_shelfName,
    )

# 선택한 부분에서 포즈 스크립트 생성
def getData_from_selection():
    _sel = cmds.ls(sl=True)
    if not _sel:
        return
    
    _namespace = ''
    _split = _sel[0].split(':')
    if len(_split)>1:
        _namespace = _split[0]
    
    _side = 'Left'
    if 'Right' in _sel[0]:
        _side='Right'
    
    _mel = Hand_printFingerAttr(_namespace,_side)
    return _mel

# 포즈 스크립트 생성
# HIK_Tool_printFingerAttr('CHAR','Left')
def Hand_printFingerAttr(_namespace,_side):
    #_HIKCtrler = cmds.ls( _namespace+':HIK_Ctrl_'+_side+'Hand*', type=['hikFKJoint','hikIKEffector'])
    _HIKCtrler = cmds.ls( _namespace+':HIK_Ctrl_'+_side+'Hand*', type=['hikFKJoint'])

    print 'Hand_printFingerAttr(\'%s\',\'%s\')'%(_namespace,_side)
    print _HIKCtrler

    _reverse = 1.0
    if _side=='Right':
        _reverse=-1

    _command  = '{\n'
    _command += '    string $sel[] = `ls -sl`;\n'
    _command += '\n'
    _command += '    // getNamespace\n'
    _command += '    string $namespace ="";\n'
    _command += '    string $buffer[];\n'
    _command += '    int $num = `tokenize $sel[0] ":" $buffer`;\n'
    _command += '    if ($num > 1) $namespace=$buffer[0]+":";\n'
    _command += '\n'
    _command += '    // Side\n'
    _command += '    string $side   = "Left";\n'
    _command += '    float $reverse = 1.0;\n'
    _command += '    if (`gmatch $sel[0] "*Right*"`) {\n'
    _command += '        $side = "Right";\n'
    _command += '        $reverse = -1.0;\n'
    _command += '    }\n'
    _command += '\n'

    for _ctrler in _HIKCtrler:
        _t = cmds.getAttr(_ctrler+'.t')[0]
        _r = cmds.getAttr(_ctrler+'.r')[0]        
        
        _command += '    // %s\n'%_ctrler
        _command += '    string $ctrler = $namespace+"%s"+$side+"%s";\n'%tuple(_ctrler[len(_namespace)+1:].split(_side))
        _command += '    if (`objExists  $ctrler`) {\n'
        _command += '        if (!`getAttr -l ( $ctrler+".tx")`) setAttr ($ctrler+".tx") (%f * $reverse);\n'%(_t[0]*_reverse)
        _command += '        if (!`getAttr -l ( $ctrler+".ty")`) setAttr ($ctrler+".ty") (%f);\n'%_t[1]
        _command += '        if (!`getAttr -l ( $ctrler+".tz")`) setAttr ($ctrler+".tz") (%f);\n'%_t[2]
        _command += '\n'
        _command += '        if (!`getAttr -l ( $ctrler+".rx")`) setAttr ($ctrler+".rx") (%f);\n'%_r[0]
        _command += '        if (!`getAttr -l ( $ctrler+".ry")`) setAttr ($ctrler+".ry") (%f * $reverse);\n'%(_r[1]*_reverse)
        _command += '        if (!`getAttr -l ( $ctrler+".rz")`) setAttr ($ctrler+".rz") (%f * $reverse);\n'%(_r[2]*_reverse)
        _command += '    }\n'

    _command += '}\n'

    return _command
    #return _joint
    
# Body Pose
def get_bodyPose_hikCtrlData_from_selected():
    _sel         = cmds.ls(sl=True)
    if not _sel: return

    # get namespace
    _namespace = getNamespace(_sel[0])

    # get HIKCharacterNode
    _HIKCharacterNode = ''
    _list = cmds.ls(_namespace+'*', exactType='HIKCharacterNode')
    if _list: _HIKCharacterNode = _list[0][ len(_namespace):]
    print 'HIKCharacterNode :',_HIKCharacterNode

    # get HIK_prefix
    _HIK_prefix = _namespace + _HIKCharacterNode + '_Ctrl_'
    print 'HIK_prefix :',_HIK_prefix

    # get Pose Data
    _HIK_IKEffectors = []
    _HIK_FKJoints = []
    _Joints = []

    for _hikIKEffector in cmds.ls(_namespace+'*', exactType='hikIKEffector'):
        _name      = _hikIKEffector[len(_HIK_prefix):]
        _translate = cmds.getAttr(_hikIKEffector+'.t')[0]
        _rotate    = cmds.getAttr(_hikIKEffector+'.r')[0]

        _HIK_IKEffectors.append({
            'name':_name, 
            'translate':_translate, 
            'rotate':_rotate
            })
    
    for _hikFKJoint    in cmds.ls(_namespace+'*', exactType='hikFKJoint'):
        _name   = _hikFKJoint[len(_HIK_prefix):]
        _rotate = cmds.getAttr(_hikFKJoint+'.r')[0]

        _HIK_FKJoints.append({
            'name':_name, 
            'rotate':_rotate
            })
    
    for _Joint   in cmds.ls(_namespace+'*', exactType='hikFKJoint'):
        _name   = _Joint[len(_namespace):]
        _rotate = cmds.getAttr(_Joint+'.r')[0]

        _HIK_FKJoints.append({
            'name':_name, 
            'rotate':_rotate
            })

    # command
    _command =''
    _command  = '{\n'
    _command += '    string $sel[] = `ls -sl`;\n'
    _command += '\n'
    _command += '    // check HIK node\n'
    _command += '    int $HIK = false;\n'
    _command += '\n'
    _command += '    // set prefix\n'
    _command += '    string $prefix = "";\n'
    _command += '\n'
    _command += '    // get Namespace\n'
    _command += '    string $namespace ="";\n'
    _command += '    string $buffer[];\n'
    _command += '    int $num = `tokenize $sel[0] ":" $buffer`;\n'
    _command += '    if ($num > 1) $namespace=$buffer[0]+":";\n'
    _command += '\n'
    _command += '    $prefix = $namespace;\n'
    _command += '\n'
    _command += '    // get HIKCharacterNode\n'
    _command += '    string $HIKCharacterNode = "";\n'
    _command += '    string $ls[] = `ls -type "HIKCharacterNode" ($namespace+"*")`;\n'
    _command += '    if (size($ls) > 0) {\n'
    _command += '        $HIK = true;\n'
    _command += '        $HIKCharacterNode = $ls[0];\n'
    _command += '        $prefix = $ls[0];\n'
    _command += '    } else {\n'
    _command += '        $HIK = false;\n'
    _command += '    }\n'
    _command += '\n'
    _command += '    $prefix = $prefix +"_Ctrl_";\n'
    _command += '\n'
    
    for _data in _HIK_IKEffectors:
        _name = _data['name']
        _t    = _data['translate']
        _r    = _data['rotate']
        #_command += '    setAttr ($prefix+"%s.t") -type "double3" %f %f %f;\n'%(_name,_t[0],_t[1],_t[2])

        _command += '    // %s\n'%_name
        _command += '    string $ctrler = $prefix+"%s";\n'%_name
        _command += '    if (`objExists $ctrler`) {\n'
        _command += '        if (!`getAttr -l ( $ctrler+".tx")`) setAttr ($ctrler+".tx") %f;\n'%_t[0]
        _command += '        if (!`getAttr -l ( $ctrler+".ty")`) setAttr ($ctrler+".ty") %f;\n'%_t[1]
        _command += '        if (!`getAttr -l ( $ctrler+".tz")`) setAttr ($ctrler+".tz") %f;\n'%_t[2]
        _command += '\n'
        _command += '        if (!`getAttr -l ( $ctrler+".rx")`) setAttr ($ctrler+".rx") %f;\n'%_r[0]
        _command += '        if (!`getAttr -l ( $ctrler+".ry")`) setAttr ($ctrler+".ry") %f;\n'%_r[1]
        _command += '        if (!`getAttr -l ( $ctrler+".rz")`) setAttr ($ctrler+".rz") %f;\n'%_r[2]
        _command += '    }\n'
    
    for _data in _HIK_FKJoints:
        _name = _data['name']
        _r    = _data['rotate']
        #_command += '    setAttr ($prefix+"%s.t") -type "double3" %f %f %f;\n'%(_name,_t[0],_t[1],_t[2])

        _command += '    // %s\n'%_name
        _command += '    string $ctrler = $prefix+"%s";\n'%_name
        _command += '    if (`objExists $ctrler`) {\n'
        _command += '        if (!`getAttr -l ( $ctrler+".tx")`) setAttr ($ctrler+".tx") %f;\n'%_t[0]
        _command += '        if (!`getAttr -l ( $ctrler+".ty")`) setAttr ($ctrler+".ty") %f;\n'%_t[1]
        _command += '        if (!`getAttr -l ( $ctrler+".tz")`) setAttr ($ctrler+".tz") %f;\n'%_t[2]
        _command += '\n'
        _command += '        if (!`getAttr -l ( $ctrler+".rx")`) setAttr ($ctrler+".rx") %f;\n'%_r[0]
        _command += '        if (!`getAttr -l ( $ctrler+".ry")`) setAttr ($ctrler+".ry") %f;\n'%_r[1]
        _command += '        if (!`getAttr -l ( $ctrler+".rz")`) setAttr ($ctrler+".rz") %f;\n'%_r[2]
        _command += '    }\n'
    
    _command += '}\n'
    return _command

#----------------------------------------
#
#     HIKCharacterControlsTool : 캐릭터 자동 선택
#
#----------------------------------------
# 2013 HIK 컨트롤 리그창 선택한 캐릭터 어싸인~
def update_HIKCurrentCharacter_from_select():
    # 암것도 선택 안했음 중단
    if not cmds.ls(sl=True):
        return

    # 현재 캐릭터 변수에 집어넣고 UI갱신
    _HIKCharacterNode = getHIKCharacterNode()

    # HIKCharacterNode와 관련없는 노드이면 중단
    if not _HIKCharacterNode:
        return

    # 여러개 선택했을경우 마지막에 선택한 노드를 적용
    if type(_HIKCharacterNode)==list:
        _HIKCharacterNode = _HIKCharacterNode[-1]

    mel.eval( '$gHIKCurrentCharacter = "%s";'%_HIKCharacterNode)
    mel.eval( 'hikUpdateCurrentCharacterFromScene();' )

# 스트립트 잡 추가
def add_ScriptJob_updateHIKCurrentCharacter():
    if cmds.dockControl( 'hikCharacterControlsDock', q=1, exists=1 ):
        # 잡 검색
        for _job in cmds.scriptJob( listJobs=True ):
            if 'update_HIKCurrentCharacter_from_select' in _job:
                # scriptJob 이름이 아래처럼 출력됨.
                # 2207: event=['SelectionChanged', 'HIK_Tools.update_HIKCurrentCharacter_from_select()'], parent='hikCharacterControlsDock'
                #
                print u'+ scriptJob이 이미 존재합니다 :',_job
                return

        # 잡 추가
        _jobNum = cmds.scriptJob( parent='hikCharacterControlsDock', killWithScene=True, event=['SelectionChanged', __name__+'.update_HIKCurrentCharacter_from_select()'] )
        update_HIKCurrentCharacter_from_select()
        
        for _job in cmds.scriptJob( listJobs=True ):
            if 'update_HIKCurrentCharacter_from_select' in _job:
                # scriptJob 이름이 아래처럼 출력됨.
                # 2207: event=['SelectionChanged', 'HIK_Tools.update_HIKCurrentCharacter_from_select()'], parent='hikCharacterControlsDock'
                #
                print u'+ scriptJob 추가 :',_job

# 스트립트 잡 삭제
def remove_ScriptJob_updateHIKCurrentCharacter():
    _jobs = cmds.scriptJob( listJobs=True )
    for _job in _jobs:
        if 'update_HIKCurrentCharacter_from_select' in _job:
            # scriptJob 이름이 아래처럼 출력됨.
            # 2207: event=['SelectionChanged', 'HIK_Tools.update_HIKCurrentCharacter_from_select()'], parent='hikCharacterControlsDock'
            #
            _split = _job.split(':')
            _jobNum = int(_split[0])
            cmds.scriptJob( kill=_jobNum, force=True)
            print u'+ scriptJob 삭제 :',_job

#----------------------------------------
#
#     namespace 알아옴
#
#----------------------------------------
def getNamespace(*args):
    if args:
        return getNamespace_from_node(args[0])
    else :
        return getNamespace_from_select()

def getNamespace_from_select():
    _namespace = []
    _sel       = cmds.ls(sl=True)

    # 선택된게 없으면 중지
    if not _sel: 
        return 
    
    for _node in _sel:
        _namespace.append( getNamespace_from_node(_node) )
    
    # namespace가 없으면 중지
    if not _namespace:
        return

    # 중복자료 삭제
    _namespace = list(set(_namespace))

    # 결과가 하나면 string, 여러개면 list로 리턴
    if len(_namespace) == 1:
        return _namespace[0]
    else:
        return _namespace

def getNamespace_from_node(_node):
    if type(_node) == str or type(_node) == unicode:
        # _node = "Hello:MyNmae:This:Hand"
        _namespace = ''

        _split = _node.split(':') # Result: ['Hello', 'MyNmae', 'This', 'Hand']
        if len(_split)<2: return        
        for _ns in _split[0:-1]: _namespace += _ns+':'

        return _namespace

    elif type(_node) == list:
        _namespace = []
        for _n in _node:
            # _n = "Hello:MyNmae:This:Hand"
            _split = _n.split(':')    # Result: ['Hello', 'MyNmae', 'This', 'Hand']
            if len(_split)<2: continue            
            for _ns in _split[0:-1]:  _namespace.append(_ns+':')

        return list(set(_namespace))

#----------------------------------------
#
#     HIKCharacterNode 알아옴1
#
#----------------------------------------
def getHIKCharacterNode(*args):
    if args:
        return getHIKCharacterNode_from_node(args[0])
    else :
        return getHIKCharacterNode_from_select()

def getHIKCharacterNode_from_select():
    _HIKCharacterNode = []
    _namespaces =[]
    _sel       = cmds.ls(sl=True)

    # 선택된게 없으면 중지
    if not _sel: 
        return 
    
    for _node in _sel:
        _namespace = getNamespace(_node)

        # 이미 같은 namespace를 검색했었으면 넘어감(또, 검색하지 않게)
        if _namespace and _namespace in _namespaces:
            continue
        _namespaces.append( _namespace )

        _result = getHIKCharacterNode_from_node(_node)

        # 찾은게 없거나, 이미 찾은 노드면 넘어감
        if not _result or _result in _HIKCharacterNode:
            continue

        # 찾은게 있으면 등록
        _HIKCharacterNode.append(_result)

    # 찾은게 없으면 None리턴
    if not _HIKCharacterNode:
        return

    # 결과가 하나면 string, 여러개면 list로 리턴
    if len(_HIKCharacterNode) == 1:
        return _HIKCharacterNode[0]
    else:
        return _HIKCharacterNode

def getHIKCharacterNode_from_node(_node):
    if type(_node) == str or type(_node) == unicode:
        # namespace 확인
        _namespace = getNamespace(_node)
        _ls = []
        
        if _namespace:
            # namespace가 존재할경우 
            # 레퍼런스로 생각하고 namespace로 시작하는 HIKProperty2State 노드 찾음.
            _ls = cmds.ls( _namespace+"*", type='HIKCharacterNode')
        else:
            # namespace가 존재하지 않을경우
            # 임포트되었거나, 캐릭터 원본 파일
            # listHistory 를 사용해서 찾음,
            # 일일히 다 검색해야 해서, 다소 피드백이 느림.
            _listHistory = cmds.listHistory( 
                _node, 
                #allFuture=True, 
                allConnections=True
                )
            _ls = cmds.ls( _listHistory, type='HIKCharacterNode')

        # 찾은게 없으면 나감
        if not _ls: 
            return

        # 찾은게 있으면 등록   
        return _ls[0]

    elif type(_node) == list:
        _HIKCharacterNode = []
        for _n in _node:
            _namespace = getNamespace(_n)
            _ls = []

            if _namespace:
                # namespace가 존재할경우 
                # 레퍼런스로 생각하고 namespace로 시작하는 HIKProperty2State 노드 찾음.
                _ls = cmds.ls( _namespace+"*", type='HIKCharacterNode')
            else:
                # namespace가 존재하지 않을경우
                # 임포트되었거나, 캐릭터 원본 파일
                # listHistory 를 사용해서 찾음,
                # 일일히 다 검색해야 해서, 다소 피드백이 느림.
                _listHistory = cmds.listHistory( 
                    _n,
                    #allFuture=True, 
                    allConnections=True
                    )
                _ls = cmds.ls( _listHistory, type='HIKCharacterNode')

            # 찾은게 없으면 나감
            if not _ls: return

            for _i in _ls:
                _HIKCharacterNode.append(_i)

        return list(set(_HIKCharacterNode))

#----------------------------------------
#
#     HIKCharacterNode 알아옴2
#
#----------------------------------------
def setHIKCharacterNode(*args):
    if not args:
        return;
    
    if cmds.nodeType(args) == 'HIKCharacterNode':
        mel.eval( '$gHIKCurrentCharacter = "%s";'%args[0])
        mel.eval( 'hikUpdateCurrentCharacterFromScene();' )

def getHIKCurrentCharacter(*args):
    return mel.eval('$tmpString = $gHIKCurrentCharacter;')

def getHIKCharacterNodes_form_Scene(*args):
	return cmds.ls( type='HIKCharacterNode' )

#----------------------------------------
#
#     HIKProperty2State 알아옴
#
#----------------------------------------
def getHIKProperty2State(*args):
    if args:
        return getHIKProperty2State_from_node(args[0])
    else :
        return getHIKProperty2State_from_select()

def getHIKProperty2State_from_select():
    _HIKProperty2State = []
    _namespaces =[]
    _sel       = cmds.ls(sl=True)

    # 선택된게 없으면 중지
    if not _sel: 
        return 
    
    for _node in _sel:
        _namespace = getNamespace(_node)

        # 이미 같은 namespace를 검색했었으면 넘어감(또, 검색하지 않게)
        if _namespace and _namespace in _namespaces:
            continue
        _namespaces.append( _namespace )

        _result = getHIKProperty2State_from_node(_node)

        # 찾은게 없거나, 이미 찾은 노드면 넘어감
        if not _result or _result in _HIKProperty2State:
            continue

        # 찾은게 있으면 등록
        _HIKProperty2State.append(_result)

    # 찾은게 없으면 None리턴
    if not _HIKProperty2State:
        return

    # 결과가 하나면 string, 여러개면 list로 리턴
    if len(_HIKProperty2State) == 1:
        return _HIKProperty2State[0]
    else:
        return _HIKProperty2State

def getHIKProperty2State_from_node(_name):
    # namespace 확인
    _namespace = getNamespace(_name)
    _ls = []
    
    if _namespace:
        # namespace가 존재할경우 
        # 레퍼런스로 생각하고 namespace로 시작하는 HIKProperty2State 노드 찾음.
        _ls = cmds.ls( _namespace+"*", type='HIKProperty2State')        
    else:
        # namespace가 존재하지 않을경우
        # 임포트되었거나, 캐릭터 원본 파일
        # listHistory 를 사용해서 찾음,
        # 일일히 다 검색해야 해서, 다소 피드백이 느림.
        _listHistory = cmds.listHistory( 
            _name, 
            #allFuture=True, 
            allConnections=True
            )
        _ls = cmds.ls( _listHistory, type='HIKProperty2State')

    # 찾은게 없으면 나감
    if not _ls: 
        return

    # 찾은게 있으면 등록   
    return _ls[0]

#----------------------------------------
#
#     루트 트랜스폼 노드를 알아옴.
#
#----------------------------------------
def getRootParent(*args):
    if args:
        return getRootParent_from_node(args[0])
    else :
        return getRootParent_from_select()

def getRootParent_from_select():
    _sel       = cmds.ls(sl=True)

    # 선택된게 없으면 중지
    if not _sel: 
        return

    _node=_sel[0]

    _root = []
    for _node in _sel:
        _result = getRootParent_from_node(_node)
        if _result and not _result in _root:
            _root.append(_result)

    return _root[0]
    
def getRootParent_from_node(_name):
    _root = []
    _transforms = []

    # _name 노드가 트랜스폼 노드이면..
    if cmds.nodeType(_name)=='transform':
        _listRelatives = cmds.listRelatives( _name, fullPath=True)
        _root = _listRelatives[0].split('|')[1]
        return _root

    # _name 노드에 네임스페이스가 붙어 있으면...
    _namespace = getNamespace(_name)

    # transform 노드들 검색    
    if _namespace:
        _transforms = cmds.ls( _namespace+"*", type='transform', long=True)
    else:
        _listHistory = cmds.listHistory( 
            _name, 
            allFuture=True, 
            allConnections=True
            )
        if not _listHistory:
            return
        _transforms = cmds.ls( _listHistory, type='transform', long=True)

    # transform 노드들 처리
    if not _transforms:
        return
    
    for _transform in _transforms:
        # _transform[0] 데이터가 아래처럼 들어옴.
        # |CHAR2__Reference|CHAR2__HIK_Ctrl_Reference|CHAR2__HIK_Ctrl_HipsEffector
        _split = _transform.split('|')
        
        if _split[1] in _root:
            continue
        
        _root.append( _split[1] )

    return _root[0]

#----------------------------------------
#
#     왼쪽? 오른쪽?
#
#----------------------------------------
def getSide(*args):
    _sel = []
    _Side = []

    if args:
        if type(args[0]) == list:
            _sel = args[0]

        elif type(args[0]) == str or type(args[0]) == unicode:
            _sel = [args[0]]

    else:
        _sel = cmds.ls(sl=True)
        if not _sel: return

    for _node in _sel:
        if 'Left'  in _node: _Side. append('Left')
        if 'Right' in _node: _Side. append('Right')

    _Side = list(set(_Side))
    return _Side

#----------------------------------------
#
#     모션캡쳐 도구
#
#----------------------------------------
# 모션캡쳐 데이터에서 클립 생성(타임 오프셋용)
def make_Clip_from_MotionCaptureData():
    _clipName = mel.eval( 'basenameEx(`file -q -sn`)')
    _Char = 'Clip'

    # make Character
    _bodyJoints = [
        'HipsTranslation','Hips','Spine','Spine1','Spine2','Spine3','Neck','Head',
        'LeftShoulder','LeftArm','LeftArmRoll','LeftForeArm','LeftForeArmRoll','LeftHand',
        'LeftUpLeg','LeftUpLegRoll','LeftLeg','LeftLegRoll','LeftFoot','LeftToeBase',
        'RightShoulder','RightArm','RightArmRoll','RightForeArm','RightForeArmRoll','RightHand',    
        'RightUpLeg','RightUpLegRoll','RightLeg','RightLegRoll','RightFoot','RightToeBase'
        ]
    _attrList = ['tx','ty','tz','rx','ry','rz']
    cmds.character(name=_Char)

    # tr, rt 속성 추가
    for _jnt in _bodyJoints:
        for _attr in _attrList:
            cmds.character(_jnt+'.'+_attr ,forceElement=_Char)

    _attrList = ['tx','ty','tz']
    # tr속성 제거
    for _jnt in _bodyJoints:
        if _jnt == 'HipsTranslation' or _jnt == 'Hips': continue
        for _attr in _attrList:
            cmds.character( _jnt+'.'+_attr , remove=_Char )

    # 애니메이션 클립 생성
    cmds.clip(_Char, name=_clipName, scheduleClip=True, allAbsolute=True, animCurveRange=True)

#------------------------------------
#
#           Sniper Gun Rig
#
#------------------------------------
# displayConnect_curve( cmds.ls(sl=True) )
def displayConnect_curve( _obj ):
	# 타겟 오브젝트
    _pointA = _obj[0]
    _pointB = _obj[1]

	# 라인생성
    _curve = cmds.curve(d=1, p=[(0,0,0),(0,0,0)], k=[0,1] )
    _pointCurveConstraint1 = cmds.pointCurveConstraint( _curve+'.ep[0]',ch=True)
    _pointCurveConstraint2 = cmds.pointCurveConstraint( _curve+'.ep[1]',ch=True)

	# pointCurveConstraint로 생성된 로케이터를 타겟 오브젝트에 붙임
    cmds.pointConstraint( _pointA, _pointCurveConstraint1[0])
    cmds.pointConstraint( _pointB, _pointCurveConstraint2[0])

	# 로케이터 가림
    _locShape1 = cmds.listRelatives( _pointCurveConstraint1[0], s=True )
    _locShape2 = cmds.listRelatives( _pointCurveConstraint2[0], s=True )
    cmds.setAttr (_locShape1[0]+'.visibility', 0)
    cmds.setAttr (_locShape2[0]+'.visibility', 0)

	# return
    return [_curve, _pointCurveConstraint1[0], _pointCurveConstraint2[0] ]

# displayConnect_arrow( cmds.ls(sl=True) )
def displayConnect_arrow( _obj ):
	# 타겟 오브젝트
    _pointA = _obj[0]
    _pointB = _obj[1]

	# 라인생성
    _createNode = cmds.createNode('annotationShape')
    _listRelatives = cmds.listRelatives( _createNode, parent=True )
    _annotation = [_listRelatives[0], _createNode]
    print _annotation

    _loc = cmds.spaceLocator()
    _listRelatives = cmds.listRelatives( _loc[0], s=True )
    _locator = [ _loc[0], _listRelatives[0] ]

    cmds.connectAttr( _locator[1]+'.worldMatrix[0]', _annotation[1]+'.dagObjectMatrix[0]')

	# pointCurveConstraint로 생성된 로케이터를 타겟 오브젝트에 붙임
    cmds.pointConstraint( _pointA, _annotation[0])
    cmds.pointConstraint( _pointB, _locator[0])

	# 로케이터 가림
    cmds.setAttr (_locator[1]+'.visibility', 0)

	# return
    return [_annotation[0], _locator[0]]

# displayOverride(  cmds.ls(sl=True) , type=0, color=5)
def displayOverride( _obj, **kwargs):
    _type = 0
    _color = 0

    # Type
    if kwargs.get('type'):
        _input = kwargs.get('type')
        _type = _input
    else:
        _type = 0

    # Color
    if kwargs.get('color'):
        _input = kwargs.get('color')
        _color = _input
    else:
        _color = 0

    # 실행
    for _node in _obj:
        cmds.setAttr ( _node+'.overrideEnabled', 1)
        cmds.setAttr ( _node+'.overrideDisplayType', _type)
        cmds.setAttr ( _node+'.overrideColor', _color)

def Gun_Rig():
    _prefix = 'Gun_'

    _hips      = 'Hips'
    _spine2    = 'Spine2'
    _leftHand  = 'LeftHand'
    _rightHand = 'RightHand'
    _rightArm  = 'RightArm'

    _rigRoot          = _prefix+'Rig'
    _buttPlate_pos    = _prefix+'buttPlate_pos'
    _buttPlate_offset = _prefix+'buttPlate_offset'
    _up               = _prefix+'up'
    _aim              = _prefix+'aim'
    _rightHand_const  = _prefix+'rightHand_const'
    _trigger_pos      = _prefix+'trigger' 
    _leftHand_const   = _prefix+'leftHand_const'
    _gunPos_offset    = _prefix+'gunPos_offset'
    _gunPos           = _prefix+'gunPos'
    _dispGrp          = _prefix+'dispGrp'
    _gunAim_point     = _prefix+'gunAim'
    _gunAim_offset    = _prefix+'gunAim_offset'
    _gunRerease_point = _prefix+'gunRerease_point'

    # Root : Hips 조인트에 parent 컨스트레인
    _rigRoot = cmds.group(name=_rigRoot, em=True)
    cmds.parentConstraint( _hips, _rigRoot )

    #-----------------------------------------
    #
    #         왼손 포인트 리깅
    #
    #-----------------------------------------
    # aim : LeftHand 조인트에 _aim 포인트 컨스트레인
    _leftHand_const = cmds.group(name=_leftHand_const, em=True)
    cmds.parentConstraint( _leftHand, _leftHand_const )
    cmds.parent(_leftHand_const, _rigRoot)

    _aim = cmds.spaceLocator( name=_aim )[0]
    cmds.setAttr( _aim+'.displayHandle', 1)
    _tmp = cmds.pointConstraint( _leftHand_const, _aim); cmds.delete(_tmp)
    cmds.parent(_aim, _leftHand_const)

    #-----------------------------------------
    #
    #         견착 
    #
    #-----------------------------------------
    # pos : Spine2 조인트에 _aim 포인트 컨스트레인
    _buttPlate_pos    = cmds.spaceLocator( name=_buttPlate_pos )[0]
    cmds.setAttr( _buttPlate_pos+'.displayHandle', 1)

    _buttPlate_offset = cmds.group( _buttPlate_pos, name=_buttPlate_offset)
    cmds.pointConstraint( _spine2, _buttPlate_offset )
    _tmp = cmds.pointConstraint( _rightArm, _buttPlate_pos ); cmds.delete(_tmp)
    cmds.parent(_buttPlate_offset, _rigRoot)

    # up : RightArm 조인트 위에 _up 포인트 위치 시킴
    _up    = cmds.spaceLocator( name=_up )[0]
    cmds.setAttr( _up+'.displayHandle', 1)
    _tmp = cmds.pointConstraint( _rightArm, _up, offset=[0,10,0] ); cmds.delete(_tmp)
    cmds.parent(_up, _rigRoot)

    # aim : Constraint
    cmds.aimConstraint( _aim, _buttPlate_pos, aimVector=[0,0,1], upVector=[0,1,0], worldUpType='object', worldUpObject=_up)

    # 견착 포인트 
    _gunAim_point = cmds.spaceLocator( name=_gunAim_point )[0]
    _gunAim_offset = cmds.group( _gunAim_point, name=_gunAim_offset)

    cmds.pointConstraint (_aim, _buttPlate_pos, _gunAim_offset)
    cmds.aimConstraint( _aim, _gunAim_offset, aimVector=[0,0,1], upVector=[0,1,0], worldUpType='object', worldUpObject=_up)
    cmds.parent(_gunAim_offset, _rigRoot)

    #-----------------------------------------
    #
    #         오른손 포인트 리깅
    #
    #-----------------------------------------
    # RightHand : RightHand 조인트에 _trigger 포인트 컨스트레인
    _gunRerease_point = cmds.spaceLocator( name=_gunRerease_point )[0]

    _rightHand_const = cmds.group(_gunRerease_point, name=_rightHand_const)
    cmds.parentConstraint( _rightHand, _rightHand_const )
    cmds.parent(_rightHand_const, _rigRoot)  
    
    #-----------------------------------------
    #
    #         총이 위치할 포인트 리깅
    #
    #-----------------------------------------
    _gunPos = cmds.spaceLocator( name=_gunPos )[0]
    cmds.setAttr( _gunPos+'.displayHandle', 1)

    _gunPos_offset = cmds.group( _gunPos, name=_gunPos_offset)
    _pointConst = cmds.pointConstraint (_gunAim_point, _gunRerease_point, _gunPos_offset)
    cmds.aimConstraint( _aim, _gunPos_offset, aimVector=[0,0,1], upVector=[0,1,0], worldUpType='object', worldUpObject=_up)
    cmds.parent(_gunPos_offset, _rigRoot)

    # 어트리뷰트 추가, 리깅
    cmds.addAttr(_gunPos, ln='aim', at='double', min=0, max=1, dv=1, keyable=True)
    _aliasList = cmds.pointConstraint(_pointConst[0], q=True, weightAliasList=True)
    _reverse   = cmds.createNode( 'reverse' )    
    cmds.connectAttr(_gunPos+'.aim', _pointConst[0]+'.'+_aliasList[0])
    cmds.connectAttr(_gunPos+'.aim', _reverse+'.inputX')
    cmds.connectAttr(_reverse+'.outputX', _pointConst[0]+'.'+_aliasList[1])
   
    # up 재배치
    _tmp = cmds.pointConstraint( _gunPos, _up, offset=[0,30,0] ); cmds.delete(_tmp)
    
    # 디스플레이 그룹
    _dispGrp = cmds.group(name=_dispGrp, em=True)
    cmds.parent(_dispGrp, _rigRoot)
    displayOverride([_dispGrp], type=1)
    #cmds.parent( displayConnect_arrow( [_trigger_pos,_aim]), _dispGrp)
    cmds.parent( displayConnect_arrow( [_buttPlate_pos,_aim]), _dispGrp)
    cmds.parent( displayConnect_arrow( [_gunPos,_up]), _dispGrp)
    cmds.parent( displayConnect_curve( [_gunAim_point,_gunRerease_point]), _dispGrp)

    displayOverride([_aim, _up, _buttPlate_pos], type=0, color=7) #darkGreen
    displayOverride([_gunAim_point, _gunRerease_point], type=0, color=8) #darkGreen
    displayOverride([_gunPos], type=0, color=13) #Red

    cmds.select(_gunPos)

'''
sniperGunRig( 'sniperGun_' , 'CHAR')
'''
