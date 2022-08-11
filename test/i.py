import sys
import os
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMainWindow, QFileDialog, QLabel, QFrame, QSizePolicy, QPushButton
from PyQt5.QtWidgets import QHeaderView, QDesktopWidget, QToolBox, QTableWidget, QTableWidgetItem, QHBoxLayout
import time, json

from test1 import *
import adjustStyle

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  
        self.ui.centralwidget.setStyleSheet("background-color: rgb(0, 0, 65);")

        with open("pi.JSON") as f:
            pis = json.load(f)


        def addPiPage(name, rList):

            def addPis(layout, pi):

                def addToolBoxItem(widget, name, index):
                    noSpace = name.replace(" ", "")
                    self.ui.mainWidget = QWidget()
                    self.ui.vWidgetLayout = QtWidgets.QVBoxLayout(self.ui.mainWidget)
                    self.ui.widgetList = QtWidgets.QListWidget()
                    self.ui.vWidgetLayout.addWidget(self.ui.widgetList)
                    widget.addItem(self.ui.mainWidget, f"{name}")
                    widget.setItemText(index, f"{name}")
                    self.ui.widgetList.setObjectName(f"{noSpace}List")

                self.ui.mainFrame = QFrame()
                self.ui.mainPiLayout = QtWidgets.QVBoxLayout(self.ui.mainFrame)

                self.ui.piHeaderFrame, self.ui.piBodyFrame= QFrame(), QFrame()
                self.ui.mainPiLayout.addWidget(self.ui.piHeaderFrame)
                self.ui.mainPiLayout.addWidget(self.ui.piBodyFrame)

                self.ui.vHeaderLayout = QtWidgets.QVBoxLayout(self.ui.piHeaderFrame)
                self.ui.vBodyLayout = QtWidgets.QVBoxLayout(self.ui.piBodyFrame)
                self.ui.piTitle = QLabel(f"{pi}")
                self.ui.vHeaderLayout.addWidget(self.ui.piTitle)

                self.ui.piToolBox = QToolBox()

                addToolBoxItem(self.ui.piToolBox, "Manual Upload", 0)
                addToolBoxItem(self.ui.piToolBox, "Auto Upload", 1)
                addToolBoxItem(self.ui.piToolBox, "Archive", 2)

                self.ui.piToolBox.setStyleSheet(u"color: rgb(230, 230, 230);")

                self.ui.vBodyLayout.addWidget(self.ui.piToolBox)

                layout.addWidget(self.ui.mainFrame)

                adjustStyle.changeTheme("VEMI", self.ui.piTitle)

            self.ui.page = QWidget()
            self.ui.footerFrame, self.ui.mainBodyFrame = QFrame(), QFrame()

            self.ui.mainLayout = QtWidgets.QVBoxLayout(self.ui.page)   
            self.ui.mainLayout.addWidget(self.ui.mainBodyFrame)
            self.ui.mainLayout.addWidget(self.ui.footerFrame)

            self.ui.bodyLayout = QtWidgets.QHBoxLayout(self.ui.mainBodyFrame)
            
            self.ui.uploadButton  = QPushButton("Upload Files")
            self.ui.archiveFiles = QPushButton("Archive")

            self.ui.horizontalFooter = QtWidgets.QHBoxLayout(self.ui.footerFrame)
            self.ui.horizontalFooter.addWidget(self.ui.uploadButton)
            self.ui.horizontalFooter.addWidget(self.ui.archiveFiles)

            self.ui.stackedWidget.addWidget(self.ui.page)

            self.ui.button = QPushButton(f"{name} Pis")
            self.ui.verticalLayout.addWidget(self.ui.button)

            self.ui.uploadButton.setObjectName(f"{name}UploadFiles")
            self.ui.archiveFiles.setObjectName(f"{name}Archive")
            self.ui.button.setObjectName(f"{name}Button")
            self.ui.page.setObjectName(f"{name}Page")
            buttonList = [
                f"{name}Button", f"{name}Page", f"{name}Archive", f"{name}UploadFiles"
            ]

            buttons = [
                self.ui.uploadButton, self.ui.archiveFiles, self.ui.button, self.ui.pushButton
            ]
            
            for button in buttons:
                adjustStyle.changeTheme("VEMI", button)

            for pi in rList:
                addPis(self.ui.bodyLayout, pi)
            
            return buttonList

        def dynamicButtons(button, page = None, command = None):
            button = self.ui.buttonFrame.findChild(QPushButton, button)
            print(command, page)
            if page != None:
                page = self.ui.stackedWidget.findChild(QWidget, page)
                button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(page))

        self.ui.pushButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.home))
        previous, pagePis, keys = "", {}, pis.keys()
    
        for piName in keys:
            prefix = piName.split(" ")[0]
            if prefix != previous:
                pagePis[prefix] = {piName: pis[piName]}
            else:
                pagePis[prefix][piName] = pis[piName]
            previous = prefix
            noSpace = piName.replace(" ", "")
        
        for page in pagePis:
            piList = []
            for pi in pagePis[page]:
                piList.append(pi)
            print(piList)
            obj = addPiPage(page, piList)
            dynamicButtons(obj[0], page = obj[1])
            
        for piName in keys:
            noSpace = piName.replace(" ", "")
            # dynamicButtons(f"{noSpace}Button", f"{noSpace}Page")
    
        
        self.show()


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec_())