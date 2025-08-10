import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from database import DB_NAME
from models.treino import Treino

class Usuario:
    def __init__(self, id, nome, email, senha):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha # Contém o hash da senha

    @staticmethod
    def create(nome, email, senha):
        """Cria e salva um novo usuário no banco de dados."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        senha_hash = generate_password_hash(senha)
        try:
            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                (nome, email, senha_hash)
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar usuário: {e}")
        finally:
            conn.close()

    def check_password(self, senha_plana):
        """Verifica se a senha fornecida corresponde ao hash salvo."""
        return check_password_hash(self.senha, senha_plana)

    @staticmethod
    def find_by_email(email):
        """Busca um usuário pelo email."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            return Usuario(*user_data)
        return None

    @staticmethod
    def find_by_id(user_id):
        """Busca um usuário pelo seu ID."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            return Usuario(*user_data)
        return None

    def get_treinos(self):
        """Busca todos os treinos associados a este usuário."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, usuario_id FROM treinos WHERE usuario_id = ?", (self.id,))
        treinos_data = cursor.fetchall()
        conn.close()
        
        lista_de_treinos = []
        for treino_data in treinos_data:
            treino = Treino(*treino_data)
            treino.exercicios = Treino.get_exercicios_by_treino_id(treino.id)
            lista_de_treinos.append(treino)
        
        return lista_de_treinos

    # Manter os métodos de gerenciamento de conta (ainda são úteis para a página de informações)
    @staticmethod
    def update_nome(user_id, novo_nome):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET nome = ? WHERE id = ?", (novo_nome, user_id))
        conn.commit()
        conn.close()

    def update_senha(self, nova_senha):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        nova_senha_hash = generate_password_hash(nova_senha)
        cursor.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (nova_senha_hash, self.id))
        conn.commit()
        conn.close()
    
    def delete(user_id):
        """
        Deleta um usuário e todos os seus dados associados (treinos e exercícios).
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            # 1. Encontra todos os treinos do usuário
            cursor.execute("SELECT id FROM treinos WHERE usuario_id = ?", (user_id,))
            treinos_ids = cursor.fetchall()

            # 2. Para cada treino, deleta os exercícios associados
            for treino_id_tuple in treinos_ids:
                cursor.execute("DELETE FROM exercicios WHERE treino_id = ?", (treino_id_tuple[0],))
            
            # 3. Deleta todos os treinos do usuário
            cursor.execute("DELETE FROM treinos WHERE usuario_id = ?", (user_id,))

            # 4. Finalmente, deleta o próprio usuário
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao deletar usuário: {e}")
            conn.rollback()
        finally:
            conn.close()
