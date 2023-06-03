import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDesktopWidget, QMessageBox
from engine import Board,RecordsWindow

class Ui_MainWindow(QMainWindow):
    def setupUi(self, MainWindow):
        self.main_window = MainWindow 
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(360, 760)
        self.setStyleSheet("background-color: rgb(245,255,250);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.rules_dialog = None  # Переменная-член для окна правил игры

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 0, 360, 111))
        font = QtGui.QFont()
        font.setFamily("Comfortaa")
        font.setPointSize(20)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setStyleSheet("background-color: rgb(173, 216, 230);")
        self.label.setObjectName("label")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.input_label = QtWidgets.QLabel(self.centralwidget)
        self.input_label.setGeometry(QtCore.QRect(80, 140, 200, 30))
        font = QtGui.QFont()
        font.setFamily("Comfortaa")
        font.setPointSize(10)
        self.input_label.setFont(font)
        self.input_label.setAlignment(QtCore.Qt.AlignCenter)
        self.input_label.setText("Введите ник:")
        
        self.textEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(80, 180, 200, 30))
        self.setStyleSheet("background-color: rgb(245,255,250);")
        self.textEdit.setObjectName("textEdit")

        self.btn_close = QtWidgets.QPushButton(self.centralwidget)
        self.btn_close.setGeometry(QtCore.QRect(80, 550, 200, 90))
        font = QtGui.QFont()
        font.setFamily("Comfortaa")
        font.setPointSize(10)
        self.btn_close.setFont(font)
        self.btn_close.setObjectName("btn_close")

        self.btn_new = QtWidgets.QPushButton(self.centralwidget)
        self.btn_new.setGeometry(QtCore.QRect(80, 250, 200, 90))
        font = QtGui.QFont()
        font.setFamily("Comfortaa")
        font.setPointSize(10)
        self.btn_new.setFont(font)
        self.btn_new.setObjectName("btn_new")

        self.btn_record = QtWidgets.QPushButton(self.centralwidget)
        self.btn_record.setGeometry(QtCore.QRect(80, 350, 200, 90))
        font = QtGui.QFont()
        font.setFamily("Comfortaa")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.btn_record.setFont(font)
        self.btn_record.setObjectName("btn_record")

        self.btn_rules = QtWidgets.QPushButton(self.centralwidget)
        self.btn_rules.setGeometry(QtCore.QRect(80, 450, 200, 90))
        font = QtGui.QFont()
        font.setFamily("Comfortaa")
        font.setPointSize(10)
        self.btn_rules.setFont(font)
        self.btn_rules.setObjectName("btn_rules")
        self.btn_rules.setText("Правила")
        self.btn_rules.clicked.connect(self.pravila_game)

        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.show()

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.add_functions()

    def pravila_game(self):
        if not self.rules_dialog:  # Проверяем, существует ли уже окно правил игры
            self.rules_dialog = QMessageBox(self.main_window)
            self.rules_dialog.setWindowTitle("Правила игры")
            self.rules_dialog.setText("Цель игры - удалить как можно больше линий и набрать очки\n\n"
                                "1. Двигать фигуры вправо и влево с помощью стрелочек влево и вправо\n"
                                "2. Фигуры можно переворачивать стрелочкой вверх\n"
                                "3. Фигуры можно ускорять стрелочкой вниз\n"
                                "4. Вы можете заменить фигуру нажав кнопку 'shift'.\n"
                                "5. Вы можете поставить игру на паузу буквой 'p' и при повторном нажатии игра продолжится\n"
                                "6. Вы можете нажать кнопку 'Escape' и появится окно с выбором дальнейшего действия\n"
                                "7. Игра закончится когда фигуры достигнут верхушки окна.\n"
                                "8. Ваш рекорд отобразится в главном меню.\n\n"
                                "Удачи!")
            self.rules_dialog.setStandardButtons(QMessageBox.Ok)
        self.rules_dialog.exec_()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Tetris"))
        self.label.setText(_translate("MainWindow", "Тетрис"))
        self.input_label.setText(_translate("MainWindow", "Введите ник"))
        self.btn_close.setText(_translate("MainWindow", "Выход из игры"))
        self.btn_new.setText(_translate("MainWindow", "Новая игра"))
        self.btn_record.setText(_translate("MainWindow", "Рекорды"))

    def add_functions(self):
        self.btn_close.clicked.connect(lambda: self.close_game())
        self.btn_new.clicked.connect(lambda: self.start_game())
        self.btn_record.clicked.connect(lambda: self.start_records())
        self.btn_new.clicked.connect(lambda: self.save_records())

    def close_game(self):
        reply = QMessageBox.question(
        self.main_window, "Выход", "Вы уверены, что хотите выйти из игры?", QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.main_window.close()
        else:
            self.main_window.show()
        
    def start_records(self):
        self.main_window.hide()
        self.record_window = RecordsWindow(self.main_window)
        self.record_window.show()

    def save_records(self):
        text = self.textEdit.text()
        with open("records.txt", "a") as file:
            file.write(text + ":" + ' ')

    def start_game(self):
        self.main_window.hide()
        self.tetris = Tetris()
        self.tetris.main_window = self.main_window
        self.tetris.show()

    def write_number(self, number):
        if self.label.text() == "0": 
            self.label.setText(number)
        else:
            self.label.setText(self.label.text()+number)

class Tetris(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.tboard = Board(self)
        self.main_window = MainWindow
        self.setCentralWidget(self.tboard)
        self.resize(360, 760)
        self.setStyleSheet("background-color: rgb(245,255,250);")

        self.statusbar = self.statusBar()
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)
        self.tboard.game_over_signal.connect(self.game_over)
        self.tboard.keyPressevent.connect(self.pause_esc)

        self.tboard.start()
        self.center()
        self.setWindowTitle('Tetris')

        self.show()

    def end_game(self, score):
        with open("records.txt", "a") as file:
            print('sdv')
            file.write(str(score) + "\n")

    def game_over(self):
        game_over = QMessageBox()
        game_over.setWindowTitle("Конец игры")
        game_over.setText("Игра окончена. Выберите дальнейшее действие")
        game_over.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        game_over.setDefaultButton(QMessageBox.Yes)

        new_game_button = game_over.button(QMessageBox.Yes)
        new_game_button.setText("Новая игра")

        main_menu_button = game_over.button(QMessageBox.No)
        main_menu_button.setText("Главное меню")

        reply = game_over.exec()

        if reply == QMessageBox.Yes:
            self.start_game()
        elif reply == QMessageBox.No:
            self.menu()

    def pause_esc(self):
        escape = QMessageBox()
        escape.setWindowTitle("Игра приостановлена")
        escape.setText("Выберите дальнейшее действие")
        escape.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Reset)

        new_button = escape.button(QMessageBox.Yes)
        new_button.setText("Новая игра")

        main_button = escape.button(QMessageBox.No)
        main_button.setText("Главное меню")

        resume_button = escape.button(QMessageBox.Reset)
        resume_button.setText("Продолжить")

        escape.exec()

        clicked_button = escape.clickedButton()

        if clicked_button == new_button:
            self.start_game()
        elif clicked_button == main_button:
            self.menu()
        elif clicked_button == resume_button:
            self.tboard.resume()

    def menu(self):
        self.tboard.close()
        self.close()  # Закрыть окно игры
        self.main_window.show()  # Показать главное меню
        self.end_game(self.tboard.numLinesRemoved)

    def start_game(self):
        self.tboard.close()
        self.close()
        self.tetris = Tetris()
        self.tetris.show()

    def resizeEvent(self, event):
        self.center()
        return super().resizeEvent(event)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())