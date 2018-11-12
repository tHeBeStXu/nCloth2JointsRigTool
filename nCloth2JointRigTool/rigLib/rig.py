import maya.cmds as cmds
import lib
from ..utils import name
from ..utils import distance
from ..base import control

reload(lib)
reload(name)
reload(distance)
reload(control)


def build(proxyVertexList, nucleus=None, jointParent='', rigScale=1.0):
    """
    build nCloth 2 Joint system
    :param proxyVertexList: list(str), vertices of sim proxy mesh
    :param nucleus: str, target nucleus
    :param jointParent: str, skin joints parent position
    :param rigScale: float, rig scale fo the ctrl
    :return: None
    """
    #############
    # Mesh Part #
    #############
    meshName = name.removeNodeAttr(proxyVertexList[0])

    if not cmds.attributeQuery('proxyMesh', node=meshName, exists=1):
        cmds.addAttr(meshName, ln='proxyMesh', at='message')

    skinMesh = cmds.duplicate(meshName, n=meshName + '_Skin')[0]

    # set sim mesh visibility Off
    cmds.setAttr(meshName + '.v', 0)

    #################
    # setting group #
    #################
    settingGrp = lib.createSettingGrp(meshName)

    ##############
    # joint part #
    ##############

    # sim joint part
    simJointList = []
    for vertex in proxyVertexList:

        cmds.select(cl=1)
        joint = cmds.joint(n=meshName + '_SimJnt_#')
        cmds.select(cl=1)
        simJointList.append(joint)

        if not cmds.attributeQuery('simJoint', node=joint, exists=1):
            cmds.addAttr(joint, ln='simJoint', at='message')

        if not cmds.attributeQuery('targetEmitter', node=joint, exists=1):
            cmds.addAttr(joint, ln='targetEmitter', at='message')

        # place joint to vertex
        lib.placeJnt2Vert(vertex=vertex, joint=joint)

        cmds.select(cl=1)

    if jointParent:
        cmds.select(cl=1)
        parentJoint = cmds.joint(n=meshName + '_SimJnt_P')
        cmds.select(cl=1)

        simJointList.append(parentJoint)

        if not cmds.attributeQuery('simJoint', node=parentJoint, exists=1):
            cmds.addAttr(parentJoint, ln='simJoint', at='message')

        if not cmds.attributeQuery('targetEmitter', node=joint, exists=1):
            cmds.addAttr(parentJoint, ln='targetEmitter', at='message')

        cmds.delete(cmds.parentConstraint(jointParent, parentJoint, mo=0))

        for joint in simJointList[:-1]:
            cmds.parent(joint, simJointList[-1])

    # skin joint part
    skinJointList = []
    for vertex in proxyVertexList:

        cmds.select(cl=1)
        joint = cmds.joint(n=meshName + '_SkinJnt_#')
        cmds.select(cl=1)

        skinJointList.append(joint)

        if not cmds.attributeQuery('skinJoint', node=joint, exists=1):
            cmds.addAttr(joint, ln='skinJoint', at='message')

        if not cmds.attributeQuery('targetVertex', node=joint, exists=1):
            cmds.addAttr(joint, ln='targetVertex', dt='string')

        if not cmds.attributeQuery('slaveJoint', node=joint, exists=1):
            cmds.addAttr(joint, ln='slaveJoint', at='message')

        # place joint to vertex
        vertexPos = lib.placeJnt2Vert(vertex=vertex, joint=joint)

        # set vertex
        closestVertex = distance.getClosestVertex(mayaMesh=skinMesh, pos=vertexPos)

        cmds.setAttr(joint + '.targetVertex', str(closestVertex), type='string', lock=1)

    if jointParent:
        cmds.select(cl=1)
        parentJoint = cmds.joint(n=meshName + '_SkinJnt_P')
        cmds.select(cl=1)

        skinJointList.append(parentJoint)

        if not cmds.attributeQuery('skinJoint', node=parentJoint, exists=1):
            cmds.addAttr(parentJoint, ln='skinJoint', at='message')

        if not cmds.attributeQuery('slaveJoint', node=parentJoint, exists=1):
            cmds.addAttr(parentJoint, ln='slaveJoint', at='message')

        cmds.delete(cmds.parentConstraint(jointParent, parentJoint, mo=0))

        for joint in skinJointList[:-1]:
            cmds.parent(joint, skinJointList[-1])

    # control joint part
    controlJointList = []
    ctrlList = []
    ctrlGrpList = []
    for vertex in proxyVertexList:
        cmds.select(cl=1)
        joint = cmds.joint(n=meshName + '_CtrlJnt_#')
        cmds.select(cl=1)
        controlJointList.append(joint)

        if not cmds.attributeQuery('ctrlJoint', node=joint, exists=1):
            cmds.addAttr(joint, ln='ctrlJoint', at='message')

        lib.placeJnt2Vert(vertex=vertex, joint=joint)

        ctrl = control.Control(prefix=joint,
                               rigPartName='',
                               scale=rigScale,
                               translateTo=joint,
                               rotateTo=joint,
                               shape='circleY')

        cmds.pointConstraint(ctrl.C, joint, mo=0)
        cmds.orientConstraint(ctrl.C, joint, mo=0)

        if not cmds.attributeQuery('bakeCtrl', node=ctrl.C, exists=1):
            cmds.addAttr(ctrl.C, ln='bakeCtrl', at='message')

        if not cmds.attributeQuery('bakeCtrlGrp', node=ctrl.Off, exists=1):
            cmds.addAttr(ctrl.Off, ln='bakeCtrlGrp', at='message')

        ctrlList.append(ctrl.C)
        ctrlGrpList.append(ctrl.Off)

    if jointParent:
        cmds.select(cl=1)
        parentJoint = cmds.joint(n=meshName + '_CtrlJnt_P')
        cmds.select(cl=1)

        controlJointList.append(parentJoint)

        if not cmds.attributeQuery('ctrlJoint', node=parentJoint, exists=1):
            cmds.addAttr(parentJoint, ln='ctrlJoint', at='message')

        cmds.delete(cmds.parentConstraint(jointParent, parentJoint, mo=0))

        for joint in controlJointList[:-1]:
            cmds.parent(joint, controlJointList[-1])

    ######################
    # build blend system #
    ######################
    lib.createBlendSystem(simJointList=simJointList,
                          skinJointList=skinJointList,
                          ctrlJointList=controlJointList,
                          settingGrp=settingGrp)

    #####################
    # skin cluster part #
    #####################
    # skin skintJoints with skin Mesh
    skinCluster = cmds.skinCluster(skinJointList[:], skinMesh, mi=3, n=skinMesh + '_skinCluster')
    cmds.select(cl=1)

    # set 100% skin weight of each simJoint and targetVertex
    if not jointParent:
        for joint in skinJointList:
            vertex = cmds.getAttr(joint + '.targetVertex')

            cmds.skinPercent(skinCluster[0], vertex, transformValue=[(joint, 1.0)])

    else:
        for joint in skinJointList[:-1]:
            vertex = cmds.getAttr(joint + '.targetVertex')
            cmds.skinPercent(skinCluster[0], vertex, transformValue=[(joint, 1.0)])
    cmds.select(cl=1)

    ###############
    # nCloth Part #
    ###############

    if not nucleus:
        nCloth_nucleus = lib.createNCloth(nClothMesh=meshName)
    else:
        nCloth_nucleus = lib.createNCloth(nClothMesh=meshName, nucleus=nucleus)


    ################
    # Emitter Part #
    ################
    emitterList = []
    particleList = []
    for vertex in proxyVertexList:

        emitterParticle = lib.createEmitter(vertex=vertex, meshName=meshName)

        cmds.setAttr(emitterParticle['particleShape'] + '.maxCount', 0)

        emitterList.append(emitterParticle['emitter'])
        particleList.append(emitterParticle['particle'])

    # parentConstraint & connect attr
    for i in xrange(len(proxyVertexList)):

        cmds.parentConstraint(emitterList[i], simJointList[i], mo=0)

        cmds.connectAttr(emitterList[i] + '.targetJoint', simJointList[i] + '.targetEmitter', f=1)

    ###############
    # connect all #
    ###############

    for joint in simJointList:
        cmds.connectAttr(settingGrp + '.simJoint', joint + '.simJoint', f=1)

    for joint in skinJointList:
        cmds.connectAttr(settingGrp + '.skinJoint', joint + '.skinJoint', f=1)

    for joint in controlJointList:
        cmds.connectAttr(settingGrp + '.ctrlJoint', joint + '.ctrlJoint', f=1)

    for ctrl in ctrlList:
        cmds.connectAttr(settingGrp + '.bakeCtrl', ctrl + '.bakeCtrl', f=1)

    for Grp in ctrlGrpList:
        cmds.connectAttr(settingGrp + '.bakeCtrlGrp', Grp + '.bakeCtrlGrp', f=1)

    cmds.connectAttr(settingGrp + '.nucleus', nCloth_nucleus['nucleus'] + '.nucleus', f=1)
    cmds.connectAttr(settingGrp + '.nCloth', nCloth_nucleus['nClothShape'] + '.nCloth', f=1)
    cmds.connectAttr(settingGrp + '.proxyMesh', meshName + '.proxyMesh', f=1)

    rootGrp = cmds.group(n=meshName + '_nCloth_Root_Grp', em=1)
    jointGrp = cmds.group(n=meshName + '_nCloth_Joint_Grp', em=1)
    CtrlGrp = cmds.group(n=meshName + '_nCloth_Ctrl_Grp', em=1)
    particleGrp = cmds.group(n=meshName + '_nCloth_Particle_Grp', em=1)

    for Grp in ctrlGrpList:
        cmds.parent(Grp, CtrlGrp)

    for particle in particleList:
        cmds.parent(particle, particleGrp)

    if jointParent:
        cmds.parent(skinJointList[-1], jointGrp)
        cmds.parent(simJointList[-1], jointGrp)
        cmds.parent(controlJointList[-1], jointGrp)

        cmds.setAttr(simJointList[-1] + '.v', 0)
        cmds.setAttr(controlJointList[-1] + '.v', 0)

    else:
        skinJointGrp = cmds.group(n=meshName + '_skinJnt_Grp', em=1)
        for joint in skinJointList:
            cmds.parent(joint, skinJointGrp)

        simJointGrp = cmds.group(n=meshName + '_simJnt_Grp', em=1)
        cmds.setAttr(simJointGrp + '.v', 0)
        for joint in simJointList:
            cmds.parent(joint, simJointGrp)

        ctrlJointGrp = cmds.group(n=meshName + '_ctrlJnt_Grp', em=1)
        cmds.setAttr(ctrlJointGrp + '.v', 0)
        for joint in controlJointList:
            cmds.parent(joint, ctrlJointGrp)

        cmds.parent(ctrlJointGrp, CtrlGrp)
        cmds.parent(simJointGrp, CtrlGrp)
        cmds.parent(skinJointGrp, CtrlGrp)

    cmds.parent(CtrlGrp, rootGrp)
    cmds.parent(jointGrp, rootGrp)
    cmds.parent(particleGrp, rootGrp)
    cmds.parent(settingGrp, rootGrp)
    cmds.parent(meshName, rootGrp)
    cmds.parent(nCloth_nucleus['nClothTrans'], rootGrp)
    cmds.parent(nCloth_nucleus['nucleus'], rootGrp)
    cmds.parent(skinMesh, rootGrp)


