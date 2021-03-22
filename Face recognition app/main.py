import sys  # sys нужен для передачи argv в QApplication
import sqlite3
import uuid

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog

import face_recognition_functions as func
from GUI import gui


def generate_id():
    return str(uuid.uuid4().fields[-1])[:5]

def search_for_matches(face_descriptor):
    """
    Ищет совпадения лиц в базе данных по вектору.
        face_descriptor - вектор, представляющий лицо человека
    """

    # после выполнения куска кода, with as закроет соединение с базой
    with sqlite3.connect('db/database.db') as db:
        cursor = db.cursor()
        sql_select_query = """SELECT t1."name", t1."vector" FROM face_vectors t1"""
        cursor.execute(sql_select_query)
        records = cursor.fetchall()
        for rec in records:
            vector = str(rec[1])
            face_descriptor2 = tuple(float(item) for item in vector.split(' '))
            if func.calc_euclid(face_descriptor, face_descriptor2) < 0.6:
                return str(rec[0])  # Есть совпадения
    return ''  # Нет совпадений


def add_vector(face_descriptor, name):
    """
    Добавляет новую запись в БД
        face_descriptor - дескриптор лица (вектор)
        name - имя человека
    """
    # Преобразуем массив в строку для добавления в БД
    str1 = ' '.join(str(e) for e in face_descriptor)

    # ВСТАВЛЯЕМОЕ ЗНАЧЕНИЕ
    insert_face_vectors = [
        (generate_id(), name, str1)
    ]

    # После выполнения куска кода, with as закроет соединение с базой
    with sqlite3.connect('db/database.db') as db:
        cursor = db.cursor()
        # ЗАПРОС ДЛЯ ВСТАВКИ В ТАБЛИЦУ
        query = """ INSERT INTO face_vectors(id, name, vector)
                VALUES(?,?,?); """
        # ВСТАВКА В ТАБЛИЦУ
        cursor.executemany(query, insert_face_vectors)


def create_database():
    """
        Создает локальную базу данных для хранения векторов лиц
    """
    # после выполнения куска кода, with as закроет соединение с базой
    with sqlite3.connect('db/database.db') as db:
        cursor = db.cursor()

        # СОЗДАНИЕ ТАБЛИЦЫ
        query = """ CREATE TABLE IF NOT EXISTS
        face_vectors("id" INTEGER,
                    "name" TEXT,
                    "vector" TEXT UNIQUE,
                    PRIMARY KEY("id")) """
        cursor.execute(query)


class ExampleApp(QtWidgets.QMainWindow, gui.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле gui.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации  дизайна
        create_database()
        self.label.setText('')
        self.labelName.setText('')
        self.labelResult.setText('')
        self.labelInfo.setText('')
        self.labelResult.setStyleSheet('color: rgb(229, 61, 26)')
        self.labelInfo.setStyleSheet('color: rgb(229, 61, 26)')

        # Открытие изображения для верификации лица
        self.btnOpenImg.clicked.connect(self.open_img)

        # Загрузка изображения для последующего добавления в БД
        self.btnLoadImg.clicked.connect(self.load_img)

        # Попытка сохранить новую запись в БД
        self.btnSaveVector.clicked.connect(self.save_vector)

        global loading_image
        loading_image = 0

    def load_img(self):
        self.labelInfo.setStyleSheet('color: rgb(229, 61, 26)')
        global loading_image
        loading_image = QFileDialog.getOpenFileName(self, 'Выбор картинки', '/home', "Image (*.png *.jpg)")[0]
        # Функции QPixmap.scaled() возвращают масштабированные копии pixmap
        pixmap = QPixmap(loading_image).scaled(221, 161,
                                               Qt.KeepAspectRatio,
                                               Qt.SmoothTransformation)
        # Помещаем картинку в label для отображения на экране
        self.labelResult.setPixmap(pixmap)

    def save_vector(self):
        global loading_image
        if not loading_image:
            self.labelResult.setText('Загрузите изображение!')
            return
        elif self.textEditName.toPlainText() == '':
            self.labelResult.setText('Заполните поле!')
            return

        # Проверка, есть ли человек уже в БД
        face_descriptor = func.return_img_vector(loading_image)
        if face_descriptor == 0:
            self.labelInfo.setText('На изображении нет человека!')
            return
        else:
            name = search_for_matches(face_descriptor)
            if name != '':
                self.labelInfo.setText('Такой человек уже есть в базе!')
            else:
                # Добавляем новую запись в БД
                name = self.textEditName.toPlainText()
                add_vector(face_descriptor, name)
                self.labelInfo.setStyleSheet('color: rgb(32, 200, 15)')
                self.labelInfo.setText('Загружено успешно!')

    def open_img(self):
        image = QFileDialog.getOpenFileName(self, 'Выбор картинки', '/home', "Image (*.png *.jpg *.jpeg)")[0]
        self.labelName.setText('')
        self.label.setText('')
        if image:
            # Функции QPixmap.scaled() возвращают масштабированные копии pixmap
            pixmap = QPixmap(image).scaled(291, 171,
                                           Qt.KeepAspectRatio,
                                           Qt.SmoothTransformation)
            face_descriptor = func.return_img_vector(image)
            if face_descriptor == 0:
                self.label.setText('На изображении нет человека!')
                self.label.setStyleSheet('color: rgb(229, 61, 26)')
                return
            else:
                name = search_for_matches(face_descriptor)
                if name != '':
                    # Помещаем картинку в label для отображения на экране
                    self.label.setPixmap(pixmap)
                    self.labelName.setText(name)
                else:
                    self.label.setText('Такого человека нет в базе!')
                    self.label.setStyleSheet('color: rgb(229, 61, 26)')


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
