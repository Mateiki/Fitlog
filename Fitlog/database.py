import sqlite3

DB_NAME = 'fitlog.db'

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')

    # Tabela de treinos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS treinos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')

    # Tabela de exercícios
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercicios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                carga TEXT,
                repeticoes INTEGER,
                needs_attention BOOLEAN DEFAULT 0,
                treino_id INTEGER NOT NULL,
                FOREIGN KEY (treino_id) REFERENCES treinos (id)
            )
        ''')

    print("Tabelas 'usuarios', 'treinos' e 'exercicios' criadas com sucesso.")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()