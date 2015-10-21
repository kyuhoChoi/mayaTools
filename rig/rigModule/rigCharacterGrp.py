# coding=utf-8
import pymel.core as pm

def rigCharacterGrp():
    ''' 캐릭터 베이스 생성 '''
    #
    # 최상위 그룹 리깅
    Group = pm.group(n='Group', em=True)
    Root = pm.curve( d=3, p=[ (-0.068059129190802453, 0.0, 0.49515769319022762), (-0.045372752829582474, 0.0, 0.52918733713445421), (-0.022686376468362496, 0.0, 0.56321698107868068), (-1.0714251708066058e-10, 0.0, 0.59724662502290737), (0.022686376254077462, 0.0, 0.56321698107868068), (0.04537275261529744, 0.0, 0.52918733713445421), (0.068059128976517419, 0.0, 0.49515769319022762), (0.17494851557291896, 0.0, 0.47998907510370475), (0.37963820444740304, 0.0, 0.37963820444740298), (0.47998907510370487, 0.0, 0.17494851557291891), (0.49515769355710038, 0.0, 0.068059128879015496), (0.52918733713445409, 0.0, 0.045372752615297385), (0.56321698107868079, 0.0, 0.022686376254077378), (0.59724662502290737, 0.0, -1.0714257259181181e-10), (0.56321698107868079, 0.0, -0.022686376468362524), (0.52918733713445409, 0.0, -0.04537275282958253), (0.49515769319022745, 0.0, -0.068059129190802536), (0.47998907510370487, 0.0, -0.17494851578720411), (0.37963820444740304, 0.0, -0.37963820466168813), (0.17494851557291899, 0.0, -0.4799890753179899), (0.068059128879015551, 0.0, -0.49515769377138547), (0.045372752567678483, 0.0, -0.52918733763445291), (0.022686376230267983, 0.0, -0.56321698154296529), (-1.0714251708066058e-10, 0.0, -0.59724662545147766), (-0.022686376444553017, 0.0, -0.56321698154296529), (-0.045372752781963517, 0.0, -0.52918733763445291), (-0.068059129119374021, 0.0, -0.49515769372594071), (-0.174948515787204, 0.0, -0.4799890753179899), (-0.37963820466168807, 0.0, -0.37963820466168813), (-0.4799890753179899, 0.0, -0.17494851578720411), (-0.49515769377138541, 0.0, -0.068059129093300641), (-0.5291873376344528, 0.0, -0.045372752781963621), (-0.56321698154296518, 0.0, -0.022686376444553125), (-0.59724662545147744, 0.0, -1.0714257259181181e-10), (-0.56321698154296518, 0.0, 0.022686376230267979), (-0.5291873376344528, 0.0, 0.045372752567678476), (-0.49515769372594048, 0.0, 0.068059128905088973), (-0.47998907531798995, 0.0, 0.17494851557291877), (-0.37963820466168807, 0.0, 0.37963820444740298), (-0.17494851578720391, 0.0, 0.47998907510370475), (-0.068059129093300405, 0.0, 0.49515769355710032) ], k=[ 14.04717124, 14.04717124, 14.04717124, 15.0, 15.0, 15.0, 15.95282876, 15.95282876, 15.95282876, 16.778606267, 17.604383774, 17.604383774, 17.604383774, 18.557212534, 18.557212534, 18.557212534, 19.510041294, 19.510041294, 19.510041294, 20.335818801, 21.161596308, 21.161596308, 21.161596308, 22.114425067, 22.114425067, 22.114425067, 23.067253826, 23.067253826, 23.067253826, 23.893031333, 24.71880884, 24.71880884, 24.71880884, 25.671637599, 25.671637599, 25.671637599, 26.624466358, 26.624466358, 26.624466358, 27.450243865, 28.276021372, 28.276021372, 28.276021372 ] )
    Motion = pm.group(n='Motion', em=True)
    Deformer = pm.group(n='Deformer', em=True)
    Geometry = pm.group(n='Geometry', em=True)
    previewGeo_grp = pm.group(n='PreviewGeo_grp', em=True)
    renderGeo_grp  = pm.group(n='RenderGeo_grp',  em=True)

    #
    # Root 리깅
    Root.s.set(100,100,100)
    pm.makeIdentity( Root, apply=True, t=1,r=1,s=1,n=0)
    Root.rename( 'Reference' )

    # diplayGeo
    Root.addAttr( "displayGeo", at="enum", en="Preview:Render:", keyable=False )
    Root.addAttr( "displayPreviewGeo", at="bool", keyable=False )
    Root.addAttr( "displayRenderGeo",  at="bool", keyable=False )
    Root.displayGeo.showInChannelBox(True)
    Root.displayPreviewGeo >> previewGeo_grp.v
    Root.displayRenderGeo  >> renderGeo_grp.v
    pm.setDrivenKeyframe( Root.displayPreviewGeo, currentDriver=Root.displayGeo, driverValue=0, value=1, inTangentType='linear', outTangentType='linear' )
    pm.setDrivenKeyframe( Root.displayPreviewGeo, currentDriver=Root.displayGeo, driverValue=1, value=0, inTangentType='linear', outTangentType='linear' )
    pm.setDrivenKeyframe( Root.displayRenderGeo,  currentDriver=Root.displayGeo, driverValue=0, value=0, inTangentType='linear', outTangentType='linear' )
    pm.setDrivenKeyframe( Root.displayRenderGeo,  currentDriver=Root.displayGeo, driverValue=1, value=1, inTangentType='linear', outTangentType='linear' )

    Root.addAttr( 'scaleFix', at='double')
    Root.scaleFix.showInChannelBox(True)

    scaleFix_DIV = pm.createNode( 'multiplyDivide', n='scaleFix_DIV')
    scaleFix_DIV.op.set(2) # div
    scaleFix_DIV.input1.set( 1,1,1 )
    Root.sy >> scaleFix_DIV.input2X
    scaleFix_DIV.outputX  >> Root.scaleFix

    Root.overrideEnabled.set( True )
    Root.overrideColor.set( 13 )

    #
    # 그루핑
    pm.parent( previewGeo_grp, renderGeo_grp, Geometry)
    pm.parent( Motion, Deformer, Root )
    pm.parent( Root, Geometry, Group)

    #
    # 어트리뷰트 조정
    Geometry.it.set(False)
    for obj in [Group, Geometry]:
        for attr in ['tx','ty','tz', 'rx','ry','rz', 'sx','sy','sz']:
            obj.setAttr(attr, keyable=False, lock=True, channelBox=False )