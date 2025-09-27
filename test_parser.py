import pytest
from dataclasses import dataclass
from typing import List, Optional, Union, Any, Tuple

# Importar nosso parser
from parcer import parse


@dataclass
class Token:
    type: str
    lex: str
    line: int
    col: int

# ---------------- Casos de teste ----------------
# VÁLIDOS (5)

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


# ---------------- Testes para casos VÁLIDOS ----------------

def test_case1_let_y():
    """Teste: let y = 1 + 3; - Atribuição simples com soma"""
    program, errors = parse(tokens1)
    assert len(errors) == 0, f"Esperado nenhum erro, mas encontrou: {errors}"
    assert program is not None, "AST deveria ter sido construída"


def test_case2_expr_paren():
    """Teste: 2 * (3 + 4); - Expressão aritmética com parênteses"""
    program, errors = parse(tokens2)
    assert len(errors) == 0, f"Esperado nenhum erro, mas encontrou: {errors}"
    assert program is not None, "AST deveria ter sido construída"


def test_case3_two_stmts():
    """Teste: let x = 5; x / 2 - Duas instruções na mesma linha"""
    program, errors = parse(tokens3)
    assert len(errors) == 0, f"Esperado nenhum erro, mas encontrou: {errors}"
    assert program is not None, "AST deveria ter sido construída"


def test_case4_if_else_logic():
    """Teste: if/else com && e != - Estrutura condicional complexa"""
    program, errors = parse(tokens4)
    assert len(errors) == 0, f"Esperado nenhum erro, mas encontrou: {errors}"
    assert program is not None, "AST deveria ter sido construída"


def test_case5_call_index():
    """Teste: let z = f(a, b)[i] * g(); - Chamada e indexação"""
    program, errors = parse(tokens5)
    assert len(errors) == 0, f"Esperado nenhum erro, mas encontrou: {errors}"
    assert program is not None, "AST deveria ter sido construída"


# ---------------- Testes para casos INVÁLIDOS ----------------

def test_case6_missing_equal():
    """Teste: ERRO - faltou '=' na atribuição (let z 7;)"""
    program, errors = parse(tokens6)
    assert len(errors) == 1, f"Esperado 1 erro, mas encontrou {len(errors)}: {errors}"
    assert "Esperado '='" in str(errors[0]), f"Erro deveria mencionar '=', mas foi: {errors[0]}"
    assert "@ 1:9" in str(errors[0]), f"Erro deveria estar na posição 1:9, mas foi: {errors[0]}"


def test_case7_missing_rparen():
    """Teste: ERRO - parêntese não fechado (1 + (2 * 3;)"""
    program, errors = parse(tokens7)
    assert len(errors) == 1, f"Esperado 1 erro, mas encontrou {len(errors)}: {errors}"
    assert "Esperado ')'" in str(errors[0]), f"Erro deveria mencionar ')', mas foi: {errors[0]}"
    assert "@ 1:11" in str(errors[0]), f"Erro deveria estar na posição 1:11, mas foi: {errors[0]}"


def test_case8_lonely_else():
    """Teste: ERRO - 'else' sem 'if' correspondente"""
    program, errors = parse(tokens8)
    assert len(errors) == 1, f"Esperado 1 erro, mas encontrou {len(errors)}: {errors}"
    expected_tokens = ["número", "'true'", "'false'", "identificador", "'("]
    error_msg = str(errors[0])
    assert any(token in error_msg for token in expected_tokens), f"Erro deveria mencionar tokens esperados, mas foi: {errors[0]}"
    assert "@ 1:1" in error_msg, f"Erro deveria estar na posição 1:1, mas foi: {errors[0]}"


def test_case9_while_rparen():
    """Teste: ERRO - while sem fechar ')' da condição"""
    program, errors = parse(tokens9)
    assert len(errors) == 2, f"Esperado 2 erros, mas encontrou {len(errors)}: {errors}"
    # Primeiro erro: Esperado ')' @ 1:14
    assert "Esperado ')'" in str(errors[0]), f"Primeiro erro deveria mencionar ')', mas foi: {errors[0]}"
    assert "@ 1:14" in str(errors[0]), f"Primeiro erro deveria estar na posição 1:14, mas foi: {errors[0]}"
    # Segundo erro: @ 1:27
    assert "@ 1:27" in str(errors[1]), f"Segundo erro deveria estar na posição 1:27, mas foi: {errors[1]}"


