from PySide.QtCore import *
from PySide.QtGui import *
import sys

class ShaderListView(QMainWindow):

    def __init__(self, slist, parent = None):
        super(ShaderListView, self).__init__(parent)
        self.slist = slist
        self.rootTypeObj = True
        self.init_UI(self.slist)

    def init_UI(self, slist):

        self.resize(640,540)
        
        self.widget = QWidget()

        self.setWindowTitle('ShaderList Viewer')
        self.main_vlayout = QVBoxLayout()
        filter_hlayout = QHBoxLayout()
        self.file_picker_layout = QHBoxLayout()

        openFile = QAction('Open File...', self)
        saveFile = QAction('Save', self)
        saveAsFile = QAction('Save as File...', self)

        refreshAct = QAction('Refresh', self)
        backwardAct = QAction('Backward Hierarchy', self)
        removeObjsAct = QAction('Remove Selected Objs', self)
        changeRoot = QAction('Change Objs Root', self)
        removeAllObjsNS = QAction('Remove All Objs Namespace...', self)
        removeAllShsNS = QAction('Remove All Shaders Namespace...', self)
        addNStoAllShaders = QAction('Add Namespace to All Shaders...', self)
        addNStoAllObjs = QAction('Add Namespace to All Objs...', self)
        replaceObjsNS = QAction('Replace All Objs Namespace...', self)
        replaceShadersNS = QAction('Replace All Shaders Namespace...', self)

        switchRootType = QAction('Switch Root Type (Objs/Shaders)', self)

        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')
        editMenu = self.menubar.addMenu('&Edit')
        viewMenu = self.menubar.addMenu('&View')

        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
        fileMenu.addAction(saveAsFile)

        editMenu.addAction(refreshAct)
        editMenu.addSeparator()
        editMenu.addAction(backwardAct)
        editMenu.addAction(changeRoot)
        editMenu.addSeparator()
        editMenu.addAction(removeObjsAct)
        editMenu.addSeparator()
        editMenu.addAction(removeAllObjsNS)
        editMenu.addAction(removeAllShsNS)
        editMenu.addSeparator()
        editMenu.addAction(addNStoAllShaders)
        editMenu.addAction(addNStoAllObjs)
        editMenu.addSeparator()
        editMenu.addAction(replaceObjsNS)
        editMenu.addAction(replaceShadersNS)

        viewMenu.addAction(switchRootType)

        self.filter_lineEdit = QLineEdit('')

        self.tree = ShaderListTreeView()
        smodel = self.tree.selectionModel()
        self.treeModel = TreeModel(slist)
        self.proxyModel = ProxyModel()
        self.proxyModel.setSourceModel(self.treeModel)
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setFilterKeyColumn(0)
        self.tree.setModel(self.proxyModel)
        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree.setColumnWidth(0, 300)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(True)

        self.help_lineEdit = QLineEdit('...')

        filter_hlayout.addWidget(QLabel('Filter:'))
        filter_hlayout.addWidget(self.filter_lineEdit)

        self.main_vlayout.addLayout(filter_hlayout)
        self.main_vlayout.addWidget(self.tree)
        self.main_vlayout.addWidget(self.help_lineEdit)
        self.widget.setLayout(self.main_vlayout)
        self.setCentralWidget(self.widget)

        openFile.triggered.connect(self.file_pick)
        saveFile.triggered.connect(self.file_save)
        saveAsFile.triggered.connect(self.file_save_as)
        refreshAct.triggered.connect(self.renew_tree)
        backwardAct.triggered.connect(self.backward_h)
        changeRoot.triggered.connect(self.changeRoot)
        removeObjsAct.triggered.connect(self.removeSelectedObjs)
        removeAllObjsNS.triggered.connect(self.rm_objs_ns)
        removeAllShsNS.triggered.connect(self.rm_shs_ns)
        addNStoAllShaders.triggered.connect(self.add_ns_to_all_shaders)
        addNStoAllObjs.triggered.connect(self.add_ns_to_all_objs)
        replaceObjsNS.triggered.connect(self.replace_objs_ns)
        replaceShadersNS.triggered.connect(self.replace_shs_ns)

        switchRootType.triggered.connect(self.switchRootType)

        self.tree.clicked.connect(self.refresh_help_lineEdit)
        self.filter_lineEdit.textChanged.connect(self.filter_list)
        
    def file_pick(self):
        path = QFileDialog.getOpenFileName(self, 'Open File', 'C:/', 'Shaderlist (*.shaderlist)')
        self.setWindowTitle('ShaderList Viewer - ' + path[0])
        if path[0] != '':
            self.slist.setFile(path[0])
            self.slist.read()
            self.renew_tree()

    def renew_tree(self):
        self.proxyModel = ProxyModel()
        self.treeModel = TreeModel(self.slist, rootTypeObj = self.rootTypeObj)
        self.proxyModel.setSourceModel(self.treeModel)
        self.tree.setModel(self.proxyModel)
        self.tree.expandAll()

    def file_save_as(self):
        path = QFileDialog.getSaveFileName(self, 'Save File', 'C:/', 'Shaderlist (*.shaderlist)')
        self.setWindowTitle('ShaderList Viewer - ' + path[0])
        self.slist.setFile(path[0])
        self.slist.write()
        self.treeModel = TreeModel(self.slist)
        self.tree.setModel(self.treeModel)

    def file_save(self):
        self.slist.write()
        self.treeModel = TreeModel(self.slist)
        self.tree.setModel(self.treeModel)

    def backward_h(self):
        self.slist.backwardObj(1)
        self.renew_tree()

    def changeRoot(self):
        dialog = LineDialog('Change Root...')
        dialog.show()
        new_root = ''
        if dialog.exec_():
            new_root = dialog.lineText
        self.slist.changeRoot(new_root)
        self.renew_tree()

    def removeSelectedObjs(self):
        target_objs = self.get_selected_objs()
        self.slist.removeObjs(target_objs)
        self.renew_tree()

    def rm_objs_ns(self):
        dialog = LineDialog('Remove All Objs Namespace')
        dialog.show()
        nspace = ''
        if dialog.exec_():
            nspace = dialog.lineText
        self.slist.removeObjsNamespace(nspace)
        self.renew_tree()

    def rm_shs_ns(self):
        dialog = LineDialog('Remove All Shaders Namespace')
        dialog.show()
        nspace = ''
        if dialog.exec_():
            nspace = dialog.lineText
        self.slist.removeShadersNamespace(nspace)
        self.renew_tree()

    def add_ns_to_all_shaders(self):
        dialog = LineDialog('Add Namespace to All Shaders')
        dialog.show()
        nspace = dialog.lineText if dialog.exec_() else ''
        self.slist.addNamespaceToShaders(nspace)
        self.renew_tree()

    def add_ns_to_all_objs(self):
        dialog = LineDialog('Add Namespace to All Objs')
        dialog.show()
        nspace = dialog.lineText if dialog.exec_() else ''
        if nspace != '':
            self.slist.addNamespaceToObjs(nspace)
            self.renew_tree()

    def get_selected_objs(self):
        sels = self.tree.selectionModel()
        proxyIndices = sels.selectedIndexes()
        indices = []
        for proxyIndex in proxyIndices:
            indices.append(self.proxyModel.mapToSource(proxyIndex))
        result = list(set([x.internalPointer().getDag() for x in indices]))
        return result

    def refresh_help_lineEdit(self):
        select_objs = self.get_selected_objs()
        try:
            self.help_lineEdit.setText(','.join(self.get_selected_objs()))
        except TypeError:
            pass

    def switchRootType(self):
        if self.rootTypeObj == True:
            self.rootTypeObj = False
        else:
            self.rootTypeObj = True
        self.renew_tree()

    def filter_list(self):
        if self.filter_lineEdit.text() != '':
            self.proxyModel = ProxyModel()
            self.treeModel = TreeModel(self.slist, rootTypeObj = self.rootTypeObj, filter_string = self.filter_lineEdit.text())
            self.proxyModel.setSourceModel(self.treeModel)
            self.tree.setModel(self.proxyModel)
            self.tree.expandAll()
        else:
            pass


    def replace_objs_ns(self):
        dialog = ReplaceDialog('Replace All Objs Namespace')
        dialog.show()
        if dialog.exec_():
            from_ns = dialog.from_text
            to_ns = dialog.to_text
            self.slist.replaceObjsNamespace(from_ns, to_ns)
        self.renew_tree()

    def replace_shs_ns(self):
        dialog = ReplaceDialog('Replace All Shaders Namespace')
        dialog.show()
        if dialog.exec_():
            from_ns = dialog.from_text
            to_ns = dialog.to_text
            self.slist.replaceShadersNamespace(from_ns, to_ns)
        self.renew_tree()

