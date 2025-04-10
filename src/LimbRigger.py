from PySide2.QtWidgets import QLabel, QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide2.QtCore import Qt
import maya.OpenMayaUI as omui
import shiboken2

def GetMayaMainWindow()->QMainWindow:
    mainWindow = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(mainWindow), QMainWindow)

def DeleteWidgettWithName(name):
    for widget in GetMayaMainWindow().findChildren(QWidget, name):
        widget.deleteLater()

class MayaWindow(QWidget):
    def __init__(self):
        super().__init__(parent = GetMayaMainWindow())
        DeleteWidgettWithName(self.GetWidgetUniqueName())
        self.setWindowFlags(Qt.WindowType.Window)
        self.setObjectName(self.GetWidgetUniqueName())

    def GetWidgetUniqueName(self):
        return "shdkovcnaofojqefqiugfc"

import maya.cmds as mc
class LimbRigger:
    def __init__(self):
        self.root = ""
        self.mid = ""
        self.end = ""
        self.controllerSize = 5
    
    def FindJointsBasedOnSelection(self):
        self.root = mc.ls(sl=True, type ="joint")[0]
        self.mid = mc.listRelatives(self.root, c=True, type="joint")[0]
        self.end = mc.listRelatives(self.mid, c=True, type="joint")[0]
    except Exception

    def CreateFkControllerForJoint(self, jntName):
        ctrlName = "ac_l_fk_" + jntName
        ctrlGrpName = ctrlName +"_grp"
        mc.circle(name = ctrlName, radius = self.controllerSize, normal = (1,0,0))
        mc.group(ctrlName, n=ctrlGrpName)
        mc.matchTransform(ctrlGrpName, jntName)
        mc.orientConstraint(ctrlName, jntName)
        return ctrlName, ctrlGrpName

def RigLimb(self):
    rootCtrl, rootCtrlGrp = self.CreateFkControllerForJoint(self.root)
    midCtrl, midCtrlGrp = self.CreateFkControllerForJoint(self.mid)
    endCtrl, endCtrlGrp = self.CreateFkControllerForJoint(self.end)

    mc.parent(midCtrlGrp, rootCtrl)
    mc.parent(endCtrlGrp, midCtrl)

class LimbRiggerWidget(MayaWindow):
    def __init__(self):
        super().__init__()
        self.rigger = LimbRigger()

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

        rigLimbBtn = QPushButton("Rig Limb")
        rigLimbBtn.clicked.connect(lambda : self.rigger.RigLimb())
        self.masterLayout.addWidget(rigLimbBtn)


    def AutoFindJntBtnClicked(self):
        self.rigger.FindJointsBasedOnSelection()
        self.jntsListLineEdit.setText(f"{self.rigger.root},{self.rigger.mid},{self.rigger.end}")
    

LimbRiggerWidget = LimbRiggerWidget()
LimbRiggerWidget.show()

GetMayaMainWindow()