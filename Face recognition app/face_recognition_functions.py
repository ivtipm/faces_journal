import cv2  # computer vision
import dlib  # библиотека с алгоритмами МО
from scipy.spatial import distance


def return_img_vector(path):
    """
    Вернет вектор лица, найденного на изображении.
        path - путь к изображению на диске
    """
    img = cv2.imread(path)
    try:
        # объект для детекции лиц
        detector = dlib.get_frontal_face_detector()
        # вернёт список из прямоугольников, где обнаружены лица
        face_rects = detector(img)
        print(face_rects)
        # ищет опорные точки на лице
        sp = dlib.shape_predictor('dat_files/shape_predictor_68_face_landmarks.dat')
        face_shape = sp(img, face_rects[0])
        facerec = dlib.face_recognition_model_v1('dat_files/dlib_face_recognition_resnet_model_v1.dat')
        face_descriptor = facerec.compute_face_descriptor(img, face_shape)
        return face_descriptor
    except Exception:
        return 0


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