def test_case10_missing_rbrack():
    """Teste: ERRO - indexação sem ']' (let a = arr[1 + 2;)"""
    program, errors = parse(tokens10)
    assert len(errors) == 1, f"Esperado 1 erro, mas encontrou {len(errors)}: {errors}"
    assert "Esperado ']'" in str(errors[0]), f"Erro deveria mencionar ']', mas foi: {errors[0]}"
    assert "@ 1:18" in str(errors[0]), f"Erro deveria estar na posição 1:18, mas foi: {errors[0]}"


def test_case11_two_errors_same_line():
    """Teste: ERRO - Dois erros na mesma linha, mas parser continua"""
    program, errors = parse(tokens11)
    assert len(errors) == 2, f"Esperado 2 erros, mas encontrou {len(errors)}: {errors}"
    # Primeiro erro: Esperado '=' @ 1:7
    assert "Esperado '='" in str(errors[0]), f"Primeiro erro deveria mencionar '=', mas foi: {errors[0]}"
    assert "@ 1:7" in str(errors[0]), f"Primeiro erro deveria estar na posição 1:7, mas foi: {errors[0]}"
    # Segundo erro: @ 1:13
    assert "@ 1:13" in str(errors[1]), f"Segundo erro deveria estar na posição 1:13, mas foi: {errors[1]}"


# ---------------- Teste runner do professor ----------------

def test_all_cases_structure():
    """Teste para verificar se todos os casos de teste estão bem formados"""
    all_tokens = [tokens1, tokens2, tokens3, tokens4, tokens5, tokens6, tokens7, tokens8, tokens9, tokens10, tokens11]
    
    for i, tokens in enumerate(all_tokens, 1):
        assert tokens[-1].type == "EOL", f"Caso {i} deveria terminar com EOL"
        
        for token in tokens:
            assert hasattr(token, 'type'), f"Token no caso {i} deveria ter campo 'type'"
            assert hasattr(token, 'lex'), f"Token no caso {i} deveria ter campo 'lex'"
            assert hasattr(token, 'line'), f"Token no caso {i} deveria ter campo 'line'"
            assert hasattr(token, 'col'), f"Token no caso {i} deveria ter campo 'col'"

CASES = [
    ("case1_let_y", "Atribuição simples com soma", tokens1),
    ("case2_expr_paren", "Expressão aritmética com parênteses", tokens2),
    ("case3_two_stmts", "Duas instruções na mesma linha", tokens3),
    ("case4_if_else_logic", "if/else com && e !=", tokens4),
    ("case5_call_index", "Chamada e indexação", tokens5),
    ("case6_missing_equal", "ERRO: faltou '=' na atribuição", tokens6),
    ("case7_missing_rparen", "ERRO: parêntese não fechado", tokens7),
    ("case8_lonely_else", "ERRO: 'else' sem 'if'", tokens8),
    ("case9_while_rparen", "ERRO: while sem fechar ')'", tokens9),
    ("case10_missing_rbrack", "ERRO: indexação sem ']'", tokens10),
    ("case11_two_errors_same_line", "ERRO: Dois erros na mesma linha", tokens11),
]

def draw_tree_if_available(program, name):
    """Tenta gerar árvore AST se o módulo estiver disponível"""
    try:
        from generate_trees import draw_tree
        import os
        
        if not os.path.exists('trees'):
            os.makedirs('trees')
            
        # Salvar árvore completa do programa
        filename = f"trees/{name}_program.png"
        draw_tree(program, filename)
        
        # Se houver múltiplos statements, salvar cada um individualmente
        if hasattr(program, 'body') and len(program.body) > 1:
            for i, stmt in enumerate(program.body):
                if stmt is not None:
                    stmt_filename = f"trees/{name}_stmt{i+1}.png"
                    draw_tree(stmt, stmt_filename)
            return f"trees/{name}_stmtNN.png"
        else:
            return f"trees/{name}_program.png"
    except ImportError:
        return None

if __name__ == "__main__":
    print("=== SUÍTE DE TESTES DO PARSER ===")
    
    for name, desc, tokens in CASES:
        print(f"\n>>> {name}")
        print()
        print("="*70)
        print(f"[CASO] {name}")
        
        # Parse dos tokens
        program, errors = parse(tokens)
        
        if not errors:
            # Caso válido - AST construída
            print("[RESULTADO] OK — AST construída")
            tree_file = draw_tree_if_available(program, name)
            if tree_file:
                print(f"[ÁRVORES] salvas em '{tree_file}'")
        else:
            # Caso com erros
            print("[RESULTADO] ERROS SINTÁTICOS")
            for error in errors:
                print(f"  - {error}")
            
            if program is not None:
                print("[AST (parcial)]")
                tree_file = draw_tree_if_available(program, name)
            else:
                print("[Sem AST]")