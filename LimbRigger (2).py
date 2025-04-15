from PySide2.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QSlider, QVBoxLayout, QWidget# this imports all ui widget we are going to use
from PySide2.QtCore import Qt# this imports 
from maya.OpenMaya import MVector
import maya.mel as mel
import maya.OpenMayaUI as omui# this imports mayas open maya ui module, it can help finding the maya main window
import shiboken2# this helps with converting the maya main window to the pyside type

def GetMayaMainWindow()->QMainWindow:# finds maya main window and converts through shiboken
    mainWindow = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(mainWindow), QMainWindow)

def DeleteWidgettWithName(name):# 
    for widget in GetMayaMainWindow().findChildren(QWidget, name):#
        widget.deleteLater()

class MayaWindow(QWidget):# setup for finding and deleting duplicate widgets
    def __init__(self):# constructor attaches widget to maya window, deletes copies, and gives unique name
        super().__init__(parent = GetMayaMainWindow())
        DeleteWidgettWithName(self.GetWidgetUniqueName())
        self.setWindowFlags(Qt.WindowType.Window)
        self.setObjectName(self.GetWidgetUniqueName())

    def GetWidgetUniqueName(self):# gives an id to the widget
        return "shdkovcnaofojqefqiugfc"

import maya.cmds as mc
class LimbRigger:# holds all code for the auto rigging process
    def __init__(self):# constructor initiates name places for each part of the limb
        self.root = ""
        self.mid = ""
        self.end = ""
        self.controllerSize = 5
    
    def FindJointsBasedOnSelection(self):# finds the joints based on how you selected them in the viewport
        try:# tries to find the three joints selected
            self.root = mc.ls(sl=True, type ="joint")[0]
            self.mid = mc.listRelatives(self.root, c=True, type="joint")[0]
            self.end = mc.listRelatives(self.mid, c=True, type="joint")[0]
        except Exception as e:# if selected in wrong order it gives an error
            raise Exception("Wrong Selection, please select the first joint of the limb!")

    def CreateFkControllerForJoint(self, jntName):# creates an FK controller for the joints
        ctrlName = "ac_l_fk_" + jntName
        ctrlGrpName = ctrlName +"_grp"
        mc.circle(name = ctrlName, radius = self.controllerSize, normal = (1,0,0))
        mc.group(ctrlName, n=ctrlGrpName)
        mc.matchTransform(ctrlGrpName, jntName)
        mc.orientConstraint(ctrlName, jntName)
        return ctrlName, ctrlGrpName
    
    def CreateBoxController(self, name):
        mel.eval(f"curve -n {name} -d 1 -p 0.5 0.5 0.5 -p -0.5 0.5 0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p -0.5 -0.5 0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p -0.5 0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 ;")
        mc.scale(self.controllerSize, self.controllerSize, self.controllerSize, name)
        mc.makeIdentity(name, apply=True) # freeze transformation
        grpName = name +"_grp"
        mc.group(name, n = grpName)
        return name, grpName 
        
    def CreatePlusController(self, name):
        mel.eval(f"curve -n {name} -d 1 -p -17 0 0 -p -17 -1 0 -p -16 -1 0 -p -16 -2 0 -p -15 -2 0 -p -15 -1 0 -p -14 -1 0 -p -14 0 0 -p -15 0 0 -p -15 1 0 -p -16 1 0 -p -16 0 0 -p -17 0 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 ; ")
        grpName = name + "_grp"
        mc.group(name, n = grpName)
        return name, grpName
    
    def GetObjectLocation(self, objectName):
        x, y, z = mc.xform(objectName, q=True, ws=True, t=True)
        return MVector(x, y, z)
    
    def PrintMVector(self, vector):
        print(f"<{vector.x}, {vector.y}, {vector.z}>")

    def RigLimb(self):# places all joints in proper parenting order in outliner
        rootCtrl, rootCtrlGrp = self.CreateFkControllerForJoint(self.root)
        midCtrl, midCtrlGrp = self.CreateFkControllerForJoint(self.mid)
        endCtrl, endCtrlGrp = self.CreateFkControllerForJoint(self.end)

        mc.parent(midCtrlGrp, rootCtrl)
        mc.parent(endCtrlGrp, midCtrl)


        ikEndCtrl =  "ac_ik_" + self.end
        ikEndCtrl, ikEndCtrlGrp = self.CreateBoxController(ikEndCtrl)
        mc.matchTransform(ikEndCtrlGrp, self.end)
        endOrientConstraint = mc.orientConstraint(ikEndCtrl, self.end)[0]

        rootJntLoc = self.GetObjectLocation(self.root)
        self.PrintMVector(rootJntLoc)

        ikHandleName = "ikHandle_" + self.end
        mc.ikHandle(n=ikHandleName, sol="ikRPsolver", sj=self.root, ee=self.end)

        poleVectorLocationVals = mc.getAttr(ikHandleName + ".poleVector")[0]
        poleVector = MVector(poleVectorLocationVals[0], poleVectorLocationVals[1], poleVectorLocationVals[2])
        poleVector.normalize()

        endJntLoc = self.GetObjectLocation(self.end)
        rootToEndVector = endJntLoc - rootJntLoc

        poleVectorCtrlLoc = rootJntLoc + rootToEndVector / 2 + poleVector * rootToEndVector.length()
        poleVectorCtrl = "ac_ik_" + self.mid
        mc.spaceLocator(n=poleVectorCtrl)
        poleVectorCtrlGrp = poleVectorCtrl + "_grp"
        mc.group(poleVectorCtrl, n=poleVectorCtrlGrp)
        mc.setAttr(poleVectorCtrlGrp+".t", poleVectorCtrlLoc.x, poleVectorCtrlLoc.y, poleVectorCtrlLoc.z, typ="double3")

        mc.poleVectorConstraint(poleVectorCtrl, ikHandleName)

        ikfkBlendCtrl = "ac_ikfk_blend" + self.root
        ikfkBlendCtrl, ikfkBlendCtrlGrp = self.CreatePlusController(ikfkBlendCtrl)
        mc.setAttr(ikfkBlendCtrlGrp +".t", rootJntLoc.x*2, 0, rootJntLoc.y, rootJntLoc.z*2, typ="double3" )
        
        ikfkBlendAttrName = "ikfkBlend"
        mc.addAttr(ikfkBlendCtrl, ln=ikfkBlendAttrName, min = 0, max = 1, k=True)
        ikfkBlendAttr = ikfkBlendCtrl + "." + ikfkBlendAttrName
        
        mc.expression(s=f"{ikHandleName}.ikBlend={ikfkBlendAttr}")
        mc.expression(s=f"{ikEndCtrlGrp}.v={poleVectorCtrlGrp}.v={ikfkBlendAttr}")
        mc.expression(s=f"{rootCtrlGrp}.v=1-{ikfkBlendAttr}")
        mc.expression(s=f"{endOrientConstraint}.{endCtrl}W0 = 1-{ikfkBlendAttr}")
        mc.expression(s=f"{endOrientConstraint}.{ikEndCtrl}W1 = {ikfkBlendAttr}")

        topGrpName = F"{self.root}_rig_grp"
        mc.group([rootCtrlGrp, ikEndCtrlGrp, poleVectorCtrlGrp, ikfkBlendCtrlGrp], n=topGrpName)
        mc.parent(ikHandleName, ikEndCtrl)



