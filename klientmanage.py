import psycopg2

try:
    connection = psycopg2.connect(
        host="<localhost>",  # имя хоста базы данных
        database="<postgres-Client-Management>",  # имя базы данных
        user="<postgresCM>",  # имя пользователя
        password="<postgresCM++>"  # пароль пользователя
    )
    cursor = connection.cursor()
    print("Подключение к PostgreSQL успешно")

    # Выполнение SQL-запросов

    connection.close()
    print("Соединение с PostgreSQL закрыто")

except (Exception, psycopg2.Error) as error:
    print("Ошибка при подключении к PostgreSQL:", error)


def create_db(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                id SERIAL PRIMARY KEY,
                client_id INT NOT NULL,
                phone_number VARCHAR(20) NOT NULL,
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
            )
        """)

    conn.commit()


def add_client(conn, first_name, last_name, email, phone=None):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO clients (first_name, last_name, email)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (first_name, last_name, email))
        client_id = cursor.fetchone()[0]

        if phone:
            cursor.execute("""
                INSERT INTO phones (client_id, phone_number)
                VALUES (%s, %s)
            """, (client_id, phone))

    conn.commit()


def add_phone(conn, client_id, phone):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO phones (client_id, phone_number)
            VALUES (%s, %s)
        """, (client_id, phone))

    conn.commit()


def change_client(conn, client_id, first_name=None, last_name=None, email=None):
    with conn.cursor() as cursor:
        if first_name:
            cursor.execute("""
                UPDATE clients
                SET first_name = %s
                WHERE id = %s
            """, (first_name, client_id))

        if last_name:
            cursor.execute("""
                UPDATE clients
                SET last_name = %s
                WHERE id = %s
            """, (last_name, client_id))

        if email:
            cursor.execute("""
                UPDATE clients
                SET email = %s
                WHERE id = %s
            """, (email, client_id))

    conn.commit()


def delete_phone(conn, client_id, phone):
    with conn.cursor() as cursor:
        cursor.execute("""
            DELETE FROM phones
            WHERE client_id = %s AND phone_number = %s
        """, (client_id, phone))

    conn.commit()


def delete_client(conn, client_id):
    with conn.cursor() as cursor:
        cursor.execute("""
            DELETE FROM clients
            WHERE id = %s
        """, (client_id,))

    conn.commit()


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    query = """
        SELECT c.id, c.first_name, c.last_name, c.email, p.phone_number
        FROM clients c
        LEFT JOIN phones p ON c.id = p.client_id
        WHERE 1=1
    """
    params = []

    if first_name:
        query += " AND c.first_name = %s"
        params.append(first_name)

    if last_name:
        query += " AND c.last_name = %s"
        params.append(last_name)

    if email:
        query += " AND c.email = %s"
        params.append(email)

    if phone:
        query += " AND p.phone_number = %s"
        params.append(phone)

    with conn.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    clients = []
    current_client_id = None
    current_client_data = None

    for row in rows:
        client_id = row[0]
        first_name = row[1]
        last_name = row[2]
        email = row[3]
        phone_number = row[4]

        if client_id != current_client_id:
            if current_client_data:
                clients.append(current_client_data)

            current_client_id = client_id
            current_client_data = {
                "id": client_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phones": [],
            }

        if phone_number:
            current_client_data["phones"].append(phone_number)

    if current_client_data:
        clients.append(current_client_data)

    return clients


# Пример использования функций

# Подключение к базе данных
with psycopg2.connect(database="postgres-Client-Management", user="postgresCM", password="postgresCM++") as conn:
    # Создание структуры базы данных
    create_db(conn)

    # Добавление нового клиента
    add_client(conn, "John", "Doe", "johndoe@example.com", "+1234567890")

    # Добавление клиента без указания телефона
    add_client(conn, "Jane", "Smith", "janesmith@example.com")

    # Добавление телефона для существующего клиента
    add_phone(conn, client_id=1, phone="+9876543210")

    # Изменение данных о клиенте
    change_client(conn, client_id=1, email="johndoe_updated@example.com")

    # Удаление телефона для существующего клиента
    delete_phone(conn, client_id=1, phone="+9876543210")

    # Удаление клиента
    delete_client(conn, client_id=1)

    # Поиск клиента по данным
    result = find_client(conn, first_name="Jane")
    print(result)




