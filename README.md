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
Распознование 

1. HOG + SVM based face detector.  Относительно простей детектор без нейросетей 
`dlib.get_frontal_face_detector()`

1. Похоже тут используется: One Millisecond Face Alignment with an Ensemble of Regression Trees [https://aigenexpert.com/blog/detecting-facial-landmarks-with-opencv-and-dlib/]
2dat_files/shape_predictor_68_face_landmarks.dat -- is trained on the ibug 300-W dataset (https://ibug.doc.ic.ac.uk/resources/facial-point-annotations/)
`dlib.shape_predictor('dat_files/shape_predictor_68_face_landmarks.dat')`\
Подробности тут (?) в комментах: http://blog.dlib.net/2014/08/real-time-face-pose-estimation.html

1.  Заново обученный ResNet с некоторыми обрезанными слоями
`facerec = dlib.face_recognition_model_v1('dat_files/dlib_face_recognition_resnet_model_v1.dat')`
https://github.com/davisking/dlib-models

 


# Ссылки
https://tproger.ru/translations/python-gui-pyqt/ -- создание интерфейса для python программы на фреимворке Qt
