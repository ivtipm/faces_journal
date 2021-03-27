import sys  # sys нужен для передачи argv в QApplication
import cv2
import imutils

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog

from GUI import gui
import face_recognition_module as FR
import database_module as db


class FaceApp(QtWidgets.QMainWindow, gui.Ui_MainWindow):

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле gui.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации  дизайна
        db.create_database()  # создаем базу либо открываем существующую
        self.reset_left_area()
        self.reset_right_area()
        self.label.setStyleSheet('color: rgb(229, 61, 26)')

        # Открытие изображения для верификации лица
        self.btnOpenImg.clicked.connect(self.open_img)

        # Загрузка изображения для последующего добавления в БД
        self.btnLoadImg.clicked.connect(self.load_img)

        # Попытка сохранить новую запись в БД
        self.btnSaveVector.clicked.connect(self.save_vector)

        # Открытие веб-камеры для верификации лица
        self.btnOpenCam.clicked.connect(self.open_cam)

        global loading_image
        loading_image = 0

    def reset_left_area(self):
        self.label.clear()
        self.labelName.setText('')
        self.labelEuclid.setText('')

    def reset_right_area(self):
        self.labelResult.clear()
        self.labelInfo.setText('')
        self.textEditName.setText('')

    def open_cam(self):
        """Открытие камеры для "заморозки" изображения"""
        self.reset_left_area()
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # video capture source camera (Here webcam of laptop)
        if cap is None or not cap.isOpened():
            self.label.setText('Веб-камера не обнаружена!')
            return
        color_yellow = (0, 255, 255)
        while True:
            (grabbed, frame) = cap.read()
            frame = imutils.resize(frame, width=400)
            cv2.putText(frame, """Press Enter to take a screenshot""",
                        (10, 10), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color_yellow, 1)
            cv2.imshow('Веб-камера', frame)
            # Чтобы "заморозить" изображение нужно нажать на Enter
            if cv2.waitKey(1) & 0xFF == 13:
                path = 'capture.png'
                buf = cv2.imread(path)  # копируем в буфер старое изображение
                cv2.imwrite(path, frame)
                cv2.destroyAllWindows()
                break

            # frame[0,:,:], frame[2,:,:] = frame[2,:,:], frame[0,:,:]
            # Убрать подвисание через таймер
            # Сделать рисование рамки в реальном времени на лице, чуть ниже писать имя человека
            # Сделать log во время выполнения программы (история узнавания)
            # План презентации в Slack
        cap.release()

        # Если человека нет в БД, то предложим ему добавить себя
        if self.check_user(path) == 0:
            # Функции QPixmap.scaled() возвращают масштабированные копии pixmap
            pixmap = QPixmap(path).scaled(221, 161,
                                          Qt.KeepAspectRatio,
                                          Qt.SmoothTransformation)
            # Помещаем картинку в label для отображения на экране
            self.labelResult.setPixmap(pixmap)
            global loading_image
            loading_image = path
        else:
            cv2.imwrite(path, buf)

    def open_img(self):
        """Открытие изображения с компьютера"""
        self.reset_left_area()
        path = QFileDialog.getOpenFileName(self, 'Выбор картинки', '/home', "Image (*.png *.jpg *.jpeg)")[0]
        self.check_user(path)

    def check_user(self, path):
        """Проверка на наличие человека в БД"""
        if path:
            # Функции QPixmap.scaled() возвращают масштабированные копии pixmap
            pixmap = QPixmap(path).scaled(291, 171,
                                          Qt.KeepAspectRatio,
                                          Qt.SmoothTransformation)

            FR.obj_FR.set_path(path)
            fd_array = FR.obj_FR.return_img_vector()
            if not fd_array:
                self.label.setText('На изображении нет человека!')
                return
            for face_descriptor in fd_array:
                name, value = FR.search_for_matches(face_descriptor)
                if name != '':
                    # Помещаем картинку в label для отображения на экране
                    self.label.setPixmap(pixmap)
                    self.labelName.setText(name)
                    self.labelEuclid.setText(str(value))
                    return
            self.label.setText('Такого человека нет в базе!')
            return 0

    def load_img(self):
        """Открытие изображения для загрузки в БД"""
        self.reset_right_area()
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
        """Сохранение вектора лица в БД по заданному изображению"""
        self.labelInfo.setStyleSheet('color: rgb(229, 61, 26)')
        global loading_image
        if not loading_image:
            self.labelInfo.setText('Загрузите изображение!')
            return
        elif self.textEditName.toPlainText() == '':
            self.labelInfo.setText('Введите свое имя!')
            return
        FR.obj_FR.set_path(loading_image)

        # Проверка, есть ли человек уже в БД
        fd_array = FR.obj_FR.return_img_vector()
        if not fd_array:
            self.labelInfo.setText('На изображении нет человека!')
            return
        for face_descriptor in fd_array:
            name, value = FR.search_for_matches(face_descriptor)
            if name != '':
                self.labelInfo.setText('Такой человек уже есть в базе!')
            else:
                # Добавляем новую запись в БД
                name = self.textEditName.toPlainText()
                db.add_vector(face_descriptor, name)
                self.reset_right_area()
                self.labelInfo.setStyleSheet('color: rgb(32, 200, 15)')
                self.labelInfo.setText('Загружено успешно!')
                loading_image = 0


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = FaceApp()  # Создаём объект класса FaceApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
