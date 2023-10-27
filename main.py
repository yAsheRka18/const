import os
from math import log, fabs, sqrt, exp

import pyqtgraph as pg
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, qApp
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from tabulate import tabulate

pg.mkQApp()

# сглаживание для графиков
pg.setConfigOptions(antialias=True)

# Нахождения файла с интерфейсом
path = os.path.dirname(os.path.abspath(__file__))
uiFile = os.path.join(path, 'interface.ui')

# "Подгружает" интерфпейс в код, чтобы потом использовать
WindowTemplate, TemplateBaseClass = pg.Qt.loadUiType(uiFile)


# Функция для боллее удобного доступа к ячейке
def getCell(table, n, m):
    return (float(table.item(n, m).text()))


# Функция для удобного показа сообщений
def showErrorMessage(text, title):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(text)
    msg.setWindowTitle(title)
    msg.exec_()


# Делегат таблицы(ячейки таблицы после объявления делегата становятся объектами QDoubleSpinBox)

class MyDelegate(QtGui.QItemDelegate):

    def createEditor(self, parent, option, index):
        return QtGui.QDoubleSpinBox(parent, maximum=1000, decimals=3, buttonSymbols=QtGui.QSpinBox.NoButtons)

class MyDelegateForChangeItem(QtWidgets.QItemDelegate):
    def creatEditor(selfself, parent, option, index):
        editor = QtWidgets.QDoubleSpinBox(parent)
        editor.setDecimals(3)
        editor.Maximum(1000)
        editor.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        return editor


