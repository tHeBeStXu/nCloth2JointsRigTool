import maya.cmds as cmds
import maya.mel as mel


def createBlendSystem(simJointList, ctrlJointList, skinJointList, settingGrp):

    for i in xrange(len(skinJointList)):

        # translation
        transBlendColor = cmds.createNode('blendColors', n='TransBlend_%s' % str(i))
        # ctrlJoint
        cmds.connectAttr(ctrlJointList[i] + '.t', transBlendColor + '.color1', f=1)
        # simJoint
        cmds.connectAttr(simJointList[i] + '.t', transBlendColor + '.color2', f=1)
        # setting group
        cmds.connectAttr(settingGrp + '.Sim2Bake', transBlendColor + '.blender', f=1)
        # skinJoint
        cmds.connectAttr(transBlendColor + '.output', skinJointList[i] + '.t', f=1)
        cmds.select(cl=1)

        # rotation
        rotBlendColor = cmds.createNode('blendColors', n='RotBlend_%s' % str(i))
        # ctrlJoint
        cmds.connectAttr(ctrlJointList[i] + '.r', rotBlendColor + '.color1', f=1)
        # simJoint
        cmds.connectAttr(simJointList[i] + '.r', rotBlendColor + '.color2', f=1)
        # setting group
        cmds.connectAttr(settingGrp + '.Sim2Bake', rotBlendColor + '.blender', f=1)
        # skinJoint
        cmds.connectAttr(rotBlendColor + '.output', skinJointList[i] + '.r', f=1)
        cmds.select(cl=1)


def createSettingGrp(name):
    settingGrp = cmds.group(n=name + '_SettingGrp', em=1)

    # set visibility to false
    cmds.setAttr(settingGrp + '.v', 0)

    for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']:
        cmds.setAttr(settingGrp + '.' + attr, keyable=0, lock=1, channelBox=0)

    if not cmds.attributeQuery('Sim2Bake', node=settingGrp, exists=1):
        cmds.addAttr(settingGrp, longName='Sim2Bake', at="float", min=0, max=1, keyable=1)

    for attr in ['simJoint', 'skinJoint', 'ctrlJoint', 'bakeCtrl', 'bakeCtrlGrp', 'nucleus', 'nCloth', 'proxyMesh']:
        if not cmds.attributeQuery(attr, node=settingGrp, exists=1):
            cmds.addAttr(settingGrp, ln=attr, at='message')

    cmds.select(cl=1)
    return settingGrp


def placeJnt2Vert(vertex, joint):
    """
    translate joint to target vertex
    :param vertex: str, target vertex
    :param joint: str, joint you want to translate
    :return: list[float, float, float], the position of the vertex
    """
    vertexPos = cmds.xform(vertex, ws=1, q=1, t=1)
    cmds.xform(joint, t=vertexPos, ws=1)

    return vertexPos


def createEmitter(vertex, meshName):
    """
    create a point emitter
    :param vertex: str, vertex name
    :return: dict(str), point Emitter, meshTransform Node.
    """
    cmds.select(cl=1)

    cmds.select(vertex)
    # create emitter on selected vertex
    emitterList = cmds.emitter(n=vertex + '_EM', type='omni', r=100, sro=0, nuv=0, cye='none', cyi=1, spd=1, srn=0, nsp=1,
                               tsp=0, mxd=0, mnd=0, dx=1, dy=0, dz=0, sp=0)
    particle = cmds.particle(n=vertex + '_PTC')
    cmds.connectDynamic(particle[0], em=emitterList[-1])
    cmds.select(cl=1)

    emitter = emitterList[-1]

    cmds.select(cl=1)

    if not cmds.attributeQuery('bindMesh', node=emitter, exists=1):
        cmds.addAttr(emitter, ln='bindMesh', at='message')

    if not cmds.attributeQuery('bindEmitter', node=meshName, exists=1):
        cmds.addAttr(meshName, ln='bindEmitter', at='message')

    if not cmds.attributeQuery('targetJoint', node=emitter, exists=1):
        cmds.addAttr(emitter, ln='targetJoint', exists=1)

    cmds.connectAttr(meshName + '.bindEmitter', emitter + '.bindMesh', f=1)

    return {'emitter': emitter,
            'particle': particle[0],
            'particleShape': particle[-1]}


def createNucleus(name):
    """
    create nucleus by given name
    :param name: str, name of the nucleus
    :return: nucleus
    """
    nucleus = cmds.createNode('nucleus', n=name + '_Nucleus_#')

    # connect attr
    cmds.connectAttr('time1.outTime', nucleus + '.currentTime')

    # add attr
    if not cmds.attributeQuery('nucleus', node=nucleus, exists=1):
        cmds.addAttr(nucleus, longName='nucleus', at='message', multi=1)
    cmds.select(cl=1)

    return nucleus


