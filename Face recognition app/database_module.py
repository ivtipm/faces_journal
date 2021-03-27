import sqlite3
import uuid


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


def generate_id():
    return str(uuid.uuid4().fields[-1])[:5]


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
