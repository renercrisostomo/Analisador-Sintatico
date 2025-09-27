"""
PARSER RECURSIVO-DESCENDENTE + AST + MODO PÂNICO
Francisco Renêr Lopes Crisostomo
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Union, Tuple

@dataclass
class Token:
    type: str
    lex: str
    line: int
    col: int

# AST Nodes
@dataclass
class Program:
    body: List[Union['Stmt', 'Expr']]
    line: int = 1
    col: int = 1

@dataclass  
class Let:
    target: 'Var'
    init: 'Expr'
    line: int = 1
    col: int = 1

@dataclass
class Assign:
    target: 'Var'
    value: 'Expr'
    line: int = 1
    col: int = 1

@dataclass
class If:
    test: 'Expr'
    then: 'Block'
    otherwise: Optional['Block'] = None
    line: int = 1
    col: int = 1

@dataclass
class While:
    test: 'Expr'
    body: 'Block'
    line: int = 1
    col: int = 1

@dataclass
class Return:
    value: Optional['Expr'] = None
    line: int = 1
    col: int = 1

@dataclass
class Block:
    body: List[Union['Stmt', 'Expr']]
    line: int = 1
    col: int = 1

@dataclass
class BinOp:
    left: 'Expr'
    op: str
    right: 'Expr'
    line: int = 1
    col: int = 1

@dataclass
class Var:
    name: str
    line: int = 1
    col: int = 1

@dataclass
class Num:
    value: str
    line: int = 1
    col: int = 1

@dataclass
class Bool:
    value: bool
    line: int = 1
    col: int = 1

@dataclass
class Call:
    callee: 'Expr'
    args: List['Expr']
    line: int = 1
    col: int = 1

@dataclass
class Index:
    target: 'Expr'
    index: 'Expr'
    line: int = 1
    col: int = 1

# Type aliases
Expr = Union[BinOp, Var, Num, Bool, Call, Index]
Stmt = Union[Let, Assign, If, While, Return, Block, Expr]

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors = []
    
    def current_token(self) -> Optional[Token]:
        return self.tokens[self.current] if self.current < len(self.tokens) else None
    
    def advance(self) -> Optional[Token]:
        if self.current < len(self.tokens):
            token = self.tokens[self.current]
            self.current += 1
            return token
        return None
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        pos = self.current + offset
        return self.tokens[pos] if pos < len(self.tokens) else None
    
    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)
    
    def match(self, *token_types: str) -> bool:
        current = self.current_token()
        return current is not None and current.type in token_types
    
    def expect(self, expected_type: str) -> bool:
        current = self.current_token()
        if current and current.type == expected_type:
            self.advance()
            return True
        
        # Mapear nomes de tokens para símbolos legíveis
        token_symbols = {
            "EQUAL": "=",
            "LPAREN": "(",
            "RPAREN": ")",
            "LBRACE": "{",
            "RBRACE": "}",
            "LBRACK": "[",
            "RBRACK": "]",
            "SEMI": ";",
            "COMMA": ","
        }
        expected_symbol = token_symbols.get(expected_type, expected_type.lower())
        
        if current:
            error_msg = f"Esperado '{expected_symbol}' (encontrado '{current.lex}') @ {current.line}:{current.col}"
        else:
            error_msg = f"Esperado '{expected_symbol}' (encontrado fim de arquivo)"
        self.errors.append(error_msg)
        return False
    
    def add_error(self, message: str, token: Optional[Token] = None):
        if token:
            self.errors.append(f"{message} @ {token.line}:{token.col}")
        else:
            current = self.current_token()
            if current:
                self.errors.append(f"{message} @ {current.line}:{current.col}")
            else:
                self.errors.append(message)
    
    def panic_mode(self):
        if self.is_at_end():
            return
        
        sync_points = {'SEMI', 'EOL', 'RBRACE', 'EOF'}
        
        while not self.is_at_end() and not self.match(*sync_points):
            self.advance()
        
        if not self.is_at_end():
            sync_token = self.current_token()
            # Se é RBRACE, deixar para o loop principal detectar como órfão
            # Se é SEMI ou EOL, consumir normalmente
            if sync_token.type in {'SEMI', 'EOL'} and sync_token.type != 'EOF':
                self.advance()
    
    def parse_primary(self) -> Optional[Expr]:
        current = self.current_token()
        if not current:
            self.add_error("Expressão esperada, mas fim de arquivo encontrado")
            return None
        
        if current.type == "NUM":
            self.advance()
            return Num(value=current.lex, line=current.line, col=current.col)
        elif current.type == "TRUE":
            self.advance()
            return Bool(value=True, line=current.line, col=current.col)
        elif current.type == "FALSE":
            self.advance()
            return Bool(value=False, line=current.line, col=current.col)
        elif current.type == "ID":
            self.advance()
            return Var(name=current.lex, line=current.line, col=current.col)
        elif current.type == "LPAREN":
            self.advance()
            expr = self.parse_expression()
            if expr is None:
                self.add_error("Expressão esperada após '('")
                return None
            if not self.expect("RPAREN"):
                self.panic_mode()
                return None
            return expr
        else:
            expected_tokens = ["número", "'true'", "'false'", "identificador", "'('"]
            expected_str = ", ".join(expected_tokens)
            self.add_error(f"Esperado {expected_str}, encontrado '{current.type}' @ {current.line}:{current.col}")
            # Não chamar panic_mode se já estamos em um ponto de sincronização
            if current.type not in {'SEMI', 'EOL', 'RBRACE', 'EOF'}:
                self.panic_mode()
            return None
    
    def parse_postfix(self) -> Optional[Expr]:
        expr = self.parse_primary()
        if expr is None:
            return None
        
        while not self.is_at_end():
            current = self.current_token()
            
            if current and current.type == "LPAREN":
                self.advance()
                args = []
                
                if not self.match("RPAREN"):
                    first_arg = self.parse_expression()
                    if first_arg is None:
                        self.add_error("Argumento esperado")
                        return None
                    args.append(first_arg)
                    
                    while self.match("COMMA"):
                        self.advance()
                        arg = self.parse_expression()
                        if arg is None:
                            self.add_error("Argumento esperado após ','")
                            return None
                        args.append(arg)
                
                if not self.expect("RPAREN"):
                    self.panic_mode()
                    return None
                
                expr = Call(callee=expr, args=args, line=current.line, col=current.col)
            
            elif current and current.type == "LBRACK":
                self.advance()
                index_expr = self.parse_expression()
                if index_expr is None:
                    self.add_error("Índice esperado após '['")
                    self.panic_mode()
                    return None
                
                if not self.expect("RBRACK"):
                    self.panic_mode()
                    return None
                
                expr = Index(target=expr, index=index_expr, line=current.line, col=current.col)
            else:
                break
        
        return expr
    
    def parse_multiplicative(self) -> Optional[Expr]:
        left = self.parse_postfix()
        if left is None:
            return None
        
        while self.match("STAR", "SLASH"):
            op_token = self.current_token()
            self.advance()
            right = self.parse_postfix()
            if right is None:
                return left
            left = BinOp(left=left, op=op_token.lex, right=right, 
                        line=op_token.line, col=op_token.col)
        
        return left
    
    def parse_additive(self) -> Optional[Expr]:
        left = self.parse_multiplicative()
        if left is None:
            return None
        
        while self.match("PLUS", "MINUS"):
            op_token = self.current_token()
            self.advance()
            right = self.parse_multiplicative()
            if right is None:
                return left
            left = BinOp(left=left, op=op_token.lex, right=right,
                        line=op_token.line, col=op_token.col)
        
        return left
    
    def parse_relational(self) -> Optional[Expr]:
        left = self.parse_additive()
        if left is None:
            return None
        
        while self.match("LT", "GT", "LE", "GE"):
            op_token = self.current_token()
            self.advance()
            right = self.parse_additive()
            if right is None:
                return left
            left = BinOp(left=left, op=op_token.lex, right=right,
                        line=op_token.line, col=op_token.col)
        
        return left
    
    def parse_equality(self) -> Optional[Expr]:
        left = self.parse_relational()
        if left is None:
            return None
        
        while self.match("EQ", "NE"):
            op_token = self.current_token()
            self.advance()
            right = self.parse_relational()
            if right is None:
                return left
            left = BinOp(left=left, op=op_token.lex, right=right,
                        line=op_token.line, col=op_token.col)
        
        return left
    
    def parse_logical_and(self) -> Optional[Expr]:
        left = self.parse_equality()
        if left is None:
            return None
        
        while self.match("AND"):
            op_token = self.current_token()
            self.advance()
            right = self.parse_equality()
            if right is None:
                return left
            left = BinOp(left=left, op=op_token.lex, right=right,
                        line=op_token.line, col=op_token.col)
        
        return left
    
    def parse_logical_or(self) -> Optional[Expr]:
        left = self.parse_logical_and()
        if left is None:
            return None
        
        while self.match("OR"):
            op_token = self.current_token()
            self.advance()
            right = self.parse_logical_and()
            if right is None:
                return left
            left = BinOp(left=left, op=op_token.lex, right=right,
                        line=op_token.line, col=op_token.col)
        
        return left
    
    def parse_expression(self) -> Optional[Expr]:
        return self.parse_logical_or()
    
    def parse_let(self) -> Optional[Let]:
        start_token = self.current_token()
        if not start_token or start_token.type != "LET":
            return None
        
        self.advance()
        
        if not self.expect("ID"):
            self.panic_mode()
            return None
        
        id_token = self.tokens[self.current - 1]
        target = Var(name=id_token.lex, line=id_token.line, col=id_token.col)
        
        if not self.expect("EQUAL"):
            # Não usar panic_mode aqui - o erro já foi reportado pelo expect()
            # Deixar o parse principal lidar com a recuperação
            return None
        
        error_count_before = len(self.errors)
        init_expr = self.parse_expression()
        
        if init_expr is None:
            if len(self.errors) == error_count_before:
                self.add_error("Expressão de inicialização esperada após '='")
            self.panic_mode()
            return None
        
        return Let(target=target, init=init_expr, line=start_token.line, col=start_token.col)
    
    def parse_assign(self) -> Optional[Assign]:
        start_token = self.current_token()
        if not start_token or start_token.type != "ID":
            self.add_error("Identificador esperado")
            return None
        
        self.advance()
        target = Var(name=start_token.lex, line=start_token.line, col=start_token.col)
        
        if not self.expect("EQUAL"):
            self.panic_mode()
            return None
        
        error_count_before = len(self.errors)
        value_expr = self.parse_expression()
        
        if value_expr is None:
            if len(self.errors) == error_count_before:
                current_pos = self.current_token()
                if current_pos:
                    self.add_error("Expressão esperada após '='", current_pos)
                else:
                    self.add_error("Expressão esperada após '='")
            # Criar uma expressão dummy para continuar o parsing sem panic_mode
            value_expr = Num(value=0, line=start_token.line, col=start_token.col)
            
            # Se o token atual é um separador (SEMI), avançar por ele para não confundir o parse principal
            current_token = self.current_token()
            if current_token and current_token.type == "SEMI":
                self.advance()
                # Marcar que já consumimos o separador
                self.consumed_separator = True
        return Assign(target=target, value=value_expr, line=start_token.line, col=start_token.col)
    
    def parse_if(self) -> Optional[If]:
        start_token = self.current_token()
        if not start_token or start_token.type != "IF":
            return None
        
        self.advance()
        
        if not self.expect("LPAREN"):
            self.panic_mode()
            return None
        
        test_expr = self.parse_expression()
        if test_expr is None:
            self.add_error("Condição esperada no if")
            self.panic_mode()
            return None
        
        if not self.expect("RPAREN"):
            self.panic_mode()
            return None
        
        then_block = self.parse_block()
        if then_block is None:
            self.add_error("Bloco esperado após condição do if")
            return None
        
        else_block = None
        if self.match("ELSE"):
            self.advance()
            else_block = self.parse_block()
            if else_block is None:
                self.add_error("Bloco esperado após 'else'")
                return None
        
        return If(test=test_expr, then=then_block, otherwise=else_block,
                 line=start_token.line, col=start_token.col)
    
    def parse_while(self) -> Optional[While]:
        start_token = self.current_token()
        if not start_token or start_token.type != "WHILE":
            return None
        
        self.advance()
        
        if not self.expect("LPAREN"):
            self.panic_mode()
            return None
        
        test_expr = self.parse_expression()
        if test_expr is None:
            self.add_error("Condição esperada no while")
            self.panic_mode()
            return None
        
        if not self.expect("RPAREN"):
            self.panic_mode()
            return None
        
        body_block = self.parse_block()
        if body_block is None:
            self.add_error("Bloco esperado após condição do while")
            return None
        
        return While(test=test_expr, body=body_block, line=start_token.line, col=start_token.col)
    
    def parse_return(self) -> Optional[Return]:
        start_token = self.current_token()
        if not start_token or start_token.type != "RETURN":
            return None
        
        self.advance()
        
        value_expr = None
        current = self.current_token()
        if current and current.type not in {";", "EOL", "EOF", "}"}:
            value_expr = self.parse_expression()
            if value_expr is None:
                pass
        
        return Return(value=value_expr, line=start_token.line, col=start_token.col)
    
    def parse_block(self) -> Optional[Block]:
        current = self.current_token()
        if not current:
            return None
        
        if current.type == "LBRACE":
            start_token = current
            self.advance()
            
            statements = []
            
            while not self.is_at_end() and not self.match("RBRACE"):
                stmt = self.parse_statement()
                if stmt is not None:
                    statements.append(stmt)
                
                if self.match("SEMI"):
                    self.advance()
                    
                if len(self.errors) > 0:
                    self.panic_mode()
                    if self.is_at_end():
                        break
            
            if not self.expect("RBRACE"):
                self.panic_mode()
                return None
            
            return Block(body=statements, line=start_token.line, col=start_token.col)
        
        else:
            stmt = self.parse_statement()
            if stmt is None:
                return None
            return Block(body=[stmt], line=current.line, col=current.col)
    
    def parse_statement(self) -> Optional[Stmt]:
        current = self.current_token()
        if not current:
            return None
        
        if current.type == "LET":
            return self.parse_let()
        elif current.type == "IF":
            return self.parse_if()
        elif current.type == "WHILE":
            return self.parse_while()
        elif current.type == "RETURN":
            return self.parse_return()
        elif current.type == "ID":
            next_token = self.peek()
            if next_token and next_token.type == "EQUAL":
                return self.parse_assign()
            else:
                return self.parse_expression()
        else:
            return self.parse_expression()
    
    def parse(self) -> tuple[Optional[Program], List[str]]:
        self.current = 0
        self.errors = []
        
        statements = []
        
        while not self.is_at_end():
            current = self.current_token()
            
            if current and current.type == "EOL":
                self.advance()
                continue
            
            # Verificar se encontramos um } órfão
            if current and current.type == "RBRACE":
                self.add_error("'}' inesperado", current)
                self.advance()
                continue
            
            stmt = self.parse_statement()
            
            if stmt is not None:
                statements.append(stmt)
                
                # Verificar se o statement já consumiu seu separador
                already_consumed_sep = getattr(self, 'consumed_separator', False)
                if already_consumed_sep:
                    self.consumed_separator = False  # Reset flag
                else:
                    # Processar separador apenas se houve um statement válido e não foi consumido
                    current = self.current_token()
                    
                    if current and current.type in {"SEMI", "EOL"}:
                        self.advance()
                    elif current and current.type != "EOF":
                        error_pos = current
                        self.add_error(f"Esperado ';' ou nova linha após statement", error_pos)
                        self.panic_mode()
            else:
                # Statement inválido - panic_mode já foi chamado pelos métodos parse_*
                # Não precisa gerar erro adicional aqui
                current = self.current_token()
                
                # Se ainda estivermos num token que não foi processado, avançar manualmente
                if current and current.type not in {"SEMI", "EOL", "EOF"}:
                    self.panic_mode()
            
            if len(self.errors) > 10:
                self.add_error("Muitos erros sintáticos - parando análise")
                break
        
        if statements or len(self.errors) == 0:
            program = Program(body=statements, line=1, col=1)
            return program, self.errors
        else:
            return None, self.errors

def parse(tokens: List[Token]) -> Tuple[Optional[Program], List[str]]:
    """Função parse principal esperada pelos testes."""
    parser = Parser(tokens)
    return parser.parse()