####

class LineDialog(QDialog):
    def __init__(self, title, parent = None):
        super(LineDialog, self).__init__(parent)
        self.lineText = ''
        self.init_UI(title)

    def init_UI(self, title):
        self.setWindowTitle(title)
        main_vlayout = QVBoxLayout()
        b_hlayout = QHBoxLayout()
        self.lineEdit = QLineEdit('')
        self.ok_b = QPushButton('OK')
        self.cancel_b = QPushButton('Cancel')
        b_hlayout.addWidget(self.ok_b)
        b_hlayout.addWidget(self.cancel_b)

        main_vlayout.addWidget(self.lineEdit)
        main_vlayout.addLayout(b_hlayout)
        self.setLayout(main_vlayout)

        self.ok_b.clicked.connect(lambda: self.submit(1))
        self.cancel_b.clicked.connect(lambda: self.submit(0))

    def submit(self, switch):
        if switch == 1:
            self.lineText = self.lineEdit.text()
            self.accept()
        else:
            self.close()

class ReplaceDialog(LineDialog):
    def __init__(self, *args, **kwargs):
        super(ReplaceDialog, self).__init__(*args, **kwargs)
        self.from_text = ''
        self.to_text = ''

    def init_UI(self, title):
        self.setWindowTitle(title)
        main_vlayout = QVBoxLayout()

        from_hlayout = QHBoxLayout()
        to_hlayout = QHBoxLayout()
        b_hlayout = QHBoxLayout()

        self.from_lineEdit = QLineEdit('')
        self.to_lineEdit = QLineEdit('')

        from_hlayout.addWidget(QLabel('From:'))
        from_hlayout.addWidget(self.from_lineEdit)
        to_hlayout.addWidget(QLabel('To:'))
        to_hlayout.addWidget(self.to_lineEdit)

        self.ok_b = QPushButton('OK')
        self.cancel_b = QPushButton('Cancel')

        b_hlayout.addWidget(self.ok_b)
        b_hlayout.addWidget(self.cancel_b)

        main_vlayout.addLayout(from_hlayout)
        main_vlayout.addLayout(to_hlayout)
        main_vlayout.addLayout(b_hlayout)
        self.setLayout(main_vlayout)

        self.ok_b.clicked.connect(lambda: self.submit(1))
        self.cancel_b.clicked.connect(lambda: self.submit(0))

    def submit(self, switch):
        if switch == 1:
            self.to_text = self.to_lineEdit.text()
            self.from_text = self.from_lineEdit.text()
            self.accept()
        else:
            self.close()