class LimbRiggerWidget(MayaWindow):# this class holds all code to create the window you interact with to auto rig the limb
    def __init__(self):# creates buttons and text for limb rigger window
        super().__init__()
        self.rigger = LimbRigger()
        self.setWindowTitle("Limb Rigger")

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        toolTipLabel = QLabel("Select the first joint of the limb, and press the auto find button")
        self.masterLayout.addWidget(toolTipLabel)

        self.jntsListLineEdit = QLineEdit()
        self.masterLayout.addWidget(self.jntsListLineEdit)
        self.jntsListLineEdit.setEnabled(False)

        autoFindJntBtn = QPushButton("Auto Find")
        autoFindJntBtn.clicked.connect(self.AutoFindJntBtnClicked)
        self.masterLayout.addWidget(autoFindJntBtn)


        ctrlSizeSlider = QSlider()
        ctrlSizeSlider.setOrientation(Qt.Horizontal)
        ctrlSizeSlider.setRange(1, 30)
        ctrlSizeSlider.setValue(self.rigger.controllerSize)
        self.ctrlSizeLabel = QLabel(f"{self.rigger.controllerSize}")
        ctrlSizeSlider.valueChanged.connect(self.CtrlSizeSliderChanged)

        ctrlSizeLayout = QHBoxLayout()
        ctrlSizeLayout.addWidget(ctrlSizeSlider)
        ctrlSizeLayout.addWidget(self.ctrlSizeLabel)
        self.masterLayout.addLayout(ctrlSizeLayout)

        colorPicker = ColorPicker()
        colorPicker.colorChanged.connect(self.ColorPickerChanged)
        self.masterLayout.addWidget(colorPicker)
        
        rigLimbBtn = QPushButton("Rig Limb")
        rigLimbBtn.clicked.connect(lambda : self.rigger.RigLimb())
        self.masterLayout.addWidget(rigLimbBtn)

    def ColorPickerChanged(self, newColor: QColor):
        self.riggercontrollerColor[0] = newColor.redF()
        self.riggercontrollerColor[1] = newColor.greenF()
        self.riggercontrollerColor[2] = newColor.blueF()

    def CtrlSizeSliderChanged(self, newValue):
        self.ctrlSizeLabel.setText(f"{newValue}")
        self.rigger.controllerSize = newValue

    def AutoFindJntBtnClicked(self):# processes once joints are selected and button is clicked
        try:# calls LimbRigger class and runs find joints based on selection
            self.rigger.FindJointsBasedOnSelection()
            self.jntsListLineEdit.setText(f"{self.rigger.root},{self.rigger.mid},{self.rigger.end}")
        except Exception as e:# if unable gives an error
            QMessageBox.critical(self, "Error", f"{e}")


LimbRiggerWidget = LimbRiggerWidget()# creates an instance of the class and assigns it to a variable
LimbRiggerWidget.show()# shows widget in maya

GetMayaMainWindow()# gets reference for maya main window