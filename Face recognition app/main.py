import os
import sys  # sys нужен для передачи argv в QApplication

import cv2
import imutils
import transliterate
import datetime

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer, QLocale, QTranslator
from PyQt5.QtGui import QPixmap, QImage, QTextCursor
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from GUI import gui
import face_recognition_module as FR
import database_module as db

I18N_QT_PATH = '/usr/share/qt/translations/'


def add_to_unknown(path_without_border, face):
    frame_without_borders = cv2.imread(path_without_border)
    cropped = frame_without_borders[face.top() - 30:face.bottom() + 30, face.left() - 30:face.right() + 30]
    cv2.imwrite('unknown faces/unknown' + str(len(os.listdir('./unknown faces')) + 1) + '.png', cropped)


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
        self.fps = 24
        self.timer = QTimer()
        self.timer_save_history = QTimer()
        self.timer_save_history.timeout.connect(self.save_history_success)
        self.flag = False
        self.btnCloseCam.setVisible(False)
        self.btnTakeScreenshot.setEnabled(False)
        self.labelSaveHistorySuccess.setVisible(False)
        self.label.setAlignment(Qt.AlignCenter)
        self.btnShowSmall.setVisible(False)

        # Открытие изображения для верификации лица
        self.btnOpenImg.clicked.connect(self.open_img)

        # Загрузка изображения для последующего добавления в БД
        self.btnLoadImg.clicked.connect(self.load_img)

        # Попытка сохранить новую запись в БД
        self.btnSaveVector.clicked.connect(self.save_vector)

        # Открытие веб-камеры для верификации лица
        self.btnOpenCam.clicked.connect(self.open_cam)

        # Закрытие веб-камеры
        self.btnCloseCam.clicked.connect(self.close_cam)

        # "Заморозить" изображение
        self.btnTakeScreenshot.clicked.connect(self.take_screenshot)

        # Сохранить историю посещений в файл
        self.btnSaveHistory.clicked.connect(self.save_history)

        # Очистить историю посещений
        self.btnDeleteHistory.clicked.connect(self.delete_history)

        # Открывает область регистрации лица
        self.btnShowMore.clicked.connect(self.show_more)

        # Закрывает область регистрации лица
        self.btnShowSmall.clicked.connect(self.show_small)

        self.loading_image = 0

    def reset_left_area(self):
        self.label.clear()
        self.labelName.setText('')
        self.labelEuclid.setText('')

    def reset_right_area(self):
        self.labelResult.clear()
        self.labelInfo.setText('')
        self.textEditName.setText('')

    def set_fps(self, fps):
        self.fps = fps

    def open_cam(self):
        """Открытие камеры для "заморозки" изображения"""
        self.btnOpenCam.setVisible(False)
        self.btnCloseCam.setVisible(True)
        self.btnTakeScreenshot.setEnabled(True)
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # video capture source camera (Here webcam of laptop)
        self.reset_left_area()
        if self.cap is None or not self.cap.isOpened():
            self.label.setText('Веб-камера не обнаружена!')
            return
        self.timer.timeout.connect(self.next_frame_slot)
        self.timer.start(1000. / self.fps)

    def close_cam(self):
        self.timer.stop()
        self.cap.release()
        self.btnOpenCam.setVisible(True)
        self.btnCloseCam.setVisible(False)
        self.btnTakeScreenshot.setEnabled(False)
        self.reset_left_area()

    def next_frame_slot(self):
        ret, frame = self.cap.read()
        # Рисуем на фрейме прямугольники в местах, где обаружены лица
        face_rects = FR.obj_FR.return_faces(frame)
        path_without_border = 'screenshots/buffer.png'
        # p1 = threading.Thread(target=self.check_user, args=(path_without_border,))
        # if not p1.is_alive():
        # p1.start()
        cv2.imwrite(path_without_border, frame)
        for face in face_rects:
            frame = cv2.rectangle(frame, (face.left(), face.top()),
                                  (face.right(), face.bottom()), (0, 200, 0), 2)
        path = 'screenshots/capture.png'
        cv2.imwrite(path, frame)
        # p1.join()
        self.check_user(path_without_border)

        frame = imutils.resize(frame, width=480)
        if self.flag:
            cv2.imwrite(path, frame)
            self.take_screenshot()
            # Если человека нет в БД, то предложим ему добавить себя
            if self.check_user(path) == 0:
                # Функции QPixmap.scaled() возвращают масштабированные копии pixmap
                pixmap = QPixmap(path).scaled(491, 351,
                                              Qt.KeepAspectRatio,
                                              Qt.SmoothTransformation)
                # Помещаем картинку в label для отображения на экране
                self.labelResult.setPixmap(pixmap)
                self.loading_image = path
                self.close_cam()
            else:
                return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.label.setPixmap(pix)

    def take_screenshot(self):
        if not self.flag:
            self.flag = True
        else:
            self.flag = False

    def show_more(self):
        self.setMinimumWidth(1360)
        self.setMaximumWidth(1360)
        self.setFixedWidth(1360)
        self.btnShowMore.setVisible(False)
        self.btnShowSmall.setVisible(True)
        self.progressBar.setFixedWidth(1360)

    def show_small(self):
        self.setMinimumWidth(849)
        self.setMaximumWidth(849)
        self.setFixedWidth(849)
        self.btnShowSmall.setVisible(False)
        self.btnShowMore.setVisible(True)
        self.progressBar.setFixedWidth(849)

    def open_img(self):
        """Открытие изображения с компьютера"""
        self.reset_left_area()
        path = QFileDialog.getOpenFileName(self, 'Выбор картинки', '/home', "Image (*.png *.jpg *.jpeg)")[0]
        if path != '':
            self.label.setText('Подождите, идёт распознавание...')
        self.check_user(path)

    def check_user(self, path):
        """Проверка на наличие человека в БД"""
        self.progressBar.setValue(0)
        # Задаем настройки текста
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        fontColor = (0, 200, 0)
        lineType = 2
        if path:
            # задаем путь к изображению
            FR.obj_FR.set_path(path)
            # получаем массив дескрипторов лиц
            fd_array = FR.obj_FR.return_img_vector()
            if not fd_array:
                self.label.setText('На изображении нет людей!')
                return
            count = 0
            isFound = False
            self.progressBar.setMaximum(len(fd_array))
            frame = cv2.imread(path)
            path_without_border = 'screenshots/buffer.png'
            cv2.imwrite(path_without_border, frame)
            # Рисуем на фрейме прямугольники в местах, где обаружены лица
            for face in FR.obj_FR.face_rects:
                frame = cv2.rectangle(frame, (face.left(), face.top()),
                                      (face.right(), face.bottom()), (0, 200, 0), 2)
            for face_descriptor in fd_array:
                name, value = FR.search_for_matches(face_descriptor)
                if name != '':
                    isFound = True  # распознан хотя бы один человек
                    trans_name = transliterate.translit(name, reversed=True)
                    bottomLeftCornerOfText = (FR.obj_FR.face_rects[count].left(),
                                              FR.obj_FR.face_rects[count].bottom() + 30)
                    frame = cv2.putText(frame, trans_name, bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
                    cv2.imwrite('screenshots/cv2write.png', frame)
                    # Функции QPixmap.scaled() возвращают масштабированные копии pixmap
                    pixmap = QPixmap('screenshots/cv2write.png').scaled(491, 351,
                                                                        Qt.KeepAspectRatio,
                                                                        Qt.SmoothTransformation)
                    # Помещаем картинку в label для отображения на экране
                    self.label.setPixmap(pixmap)
                    self.set_info_about_user(name, value)
                    self.add_to_history(name)
                else:
                    # Добавляем изображения нераспознанных людей в папку на диске
                    add_to_unknown(path_without_border, FR.obj_FR.face_rects[count])
                count += 1
                self.progressBar.setValue(count)
                if count == len(fd_array) and isFound:
                    return
            self.label.setText('Совпадений не обнаружено!')
            return 0

    def save_history_success(self):
        self.timer_save_history.stop()
        self.labelSaveHistorySuccess.setVisible(False)
        self.btnSaveHistory.setVisible(True)

    def save_history(self):
        self.timer_save_history.start(3000)
        self.labelSaveHistorySuccess.setVisible(True)
        self.btnSaveHistory.setVisible(False)
        now = datetime.datetime.now()
        f = open('history/' + now.strftime("%d-%m-%Y %H-%M") + '.txt', 'w')
        f.write(self.plainTextEdit.toPlainText())
        f.close()

    def delete_history(self):
        answer = QMessageBox.question(
            self, 'Очистка истории', 'Вы уверены, что хотите очистить историю?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer == QMessageBox.Yes:
            self.plainTextEdit.setPlainText('Все нераспознанные лица хранятся в папке unknown faces!\n')

    def set_info_about_user(self, name, value):
        if self.labelName.text().find(name) == -1:
            if name != '' and self.labelName.text() == '':
                self.labelName.setText(self.labelName.text() + name)
            else:
                self.labelName.setText(self.labelName.text() + ' & ' + name)

            if str(value) != '' and self.labelEuclid.text() == '':
                self.labelEuclid.setText(self.labelEuclid.text() + str(value))
            else:
                self.labelEuclid.setText(self.labelEuclid.text() + ' & ' + str(value))

    def add_to_history(self, name):
        self.plainTextEdit.moveCursor(QTextCursor.End)
        strings = self.plainTextEdit.toPlainText().split('\n')
        now = datetime.datetime.now()
        if strings[1] == '':
            self.plainTextEdit.moveCursor(QTextCursor.End)
            self.plainTextEdit.insertPlainText('[' + now.strftime("%H:%M") + ']: ' + name + '\n')
        else:
            if strings[-2].find(name) == -1:
                self.plainTextEdit.insertPlainText('[' + now.strftime("%H:%M") + ']: ' + name + '\n')

    def load_img(self):
        """Открытие изображения для загрузки в БД"""
        self.reset_right_area()
        self.labelInfo.setStyleSheet('color: rgb(229, 61, 26)')
        self.loading_image = QFileDialog.getOpenFileName(self, 'Выбор картинки', '/home', "Image (*.png *.jpg)")[0]
        # Функции QPixmap.scaled() возвращают масштабированные копии pixmap
        pixmap = QPixmap(self.loading_image).scaled(221, 161,
                                                    Qt.KeepAspectRatio,
                                                    Qt.SmoothTransformation)
        # Помещаем картинку в label для отображения на экране
        self.labelResult.setPixmap(pixmap)

    def save_vector(self):
        """Сохранение вектора лица в БД по заданному изображению"""
        self.labelInfo.setStyleSheet('color: rgb(229, 61, 26)')
        if not self.loading_image:
            self.labelInfo.setText('Загрузите изображение!')
            return
        elif self.textEditName.toPlainText() == '':
            self.labelInfo.setText('Введите свое имя!')
            return
        FR.obj_FR.set_path(self.loading_image)

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
                self.loading_image = 0


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    locale = QLocale.system().name()
    translator = QTranslator(app)
    translator.load('{}qtbase_{}.qm'.format(I18N_QT_PATH, locale))
    app.installTranslator(translator)
    window = FaceApp()  # Создаём объект класса FaceApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
