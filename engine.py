import os
import sys
import random
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFrame, QDesktopWidget, QMessageBox

class Board(QFrame):

    msg2Statusbar = pyqtSignal(str)
    game_over_signal = QtCore.pyqtSignal()
    keyPressevent = QtCore.pyqtSignal()

    BoardWidth = 10
    BoardHeight = 20
    Speed = 300

    def __init__(self, parent):
        super().__init__(parent)
        
        self.initBoard()
        self.savedPiece = None
        self.isSavedPiece = False 


    def initBoard(self):

        self.timer = QBasicTimer()
        self.isWaitingAfterLine = False

        self.curX = 0
        self.curY = 0
        self.numLinesRemoved = 0
        self.board = []

        self.setFocusPolicy(Qt.StrongFocus)
        self.isStarted = False
        self.isPaused = False
        self.clearBoard()

    def drawProjection(self, painter):
        if self.curPiece.shape() == Tetrominoe.NoShape:
            return

        projectionPiece = self.curPiece
        projectionX = self.curX
        projectionY = self.curY

        while self.tryMove(projectionPiece, projectionX, projectionY - 1):
            projectionY -= 1

        for i in range(4):
            x = projectionX + projectionPiece.x(i)
            y = projectionY - projectionPiece.y(i)
            self.drawSquare(painter, self.squareWidth() * x, self.squareHeight() * y,
                            Tetrominoe.ProjectionShape)

    def start(self):
        self.clearBoard()

        if self.isPaused:
            return
        
        self.isStarted = True
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0

        self.msg2Statusbar.emit(str(self.numLinesRemoved))

        self.newPiece()
        self.timer.start(Board.Speed, self)

    def savePiece(self):
        if not self.isSavedPiece:
            self.savedPiece = self.curPiece
            self.curPiece = Shape()
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.update()
        if self.savedPiece is not None:  # Если есть сохраненная фигура
            self.isSavedPiece = True  # Установка флага сохраненной фигуры

            self.curPiece = self.savedPiece
            self.curPiece.setShape(self.savedPiece.shape())
            self.curX = Board.BoardWidth // 2 + 1
            self.curY = Board.BoardHeight - 1 + self.curPiece.minY()
            self.newPiece()  # Исправленный вызов метода
            self.update()
        else:
            self.savePiece()  # Если нет сохраненной фигуры, сохраняем текущую

    def shapeAt(self, x, y):
        return self.board[(y * Board.BoardWidth) + x]

    def setShapeAt(self, x, y, shape):
        self.board[(y * Board.BoardWidth) + x] = shape

    def squareWidth(self):
        return self.rect().width() // Board.BoardWidth

    def squareHeight(self):
        return self.rect().height() // Board.BoardHeight

    def pause(self):

        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.msg2Statusbar.emit("paused")

        else:
            self.timer.start(Board.Speed, self)
            self.msg2Statusbar.emit(str(self.numLinesRemoved))

        self.update()

    def resume(self):
        if not self.isStarted or not self.isPaused:
            return

        self.isPaused = False
        self.timer.start(Board.Speed, self)
        self.msg2Statusbar.emit(str(self.numLinesRemoved))

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        boardTop = rect.top()
        
        squareWidth = rect.width() // Board.BoardWidth
        squareHeight = rect.height() // Board.BoardHeight
        painter.setPen(QColor(0, 0, 0))

        # Рисование вертикальных линий
        for x in range(Board.BoardWidth + 1):
            painter.drawLine(rect.left() + x * squareWidth, boardTop,
                            rect.left() + x * squareWidth, boardTop + rect.height())

        # Рисование горизонтальных линий
        for y in range(Board.BoardHeight + 1):
            painter.drawLine(rect.left(), boardTop + y * squareHeight,
                            rect.left() + rect.width(), boardTop + y * squareHeight)

        # Рисование заполненных клеток на игровом поле
        for y in range(Board.BoardHeight):
            for x in range(Board.BoardWidth):
                shape = self.shapeAt(x, Board.BoardHeight - y - 1)

                if shape != Tetrominoe.NoShape:
                    self.drawSquare(painter,
                                    rect.left() + x * squareWidth,
                                    boardTop + y * squareHeight, shape)

        # Рисование текущей падающей фигуры
        if self.curPiece.shape() != Tetrominoe.NoShape:
            for i in range(4):
                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)
                self.drawSquare(painter, rect.left() + x * squareWidth,
                                boardTop + (Board.BoardHeight - y - 1) * squareHeight,
                                self.curPiece.shape())

    def keyPressEvent(self, event):

        if not self.isStarted or self.curPiece.shape() == Tetrominoe.NoShape:
            super(Board, self).keyPressEvent(event)
            return

        key = event.key()
        
        if key == Qt.Key_P:
            self.pause()
            return

        if self.isPaused:
            return

        elif key == Qt.Key_Left:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)

        elif key == Qt.Key_Right:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)

        elif key == Qt.Key_Down:
            self.oneLineDown()

        

        elif key == Qt.Key_Shift:
            self.savePiece()

        elif key == Qt.Key_Up:
            self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)

        elif key == Qt.Key_Space:
            self.dropDown()
        
        elif key == Qt.Key_Escape:
            self.pause()
            self.keyPressevent.emit()
            return

        else:
            super(Board, self).keyPressEvent(event)

    def timerEvent(self, event):

        if event.timerId() == self.timer.timerId():

            if self.isWaitingAfterLine:
                self.isWaitingAfterLine = False
                self.newPiece()
            else:
                self.oneLineDown()

        else:
            super(Board, self).timerEvent(event)

    def clearBoard(self):

        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(Tetrominoe.NoShape)

    def dropDown(self):

        newY = self.curY

        while newY > 0:

            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break

            newY -= 1

        self.pieceDropped()

    def oneLineDown(self):

        if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
            self.pieceDropped()

    def pieceDropped(self):

        for i in range(4):

            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())

        self.removeFullLines()

        if not self.isWaitingAfterLine:
            self.newPiece()

    def removeFullLines(self):

        numFullLines = 0
        rowsToRemove = []

        for i in range(Board.BoardHeight):

            n = 0
            for j in range(Board.BoardWidth):
                if not self.shapeAt(j, i) == Tetrominoe.NoShape:
                    n = n + 1

            if n == 10:
                rowsToRemove.append(i)

        rowsToRemove.reverse()


        for m in rowsToRemove:

            for k in range(m, Board.BoardHeight):
                for l in range(Board.BoardWidth):
                        self.setShapeAt(l, k, self.shapeAt(l, k + 1))

        numFullLines = numFullLines + len(rowsToRemove)

        if numFullLines > 0:

            self.numLinesRemoved = self.numLinesRemoved + numFullLines
            self.msg2Statusbar.emit(str(self.numLinesRemoved))

            self.isWaitingAfterLine = True
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.update()

    def newPiece(self):

        self.curPiece = Shape()
        self.curPiece.setRandomShape()
        self.curX = Board.BoardWidth // 2 + 1
        self.curY = Board.BoardHeight - 1 + self.curPiece.minY()

        if not self.tryMove(self.curPiece, self.curX, self.curY):

            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()
            self.isStarted = False
            self.msg2Statusbar.emit("Game over")
            self.game_over_signal.emit()

    def tryMove(self, newPiece, newX, newY):

        for i in range(4):

            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)

            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
                return False

            if self.shapeAt(x, y) != Tetrominoe.NoShape:
                return False

        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()

        return True

    def drawSquare(self, painter, x, y, shape):

        colorTable = [0xFFC0CB, 0x00CED1, 0x9370DB, 0xFF69B4,
                      0xFFD700, 0xFFA500, 0x00FF7F, 0xADD8E6]

        color = QColor(colorTable[shape])
        painter.fillRect(x + 1, y + 1, self.squareWidth() - 2,
            self.squareHeight() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.squareHeight() - 1, x, y)
        painter.drawLine(x, y, x + self.squareWidth() - 1, y)

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.squareHeight() - 1,
            x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        painter.drawLine(x + self.squareWidth() - 1,
            y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)

