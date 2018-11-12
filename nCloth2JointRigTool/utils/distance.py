import maya.api.OpenMaya as om
import maya.cmds as cmds

# returns the closest vertex given a mesh and a position [x,y,z] in world space.
# Uses om.MfnMesh.getClosestPoint() returned face ID and iterates through face's vertices.


def getClosestVertex(mayaMesh, pos=[0, 0, 0]):
    # using MVector type to represent position
    mVector = om.MVector(pos)
    selectionList = om.MSelectionList()
    selectionList.add(mayaMesh)
    dPath = selectionList.getDagPath(0)
    mMesh = om.MFnMesh(dPath)

    # getting closest face ID
    ID = mMesh.getClosestPoint(om.MPoint(mVector), space=om.MSpace.kWorld)[1]

    # face's vertices list
    list = cmds.ls(cmds.polyListComponentConversion(mayaMesh+'.f['+str(ID)+']', ff=True, tv=True), flatten=True)

    # setting vertex [0] as the closest one
    d = mVector-om.MVector(cmds.xform(list[0], t=True, ws=True, q=True))

    # using distance squared to compare distance
    smallestDist2 = d.x*d.x+d.y*d.y+d.z*d.z
    closest = list[0]
    # iterating from vertex [1]
    for i in range(1, len(list)):
        d = mVector - om.MVector(cmds.xform(list[i], t=True, ws=True, q=True))
        d2 = d.x*d.x+d.y*d.y+d.z*d.z
        if d2 < smallestDist2:
            smallestDist2 = d2
            closest = list[i]

    return closest