####

class TreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []
        self.dag = None
        self.color = None
        self.bgColor = None
        if parent is not None:
            parent.appendChild(self)

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

    def children(self):
        return self.childItems

    def setDag(self, dag):
        self.dag = dag

    def getDag(self):
        return self.dag

    def setBGColor(self, value):
        self.bgColor = value
        self.color = QColor(Qt.black)

    def getBGColor(self):
        return self.bgColor

    def getFGColor(self):
        return self.color

    def setItemData(self, value):
        self.itemData = value


####

class TreeModel(QAbstractItemModel):
    def __init__(self, slist, rootTypeObj = True, filter_string = '', parent=None):
        super(TreeModel, self).__init__(parent)
        if rootTypeObj == True:
            self.rootItem = TreeItem(("DagPath", "Shader"))
        else:
            self.rootItem = TreeItem(('Shader/DagPath', 'Shader'))
        self.rootTypeObj = rootTypeObj
        self.setupModelData(slist, self.rootItem, filter_string)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item.data(index.column())
        elif role == Qt.BackgroundRole:
            return item.getBGColor()
        elif role == Qt.ForegroundRole:
            return item.getFGColor()
        else:
            return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)
        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        childItem = index.internalPointer()
        parentItem = childItem.parent()
        if parentItem == self.rootItem:
            return QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        return parentItem.childCount()

    def setupModelData(self, slist, root, filter_string = ''):
        shaderlsit = ''
        if filter_string == '':
            shaderlist = slist.shaderList
        else:
            shaderlist = filter_list(slist.shaderList, filter_string)

        if shaderlist != {}:
            objs = shaderlist.keys()
            missingObjs = []
            missingShaders = []

            if hasattr(slist, 'checkObjs'):
                missingObjs = slist.checkObjs()
                missingShaders = slist.checkShaders()

            newobjs = []

            for obj in objs:
                if self.rootTypeObj == True:
                    newobjs.append([obj, obj])
                else:
                    for shader in shaderlist[obj][0]:
                        newobjs.append(['/' + shader + obj, obj])

            for obj in newobjs:
                string_list = obj[0].split('/')
                parent = root
                for i,j in enumerate(string_list):
                    if i > 0:
                        temp = [None]
                        temp +=  [x if x.data(0) == j else None for x in parent.children()]
                        checkpoint = reduce(filter_none, temp)
                        if checkpoint == None:
                            if i == len(string_list) - 1:
                                checkpoint = TreeItem([j,','.join(shaderlist[obj[1]][0])], parent)
                                checkpoint.setDag(obj[1])
                                if shaderlist[obj[1]][1][0] != -1:
                                    checkpoint.setBGColor(QColor(Qt.yellow))
                                try:
                                    for shader in shaderlist[obj[1]][0]:
                                        try:
                                            if missingShaders.index(shader) != None:
                                                checkpoint.setBGColor(QColor(Qt.magenta))
                                        except ValueError:
                                            pass
                                    if missingObjs.index(obj[1]) != None:
                                        checkpoint.setBGColor(QColor(Qt.red))
                                except ValueError:
                                    pass
                            else:
                                checkpoint = TreeItem([j,''], parent)
                            parent = checkpoint
                        else:
                            if i == len(string_list) - 1:
                                checkpoint.setItemData([j,','.join(shaderlist[obj[1]][0])])
                                checkpoint.setDag(obj[1])
                                if shaderlist[obj[1]][1][0] != -1:
                                    checkpoint.setBGColor(QColor(Qt.yellow))
                                try:
                                    if missingObjs.index(obj[1]) != None:
                                        checkpoint.setBGColor(QColor(Qt.red))
                                except ValueError:
                                    pass
                            parent = checkpoint

class ShaderListTreeView(QTreeView):
    def __init__(self, parent = None):
        super(ShaderListTreeView, self).__init__(parent)

class ProxyModel(QSortFilterProxyModel):
    def __init__(self, parent = None):
        super(ProxyModel, self).__init__(parent)




def filter_none(x,y):
    if x != None:
        return x
    else:
        return y

def filter_list(slist, filter_string):
    contents = filter_string.split(' ')
    contents = list(set(contents))
    objs = slist.keys()
    newobjs = []
    for content in contents:
        for obj in objs:
            if content in obj:
                newobjs.append(obj)
    newobjs = list(set(newobjs))
    new_dict = {}
    for newobj in newobjs:
        new_dict[newobj] = slist[newobj]

    return new_dict
