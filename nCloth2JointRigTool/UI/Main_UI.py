from PySide2 import QtWidgets, QtGui, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import logging
from ..rigLib import lib
from functools import partial
import inspect
import Splitter_UI
from ..rigLib import rig
from ..utils import name

reload(lib)
reload(rig)
reload(Splitter_UI)
reload(name)

logging.basicConfig()
logger = logging.getLogger('nCloth2JointRigTool')
logger.setLevel(logging.DEBUG)


def getMayaWindow():
    """
    get the mayaMainWindow as parent
    :return: mayaMainWindow Ptr
    """
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QMainWindow)


class MainUI(QtWidgets.QDialog):
    def __init__(self):
        try:
            cmds.deleteUI('nCloth2JointRigTool')
        except:
            logger.info('No previous UI exists!')

        super(MainUI, self).__init__(parent=getMayaWindow())

        self.setModal(False)
        self.setObjectName('nCloth2JointRigTool')
        self.setWindowTitle('nCloth To Joints')

        self.buildUI()

        self.setGrps = []
        self.currentSetGrp = None

        self.show()
        self.refreshListWidget()

    def buildUI(self):
        """
        Build the Main UI
        :return: None
        """
        self.setFixedSize(380, 515)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.mainWidget = QtWidgets.QTabWidget()
        self.mainLayout.addWidget(self.mainWidget)

        self.rigWidget = QtWidgets.QWidget()
        self.bakeWidget = QtWidgets.QWidget()

        # add widget to TabWidget
        self.mainWidget.addTab(self.rigWidget, 'Create')
        self.mainWidget.addTab(self.bakeWidget, 'Bake')

        self.mainWidget.currentChanged.connect(self.populateSettingGrp)

        ######################
        # Create widget Part #
        ######################

        self.rigLayout = QtWidgets.QVBoxLayout()
        self.rigWidget.setLayout(self.rigLayout)

        self.formWidget = QtWidgets.QWidget()
        self.formLayout = QtWidgets.QFormLayout()
        self.formWidget.setLayout(self.formLayout)

        self.rowItem = {}
        self.tupe = inspect.getargspec(func=rig.build)
        for i in self.tupe[0]:
            layout = QtWidgets.QHBoxLayout()
            self.rowItem[i] = QtWidgets.QLineEdit()
            button = QtWidgets.QPushButton('<<<')

            layout.addWidget(self.rowItem[i])
            layout.addWidget(button)

            button.clicked.connect(partial(self.setEditLine, self.rowItem[i]))

            self.formLayout.addRow(i, layout)

        self.rigLayout.addWidget(self.formWidget)

        # selection Splitter
        self.listSplitter = Splitter_UI.Splitter('Check & Select')
        self.rigLayout.addWidget(self.listSplitter)

        # selection widget
        selectionWidget = QtWidgets.QWidget()
        selectionLayout = QtWidgets.QVBoxLayout()
        selectionWidget.setLayout(selectionLayout)

        filterWidget = QtWidgets.QWidget()
        filterLayout = QtWidgets.QHBoxLayout()
        filterWidget.setLayout(filterLayout)

        filterLable = QtWidgets.QLabel('Filter:   ')
        self.jointCheck = QtWidgets.QCheckBox('Joint')
        self.nucleusCheck = QtWidgets.QCheckBox('Nucleus')

        filterLayout.addWidget(filterLable)
        filterLayout.addWidget(self.jointCheck)
        filterLayout.addWidget(self.nucleusCheck)

        self.jointCheck.stateChanged.connect(self.refreshListWidget)
        self.nucleusCheck.stateChanged.connect(self.refreshListWidget)

        self.rigLayout.addWidget(selectionWidget)

        self.listWidget = QtWidgets.QListWidget()
        # single selection
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        selectionLayout.addWidget(filterWidget)
        selectionLayout.addWidget(self.listWidget)

        # create button Splitter
        self.createRigSplitter = Splitter_UI.Splitter()
        self.rigLayout.addWidget(self.createRigSplitter)

        # button
        self.createRigBtn = QtWidgets.QPushButton('Create nCloth Joints Rig!')
        self.createRigBtn.clicked.connect(self.buildRig)
        self.rigLayout.addWidget(self.createRigBtn)

        ####################
        # Bake widget Part #
        ####################

        self.bakeLayout = QtWidgets.QVBoxLayout()
        self.bakeWidget.setLayout(self.bakeLayout)

        # setting Grp splitter
        self.settingSplitter = Splitter_UI.Splitter(text='SETTING GROUPS')
        self.bakeLayout.addWidget(self.settingSplitter)

        # setting Grp comboBox
        self.setGrpComboBox = QtWidgets.QComboBox()
        self.setGrpComboBox.currentIndexChanged.connect(self.setCurrentSetGrp)
        self.bakeLayout.addWidget(self.setGrpComboBox)

        # selection spliter
        self.selSplitter = Splitter_UI.Splitter(text='SELECTION')
        self.bakeLayout.addWidget(self.selSplitter)

        # selection Btns
        self.selGridLaytout = QtWidgets.QGridLayout()

        self.selnClothBtn = QtWidgets.QPushButton('Select nCloth')
        self.selNucleusBtn = QtWidgets.QPushButton('Select Nucleus')
        self.selBakeCtrlGrpBtn = QtWidgets.QPushButton('Select Bake CtrlGrps')
        self.selBakeCtrlBtn = QtWidgets.QPushButton('Select Bake Ctrls')
        self.selSimJntBtn = QtWidgets.QPushButton('Select Sim Joints')
        self.selCtrlJntBtn = QtWidgets.QPushButton('Select Ctrl Joints')
        self.selSkinJntBtn = QtWidgets.QPushButton('Select Skin Joints')
        self.selSimMeshBtn = QtWidgets.QPushButton('Select Proxy Mesh')
        self.selSetGrpBtn = QtWidgets.QPushButton('Select Setting Group')

        self.selGridLaytout.addWidget(self.selnClothBtn, 0, 0, 1, 2)
        self.selGridLaytout.addWidget(self.selNucleusBtn, 0, 2, 1, 2)
        self.selGridLaytout.addWidget(self.selBakeCtrlGrpBtn, 1, 0, 1, 2)
        self.selGridLaytout.addWidget(self.selBakeCtrlBtn, 1, 2, 1, 2)
        self.selGridLaytout.addWidget(self.selSimJntBtn, 2, 0, 1, 2)
        self.selGridLaytout.addWidget(self.selCtrlJntBtn, 2, 2, 1, 2)
        self.selGridLaytout.addWidget(self.selSkinJntBtn, 3, 0, 1, 2)
        self.selGridLaytout.addWidget(self.selSimMeshBtn, 3, 2, 1, 2)
        self.selGridLaytout.addWidget(self.selSetGrpBtn, 4, 1, 1, 2)

        self.selnClothBtn.clicked.connect(partial(self.selectSpecifiedItem, 'nCloth'))
        self.selNucleusBtn.clicked.connect(partial(self.selectSpecifiedItem, 'nucleus'))
        self.selBakeCtrlGrpBtn.clicked.connect(partial(self.selectSpecifiedItem, 'bakeCtrlGrp'))
        self.selBakeCtrlBtn.clicked.connect(partial(self.selectSpecifiedItem, 'bakeCtrl'))
        self.selSimJntBtn.clicked.connect(partial(self.selectSpecifiedItem, 'simJoint'))
        self.selCtrlJntBtn.clicked.connect(partial(self.selectSpecifiedItem, 'ctrlJoint'))
        self.selSkinJntBtn.clicked.connect(partial(self.selectSpecifiedItem, 'skinJoint'))
        self.selSimMeshBtn.clicked.connect(partial(self.selectSpecifiedItem, 'proxyMesh'))
        self.selSetGrpBtn.clicked.connect(self.selectCurrentSetGrp)

        self.bakeLayout.addLayout(self.selGridLaytout)

        # bake Splitter
        self.bakeSplitter = Splitter_UI.Splitter(text='BAKE')
        self.bakeLayout.addWidget(self.bakeSplitter)

        # bake Button
        self.bakeBtnLayout = QtWidgets.QHBoxLayout()
        self.bakeSimulationBtn = QtWidgets.QPushButton('Bake nCloth SIM on Ctrls')
        self.bakeBtnLayout.addWidget(self.bakeSimulationBtn)
        self.bakeLayout.addLayout(self.bakeBtnLayout)
        self.bakeSimulationBtn.clicked.connect(self.bakeSimulation2Ctrls)

        # replace Splitter
        self.replaceSplitter = Splitter_UI.Splitter(text='NUCLEUS')
        self.bakeLayout.addWidget(self.replaceSplitter)

        # replace Layout
        self.replaceLayout = QtWidgets.QGridLayout()

        self.repNecleusComBox = QtWidgets.QComboBox()
        self.repNecleusBtn = QtWidgets.QPushButton('Replace')
        self.repNecleusBtn.clicked.connect(self.replaceNucleus)

        self.replaceLayout.addWidget(self.repNecleusComBox, 0, 0, 1, 2)
        self.replaceLayout.addWidget(self.repNecleusBtn, 0, 2, 1, 1)

        self.bakeLayout.addLayout(self.replaceLayout)

        # to be continued... splitter
        self.toBeContinuedSplitter = Splitter_UI.Splitter(text='TO BE CONTINUED...')
        self.bakeLayout.addWidget(self.toBeContinuedSplitter)

    def buildRig(self):
        """
        Build dynamic chain rig
        :return: None
        """
        proxyVertexList = eval(self.rowItem['proxyVertexList'].text())
        nucleus = self.rowItem['nucleus'].text()
        jointParent = self.rowItem['jointParent'].text()
        rigScale = eval(self.rowItem['rigScale'].text())

        # build
        rig.build(proxyVertexList=proxyVertexList,
                  nucleus=nucleus,
                  jointParent=jointParent,
                  rigScale=rigScale)

    def populateSettingGrp(self):
        """
        Refresh setting group combo box.
        :return: None
        """
        self.setGrpComboBox.clear()
        self.setGrps = lib.findSettingGrp()
        self.setGrpComboBox.addItems(self.setGrps)

    def setEditLine(self, editLine):
        """
        Set specified edit line for parameter
        :param editLine: dict, editLine
        :return: None
        """
        selections = cmds.ls(sl=1, fl=1)

        items = self.listWidget.selectedItems()

        itemStr = []
        for i in items:
            itemStr.append(self.listWidget.item(self.listWidget.row(i)).text())

        finalStr = selections + itemStr

        if finalStr:
            if len(finalStr) < 2:
                editLine.setText(finalStr[0])
            else:
                editLine.setText(str(finalStr))

    def refreshListWidget(self):
        """
        refresh listWidget with specified checked
        :return: None
        """
        self.listWidget.clear()

        joints = []
        nucleus = []

        if self.jointCheck.isChecked():
            joints = cmds.ls(type='joint')

        if self.nucleusCheck.isChecked():
            nucleus = cmds.ls(type='nucleus')

        returnList = joints + nucleus

        if returnList:
            if len(returnList) > 1:
                self.listWidget.addItems(returnList)

            else:
                self.listWidget.addItem(returnList[0])

    def setCurrentSetGrp(self):
        """
        Set current setting group
        :return: None
        """
        self.currentSetGrp = self.setGrpComboBox.currentText()

        # necleus
        self.repNecleusComBox.clear()

        nucleusList = cmds.ls(type='nucleus')
        connectedNucleus = cmds.listConnections(self.currentSetGrp + '.nucleus', source=0, destination=1,
                                                type='nucleus')

        self.repNecleusComBox.addItems(connectedNucleus)

        for i in nucleusList:
            if i not in connectedNucleus:
                self.repNecleusComBox.addItem(i)

        # add item new
        self.repNecleusComBox.addItem('New...')

    def selectSpecifiedItem(self, item):
        """
        Select specified item
        :param item: str, specified item
        :return: None
        """
        if item not in ['nCloth', 'nucleus', 'bakeCtrlGrp', 'bakeCtrl',
                        'ctrlJoint', 'skinJoint', 'simJoint', 'proxyMesh']:
            cmds.warning('Unknown item, please check again!')

        if item in ['nCloth']:
            listConnection = cmds.listConnections(self.currentSetGrp + '.' + item, source=0, destination=1, shapes=1)
        else:
            listConnection = cmds.listConnections(self.currentSetGrp + '.' + item, source=0, destination=1)

        if listConnection:
            if len(listConnection) > 2:
                listConnection.sort()
                cmds.select(cl=1)
                for i in listConnection:
                    cmds.select(i, add=1)

            else:
                cmds.select(listConnection[0])

    def selectCurrentSetGrp(self):
        """
        Select current setting group
        :return: None
        """
        cmds.select(self.currentSetGrp)

    def bakeSimulation2Ctrls(self):
        """
        Bake simulation to the controls
        :return: None
        """
        skinJointsList = cmds.listConnections(self.currentSetGrp + '.skinJoint', source=0, destination=1, type='joint')

        bakeCtrlList = cmds.listConnections(self.currentSetGrp + '.bakeCtrl', source=0, destination=1)

        # anim time attr
        animMinTime = cmds.playbackOptions(min=1, q=1)
        animMaxTime = cmds.playbackOptions(max=1, q=1)

        # set keyframe
        for i in xrange(int(animMaxTime - animMinTime) + 1):
            cmds.currentTime(animMinTime + i)

            for j in xrange(len(bakeCtrlList)):
                cmds.matchTransform(bakeCtrlList[j], skinJointsList[j], pos=1, rot=1)
                for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']:
                    cmds.setKeyframe(bakeCtrlList[j], at=attr, time=cmds.currentTime(q=1))

            print 'current time is: ' + str(animMinTime + i)

        cmds.select(cl=1)

    def replaceNucleus(self):
        """
        Replace existed nucleus with selected nucleus or new nucleus
        :return: None
        """
        currentNucleus = cmds.listConnections(self.currentSetGrp + '.nucleus', source=0, destination=1)[0]

        if currentNucleus == self.repNecleusComBox.currentText():
            return

        elif currentNucleus != self.repNecleusComBox.currentText() and self.repNecleusComBox.currentText() != 'New...':
            # disconnect original nucleus
            currentNCloth = cmds.listConnections(self.currentSetGrp + '.nCloth', source=0, destination=1, shapes=1)[0]

            inputActiveAttr = cmds.listConnections(currentNCloth + '.currentState',
                                                   source=0, destination=1, plugs=1)[0]
            inputActiveStartAttr = cmds.listConnections(currentNCloth + '.startState',
                                                        source=0, destination=1, plugs=1)[0]
            outputObjectAttr = cmds.listConnections(currentNCloth + '.nextState',
                                                    source=1, destination=0, plugs=1)[0]

            cmds.disconnectAttr(currentNCloth + '.currentState', inputActiveAttr)
            cmds.disconnectAttr(currentNCloth + '.startState', inputActiveStartAttr)
            cmds.disconnectAttr(outputObjectAttr, currentNCloth + '.nextState')
            cmds.disconnectAttr(currentNucleus + '.startFrame', currentNCloth + '.startFrame')

            currentNucleusAttr = cmds.listConnections(self.currentSetGrp + '.nucleus',
                                                      source=0, destination=1, plugs=1)[0]
            cmds.disconnectAttr(self.currentSetGrp + '.nucleus', currentNucleusAttr)

            # connect specified nucleus
            index = lib.findTribleAvailableIndex(firstAttr=self.repNecleusComBox.currentText() + '.inputActive',
                                                 secondAttr=self.repNecleusComBox.currentText() + '.inputActiveStart',
                                                 thirdAttr=self.repNecleusComBox.currentText() + '.outputObjects')

            nucleusIndex = lib.findSingleAvailableIndex(self.repNecleusComBox.currentText() + '.nucleus')

            cmds.connectAttr(self.repNecleusComBox.currentText() + '.outputObjects[%s]' % (str(index)),
                             currentNCloth + '.nextState', f=1)
            cmds.connectAttr(self.repNecleusComBox.currentText() + '.startFrame',
                             currentNCloth + '.startFrame', f=1)

            cmds.connectAttr(currentNCloth + '.currentState',
                             self.repNecleusComBox.currentText() + '.inputActive[%s]' % (str(index)), f=1)
            cmds.connectAttr(currentNCloth + '.startState',
                             self.repNecleusComBox.currentText() + '.inputActiveStart[%s]' % (str(index)),
                             f=1)

            cmds.connectAttr(self.currentSetGrp + '.nucleus',
                             self.repNecleusComBox.currentText() + '.nucleus[%s]' % (str(nucleusIndex)), f=1)

        else:
            # disconnect original nucleus
            currentNCloth = cmds.listConnections(self.currentSetGrp + '.nCloth', source=0, destination=1, shapes=1)[0]

            inputActiveAttr = cmds.listConnections(currentNCloth + '.currentState',
                                                   source=0, destination=1, plugs=1)[0]
            inputActiveStartAttr = cmds.listConnections(currentNCloth + '.startState',
                                                        source=0, destination=1, plugs=1)[0]
            outputObjectAttr = cmds.listConnections(currentNCloth + '.nextState',
                                                    source=1, destination=0, plugs=1)[0]

            cmds.disconnectAttr(currentNCloth + '.currentState', inputActiveAttr)
            cmds.disconnectAttr(currentNCloth + '.startState', inputActiveStartAttr)
            cmds.disconnectAttr(outputObjectAttr, currentNCloth + '.nextState')
            cmds.disconnectAttr(currentNucleus + '.startFrame', currentNCloth + '.startFrame')

            currentNucleusAttr = cmds.listConnections(self.currentSetGrp + '.nucleus',
                                                      source=0, destination=1, plugs=1)[0]
            cmds.disconnectAttr(self.currentSetGrp + '.nucleus', currentNucleusAttr)

            # create and connect
            createdNucleus = lib.createNucleus(name=name.removeSuffix(self.currentSetGrp))

            inputActiveIndex = cmds.getAttr(createdNucleus + '.inputActive', size=1)
            inputActiveStartIndex = cmds.getAttr(createdNucleus + '.inputActiveStart', size=1)
            outputObjectIndex = cmds.getAttr(createdNucleus + '.outputObjects', size=1)

            nucleusIndex = cmds.getAttr(createdNucleus + '.nucleus', size=1)

            cmds.connectAttr(createdNucleus + '.outputObjects[%s]' % (str(outputObjectIndex)),
                             currentNCloth + '.nextState', f=1)
            cmds.connectAttr(createdNucleus + '.startFrame',
                             currentNCloth + '.startFrame', f=1)

            cmds.connectAttr(currentNCloth + '.currentState',
                             createdNucleus + '.inputActive[%s]' % (str(inputActiveIndex)), f=1)
            cmds.connectAttr(currentNCloth + '.startState',
                             createdNucleus + '.inputActiveStart[%s]' % (str(inputActiveStartIndex)), f=1)

            cmds.connectAttr(self.currentSetGrp + '.nucleus',
                             createdNucleus + '.nucleus[%s]' % (str(nucleusIndex)), f=1)
            # clean hierarchy
            targetParent = cmds.listRelatives(self.currentSetGrp, c=0, p=1, path=1)[0]
            cmds.parent(createdNucleus, targetParent)

            cmds.select(cl=1)

        self.setCurrentSetGrp()
