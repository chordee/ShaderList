
import json
import sys
from PySide.QtGui import *
import ShaderListView

class SHL:
    Shaders = 0
    Faces = 1

class ShaderListFile(object):
    def __init__(self, file = '', indent = False):
        self.shaderList = {}
        self.__file = file
        self.__indent = indent

    def getShaders(self):
        objs = self.shaderList.keys()
        shaders = []
        for obj in objs:
            for shader in self.shaderList[obj][0]:
                shaders.append(shader)
        return list(set(shaders))

    def getObjs(self):
        return self.shaderList.keys()

    def getShaderList(self):
        return self.shaderList

    def setFile(self, file):
        self.__file = file

    def write(self):
        if self.__file != '':
            with open(self.__file, 'w') as file:
                json.dump(self.shaderList, file, sort_keys=True, indent = self.__indent)

    def read(self):
        with open(self.__file, 'r') as file:
            self.shaderList = json.load(file)

    def append(self, obj, shader, indices):
        self.shaderList[obj] = [shader, indices]

    def remove(self, obj):
        del self.shaderList[obj]

    def backwardObj(self, step):
        step = int(step)
        if step > 0:
            objs = self.shaderList.keys()
            for obj in objs:
                temp_name = obj.split('/')
                fixed_name = ""
                if len(temp_name) < (step+2):
                    fixed_name = '/' + temp_name[-1]
                else:
                    fixed_name = '/' + "/".join(temp_name[step+1:])

                self.shaderList[fixed_name] = self.shaderList[obj]
                del self.shaderList[obj]

    def changeRoot(self, new_root):
        new_root = new_root.replace('\\','/')
        if new_root[0] != '/':
            new_root = '/'+new_root
        for obj in self.shaderList.keys():
            self.shaderList[new_root + obj] = self.shaderList.pop(obj)

    def removeObjsNamespace(self, nspace = ''):
        objs = self.shaderList.keys()
        for obj in objs:
            fixed_name = self.__removeObjNamespace(obj, ns = nspace)
            if fixed_name != obj:
                self.shaderList[fixed_name] = self.shaderList[obj]
                del self.shaderList[obj]

    def replaceObjsNamespace(self, orig_nspace, new_nspace):
        for obj in self.shaderList.keys():
            new_name = []
            for i,j in enumerate(obj.split('/')):
                if i > 0:
                    new = []
                    for name in j.split(':'):
                        if name == orig_nspace:
                            name = new_nspace
                        new.append(name)
                    new_name.append(":".join(new))
                else:
                    new_name.append(j)

            new_name = '/'.join(new_name)
            self.shaderList[new_name] = self.shaderList.pop(obj)

    def replaceShadersNamespace(self, orig_nspace, new_nspace):
        for obj in self.shaderList.keys():
            for i,shader in enumerate(self.shaderList[obj][0]):
                new_name = []
                for name in shader.split(':'):
                    if name == orig_nspace:
                        name = new_nspace
                    new_name.append(name)
                new_name = ':'.join(new_name)
                self.shaderList[obj][0][i] = new_name


    def removeObjNamespace(self, target_obj, nspace = ''):
        objs = self.shaderList.keys()
        for obj in objs:
            if obj == target_obj:
                fixed_name = self.__removeObjNamespace(obj, ns = nspace)
                if fixed_name != obj:
                    self.shaderList[fixed_name] = self.shaderList[obj]
                    del self.shaderList[obj]

    def removeShadersNamespace(self, nspace = ''):
        objs = self.shaderList.keys()
        for obj in objs:
            shaders = self.shaderList[obj][0]
            for i in range(len(shaders)):
                if nspace == '':
                    self.shaderList[obj][0][i] = self.shaderList[obj][0][i].split(':')[-1]
                else:
                    temp = self.shaderList[obj][0][i].split(':')
                    try:
                        self.shaderList[obj][0][i] = ":".join([x for x in temp if x != nspace])
                    except ValueError:
                        self.shaderList[obj][0][i] = self.shaderList[obj][0][i]

    def removeShaderNamespace(self, shader):
        objs = self.shaderList.keys()
        for obj in objs:
            shaders = self.shaderList[obj][0]
            for i in range(len(shaders)):
                if self.shaderList[obj][0][i] == shader:
                    self.shaderList[obj][0][i] = self.shaderList[obj][0][i].split(':')[-1]

    def __removeObjNamespace(self, name, ns = ''):
        temp_name = name.split('/')
        fixed_name = []
        for name in temp_name:
            if ns == '':
                fixed_name.append(name.split(':')[-1])
            else:
                fixed_name.append(":".join([x for x in name.split(':') if x != ns]))
        fixed_name = '/'.join(fixed_name)

        return fixed_name

    def addNamespaceToShaders(self, ns):
        objs = self.shaderList.keys()
        for obj in objs:
            for i in range(len(self.shaderList[obj][0])):
                self.shaderList[obj][0][i] = ns+':'+self.shaderList[obj][0][i]

    def addNamespaceToObjs(self, nspace):
        for obj in self.shaderList.keys():
            new_dag = []
            for i,j in enumerate(obj.split('/')):
                if i == 0:
                    new_dag.append('')
                else:
                    new_dag.append(nspace + ':' + j)
            self.shaderList['/'.join(new_dag)] = self.shaderList.pop(obj)

    def addNamespaceToShader(self, shader, ns):
        objs = self.shaderList.keys()
        for obj in objs:
            for i in range(len(self.shaderList[obj][0])):
                if self.shaderList[obj][0][i] == shader:
                    self.shaderList[obj][0][i] = ns+':'+self.shaderList[obj][0][i]

    def addNamespaceToShaderFromObj(self, obj, ns):
        for i in range(len(self.shaderList[obj][0])):
            self.shaderList[obj][0][i] = ns +':'+self.shaderList[obj][0][i]

    def renameShader(self, orig_name, new_name):
        objs = self.shaderList.keys()
        for obj in objs:
            for i in range(len(self.shaderList[obj][0])):
                shader = self.shaderList[obj][0][i]
                if shader == orig_name:
                    self.shaderList[obj][0][i] = new_name

    def removeObjs(self, target_objs):
        objs = self.shaderList.keys()
        for obj in objs:
            for target_obj in target_objs:
                if obj == target_obj:
                    del self.shaderList[obj]

    def view(self):
        app = QApplication(sys.argv)
        tp = ShaderListView.ShaderListView(self)
        tp.show()
        sys.exit(app.exec_())
        
####

if __name__ == '__main__':
    #path = 'd:/test2.shaderlist'
    slist = ShaderListFile()
    slist.view()
  