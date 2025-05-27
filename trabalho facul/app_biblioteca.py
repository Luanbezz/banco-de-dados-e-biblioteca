import tkinter as tk
from tkinter import ttk, messagebox
import database as db  # Nosso módulo para interagir com o banco de dados SQLite

# --- CLASSE PRINCIPAL DA APLICAÇÃO ---
class AppBiblioteca(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gerenciamento de Biblioteca")
        self.geometry("850x650") # Um pouco maior para melhor visualização
        self.minsize(700, 500) # Tamanho mínimo da janela

        # Chamada para criar/verificar tabelas no banco de dados ao iniciar
        # Esta função está definida em database.py
        db.criar_tabelas()

        # Container principal onde as diferentes "telas" (frames) serão exibidas
        self.container = ttk.Frame(self, padding="10")
        self.container.pack(fill="both", expand=True)

        self.frames = {}  # Dicionário para armazenar as instâncias dos frames

        self._criar_menus_navegacao_ajuda()
        self.mostrar_tela(AutoresFrame) # Inicia mostrando a tela de autores

    def _criar_menus_navegacao_ajuda(self):
        """Cria a barra de menus superior da aplicação."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Menu "Navegação"
        menu_navegacao = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Navegação", menu=menu_navegacao)
        menu_navegacao.add_command(label="Gerenciar Autores", command=lambda: self.mostrar_tela(AutoresFrame))
        menu_navegacao.add_command(label="Gerenciar Livros", command=lambda: self.mostrar_tela(LivrosFrame))
        menu_navegacao.add_separator()
        menu_navegacao.add_command(label="Sair", command=self.quit)

        # Menu "Ajuda"
        menu_ajuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Sobre o Sistema", command=self._mostrar_dialogo_sobre)

    def mostrar_tela(self, classe_frame):
        """Gerencia a exibição das telas (frames) no container principal."""
        # Destroi widgets do frame anterior para limpar o container
        for widget in self.container.winfo_children():
            widget.destroy()

        # Cria uma nova instância do frame ou reutiliza uma existente (se não foi destruída)
        frame = self.frames.get(classe_frame)
        if not frame or not frame.winfo_exists():
            frame = classe_frame(self.container, self)  # Passa o container e a instância da app
            self.frames[classe_frame] = frame
        frame.pack(fill="both", expand=True)

        # Atualiza título e dados da tela
        if classe_frame == AutoresFrame:
            self.title("Biblioteca - Gerenciar Autores")
            frame.atualizar_lista_autores() # Garante que a lista de autores seja carregada/atualizada
        elif classe_frame == LivrosFrame:
            self.title("Biblioteca - Gerenciar Livros")
            frame.atualizar_combobox_autores() # Essencial para o cadastro de livros
            frame.atualizar_lista_livros()   # Garante que a lista de livros seja carregada/atualizada

    def _mostrar_dialogo_sobre(self):
        """Exibe a caixa de diálogo 'Sobre' com os créditos."""
        titulo_janela = "Sobre o Sistema de Biblioteca"
        mensagem = """
        Título do Projeto: Banco de dados e Biblioteca
        --------------------------------------------------
        Equipe de Desenvolvimento:
        - Luan José Bezerra da Silva
        - Victor da costa
        --------------------------------------------------
        Descrição da Aplicação:
        Este sistema permite o gerenciamento de autores e
        livros de uma biblioteca. Desenvolvido com Tkinter
        para a interface gráfica e SQLite para o armazenamento
        de dados, oferece funcionalidades de cadastro, consulta,
        atualização e exclusão de registros.
        """
        messagebox.showinfo(titulo_janela, mensagem)


# --- TELA (FRAME) PARA GERENCIAMENTO DE AUTORES ---
class AutoresFrame(ttk.Frame):
    def __init__(self, parent_container, app_controller):
        super().__init__(parent_container)
        self.app_controller = app_controller  # Referência à instância principal da App
        self.id_autor_selecionado = None  # Armazena o ID do autor selecionado na Treeview

        # --- Widgets do Formulário ---
        frame_formulario = ttk.LabelFrame(self, text="Dados do Autor", padding=(15, 10))
        frame_formulario.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame_formulario, text="Nome do Autor:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nome_autor_var = tk.StringVar()
        self.entry_nome_autor = ttk.Entry(frame_formulario, textvariable=self.nome_autor_var, width=50)
        self.entry_nome_autor.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        frame_formulario.columnconfigure(1, weight=1) # Faz a entry expandir com a janela

        # --- Botões de Ação ---
        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(pady=5, padx=10, fill="x")

        self.btn_adicionar = ttk.Button(frame_botoes, text="Adicionar", command=self._adicionar_autor)
        self.btn_adicionar.pack(side="left", padx=5)
        self.btn_atualizar = ttk.Button(frame_botoes, text="Atualizar Selecionado", command=self._atualizar_autor, state="disabled")
        self.btn_atualizar.pack(side="left", padx=5)
        self.btn_deletar = ttk.Button(frame_botoes, text="Deletar Selecionado", command=self._deletar_autor, state="disabled")
        self.btn_deletar.pack(side="left", padx=5)
        self.btn_limpar = ttk.Button(frame_botoes, text="Limpar Formulário", command=self._limpar_campos_autor)
        self.btn_limpar.pack(side="left", padx=5)

        # --- Grade (Treeview) para Exibir Autores ---
        frame_treeview = ttk.Frame(self)
        frame_treeview.pack(pady=10, padx=10, fill="both", expand=True)

        colunas_treeview = ("id_autor", "nome")
        self.tree_autores = ttk.Treeview(frame_treeview, columns=colunas_treeview, show="headings", selectmode="browse")
        self.tree_autores.heading("id_autor", text="ID")
        self.tree_autores.heading("nome", text="Nome do Autor")
        self.tree_autores.column("id_autor", width=80, anchor="center", stretch=tk.NO)
        self.tree_autores.column("nome", width=300, anchor="w")

        scrollbar_vertical = ttk.Scrollbar(frame_treeview, orient="vertical", command=self.tree_autores.yview)
        self.tree_autores.configure(yscrollcommand=scrollbar_vertical.set)
        self.tree_autores.pack(side="left", fill="both", expand=True)
        scrollbar_vertical.pack(side="right", fill="y")

        self.tree_autores.bind("<<TreeviewSelect>>", self._ao_selecionar_autor)

        self.atualizar_lista_autores() # Carrega dados iniciais na Treeview

    def atualizar_lista_autores(self):
        """Busca autores do banco e atualiza a Treeview."""
        # Limpa itens existentes na Treeview
        for item in self.tree_autores.get_children():
            self.tree_autores.delete(item)
        # Busca dados do banco (lista de tuplas)
        lista_de_autores = db.listar_autores()
        for autor_tupla in lista_de_autores:
            self.tree_autores.insert("", "end", values=autor_tupla)
        # Se a tela de livros já foi criada, atualiza seu combobox de autores
        if LivrosFrame in self.app_controller.frames:
             if self.app_controller.frames[LivrosFrame].winfo_exists():
                self.app_controller.frames[LivrosFrame].atualizar_combobox_autores()

    def _adicionar_autor(self):
        nome = self.nome_autor_var.get().strip()
        if not nome:
            messagebox.showwarning("Campo Obrigatório", "O nome do autor não pode ser vazio.")
            return

        autor_id = db.adicionar_autor(nome)
        if autor_id: # Se o ID retornado não for None (sucesso)
            messagebox.showinfo("Sucesso", f"Autor '{nome}' adicionado com ID: {autor_id}.")
            self.atualizar_lista_autores()
            self._limpar_campos_autor()
        else:
            # A função db.adicionar_autor já imprime a causa do erro no console.
            messagebox.showerror("Erro ao Adicionar", f"Não foi possível adicionar o autor '{nome}'. Verifique se já existe.")

    def _atualizar_autor(self):
        if self.id_autor_selecionado is None:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione um autor da lista para atualizar.")
            return
        novo_nome = self.nome_autor_var.get().strip()
        if not novo_nome:
            messagebox.showwarning("Campo Obrigatório", "O nome do autor não pode ser vazio.")
            return

        if db.atualizar_autor(self.id_autor_selecionado, novo_nome):
            messagebox.showinfo("Sucesso", "Autor atualizado com sucesso!")
            self.atualizar_lista_autores()
            self._limpar_campos_autor()
        else:
            messagebox.showerror("Erro ao Atualizar", f"Não foi possível atualizar o autor. Verifique se o novo nome já existe.")

    def _deletar_autor(self):
        if self.id_autor_selecionado is None:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione um autor da lista para deletar.")
            return

        nome_autor_para_deletar = self.nome_autor_var.get() # Pega o nome do campo para a mensagem
        confirmacao = messagebox.askyesno("Confirmar Exclusão",
                                          f"Tem certeza que deseja excluir o autor '{nome_autor_para_deletar}' (ID: {self.id_autor_selecionado})?\n\nATENÇÃO: Esta ação não será possível se o autor tiver livros cadastrados.")
        if confirmacao:
            if db.deletar_autor(self.id_autor_selecionado):
                messagebox.showinfo("Sucesso", "Autor excluído com sucesso!")
                self.atualizar_lista_autores()
                self._limpar_campos_autor()
            else:
                # db.deletar_autor já imprime a causa específica (IntegrityError)
                messagebox.showerror("Erro ao Excluir", "Não foi possível excluir o autor. Verifique se ele possui livros associados.")

    def _limpar_campos_autor(self):
        self.nome_autor_var.set("")
        self.id_autor_selecionado = None
        if self.tree_autores.selection(): # Remove seleção da treeview
            self.tree_autores.selection_remove(self.tree_autores.selection()[0])
        self.btn_adicionar.config(state="normal")
        self.btn_atualizar.config(state="disabled")
        self.btn_deletar.config(state="disabled")
        self.entry_nome_autor.focus()

    def _ao_selecionar_autor(self, event):
        """Chamado quando um autor é selecionado na Treeview."""
        item_selecionado_id = self.tree_autores.focus() # ID interno do item na Treeview
        if item_selecionado_id:
            valores_do_item = self.tree_autores.item(item_selecionado_id, "values")
            self.id_autor_selecionado = int(valores_do_item[0]) # ID do autor do banco
            self.nome_autor_var.set(valores_do_item[1])       # Nome do autor
            self.btn_adicionar.config(state="disabled")
            self.btn_atualizar.config(state="normal")
            self.btn_deletar.config(state="normal")
        else: # Caso a seleção seja limpa (clicar fora)
            self._limpar_campos_autor()


# --- TELA (FRAME) PARA GERENCIAMENTO DE LIVROS ---
class LivrosFrame(ttk.Frame):
    def __init__(self, parent_container, app_controller):
        super().__init__(parent_container)
        self.app_controller = app_controller
        self.id_livro_selecionado = None
        self.mapa_id_autores = {} # Mapeia Nome do Autor (string) para ID do Autor (int)

        # --- Widgets do Formulário ---
        frame_formulario = ttk.LabelFrame(self, text="Dados do Livro", padding=(15, 10))
        frame_formulario.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame_formulario, text="Título do Livro:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.titulo_livro_var = tk.StringVar()
        self.entry_titulo_livro = ttk.Entry(frame_formulario, textvariable=self.titulo_livro_var, width=50)
        self.entry_titulo_livro.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame_formulario, text="Autor:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.nome_autor_combobox_var = tk.StringVar()
        self.combobox_autores = ttk.Combobox(frame_formulario, textvariable=self.nome_autor_combobox_var, state="readonly", width=47)
        self.combobox_autores.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        frame_formulario.columnconfigure(1, weight=1)

        # --- Botões de Ação ---
        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(pady=5, padx=10, fill="x")

        self.btn_adicionar = ttk.Button(frame_botoes, text="Adicionar Livro", command=self._adicionar_livro)
        self.btn_adicionar.pack(side="left", padx=5)
        self.btn_atualizar = ttk.Button(frame_botoes, text="Atualizar Selecionado", command=self._atualizar_livro, state="disabled")
        self.btn_atualizar.pack(side="left", padx=5)
        self.btn_deletar = ttk.Button(frame_botoes, text="Deletar Selecionado", command=self._deletar_livro, state="disabled")
        self.btn_deletar.pack(side="left", padx=5)
        self.btn_limpar = ttk.Button(frame_botoes, text="Limpar Formulário", command=self._limpar_campos_livro)
        self.btn_limpar.pack(side="left", padx=5)

        # --- Grade (Treeview) para Exibir Livros ---
        frame_treeview = ttk.Frame(self)
        frame_treeview.pack(pady=10, padx=10, fill="both", expand=True)

        # Colunas exibidas: id_livro, titulo, nome_autor
        colunas_treeview = ("id_livro", "titulo", "nome_autor")
        self.tree_livros = ttk.Treeview(frame_treeview, columns=colunas_treeview, show="headings", selectmode="browse")
        self.tree_livros.heading("id_livro", text="ID Livro")
        self.tree_livros.heading("titulo", text="Título do Livro")
        self.tree_livros.heading("nome_autor", text="Nome do Autor")
        self.tree_livros.column("id_livro", width=70, anchor="center", stretch=tk.NO)
        self.tree_livros.column("titulo", width=300, anchor="w")
        self.tree_livros.column("nome_autor", width=200, anchor="w")

        scrollbar_vertical = ttk.Scrollbar(frame_treeview, orient="vertical", command=self.tree_livros.yview)
        self.tree_livros.configure(yscrollcommand=scrollbar_vertical.set)
        self.tree_livros.pack(side="left", fill="both", expand=True)
        scrollbar_vertical.pack(side="right", fill="y")

        self.tree_livros.bind("<<TreeviewSelect>>", self._ao_selecionar_livro)

        self.atualizar_combobox_autores() # Carrega autores no combobox
        self.atualizar_lista_livros()   # Carrega livros na treeview

    def atualizar_combobox_autores(self):
        """Busca autores do banco e atualiza o Combobox de autores."""
        lista_de_autores_tuplas = db.listar_autores() # Lista de (id_autor, nome_autor)
        self.mapa_id_autores.clear()
        nomes_autores_para_combobox = []
        for id_autor, nome_autor in lista_de_autores_tuplas:
            self.mapa_id_autores[nome_autor] = id_autor # Mapeia Nome para ID
            nomes_autores_para_combobox.append(nome_autor)
        self.combobox_autores['values'] = nomes_autores_para_combobox
        if nomes_autores_para_combobox:
            self.nome_autor_combobox_var.set('') # Limpa seleção atual
        else:
            self.nome_autor_combobox_var.set('')


    def atualizar_lista_livros(self):
        """Busca livros (com nome do autor) do banco e atualiza a Treeview."""
        for item in self.tree_livros.get_children():
            self.tree_livros.delete(item)
        # db.listar_livros_com_autor() retorna (id_livro, titulo, nome_autor, id_autor_fk)
        lista_de_livros_tuplas = db.listar_livros_com_autor()
        for id_l, tit, nome_a, _id_a_fk in lista_de_livros_tuplas:
            self.tree_livros.insert("", "end", values=(id_l, tit, nome_a))

    def _adicionar_livro(self):
        titulo = self.titulo_livro_var.get().strip()
        nome_autor_selecionado = self.nome_autor_combobox_var.get()

        if not titulo:
            messagebox.showwarning("Campo Obrigatório", "O título do livro não pode ser vazio.")
            return
        if not nome_autor_selecionado:
            messagebox.showwarning("Seleção Obrigatória", "Selecione um autor para o livro.")
            return

        id_autor_para_fk = self.mapa_id_autores.get(nome_autor_selecionado)
        if id_autor_para_fk is None: # Checagem de segurança
            messagebox.showerror("Erro Interno", "Autor selecionado não encontrado no mapeamento.")
            return

        livro_id = db.adicionar_livro(titulo, id_autor_para_fk)
        if livro_id:
            messagebox.showinfo("Sucesso", f"Livro '{titulo}' adicionado com ID: {livro_id}.")
            self.atualizar_lista_livros()
            self._limpar_campos_livro()
        else:
            messagebox.showerror("Erro ao Adicionar", "Não foi possível adicionar o livro.")

    def _atualizar_livro(self):
        if self.id_livro_selecionado is None:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione um livro da lista para atualizar.")
            return
        novo_titulo = self.titulo_livro_var.get().strip()
        novo_nome_autor = self.nome_autor_combobox_var.get()

        if not novo_titulo:
            messagebox.showwarning("Campo Obrigatório", "O título do livro não pode ser vazio.")
            return
        if not novo_nome_autor:
            messagebox.showwarning("Seleção Obrigatória", "Selecione um autor para o livro.")
            return

        novo_id_autor_para_fk = self.mapa_id_autores.get(novo_nome_autor)
        if novo_id_autor_para_fk is None:
            messagebox.showerror("Erro Interno", "Novo autor selecionado não encontrado no mapeamento.")
            return

        if db.atualizar_livro(self.id_livro_selecionado, novo_titulo, novo_id_autor_para_fk):
            messagebox.showinfo("Sucesso", "Livro atualizado com sucesso!")
            self.atualizar_lista_livros()
            self._limpar_campos_livro()
        else:
            messagebox.showerror("Erro ao Atualizar", "Não foi possível atualizar o livro.")

    def _deletar_livro(self):
        if self.id_livro_selecionado is None:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione um livro da lista para deletar.")
            return

        titulo_livro_para_deletar = self.titulo_livro_var.get()
        confirmacao = messagebox.askyesno("Confirmar Exclusão",
                                          f"Tem certeza que deseja excluir o livro '{titulo_livro_para_deletar}' (ID: {self.id_livro_selecionado})?")
        if confirmacao:
            if db.deletar_livro(self.id_livro_selecionado):
                messagebox.showinfo("Sucesso", "Livro excluído com sucesso!")
                self.atualizar_lista_livros()
                self._limpar_campos_livro()
            else:
                messagebox.showerror("Erro ao Excluir", "Não foi possível excluir o livro.")

    def _limpar_campos_livro(self):
        self.titulo_livro_var.set("")
        self.nome_autor_combobox_var.set("") # Limpa a seleção do combobox
        self.combobox_autores.set('')      # Limpa o texto exibido no combobox (redundante, mas seguro)
        self.id_livro_selecionado = None
        if self.tree_livros.selection(): # Remove seleção da treeview
            self.tree_livros.selection_remove(self.tree_livros.selection()[0])
        self.btn_adicionar.config(state="normal")
        self.btn_atualizar.config(state="disabled")
        self.btn_deletar.config(state="disabled")
        self.entry_titulo_livro.focus()

    def _ao_selecionar_livro(self, event):
        """Chamado quando um livro é selecionado na Treeview."""
        item_selecionado_id = self.tree_livros.focus()
        if item_selecionado_id:
            # Na Treeview de livros, os valores são (id_livro, titulo, nome_autor)
            valores_do_item = self.tree_livros.item(item_selecionado_id, "values")
            self.id_livro_selecionado = int(valores_do_item[0])
            self.titulo_livro_var.set(valores_do_item[1])
            self.nome_autor_combobox_var.set(valores_do_item[2]) # Define o nome do autor no Combobox
            self.btn_adicionar.config(state="disabled")
            self.btn_atualizar.config(state="normal")
            self.btn_deletar.config(state="normal")
        else:
            self._limpar_campos_livro()


# --- PONTO DE ENTRADA DA APLICAÇÃO ---
if __name__ == "__main__":
    app = AppBiblioteca()
    app.mainloop()