import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            firstname VARCHAR(30) NOT NULL,
            lastname VARCHAR(30) NOT NULL,
            email VARCHAR(64) NOT NULL UNIQUE
            );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phone(
            client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
            phonenumber VARCHAR(30) NOT NULL UNIQUE
            );
        """)
        conn.commit()

def add_client(conn, first_name, last_name, email, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clients(firstname, lastname, email)
            VALUES(%s, %s, %s)
            """, (first_name, last_name, email))
        cur.execute("""
            SELECT id FROM clients
            ORDER BY id DESC
            LIMIT 1
            """)
        id = cur.fetchone()[0]
        if phone is None:
            return id
        else:
            add_phone(conn, id, phone)
            return id


def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
                INSERT INTO phone(client_id, phonenumber)
                VALUES (%s, %s)
        """, (client_id, phone))
        return client_id

def change_client(conn, client_id, first_name=None, last_name=None, email=None):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM clients
            WHERE id = %s
            """, (client_id, ))
        info_user = cur.fetchone()
        if first_name is None:
            first_name = info_user[1]
        if last_name is None:
            last_name = info_user[2]
        if email is None:
            email = info_user[3]
        cur.execute("""
            UPDATE clients
            SET firstname = %s, lastname = %s, email = %s
            WHERE id = %s
            """, (first_name, last_name, email, client_id))
        return client_id

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phone
            WHERE client_id = %s and phonenumber = %s
            RETURNING *
            """, (client_id, phone))
        if not cur.fetchone():
            return "Такого номера телефона нет"
        conn.commit()
    return "Успешная операция"



def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM clients
            WHERE id = %s
        """, (client_id, ))
        return client_id

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        if first_name is None:
            first_name = "%"
        else:
            first_name = "%" + first_name + "%"
        if last_name is None:
            last_name = "%"
        else:
            last_name = "%" + last_name + "%"
        if email is None:
            email = "%"
        else:
            email = "%" + email + "%"
        if phone is None:
            cur.execute("""
                SELECT c.id, c.firstname, c.lastname, c.email, p.phonenumber FROM clients c
                LEFT JOIN phone p ON c.id = p.client_id
                WHERE c.firstname LIKE %s AND c.lastname LIKE %s and c.email LIKE %s
            """, (first_name, last_name, email))
        else:
            cur.execute("""
                SELECT c.id, c.firstname, c.lastname, c.email, p.phonenumber FROM clients c
                LEFT JOIN phone p ON c.id = p.client_id
                WHERE c.firstname LIKE %s AND c.lastname LIKE %s AND c.email LIKE %s AND p.phonenumber LIKE %s
            """, (first_name, last_name, email, phone))
        return cur.fetchone()



with psycopg2.connect(database="postgres", user="postgres", password="") as conn:
    # with conn.cursor() as cur:
    #     cur.execute("""
    #     DROP TABLE phone;
    #     DROP TABLE clients;
    #     """)

    create_db(conn)

    add_client(conn, "Michael", "Jackson", "16655jh@gmail.com")
    add_client(conn, "Mikhail", "Shafutinsky", "76hbhjn@gmail.com", 79346943)
    add_client(conn, "Egor", "Kreed", "7bgjbhy66@gmail.com", 79856643)

    add_phone(conn, 1, "79876543")

    change_client(conn, 2, "Egor", "Ivanov", "hyghg23d@gmail.com")

    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.firstname, c.lastname, c.email, p.phonenumber FROM clients c
            LEFT JOIN phone p ON c.id = p.client_id
            ORDER BY c.id
            """)
        print(cur.fetchall())

    delete_phone(conn, 2, "79346943")

    delete_client(conn, 3)

    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.firstname, c.lastname, c.email, p.phonenumber FROM clients c
            LEFT JOIN phone p ON c.id = p.client_id
            ORDER BY c.id
            """)
        print(cur.fetchall())

    print(find_client(conn, "Egor"))
    print(find_client(conn, "Egor", "Ivanov"))
    print(find_client(conn, None, None, "hyghg23d@gmail.com"))
    print(find_client(conn, None, None, None, "79876543"))


conn.close()
