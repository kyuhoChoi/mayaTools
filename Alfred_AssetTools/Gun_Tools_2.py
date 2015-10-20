_namespace = 'CHAR:'
_HIK_Ctrl = 'HIK_Ctrl_'
_prefix = _namespace+_HIK_Ctrl

_Hips          = _prefix+'Hips'
_LeftShoulder  = _prefix+'LeftShoulder'
_LeftArm       = _prefix+'LeftArm'
_LeftHand      = _prefix+'LeftHand'
_RightShoulder = _prefix+'RightShoulder'
_RightArm      = _prefix+'RightArm'
_RightHand     = _prefix+'RightHand'

_prefix = 'Gun_'
_Gun_Rig_Grp = cmds.group( name=_prefix+'Rig_Grp', em=True )
cmds.parentConstraint(_Hips, _Gun_Rig_Grp)

_up_Ctrl  = Ctrler( _prefix+'up',  initTransform=_Gun_Rig_Grp,  displayHandle=True)
cmds.parent(_up_Ctrl[0], _Gun_Rig_Grp)
cmds.setAttr( _up_Ctrl[0]+'.t', 0, 100, 0, type='double3')

_LeftShoulder_Ctrl  = Ctrler( _prefix+'LeftShoulder',  initTransform=_LeftShoulder,  displayHandle=True, constraint=['parent', _LeftShoulder]  )
_LeftArm_Ctrl       = Ctrler( _prefix+'LeftArm',       initTransform=_LeftArm,       displayHandle=True, constraint=['parent', _LeftArm]       )
_LeftHand_Ctrl      = Ctrler( _prefix+'LeftHand',      initTransform=_LeftHand,      displayHandle=True, constraint=['parent', _LeftHand]      )
_RightShoulder_Ctrl = Ctrler( _prefix+'RightShoulder', initTransform=_RightShoulder, displayHandle=True, constraint=['parent', _RightShoulder] )
_RightArm_Ctrl      = Ctrler( _prefix+'RightArm',      initTransform=_RightArm,      displayHandle=True, constraint=['parent', _RightArm]      )
_RightHand_Ctrl     = Ctrler( _prefix+'RightHand',     initTransform=_RightHand,     displayHandle=True, constraint=['parent', _RightHand]     )
cmds.parent(_LeftShoulder_Ctrl[0],_LeftArm_Ctrl[0],_LeftHand_Ctrl[0],_RightShoulder_Ctrl[0],_RightArm_Ctrl[0],_RightHand_Ctrl[0],     _Gun_Rig_Grp)

_constKey = ['LeftShoulder',        'LeftArm',        'LeftHand',        'RightShoulder',        'RightArm',        'RightHand']
_constVal = [_LeftShoulder_Ctrl[1], _LeftArm_Ctrl[1], _LeftHand_Ctrl[1], _RightShoulder_Ctrl[1], _RightArm_Ctrl[1], _RightHand_Ctrl[1]]
_constraintTarget = {
    'LeftShoulder': _LeftShoulder_Ctrl[1], 
    'LeftArm':      _LeftArm_Ctrl[1], 
    'LeftHand':     _LeftHand_Ctrl[1], 
    'RightShoulder':_RightShoulder_Ctrl[1], 
    'RightArm':     _RightArm_Ctrl[1], 
    'RightHand':    _RightHand_Ctrl[1]
    }

# ÃÑ±¸
_Aim_Ctrl         = Ctrler( _prefix+'Aim', displayHandle=True)
_Aim_Const        = cmds.pointConstraint(_constVal,   _Aim_Ctrl[0])[0]
_Aim_Const_Target = cmds.pointConstraint(_Aim_Const, q=True, weightAliasList=True)
for _i,_attr in enumerate(_constKey):
    cmds.addAttr( _Aim_Ctrl[1], ln=_attr, attributeType='double', keyable=True)
    cmds.connectAttr(_Aim_Ctrl[1]+'.'+_attr, _Aim_Const+'.'+_Aim_Const_Target[_i])
displayOverride( _Aim_Ctrl[1], color=18 )

# ÃÑÀ§Ä¡
_Gun_Ctrl         = Ctrler( _prefix+'Gun', displayHandle=True)
_Gun_Const        = cmds.pointConstraint(_constVal,   _Gun_Ctrl[0])[0]
_Aim_Const_Target = cmds.pointConstraint(_Aim_Const, q=True, weightAliasList=True)
for _i,_attr in enumerate(_constKey):
    cmds.addAttr( _Gun_Ctrl[1], ln=_attr, attributeType='double', keyable=True)
    cmds.connectAttr(_Gun_Ctrl[1]+'.'+_attr, _Gun_Const+'.'+_Aim_Const_Target[_i])
displayOverride( _Gun_Ctrl[1], color=15 )

def Ctrler(_prefix, **kwargs):
    _position = [0,0,0]
    _rotation = [0,0,0]
    _displayHandle = False
    _constraint = ''
    _constraintTarget = ''

    # initTransform
    if kwargs.get('initTransform'):
        _input = kwargs.get('initTransform')

        if type(_input) == list:
            _position = _input[0]
            _rotation = _input[1]
        
        if type(_input) == str or type(_input)==unicode and cmds.objExists(_input):
            _position = cmds.xform( _input, q=True, worldSpace=True, translation=True )
            _rotation = cmds.xform( _input, q=True, worldSpace=True, rotation=True    )
    
    # displayHandle
    if kwargs.get('displayHandle'):
        _input = kwargs.get('displayHandle')

        if type(_input) == bool:
            _displayHandle = _input

    # displayHandle
    if kwargs.get('constraint'):
        _input = kwargs.get('constraint')

        if type(_input) == list:
            _constraint = _input[0]
            _constraintTarget = _input[1]
    
    # createNode
    _loc      = cmds.spaceLocator( name=_prefix+'_posCtrl' )[0]
    _locShape = cmds.listRelatives(_loc, s=True)[0]
    _grp      = cmds.group( _loc, name=_prefix+'_Offset' )

    # ctrl Shape
    if _displayHandle:
        cmds.setAttr( _loc+'.displayHandle', 1)
        cmds.setAttr( _locShape+'.localScale', 0, 0, 0, type='double3')

    # set default Position
    cmds.setAttr( _grp+'.t', _position[0], _position[1], _position[2], type='double3')
    cmds.setAttr( _grp+'.r', _rotation[0], _rotation[1], _rotation[2], type='double3')

    # constraint
    if _constraint == 'parent':
        cmds.parentConstraint(_constraintTarget,_grp)
    elif _constraint == 'point':
        cmds.pointConstraint(_constraintTarget,_grp)
    elif _constraint == 'orient':
        cmds.orientConstraint(_constraintTarget,_grp)

    return [ _grp, _loc ]

def displayOverride( _obj, **kwargs):
    _type = 0
    _color = 0

    if type(_obj)==str or type(_obj)==unicode:
        _obj = [_obj]

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

    # ½ÇÇà
    for _node in _obj:
        cmds.setAttr ( _node+'.overrideEnabled', 1)
        cmds.setAttr ( _node+'.overrideDisplayType', _type)
        cmds.setAttr ( _node+'.overrideColor', _color)
