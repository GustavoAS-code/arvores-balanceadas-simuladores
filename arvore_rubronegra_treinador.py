import tkinter as tk
from tkinter import ttk, messagebox
import copy
import random

# ==============================================================================
# MOTOR CANÓNICO DA ÁRVORE RUBRO-NEGRA (LLRB - SEDGEWICK)
# ==============================================================================

RED = True
BLACK = False

class CanonicalLLRBNode:
    def __init__(self, val, color=RED):
        self.val = val
        self.color = color
        self.left = None
        self.right = None

class CanonicalLLRBTree:
    def __init__(self):
        self.root = None

    def is_red(self, node):
        if node is None:
            return False
        return node.color == RED

    def rot_left(self, h):
        x = h.right
        h.right = x.left
        x.left = h
        x.color = h.color
        h.color = RED
        return x

    def rot_right(self, h):
        x = h.left
        h.left = x.right
        x.right = h
        x.color = h.color
        h.color = RED
        return x

    def flip_colors(self, h):
        h.color = not h.color
        if h.left:
            h.left.color = not h.left.color
        if h.right:
            h.right.color = not h.right.color

    def insert(self, val):
        self.root = self._insert(self.root, val)
        if self.root:
            self.root.color = BLACK

    def _insert(self, h, val):
        if h is None:
            return CanonicalLLRBNode(val, RED)

        if val < h.val:
            h.left = self._insert(h.left, val)
        elif val > h.val:
            h.right = self._insert(h.right, val)
        else:
            return h

        # Regras LLRB
        if self.is_red(h.right) and not self.is_red(h.left):
            h = self.rot_left(h)
        if self.is_red(h.left) and self.is_red(h.left.left):
            h = self.rot_right(h)
        if self.is_red(h.left) and self.is_red(h.right):
            self.flip_colors(h)

        return h

    def _balance(self, h):
        if self.is_red(h.right) and not self.is_red(h.left):
            h = self.rot_left(h)
        if self.is_red(h.left) and self.is_red(h.left.left):
            h = self.rot_right(h)
        if self.is_red(h.left) and self.is_red(h.right):
            self.flip_colors(h)
        return h

    def _move_red_left(self, h):
        self.flip_colors(h)
        if h.right and self.is_red(h.right.left):
            h.right = self.rot_right(h.right)
            h = self.rot_left(h)
            self.flip_colors(h)
        return h

    def _move_red_right(self, h):
        self.flip_colors(h)
        if h.left and self.is_red(h.left.left):
            h = self.rot_right(h)  # Correção aplicada aqui
            self.flip_colors(h)
        return h

    def _min(self, h):
        while h.left:
            h = h.left
        return h

    def _delete_min(self, h):
        if h.left is None:
            return None
        if not self.is_red(h.left) and not (h.left and self.is_red(h.left.left)):
            h = self._move_red_left(h)
        h.left = self._delete_min(h.left)
        return self._balance(h)

    def delete(self, val):
        if self.root is None:
            return
        if not self._contains(self.root, val):
            return
        if not self.is_red(self.root.left) and not self.is_red(self.root.right):
            self.root.color = RED
        self.root = self._delete(self.root, val)
        if self.root:
            self.root.color = BLACK

    def _contains(self, h, val):
        while h:
            if val < h.val: h = h.left
            elif val > h.val: h = h.right
            else: return True
        return False

    def _delete(self, h, val):
        if h is None:
            return None
        if val < h.val:
            if h.left and not self.is_red(h.left) and not self.is_red(h.left.left):
                h = self._move_red_left(h)
            h.left = self._delete(h.left, val)
        else:
            if self.is_red(h.left):
                h = self.rot_right(h)
            if val == h.val and h.right is None:
                return None
            if h.right and not self.is_red(h.right) and not self.is_red(h.right.left):
                h = self._move_red_right(h)
            if val == h.val:
                succ = self._min(h.right)
                h.val = succ.val
                h.right = self._delete_min(h.right)
            else:
                h.right = self._delete(h.right, val)
        return self._balance(h)

# ==============================================================================
# NÓ DO USUÁRIO
# ==============================================================================

