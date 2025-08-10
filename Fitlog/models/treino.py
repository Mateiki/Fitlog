import sqlite3
from database import DB_NAME

class Exercicio:
    def __init__(self, id, nome, carga, repeticoes, needs_attention, treino_id):
        self.id = id
        self.nome = nome
        self.carga = carga
        self.repeticoes = repeticoes
        self.treino_id = treino_id
        # Garante que o estado seja 0 (Padrão) ou 1 (Progressão)
        self.needs_attention = int(needs_attention)

    @staticmethod
    def create(nome, carga, repeticoes, treino_id):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO exercicios (nome, carga, repeticoes, treino_id) VALUES (?, ?, ?, ?)",
            (nome, carga, repeticoes, treino_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update(exercicio_id, novo_nome, nova_carga, novas_repeticoes):
        """ Ao editar, o estado volta para 'Padrão' (needs_attention = 0) """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE exercicios SET nome = ?, carga = ?, repeticoes = ?, needs_attention = 0 WHERE id = ?",
            (novo_nome, nova_carga, int(novas_repeticoes), exercicio_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(exercicio_id):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM exercicios WHERE id = ?", (exercicio_id,))
        conn.commit()
        conn.close()

class Treino:
    def __init__(self, id, nome, usuario_id):
        self.id = id
        self.nome = nome
        self.usuario_id = usuario_id
        self.exercicios = []

    @staticmethod
    def create(nome, usuario_id):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO treinos (nome, usuario_id) VALUES (?, ?)", (nome, usuario_id))
        conn.commit()
        conn.close()

    @staticmethod
    def progredir_treino(treino_id):
        """ Se passar de 12 reps, volta para 8 e muda o estado para 'Progressão' """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, repeticoes FROM exercicios WHERE treino_id = ?", (treino_id,))
        exercicios = cursor.fetchall()
        
        for ex_id, reps_atuais in exercicios:
            novas_reps = (reps_atuais or 8) + 2
            if novas_reps > 12:
                # Se passou de 12, reseta as reps E ativa a flag de atenção.
                # Fazemos isso em um ÚNICO comando UPDATE para este exercício.
                cursor.execute(
                    "UPDATE exercicios SET repeticoes = 8, needs_attention = 1 WHERE id = ?",
                    (ex_id,)
                )
            else:
                # Se não passou de 12, apenas atualiza as reps.
                # A flag 'needs_attention' deste exercício não é alterada.
                cursor.execute(
                    "UPDATE exercicios SET repeticoes = ? WHERE id = ?",
                    (novas_reps, ex_id)
                )
        conn.commit()
        conn.close()

    @staticmethod
    def update_nome(treino_id, novo_nome):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE treinos SET nome = ? WHERE id = ?", (novo_nome, treino_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(treino_id):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM exercicios WHERE treino_id = ?", (treino_id,))
        cursor.execute("DELETE FROM treinos WHERE id = ?", (treino_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_exercicios_by_treino_id(treino_id):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Garante que estamos pegando todas as colunas necessárias na ordem certa
        cursor.execute("SELECT id, nome, carga, repeticoes, needs_attention, treino_id FROM exercicios WHERE treino_id = ?", (treino_id,))
        exercicios_data = cursor.fetchall()
        conn.close()
        
        return [Exercicio(*row) for row in exercicios_data]