class RecordsWindow(QtWidgets.QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setObjectName("MainWindow")
        self.resize(360, 760)
        self.setStyleSheet("background-color: rgb(245,255,250);")
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 0, 360, 80))
        font = QtGui.QFont()
        font.setFamily("Comfortaa")
        font.setPointSize(20)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(0, 70, 360, 580))
        self.plainTextEdit.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setObjectName("plainTextEdit")

        self.btn_menu2 = QtWidgets.QPushButton(self.centralwidget)
        self.btn_menu2.setGeometry(QtCore.QRect(80, 700, 200, 50))
        font = QtGui.QFont()
        font.setFamily("Comfortaa")
        font.setPointSize(10)
        self.btn_menu2.setFont(font)
        self.btn_menu2.setStyleSheet("\nbackground-color: rgb(220, 220, 220);")
        self.btn_menu2.setObjectName("pushButton")

        self.btn_record = QtWidgets.QPushButton(self.centralwidget)
        self.btn_record.setGeometry(QtCore.QRect(80, 650, 200, 50))
        font = QtGui.QFont()
        font.setFamily("Comfortaa")
        font.setPointSize(10)
        self.btn_record.setFont(font)
        self.btn_record.setStyleSheet("\nbackground-color: rgb(220, 220, 220);")
        self.btn_record.setObjectName("pushButton2")
        self.btn_menu2.clicked.connect(self.menu)
        self.btn_record.clicked.connect(self.load_records)

        self.setCentralWidget(self.centralwidget)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def load_records(self):
        if os.path.exists("records.txt"):
            with open("records.txt", "r") as file:
                records = file.read()

            font = QtGui.QFont()
            font.setFamily("Comfortaa")
            font.setPointSize(12)
            self.plainTextEdit.setFont(font)

            option = QtGui.QTextOption(QtCore.Qt.AlignTop)  # Исправленная строка
            self.plainTextEdit.document().setDefaultTextOption(option)

            self.plainTextEdit.setPlainText(records)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Records"))
        self.label.setText(_translate("MainWindow", "Рекорды"))
        self.btn_menu2.setText(_translate("MainWindow", "Главное меню"))
        self.btn_menu2.setObjectName("btn_menu2")
        self.btn_record.setText(_translate("MainWindow", "Показать рекорды"))
        self.btn_record.setObjectName("btn_record")


    def menu(self):
        self.close()  # Закрыть окно рекордов
        self.main_window.show()  # Показать главное меню

