import sqlite3

# Nome do arquivo do banco de dados SQLite
DB_NAME = 'biblioteca.db'

def conectar_db():
    """
    Estabelece e retorna uma conexão com o banco de dados SQLite e um cursor.
    Habilita o suporte a chaves estrangeiras.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON")  # Ativa a checagem de chaves estrangeiras
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None, None

def criar_tabelas():
    """
    Cria as tabelas 'autor' e 'livro' no banco de dados, se elas ainda não existirem.
    A tabela 'livro' terá uma chave estrangeira referenciando 'autor'.
    """
    conn, cursor = conectar_db()
    if conn is None or cursor is None:
        print("Falha ao conectar ao banco de dados. Tabelas não podem ser criadas.")
        return # Não foi possível conectar ao DB

    try:
        # --- Tabela AUTOR ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS autor (
                id_autor INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            )
        ''')

        # --- Tabela LIVRO ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS livro (
                id_livro INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                id_autor INTEGER NOT NULL,
                FOREIGN KEY (id_autor) REFERENCES autor(id_autor)
                    ON DELETE RESTRICT
                    ON UPDATE CASCADE
            )
        ''')

        conn.commit()
        print(f"Tabelas 'autor' e 'livro' verificadas/criadas com sucesso no arquivo '{DB_NAME}'.")
    except sqlite3.Error as e:
        print(f"Erro ao criar as tabelas: {e}")
    finally:
        if conn:
            conn.close()

# --- Funções CRUD para a Tabela AUTOR ---

def adicionar_autor(nome):
    """Adiciona um novo autor ao banco de dados."""
    conn, cursor = conectar_db()
    if conn is None: return None

    try:
        cursor.execute("INSERT INTO autor (nome) VALUES (?)", (nome,))
        conn.commit()
        last_id = cursor.lastrowid
        # print(f"Autor '{nome}' adicionado com ID: {last_id}.") # Opcional: para debug no console
        return last_id
    except sqlite3.IntegrityError:
        # print(f"Erro de integridade: O autor '{nome}' já está cadastrado.") # Opcional
        return None
    except sqlite3.Error as e:
        print(f"Erro ao adicionar autor '{nome}': {e}")
        return None
    finally:
        if conn:
            conn.close()

def listar_autores():
    """Retorna uma lista de todos os autores, ordenados por nome."""
    conn, cursor = conectar_db()
    if conn is None: return []

    try:
        cursor.execute("SELECT id_autor, nome FROM autor ORDER BY nome ASC")
        autores = cursor.fetchall()
        return autores
    except sqlite3.Error as e:
        print(f"Erro ao buscar autores: {e}")
        return []
    finally:
        if conn:
            conn.close()

def atualizar_autor(id_autor, novo_nome):
    """Atualiza o nome de um autor existente."""
    conn, cursor = conectar_db()
    if conn is None: return False

    try:
        cursor.execute("UPDATE autor SET nome = ? WHERE id_autor = ?", (novo_nome, id_autor))
        conn.commit()
        if cursor.rowcount > 0:
            # print(f"Autor ID {id_autor} atualizado para '{novo_nome}'.") # Opcional
            return True
        else:
            # print(f"Autor ID {id_autor} não encontrado para atualização.") # Opcional
            return False # Nenhuma linha foi afetada, ID pode não existir
    except sqlite3.IntegrityError:
        # print(f"Erro de integridade: O nome '{novo_nome}' já existe para outro autor.") # Opcional
        return False
    except sqlite3.Error as e:
        print(f"Erro ao atualizar autor ID {id_autor}: {e}")
        return False
    finally:
        if conn:
            conn.close()

def deletar_autor(id_autor):
    """Deleta um autor, somente se ele não tiver livros associados."""
    conn, cursor = conectar_db()
    if conn is None: return False

    try:
        cursor.execute("DELETE FROM autor WHERE id_autor = ?", (id_autor,))
        conn.commit()
        if cursor.rowcount > 0:
            # print(f"Autor ID {id_autor} deletado com sucesso.") # Opcional
            return True
        else:
            # print(f"Autor ID {id_autor} não encontrado para deleção.") # Opcional
            return False
    except sqlite3.IntegrityError as e: # Acionado pelo ON DELETE RESTRICT
        # print(f"Erro de integridade: Não é possível deletar o autor ID {id_autor}, pois ele possui livros cadastrados. ({e})") # Opcional
        return False
    except sqlite3.Error as e:
        print(f"Erro ao deletar autor ID {id_autor}: {e}")
        return False
    finally:
        if conn:
            conn.close()

def buscar_autor_por_id(id_autor): # Esta função não estava sendo usada na GUI, mas é útil
    """Busca um autor específico pelo seu ID."""
    conn, cursor = conectar_db()
    if conn is None: return None

    try:
        cursor.execute("SELECT id_autor, nome FROM autor WHERE id_autor = ?", (id_autor,))
        autor = cursor.fetchone()
        return autor
    except sqlite3.Error as e:
        print(f"Erro ao buscar autor por ID {id_autor}: {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- Funções CRUD para a Tabela LIVRO ---

def adicionar_livro(titulo, id_autor):
    """Adiciona um novo livro ao banco de dados, associado a um autor."""
    conn, cursor = conectar_db()
    if conn is None: return None

    try:
        cursor.execute("INSERT INTO livro (titulo, id_autor) VALUES (?, ?)", (titulo, id_autor))
        conn.commit()
        last_id = cursor.lastrowid
        # print(f"Livro '{titulo}' adicionado com ID: {last_id} para o autor ID: {id_autor}.") # Opcional
        return last_id
    except sqlite3.IntegrityError as e:
        # print(f"Erro de integridade ao adicionar livro '{titulo}' (verifique se o autor ID {id_autor} existe): {e}") # Opcional
        return None
    except sqlite3.Error as e:
        print(f"Erro ao adicionar livro '{titulo}': {e}")
        return None
    finally:
        if conn:
            conn.close()

def listar_livros_com_autor():
    """
    Retorna uma lista de todos os livros, incluindo o ID do livro, título,
    o NOME do autor e o ID do autor. Ordenados por título do livro.
    """
    conn, cursor = conectar_db()
    if conn is None: return []

    try:
        # A ordem das colunas no SELECT deve corresponder à forma como são usadas na GUI
        cursor.execute('''
            SELECT l.id_livro, l.titulo, a.nome, l.id_autor
            FROM livro l
            INNER JOIN autor a ON l.id_autor = a.id_autor
            ORDER BY l.titulo ASC
        ''')
        livros = cursor.fetchall()
        return livros
    except sqlite3.Error as e:
        print(f"Erro ao buscar livros com nomes dos autores: {e}")
        return []
    finally:
        if conn:
            conn.close()

def atualizar_livro(id_livro, novo_titulo, novo_id_autor):
    """Atualiza o título e/ou o autor de um livro existente."""
    conn, cursor = conectar_db()
    if conn is None: return False

    try:
        cursor.execute("UPDATE livro SET titulo = ?, id_autor = ? WHERE id_livro = ?",
                       (novo_titulo, novo_id_autor, id_livro))
        conn.commit()
        if cursor.rowcount > 0:
            # print(f"Livro ID {id_livro} atualizado.") # Opcional
            return True
        else:
            # print(f"Livro ID {id_livro} não encontrado para atualização.") # Opcional
            return False
    except sqlite3.IntegrityError as e:
        # print(f"Erro de integridade ao atualizar livro ID {id_livro} (verifique se o autor ID {novo_id_autor} existe): {e}") # Opcional
        return False
    except sqlite3.Error as e:
        print(f"Erro ao atualizar livro ID {id_livro}: {e}")
        return False
    finally:
        if conn:
            conn.close()

def deletar_livro(id_livro):
    """Deleta um livro do banco de dados."""
    conn, cursor = conectar_db()
    if conn is None: return False

    try:
        cursor.execute("DELETE FROM livro WHERE id_livro = ?", (id_livro,))
        conn.commit()
        if cursor.rowcount > 0:
            # print(f"Livro ID {id_livro} deletado com sucesso.") # Opcional
            return True
        else:
            # print(f"Livro ID {id_livro} não encontrado para deleção.") # Opcional
            return False
    except sqlite3.Error as e:
        print(f"Erro ao deletar livro ID {id_livro}: {e}")
        return False
    finally:
        if conn:
            conn.close()

def buscar_livro_por_id(id_livro): # Esta função não estava sendo usada na GUI, mas é útil
    """Busca um livro específico pelo seu ID, incluindo o nome do autor."""
    conn, cursor = conectar_db()
    if conn is None: return None

    try:
        cursor.execute('''
            SELECT l.id_livro, l.titulo, a.nome AS nome_autor, l.id_autor
            FROM livro l
            INNER JOIN autor a ON l.id_autor = a.id_autor
            WHERE l.id_livro = ?
        ''', (id_livro,))
        livro = cursor.fetchone()
        return livro
    except sqlite3.Error as e:
        print(f"Erro ao buscar livro por ID {id_livro}: {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- Bloco para execução de teste (opcional) ---
if __name__ == '__main__':
    print("--- Executando testes do módulo database.py ---")
    criar_tabelas()

    print("\n[TESTE] Adicionando autores...")
    id_a1 = adicionar_autor("Carlos Drummond de Andrade")
    id_a2 = adicionar_autor("Cecília Meireles")

    print("\n[TESTE] Listando autores:")
    for autor in listar_autores(): print(f"  {autor}")

    if id_a1: adicionar_livro("Sentimento do Mundo", id_a1)
    if id_a2: adicionar_livro("Romanceiro da Inconfidência", id_a2)
    if id_a1: adicionar_livro("A Rosa do Povo", id_a1)

    print("\n[TESTE] Listando livros com autores:")
    for livro in listar_livros_com_autor(): print(f"  {livro}")

    print("\n--- Fim dos testes ---")