def createNCloth(nClothMesh, nucleus=None):
    """
    create nCloth on target mesh
    :param nClothMesh: str, the nMesh you want to create nCloth on
    :param nucleus: str, specified nucleus
    :return: dict, {'nClothShape', 'nClothTrans', 'nucleus'}
    """

    cmds.select(cl=1)
    # create nCloth on selected mesh
    cmds.select(nClothMesh)
    nClothShape = mel.eval('createNCloth 0;')

    nClothTrans = cmds.listRelatives(nClothShape, p=1, s=0, c=0)[0]
    nClothTrans = cmds.rename(nClothTrans, nClothMesh + '_nCloth')
    nClothShape = cmds.listRelatives(nClothTrans, c=1, s=1, p=0)[0]

    connectedNucleus = cmds.listConnections(nClothShape + '.startFrame', source=1, destination=0)
    if connectedNucleus:
        currentNucleus = cmds.rename(connectedNucleus[0], nClothMesh + '_Nucleus')

    # not the taret nucleus
    if nucleus:
        if nucleus != currentNucleus:
            # disconnect nCloth from current Nucleus
            for attr in ['currentState', 'startState', 'nextState', 'startFrame']:
                connectedAttr = cmds.listConnections(nClothShape + '.' + attr, connections=1, plugs=1)
                try:
                    cmds.disconnectAttr(connectedAttr[0], connectedAttr[-1])
                except:
                    cmds.disconnectAttr(connectedAttr[-1], connectedAttr[0])

            # connect nCloth to target nucleus
            for sourceAttr, destAttr in zip(['currentState', 'startState'], ['inputActive', 'inputActiveStart']):
                index = findSingleAvailableIndex(nucleus + '.' + destAttr)
                cmds.connectAttr(nClothShape + '.' + sourceAttr, nucleus + '.' + destAttr + '[%s]' % str(index), f=1)

            # connect nucleus to ncloth
            for sourceAttr, destAttr in zip(['outputObjects', 'startFrame'], ['nextState', 'startFrame']):
                if cmds.attributeQuery(sourceAttr, node=nucleus, multi=1):
                    index = findSingleAvailableIndex(nucleus + '.' + sourceAttr)
                    cmds.connectAttr(nucleus + '.' + sourceAttr + '[%s]' % str(index), nClothShape + '.' + destAttr, f=1)
                else:
                    cmds.connectAttr(nucleus + '.' + sourceAttr, nClothShape + '.' + destAttr, f=1)

            cmds.select(cl=1)

    else:
        nucleus = currentNucleus

    # add attr
    if not cmds.attributeQuery('nCloth', node=nClothShape, exists=1):
        cmds.addAttr(nClothShape, ln='nCloth', at='message', multi=1)

    if not cmds.attributeQuery('nucleus', node=nucleus, exists=1):
        cmds.addAttr(nucleus, ln='nucleus', at='message', multi=1)

    cmds.select(cl=1)

    return {'nucleus': nucleus,
            'nClothShape': nClothShape,
            'nClothTrans': nClothTrans}


def findSettingGrp():
    """
    find and return setting group for selection
    :return: list(str), setting groups
    """
    transformNodes = cmds.ls(type='transform')

    settingGrps = []

    if transformNodes:
        for i in transformNodes:
            if cmds.attributeQuery('Sim2Bake', node=i, exists=1):
                settingGrps.append(i)

    return settingGrps

#####################################
# find same multi attr index method #
#####################################


def findSingleAvailableIndex(attr):
    """
    find the first free array index of multi-attribute
    :param attr: str, attribute without index
    :return: int, index of free array.
    """
    index = 0

    while index < 10000:
        fullAttr = attr + '[%s]' % (str(index))

        inputAttr = cmds.listConnections(fullAttr, plugs=1)

        if not inputAttr:
            return index

        index += 1


def findDoubleAvailableIndex(firstAttr, secondAttr):
    """
    find the common free array index of 3 multi-attributes.
    :param firstAttr: str, first attribute without index.
    :param secondAttr:str, second attribute without index.
    :return:int, index of free array.
    """
    index = 0

    while index < 10000:
        firstFullAttr = firstAttr + '[%s]' % (str(index))
        secondFullAttr = secondAttr + '[%s]' % (str(index))

        firstInputAttr = cmds.listConnections(firstFullAttr, plugs=1)
        secondInputAttr = cmds.listConnections(secondFullAttr, plugs=1)

        if not firstInputAttr and not secondInputAttr:
            return index

        index += 1


def findTribleAvailableIndex(firstAttr, secondAttr, thirdAttr):
    """
    find the common free array index of 3 multi-attributes.
    :param firstAttr: str, first attribute without index.
    :param secondAttr:str, second attribute without index.
    :param thirdAttr:str, third attribute without index.
    :return:int, index of free array.
    """
    index = 0

    while index < 10000:
        firstFullAttr = firstAttr + '[%s]' % (str(index))
        secondFullAttr = secondAttr + '[%s]' % (str(index))
        thirdFullAttr = thirdAttr + '[%s]' % (str(index))

        firstInputAttr = cmds.listConnections(firstFullAttr, plugs=1)
        secondInputAttr = cmds.listConnections(secondFullAttr, plugs=1)
        thirdInputAttr = cmds.listConnections(thirdFullAttr, plugs=1)

        if not firstInputAttr:
            if not secondInputAttr:
                if not thirdInputAttr:
                    return index

        index += 1