# Класс главного окна
class MainWindow(TemplateBaseClass):
    # Определение инициализации формы
    def __init__(self):
        TemplateBaseClass.__init__(self)
        self.setWindowTitle('Расчет константы скорости химической реакции 5A = 3B + 3C + 2D')

        # Create the main window
        # Добавил ui  к  mian window
        self.ui = WindowTemplate()
        self.ui.setupUi(self)

        #Добавил делегат к мэин виндов
        delegate = MyDelegate()
        delegateForManualInput = MyDelegateForChangeItem()
        self.ui.tableWidget.setItemDelegate(delegate)


        self.ui.plot.setBackground('w')
        self.ui.plot.addLegend()
        self.ui.plot.setLabel('bottom', 'Время (с)')
        self.ui.plot.setLabel('left', 'Концетрация(C), моль/с', labelTextSize='50pt')
        self.ui.plot.setTitle("Эксперементальные точки и аппроксимационная кривая")
        self.ui.plot.setEnabled(False)

        # Маленькая таблица
        # Установка начальных значений
        # 2 столбца, 8 строок
        self.ui.tableWidget.setColumnCount(2)
        self.ui.tableWidget.setRowCount(8)

        self.ui.tableWidget.setHorizontalHeaderLabels(["Ca, моль/л", "t, с"])

        self.ui.tableWidget.setItem(0, 0, QTableWidgetItem("2.2"))
        self.ui.tableWidget.setItem(1, 0, QTableWidgetItem("1.7"))
        self.ui.tableWidget.setItem(2, 0, QTableWidgetItem("1.5"))
        self.ui.tableWidget.setItem(3, 0, QTableWidgetItem("1.2"))
        self.ui.tableWidget.setItem(4, 0, QTableWidgetItem("1.1"))
        self.ui.tableWidget.setItem(5, 0, QTableWidgetItem("1.0"))
        self.ui.tableWidget.setItem(6, 0, QTableWidgetItem("0.9"))
        self.ui.tableWidget.setItem(7, 0, QTableWidgetItem("0.8"))

        self.ui.tableWidget.setItem(0, 1, QTableWidgetItem("0"))
        self.ui.tableWidget.setItem(1, 1, QTableWidgetItem("1.7"))
        self.ui.tableWidget.setItem(2, 1, QTableWidgetItem("2.5"))
        self.ui.tableWidget.setItem(3, 1, QTableWidgetItem("3.4"))
        self.ui.tableWidget.setItem(4, 1, QTableWidgetItem("4"))
        self.ui.tableWidget.setItem(5, 1, QTableWidgetItem("4.6"))
        self.ui.tableWidget.setItem(6, 1, QTableWidgetItem("5.2"))
        self.ui.tableWidget.setItem(7, 1, QTableWidgetItem("6"))

        # утанавливает делегат к 1ой таблице
        self.ui.tableWidget.setItemDelegate(delegateForManualInput)

        # 2ая таблица
        # 5 столбцов
        self.ui.tableWidget_2.setColumnCount(5)

        self.ui.tableWidget_2.setHorizontalHeaderLabels(["t, с", "Ca расч., моль/л", "Cb, моль/л", "Cc, моль/л", "Cd, моль/л"])

        for i in range(self.ui.tableWidget_2.columnCount()):
            self.ui.tableWidget_2.horizontalHeader().setResizeMode(i, QtGui.QHeaderView.Stretch)

        for i in range(self.ui.tableWidget.columnCount()):
            self.ui.tableWidget.horizontalHeader().setResizeMode(i, QtGui.QHeaderView.Stretch)

        # Подключение функций к элементам интерфейса
        self.ui.pushButton.clicked.connect(self.plot)
        self.ui.spinBox_2.valueChanged.connect(self.changeTableSize)
        self.ui.action.triggered.connect(self.save)
        self.ui.action_2.triggered.connect(qApp.quit)
        self.ui.action_3.triggered.connect(self.faq)

        self.show()

        self.n = 0
        self.k = 0
        self.d = 0
        self.r = 0
        self.isDataNormal = False

    # функция сохранения результата
    def save(self):
        if self.isDataNormal:
            text = "Порядок реакции: " + str(round(self.n, 3)) + "\nКонстанта скорости: " + str(
                round(self.k, 3)) + " 1/с\nДисперсия: " + str(round(self.d, 3)) + " (моль/л)^2\nКорреляция: " + str(
                round(self.r, 3)) + "\n\nТаблица вычисленных значений\n"
            # Сохранение большой таблицы в values
            values = [["t, с", "Ca расч., моль/л", "Cb, моль/л", "Cc, моль/л"]]
            for i in range(self.ui.tableWidget_2.rowCount()):
                values.append([])
                for j in range(self.ui.tableWidget_2.columnCount()):
                    values[i + 1].append(str(getCell(self.ui.tableWidget_2, i, j)))

            text += tabulate(values)

            fileName = QtGui.QFileDialog.getSaveFileName(self, "Сохранить результаты", "Результаты вычислений",
                                                         "Текстовый документ (*.txt)")[0]
            print(fileName)
            with open(fileName, 'w') as fp:
                fp.write(text)
        else:
            showErrorMessage("Сначала должны быть произведены расчеты.", "Ошибка сохранения файла")

    # функция вызова справки
    def faq(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("""
Данная программа расчитывает порядок и консанту скорости химической реакции.
Для начала работы введите данные об исходных веществах: начальныее концетрации Cb, Cc и Cd, заполните таблицу с измененим концетрации Ca в течении времени.
После ввода начальных данных нажмите кнопку "Провести расчёты" и вы получите результаты.
        """)
        msg.setWindowTitle("Справка")
        msg.exec_()

    # функция изменяющая размер таблицы при изменении значения количетсва точек
    def changeTableSize(self):
        s = self.ui.spinBox_2.value()
        self.ui.tableWidget.setRowCount(s)

    # функция очищающая таблицы, график
    def dataIsBad(self):
        while self.ui.tableWidget_2.rowCount() > 0:
            self.ui.tableWidget_2.removeRow(0)
        self.ui.plot.plot(clear=True)
        self.isDataNormal = False
        self.ui.plot.setEnabled(False)  # выключение графика

    # функция вычисления
    def plot(self):
        try:
            self.d = 0
            spinboxvalue = self.ui.spinBox_2.value() #
            print("spinboxvalue - ",spinboxvalue)
            self.ui.tableWidget_2.setRowCount(spinboxvalue)
            s1 = spinboxvalue - 1
            print("s1 - ", s1) #del
            reg_down = reg_up = 0
            s2 = s3 = s4 = s5 = s6 = 0
            x = []
            y = []

            ca = getCell(self.ui.tableWidget, 0, 0)
            cb = (self.ui.doubleSpinBox.value())
            cc = (self.ui.doubleSpinBox_2.value())
            cd = (self.ui.doubleSpinBox_3.value())

            if ca < 0 or cb < 0 or cc < 0 or cd < 0:
                self.dataIsBad()
                showErrorMessage("Начальные концентрации компонентов должны быть больше 0.", "Введены неверные данные")
                return
            for i in range(spinboxvalue - 1):
                if getCell(self.ui.tableWidget, i, 0) > getCell(self.ui.tableWidget, i + 1, 0):
                    reg_down += 1
                else:
                    reg_up += 1
                if getCell(self.ui.tableWidget, i, 0) == getCell(self.ui.tableWidget, i + 1, 0):
                    self.dataIsBad()
                    showErrorMessage("Концетрации в соседних точках должна быть различна.", "Введены неверные данные")
                    return
                if getCell(self.ui.tableWidget, i, 1) >= getCell(self.ui.tableWidget, i + 1, 1):
                    self.dataIsBad()
                    showErrorMessage("Нарушение последовательности ввода времени.", "Введены неверные данные")
                    return
                if getCell(self.ui.tableWidget, i, 1) < 0 or getCell(self.ui.tableWidget, i, 0) < 0:
                    self.dataIsBad()
                    showErrorMessage("Время и концентрация не могут быть отрицательными.", "Введены неверные данные")
                    return

            for i in range(spinboxvalue - 1):
                y.append(log((fabs(getCell(self.ui.tableWidget, i + 1, 0) - (getCell(self.ui.tableWidget, i, 0)))) / (
                        getCell(self.ui.tableWidget, i + 1, 1) - getCell(self.ui.tableWidget, i, 1))))
                x.append(log(getCell(self.ui.tableWidget, i, 0)))
                print("s2Clear - ", s2)  # del
                s2 += x[i]
                print("s2 - ", s2) #del
                s3 += y[i]
                print("s3 - ", s3)  # del
                s4 += x[i] * x[i]
                print("s4 - ", s4)  # del
                s5 += x[i] * y[i]
                s6 += y[i] * y[i]
            self.k = exp((s3 * s4 - s2 * s5) / (s1 * s4 - s2 * s2))
            self.n = (s1 * s5 - s2 * s3) / (s1 * s4 - s2 * s2) #вот наша экспериментально определяемая степень, вместо стехиометрических коэффициентов
            self.r = (s1 * s5 - s2 * s3) / sqrt((s1 * s4 - s2 * s2) * (s1 * s6 - s3 * s3))
            series1 = [[], []]
            series2 = [[], []]
            series3 = [[], []]
            series4 = [[], []]
            series5 = [[], []]

            for i in range(spinboxvalue):
                series1[0].append(getCell(self.ui.tableWidget, i, 1))
                series1[1].append(getCell(self.ui.tableWidget, i, 0))
                self.ui.tableWidget_2.setItem(1, 1, QTableWidgetItem(str(getCell(self.ui.tableWidget, 1, 0))))
                self.ui.tableWidget_2.setItem(i, 0, QTableWidgetItem(str(getCell(self.ui.tableWidget, i, 1))))

                if ca < 0:
                    self.dataIsBad()
                    showErrorMessage("Модель невозможно описать линейной регрессией", "Ошибка")
                    return
                if i == 0:
                    series2[0].append(getCell(self.ui.tableWidget, i, 1))
                    series2[1].append(ca)
                    self.ui.tableWidget_2.setItem(i, 1, QTableWidgetItem(str(round(ca, 2))))

                    series3[0].append(getCell(self.ui.tableWidget, i, 1))
                    series3[1].append(cb)
                    self.ui.tableWidget_2.setItem(i, 2, QTableWidgetItem(str(round(cb, 2))))

                    series4[0].append(getCell(self.ui.tableWidget, i, 1))
                    series4[1].append(cc)
                    self.ui.tableWidget_2.setItem(i, 3, QTableWidgetItem(str(round(cc, 2))))

                    series5[0].append(getCell(self.ui.tableWidget, i, 1))
                    series5[1].append(cd)
                    self.ui.tableWidget_2.setItem(i, 4, QTableWidgetItem(str(round(cd, 2))))
                else:
                    t = getCell(self.ui.tableWidget, i, 1) - getCell(self.ui.tableWidget, i - 1, 1)
                    cb = cb + self.k * (ca ** self.n) * t * 3
                    cc = cc + self.k * (ca ** self.n) * t * 3
                    cd = cd + self.k * (ca ** self.n) * t * 2

                    series3[0].append(getCell(self.ui.tableWidget, i, 1))
                    series3[1].append(cb)
                    self.ui.tableWidget_2.setItem(i, 2, QTableWidgetItem(str(round(cb, 2))))

                    series4[0].append(getCell(self.ui.tableWidget, i, 1))
                    series4[1].append(cc)
                    self.ui.tableWidget_2.setItem(i, 3, QTableWidgetItem(str(round(cc, 2))))

                    series5[0].append(getCell(self.ui.tableWidget, i, 1))
                    series5[1].append(cd)
                    self.ui.tableWidget_2.setItem(i, 4, QTableWidgetItem(str(round(cd, 2))))

                    if reg_down > reg_up:
                        ca = ca - self.k * (ca ** self.n) * t
                        print(self.n)
                    else:
                        ca = ca + self.k * (ca ** self.n) * t
                        print("self n_2 - ", self.n)
                    series2[0].append(getCell(self.ui.tableWidget, i, 1))
                    series2[1].append(ca)
                    self.ui.tableWidget_2.setItem(i, 1, QTableWidgetItem(str(round(ca, 2))))
                self.d += (getCell(self.ui.tableWidget, i, 0) - ca) ** 2

            allCValues = []
            for i in range(spinboxvalue):
                for j in range(1, 4):
                    allCValues.append(getCell(self.ui.tableWidget_2, i, j))
            xmax = getCell(self.ui.tableWidget_2, spinboxvalue - 1, 0)
            ymax = max(allCValues)

            # установка ограничений для графика
            self.ui.plot.setLimits(xMin=-1, xMax=xmax * 1.2,
                                   minXRange=0.1, maxXRange=xmax * 1.2,
                                   yMin=0, yMax=ymax * 1.2,
                                   minYRange=0.1, maxYRange=ymax * 1.2)

            # отрисовка линий
            self.ui.plot.plot(series2[0], series2[1], clear=True, pen='#000DFF', symbolPen='#000DFF', name='Ca расч')
            self.ui.plot.plot(series1[0], series1[1], pen=(0, 0, 0, 0), symbolBrush="r", name='Ca эксп')
            self.ui.plot.plot(series3[0], series3[1], pen='#FF0000', symbolPen='#FF0000', name='Cb расч')
            self.ui.plot.plot(series4[0], series4[1], pen='#7FFF00', symbolPen='#7FFF00', name='Cс расч')
            self.ui.plot.plot(series5[0], series5[1], pen='#4B0082', symbolPen='#4B0082', name='Cd расч')
            # вывод сообщения
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Порядок реакции: " + str(round(self.n, 3)) + "\nКонстанта скорости: " + str(
                round(self.k, 3)) + " 1/с\nДисперсия: " + str(round(self.d, 3)) + " (моль/л)^2\nКорреляция: " + str(
                round(self.r, 3)))
            msg.setWindowTitle("Результаты расчёта")
            msg.exec_()
            self.isDataNormal = True
            self.ui.plot.setEnabled(True)
        except:
            showErrorMessage("Произошла непредвиденная ошибка, попробуйте изменить данные", "Ошибка")


win = MainWindow()


if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


