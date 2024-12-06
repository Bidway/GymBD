import sqlite3

def create_tables():
    connection_params = {"database": "fitness_db.sqlite3"}
    connect = sqlite3.connect(connection_params["database"])
    cursor = connect.cursor()

    # Таблица Клиенты
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS Клиенты (
                id INTEGER PRIMARY KEY,
                имя TEXT,
                возраст INTEGER,
                телефон TEXT
            )
        ''')
    # Таблица Абонементы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Абонементы (
            id INTEGER PRIMARY KEY,
            название TEXT,
            стоимость INTEGER,
            длительность_дней INTEGER
        )
    ''')

    # Таблица Залы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Залы (
            id INTEGER PRIMARY KEY,
            размер TEXT,
            состояние TEXT,
            вместимость INTEGER
        )
    ''')

    # Таблица Тренеры
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Тренеры (
            id INTEGER PRIMARY KEY,
            имя TEXT,
            опыт_лет INTEGER,
            специализация TEXT
        )
    ''')


    # Таблица Тренировки
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Тренировки (
            id INTEGER PRIMARY KEY,
            Клиент_id INTEGER,
            Абонемент_id INTEGER,
            Зал_id INTEGER,
            Тренер_id INTEGER,
            FOREIGN KEY (Клиент_id) REFERENCES Клиенты (id),
            FOREIGN KEY (Абонемент_id) REFERENCES Абонементы (id),
            FOREIGN KEY (Зал_id) REFERENCES Залы (id),
            FOREIGN KEY (Тренер_id) REFERENCES Тренеры (id)
        )
    ''')

    cursor.executemany('''
            INSERT INTO Клиенты (имя, возраст, телефон) VALUES (?, ?, ?)
        ''', [
        ("Алексей", 25, "+375291234567"),
        ("Мария", 30, "+375292345678"),
        ("Дмитрий", 28, "+375293456789"),
        ("Екатерина", 22, "+375294567890"),
        ("Иван", 35, "+375295678901")
    ])

    cursor.executemany('''
            INSERT INTO Абонементы (название, стоимость, длительность_дней) VALUES (?, ?, ?)
        ''', [
        ("Базовый", 5000, 30),
        ("Стандартный", 7000, 60),
        ("Премиум", 10000, 90),
        ("VIP", 15000, 120),
        ("Тренировочный", 3000, 15)
    ])

    cursor.executemany('''
            INSERT INTO Залы (размер, состояние, вместимость) VALUES (?, ?, ?)
        ''', [
        ("Маленький", "Хорошее", 15),
        ("Средний", "Отличное", 25),
        ("Большой", "Удовлетворительное", 50),
        ("Премиальный", "Отличное", 10),
        ("Стандартный", "Хорошее", 20)
    ])

    cursor.executemany('''
            INSERT INTO Тренеры (имя, опыт_лет, специализация) VALUES (?, ?, ?)
        ''', [
        ("Сергей", 5, "Силовые тренировки"),
        ("Анна", 3, "Кардиотренировки"),
        ("Максим", 7, "Йога"),
        ("Ольга", 2, "Танцы"),
        ("Игорь", 10, "Боевые искусства")
    ])

    cursor.executemany('''
            INSERT INTO Тренировки (Клиент_id, Абонемент_id, Зал_id, Тренер_id) VALUES (?, ?, ?, ?)
        ''', [
        (1, 1, 1, 1),
        (2, 2, 2, 2),
        (3, 3, 3, 3),
        (4, 4, 4, 4),
        (5, 5, 5, 5)
    ])

    connect.commit()
    cursor.close()
    connect.close()

if __name__ == "__main__":
    create_tables()
    print("Таблицы созданы и данные добавлены.")
