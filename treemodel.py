# This Python file uses the following encoding: utf-8


from PySide2.QtCore import QAbstractItemModel, QFile, QIODevice, QItemSelectionModel, QModelIndex, QObject ,Qt, Signal, Slot
from PySide2.QtWidgets import QApplication, QMainWindow
from treeitem import TreeItem


class TreeModel(QAbstractItemModel):
    checkChanged = Signal(int, str)
    def __init__(self, headers, data, tablemodel, parent=None):
        super(TreeModel, self).__init__(parent)

        rootData = [header for header in headers]
        self.rootItem = TreeItem(rootData)
        self.treeDict = data
        self.tablemodel = tablemodel
        self.setupModelData(data, self.rootItem)
        self.examingParents = False
        self.examiningChildren = False

    def changeLeafCheck(self, source):
        curNode = self.rootItem.child(0)
        keyNames = source.split("/")
        curRow = 0
        for key in keyNames:
            for i in range(curNode.childCount()):
                if curNode.child(i).itemData[0] == key:
                        curNode = curNode.child(i)
                        curRow = i
                        break
        anIndex = self.createIndex(curRow, curNode.columnCount(), curNode)
        self.setData(anIndex, 0, Qt.CheckStateRole)



    def columnCount(self, parent=QModelIndex()):
        return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        item = self.getItem(index)
        if role == Qt.DisplayRole:
            return item.data(index.column())
        elif role == Qt.CheckStateRole:
            return item.checked

        return None


    def flags(self, index):
        if not index.isValid():
            return 0

        return Qt.ItemIsUserCheckable | super(TreeModel, self).flags(index)

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.rootItem

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent=QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parentItem = self.getItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def insertColumns(self, position, columns, parent=QModelIndex()):
        self.beginInsertColumns(parent, position, position + columns - 1)
        success = self.rootItem.insertColumns(position, columns)
        self.endInsertColumns()

        return success

    def insertRows(self, position, rows, parent=QModelIndex()):
        parentItem = self.getItem(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        success = parentItem.insertChildren(position, rows,
                self.rootItem.columnCount())
        self.endInsertRows()

        return success

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = self.getItem(index)
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.childNumber(), 0, parentItem)

    def removeColumns(self, position, columns, parent=QModelIndex()):
        self.beginRemoveColumns(parent, position, position + columns - 1)
        success = self.rootItem.removeColumns(position, columns)
        self.endRemoveColumns()

        if self.rootItem.columnCount() == 0:
            self.removeRows(0, self.rowCount())

        return success

    def removeRows(self, position, rows, parent=QModelIndex()):
        parentItem = self.getItem(parent)

        self.beginRemoveRows(parent, position, position + rows - 1)
        success = parentItem.removeChildren(position, rows)
        self.endRemoveRows()

        return success

    def rowCount(self, parent=QModelIndex()):
        parentItem = self.getItem(parent)

        return parentItem.childCount()

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
           item = self.getItem(index)
           result = item.setData(index.column(), value)
           if result:
               self.dataChanged.emit(index, index)
               return result
        elif role == Qt.CheckStateRole:
            item = self.getItem(index)
            item.checked = value
            checked = item.checked
            source=""
            sourceList= []

            while item.parentItem:
                sourceList.insert(0,item.itemData[0]+"/")
                item = item.parentItem
            if self.examingParents == False:
                self.checkChanged.emit(checked,source.join(sourceList)[:-1])
            self.checkChildren(index,value)
            self.checkParent(index)
            self.dataChanged.emit(index, index)
            return True
        return False


    def setHeaderData(self, section, orientation, value, role=Qt.EditRole):
        if role != Qt.EditRole or orientation != Qt.Horizontal:
            return False

        result = self.rootItem.setData(section, value)
        if result:
            self.headerDataChanged.emit(orientation, section, section)

        return result

    def setupModelData(self, data, parent):
             visited={}
             queue=[]
             grandParents = {}

             for key in data.keys():
                 visited[(parent.itemData[0])]=[key]
                 queue.append((key,parent,""))
                 grandParents[key] = (data[key],parent)
             curDict = data
             tempSource= ""
             while queue:
                 poppedItem = queue.pop(0)
                 child = poppedItem[0]
                 parentOfChild = poppedItem[1]
                 childSource = poppedItem[2]
                 parent = parentOfChild
                 parent.insertChildren(parent.childCount(),1,self.rootItem.columnCount())
                 parent.child(parent.childCount() -1).setData(0,child)

                 if child in grandParents:

                     curDict =  grandParents[child][0]
                     tempSource = childSource+child+"/"
                     for curChild in range(grandParents[child][1].childCount()):
                         if child == grandParents[child][1].child(curChild).itemData[0]:
                            parent = grandParents[child][1].child(curChild)
                            visited[(parent.itemData[0])]=[]

                 if isinstance(curDict, dict):
                     for key in curDict.keys():
                         if key not in visited[(parent.itemData[0])]:
                             visited[(parent.itemData[0])].append(key)
                             queue.append((key,parent,tempSource))
                             if (isinstance(curDict[key],dict)):
                                grandParents[key]= (curDict[key],parent)
                             else:
                                self.tablemodel.addRow(curDict,tempSource,key)

    def checkChildren(self,index,value):
        self.examingChildren = True
        if not index.isValid() or self.examingParents:
            self.examingChildren = False
            return
        else:
            childCount = self.rowCount(index)
            for i in range(childCount):
                child = index.child(i, 0)
                if value == 1:
                    return
                self.setData(child, value, Qt.CheckStateRole)
                self.checkChildren(child,value)

    def checkParent(self,index):
        self.examingParents = True
        if not index.isValid() or self.examiningChildren:
            self.examingParents = False
            return
        else:
            parent = index.parent()
            if parent.data() == None:
                self.examingParents = False
                return
            value = self.checkChildrenStates(parent)
            self.setData(parent, value, Qt.CheckStateRole)

    def checkChildrenStates(self, index):
        childCount = self.rowCount(index)
        checkedChildrenCount = 0
        for i in range(childCount):
            child = index.child(i, 0)
            if child.data(Qt.CheckStateRole) == Qt.Checked or child.data(Qt.CheckStateRole) == Qt.PartiallyChecked:
                checkedChildrenCount += 1
        if checkedChildrenCount == 0:
            return 0
        elif checkedChildrenCount == childCount:
            return 2
        else:
            return 1



