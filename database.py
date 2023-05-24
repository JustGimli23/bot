import sqlite3


def get_curs():
    con = sqlite3.connect("metanit.db")
    cursor = con.cursor()

    return con, cursor


def set_messsages(id: int, message: str) -> None:
    db, cursor = get_curs()

    cursor.execute(f"""CREATE TABLE IF NOT EXISTS user_{id} 
                (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                text TEXT NOT NULL)
            """)

    cursor.execute(f"""INSERT INTO user_{id}
                          (text)
                           VALUES 
                          (?)""", (message))

    db.commit()

    cursor.close()


def create_chat(id: int):
    db, cursor = get_curs()

    cursor.execute(f"""CREATE TABLE IF NOT EXISTS user_chats_{id} 
                ( name_chat TEXT NOT NULL)
            """)

    cursor.close()


def set_chats(id: int, chat: list):

    db, cursor = get_curs()

    cursor.execute(f"""CREATE TABLE IF NOT EXISTS user_chats_{id} 
                ( name_chat TEXT NOT NULL)
            """)

    for i in chat:
        cursor.execute(f"""INSERT INTO user_chats_{id} VALUES (?)""", [i])

    db.commit()
    cursor.close()


def del_chat(id: int, chat_id: list):
    db, cursor = get_curs()

    for i in chat_id:
        cursor.execute(f'DELETE FROM user_chats_{id} WHERE rowid={i}')

    db.commit()
    cursor.close()


def show_chats(id: int) -> str:
    db, cursor = get_curs()

    res = ''
    for b in cursor.execute(f'SELECT rowid,name_chat  FROM user_chats_{id}'):
        res += f'{b[0]}: {b[1]}\n'

    cursor.close()

    return res


def show_chats_id(id: int) -> list:
    db, cursor = get_curs()

    res = []
    for b in cursor.execute(f'SELECT rowid,name_chat  FROM user_chats_{id}'):
        res.append(b[0])

    cursor.close()

    return res


def get_name_chats(id, ids):
    db, cursor = get_curs()

    name = []

    for i in ids:
        for b in cursor.execute(f'SELECT name_chat FROM user_chats_{id} WHERE rowid={i}'):
            name.append(b[0])

    cursor.close()

    return name
