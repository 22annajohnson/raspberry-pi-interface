"""
    Author: Anna Johnson
    Date:  06/28/2022
    Version: 1
    Description: GUI to ssh into 6 Raspberry Pis, uploads user defined videos, and 
    runs command to play selected videos
"""
 
import sys
import os
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMainWindow, QFileDialog, QLabel, QFrame, QSizePolicy, QMessageBox
from PyQt5.QtWidgets import QHeaderView, QDesktopWidget, QToolBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton
import time, json, paramiko

import connectRemote as ct
### Imports the generated Python programs for each page
from homeScreen import *
import makeVideo
 
workingDir= os.getcwd()
with open("./resources/preferences.JSON") as f:
        preferences = json.load(f)

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        ###################################################
        ### Removes the top control bar from the window ### 
        ###################################################

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        ####################################################
        #### Sets and configures a shadow on the window ####
        ####################################################

        self.shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(50)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QtGui.QColor(0, 92, 157, 550))
        
        self.ui.centralwidget.setGraphicsEffect(self.shadow)
        
        ###################################################
        ###### Adds the title and icon to the window ###### 
        ###################################################

        self.setWindowIcon(QtGui.QIcon(":/icons/icons/duck.svg"))
        self.setWindowTitle("RPI Interface")
        self.ui.headerMenuButton.setIcon(QtGui.QIcon(":/icons/icons/menu.svg"))

        ####################################################
        ###### Centers the window to the users screen ###### 
        ####################################################

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        ###################################################
        ###### Adds functionality to the nav buttons ######
        ###################################################

        QtWidgets.QSizeGrip(self.ui.sizeGrip)

        ### Function to dynamically connect buttons to their functions
        def connectButtons(dictionary, option, inputType=None):
            if inputType == dict:
                for button in dictionary:
                    if option == "function":
                        button.clicked.connect(dictionary[button])
                
            elif option == "page":
                for page in dictionary:
                    page.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(dictionary[page]))

        # Dictionary containing buttons and corresponding functions
        buttonDictionary = {
            self.ui.minimize: (lambda: self.showMinimized()),
            self.ui.exit: (lambda: self.close()),
            self.ui.exitButton: (lambda: self.close()),
            self.ui.fullScreen: (lambda: self.restoreMaximize()),
            self.ui.headerMenuButton: (lambda: self.slideLeftMenu()),
            self.ui.imageToVidUploadFile: lambda: self.browseFiles(t = self.ui.tableWidget, duration = 3),
            self.ui.imageToVidUploadFolder: (lambda: self.browseFiles(t = self.ui.tableWidget, duration = 3)),
            self.ui.imageToVidConvert: (lambda: self.mp4Convert(self.ui.tableWidget)), 
        }

        connectButtons(buttonDictionary, "function", inputType=dict)

        ### Setting the default page on the main body stackedWidget
        self.ui.stackedWidget.setCurrentWidget(self.ui.homePage)

        ####################################################
        ##### Connecting the menu buttons to the pages #####
        ####################################################

        # Dictionary containing buttons and corresponding pages
        pageDictionary = {
            self.ui.overall: self.ui.sysInfoOverall,
            self.ui.preferences: self.ui.settingsPreferences,
            self.ui.versionInformation: self.ui.settingsVersionInfo,
            self.ui.imageToVideo: self.ui.imageToVid,
            self.ui.footerDuck: self.ui.homePage,
            self.ui.headerVemiButton: self.ui.homePage,
            self.ui.sideMenuDuck: self.ui.homePage,
            self.ui.headerHomeButton: self.ui.homePage
            }

        for page in pageDictionary:
            connectButtons({page: pageDictionary[page]}, "page")

        ####################################################
        ######### Formatting Tables and Adding Data ########
        ####################################################

        ### Function to connect dictionarys of data to table widgets
        def setTableData(table, data):
            headers = []
            for n, key in enumerate(data):
                headers.append(key)
                for m, item in enumerate(data[key]):
                    newItem = QTableWidgetItem(item)
                    table.setItem(m, n, newItem)
            table.setHorizontalHeaderLabels(headers)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.horizontalHeader().setStretchLastSection(True)
            table.setAlternatingRowColors(True)

        # Adds tabel data to image to vid convertsion tool
        tableData = {
            "Image": [],
            "Path": [],
            "Duration": []
            }
        setTableData(self.ui.tableWidget, tableData)

        ###############################################
        ######### Connecting to Pis in Pi.JSON ########
        ###############################################

        # Retrieves info on pis saved in the pi.JSON file
        with open("./resources/pi.JSON") as f:
            pi = json.load(f)
        keys = pi.keys()
        
        # Remote paths to screen player directories
        screenPlayer = "/home/pi/ScreenPlayer"
        manual = f"{screenPlayer}/ManualUpload"
        auto = f"{screenPlayer}/AutoUpload"
        archive = f"{screenPlayer}/Archive"
        
        filesDictionary = {}
        # Gets list of files in each program folder on pis
        for rPi in keys:
            ip = pi[rPi]["ip"]
            files, sftp = ct.fileList(ip, [manual, auto, archive])
            sftp.close()
            filesDictionary[rPi] = {}
            filesDictionary[rPi]["Manual"], filesDictionary[rPi]["Auto"], filesDictionary[rPi]["Archive"] = files[0], files[1], files[2]
        # ct.uploadFile("10.10.0.200", f"{workingDir}\8122022_10-6-3.mp4", auto)

        ###############################################
        ###### Dynamically adds pages for Pis and #####
        ###########       Pi grouping      ############
        ###############################################


        ### Function that dynamically adds style classes to elements
        def addStyleClass(e, c ="", classType=None):
            if classType==dict:
                for element in e:
                    element.setProperty("class", e[element])
            else: e.setProperty("class", c)

        ### Funtion to add new menu tabs
        def addToolBoxItem(widget, name, index, indicator=""):
            noSpace = name.replace(" ", "")
            self.ui.mainWidget = QWidget()
            self.ui.vWidgetLayout = QtWidgets.QVBoxLayout(self.ui.mainWidget)
            self.ui.widgetList = QtWidgets.QListWidget()
            self.ui.widgetList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            self.ui.vWidgetLayout.addWidget(self.ui.widgetList)
            widget.insertItem(index, self.ui.mainWidget, QtGui.QIcon("./icons/chevron-down.svg") ,f"{name}")
            widget.setItemText(index, f"{name}")
            self.ui.widgetList.setObjectName(f"{indicator}{noSpace}List")

        ### Function to add new pi grouping pages
        def addPiPage(name, rList):

            def addPis(layout, pi):

                self.ui.mainFrame = QFrame()
                self.ui.mainPiLayout = QtWidgets.QVBoxLayout(self.ui.mainFrame)

                self.ui.piHeaderFrame, self.ui.piBodyFrame= QFrame(), QFrame()
                self.ui.mainPiLayout.addWidget(self.ui.piHeaderFrame)
                self.ui.mainPiLayout.addWidget(self.ui.piBodyFrame)

                self.ui.vHeaderLayout = QtWidgets.QVBoxLayout(self.ui.piHeaderFrame)
                self.ui.vBodyLayout = QtWidgets.QVBoxLayout(self.ui.piBodyFrame)
                self.ui.piTitle = QLabel(f"{pi}")
                addStyleClass({self.ui.piTitle: "fs-heading"}, classType=dict)
                self.ui.vHeaderLayout.addWidget(self.ui.piTitle)

                self.ui.piToolBox = QToolBox()
                addToolBoxItem(self.ui.piToolBox, "Manual Upload", 0)
                addToolBoxItem(self.ui.piToolBox, "Auto Upload", 1)
                addToolBoxItem(self.ui.piToolBox, "Archive", 2)

                self.ui.piToolBox.setStyleSheet(u"color: rgb(230, 230, 230);")

                noSpace = pi.replace(" ", "")

                self.ui.piToolBox.setObjectName(f"{noSpace}ToolBox")
                self.ui.piBodyFrame.setObjectName(f"{noSpace}BodyFrame")
                self.ui.mainFrame.setObjectName(f"{noSpace}MainFrame")

                dynamicList = [f"{noSpace}ToolBox", f"{noSpace}BodyFrame", f"{noSpace}MainFrame"]

                self.ui.vBodyLayout.addWidget(self.ui.piToolBox)

                layout.addWidget(self.ui.mainFrame)


                return dynamicList

            self.ui.page = QWidget()
            self.ui.footerFrame, self.ui.mainBodyFrame = QFrame(), QFrame()

            self.ui.mainLayout = QtWidgets.QVBoxLayout(self.ui.page)   
            self.ui.mainLayout.addWidget(self.ui.mainBodyFrame)
            self.ui.mainLayout.addWidget(self.ui.footerFrame)

            self.ui.bodyLayout = QtWidgets.QHBoxLayout(self.ui.mainBodyFrame)
            
            self.ui.uploadButton  = QPushButton("Upload Files")
            self.ui.archiveFiles = QPushButton("Archive")

            addStyleClass({self.ui.uploadButton: "button", self.ui.archiveFiles: "button"}, classType=dict)

            self.ui.horizontalFooter = QtWidgets.QHBoxLayout(self.ui.footerFrame)
            # self.ui.horizontalFooter.addWidget(self.ui.uploadButton)
            # self.ui.horizontalFooter.addWidget(self.ui.archiveFiles)

            self.ui.stackedWidget.addWidget(self.ui.page)

            noSpace = name.replace(" ", "")
            self.ui.uploadButton.setObjectName(f"{noSpace}UploadFiles")
            self.ui.archiveFiles.setObjectName(f"{noSpace}Archive")
            self.ui.mainBodyFrame.setObjectName(f"{noSpace}MainBodyFrame")
            self.ui.page.setObjectName(f"{noSpace}Page")

            buttonList = [
                f"{noSpace}Page", f"{noSpace}Archive", f"{noSpace}UploadFiles"
                ]

            buttons = [
                self.ui.uploadButton, self.ui.archiveFiles
                ]
            
            for pi in rList:
                dynamicList = addPis(self.ui.bodyLayout, pi)
                for item in dynamicList:
                    buttonList.append(item)
            
            return buttonList
           
        
        ### Function to start slide show on Pi
        def startSlideShow(pi):
            slideShowButton = self.sender()
            
            piName = slideShowButton.objectName().replace("SlideShow", "")
            addSpace = ""
            addedSpace = False
            for letter in piName:
                if addedSpace != True:
                    try:
                        int(letter)
                        addSpace = f"{addSpace} {letter}"
                        addedSpace = True
                    except:
                        addSpace = f"{addSpace}{letter}"
                else: 
                    addSpace = f"{addSpace}{letter}"
            ip = pi[addSpace]["ip"]

            if slideShowButton.text() == "Stop Slide Show":
                ct.slideShow(ip, option="kill")
                slideShowButton.setText("Start Slide Show")
                return

            ct.slideShow(ip)
            slideShowButton.setText("Stop Slide Show")

        ### Function that archives selected files
        def archiveFiles(pi):
            archiveButton = self.sender()
            piName = archiveButton.objectName().replace("ArchiveButton", "")
            addSpace = ""
            addedSpace = False
            for letter in piName:
                if addedSpace != True:
                    try:
                        int(letter)
                        addSpace = f"{addSpace} {letter}"
                        addedSpace = True
                    except:
                        addSpace = f"{addSpace}{letter}"
                else: 
                    addSpace = f"{addSpace}{letter}"
            print(addSpace)
            ip = pi[addSpace]["ip"]
            
            footerFrame = archiveButton.parent()
            mainBodyFrame = footerFrame.parent()
            bodyFrame = mainBodyFrame.findChild(QFrame, f"{piName}Body")
            toolBox = bodyFrame.findChild(QToolBox, f"{piName}ToolBox")
            listBox = toolBox.findChild(QWidget, f"AutoUploadList")
            archiveListBox = toolBox.findChild(QWidget, f"ArchiveList")
            
            # print("Listbox count: ",listBox.count())
            selectedItems = listBox.selectedItems()
            path = "/home/pi/ScreenPlayer/AutoUpload/"
            workingDir = os.getcwd()
            for file in selectedItems:
                row = listBox.row(file)
                
                item = QtWidgets.QListWidgetItem(file)
                archiveListBox.addItem(item)
                listBox.takeItem(row)
                print(str(file.text()))
                ct.archiveFile(ip, str(file.text()), workingDir)

        
        ### Function to find/connect dynamically made opjects
        def dynamicElement(target, objectParent, elementType, command = None, page = None, listBox = None, ip = None):
            widgetList = ["QWidget", "QListWidget", "QFrame", "QToolBox", "Archive"]
            if elementType == "QPushButton":
                target = objectParent.findChild(QPushButton, target)
                if command == None:
                    target.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(page))
                elif command =="BrowseFiles":
                    connectButtons({target: lambda: self.browseFiles(l=listBox, ip=ip)}, "function", inputType=dict)
                else:
                    target.clicked.connect(command)
            elif elementType in widgetList:
                target = objectParent.findChild(QWidget, target)
                return(target)


            # TODO: uncomment and fix
            # if page != None:
            #     page = self.ui.stackedWidget.findChild(QWidget, page)
            #     button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(page))

        # Segments pis into groups based on their names in pi.JSON file
        # Example: "Tour": {"Tour 1":..., "Tour 2":..., "Tour 3":...}
        previous, pagePis, = "", {}
        for piName in keys:
            prefix = piName.split(" ")[0]
            if prefix != previous:
                pagePis[prefix] = {piName: pi[piName]}
            else:
                pagePis[prefix][piName] = pi[piName]
            previous = prefix
        
        ### Function to add Individual to the user interface
        def addIndividualPages(piName, piGroup):
            noSpace = piName.replace(" ", "")
            elementList = [f"{noSpace}Page", f"{noSpace}NavFrame"]

            self.ui.page = QWidget()
            self.ui.page.setObjectName(f"{noSpace}Page")
            self.ui.stackedWidget.addWidget(self.ui.page)
            
            self.ui.layout = QtWidgets.QHBoxLayout(self.ui.page)  

            self.ui.navFrame = QFrame()
            self.ui.navFrame.setMinimumSize(QtCore.QSize(200, 0))
            self.ui.navFrame.setObjectName(f"{noSpace}NavFrame")

            self.ui.mainBodyFrame = QFrame()
            self.ui.mainBodyFrame.setObjectName(f"{noSpace}MainBody")

            self.ui.layout.addWidget(self.ui.mainBodyFrame)
            self.ui.layout.addWidget(self.ui.navFrame)

            self.ui.navLayout = QtWidgets.QVBoxLayout(self.ui.navFrame)
            self.ui.navLayout.setObjectName(f"{noSpace}NavFrame")

            for num, pi in enumerate(piGroup):
                self.ui.navButton = QPushButton(str(num+1))
                self.ui.navButton.setObjectName(f"{num}Button")
                self.ui.navLayout.addWidget(self.ui.navButton)
                
                # elementList.append(f"{num}Button")

                if pi == piName:
                    self.ui.navButton.setProperty("class", "nav-button nav-button-self")
                else:
                    self.ui.navButton.setProperty("class", "nav-button")

            self.ui.spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.ui.navLayout.addItem(self.ui.spacer)

            self.ui.headerFrame, self.ui.bodyFrame, self.ui.footerFrame = QFrame(), QFrame(), QFrame()
            self.ui.mainBodyLayout = QtWidgets.QVBoxLayout(self.ui.mainBodyFrame)
            self.ui.mainBodyLayout.addWidget(self.ui.headerFrame)
            self.ui.mainBodyLayout.addWidget(self.ui.bodyFrame)
            self.ui.mainBodyLayout.addWidget(self.ui.footerFrame)


            self.ui.headerFrame.setObjectName(f"{noSpace}Header")
            self.ui.bodyFrame.setObjectName(f"{noSpace}Body")
            self.ui.footerFrame.setObjectName(f"{noSpace}Footer")

            elementList.append(f"{noSpace}MainBody")
            elementList.append(f"{noSpace}Header")
            elementList.append(f"{noSpace}Body")
            elementList.append(f"{noSpace}Footer")

            self.ui.headerLayout = QtWidgets.QHBoxLayout(self.ui.headerFrame)
            self.ui.header = QLabel(piName)
            self.ui.headerLayout.addWidget(self.ui.header)

            self.ui.bodyLayout = QtWidgets.QVBoxLayout(self.ui.bodyFrame)
            self.ui.toolBox = QToolBox()
            self.ui.toolBox.setObjectName(f"{noSpace}ToolBox")
            elementList.append(f"{noSpace}ToolBox")
            addToolBoxItem(self.ui.toolBox, "Manual Upload", 0)
            addToolBoxItem(self.ui.toolBox, "Auto Upload", 1)
            addToolBoxItem(self.ui.toolBox, "Archive", 2)

            manual = dynamicElement(f"ManualUploadList", self.ui.toolBox, "QListWidget")
            auto = dynamicElement(f"AutoUploadList", self.ui.toolBox, "QListWidget")
            archive = dynamicElement(f"ArchiveList", self.ui.toolBox, "QListWidget")

            for directoryList in filesDictionary[piName]:
                for item in filesDictionary[piName][directoryList]:
                    if directoryList == "Manual":
                        manual.addItem(item) 
                    elif directoryList == "Auto":
                        auto.addItem(item)
                    else:
                        archive.addItem(item)


            self.ui.bodyLayout.addWidget(self.ui.toolBox)


            self.ui.uploadButton, self.ui.archiveButton, self.ui.slideShow = QPushButton("Upload Files"), QPushButton("Archive Files"), QPushButton("Start Slide Show")


            self.ui.footerLayout = QtWidgets.QHBoxLayout(self.ui.footerFrame)
            self.ui.footerLayout.addWidget(self.ui.uploadButton)
            self.ui.footerLayout.addWidget(self.ui.archiveButton)
            self.ui.footerLayout.addWidget(self.ui.slideShow)
            
            self.ui.uploadButton.setObjectName(f"{noSpace}UploadButton")
            self.ui.archiveButton.setObjectName(f"{noSpace}ArchiveButton")
            self.ui.slideShow.setObjectName(f"{noSpace}SlideShow")
            
            elementList.append(f"{noSpace}UploadButton")
            elementList.append(f"{noSpace}ArchiveButton")
            elementList.append(f"{noSpace}SlideShow")


            styleDictionary = {
                self.ui.uploadButton: "button",
                self.ui.archiveButton: "button",
                self.ui.slideShow: "button",
                self.ui.header: "fs-heading",
                }

            addStyleClass(styleDictionary, classType=dict)
            return self.ui.page, elementList

        ### Function to add buttons to the menus for each Pi/Pi grouping
        def addMenuButtons(piList, widget, allPis, dictionary = None):
            objectDictionary, uploadDictionary = {}, {}
            if dictionary == None:
                elementList = []
            self.ui.verticalButtonLayout = QtWidgets.QVBoxLayout(widget)
            for piName in piList:
                # Adds the buttons to the menu
                noSpace = piName.replace(" ", "")
                self.ui.piButton = QPushButton(f"{piName}")
                self.ui.verticalButtonLayout.addWidget(self.ui.piButton)
                self.ui.piButton.setObjectName(f"{noSpace}MenuButton")
                self.ui.piButton.setProperty("class", "button")

                # Adds the pages to the widget
                if dictionary == None:
                    # Connects the buttons to the pages
                    page, obj = addIndividualPages(piName, piList)
                    elementList.append(obj)
                    uploadDictionary[piName] = obj
                    connectButtons({self.ui.piButton: self.ui.page}, "page")
                else:
                    keys = dictionary[piName.replace(" Pis", "")].keys()
                    obj = addPiPage(piName, keys)                
                    objectDictionary[piName] = obj

                    findPage = dynamicElement(obj[0], self.ui.stackedWidget, "QWidget")
                    connectButtons({self.ui.piButton: findPage}, "page")

            elements = {
                "Pages": [],
                "NavFrames": [],
            }
            if dictionary == None:
                for pageElements in elementList:
                    page = dynamicElement(pageElements[0], self.ui.stackedWidget, "QWidget")
                    nav = dynamicElement(pageElements[1], page, "QFrame")
                    elements["Pages"].append(page)
                    elements["NavFrames"].append(nav)
                
                for nav in elements["NavFrames"]:
                    for num, page in enumerate(elements["Pages"]):
                        button = dynamicElement(f"{num}Button", nav, "QPushButton", page=page)


                

            return objectDictionary, uploadDictionary

        addToolBoxItem(self.ui.dropMenu, "All Pis", 0)
        
        # Adds each Pi to a master list to add to menu
        pageList, upload = [], {}
        for counter, page in enumerate(pagePis, start=1):
            piList = []
            pageList.append(f"{page} Pis")

            for rPi in pagePis[page]:
                piList.append(rPi)

            #TODO: uncomment and add functionality
                # obj = addPiPage(page, piList)
                # dynamicButtons(obj[0], page = obj[1])

            addToolBoxItem(self.ui.dropMenu, f"{page} Pis", counter)
            element = dynamicElement(f"{page}PisList", self.ui.dropMenu, "QWidget")
            unNeeded, uploadDictionary = addMenuButtons(piList, element, pi)
            upload[page] = uploadDictionary
        
        element = dynamicElement("AllPisList", self.ui.dropMenu, "QWidget")
        elementDictionary, unNeeded = addMenuButtons(pageList, element, pi, dictionary = pagePis)
        
        ###################################################
        ######### Formatting Lists and Adding Data ########
        ###################################################

        # List of each grouping of Pis 
        # Example: Space Pis, Tour Pis
        piGroups = list(elementDictionary.keys())

        # Populates the list widgets with the files on each Pi
        currentGroup, piCounter = piGroups[0], 0
        for rPi in filesDictionary:
            noSpace = rPi.replace(" ", "")
            # Finds the correct grouping of Pis in the element dictionary
            if piCounter >= (len(elementDictionary[currentGroup])-3)/3:
                index = piGroups.index(currentGroup)
                if index + 1 != len(piGroups):
                    currentGroup = piGroups[index+1]
                    piCounter = 0
                else: break

            # Finds the dynamically created elements and populates the file list widgets
            for directoryList in filesDictionary[rPi]:
                listIndex = (piCounter+1)*3

                page = dynamicElement(elementDictionary[currentGroup][0], self.ui.stackedWidget, "QWidget")
                mainFrame = dynamicElement(elementDictionary[currentGroup][listIndex+2], page, "QFrame")
                bodyFrame = dynamicElement(elementDictionary[currentGroup][listIndex+1], mainFrame, "QFrame")
                footerFrame = dynamicElement(f"{noSpace}Footer", mainFrame, "QFrame")

                toolBox = dynamicElement(elementDictionary[currentGroup][listIndex], bodyFrame, "QFrame")

                if directoryList == "Manual":
                    listBox = dynamicElement(f"ManualUploadList", toolBox , "QListWidget")
                elif directoryList == "Auto":
                    listBox = dynamicElement(f"AutoUploadList", toolBox, "QListWidget")
      
                elif directoryList == "Archive":
                    listBox = dynamicElement(f"ArchiveList", toolBox, "QListWidget")
                for item in filesDictionary[rPi][directoryList]:
                    listBox.addItem(item)    

            piCounter+=1

        # Adds functionality to Upload File Buttons on Individual pages
        archiveButtons = {}
        for group in upload:
            for piName in upload[group]:
                noSpace = piName.replace(" ", "")
                page = dynamicElement(upload[group][piName][0], self.ui.centralwidget, "QWidget")
                mainBody = dynamicElement(upload[group][piName][2], page, "QFrame")
                footer = dynamicElement(upload[group][piName][5], mainBody, "QFrame")
                body = dynamicElement(upload[group][piName][4], mainBody, "QFrame")
                toolBox = dynamicElement(upload[group][piName][6], body, "QToolBox")
                listBox = dynamicElement("AutoUploadList", toolBox, "QListWidget")
                # print(listBox.objectName())

                dynamicElement(upload[group][piName][7], footer, "QPushButton", command = "BrowseFiles", listBox = listBox, ip = pi[piName]["ip"])
                # archiveButton = dynamicElement(upload[group][piName][8], footer, "QWidget")
                # archiveButtons[archiveButton] = lambda:archiveFiles(upload[group], archiveButton, pi[piName]["ip"])
                # connectButtons({archiveButton: lambda:archiveFiles(upload[group], archiveButton, pi[piName]["ip"])}, option="function", inputType=dict)
                dynamicElement(upload[group][piName][8], footer, "QPushButton", command = lambda:archiveFiles(pi))
                
                dynamicElement(upload[group][piName][9], footer, "QPushButton", command = lambda:startSlideShow(pi))
        
        # print(json.dumps(archiveButtons, indent = 3))
        # connectButtons(archiveButtons, option="function", inputType=dict)

        ####################################################
        ### Styles the UI elements with user preferences ###
        ####################################################

        elementDictionary = {
            self.ui.slideMenu: "bg-secondary",
            self.ui.dropMenuFrame: "bg-secondary",
            self.ui.exitFrame: "bg-secondary",
            self.ui.sideMenuLabelFrame: "bg-secondary",
            self.ui.imageToVideo: "button",
            self.ui.overall: "button",
            self.ui.preferences: "button",
            self.ui.versionInformation: "button",
            self.ui.exitButton: "button-icon bg-secondary",
            self.ui.sideMenuDuck: "button-icon bg-secondary",
            self.ui.sideMenuLabel: "fs-heading bg-secondary",
            self.ui.imageToVidUploadFile: "button",
            self.ui.imageToVidUploadFolder: "button",
            self.ui.imageToVidConvert: "button",
            self.ui.imageToVidTitle: "fs-heading"
            }

        addStyleClass(elementDictionary, classType=dict)

        ####################################################
        ##### Adds final functionality to main window #####
        ####################################################

        ### Function to move the window around by clicking the header
        def moveWindow(e):
            if self.isMaximized() == False:
                if e.buttons() == QtCore.Qt.LeftButton:
                    self.move(self.pos() +e.globalPos() - self.clickPosition)
                    self.clickPosition = e.globalPos()
                    e.accept()
      
        self.ui.headerframe.mouseMoveEvent = moveWindow
        
        self.show()

    ### Function that animates the side menu 
    def slideLeftMenu(self):
        
        width = self.ui.slideMenuContainer.width()
        if width < 400:
            newWidth = 400
            
        else:
            newWidth = 0
            
        self.animation = QtCore.QPropertyAnimation(self.ui.slideMenuContainer, b"maximumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(newWidth)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutBounce)
        self.animation.start()

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        
    ### Function that monitors the mouse if pressed
    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()
    
    ### Function that changes the size of the window
    def restoreMaximize(self):
        if self.isMaximized():
            self.showNormal()
            self.ui.fullScreen.setIcon(QtGui.QIcon(":/icons/icons/maximize-2.svg"))
        else:
            self.showMaximized()
            self.ui.fullScreen.setIcon(QtGui.QIcon(":/icons/icons/minimize-2.svg"))
        self.ui.fullScreen.setIconSize(QtCore.QSize(30, 30))
        # self.ui.fullScreen.height(45)

    ###Function to open a file explorer window
    def browseFiles(self, t = None, duration = "", l = None, ip = None):
        fname = QFileDialog.getOpenFileName(self, "Choose a File", f"{workingDir}", "Image files (*.jpg *.jpeg)")
        path, fileName = fname[0], fname[0].split("/")[-1]
        if t != None:
            rows = t.rowCount()
            t.insertRow(rows)
            t.setItem(rows, 0, QTableWidgetItem(str(fileName)))
            t.setItem(rows, 1, QTableWidgetItem(str(path)))
            if duration != "":
                t.setItem(rows, 2, QTableWidgetItem(str(duration)))
        elif l != None:
            # print(fileName)
            l.addItem(fileName)
            if ip != None:
                ct.uploadFile(ip, path, f"/home/pi/ScreenPlayer/AutoUpload/{fileName}")
            return fileName
        else: print("else")

    ###Function to convert photos to .mp4 file
    def mp4Convert(self, table):
        photoList, durationList = [], []
        for row in range(0, table.rowCount()):
            photoList.append(table.item(row, 1).text())
            durationList.append(table.item(row, 2).text())
        makeVideo.compile(photoList, durationList)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    with open(f"{workingDir}/style/vemi.css","r") as file:
        app.setStyleSheet(file.read())
    sys.exit(app.exec_())


    #TODO: open live streams and web addresses
    #TODO: allow users to name videos