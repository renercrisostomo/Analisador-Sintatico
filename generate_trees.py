from __future__ import annotations
from typing import List, Optional, Union, Any, Tuple, Dict
import os
from dataclasses import is_dataclass

# Importar o parser e os casos de teste
from parcer import parse, Token, Program, Let, Assign, If, While, Return, Block, BinOp, Var, Num, Bool, Call, Index

# -----------------------------------------------------------
# Visualizador de AST genérico (adaptado do notebook)
# -----------------------------------------------------------

try:
    import matplotlib.pyplot as plt
    HAVE_MPL = True
except ImportError:
    HAVE_MPL = False

NodeLike = Any  # aceitamos qualquer objeto com atributos esperados

# ----------------------------
# Rótulo amigável para cada nó
# ----------------------------
def node_label(n: NodeLike) -> str:
    tname = type(n).__name__
    # Casos da nossa AST:
    if tname == "Program": return "Program"
    if tname == "Let":     return "Let"
    if tname == "Assign":  return "Assign"
    if tname == "If":      return "If"
    if tname == "While":   return "While"
    if tname == "Return":  return "Return"
    if tname == "Block":   return "Block"
    if tname == "Call":    return "Call"
    if tname == "Index":   return "Index"
    if tname == "BinOp":   return f"BinOp('{getattr(n, 'op', '?')}')"
    if tname == "Var":     return f"Id({getattr(n, 'name', '?')})"
    if tname == "Num":     return f"Num({getattr(n, 'value', '?')})"
    if tname == "Bool":
        v = getattr(n, "value", None)
        return f"Bool({str(v).lower()})" if isinstance(v, bool) else "Bool(?)"
    # Fallback genérico:
    return tname

# ----------------------------------------
# Lista de filhos (adaptado para nossa AST)
# ----------------------------------------
def children(n: NodeLike) -> List[NodeLike]:
    tname = type(n).__name__
    # Mapeamento pelos atributos usados na nossa AST
    if tname == "Program": return list(getattr(n, "body", []))
    if tname == "Let":     return [getattr(n, "target", None), getattr(n, "init", None)]
    if tname == "Assign":  return [getattr(n, "target", None), getattr(n, "value", None)]
    if tname == "If":
        lst = [getattr(n, "test", None), getattr(n, "then", None)]
        other = getattr(n, "otherwise", None)
        if other is not None: lst.append(other)
        return lst
    if tname == "While":   return [getattr(n, "test", None), getattr(n, "body", None)]
    if tname == "Return":
        v = getattr(n, "value", None)
        return [v] if v is not None else []
    if tname == "Block":   return list(getattr(n, "body", []))
    if tname == "Call":    return [getattr(n, "callee", None)] + list(getattr(n, "args", []))
    if tname == "Index":   return [getattr(n, "target", None), getattr(n, "index", None)]
    if tname == "BinOp":   return [getattr(n, "left", None), getattr(n, "right", None)]

    # Fallback: se for dataclass, tenta varrer campos;
    # caso contrário, tenta um atributo 'children' se existir.
    if is_dataclass(n):
        out: List[Any] = []
        for k, v in n.__dict__.items():
            if k in ("line", "col", "op", "name", "value"):  # metadados/escalares
                continue
            if isinstance(v, list):
                out.extend(v)
            elif v is not None:
                out.append(v)
        return [child for child in out if child is not None]
    if hasattr(n, "children"):
        return list(getattr(n, "children"))
    return []

# -------------------------------------------------
# Layout recursivo (retorna posicoes e largura)
# -------------------------------------------------
def _compute_layout(n: NodeLike, x0=0.0, y0=0.0, y_spacing=1.6) -> Tuple[Dict[int,Tuple[float,float]], float]:
    ch = [c for c in children(n) if c is not None]
    if not ch:
        return ({id(n): (x0, y0)}, 1.0)

    pos: Dict[int,Tuple[float,float]] = {}
    widths: List[float] = []
    subs: List[NodeLike] = []

    for c in ch:
        subpos, w = _compute_layout(c, 0, 0, y_spacing)
        pos.update(subpos)
        widths.append(w)
        subs.append(c)

    total_w = sum(widths) + (len(widths)-1)*0.8
    cur_x = x0 - total_w/2.0

    def shift(node: NodeLike, dx: float, dy: float):
        x, y = pos[id(node)]
        pos[id(node)] = (x + dx, y + dy)
        for cc in children(node):
            if cc is not None:
                shift(cc, dx, dy)

    for c, w in zip(subs, widths):
        cx = cur_x + w/2.0
        shift(c, cx, y0 - y_spacing)
        cur_x += w + 0.8

    pos[id(n)] = (x0, y0)
    return pos, total_w

