# Treinadores Interativos de Árvores Balanceadas (2-3 e Rubro-Negra LLRB)

Aplicações interativas desktop desenvolvidas em Python (Tkinter) para estudo prático, simulação passo a passo e validação estrutural de operações em **Árvores 2-3** e **Árvores Rubro-Negras Inclinadas à Esquerda (LLRB - Left-Leaning Red-Black)**.

Projetado especificamente para fixação conceitual e treino prático voltado para avaliações e listas de exercícios da disciplina de **Estrutura de Dados II**.

---

## Funcionalidades Principais

* **Construção Manual Passo a Passo:** Crie nós, defina valores, cores e estabeleça conexões de ponteiros manualmente.
* **Suporte a Nós em Branco (Rascunho):** Permite criar nós vazios (`[ ? ]`) para esboçar o esqueleto da árvore antes de calcular e preencher os valores definitivos.
* **Motor Canônico de Gabarito Oficial:** Processa em segundo plano a árvore estritamente correta a partir de qualquer sequência de inserção e remoção fornecida.
* **Verificação Estrutural Automática:** O botão `🔍 VERIFICAR MINHA ÁRVORE` analisa:
  * Presença indevida de nós em branco conectados.
  * Detecção de ciclos/loops fechados.
  * Propriedades de balanceamento (folhas na mesma profundidade na 2-3; invariantes e altura negra constante na LLRB).
  * Confronto detalhado nó por nó contra o gabarito oficial.
* **Histórico Completo de Ações:** Suporte nativo a **Desfazer (`Ctrl + Z`)** e **Refazer (`Ctrl + Y` / `Ctrl + Shift + Z`)**.
* **Gerador Aleatório Customizado:** Gera sequências numéricas aleatórias com quantidade configurável e sugestões de remoções.
* **Aba de Dicas e Checklists:** Resumos teóricos com regras de splits, rotações, empréstimos e fusões integrados diretamente na interface.
* **Bloco de Notas Flutuante:** Janela auxiliar de anotações com opção de fixação no topo (`📌 Fixar no Topo`).

---

## Pré-requisitos

* **Python 3.8** ou superior instalado no sistema.
* Não é necessária a instalação de bibliotecas externas (utiliza apenas bibliotecas padrão do Python: `tkinter`, `random`, `copy`).

---

## Como Inicializar os Scripts

Abra o terminal (ou prompt de comando) na pasta do projeto e execute o comando correspondente:

### 1. Simulador de Árvore 2-3
```bash
python arvore23_treinador.py