class Tetrominoe(object):

    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7

class Shape(object):

    coordsTable = (
        ((0, 0),     (0, 0),     (0, 0),     (0, 0)),
        ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),
        ((0, -1),    (0, 0),     (1, 0),     (1, 1)),
        ((0, -1),    (0, 0),     (0, 1),     (0, 2)),
        ((-1, 0),    (0, 0),     (1, 0),     (0, 1)),
        ((0, 0),     (1, 0),     (0, 1),     (1, 1)),
        ((-1, -1),   (0, -1),    (0, 0),     (0, 1)),
        ((1, -1),    (0, -1),    (0, 0),     (0, 1))
    )

    def __init__(self):

        self.coords = [[0,0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape

        self.setShape(Tetrominoe.NoShape)


    def shape(self):
        return self.pieceShape


    def setShape(self, shape):

        table = Shape.coordsTable[shape]

        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape


    def setRandomShape(self):
        self.setShape(random.randint(1, 7))


    def x(self, index):
        return self.coords[index][0]


    def y(self, index):
        return self.coords[index][1]


    def setX(self, index, x):
        self.coords[index][0] = x


    def setY(self, index, y):
        self.coords[index][1] = y


    def minX(self):

        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])

        return m


    def maxX(self):

        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])

        return m


    def minY(self):

        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])

        return m


    def maxY(self):

        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])

        return m


    def rotateLeft(self):

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):

            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))

        return result


    def rotateRight(self):

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):

            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))

        return result