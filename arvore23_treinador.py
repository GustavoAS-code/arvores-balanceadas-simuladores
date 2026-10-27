import tkinter as tk
from tkinter import ttk, messagebox
import copy
import random

# ==============================================================================
# MOTOR CANÓNICO DA ÁRVORE 2-3 (GABARITO OFICIAL)
# ==============================================================================

class CanonicalNode23:
    def __init__(self, keys, children=None):
        self.keys = list(keys)
        self.children = list(children) if children else []
        self.parent = None
        for c in self.children:
            c.parent = self

    def is_leaf(self):
        return len(self.children) == 0

class CanonicalTree23:
    def __init__(self):
        self.root = None

    def insert(self, val):
        if self.root is None:
            self.root = CanonicalNode23([val])
            return

        leaf = self._find_leaf(self.root, val)
        leaf.keys.append(val)
        leaf.keys.sort()
        self._split_and_promote(leaf)

    def _find_leaf(self, node, val):
        if node.is_leaf():
            return node
        if val < node.keys[0]:
            return self._find_leaf(node.children[0], val)
        elif len(node.keys) == 1 or val < node.keys[1]:
            return self._find_leaf(node.children[1], val)
        else:
            return self._find_leaf(node.children[2], val)

    def _split_and_promote(self, node):
        if len(node.keys) <= 2:
            return

        k1, k2, k3 = node.keys
        left_node = CanonicalNode23([k1])
        right_node = CanonicalNode23([k3])

        if not node.is_leaf():
            left_node.children = node.children[0:2]
            right_node.children = node.children[2:4]
            for c in left_node.children:
                c.parent = left_node
            for c in right_node.children:
                c.parent = right_node

        parent = node.parent
        if parent is None:
            new_root = CanonicalNode23([k2], [left_node, right_node])
            self.root = new_root
            return

        idx = parent.children.index(node)
        parent.keys.insert(idx, k2)
        parent.children.pop(idx)
        parent.children.insert(idx, right_node)
        parent.children.insert(idx, left_node)
        left_node.parent = parent
        right_node.parent = parent

        self._split_and_promote(parent)

    def delete(self, val):
        node = self._find_node(self.root, val)
        if node is None:
            return

        if not node.is_leaf():
            idx = node.keys.index(val)
            succ_node = node.children[idx + 1]
            while not succ_node.is_leaf():
                succ_node = succ_node.children[0]
            succ_val = succ_node.keys[0]
            node.keys[idx] = succ_val
            succ_node.keys.remove(succ_val)
            self._fix_underflow(succ_node)
        else:
            node.keys.remove(val)
            self._fix_underflow(node)

    def _find_node(self, node, val):
        if node is None:
            return None
        if val in node.keys:
            return node
        if node.is_leaf():
            return None
        if val < node.keys[0]:
            return self._find_node(node.children[0], val)
        elif len(node.keys) == 1 or val < node.keys[1]:
            return self._find_node(node.children[1], val)
        else:
            return self._find_node(node.children[2], val)

    def _fix_underflow(self, node):
        if len(node.keys) > 0:
            return

        if node == self.root:
            if len(node.children) > 0:
                self.root = node.children[0]
                self.root.parent = None
            else:
                self.root = None
            return

        parent = node.parent
        idx = parent.children.index(node)

        # 1. Empréstimo Esquerda
        if idx > 0 and len(parent.children[idx - 1].keys) == 2:
            left_sib = parent.children[idx - 1]
            node.keys.insert(0, parent.keys[idx - 1])
            parent.keys[idx - 1] = left_sib.keys.pop(-1)
            if not left_sib.is_leaf():
                c = left_sib.children.pop(-1)
                c.parent = node
                node.children.insert(0, c)
            return

        # 2. Empréstimo Direita
        if idx < len(parent.children) - 1 and len(parent.children[idx + 1].keys) == 2:
            right_sib = parent.children[idx + 1]
            node.keys.append(parent.keys[idx])
            parent.keys[idx] = right_sib.keys.pop(0)
            if not right_sib.is_leaf():
                c = right_sib.children.pop(0)
                c.parent = node
                node.children.append(c)
            return

        # 3. Fusão
        if idx > 0:
            left_sib = parent.children[idx - 1]
            left_sib.keys.append(parent.keys.pop(idx - 1))
            if not node.is_leaf():
                for c in node.children:
                    c.parent = left_sib
                left_sib.children.extend(node.children)
            parent.children.pop(idx)
        else:
            right_sib = parent.children[idx + 1]
            right_sib.keys.insert(0, parent.keys.pop(idx))
            if not node.is_leaf():
                for c in reversed(node.children):
                    c.parent = right_sib
                    right_sib.children.insert(0, c)
            parent.children.pop(idx)

        self._fix_underflow(parent)

# ==============================================================================
# NÓ DO USUÁRIO COM SUPORTE A NÓS EM BRANCO (RASCUNHO)
# ==============================================================================

class UserNode:
    def __init__(self, node_id, k1=None, k2=None):
        self.id = node_id
        self.k1 = k1
        self.k2 = k2
        self.left_id = None
        self.mid_id = None
        self.right_id = None

    def is_blank(self):
        return self.k1 is None

    def get_keys(self):
        if self.k1 is None:
            return []
        return [self.k1] if self.k2 is None else [self.k1, self.k2]

    def display_text(self):
        if self.k1 is None:
            return "[  ?  |      ]"
        if self.k2 is not None:
            return f"[ {self.k1} | {self.k2} ]"
        return f"[ {self.k1} |      ]"

# ==============================================================================
# INTERFACE GRÁFICA
# ==============================================================================