# -----------------------------------------
# Função principal: salva a árvore em PNG
# -----------------------------------------
def draw_tree(root: NodeLike, filename: str, figsize=(12, 8), dpi: int = 150):
    if not HAVE_MPL:
        return
    
    pos, _ = _compute_layout(root, 0.0, 0.0)

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_axis_off()

    def draw_edges(node: NodeLike):
        x, y = pos[id(node)]
        for c in children(node):
            if c is None:
                continue
            xc, yc = pos[id(c)]
            ax.plot([x, xc], [y-0.05, yc+0.05], 'k-', linewidth=1)
            draw_edges(c)

    def draw_nodes(node: NodeLike):
        x, y = pos[id(node)]
        bbox = dict(boxstyle="round,pad=0.3", fc="lightblue", ec="navy", lw=1.5)
        ax.text(x, y, node_label(node), ha="center", va="center", bbox=bbox, fontsize=9, fontweight="bold")
        for c in children(node):
            if c is not None:
                draw_nodes(c)

    draw_edges(root)
    draw_nodes(root)

    if pos:  # Se há nós para desenhar
        xs = [xy[0] for xy in pos.values()]
        ys = [xy[1] for xy in pos.values()]
        pad = 1.5
        ax.set_xlim(min(xs)-pad, max(xs)+pad)
        ax.set_ylim(min(ys)-pad, max(ys)+pad)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

# -----------------------------------------------------------
# Casos de teste
# -----------------------------------------------------------

# Casos VÁLIDOS (5)
tokens1 = [
    # let y = 1 + 3;
    Token("LET","let",1,1),
    Token("ID","y",1,5),
    Token("EQUAL","=",1,7),
    Token("NUM","1",1,9),
    Token("PLUS","+",1,11),
    Token("NUM","3",1,13),
    Token("SEMI",";",1,14),
    Token("EOL","",1,15)
]

tokens2 = [
    # 2 * (3 + 4);
    Token("NUM","2",1,1),
    Token("STAR","*",1,3),
    Token("LPAREN","(",1,5),
    Token("NUM","3",1,6),
    Token("PLUS","+",1,8),
    Token("NUM","4",1,10),
    Token("RPAREN",")",1,11),
    Token("SEMI",";",1,12),
    Token("EOL","",1,13)
]

tokens3 = [
    # let x = 5; x / 2
    Token("LET","let",1,1),
    Token("ID","x",1,5),
    Token("EQUAL","=",1,7),
    Token("NUM","5",1,9),
    Token("SEMI",";",1,10),
    Token("ID","x",1,12),
    Token("SLASH","/",1,14),
    Token("NUM","2",1,16),
    Token("EOL","",1,17)
]

tokens4 = [
    # if (x < 10 && y != 0) { x = x + 1; } else x = 0;
    Token("IF","if",1,1),
    Token("LPAREN","(",1,3),
    Token("ID","x",1,4),
    Token("LT","<",1,6),
    Token("NUM","10",1,9),
    Token("AND","&&",1,11),
    Token("ID","y",1,14),
    Token("NE","!=",1,16),
    Token("NUM","0",1,19),
    Token("RPAREN",")",1,20),
    Token("LBRACE","{",1,22),
    Token("ID","x",1,24),
    Token("EQUAL","=",1,26),
    Token("ID","x",1,28),
    Token("PLUS","+",1,30),
    Token("NUM","1",1,32),
    Token("SEMI",";",1,33),
    Token("RBRACE","}",1,35),
    Token("ELSE","else",1,37),
    Token("ID","x",1,42),
    Token("EQUAL","=",1,44),
    Token("NUM","0",1,46),
    Token("SEMI",";",1,47),
    Token("EOL","",1,48)
]

tokens5 = [
    # let z = f(a, b)[i] * g();
    Token("LET","let",1,1),
    Token("ID","z",1,5),
    Token("EQUAL","=",1,7),
    Token("ID","f",1,9),
    Token("LPAREN","(",1,10),
    Token("ID","a",1,11),
    Token("COMMA",",",1,12),
    Token("ID","b",1,14),
    Token("RPAREN",")",1,15),
    Token("LBRACK","[",1,16),
    Token("ID","i",1,17),
    Token("RBRACK","]",1,18),
    Token("STAR","*",1,20),
    Token("ID","g",1,22),
    Token("LPAREN","(",1,23),
    Token("RPAREN",")",1,24),
    Token("SEMI",";",1,25),
    Token("EOL","",1,26)
]

# INVÁLIDOS (6)

tokens6 = [
    # ERRO: faltou '=' após ID -> let z 7;
    Token("LET","let",1,1),
    Token("ID","z",1,5),
    # Token("EQUAL","=",1,7),  # ausente
    Token("NUM","7",1,9),
    Token("SEMI",";",1,10),
    Token("EOL","",1,11)
]

