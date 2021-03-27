import sqlite3
import cv2  # computer vision
import dlib  # библиотека с алгоритмами МО
from scipy.spatial import distance


def search_for_matches(face_descriptor1):
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
            face_descriptor2 = tuple(float(item) for item in rec[1].split(' '))
            value = calc_euclid(face_descriptor1, face_descriptor2)
            if value < 0.6:
                return rec[0], value  # Есть совпадения
    return '', 0  # Нет совпадений


def calc_euclid(face_descriptor1, face_descriptor2):
    """
    Рассчитает число для верификации лица - евклидово расстояние
        face_descriptor1: дескриптор первого лица
        face_descriptor2: дескриптор второго лица
    """
    # Расчитываем евклидово расстояние
    euclid = distance.euclidean(face_descriptor1, face_descriptor2)
    # Возвращаем результат (если < 0.6, значит на картинках есть совпадение)
    return euclid


class FaceRecognition(object):

    def __init__(self, path):
        self.path = path

    def set_path(self, path):
        self.path = path

    def return_img_vector(self):
        """
        Вернет вектор лица, найденного на изображении.
            path - путь к изображению на диске
        """
        img = cv2.imread(self.path)
        try:
            # объект для детекции лиц
            detector = dlib.get_frontal_face_detector()
            # вернёт список из прямоугольников, где обнаружены лица
            face_rects = detector(img)
            print(face_rects)
            fd_array = []
            for rec in face_rects:
                # ищет опорные точки на лице
                sp = dlib.shape_predictor('dat_files/shape_predictor_68_face_landmarks.dat')
                face_shape = sp(img, rec)
                facerec = dlib.face_recognition_model_v1('dat_files/dlib_face_recognition_resnet_model_v1.dat')
                face_descriptor = facerec.compute_face_descriptor(img, face_shape)
                fd_array.append(face_descriptor)
            return fd_array
        except Exception:
            return 0


obj_FR = FaceRecognition('')
