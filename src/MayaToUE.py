from MayaUtils import *
from PySide2.QtWidgets import QLineEdit, QMessageBox, QPushButton, QVBoxLayout
import maya.cmds as mc

class AnimClip:
        def __init__(self):
                self.subfix = ""
                self.frameMin = mc.playbackOptions(q=True, min=True)
                self.frameMax = mc.playbackOptions(q=True, min=True)
                self.shouldExport = True


class MayaToUE:
        def __init__(self):
                self.rootJnt = ""
                self.models  = set()
                self.animations : list[AnimClip] = []
                self.fileName = ""
                self.saveDir = ""
                    
        def SetSelectedJointAsRoot(self):
                selection = mc.ls(sl=True, type="joint")
                if not selection:
                        raise Exception("Wrong Selection please select the root joint of your rig!")
                
                self. rootJnt = selection[0]

class MayaToUEWidget(MayaWindow):
        def GetWidgetUniqueName(self):
                return "MayaToUEWidgetKJ4235KLJH5300"
                
        def __init__(self):
                super().__init__()
                self.mayaToUE = MayaToUE()
                
                self.setWindowTitle("Maya to UE")
                self.masterLayout = QVBoxLayout()
                self.setLayout(self.masterLayout)

                self.rootJntText = QLineEdit()
                self.rootJntText.setEnabled(False)
                self.masterLayout.addWidget(self.rootJntText)

                setSelectedAsRootJntBtn = QPushButton("Set Root Joint")
                setSelectedAsRootJntBtn.clicked.connect(self.SetSelectedAsRootJntBtnClicked)
                self.masterLayout.addWidget(setSelectedAsRootJntBtn)

        def SetSelectedAsRootJntBtnClicked(self):
                try:
                        self.mayaToUE.SetSelectedJointAsRoot()
                        self.rootJntText.setText(self.mayaToUE.rootJnt)
                except Exception as e:
                        QMessageBox().critical(self, "Error!", f"{e}")

MayaToUEWidget().show()