tokens7 = [
    # ERRO: parêntese não fechado -> 1 + (2 * 3;
    Token("NUM","1",1,1),
    Token("PLUS","+",1,3),
    Token("LPAREN","(",1,5),
    Token("NUM","2",1,6),
    Token("STAR","*",1,8),
    Token("NUM","3",1,10),
    # faltou RPAREN
    Token("SEMI",";",1,11),
    Token("EOL","",1,12)
]

tokens8 = [
    # ERRO: 'else' sem 'if'
    Token("ELSE","else",1,1),
    Token("ID","x",1,6),
    Token("EQUAL","=",1,8),
    Token("NUM","1",1,10),
    Token("SEMI",";",1,11),
    Token("EOL","",1,12)
]

tokens9 = [
    # ERRO: while com parêntese da condição não fechado
    # while (x < 5 { x = x + 1; }
    Token("WHILE","while",1,1),
    Token("LPAREN","(",1,7),
    Token("ID","x",1,8),
    Token("LT","<",1,10),
    Token("NUM","5",1,12),
    # faltou RPAREN
    Token("LBRACE","{",1,14),
    Token("ID","x",1,16),
    Token("EQUAL","=",1,18),
    Token("ID","x",1,20),
    Token("PLUS","+",1,22),
    Token("NUM","1",1,24),
    Token("SEMI",";",1,25),
    Token("RBRACE","}",1,27),
    Token("EOL","",1,28)
]

tokens10 = [
    # ERRO: indexador sem ']' -> let a = arr[1 + 2;
    Token("LET","let",1,1),
    Token("ID","a",1,5),
    Token("EQUAL","=",1,7),
    Token("ID","arr",1,9),
    Token("LBRACK","[",1,12),
    Token("NUM","1",1,13),
    Token("PLUS","+",1,15),
    Token("NUM","2",1,17),
    # faltou RBRACK
    Token("SEMI",";",1,18),
    Token("EOL","",1,19)
]

tokens11 = [
    Token("LET","let",1,1),
    Token("ID","a",1,5),
    # Token("EQUAL","=",1,7),  # faltando de propósito
    Token("NUM","1",1,7),
    Token("SEMI",";",1,8),

    Token("ID","x",1,10),
    Token("EQUAL","=",1,12),
    # faltou expressão aqui
    Token("SEMI",";",1,13),

    Token("ID","y",1,15),
    Token("EQUAL","=",1,17),
    Token("NUM","3",1,19),
    Token("SEMI",";",1,20),
    Token("EOL","",1,21),
]

# Lista de casos de teste
CASES = [
    ("case1_let_y",            "Atribuição simples com soma",                               tokens1),
    ("case2_expr_paren",       "Expressão aritmética com parênteses",                      tokens2),
    ("case3_two_stmts",        "Duas instruções na mesma linha",                           tokens3),
    ("case4_if_else_logic",    "if/else com && e !=",                                      tokens4),
    ("case5_call_index",       "Chamada e indexação",                                      tokens5),
    ("case6_missing_equal",    "ERRO: faltou '=' na atribuição",                          tokens6),
    ("case7_missing_rparen",   "ERRO: parêntese aberto sem fechar",                       tokens7),
    ("case8_lonely_else",      "ERRO: 'else' sem 'if' correspondente",                    tokens8),
    ("case9_while_rparen",     "ERRO: while sem fechar ')' da condição",                  tokens9),
    ("case10_missing_rbrack",  "ERRO: indexação sem ']'",                                 tokens10),
    ("case11_two_errors_same_line", "Dois erros, mas parser continua",                    tokens11),
]

def generate_all_trees():
    """Gera árvores AST para todos os casos de teste."""
    if not HAVE_MPL:
        print("Erro: matplotlib não encontrado. Instale com: pip install matplotlib")
        return
    
    success_count = 0
    total_count = len(CASES)
    
    for name, desc, tokens in CASES:
        # Parse dos tokens
        program, errors = parse(tokens)
        
        if program is not None:
            # Salvar árvore completa do programa
            filename = f"trees/{name}_program.png"
            draw_tree(program, filename)
            success_count += 1
            
            # Se houver múltiplos statements, salvar cada um individualmente
            if hasattr(program, 'body') and len(program.body) > 1:
                for i, stmt in enumerate(program.body):
                    if stmt is not None:
                        stmt_filename = f"trees/{name}_stmt{i+1}.png"
                        draw_tree(stmt, stmt_filename)
    
    print(f"Geradas {success_count}/{total_count} árvores em: {os.path.abspath('trees')}")

if __name__ == "__main__":
    generate_all_trees()