import ShaderListView
from PySide.QtCore import *
from PySide.QtGui import *
import maya.cmds as cmds

class ShaderListViewMaya(ShaderListView.ShaderListView):
    def __init__(self, *args, **kwargs):
        super(ShaderListViewMaya, self).__init__(*args, **kwargs)

    def init_UI(self, *args):
        self.resize(960, 540)

        super(ShaderListViewMaya, self).init_UI(*args)

        bottom_h_layout = QHBoxLayout()

        readMayaAct = QAction('Read From Maya Selection', self)
        assignAct = QAction('Assign', self)

        mayaMenu = self.menubar.addMenu('&Maya')

        mayaMenu.addAction(readMayaAct)
        mayaMenu.addAction(assignAct)

        self.menubar.addMenu(mayaMenu)

        select_objs_button = QPushButton('Selected Objs')
        select_shaders_button = QPushButton('Selected Shaders')

        bottom_h_layout.addWidget(select_objs_button)
        bottom_h_layout.addWidget(select_shaders_button)

        self.main_vlayout.addLayout(bottom_h_layout)

        readMayaAct.triggered.connect(self.read_from_maya)
        assignAct.triggered.connect(self.assign)
        select_objs_button.clicked.connect(self.select_objs)
        select_shaders_button.clicked.connect(self.select_shaders)

    def read_from_maya(self):
        self.slist.readFromMaya()
        self.renew_tree()

    def assign(self):
        #self.slist.assign()
        dialog = assignDialog(self.slist)
        dialog.show()
        if dialog.exec_():
            self.slist.assign(autoCreate = dialog.isCheck)
        else:
            pass

    def select_objs(self):
        targets = self.get_selected_objs()
        cmds.select(clear = True)
        for target in targets:
            if target != None:
                cmds.select(target.replace('/','|'), add = True)

    def select_shaders(self):
        targets = self.get_selected_objs()
        shaders = []
        for target in targets:
            shaders += self.slist.shaderList[target][0]
        shaders = list(set(shaders))
        cmds.select(clear = True)
        for shader in shaders:
            sh = cmds.listConnections('%s.surfaceShader' % shader)
            cmds.select(sh[0], add = True)


class assignDialog(QDialog):
    def __init__(self, slist, parent = None):
        super(assignDialog, self).__init__(parent)
        self.isCheck = False
        self.slist = slist
        self.init_UI()


    def init_UI(self):

        self.resize(400,200)
        self.setWindowTitle('Assign')

        main_vlayout = QVBoxLayout()
        button_hlayout = QHBoxLayout()

        self.auto_check = QCheckBox('Auto Create ShadingGroup')

        ok_button = QPushButton('OK')
        cancel_button = QPushButton('Cancel')

        button_hlayout.addWidget(ok_button)
        button_hlayout.addWidget(cancel_button)

        main_vlayout.addWidget(QLabel('Missing Objs Count: ' + str(len(self.slist.checkObjs()))))
        #main_vlayout.addWidget(QLabel('Missing Objs: ' + '\n'.join((self.slist.checkObjs()))))
        main_vlayout.addWidget(QLabel('Missing Shaders Count : ' + str(len(self.slist.checkShaders()))))
        main_vlayout.addWidget(QLabel('Missing Objs Namepsace: ' + ', '.join(self.slist.checkObjsNamespace())))
        main_vlayout.addWidget(QLabel('Missing Shaders Namepsace: ' + ', '.join(self.slist.checkShadersNamespace())))
        main_vlayout.addWidget(self.auto_check)
        main_vlayout.addLayout(button_hlayout)

        self.setLayout(main_vlayout)

        self.resize(400,200)

        ok_button.clicked.connect(lambda: self.submit(1))
        cancel_button.clicked.connect(lambda: self.submit(0))

    def submit(self, switch):
        if switch == 1:
            self.isCheck = self.auto_check.isChecked()
            self.accept()
        else:
            self.close()