class Tree23TrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Treinador de Árvore 2-3 | Notação [ ch1 | ch2 ]")
        self.root.geometry("1300x880")
        self.root.minsize(1080, 720)

        self.user_nodes = {}
        self.user_root_id = None
        self.next_node_id = 1

        self.undo_stack = []
        self.redo_stack = []

        self.notepad_window = None
        self.notepad_text_content = ""

        self.canonical_tree = CanonicalTree23()

        self._setup_style()
        self._build_layout()
        self._bind_shortcuts()
        self._load_default_sample()

    def _setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))
        self.style.configure("Action.TButton", font=("Segoe UI", 10, "bold"))
        self.style.configure("TopUndo.TButton", font=("Segoe UI", 9, "bold"), foreground="#B71C1C")
        self.style.configure("TopRedo.TButton", font=("Segoe UI", 9, "bold"), foreground="#1B5E20")
        self.style.configure("Gen.TButton", font=("Segoe UI", 9, "bold"), foreground="#0D47A1")

    def _bind_shortcuts(self):
        self.root.bind_all("<Control-z>", self._shortcut_undo)
        self.root.bind_all("<Control-Z>", self._shortcut_undo)
        self.root.bind_all("<Control-y>", self._shortcut_redo)
        self.root.bind_all("<Control-Y>", self._shortcut_redo)
        self.root.bind_all("<Control-Shift-z>", self._shortcut_redo)
        self.root.bind_all("<Control-Shift-Z>", self._shortcut_redo)

    def _shortcut_undo(self, event=None):
        if event and isinstance(event.widget, (tk.Entry, ttk.Entry, tk.Text)):
            return
        self._action_undo()

    def _shortcut_redo(self, event=None):
        if event and isinstance(event.widget, (tk.Entry, ttk.Entry, tk.Text)):
            return
        self._action_redo()

    def _push_undo_state(self):
        state = {
            "nodes": copy.deepcopy(self.user_nodes),
            "root_id": self.user_root_id,
            "next_id": self.next_node_id
        }
        self.undo_stack.append(state)
        self.redo_stack.clear()
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

    def _action_undo(self, event=None):
        if not self.undo_stack:
            self._log_msg("Nenhuma ação anterior para desfazer.", "WARN")
            return

        current_state = {
            "nodes": copy.deepcopy(self.user_nodes),
            "root_id": self.user_root_id,
            "next_id": self.next_node_id
        }
        self.redo_stack.append(current_state)
        if len(self.redo_stack) > 50:
            self.redo_stack.pop(0)

        last_state = self.undo_stack.pop()
        self.user_nodes = last_state["nodes"]
        self.user_root_id = last_state["root_id"]
        self.next_node_id = last_state["next_id"]

        self._sync_node_selectors()
        self._redraw_user_canvas()
        self._log_msg("Ação desfeita com sucesso! (Ctrl+Z)", "INFO")

    def _action_redo(self, event=None):
        if not self.redo_stack:
            self._log_msg("Nenhuma ação para refazer.", "WARN")
            return

        current_state = {
            "nodes": copy.deepcopy(self.user_nodes),
            "root_id": self.user_root_id,
            "next_id": self.next_node_id
        }
        self.undo_stack.append(current_state)

        next_state = self.redo_stack.pop()
        self.user_nodes = next_state["nodes"]
        self.user_root_id = next_state["root_id"]
        self.next_node_id = next_state["next_id"]

        self._sync_node_selectors()
        self._redraw_user_canvas()
        self._log_msg("Ação refeita com sucesso! (Ctrl+Y)", "INFO")

    def _build_layout(self):
        # 1. Painel Superior
        top_frame = ttk.LabelFrame(self.root, text=" 1. Configuração do Exercício ", padding=8)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=4)

        ttk.Label(top_frame, text="Sequência:").grid(row=0, column=0, sticky=tk.W, padx=3, pady=2)
        self.entry_seq = ttk.Entry(top_frame, width=38)
        self.entry_seq.grid(row=0, column=1, padx=3, pady=2)

        ttk.Label(top_frame, text="Qtd:").grid(row=0, column=2, sticky=tk.W, padx=3, pady=2)
        self.entry_rand_count = ttk.Entry(top_frame, width=4)
        self.entry_rand_count.insert(0, "10")
        self.entry_rand_count.grid(row=0, column=3, padx=2, pady=2)

        btn_gen = ttk.Button(top_frame, text="🎲 Gerar", style="Gen.TButton", command=self._action_generate_random)
        btn_gen.grid(row=0, column=4, padx=3, pady=2)

        btn_sample = ttk.Button(top_frame, text="Exemplo Prova", command=self._load_exam_sample)
        btn_sample.grid(row=0, column=5, padx=3, pady=2)

        btn_notes = ttk.Button(top_frame, text="📝 Bloco de Notas", command=self._open_notepad)
        btn_notes.grid(row=0, column=6, padx=6, pady=2)

        ttk.Label(top_frame, text="Remoções:").grid(row=1, column=0, sticky=tk.W, padx=3, pady=2)
        self.entry_del = ttk.Entry(top_frame, width=38)
        self.entry_del.grid(row=1, column=1, padx=3, pady=2)

        btn_calc = ttk.Button(top_frame, text="Processar Gabarito", style="Action.TButton", command=self._compute_canonical)
        btn_calc.grid(row=1, column=2, columnspan=3, sticky=tk.EW, padx=3, pady=2)

        btn_top_undo = ttk.Button(top_frame, text="↶ Desfazer (Ctrl+Z)", style="TopUndo.TButton", command=self._action_undo)
        btn_top_undo.grid(row=1, column=5, sticky=tk.EW, padx=3, pady=2)

        btn_top_redo = ttk.Button(top_frame, text="↷ Refazer (Ctrl+Y)", style="TopRedo.TButton", command=self._action_redo)
        btn_top_redo.grid(row=1, column=6, sticky=tk.EW, padx=3, pady=2)

        # 3. Painel Inferior (Relatório com Scrollbar)
        bottom_frame = ttk.LabelFrame(self.root, text=" 3. Diagnóstico e Relatório de Erros ", padding=6)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=4)

        report_container = ttk.Frame(bottom_frame)
        report_container.pack(fill=tk.BOTH, expand=True)

        self.txt_feedback = tk.Text(report_container, height=5, font=("Consolas", 10), wrap=tk.WORD)
        sb_report = ttk.Scrollbar(report_container, orient=tk.VERTICAL, command=self.txt_feedback.yview)
        self.txt_feedback.config(yscrollcommand=sb_report.set)

        sb_report.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_feedback.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.txt_feedback.tag_config("SUCCESS", foreground="#2E7D32", font=("Consolas", 10, "bold"))
        self.txt_feedback.tag_config("ERROR", foreground="#C62828", font=("Consolas", 10, "bold"))
        self.txt_feedback.tag_config("WARN", foreground="#EF6C00")

        # 2. Painel Central
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=4)

        left_frame = ttk.LabelFrame(main_pane, text=" 2. Construir / Editar a Sua Árvore ", padding=6, width=380)
        main_pane.add(left_frame, weight=0)

        # Criar / Editar Nó
        edit_box = ttk.LabelFrame(left_frame, text="Valores do Nó (Deixe Vazio para Nó Branco)", padding=6)
        edit_box.pack(fill=tk.X, pady=2)

        c_grid = ttk.Frame(edit_box)
        c_grid.pack(fill=tk.X, pady=1)
        ttk.Label(c_grid, text="Chave 1:").grid(row=0, column=0, sticky=tk.W)
        self.entry_k1 = ttk.Entry(c_grid, width=7)
        self.entry_k1.grid(row=0, column=1, padx=3)

        ttk.Label(c_grid, text="Chave 2:").grid(row=0, column=2, sticky=tk.W)
        self.entry_k2 = ttk.Entry(c_grid, width=7)
        self.entry_k2.grid(row=0, column=3, padx=3)

        btn_bar = ttk.Frame(edit_box)
        btn_bar.pack(fill=tk.X, pady=2)
        btn_create = ttk.Button(btn_bar, text="+ Criar Nó (ou Branco)", command=self._action_create_node)
        btn_create.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        btn_save = ttk.Button(btn_bar, text="💾 Salvar Edição", command=self._action_save_node_edit)
        btn_save.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=1)

        # Lista de Nós
        list_box = ttk.LabelFrame(left_frame, text="Nós Criados (Clique para carregar e editar)", padding=6)
        list_box.pack(fill=tk.BOTH, expand=True, pady=2)

        self.list_nodes = tk.Listbox(list_box, height=5, font=("Consolas", 10), exportselection=False)
        self.list_nodes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_list = ttk.Scrollbar(list_box, orient=tk.VERTICAL, command=self.list_nodes.yview)
        sb_list.pack(side=tk.RIGHT, fill=tk.Y)
        self.list_nodes.config(yscrollcommand=sb_list.set)
        self.list_nodes.bind("<<ListboxSelect>>", self._on_node_selected)

        node_action_bar = ttk.Frame(left_frame)
        node_action_bar.pack(fill=tk.X, pady=2)
        btn_set_root = ttk.Button(node_action_bar, text="Definir como Raiz", command=self._action_set_root)
        btn_set_root.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        btn_del_node = ttk.Button(node_action_bar, text="Excluir Nó", command=self._action_delete_node)
        btn_del_node.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=1)

        btn_put_above = ttk.Button(left_frame, text="⬆️ Colocar Selecionado ACIMA da Raiz", command=self._action_put_above_root)
        btn_put_above.pack(fill=tk.X, pady=2)

        # Conectar Setas
        link_box = ttk.LabelFrame(left_frame, text="Conectar Seta (Pai -> Filho)", padding=6)
        link_box.pack(fill=tk.X, pady=2)

        ttk.Label(link_box, text="Nó Pai:").grid(row=0, column=0, sticky=tk.W)
        self.cb_parent = ttk.Combobox(link_box, state="readonly", width=16)
        self.cb_parent.grid(row=0, column=1, columnspan=2, pady=1, sticky=tk.W)
        self.cb_parent.bind("<<ComboboxSelected>>", self._on_parent_combo_changed)

        ttk.Label(link_box, text="Ponteiro:").grid(row=1, column=0, sticky=tk.W)
        self.link_pos = tk.StringVar(value="esq")
        pos_frame = ttk.Frame(link_box)
        pos_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W)

        self.rb_esq = ttk.Radiobutton(pos_frame, text="Esq", variable=self.link_pos, value="esq")
        self.rb_esq.pack(side=tk.LEFT)
        self.rb_mid = ttk.Radiobutton(pos_frame, text="Meio", variable=self.link_pos, value="mid")
        self.rb_mid.pack(side=tk.LEFT)
        self.rb_dir = ttk.Radiobutton(pos_frame, text="Dir", variable=self.link_pos, value="dir")
        self.rb_dir.pack(side=tk.LEFT)

        ttk.Label(link_box, text="Nó Filho:").grid(row=2, column=0, sticky=tk.W)
        self.cb_child = ttk.Combobox(link_box, state="readonly", width=16)
        self.cb_child.grid(row=2, column=1, columnspan=2, pady=1, sticky=tk.W)

        btn_link = ttk.Button(link_box, text="⬇️ Ligar Filho", command=self._action_link_nodes)
        btn_link.grid(row=3, column=0, columnspan=2, pady=3, sticky=tk.EW)
        btn_unlink = ttk.Button(link_box, text="Desligar", command=self._action_unlink_pos)
        btn_unlink.grid(row=3, column=2, pady=3, sticky=tk.EW, padx=2)

        # Botão de Verificação
        verify_frame = ttk.Frame(left_frame)
        verify_frame.pack(fill=tk.X, pady=4)
        btn_verify = tk.Button(verify_frame, text="🔍 VERIFICAR MINHA ÁRVORE", bg="#1976D2", fg="white",
                               font=("Segoe UI", 11, "bold"), relief=tk.RAISED, cursor="hand2", command=self._verify_trees)
        btn_verify.pack(fill=tk.X, ipady=4)

        btn_clear_all = ttk.Button(verify_frame, text="Limpar Minha Árvore", command=self._action_clear_user_tree)
        btn_clear_all.pack(fill=tk.X, pady=2)

        # Notebook com Canvas, Gabarito e Aba de Dicas
        notebook_frame = ttk.Frame(main_pane)
        main_pane.add(notebook_frame, weight=1)

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Aba 1: A Minha Árvore
        tab_user = ttk.Frame(self.notebook)
        self.notebook.add(tab_user, text=" A Minha Árvore (Construção) ")

        bar_info_user = ttk.Frame(tab_user, padding=5)
        bar_info_user.pack(side=tk.TOP, fill=tk.X)
        self.lbl_info_seq_user = ttk.Label(bar_info_user, text="📥 Inserção: -", font=("Segoe UI", 9, "bold"), foreground="#0D47A1")
        self.lbl_info_seq_user.pack(side=tk.LEFT, padx=6)
        self.lbl_info_del_user = ttk.Label(bar_info_user, text="🗑️ Remoções: -", font=("Segoe UI", 9, "bold"), foreground="#B71C1C")
        self.lbl_info_del_user.pack(side=tk.LEFT, padx=12)

        self.canvas_user = tk.Canvas(tab_user, bg="#F8F9FA")
        self.canvas_user.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Aba 2: Gabarito Oficial
        tab_canonical = ttk.Frame(self.notebook)
        self.notebook.add(tab_canonical, text=" Gabarito Oficial ")

        bar_info_can = ttk.Frame(tab_canonical, padding=5)
        bar_info_can.pack(side=tk.TOP, fill=tk.X)
        self.lbl_info_seq_can = ttk.Label(bar_info_can, text="📥 Inserção: -", font=("Segoe UI", 9, "bold"), foreground="#0D47A1")
        self.lbl_info_seq_can.pack(side=tk.LEFT, padx=6)
        self.lbl_info_del_can = ttk.Label(bar_info_can, text="🗑️ Remoções: -", font=("Segoe UI", 9, "bold"), foreground="#B71C1C")
        self.lbl_info_del_can.pack(side=tk.LEFT, padx=12)

        self.canvas_canonical = tk.Canvas(tab_canonical, bg="#F8F9FA")
        self.canvas_canonical.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Aba 3: Dicas Exclusivas da Árvore 2-3
        tab_tips = ttk.Frame(self.notebook)
        self.notebook.add(tab_tips, text=" 💡 Dicas da Árvore 2-3 ")
        self._build_23_tips_tab(tab_tips)

    # ==============================================================================
    # ABA DE DICAS EXCLUSIVA DA ÁRVORE 2-3
    # ==============================================================================

    def _build_23_tips_tab(self, parent):
        tips_container = ttk.Frame(parent, padding=8)
        tips_container.pack(fill=tk.BOTH, expand=True)

        txt_tips = tk.Text(tips_container, font=("Segoe UI", 10), wrap=tk.WORD, bg="#FFFFFF", padx=10, pady=10)
        sb_tips = ttk.Scrollbar(tips_container, orient=tk.VERTICAL, command=txt_tips.yview)
        txt_tips.config(yscrollcommand=sb_tips.set)

        sb_tips.pack(side=tk.RIGHT, fill=tk.Y)
        txt_tips.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        txt_tips.tag_config("TITLE", font=("Segoe UI", 12, "bold"), foreground="#0D47A1")
        txt_tips.tag_config("SUBTITLE", font=("Segoe UI", 11, "bold"), foreground="#B71C1C")
        txt_tips.tag_config("HIGHLIGHT", font=("Consolas", 10, "bold"), foreground="#1B5E20")

        conteudo = """GUIA RÁPIDO E CHECKLIST DA ÁRVORE 2-3

1. PROPRIEDADES FUNDAMENTAIS
• 2-Nó: contém exatamente 1 chave e possui 2 filhos:
    - Filho da Esquerda: valores menores que a Chave 1.
    - Filho da Direita: valores maiores que a Chave 1.
    * (O ponteiro do 'Meio' NÃO EXISTE em um 2-nó).
• 3-Nó: contém exatamente 2 chaves [ ch1 | ch2 ] e possui 3 filhos:
    - Filho da Esquerda: valores < ch1.
    - Filho do Meio: valores entre ch1 e ch2 (ch1 < x < ch2).
    - Filho da Direita: valores > ch2.
• TODAS AS FOLHAS devem estar rigorosamente no mesmo nível horizontal.
• A árvore cresce sempre DE BAIXO PARA CIMA.

--------------------------------------------------------------------------------

2. INSERÇÃO (Passo a Passo)
Toda nova chave é inserida inicialmente em uma FOLHA:
1º) Desça na árvore fazendo as comparações até encontrar a folha de destino.
2º) A folha possui espaço (é um 2-nó com 1 chave)?
    -> Apenas insira a nova chave em ordem. Ela vira um 3-nó [ menor | maior ]. FIM!
3º) A folha já tem 2 chaves (estouro / overflow com 3 valores [ A, B, C ])?
    -> Execute o SPLIT:
       - O menor valor (A) fica em um nó à Esquerda.
       - O maior valor (C) fica em um nó à Direita.
       - O valor central (B) SOBE para o nó PAI.
4º) Tratar a chegada da chave no Pai:
    - Se o Pai tinha 1 chave: ele absorve a chave B e conecta os novos nós A e C. FIM!
    - Se o Pai já tinha 2 chaves: o Pai entra em overflow e sofre split também.
    - Se o overflow atingir a RAIZ: o valor do meio sobe e cria uma NOVA RAIZ isolada.
      (A árvore aumenta a sua altura em 1 nível).

--------------------------------------------------------------------------------

3. REMOÇÃO (Passo a Passo)
Toda exclusão real deve ser resolvida em uma FOLHA:
1º) Se a chave estiver em um NÓ INTERNO:
    -> Encontre o SUCESSOR IMEDIATO (o menor valor da subárvore direita).
    -> Copie o valor do sucessor para o nó interno.
    -> O seu alvo de exclusão real passa a ser a folha de onde o sucessor saiu.
2º) Removendo da Folha:
    - Se a folha era um 3-nó (tinha 2 chaves):
      -> Basta apagar a chave. A folha continua com 1 chave. FIM!
    - Se a folha era um 2-nó (tinha 1 chave):
      -> Ao apagar, o nó fica VAZIO (Underflow / Déficit). Vá para o 3º passo.
3º) Resolvendo o Underflow (Olhe para o irmão vizinho imediato):
    • CASO A: Irmão Rico (tem 2 chaves) -> EMPRÉSTIMO / REDISTRIBUIÇÃO:
      - A chave mais próxima do irmão sobe para o pai.
      - A chave do pai desce para preencher o nó que estava vazio.
      - FIM! O déficit foi corrigido localmente.
    • CASO B: Irmão Pobre (tem 1 chave) -> FUSÃO (MERGE):
      - Junte em um único bloco: [ Irmão de 1 chave + Chave intermediária do Pai ].
      - O nó vazio é descartado. O bloco vira um 3-nó.
      - Como o Pai cedeu uma chave:
        * Se o Pai era um 3-nó: ele vira um 2-nó. FIM!
        * Se o Pai era um 2-nó: o Pai ficou vazio! Repita o 3º passo subindo para o Pai.
4º) Se o déficit atingir a RAIZ:
    - Se a raiz antiga cedeu sua única chave para uma fusão abaixo, ela é descartada.
    - O nó fundido torna-se a NOVA RAIZ (a altura da árvore diminui em 1 nível).

--------------------------------------------------------------------------------

4. CHECKLIST RÁPIDO ANTES DE FINALIZAR
[ ] Todas as folhas estão exatamente na mesma altura horizontal?
[ ] Nenhum nó final ficou vazio (0 chaves) ou com mais de 2 chaves?
[ ] Para cada nó [ A | B ]: Esquerda < A, Meio entre A e B, Direita > B?
[ ] No simulador: não deixe nós em branco (?); preencha todos antes de verificar!
"""
        txt_tips.insert("1.0", conteudo)
        txt_tips.tag_add("TITLE", "1.0", "1.50")
        txt_tips.tag_add("SUBTITLE", "3.0", "3.30")
        txt_tips.tag_add("SUBTITLE", "16.0", "16.35")
        txt_tips.tag_add("SUBTITLE", "35.0", "35.35")
        txt_tips.tag_add("SUBTITLE", "62.0", "62.45")
        txt_tips.config(state="disabled")

    # ==============================================================================
    # GERADOR ALEATÓRIO E BANNERS
    # ==============================================================================

    def _update_banners(self):
        seq_txt = self.entry_seq.get().strip()
        del_txt = self.entry_del.get().strip()

        seq_display = seq_txt if seq_txt else "(nenhuma)"
        del_display = del_txt if del_txt else "(nenhuma)"

        self.lbl_info_seq_user.config(text=f"📥 Inserção: {seq_display}")
        self.lbl_info_del_user.config(text=f"🗑️ Remoções: {del_display}")

        self.lbl_info_seq_can.config(text=f"📥 Inserção: {seq_display}")
        self.lbl_info_del_can.config(text=f"🗑️ Remoções: {del_display}")

    def _action_generate_random(self):
        qtd_s = self.entry_rand_count.get().strip()
        if not qtd_s.isdigit() or int(qtd_s) <= 0:
            messagebox.showwarning("Aviso", "Informe uma quantidade válida de números (ex: 10).")
            return
        qtd = int(qtd_s)

        pool = list(range(5, 1005, 5))
        if qtd > len(pool):
            messagebox.showwarning("Aviso", f"A quantidade máxima de números únicos é {len(pool)}.")
            return

        nums = random.sample(pool, qtd)

        self.entry_seq.delete(0, tk.END)
        self.entry_seq.insert(0, ", ".join(map(str, nums)))

        dels = random.sample(nums, min(2, len(nums)))
        self.entry_del.delete(0, tk.END)
        self.entry_del.insert(0, ", ".join(map(str, dels)))

        self._compute_canonical()
        self._log_msg(f"Sequência de {qtd} números gerada com sucesso! Gabarito processado.", "SUCCESS")

    # ==============================================================================
    # BLOCO DE NOTAS FLUTUANTE
    # ==============================================================================

    def _open_notepad(self):
        if self.notepad_window is not None and tk.Toplevel.winfo_exists(self.notepad_window):
            self.notepad_window.lift()
            self.notepad_window.focus_force()
            return

        self.notepad_window = tk.Toplevel(self.root)
        self.notepad_window.title("📝 Bloco de Notas / Anotações")
        self.notepad_window.geometry("450x420")
        self.notepad_window.minsize(320, 240)

        bar = ttk.Frame(self.notepad_window, padding=6)
        bar.pack(fill=tk.X)

        self.var_pin_note = tk.BooleanVar(value=True)
        self.notepad_window.attributes('-topmost', True)

        def toggle_pin():
            self.notepad_window.attributes('-topmost', self.var_pin_note.get())

        cb_pin = ttk.Checkbutton(bar, text="📌 Fixar no Topo", variable=self.var_pin_note, command=toggle_pin)
        cb_pin.pack(side=tk.LEFT)

        btn_clear_note = ttk.Button(bar, text="Limpar Notas", command=lambda: txt_note.delete("1.0", tk.END))
        btn_clear_note.pack(side=tk.RIGHT)

        note_frame = ttk.Frame(self.notepad_window, padding=6)
        note_frame.pack(fill=tk.BOTH, expand=True)

        txt_note = tk.Text(note_frame, font=("Segoe UI", 10), wrap=tk.WORD)
        sb_note = ttk.Scrollbar(note_frame, orient=tk.VERTICAL, command=txt_note.yview)
        txt_note.config(yscrollcommand=sb_note.set)

        sb_note.pack(side=tk.RIGHT, fill=tk.Y)
        txt_note.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        txt_note.insert("1.0", self.notepad_text_content)

        def on_close():
            self.notepad_text_content = txt_note.get("1.0", tk.END).strip()
            self.notepad_window.destroy()
            self.notepad_window = None

        self.notepad_window.protocol("WM_DELETE_WINDOW", on_close)

    # ==============================================================================
    # LÓGICA ESTRUTURAL
    # ==============================================================================

    def _on_parent_combo_changed(self, event=None):
        parent_s = self.cb_parent.get()
        if not parent_s:
            return
        pid = parent_s.split(":")[0].strip()
        if pid in self.user_nodes:
            node = self.user_nodes[pid]
            if node.k2 is None:
                self.rb_mid.config(state="disabled")
                if self.link_pos.get() == "mid":
                    self.link_pos.set("esq")
            else:
                self.rb_mid.config(state="normal")

    def _reindex_nodes(self):
        if not self.user_nodes:
            self.user_root_id = None
            self.next_node_id = 1
            return

        def get_num(nid):
            digits = "".join(c for c in nid if c.isdigit())
            return int(digits) if digits else 0

        sorted_old_ids = sorted(self.user_nodes.keys(), key=get_num)
        mapping = {old_id: f"N{i}" for i, old_id in enumerate(sorted_old_ids, start=1)}

        new_dict = {}
        for old_id, new_id in mapping.items():
            node = self.user_nodes[old_id]
            node.id = new_id
            node.left_id = mapping.get(node.left_id, None)
            node.mid_id = mapping.get(node.mid_id, None)
            node.right_id = mapping.get(node.right_id, None)
            new_dict[new_id] = node

        self.user_nodes = new_dict
        self.user_root_id = mapping.get(self.user_root_id, None)
        self.next_node_id = len(self.user_nodes) + 1

    def _on_node_selected(self, event=None):
        sel = self.list_nodes.curselection()
        if not sel:
            return
        txt = self.list_nodes.get(sel[0])
        node_id = txt.split(":")[0].strip()

        if node_id in self.user_nodes:
            node = self.user_nodes[node_id]
            self.entry_k1.delete(0, tk.END)
            if node.k1 is not None:
                self.entry_k1.insert(0, str(node.k1))
            self.entry_k2.delete(0, tk.END)
            if node.k2 is not None:
                self.entry_k2.insert(0, str(node.k2))

    def _action_create_node(self):
        k1_s = self.entry_k1.get().strip()
        k2_s = self.entry_k2.get().strip()

        k1, k2 = None, None

        if k1_s:
            try:
                k1 = int(k1_s)
            except ValueError:
                messagebox.showerror("Erro", "A Chave 1 deve ser um número inteiro ou ficar em branco.")
                return

        if k2_s:
            try:
                k2 = int(k2_s)
            except ValueError:
                messagebox.showerror("Erro", "A Chave 2 deve ser um número inteiro ou ficar em branco.")
                return

        if k1 is not None and k2 is not None:
            if k1 > k2:
                k1, k2 = k2, k1
        elif k1 is None and k2 is not None:
            k1 = k2
            k2 = None

        self._push_undo_state()

        node_id = f"N{self.next_node_id}"
        self.next_node_id += 1

        node = UserNode(node_id, k1, k2)
        self.user_nodes[node_id] = node

        if self.user_root_id is None:
            self.user_root_id = node_id

        self.entry_k1.delete(0, tk.END)
        self.entry_k2.delete(0, tk.END)

        self._sync_node_selectors()
        self._redraw_user_canvas()
        if node.is_blank():
            self._log_msg(f"Nó em branco {node_id} criado para rascunho de estrutura.", "INFO")
        else:
            self._log_msg(f"Nó {node_id} criado: {node.display_text()}", "INFO")

    def _action_save_node_edit(self):
        sel = self.list_nodes.curselection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um nó na lista para editar.")
            return

        txt = self.list_nodes.get(sel[0])
        node_id = txt.split(":")[0].strip()

        if node_id not in self.user_nodes:
            return

        k1_s = self.entry_k1.get().strip()
        k2_s = self.entry_k2.get().strip()

        k1, k2 = None, None

        if k1_s:
            try:
                k1 = int(k1_s)
            except ValueError:
                messagebox.showerror("Erro", "A Chave 1 deve ser um número inteiro ou ficar em branco.")
                return

        if k2_s:
            try:
                k2 = int(k2_s)
            except ValueError:
                messagebox.showerror("Erro", "A Chave 2 deve ser um número inteiro ou ficar em branco.")
                return

        if k1 is not None and k2 is not None:
            if k1 > k2:
                k1, k2 = k2, k1
        elif k1 is None and k2 is not None:
            k1 = k2
            k2 = None

        self._push_undo_state()

        node = self.user_nodes[node_id]
        node.k1 = k1
        node.k2 = k2

        if node.k2 is None and node.mid_id is not None:
            node.mid_id = None

        current_idx = sel[0]
        self._sync_node_selectors()
        self.list_nodes.selection_set(current_idx)
        self._on_parent_combo_changed()
        self._redraw_user_canvas()
        self._log_msg(f"Nó {node_id} atualizado para {node.display_text()}", "INFO")

    def _action_delete_node(self):
        sel = self.list_nodes.curselection()
        if not sel:
            return
        txt = self.list_nodes.get(sel[0])
        node_id = txt.split(":")[0].strip()

        self._push_undo_state()

        for nid, n in self.user_nodes.items():
            if n.left_id == node_id: n.left_id = None
            if n.mid_id == node_id: n.mid_id = None
            if n.right_id == node_id: n.right_id = None

        if self.user_root_id == node_id:
            self.user_root_id = None

        del self.user_nodes[node_id]
        self._reindex_nodes()

        self.entry_k1.delete(0, tk.END)
        self.entry_k2.delete(0, tk.END)
        self._sync_node_selectors()
        self._redraw_user_canvas()
        self._log_msg("Nó excluído com sucesso.", "INFO")

    def _action_set_root(self):
        sel = self.list_nodes.curselection()
        if not sel:
            return
        txt = self.list_nodes.get(sel[0])
        node_id = txt.split(":")[0].strip()

        self._push_undo_state()
        self.user_root_id = node_id
        self._sync_node_selectors()
        self._redraw_user_canvas()
        self._log_msg(f"{node_id} definido como Raiz da árvore.", "INFO")

    def _action_put_above_root(self):
        sel = self.list_nodes.curselection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione na lista o nó que deseja colocar acima da raiz.")
            return

        txt = self.list_nodes.get(sel[0])
        node_id = txt.split(":")[0].strip()

        if not self.user_root_id or self.user_root_id not in self.user_nodes:
            self._push_undo_state()
            self.user_root_id = node_id
            self._sync_node_selectors()
            self._redraw_user_canvas()
            return

        old_root = self.user_root_id
        if node_id == old_root:
            messagebox.showinfo("Aviso", "Este nó já é a raiz atual.")
            return

        self._push_undo_state()

        new_parent = self.user_nodes[node_id]
        pos = self.link_pos.get()
        if pos == "mid" and new_parent.k2 is None:
            pos = "esq"

        if pos == "esq": new_parent.left_id = old_root
        elif pos == "mid": new_parent.mid_id = old_root
        elif pos == "dir": new_parent.right_id = old_root

        self.user_root_id = node_id
        self._sync_node_selectors()
        self._redraw_user_canvas()
        self._log_msg(f"{node_id} colocado ACIMA como nova Raiz.", "SUCCESS")

    def _action_link_nodes(self):
        parent_s = self.cb_parent.get()
        child_s = self.cb_child.get()
        if not parent_s or not child_s:
            messagebox.showwarning("Aviso", "Selecione o Pai e o Filho.")
            return

        pid = parent_s.split(":")[0].strip()
        cid = child_s.split(":")[0].strip()

        if pid == cid:
            messagebox.showerror("Erro", "Um nó não pode ser filho dele próprio.")
            return

        parent = self.user_nodes[pid]
        pos = self.link_pos.get()

        if pos == "mid" and parent.k2 is None:
            messagebox.showwarning("Atenção", "O ponteiro Meio é reservado para nós de 2 chaves [ ch1 | ch2 ].")
            return

        self._push_undo_state()

        if pos == "esq": parent.left_id = cid
        elif pos == "mid": parent.mid_id = cid
        elif pos == "dir": parent.right_id = cid

        self._redraw_user_canvas()
        self._log_msg(f"Seta ligada: {pid} apontando ({pos.upper()}) para {cid}.", "SUCCESS")

    def _action_unlink_pos(self):
        parent_s = self.cb_parent.get()
        if not parent_s:
            return
        pid = parent_s.split(":")[0].strip()
        parent = self.user_nodes[pid]
        pos = self.link_pos.get()

        self._push_undo_state()

        if pos == "esq": parent.left_id = None
        elif pos == "mid": parent.mid_id = None
        elif pos == "dir": parent.right_id = None

        self._redraw_user_canvas()
        self._log_msg(f"Ponteiro {pos.upper()} de {pid} desligado.", "INFO")

    def _action_clear_user_tree(self):
        if not self.user_nodes:
            return
        self._push_undo_state()
        self.user_nodes.clear()
        self.user_root_id = None
        self.next_node_id = 1
        self.entry_k1.delete(0, tk.END)
        self.entry_k2.delete(0, tk.END)
        self._sync_node_selectors()
        self._redraw_user_canvas()
        self.txt_feedback.delete("1.0", tk.END)
        self._log_msg("Árvore limpa. Pode recomeçar ou pressionar Ctrl+Z.", "INFO")

    def _sync_node_selectors(self):
        self.list_nodes.delete(0, tk.END)
        options = []
        for nid, n in sorted(self.user_nodes.items(), key=lambda x: int(x[0][1:])):
            prefix = "(RAIZ) " if nid == self.user_root_id else ""
            desc = f"{nid}: {prefix}{n.display_text()}"
            self.list_nodes.insert(tk.END, desc)
            options.append(f"{nid}: {n.display_text()}")

        self.cb_parent['values'] = options
        self.cb_child['values'] = options

        if options:
            if not self.cb_parent.get() in options:
                self.cb_parent.current(0)
            if not self.cb_child.get() in options:
                self.cb_child.current(min(1, len(options) - 1))
        self._on_parent_combo_changed()

    # ==============================================================================
    # DESENHO NO CANVAS
    # ==============================================================================

    def _redraw_user_canvas(self):
        self.canvas_user.delete("all")
        if not self.user_nodes:
            self.canvas_user.create_text(400, 200, text="Nenhum nó criado ainda.\nCrie nós à esquerda no painel 2.",
                                         fill="#757575", font=("Segoe UI", 12))
            return

        box_w, box_h, y_gap, h_gap = 110, 36, 75, 25

        reachable = set()
        def mark_reachable(nid):
            if not nid or nid in reachable or nid not in self.user_nodes:
                return
            reachable.add(nid)
            n = self.user_nodes[nid]
            for cid in [n.left_id, n.mid_id, n.right_id]:
                if cid: mark_reachable(cid)

        if self.user_root_id and self.user_root_id in self.user_nodes:
            mark_reachable(self.user_root_id)

        max_y_tree = 30
        if self.user_root_id and self.user_root_id in self.user_nodes:
            class FixedSlotDrawNode:
                def __init__(self, u_node, user_dict):
                    self.id = u_node.id
                    self.keys = u_node.get_keys()
                    self.is_blank = u_node.is_blank()
                    self.is_2node = (u_node.k2 is None)

                    self.left = FixedSlotDrawNode(user_dict[u_node.left_id], user_dict) if (u_node.left_id and u_node.left_id in user_dict) else None
                    self.mid = FixedSlotDrawNode(user_dict[u_node.mid_id], user_dict) if (not self.is_2node and u_node.mid_id and u_node.mid_id in user_dict) else None
                    self.right = FixedSlotDrawNode(user_dict[u_node.right_id], user_dict) if (u_node.right_id and u_node.right_id in user_dict) else None

                def is_leaf(self):
                    return self.left is None and self.mid is None and self.right is None

            root_obj = FixedSlotDrawNode(self.user_nodes[self.user_root_id], self.user_nodes)

            def get_w(n):
                if n is None:
                    return box_w + h_gap
                if n.is_leaf():
                    return box_w + h_gap
                if n.is_2node:
                    w_l = get_w(n.left) if n.left else (box_w + h_gap)
                    w_r = get_w(n.right) if n.right else (box_w + h_gap)
                    return max(box_w + h_gap, w_l + w_r)
                else:
                    w_l = get_w(n.left) if n.left else (box_w + h_gap)
                    w_m = get_w(n.mid) if n.mid else (box_w + h_gap)
                    w_r = get_w(n.right) if n.right else (box_w + h_gap)
                    return max(box_w + h_gap, w_l + w_m + w_r)

            coords = {}
            lines_to_draw = []

            def place(n, x_left, y):
                nonlocal max_y_tree
                tot_w = get_w(n)
                my_x = x_left + tot_w / 2
                coords[n.id] = (my_x, y, n)
                if y > max_y_tree: max_y_tree = y

                y_anchor = y + box_h / 2
                p_left_anchor = (my_x - box_w * 0.25, y_anchor)
                p_mid_anchor = (my_x, y_anchor)
                p_right_anchor = (my_x + box_w * 0.25, y_anchor)

                if n.is_2node:
                    w_l = get_w(n.left) if n.left else (box_w + h_gap)
                    w_r = get_w(n.right) if n.right else (box_w + h_gap)
                    cur_x = x_left
                    if n.left:
                        place(n.left, cur_x, y + y_gap)
                        c_x, c_y, _ = coords[n.left.id]
                        lines_to_draw.append((p_left_anchor[0], p_left_anchor[1], c_x, c_y - box_h / 2))
                    cur_x += w_l

                    if n.right:
                        place(n.right, cur_x, y + y_gap)
                        c_x, c_y, _ = coords[n.right.id]
                        lines_to_draw.append((p_right_anchor[0], p_right_anchor[1], c_x, c_y - box_h / 2))
                else:
                    w_l = get_w(n.left) if n.left else (box_w + h_gap)
                    w_m = get_w(n.mid) if n.mid else (box_w + h_gap)
                    w_r = get_w(n.right) if n.right else (box_w + h_gap)

                    cur_x = x_left
                    if n.left:
                        place(n.left, cur_x, y + y_gap)
                        c_x, c_y, _ = coords[n.left.id]
                        lines_to_draw.append((p_left_anchor[0], p_left_anchor[1], c_x, c_y - box_h / 2))
                    cur_x += w_l

                    if n.mid:
                        place(n.mid, cur_x, y + y_gap)
                        c_x, c_y, _ = coords[n.mid.id]
                        lines_to_draw.append((p_mid_anchor[0], p_mid_anchor[1], c_x, c_y - box_h / 2))
                    cur_x += w_m

                    if n.right:
                        place(n.right, cur_x, y + y_gap)
                        c_x, c_y, _ = coords[n.right.id]
                        lines_to_draw.append((p_right_anchor[0], p_right_anchor[1], c_x, c_y - box_h / 2))

            place(root_obj, 30, 45)

            for x1, y1, x2, y2 in lines_to_draw:
                self.canvas_user.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=1.8, fill="#37474F", smooth=False)

            for nid, (cx, cy, node_obj) in coords.items():
                x0, y0 = cx - box_w / 2, cy - box_h / 2
                x1, y1 = cx + box_w / 2, cy + box_h / 2

                bg_col = "#FFF9C4" if node_obj.is_blank else "#E3F2FD"
                border_col = "#F57F17" if node_obj.is_blank else "#1565C0"

                self.canvas_user.create_text(cx, y0 - 8, text=node_obj.id, font=("Segoe UI", 8, "bold"), fill=border_col)
                self.canvas_user.create_rectangle(x0, y0, x1, y1, fill=bg_col, outline=border_col, width=2)
                self.canvas_user.create_line(cx, y0, cx, y1, fill=border_col, width=1.5)

                if node_obj.is_blank:
                    self.canvas_user.create_text(x0 + box_w * 0.25, cy, text="?", font=("Consolas", 11, "bold"), fill="#F57F17")
                elif len(node_obj.keys) == 1:
                    self.canvas_user.create_text(x0 + box_w * 0.25, cy, text=str(node_obj.keys[0]), font=("Consolas", 11, "bold"), fill="#212121")
                elif len(node_obj.keys) == 2:
                    self.canvas_user.create_text(x0 + box_w * 0.25, cy, text=str(node_obj.keys[0]), font=("Consolas", 11, "bold"), fill="#212121")
                    self.canvas_user.create_text(x0 + box_w * 0.75, cy, text=str(node_obj.keys[1]), font=("Consolas", 11, "bold"), fill="#212121")

        unlinked = [nid for nid in sorted(self.user_nodes.keys(), key=lambda x: int(x[1:])) if nid not in reachable]
        if unlinked:
            sep_y = max(max_y_tree + box_h + 35, 120) if self.user_root_id else 40
            self.canvas_user.create_line(20, sep_y, 800, sep_y, dash=(4, 4), fill="#B0BEC5")
            self.canvas_user.create_text(30, sep_y + 12, anchor="w",
                                         text="Nós Desconectados / Bancada (Aguardando Conexão):",
                                         font=("Segoe UI", 9, "bold italic"), fill="#546E7A")

            start_x = 75
            row_y = sep_y + 45
            for i, uid in enumerate(unlinked):
                u_node = self.user_nodes[uid]
                cx = start_x + i * (box_w + 25)
                cy = row_y
                x0, y0 = cx - box_w / 2, cy - box_h / 2
                x1, y1 = cx + box_w / 2, cy + box_h / 2

                bg_c = "#FFF9C4" if u_node.is_blank() else "#ECEFF1"
                bdr_c = "#F57F17" if u_node.is_blank() else "#78909C"

                self.canvas_user.create_text(cx, y0 - 8, text=uid, font=("Segoe UI", 8, "bold"), fill=bdr_c)
                self.canvas_user.create_rectangle(x0, y0, x1, y1, fill=bg_c, outline=bdr_c, width=1.5)
                self.canvas_user.create_line(cx, y0, cx, y1, fill=bdr_c, width=1)

                keys = u_node.get_keys()
                if u_node.is_blank():
                    self.canvas_user.create_text(x0 + box_w * 0.25, cy, text="?", font=("Consolas", 10, "bold"), fill="#F57F17")
                elif len(keys) == 1:
                    self.canvas_user.create_text(x0 + box_w * 0.25, cy, text=str(keys[0]), font=("Consolas", 10, "bold"), fill="#37474F")
                else:
                    self.canvas_user.create_text(x0 + box_w * 0.25, cy, text=str(keys[0]), font=("Consolas", 10, "bold"), fill="#37474F")
                    self.canvas_user.create_text(x0 + box_w * 0.75, cy, text=str(keys[1]), font=("Consolas", 10, "bold"), fill="#37474F")

    def _draw_tree(self, canvas, root_node, is_canonical=False):
        canvas.delete("all")
        if root_node is None:
            canvas.create_text(400, 200, text="Árvore Vazia.", fill="#757575", font=("Segoe UI", 12))
            return

        box_w, box_h, y_gap = 110, 36, 75
        subtree_widths = {}
        def calc_w(n):
            if not n or n.is_leaf():
                w = box_w + 30
                subtree_widths[id(n)] = w
                return w
            w_sum = sum(calc_w(c) for c in n.children)
            w = max(box_w + 30, w_sum)
            subtree_widths[id(n)] = w
            return w

        calc_w(root_node)
        coords = {}
        def assign_coords(n, x_left, y):
            tot_w = subtree_widths[id(n)]
            my_x = x_left + tot_w / 2
            coords[id(n)] = (my_x, y)
            cur_x = x_left
            for c in n.children:
                c_w = subtree_widths[id(c)]
                assign_coords(c, cur_x, y + y_gap)
                cur_x += c_w

        assign_coords(root_node, 30, 45)

        def draw_lines(n):
            px, py = coords[id(n)]
            c_count = len(n.children)
            for i, c in enumerate(n.children):
                cx, cy = coords[id(c)]
                if c_count == 2:
                    p_anchor_x = px - box_w * 0.25 if i == 0 else px + box_w * 0.25
                elif c_count == 3:
                    p_anchor_x = px - box_w * 0.25 if i == 0 else (px if i == 1 else px + box_w * 0.25)
                else:
                    p_anchor_x = px

                canvas.create_line(p_anchor_x, py + box_h / 2, cx, cy - box_h / 2,
                                   arrow=tk.LAST, width=1.5, fill="#37474F", smooth=False)
                draw_lines(c)

        draw_lines(root_node)

        box_color = "#E8F5E9" if is_canonical else "#E3F2FD"
        border_color = "#2E7D32" if is_canonical else "#1565C0"

        def draw_boxes(n):
            cx, cy = coords[id(n)]
            x0, y0 = cx - box_w / 2, cy - box_h / 2
            x1, y1 = cx + box_w / 2, cy + box_h / 2

            canvas.create_rectangle(x0, y0, x1, y1, fill=box_color, outline=border_color, width=2)
            canvas.create_line(cx, y0, cx, y1, fill=border_color, width=1.5)

            if len(n.keys) == 1:
                canvas.create_text(x0 + box_w * 0.25, cy, text=str(n.keys[0]), font=("Consolas", 11, "bold"), fill="#212121")
            elif len(n.keys) == 2:
                canvas.create_text(x0 + box_w * 0.25, cy, text=str(n.keys[0]), font=("Consolas", 11, "bold"), fill="#212121")
                canvas.create_text(x0 + box_w * 0.75, cy, text=str(n.keys[1]), font=("Consolas", 11, "bold"), fill="#212121")

            for c in n.children:
                draw_boxes(c)

        draw_boxes(root_node)

    # ==============================================================================
    # PROCESSAMENTO E VERIFICAÇÃO COM BLOQUEIO DE NÓS EM BRANCO
    # ==============================================================================

    def _load_default_sample(self):
        self.entry_seq.delete(0, tk.END)
        self.entry_seq.insert(0, "400, 250, 600, 150, 300, 500, 700, 180, 350, 550")
        self.entry_del.delete(0, tk.END)
        self.entry_del.insert(0, "400, 700")
        self._compute_canonical()

    def _load_exam_sample(self):
        self.entry_seq.delete(0, tk.END)
        self.entry_seq.insert(0, "320, 335, 200, 245, 500, 300, 555, 465, 530, 525")
        self.entry_del.delete(0, tk.END)
        self.entry_del.insert(0, "320, 200")
        self._compute_canonical()

    def _parse_list(self, text):
        items = []
        for p in text.replace(";", ",").split(","):
            p = p.strip()
            if p:
                try: items.append(int(p))
                except ValueError: pass
        return items

    def _compute_canonical(self):
        seq = self._parse_list(self.entry_seq.get())
        dels = self._parse_list(self.entry_del.get())

        if not seq:
            messagebox.showwarning("Aviso", "Insira pelo menos um número para a sequência.")
            return

        self.canonical_tree = CanonicalTree23()
        for x in seq: self.canonical_tree.insert(x)
        for x in dels: self.canonical_tree.delete(x)

        self._update_banners()
        self._draw_tree(self.canvas_canonical, self.canonical_tree.root, is_canonical=True)
        self._log_msg("Gabarito oficial atualizado com sucesso!", "INFO")

    def _verify_trees(self):
        self.txt_feedback.delete("1.0", tk.END)

        if not self.user_root_id or self.user_root_id not in self.user_nodes:
            self._log_msg("A sua árvore está vazia! Crie os nós e defina a raiz antes de verificar.", "ERROR")
            return

        if self.canonical_tree.root is None:
            self._log_msg("Gabarito vazio. Clique primeiro em 'Processar Gabarito'.", "WARN")
            return

        # 1. Identificar todos os nós conectados à árvore
        reachable = set()
        def mark_reachable(nid):
            if not nid or nid in reachable or nid not in self.user_nodes:
                return
            reachable.add(nid)
            n = self.user_nodes[nid]
            for cid in [n.left_id, n.mid_id, n.right_id]:
                if cid: mark_reachable(cid)

        mark_reachable(self.user_root_id)

        # 2. BLOQUEIO DE NÓS EM BRANCO NA VERIFICAÇÃO
        blank_nodes = [nid for nid in reachable if self.user_nodes[nid].is_blank()]
        if blank_nodes:
            err_msg = (f"NÓS EM BRANCO DETECTADOS: Os nós {', '.join(blank_nodes)} estão vazios (sem chaves).\n"
                       f"-> Nós em branco só são permitidos como rascunho durante a construção.\n"
                       f"-> Preencha as chaves de todos os nós conectados antes de verificar.")
            self._log_msg(err_msg, "ERROR")
            messagebox.showwarning("Nós em Branco Detectados",
                                   "A sua árvore possui nós em branco [ ? ] conectados.\n\n"
                                   "Nós em branco só podem existir durante a construção!\n"
                                   "Preencha todos os nós antes de validar.")
            return

        # 3. Verificação de Ciclos
        visited = set()
        has_cycle = False
        def check_cycle(nid):
            nonlocal has_cycle
            if nid in visited:
                has_cycle = True
                return
            visited.add(nid)
            node = self.user_nodes[nid]
            for cid in [node.left_id, node.mid_id, node.right_id]:
                if cid and cid in self.user_nodes:
                    check_cycle(cid)

        check_cycle(self.user_root_id)
        if has_cycle:
            self._log_msg("ERRO DE CICLO: Há um loop fechado na árvore. Verifique as conexões.", "ERROR")
            return

        # 4. Todas as Folhas no Mesmo Nível
        leaf_depths = []
        def check_leaves(nid, depth):
            node = self.user_nodes[nid]
            children = [c for c in [node.left_id, node.mid_id, node.right_id] if c and c in self.user_nodes]
            if not children:
                leaf_depths.append((nid, node.display_text(), depth))
            else:
                for c in children:
                    check_leaves(c, depth + 1)

        check_leaves(self.user_root_id, 0)
        depths = set(d for _, _, d in leaf_depths)
        if len(depths) > 1:
            err_details = ", ".join([f"{txt} no nível {d}" for _, txt, d in leaf_depths])
            self._log_msg(f"ERRO DE BALANCEAMENTO: Todas as folhas têm de estar rigorosamente no mesmo nível!\n"
                          f"-> Folhas em alturas diferentes: {err_details}.", "ERROR")
            return

        # 5. Comparação Estrutural com o Gabarito Oficial
        class UNodeC:
            def __init__(self, u_node, user_dict):
                self.keys = u_node.get_keys()
                self.children = []
                order = [u_node.left_id, u_node.right_id] if len(self.keys) == 1 else [u_node.left_id, u_node.mid_id, u_node.right_id]
                for cid in order:
                    if cid and cid in user_dict:
                        self.children.append(UNodeC(user_dict[cid], user_dict))

        user_root = UNodeC(self.user_nodes[self.user_root_id], self.user_nodes)
        errors = []

        def compare_nodes(u_n, c_n, path="Raiz"):
            if c_n is None and u_n is None: return
            if u_n is None and c_n is not None:
                errors.append(f"Em {path}: Falta o nó esperado com chaves {c_n.keys}.")
                return
            if u_n is not None and c_n is None:
                errors.append(f"Em {path}: Nó inesperado com chaves {u_n.keys} foi adicionado.")
                return

            if u_n.keys != c_n.keys:
                errors.append(f"Em {path}: O nó possui chaves {u_n.keys}, mas deveria conter {c_n.keys}.")

            u_c_count = len(u_n.children)
            c_c_count = len(c_n.children)

            if u_c_count != c_c_count:
                errors.append(f"Em {path} {u_n.keys}: Tem {u_c_count} filho(s) ligado(s), mas deveria ter {c_c_count}.")

            min_c = min(u_c_count, c_c_count)
            labels = ["Filho Esquerdo", "Filho Direito"] if c_c_count == 2 else ["Filho Esquerdo", "Filho do Meio", "Filho Direito"]
            for i in range(min_c):
                lbl = labels[i] if i < len(labels) else f"Filho {i+1}"
                compare_nodes(u_n.children[i], c_n.children[i], f"{path} -> {lbl}")

        compare_nodes(user_root, self.canonical_tree.root, "Raiz")

        if not errors:
            self._log_msg("PARABÉNS! A sua Árvore 2-3 está 100% CORRETA!\n"
                          "Todos os nós, chaves, ponteiros e níveis coincidem rigorosamente com o gabarito.", "SUCCESS")
        else:
            self._log_msg(f"FORAM ENCONTRADOS {len(errors)} ERRO(S) NA SUA ÁRVORE:\n" + "\n".join(f"• {e}" for e in errors), "ERROR")

    def _log_msg(self, msg, tag="INFO"):
        self.txt_feedback.delete("1.0", tk.END)
        self.txt_feedback.insert(tk.END, msg, tag)
        self.txt_feedback.see(tk.END)

# ==============================================================================
if __name__ == "__main__":
    app_window = tk.Tk()
    app = Tree23TrainerApp(app_window)
    app_window.mainloop()