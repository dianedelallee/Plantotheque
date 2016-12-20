import sys
import os
from PyQt5.QtWidgets import (QDialog, QToolTip, QLabel,QWidget,
    QPushButton, QComboBox, QMessageBox, QApplication, QMainWindow, QAction, QGridLayout, QVBoxLayout, QGroupBox)
from PyQt5.QtGui import QFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import helpers.JsonHelper as jsonHelper



# ecrire les fonctions pour le menu




class Plantotheque(QMainWindow):
    ref = {}
    refFinal = {}
    cmpt = 0

    def __init__(self):
        super().__init__()

        self.initUI()



    def initUI(self):

        QToolTip.setFont(QFont('SansSerif', 10))

        self.menu()
        self.mode = "research"
        wid = QWidget(self)
        self.setCentralWidget(wid)
        layout = QGridLayout()

        self.drawUI(layout)

        wid.setLayout(layout)


        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('Plantothèque')
        self.show()


    def menu(self):

        addPlante = QAction("Add plante", self)
        addPlante.setShortcut("Ctrl+P")
        addPlante.setStatusTip('add a new plante to the database')
        addPlante.triggered.connect(self.addPlante)

        research = QAction("Research", self)
        research.setShortcut("Ctrl+R")
        research.setStatusTip("Research some plantes")
        research.triggered.connect(self.search_plantes)

        quitApp = QAction('Leave the app', self)
        quitApp.setShortcut('Ctrl+Q')
        quitApp.setStatusTip('Leave The App')
        quitApp.triggered.connect(self.close_application)

        self.statusBar()

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')

        fileMenu.addAction(addPlante)
        fileMenu.addAction(research)
        fileMenu.addAction(quitApp)

    def launchResearch(self):
        lay = self.centralWidget().layout()
        self.cmpt = 0
        criteria = {}
        for i in range(lay.count()):
            item = lay.itemAt(i).widget()
            if type(item) is QComboBox:
                criteria[self.ref[self.cmpt]] = item.currentText()
                self.cmpt += 1
        result = self.drawResult(criteria)
        lay.itemAt(lay.count()-2).widget().setText("recherche effectuée : " + str(len(result)) + " plante(s) trouvé(es)")
        if len(result) > 0:
            self.writeFile(result)

    def writeFile(self, result):
        compteur = 800
        size_plante = len(result[0])*20
        largeurP, hauteurP = A4
        centreX, centreY = largeurP/2, hauteurP/2
        c = canvas.Canvas("Result.pdf")
        c.setLineWidth(.3)
        c.setFont('Helvetica', 12)
        c.drawCentredString(centreX, compteur, "Plantothèque résultat ")
        compteur -= 30
        for plante in result:
            for eleK in plante:
                if eleK != "Image":
                    c.drawString(100, compteur, ""+str(eleK) + " : " + str(plante[eleK]))
                else:
                    compteur = self.drawAllImages(str(plante[eleK]), compteur, c, size_plante)
                compteur -= 20
            c.drawCentredString(centreX, compteur, "__________________________")
            compteur -= 20
            if compteur < size_plante:
                c.showPage()
                compteur = 800
        c.save()

    def drawAllImages(self, name: str, compteur: int, c: canvas, size_plante: int):
        case = name.split(".")
        cmpt = compteur-size_plante+10
        if len(case) == 2:
            c.drawImage("/Users/dianedelallee/Desktop/PythonProject/Plantotheque/img/" + name,
                                350, compteur+10, 100, 100)
        else:
            files = os.listdir("/Users/dianedelallee/Desktop/PythonProject/Plantotheque/img/" + name)
            largeur = 60
            for file in files:
                if largeur > 550:
                    largeur = 60
                    cmpt = cmpt - 120
                c.drawImage("/Users/dianedelallee/Desktop/PythonProject/Plantotheque/img/" + name + "/" + file,
                                largeur, cmpt, 100, 100)
                largeur += 125
            return cmpt
        return compteur

    def close_application(self):
        sys.exit()

    def search_plantes(self):
        if self.mode == "addPlante":
            self.switchMode()
            self.mode = "research"

    def addPlante(self):
        if self.mode == "research":
            self.switchMode()
            self.mode = "addPlante"


    def drawUI(self, layout):

        position_vertical = 0
        position_horizontal = 0

        class_json = jsonHelper.JsonHelper()
        data = jsonHelper.JsonHelper.read_file(class_json,
                    '/Users/dianedelallee/Desktop/PythonProject/Plantotheque/Criteria.json')

        for i in data:
            layout.addWidget(QLabel(i, self),position_vertical, position_horizontal)
            criteriaAdd = QLabel(i, self)
            criteriaAdd.setHidden(True)
            layout.addWidget(criteriaAdd, position_vertical, position_horizontal)
            if type(data[i]) is list:
                self.ref[self.cmpt] = i
                combo = QComboBox(self)
                for j in data[i]:
                    combo.addItem(j)
                layout.addWidget(combo, position_vertical, position_horizontal+1)
                self.cmpt += 1
            position_vertical += 1

        btn = QPushButton('Rechercher', self)
        layout.addWidget(btn, position_vertical, position_horizontal)
        btn.clicked.connect(self.launchResearch)

        btnAdd = QPushButton('Ajouter', self)
        btnAdd.setHidden(True)
        layout.addWidget(btnAdd, position_vertical, position_horizontal)
        btnAdd.clicked.connect(self.addToDB)
        position_vertical += 1


        layout.addWidget(QLabel("Que recherches-tu", self), position_vertical, position_horizontal)
        resAdd = QLabel("remplir les champs", self)
        resAdd.setHidden(True)
        layout.addWidget(resAdd, position_vertical, position_horizontal)

        self.show()

    def switchMode(self):
        lay = self.centralWidget().layout()
        for i in range(lay.count()):
            item = lay.itemAt(i).widget()
            item.setHidden(not item.isHidden())


    def addToDB(self):
        lay = self.centralWidget().layout()
        lay.itemAt(lay.count()-1).widget().setText("plante ajoutée")

    def drawResult(self, criteria:dict):
        result = []
        class_json = jsonHelper.JsonHelper()
        data = jsonHelper.JsonHelper.read_file(class_json,
                    '/Users/dianedelallee/Desktop/PythonProject/Plantotheque/DataBase.json')
        for plante in data["plantes"]:
            verify_criteria = True
            for criteriaKey in criteria.keys():
                if str(plante[criteriaKey]) != criteria[criteriaKey] and criteria[criteriaKey]!= "None"  :
                    verify_criteria = False
            if verify_criteria:
                result.append(plante)
        return result

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Plantotheque()
    sys.exit(app.exec_())