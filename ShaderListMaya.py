import ShaderList
import ShaderListViewMaya
import threading
import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.utils as utils
from maya import OpenMayaUI as omui
from shiboken import wrapInstance 
from PySide.QtGui import *
from PySide.QtCore import *

class ShaderListFileMaya(ShaderList.ShaderListFile):
    def __init__(self, *args, **kwargs):
        super(ShaderListFileMaya, self).__init__(*args, **kwargs)

    def readFromMaya(self):
        sels = cmds.ls(sl = True)
        cmds.select(clear = True)
        for sel in sels:
            cmds.select(sel,add = True,hi = True)

        sList = om.MGlobal.getActiveSelectionList()
        iter = om.MItSelectionList(sList, om.MFn.kMesh)

        sels = []

        while not iter.isDone():
            path = '|'.join(iter.getDagPath().fullPathName().split('|')[:-1])
            sels.append(path)
            iter.next()

        sList = om.MSelectionList()

        for item in list(set(sels)):
            sList.add(item)
            

        self.shaderList = {}

        for i in range(sList.length()):
            obj = sList.getDagPath(i).fullPathName().replace('|','/')
            dagpath = sList.getDagPath(i).extendToShape()
            #print sList.getDependNode(i)
            fnMesh = om.MFnMesh(dagpath)
            indices = om.MIntArray()
            shaders = om.MObjectArray()
            instanceNumber = 0
            shaders, indices = fnMesh.getConnectedShaders(instanceNumber)
            shader_collection = []

            for shader in shaders:
                shader_name = om.MFnDependencyNode(shader).name()
                shader_collection.append(shader_name)

            if len(shader_collection) == 1:
                self.shaderList[obj] = [shader_collection,[-1]]
            else:
                self.shaderList[obj] = [shader_collection,list(indices)]

    def assign(self, autoCreate = False):
        objs = self.shaderList.keys()
        ths = []
        for obj in objs:
            if cmds.objExists(obj.replace('/','|')):
                if len(self.shaderList[obj][0]) == 1:
                    sg = self.shaderList[obj][0][0]
                    if autoCreate == True and not cmds.objExists(sg):
                        self.__createNewShadingGroup(sg)
                    if cmds.objExists(sg):
                        th = threading.Thread(target = cmds.sets, args = (obj.replace('/','|'), ), kwargs = {'fe' : sg})
                        th.start()
                        ths.append(th)

                else:
                    if autoCreate == True:
                        for shader in self.shaderList[obj][0]:
                            if not cmds.objExists(shader):
                                self.__createNewShadingGroup(shader)
                    for i in range(len(self.shaderList[obj][1])):
                        value = self.shaderList[obj][1][i]
                        mat = self.shaderList[obj][0][value]
                        if cmds.objExists(mat):
                            th = threading.Thread(target = self.__threadAssign, args = (obj.replace('/','|')+'.f['+str(i)+']', mat))
                            th.start()
                            ths.append(th)
        for th in ths:
            th.join()

    def __threadAssign(self, target, shader):
        utils.executeDeferred(cmds.sets, target, fe = shader)

    def __createNewShadingGroup(self, sg):
        shader = cmds.shadingNode("blinn", asShader=True)
        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name = sg)
        cmds.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)

    def checkObjs(self):
        objs = self.shaderList.keys()
        result = []
        for obj in objs:
            if not cmds.objExists(obj.replace('/','|')):
                result.append(obj)
        return result

    def checkShaders(self):
        objs = self.shaderList.keys()
        result = []
        for obj in objs:
            for i in range(len(self.shaderList[obj][0])):
                shader = self.shaderList[obj][0][i]
                if not cmds.objExists(shader):
                    result.append(shader)
        result = list(set(result))
        return result

    def checkObjsNamespace(self):
        objs = self.shaderList.keys()
        result = []
        for obj in objs:
            for name in obj.split('/'):
                ns = name.split(':')[:-1]
                if len(ns) != 0:
                    whole_ns = ":".join(ns)
                    if cmds.namespace(exists = whole_ns) == False:
                        result.append(whole_ns)
        result = list(set(result))
        return result

    def checkShadersNamespace(self):
        objs = self.shaderList.keys()
        result = []
        for obj in objs:
            for i in range(len(self.shaderList[obj][0])):
                shader_name = self.shaderList[obj][0][i]
                ns = shader_name.split(':')[:-1]
                if len(ns) != 0:
                    whole_ns = ":".join(ns)
                    if cmds.namespace(exists = whole_ns) == False:
                        result.append(whole_ns)
        return list(set(result))

    def view(self):
        mayaMainWindowPtr = omui.MQtUtil.mainWindow()
        mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
        tp = ShaderListViewMaya.ShaderListViewMaya(self, parent = mayaMainWindow)
        tp.show()

####



