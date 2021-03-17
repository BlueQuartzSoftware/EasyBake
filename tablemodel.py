from PySide2.QtNetwork import QNetworkReply
from PySide2.QtCore import QAbstractTableModel, Qt, QModelIndex



class TableModel(QAbstractTableModel):
    def __init__(self,data ,parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.metadataList = []
        visited=[]
        queue=[]
        source=""

        for key in data.keys():
            visited.append(key)
            queue.append(key)
        curDict = data
        while queue:

            child = queue.pop(0)
            if not isinstance(curDict[child],dict):
                self.metadataList.append({"Key":child,"Value":curDict[child],"Source":source+child,"Checked":Qt.Unchecked})
            if child in curDict.keys() and isinstance(curDict[child],dict):
                curDict = curDict[child]
                source+= child+"/"

            if isinstance(curDict, dict):
                for key in curDict.keys():
                    if key not in visited:
                        visited.append(key)
                        queue.append(key)

    def rowCount(self, parent=QModelIndex()):
        return len(self.metadataList)

    def columnCount(self, parent=QModelIndex()):
        return 9

    def data(self, index, role):
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return index.row()
            elif index.column() == 1:
                return self.metadataList[index.row()]["Key"]
            elif index.column() == 2:
                if self.metadataList[index.row()]["Value"] == "None":
                    return ""
                return str(self.metadataList[index.row()]["Value"])
            elif index.column() == 3:
                return self.metadataList[index.row()]["Source"]
            #elif index.column() == 4:
            #    return self.metadataList[index.row()][0]
            elif index.column() == 5:
                return str(type(self.metadataList[index.row()]["Value"])).split("'")[1].upper()
        elif role == Qt.CheckStateRole:
            if index.column() == 6:
                return self.metadataList[index.row()]["Checked"]
            elif index.column() == 7:
                return self.metadataList[index.row()]["Checked"]
            #elif index.column() == 8:
            #    return self.metadataList[index.row()][0]

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            if section == 0:
                return "#^"
            elif section == 1:
                return "Key"
            elif section == 2:
                return "Value"
            elif section == 3:
                return "Source"
            elif section == 4:
                return "Default Value"
            elif section == 5:
                return "Type"
            elif section == 6:
                return "Require"
            elif section == 7:
                return "Editable"
            elif section == 8:
                return " "
            return None
    def setData(self,index, value, role):
        if role == Qt.EditRole:
            if not index.isValid():
                return False
            if index.column() == 0:
                self.metadataList.insert(int(value),self.metadataList[index.row()])
            elif index.column() == 1:
                self.metadataList[index.row()]["Key"] = value
            elif index.column() == 2:
                self.metadataList[index.row()]["Value"] = value
            elif index.column() == 3:
                print("hi")
                #self.metadataList[index.row()]["Source"] = value
            return True
        elif role == Qt.CheckStateRole:
            if index.column() == 6 or index.column() == 7:
                self.changeChecked(index)
            self.dataChanged.emit(index, index)
            return True



        return False

    def changeChecked(self, index):
        if self.metadataList[index.row()]["Checked"] == Qt.Unchecked:
            self.metadataList[index.row()]["Checked"] = Qt.Checked
        else:
            self.metadataList[index.row()]["Checked"] = Qt.Unchecked

    def flags(self, index):
        if not index.isValid():

            return Qt.ItemIsEnabled
        if index.column() < 5:
            return Qt.ItemFlags(QAbstractTableModel.flags(self,index) | Qt.ItemIsEditable)
        elif index.column() == 6 or index.column() == 7:
            return Qt.ItemFlags(QAbstractTableModel.flags(self,index) | Qt.ItemIsUserCheckable)
        else:
            return Qt.ItemIsEnabled
