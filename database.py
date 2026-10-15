import sqlite3

DATABASE_NAME = "weather_history.db"


def create_table():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_search(location):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO search_history (location) VALUES (?)",
        (location,)
    )

    connection.commit()
    connection.close()


def get_search_history():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, location, searched_at
        FROM search_history
        ORDER BY id DESC
        LIMIT 10
    """)

    history = cursor.fetchall()
    connection.close()

    return history


def delete_search(search_id):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM search_history WHERE id = ?",
        (search_id,)
    )

    connection.commit()
    connection.close()


def clear_search_history():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM search_history")

    connection.commit()
    connection.close()