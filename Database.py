import sqlite3


DB_FILE = "securevault.db"

class Database:
    #Create Database and Tables
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)

        self.conn.execute('''
                            CREATE TABLE IF NOT EXISTS settings (
                            id INTEGER PRIMARY KEY,
                            salt BLOB NOT NULL,
                            verified BLOB NOT NULL)
                          ''')

        self.conn.execute('''
                          CREATE TABLE IF NOT EXISTS credentials
                          (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              service BLOB NOT NULL,
                              username BLOB NOT NULL,
                              password BLOB NOT NULL,
                              notes BLOB,
                              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                          )
                          ''')
        self.conn.commit()

    #Function to check if master password exists
    def master_exists(self):
        row=self.conn.execute(
            "Select id from settings where id=1"
        ).fetchone()

        return row is not None

    #Function to store master password
    def create_master(self,salt, verifier):
        self.conn.execute(
            "INSERT INTO settings(id,salt,verifier) VALUES (1,?,?)",
            (salt,verifier)
        )
        self.conn.commit()

    #Function to retrieve master password
    def get_master(self):
        return self.conn.execute(
            "SELECT salt, verifier FROM settings where id = 1"
            ).fetchone()

    #Function to add credential to the database
    def add_credential(
        self,
        service,
        username,
        password,
        notes
    ):

        self.conn.execute("""

        INSERT INTO credentials(

        service,
        username,
        password,
        notes

        )

        VALUES(?,?,?,?)

        """,

        (
            service,
            username,
            password,
            notes
        ))

        self.conn.commit()

    #Function to update credential in the database
    def update_credential(
        self,
        credential_id,
        service,
        username,
        password,
        notes
    ):

        self.conn.execute("""

        UPDATE credentials

        SET

        service=?,
        username=?,
        password=?,
        notes=?

        WHERE id=?

        """,

        (
            service,
            username,
            password,
            notes,
            credential_id
        ))

        self.conn.commit()

    #Function to delete credential from the database
    def delete_credential(self, credential_id):

        self.conn.execute(

            "DELETE FROM credentials WHERE id=?",

            (credential_id,)

        )

        self.conn.commit()

    #Function to fetch credentials from the database
    def get_credentials(self):

        return self.conn.execute("""

        SELECT

        id,
        service,
        username,
        password,
        notes

        FROM credentials

        ORDER BY id DESC

        """).fetchall()
