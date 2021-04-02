# faces_journal

# Todo
- [ ] face_recognition_functions сделать классом
- [ ] туда же стоит добавить загрузку БД
- [ ] и поиск похожего лица


- [ ] добавить поддержку веб-камеры
- [ ] кнопку "заморозить изображение с веб-камеры"
- [ ] кнопку "сохранить картинку с веб камеры в файл"
- [ ] + функция добавления замороженного изображения в БД


# Help
HOG + SVM based face detector.  Относительно простей детектор без нейросетей 
`dlib.get_frontal_face_detector()`

dat_files/shape_predictor_68_face_landmarks.dat -- is trained on the ibug 300-W dataset (https://ibug.doc.ic.ac.uk/resources/facial-point-annotations/)
`dlib.shape_predictor('dat_files/shape_predictor_68_face_landmarks.dat')`

Подробности тут в комментах: http://blog.dlib.net/2014/08/real-time-face-pose-estimation.html



# Ссылки
https://tproger.ru/translations/python-gui-pyqt/ -- создание интерфейса для python программы на фреимворке Qt