class UserRBNode:
    def __init__(self, node_id, val=None, color="P"):
        self.id = node_id
        self.val = val
        self.color = color
        self.left_id = None
        self.right_id = None

    def is_blank(self):
        return self.val is None

    def display_text(self):
        cor_tag = "P" if self.color == "P" else "V"
        val_txt = "?" if self.val is None else str(self.val)
        return f"({val_txt}) [{cor_tag}]"

# ==============================================================================
# INTERFACE GRÁFICA DA ÁRVORE RUBRO-NEGRA
# ==============================================================================

class RBTrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Treinador de Árvore Rubro-Negra (LLRB)")
        self.root.geometry("1300x880")
        self.root.minsize(1080, 720)

        self.user_nodes = {}
        self.user_root_id = None
        self.next_node_id = 1

        self.undo_stack = []
        self.redo_stack = []

        self.notepad_window = None
        self.notepad_text_content = ""

        self.canonical_tree = CanonicalLLRBTree()

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

        # 3. Painel Inferior
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
        edit_box = ttk.LabelFrame(left_frame, text="Nó Rubro-Negro (Vazio = Rascunho)", padding=6)
        edit_box.pack(fill=tk.X, pady=2)

        c_grid = ttk.Frame(edit_box)
        c_grid.pack(fill=tk.X, pady=2)
        ttk.Label(c_grid, text="Chave:").grid(row=0, column=0, sticky=tk.W)
        self.entry_val = ttk.Entry(c_grid, width=8)
        self.entry_val.grid(row=0, column=1, padx=4)

        ttk.Label(c_grid, text="Cor:").grid(row=0, column=2, sticky=tk.W, padx=4)
        self.node_color = tk.StringVar(value="P")
        col_frame = ttk.Frame(c_grid)
        col_frame.grid(row=0, column=3, sticky=tk.W)
        ttk.Radiobutton(col_frame, text="Preto", variable=self.node_color, value="P").pack(side=tk.LEFT)
        ttk.Radiobutton(col_frame, text="Vermelho", variable=self.node_color, value="V").pack(side=tk.LEFT, padx=3)

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

        # Conectar Arestas (Esq / Dir)
        link_box = ttk.LabelFrame(left_frame, text="Conectar Aresta (Pai -> Filho)", padding=6)
        link_box.pack(fill=tk.X, pady=2)

        ttk.Label(link_box, text="Nó Pai:").grid(row=0, column=0, sticky=tk.W)
        self.cb_parent = ttk.Combobox(link_box, state="readonly", width=16)
        self.cb_parent.grid(row=0, column=1, columnspan=2, pady=1, sticky=tk.W)

        ttk.Label(link_box, text="Ponteiro:").grid(row=1, column=0, sticky=tk.W)
        self.link_pos = tk.StringVar(value="esq")
        pos_frame = ttk.Frame(link_box)
        pos_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W)

        self.rb_esq = ttk.Radiobutton(pos_frame, text="Esq (< pai)", variable=self.link_pos, value="esq")
        self.rb_esq.pack(side=tk.LEFT)
        self.rb_dir = ttk.Radiobutton(pos_frame, text="Dir (> pai)", variable=self.link_pos, value="dir")
        self.rb_dir.pack(side=tk.LEFT, padx=6)

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

        # Notebook
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

        # Aba 3: Dicas Rubro-Negra LLRB
        tab_tips = ttk.Frame(self.notebook)
        self.notebook.add(tab_tips, text=" 💡 Dicas da Rubro-Negra (LLRB) ")
        self._build_rb_tips_tab(tab_tips)

    # ==============================================================================
    # ABA DE DICAS EXCLUSIVA DA LLRB
    # ==============================================================================

    def _build_rb_tips_tab(self, parent):
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

        conteudo = """GUIA RÁPIDO: ÁRVORE RUBRO-NEGRA INCLINADA À ESQUERDA (LLRB)

1. PROPRIEDADES E INVARIANTES FUNDAMENTAIS
• Todo nó é estritamente PRETO ou VERMELHO.
• A RAIZ é sempre PRETA (se no final de uma inserção ela ficar vermelha, force-a a preta).
• Todas as folhas nulas (ponteiros NULL) são consideradas PRETAS.
• SEM NÓS VERMELHOS CONSECUTIVOS: O pai de um nó vermelho é SEMPRE preto!
• ALTURA NEGRA CONSTANTE: Qualquer caminho da raiz até uma folha NULL possui o mesmo
  número exato de nós PRETOS.
• REGRA LLRB: Arestas/nós vermelhos INCLINAM-SE SEMPRE À ESQUERDA.
  (Nunca se permite um nó vermelho isolado à direita).

--------------------------------------------------------------------------------

2. INSERÇÃO (As Três Regras na Volta da Recursão)
Toda nova chave é inserida como folha com cor VERMELHA. Ao retornar da recursão,
execute estas 3 correções RIGOROSAMENTE nesta ordem:

1º) Filho DIREITO é VERMELHO e Filho ESQUERDO é PRETO:
    -> Ação: rotacionaEsquerda(H)
    -> Motivo: Corrige a inclinação, forçando a aresta vermelha para a esquerda.

2º) Filho ESQUERDO é VERMELHO e Neto ESQUERDO é VERMELHO (dois vermelhos seguidos):
    -> Ação: rotacionaDireita(H)
    -> Motivo: Desfaz a colisão de nós vermelhos consecutivos na esquerda.

3º) AMBOS os Filhos (Esquerdo e Direito) são VERMELHOS:
    -> Ação: inverteCores(H)
    -> Motivo: Equivale ao SPLIT da 2-3! Os dois filhos viram PRETO e o pai vira
      VERMELHO (para promover o elemento na subida).

* Ao final da inserção completa na raiz: raiz.cor = PRETO.

--------------------------------------------------------------------------------

3. EQUIVALÊNCIA DIRETA: ÁRVORE 2-3 <---> LLRB
Para converter sem errar:
• 2-Nó [ A |     ]  --->  Nó PRETO simples contendo a chave A.
• 3-Nó [ A | B   ]  --->  A chave MAIOR (B) vira nó PRETO no topo; a chave MENOR (A)
                          vira o filho ESQUERDO VERMELHO de B.
  - Subárvore esquerda de A (< A): entra na esquerda de A.
  - Subárvore central (entre A e B): entra na direita de A.
  - Subárvore direita (> B): entra na direita de B.

--------------------------------------------------------------------------------

4. REMOÇÃO (Conceitos Críticos)
• Se o nó a ser removido for VERMELHO:
    -> Pode ser apagado diretamente da folha sem violar a altura negra!
• Se o nó a remover estiver em Nó Interno:
    -> Troque o valor pelo SUCESSOR IMEDIATO (o menor da subárvore direita).
    -> A exclusão real é sempre resolvida em uma folha.
• Se o nó for PRETO:
    -> Gera déficit de altura negra. A LLRB usa move2EsqRED / move2DirRED na descida
      para "empurrar" uma cor vermelha até a folha a ser excluída, permitindo a exclusão
      segura e balanceando na subida com balancear(H).

--------------------------------------------------------------------------------

5. CHECKLIST DE CONFERÊNCIA ANTES DE VERIFICAR
[ ] A raiz da árvore está PRETA?
[ ] Existe algum nó VERMELHO com filho VERMELHO? (Se sim, está errado).
[ ] Existe algum nó VERMELHO isolado à direita? (Se sim, falta rotacionar à esquerda).
[ ] Altura Negra: conte os nós pretos da raiz até cada NULL. Todos os caminhos têm o mesmo total?
[ ] No simulador: não deixe nós em branco (?); preencha o valor de todos antes de verificar!
"""
        txt_tips.insert("1.0", conteudo)
        txt_tips.tag_add("TITLE", "1.0", "1.65")
        txt_tips.tag_add("SUBTITLE", "3.0", "3.45")
        txt_tips.tag_add("SUBTITLE", "15.0", "15.60")
        txt_tips.tag_add("SUBTITLE", "34.0", "34.50")
        txt_tips.tag_add("SUBTITLE", "46.0", "46.35")
        txt_tips.tag_add("SUBTITLE", "59.0", "59.48")
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
        self._log_msg(f"Sequência de {qtd} números gerada com sucesso! Gabarito LLRB processado.", "SUCCESS")

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
            self.entry_val.delete(0, tk.END)
            if node.val is not None:
                self.entry_val.insert(0, str(node.val))
            self.node_color.set(node.color)

    def _action_create_node(self):
        val_s = self.entry_val.get().strip()
        color = self.node_color.get()
        val = None

        if val_s:
            try:
                val = int(val_s)
            except ValueError:
                messagebox.showerror("Erro", "A Chave deve ser um número inteiro ou ficar vazia para rascunho.")
                return

        self._push_undo_state()

        node_id = f"N{self.next_node_id}"
        self.next_node_id += 1

        node = UserRBNode(node_id, val, color)
        self.user_nodes[node_id] = node

        if self.user_root_id is None:
            self.user_root_id = node_id

        self.entry_val.delete(0, tk.END)

        self._sync_node_selectors()
        self._redraw_user_canvas()
        if node.is_blank():
            self._log_msg(f"Nó em branco {node_id} [{color}] criado para rascunho.", "INFO")
        else:
            self._log_msg(f"Nó {node_id}: {node.display_text()} criado com sucesso.", "INFO")

    def _action_save_node_edit(self):
        sel = self.list_nodes.curselection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um nó na lista para editar.")
            return

        txt = self.list_nodes.get(sel[0])
        node_id = txt.split(":")[0].strip()

        if node_id not in self.user_nodes:
            return

        val_s = self.entry_val.get().strip()
        color = self.node_color.get()
        val = None

        if val_s:
            try:
                val = int(val_s)
            except ValueError:
                messagebox.showerror("Erro", "A Chave deve ser um número inteiro ou ficar vazia.")
                return

        self._push_undo_state()

        node = self.user_nodes[node_id]
        node.val = val
        node.color = color

        current_idx = sel[0]
        self._sync_node_selectors()
        self.list_nodes.selection_set(current_idx)
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
            if n.right_id == node_id: n.right_id = None

        if self.user_root_id == node_id:
            self.user_root_id = None

        del self.user_nodes[node_id]
        self._reindex_nodes()

        self.entry_val.delete(0, tk.END)
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

        if pos == "esq":
            new_parent.left_id = old_root
        else:
            new_parent.right_id = old_root

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

        self._push_undo_state()

        if pos == "esq":
            parent.left_id = cid
        else:
            parent.right_id = cid

        self._redraw_user_canvas()
        self._log_msg(f"Aresta conectada: {pid} apontando ({pos.upper()}) para {cid}.", "SUCCESS")

    def _action_unlink_pos(self):
        parent_s = self.cb_parent.get()
        if not parent_s:
            return
        pid = parent_s.split(":")[0].strip()
        parent = self.user_nodes[pid]
        pos = self.link_pos.get()

        self._push_undo_state()

        if pos == "esq":
            parent.left_id = None
        else:
            parent.right_id = None

        self._redraw_user_canvas()
        self._log_msg(f"Ponteiro {pos.upper()} de {pid} desligado.", "INFO")

    def _action_clear_user_tree(self):
        if not self.user_nodes:
            return
        self._push_undo_state()
        self.user_nodes.clear()
        self.user_root_id = None
        self.next_node_id = 1
        self.entry_val.delete(0, tk.END)
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

    # ==============================================================================
    # DESENHO NO CANVAS (SEM O TEXTO N1 (P) EM CIMA DAS SETAS)
    # ==============================================================================

    def _redraw_user_canvas(self):
        self.canvas_user.delete("all")
        if not self.user_nodes:
            self.canvas_user.create_text(400, 200, text="Nenhum nó criado ainda.\nCrie nós à esquerda no painel 2.",
                                         fill="#757575", font=("Segoe UI", 12))
            return

        r = 22
        node_d = 44
        y_gap = 75
        h_gap = 25

        reachable = set()
        def mark_reachable(nid):
            if not nid or nid in reachable or nid not in self.user_nodes:
                return
            reachable.add(nid)
            n = self.user_nodes[nid]
            for cid in [n.left_id, n.right_id]:
                if cid: mark_reachable(cid)

        if self.user_root_id and self.user_root_id in self.user_nodes:
            mark_reachable(self.user_root_id)

        max_y_tree = 30
        if self.user_root_id and self.user_root_id in self.user_nodes:
            class RBUserDrawNode:
                def __init__(self, u_node, user_dict):
                    self.id = u_node.id
                    self.val = u_node.val
                    self.color = u_node.color
                    self.is_blank = u_node.is_blank()

                    self.left = RBUserDrawNode(user_dict[u_node.left_id], user_dict) if (u_node.left_id and u_node.left_id in user_dict) else None
                    self.right = RBUserDrawNode(user_dict[u_node.right_id], user_dict) if (u_node.right_id and u_node.right_id in user_dict) else None

                def is_leaf(self):
                    return self.left is None and self.right is None

            root_obj = RBUserDrawNode(self.user_nodes[self.user_root_id], self.user_nodes)

            def get_w(n):
                if n is None:
                    return node_d + h_gap
                if n.is_leaf():
                    return node_d + h_gap
                w_l = get_w(n.left) if n.left else (node_d + h_gap)
                w_r = get_w(n.right) if n.right else (node_d + h_gap)
                return max(node_d + h_gap, w_l + w_r)

            coords = {}
            lines_to_draw = []

            def place(n, x_left, y):
                nonlocal max_y_tree
                tot_w = get_w(n)
                my_x = x_left + tot_w / 2
                coords[n.id] = (my_x, y, n)
                if y > max_y_tree: max_y_tree = y

                w_l = get_w(n.left) if n.left else (node_d + h_gap)
                w_r = get_w(n.right) if n.right else (node_d + h_gap)

                cur_x = x_left
                if n.left:
                    place(n.left, cur_x, y + y_gap)
                    c_x, c_y, _ = coords[n.left.id]
                    lines_to_draw.append((my_x - 12, y + r - 3, c_x, c_y - r, n.left.color))
                cur_x += w_l

                if n.right:
                    place(n.right, cur_x, y + y_gap)
                    c_x, c_y, _ = coords[n.right.id]
                    lines_to_draw.append((my_x + 12, y + r - 3, c_x, c_y - r, n.right.color))

            place(root_obj, 30, 45)

            # 1. Desenha as Arestas com destaque de cor
            for x1, y1, x2, y2, c_col in lines_to_draw:
                line_color = "#D32F2F" if c_col == "V" else "#37474F"
                line_w = 2.5 if c_col == "V" else 1.8
                self.canvas_user.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=line_w, fill=line_color, smooth=False)

            # 2. Desenha os Círculos dos Nós (sem texto no topo)
            for nid, (cx, cy, node_obj) in coords.items():
                x0, y0 = cx - r, cy - r
                x1, y1 = cx + r, cy + r

                if node_obj.is_blank:
                    fill_c = "#FFF9C4"
                    border_c = "#F57F17"
                    txt_c = "#E65100"
                    txt_val = "?"
                elif node_obj.color == "V":
                    fill_c = "#D32F2F"
                    border_c = "#B71C1C"
                    txt_c = "#FFFFFF"
                    txt_val = str(node_obj.val)
                else:
                    fill_c = "#263238"
                    border_c = "#102027"
                    txt_c = "#FFFFFF"
                    txt_val = str(node_obj.val)

                self.canvas_user.create_oval(x0, y0, x1, y1, fill=fill_c, outline=border_c, width=2)
                self.canvas_user.create_text(cx, cy, text=txt_val, font=("Consolas", 11, "bold"), fill=txt_c)

        # 3. Bancada de Nós Desconectados
        unlinked = [nid for nid in sorted(self.user_nodes.keys(), key=lambda x: int(x[1:])) if nid not in reachable]
        if unlinked:
            sep_y = max(max_y_tree + node_d + 35, 120) if self.user_root_id else 40
            self.canvas_user.create_line(20, sep_y, 800, sep_y, dash=(4, 4), fill="#B0BEC5")
            self.canvas_user.create_text(30, sep_y + 12, anchor="w",
                                         text="Nós Desconectados / Bancada (Aguardando Conexão):",
                                         font=("Segoe UI", 9, "bold italic"), fill="#546E7A")

            start_x = 60
            row_y = sep_y + 45
            for i, uid in enumerate(unlinked):
                u_node = self.user_nodes[uid]
                cx = start_x + i * (node_d + 30)
                cy = row_y
                x0, y0 = cx - r, cy - r
                x1, y1 = cx + r, cy + r

                if u_node.is_blank():
                    fill_c = "#FFF9C4"
                    border_c = "#F57F17"
                    txt_c = "#E65100"
                    txt_val = "?"
                elif u_node.color == "V":
                    fill_c = "#D32F2F"
                    border_c = "#B71C1C"
                    txt_c = "#FFFFFF"
                    txt_val = str(u_node.val)
                else:
                    fill_c = "#263238"
                    border_c = "#102027"
                    txt_c = "#FFFFFF"
                    txt_val = str(u_node.val)

                self.canvas_user.create_oval(x0, y0, x1, y1, fill=fill_c, outline=border_c, width=1.5)
                self.canvas_user.create_text(cx, cy, text=txt_val, font=("Consolas", 10, "bold"), fill=txt_c)
                self.canvas_user.create_text(cx, y1 + 10, text=f"{uid}", font=("Segoe UI", 8, "bold"), fill="#546E7A")

    def _draw_tree(self, canvas, root_node, is_canonical=False):
        canvas.delete("all")
        if root_node is None:
            canvas.create_text(400, 200, text="Árvore Vazia.", fill="#757575", font=("Segoe UI", 12))
            return

        r = 22
        node_d = 44
        y_gap = 75
        h_gap = 25

        subtree_widths = {}
        def calc_w(n):
            if n is None:
                return node_d + h_gap
            if n.left is None and n.right is None:
                w = node_d + h_gap
                subtree_widths[id(n)] = w
                return w
            w_l = calc_w(n.left) if n.left else (node_d + h_gap)
            w_r = calc_w(n.right) if n.right else (node_d + h_gap)
            w = max(node_d + h_gap, w_l + w_r)
            subtree_widths[id(n)] = w
            return w

        calc_w(root_node)

        coords = {}
        lines_to_draw = []

        def assign_coords(n, x_left, y):
            tot_w = subtree_widths[id(n)]
            my_x = x_left + tot_w / 2
            coords[id(n)] = (my_x, y, n)

            w_l = subtree_widths[id(n.left)] if n.left else (node_d + h_gap)
            w_r = subtree_widths[id(n.right)] if n.right else (node_d + h_gap)

            cur_x = x_left
            if n.left:
                assign_coords(n.left, cur_x, y + y_gap)
                c_x, c_y, _ = coords[id(n.left)]
                lines_to_draw.append((my_x - 12, y + r - 3, c_x, c_y - r, n.left.color))
            cur_x += w_l

            if n.right:
                assign_coords(n.right, cur_x, y + y_gap)
                c_x, c_y, _ = coords[id(n.right)]
                lines_to_draw.append((my_x + 12, y + r - 3, c_x, c_y - r, n.right.color))

        assign_coords(root_node, 30, 45)

        for x1, y1, x2, y2, c_col in lines_to_draw:
            line_color = "#D32F2F" if (c_col == RED or c_col == "V") else "#37474F"
            line_w = 2.5 if (c_col == RED or c_col == "V") else 1.8
            canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=line_w, fill=line_color, smooth=False)

        for obj_id, (cx, cy, node_obj) in coords.items():
            x0, y0 = cx - r, cy - r
            x1, y1 = cx + r, cy + r

            is_red_node = (node_obj.color == RED or node_obj.color == "V")
            fill_c = "#D32F2F" if is_red_node else "#263238"
            border_c = "#B71C1C" if is_red_node else "#102027"

            canvas.create_oval(x0, y0, x1, y1, fill=fill_c, outline=border_c, width=2)
            canvas.create_text(cx, cy, text=str(node_obj.val), font=("Consolas", 11, "bold"), fill="#FFFFFF")

    # ==============================================================================
    # PROCESSAMENTO E VERIFICAÇÃO
    # ==============================================================================

    def _load_default_sample(self):
        self.entry_seq.delete(0, tk.END)
        self.entry_seq.insert(0, "500, 200, 750, 150, 350, 600, 850, 250, 700, 300")
        self.entry_del.delete(0, tk.END)
        self.entry_del.insert(0, "150, 750")
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

        self.canonical_tree = CanonicalLLRBTree()
        for x in seq: self.canonical_tree.insert(x)
        for x in dels: self.canonical_tree.delete(x)

        self._update_banners()
        self._draw_tree(self.canvas_canonical, self.canonical_tree.root, is_canonical=True)
        self._log_msg("Gabarito LLRB oficial atualizado com sucesso!", "INFO")

    def _verify_trees(self):
        self.txt_feedback.delete("1.0", tk.END)

        if not self.user_root_id or self.user_root_id not in self.user_nodes:
            self._log_msg("A sua árvore está vazia! Crie os nós e defina a raiz antes de verificar.", "ERROR")
            return

        if self.canonical_tree.root is None:
            self._log_msg("Gabarito vazio. Clique primeiro em 'Processar Gabarito'.", "WARN")
            return

        # 1. Identificar nós conectados
        reachable = set()
        def mark_reachable(nid):
            if not nid or nid in reachable or nid not in self.user_nodes:
                return
            reachable.add(nid)
            n = self.user_nodes[nid]
            for cid in [n.left_id, n.right_id]:
                if cid: mark_reachable(cid)

        mark_reachable(self.user_root_id)

        # 2. BLOQUEIO DE NÓS EM BRANCO
        blank_nodes = [nid for nid in reachable if self.user_nodes[nid].is_blank()]
        if blank_nodes:
            err_msg = (f"NÓS EM BRANCO DETECTADOS: Os nós {', '.join(blank_nodes)} estão vazios (sem valor).\n"
                       f"-> Nós em branco só são permitidos como rascunho durante a construção.\n"
                       f"-> Preencha as chaves de todos os nós conectados antes de verificar.")
            self._log_msg(err_msg, "ERROR")
            messagebox.showwarning("Nós em Branco Detectados",
                                   "A sua árvore possui nós em branco (?) conectados.\n\n"
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
            for cid in [node.left_id, node.right_id]:
                if cid and cid in self.user_nodes:
                    check_cycle(cid)

        check_cycle(self.user_root_id)
        if has_cycle:
            self._log_msg("ERRO DE CICLO: Há um loop fechado na árvore. Verifique as conexões.", "ERROR")
            return

        # 4. Invariantes da Rubro-Negra
        user_root_node = self.user_nodes[self.user_root_id]
        invariant_errors = []

        if user_root_node.color != "P":
            invariant_errors.append("VIOLAÇÃO: A Raiz de uma Árvore Rubro-Negra deve ser sempre PRETA!")

        def check_rb_rules(nid):
            node = self.user_nodes[nid]
            is_red = (node.color == "V")

            l_node = self.user_nodes.get(node.left_id)
            r_node = self.user_nodes.get(node.right_id)

            if is_red:
                if l_node and l_node.color == "V":
                    invariant_errors.append(f"VIOLAÇÃO: Nós vermelhos consecutivos! {node.id} ({node.val}) e seu filho esquerdo {l_node.id} ({l_node.val}) são vermelhos.")
                if r_node and r_node.color == "V":
                    invariant_errors.append(f"VIOLAÇÃO: Nós vermelhos consecutivos! {node.id} ({node.val}) e seu filho direito {r_node.id} ({r_node.val}) são vermelhos.")

            if r_node and r_node.color == "V":
                if not l_node or l_node.color != "V":
                    invariant_errors.append(f"REGRA LLRB VIOLADA: O nó {node.id} ({node.val}) possui filho direito VERMELHO ({r_node.val}). Na LLRB, arestas vermelhas devem inclinar para a esquerda!")

            if l_node: check_rb_rules(node.left_id)
            if r_node: check_rb_rules(node.right_id)

        check_rb_rules(self.user_root_id)

        black_heights = []
        def check_bh(nid, current_bh):
            node = self.user_nodes[nid]
            bh = current_bh + (1 if node.color == "P" else 0)

            l_node = self.user_nodes.get(node.left_id)
            r_node = self.user_nodes.get(node.right_id)

            if not l_node:
                black_heights.append((f"{node.val} -> NULL_ESQ", bh))
            else:
                check_bh(node.left_id, bh)

            if not r_node:
                black_heights.append((f"{node.val} -> NULL_DIR", bh))
            else:
                check_bh(node.right_id, bh)

        check_bh(self.user_root_id, 0)
        unique_bh = set(h for _, h in black_heights)
        if len(unique_bh) > 1:
            details = ", ".join([f"{p} ({h})" for p, h in black_heights[:4]])
            invariant_errors.append(f"VIOLAÇÃO DE ALTURA NEGRA: Caminhos até NULL com contagens diferentes de nós pretos: {details}...")

        if invariant_errors:
            self._log_msg("A SUA ÁRVORE POSSUI ERROS DE INVARIANTES RUBRO-NEGRA:\n" +
                          "\n".join(f"• {e}" for e in invariant_errors), "ERROR")
            return

        # 5. Comparação Estrutural com Gabarito
        class UNodeRB:
            def __init__(self, u_node, user_dict):
                self.val = u_node.val
                self.color = u_node.color
                self.left = UNodeRB(user_dict[u_node.left_id], user_dict) if (u_node.left_id and u_node.left_id in user_dict) else None
                self.right = UNodeRB(user_dict[u_node.right_id], user_dict) if (u_node.right_id and u_node.right_id in user_dict) else None

        user_root_obj = UNodeRB(self.user_nodes[self.user_root_id], self.user_nodes)
        errors = []

        def compare_nodes(u_n, c_n, path="Raiz"):
            if c_n is None and u_n is None: return
            if u_n is None and c_n is not None:
                c_col = "V" if c_n.color == RED else "P"
                errors.append(f"Em {path}: Falta o nó esperado com valor {c_n.val} [{c_col}].")
                return
            if u_n is not None and c_n is None:
                errors.append(f"Em {path}: Nó inesperado ({u_n.val}) [{u_n.color}] foi adicionado.")
                return

            c_col = "V" if c_n.color == RED else "P"
            if u_n.val != c_n.val:
                errors.append(f"Em {path}: O nó possui valor {u_n.val}, mas deveria conter {c_n.val}.")
            if u_n.color != c_col:
                errors.append(f"Em {path} ({u_n.val}): O nó está marcado como [{u_n.color}], mas deveria ser [{c_col}].")

            if (u_n.left is None) != (c_n.left is None):
                if u_n.left: errors.append(f"Em {path} ({u_n.val}): Filho esquerdo não deveria existir.")
                else: errors.append(f"Em {path} ({u_n.val}): Falta o filho esquerdo ({c_n.left.val}).")

            if (u_n.right is None) != (c_n.right is None):
                if u_n.right: errors.append(f"Em {path} ({u_n.val}): Filho direito não deveria existir.")
                else: errors.append(f"Em {path} ({u_n.val}): Falta o filho direito ({c_n.right.val}).")

            if u_n.left and c_n.left:
                compare_nodes(u_n.left, c_n.left, f"{path} -> Esq")
            if u_n.right and c_n.right:
                compare_nodes(u_n.right, c_n.right, f"{path} -> Dir")

        compare_nodes(user_root_obj, self.canonical_tree.root, "Raiz")

        if not errors:
            self._log_msg("PARABÉNS! A sua Árvore Rubro-Negra (LLRB) está 100% CORRETA!\n"
                          "Todos os nós, chaves, cores e arestas coincidem rigorosamente com o gabarito oficial.", "SUCCESS")
        else:
            self._log_msg(f"FORAM ENCONTRADOS {len(errors)} ERRO(S) NA SUA ÁRVORE:\n" + "\n".join(f"• {e}" for e in errors), "ERROR")

    def _log_msg(self, msg, tag="INFO"):
        self.txt_feedback.delete("1.0", tk.END)
        self.txt_feedback.insert(tk.END, msg, tag)
        self.txt_feedback.see(tk.END)

# ==============================================================================
if __name__ == "__main__":
    app_window = tk.Tk()
    app = RBTrainerApp(app_window)
    app_window.mainloop()